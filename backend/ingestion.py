"""
Document ingestion: extract clean text from PDF/TXT, OCR scanned pages
automatically with the vision model, strip repeated headers/footers, and
chunk by paragraph/sentence boundaries (never by a fixed character count)
with overlap for context continuity.
"""
from __future__ import annotations

import hashlib
import logging
import re
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import fitz  # PyMuPDF

import backend.config as config
import backend.llm as llm
import backend.runtime_state as runtime_state

logger = logging.getLogger("ingestion")


@dataclass
class Chunk:
    text: str
    page_number: int
    chunk_index: int
    heading: str = ""


@dataclass
class Document:
    file_name: str
    extension: str
    sha256: str
    full_pages: List[str] = field(default_factory=list)
    chunks: List[Chunk] = field(default_factory=list)
    ocr_pages: int = 0


def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(8192), b""):
            h.update(block)
    return h.hexdigest()


def _ocr_page(page: "fitz.Page", page_num: int) -> str:
    """Render a page to an image and OCR it with the vision model."""
    try:
        pix = page.get_pixmap(dpi=config.OCR_RENDER_DPI)
        png_bytes = pix.tobytes("png")
        text = llm.vision_extract_text(png_bytes, model=runtime_state.get_vision_model())
        logger.info("OCR'd page %d with %s (%d chars extracted)", page_num, runtime_state.get_vision_model(), len(text))
        return text
    except Exception as e:
        logger.warning("OCR failed on page %d: %s", page_num, e)
        return ""


def _extract_pdf_pages(path: Path) -> tuple[List[str], int]:
    """Return raw text per page using PyMuPDF, auto-OCRing pages that look
    scanned/image-only (very little extractable text) if a vision model is
    configured. Returns (pages, ocr_page_count)."""
    pages = []
    ocr_count = 0
    with fitz.open(path) as doc:
        low_text_pages = []
        for i, page in enumerate(doc):
            text = page.get_text("text")
            pages.append(text)
            if len(text.strip()) < config.OCR_MIN_CHARS_PER_PAGE:
                low_text_pages.append(i)

        if low_text_pages and config.AUTO_OCR:
            if len(low_text_pages) > config.OCR_MAX_PAGES:
                logger.warning(
                    "%d pages look scanned, which exceeds OCR_MAX_PAGES=%d. "
                    "Only OCRing the first %d.",
                    len(low_text_pages), config.OCR_MAX_PAGES, config.OCR_MAX_PAGES,
                )
                low_text_pages = low_text_pages[:config.OCR_MAX_PAGES]

            if low_text_pages:
                logger.info(
                    "Chunking started: %d page(s) look scanned/image-only, "
                    "OCRing with vision model '%s' first...",
                    len(low_text_pages), runtime_state.get_vision_model(),
                )
            for i in low_text_pages:
                ocr_text = _ocr_page(doc[i], i + 1)
                if ocr_text:
                    pages[i] = ocr_text
                    ocr_count += 1
    return pages, ocr_count


def _extract_txt_pages(path: Path) -> List[str]:
    """Treat a .txt/.md file as a single 'page'. Tries common encodings in
    order since Windows editors (Notepad, etc.) often save as UTF-16 or
    with a BOM, which silently produces empty/garbled text under strict
    UTF-8 decoding."""
    raw = path.read_bytes()
    if not raw.strip():
        return [""]

    for encoding in ("utf-8-sig", "utf-16", "utf-8"):
        try:
            text = raw.decode(encoding)
            if text.strip():
                return [text]
        except (UnicodeDecodeError, UnicodeError):
            continue

    # last resort: never crash, just recover what we can
    return [raw.decode("utf-8", errors="ignore")]


def _strip_repeated_headers_footers(pages: List[str]) -> List[str]:
    if len(pages) < 3:
        return pages

    line_counts: Counter = Counter()
    per_page_lines = []
    for page_text in pages:
        lines = [ln.strip() for ln in page_text.split("\n")]
        per_page_lines.append(lines)
        for ln in set(lines):
            if 0 < len(ln) <= 100:
                line_counts[ln] += 1

    threshold = max(3, int(len(pages) * 0.5))
    boilerplate = {
        ln for ln, cnt in line_counts.items()
        if cnt >= threshold and (len(ln) < 60 or re.match(r"^[\d\s\-\u2013|]+$", ln))
    }

    cleaned_pages = []
    for lines in per_page_lines:
        kept = [ln for ln in lines if ln not in boilerplate]
        cleaned_pages.append("\n".join(kept))
    return cleaned_pages


def _detect_heading(paragraph: str) -> str:
    first_line = paragraph.strip().split("\n")[0].strip()
    if 0 < len(first_line) <= 90 and not first_line.endswith((".", ",", ";")):
        words = first_line.split()
        if words and (first_line.isupper() or sum(w[:1].isupper() for w in words) / len(words) > 0.6):
            return first_line
    return ""


def _split_into_paragraphs(page_text: str) -> List[str]:
    raw_paragraphs = re.split(r"\n\s*\n", page_text)
    paragraphs = []
    for p in raw_paragraphs:
        p = re.sub(r"[ \t]+", " ", p).strip()
        if p:
            paragraphs.append(p)
    # Fallback: no blank-line paragraphs found (common in plain .txt files
    # that use single newlines) - split on single newlines instead so we
    # never silently produce zero chunks for otherwise-valid text.
    if not paragraphs and page_text.strip():
        for line in page_text.split("\n"):
            line = re.sub(r"[ \t]+", " ", line).strip()
            if line:
                paragraphs.append(line)
    return paragraphs


def _chunk_pages(pages: List[str]) -> List[Chunk]:
    chunks: List[Chunk] = []
    chunk_index = 0
    current_text = ""
    current_page = 1
    current_heading = ""

    def flush():
        nonlocal current_text, chunk_index
        if current_text.strip():
            chunks.append(
                Chunk(
                    text=current_text.strip(),
                    page_number=current_page,
                    chunk_index=chunk_index,
                    heading=current_heading,
                )
            )
            chunk_index += 1

    for page_num, page_text in enumerate(pages, start=1):
        for para in _split_into_paragraphs(page_text):
            heading = _detect_heading(para)
            if heading:
                current_heading = heading

            candidate = (current_text + "\n\n" + para).strip() if current_text else para

            if len(candidate) > config.CHUNK_SIZE_CHARS and current_text:
                flush()
                overlap_tail = current_text[-config.CHUNK_OVERLAP_CHARS:]
                current_text = (overlap_tail + "\n\n" + para).strip()
                current_page = page_num
            else:
                current_text = candidate
                current_page = current_page or page_num

    flush()

    # Absolute last resort: if a single page had a huge wall of text with
    # no paragraph/line breaks at all, still make sure something gets
    # indexed rather than raising "no chunks".
    if not chunks:
        joined = "\n".join(p for p in pages if p and p.strip())
        if joined.strip():
            step = config.CHUNK_SIZE_CHARS
            for idx, start in enumerate(range(0, len(joined), step)):
                chunks.append(Chunk(text=joined[start:start + step], page_number=1, chunk_index=idx))

    return chunks


def ingest_file(path: Path) -> Document:
    ext = path.suffix.lower()
    if ext not in config.ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")

    sha256 = _sha256_of_file(path)
    ocr_count = 0

    logger.info("Chunking started for %s", path.name)
    t0 = time.time()

    if ext == ".pdf":
        pages, ocr_count = _extract_pdf_pages(path)
    else:
        pages = _extract_txt_pages(path)

    pages = _strip_repeated_headers_footers(pages)
    chunks = _chunk_pages(pages)

    elapsed = round(time.time() - t0, 2)
    logger.info(
        "Chunking finished for %s in %.2fs: %d pages, %d chunks, %d OCR'd page(s)",
        path.name, elapsed, len(pages), len(chunks), ocr_count,
    )

    if not chunks:
        raise ValueError(
            "No extractable text was found in this file. It may be empty, "
            "corrupted, or (if a PDF) fully image-based with OCR disabled/failed."
        )

    return Document(
        file_name=path.name,
        extension=ext,
        sha256=sha256,
        full_pages=pages,
        chunks=chunks,
        ocr_pages=ocr_count,
    )
