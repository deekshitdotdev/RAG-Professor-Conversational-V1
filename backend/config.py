"""
Central configuration for the Offline RAG Assistant.
Everything here can be overridden with environment variables so you never
have to hunt through code to change a setting.

Tuned for: RTX 3050 Laptop (6GB VRAM) + 16GB DDR5 RAM.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
CHROMA_DIR = DATA_DIR / "chroma"
HISTORY_FILE = DATA_DIR / "history.json"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Embedding model
# ---------------------------------------------------------------------------
# bge-base is noticeably more accurate than bge-small; on a single document
# CPU encoding is fast enough (a 40 page PDF embeds in a few seconds) that
# there is no real reason to burn your 6GB of VRAM on it and fight Ollama
# for space. Set EMBEDDING_DEVICE=cuda if you really want GPU embeddings,
# but then drop the LLM to a 4B model so both fit.
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5")
EMBEDDING_MODEL_FALLBACK = "BAAI/bge-small-en-v1.5"
EMBEDDING_DEVICE = os.environ.get("EMBEDDING_DEVICE", "cpu")  # "cpu" or "cuda"
EMBEDDING_BATCH_SIZE = int(os.environ.get("EMBEDDING_BATCH_SIZE", "32"))

# ---------------------------------------------------------------------------
# Reranker (optional - off by default to save resources on a laptop GPU)
# ---------------------------------------------------------------------------
USE_RERANKER = os.environ.get("USE_RERANKER", "false").lower() == "true"
RERANKER_MODEL = "BAAI/bge-reranker-base"
RERANKER_DEVICE = os.environ.get("RERANKER_DEVICE", "cpu")

# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------
CHUNK_SIZE_TOKENS = int(os.environ.get("CHUNK_SIZE_TOKENS", "700"))
CHUNK_OVERLAP_TOKENS = int(os.environ.get("CHUNK_OVERLAP_TOKENS", "50"))
# rough heuristic, ~4 chars per token for English text
CHARS_PER_TOKEN = 4
CHUNK_SIZE_CHARS = CHUNK_SIZE_TOKENS * CHARS_PER_TOKEN
CHUNK_OVERLAP_CHARS = CHUNK_OVERLAP_TOKENS * CHARS_PER_TOKEN

# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------
TOP_K = int(os.environ.get("TOP_K", "5"))
CANDIDATE_K = int(os.environ.get("CANDIDATE_K", "20"))  # candidates before fusion/rerank
RRF_K = 60  # standard reciprocal-rank-fusion constant

# ---------------------------------------------------------------------------
# LLM (served locally by Ollama)
# ---------------------------------------------------------------------------
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434")
# Text chat / coding / math -> qwen3:8b (~5.5GB at Q4, tightest fit in 6GB
# VRAM but this is what you asked for; drop to qwen3:4b-instruct if it
# ever spills to CPU and feels slow).
LLM_MODEL = os.environ.get("LLM_MODEL", "qwen3:8b")
LLM_TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.2"))
# 4096 was too tight once conversation history + retrieved chunks + a verbose
# system prompt are all in the same context window - raised to 8192 so there
# is still headroom left for the answer itself. Lower this back down if your
# GPU can't fit it (it will just spill to CPU and get slow, not crash).
LLM_NUM_CTX = int(os.environ.get("LLM_NUM_CTX", "8192"))
# 1024 was the main cause of answers stopping mid-sentence: Ollama hits this
# cap (done_reason="length") before the model reaches a natural stopping
# point. Raised the cap, and llm.py now also auto-continues generation if it
# still gets cut off, so this is a soft limit rather than a hard wall.
LLM_MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", "2048"))
# How many times to auto-continue a single answer if Ollama stops because it
# hit LLM_MAX_TOKENS rather than because it was actually done.
LLM_MAX_AUTO_CONTINUATIONS = int(os.environ.get("LLM_MAX_AUTO_CONTINUATIONS", "3"))

# ---------------------------------------------------------------------------
# Conversation memory
# ---------------------------------------------------------------------------
# How many previous question/answer pairs to feed back into the prompt so
# the model can handle follow-ups ("what about page 3?", "explain that more").
# Kept modest since it eats into LLM_NUM_CTX along with the document context.
CONVO_HISTORY_TURNS = int(os.environ.get("CONVO_HISTORY_TURNS", "6"))
# Hard cap (characters) on how much of the conversation history text gets
# sent, so a handful of long answers can't quietly blow the context window.
CONVO_HISTORY_MAX_CHARS = int(os.environ.get("CONVO_HISTORY_MAX_CHARS", "6000"))

# ---------------------------------------------------------------------------
# Vision model - used ONLY for OCR of scanned/image-only PDF pages, image
# understanding, and screenshot/GUI debugging. Kept small (2B) on purpose:
# Ollama swaps models in/out of VRAM automatically so this and qwen3:8b
# don't both have to fit at once.
# ---------------------------------------------------------------------------
VISION_MODEL = os.environ.get("VISION_MODEL", "qwen3-vl:2b")
AUTO_OCR = os.environ.get("AUTO_OCR", "true").lower() == "true"
# If a PDF page extracts fewer than this many characters, treat it as
# scanned/image-only and OCR it with the vision model instead.
OCR_MIN_CHARS_PER_PAGE = int(os.environ.get("OCR_MIN_CHARS_PER_PAGE", "40"))
OCR_MAX_PAGES = int(os.environ.get("OCR_MAX_PAGES", "60"))  # safety cap
OCR_RENDER_DPI = int(os.environ.get("OCR_RENDER_DPI", "150"))
OCR_TIMEOUT_SECONDS = int(os.environ.get("OCR_TIMEOUT_SECONDS", "120"))

# ---------------------------------------------------------------------------
# Uploads
# ---------------------------------------------------------------------------
ALLOWED_EXTENSIONS = {".pdf", ".txt"}
MAX_FILE_SIZE_MB = int(os.environ.get("MAX_FILE_SIZE_MB", "200"))

COLLECTION_NAME = "current_document"
