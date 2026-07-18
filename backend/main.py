"""
Offline RAG Assistant - FastAPI backend.

Run with:  uvicorn main:app --host 127.0.0.1 --port 8000
(see README.md for full setup instructions)
"""
import json
import logging
import shutil
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import backend.config as config
import backend.llm as llm
import backend.runtime_state as runtime_state
import backend.system_monitor as system_monitor
from backend.ingestion import ingest_file
from backend.vectorstore import get_store

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("main")

app = FastAPI(title="Offline RAG Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Guarantee every error response is JSON. Without this, an uncaught
    exception falls through to Starlette's default plain-text 'Internal
    Server Error', which breaks any frontend that does resp.json()."""
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": f"Internal error: {exc}"})


FRONTEND_DIR = config.BASE_DIR / "frontend"


class AskRequest(BaseModel):
    query: str


class ModelSwitchRequest(BaseModel):
    role: str  # "chat" or "vision"
    model: str


# ---------------------------------------------------------------------------
# Chat history - simple JSON file, no DB needed for this scope
# ---------------------------------------------------------------------------
def _load_history() -> list:
    if config.HISTORY_FILE.exists():
        try:
            return json.loads(config.HISTORY_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
    return []


def _save_history(history: list):
    config.HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")


def _append_history(entry: dict):
    history = _load_history()
    history.append(entry)
    _save_history(history)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api/status")
def status():
    store = get_store()
    doc_info = None
    if store.doc_meta:
        doc_info = {
            "file_name": store.doc_meta.file_name,
            "pages": len(store.doc_meta.full_pages),
            "chunks": len(store.doc_meta.chunks),
            "ocr_pages": store.doc_meta.ocr_pages,
            "embed_seconds": store.last_embed_seconds,
        }
    ollama_ok, ollama_msg = llm.check_ollama_available()
    return {
        "system": system_monitor.get_status(),
        "current_document": doc_info,
        "ollama": {
            "available": ollama_ok,
            "message": ollama_msg,
            "chat_model": runtime_state.get_chat_model(),
            "vision_model": runtime_state.get_vision_model(),
        },
    }


@app.get("/api/models")
def get_models():
    """List models Ollama has pulled, so the UI can offer a dropdown."""
    installed = llm.list_installed_models()
    return {
        "installed": installed,
        "chat_model": runtime_state.get_chat_model(),
        "vision_model": runtime_state.get_vision_model(),
        "recommended_chat": config.LLM_MODEL,
        "recommended_vision": config.VISION_MODEL,
    }


@app.post("/api/model")
def set_model(req: ModelSwitchRequest):
    if req.role == "chat":
        runtime_state.set_chat_model(req.model)
    elif req.role == "vision":
        runtime_state.set_vision_model(req.model)
    else:
        raise HTTPException(400, "role must be 'chat' or 'vision'")
    return {"role": req.role, "model": req.model}


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in config.ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type '{ext}'. Only PDF and TXT are supported.")

    temp_path = config.UPLOAD_DIR / f"{uuid.uuid4().hex}{ext}"
    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        size_mb = temp_path.stat().st_size / 1024 / 1024
        if size_mb > config.MAX_FILE_SIZE_MB:
            raise HTTPException(400, f"File too large ({size_mb:.1f}MB). Max is {config.MAX_FILE_SIZE_MB}MB.")

        try:
            chunk_start = time.time()
            document = ingest_file(temp_path)
            chunk_seconds = round(time.time() - chunk_start, 2)

            store = get_store()
            store.index_document(document)
            # A new document means old conversation turns no longer apply.
            runtime_state.reset_conversation()
        except ValueError as e:
            # Known, explainable failure (empty file, no extractable text, etc.)
            raise HTTPException(400, str(e))
        except Exception as e:
            logger.exception("Failed to process %s", file.filename)
            raise HTTPException(500, f"Failed to process document: {e}")

        return {
            "file_name": file.filename,
            "pages": len(document.full_pages),
            "chunks": len(document.chunks),
            "ocr_pages": document.ocr_pages,
            "chunk_seconds": chunk_seconds,
            "embed_seconds": store.last_embed_seconds,
            "seconds": round(chunk_seconds + store.last_embed_seconds, 2),
        }
    finally:
        # Never keep uploaded files on disk after indexing.
        if temp_path.exists():
            temp_path.unlink()


@app.post("/api/ask")
def ask(req: AskRequest):
    store = get_store()
    if not store.has_document():
        raise HTTPException(400, "No document uploaded yet. Upload a PDF or TXT first.")

    if not req.query or not req.query.strip():
        raise HTTPException(400, "Question can't be empty.")

    history = runtime_state.get_conversation()

    def event_stream():
        full_answer = []
        citations = []
        for event in _stream_answer_safe(req.query, history):
            if event["type"] == "citations":
                citations = event["data"]
            elif event["type"] == "token":
                full_answer.append(event["data"])
            yield json.dumps(event) + "\n"

        if full_answer:
            answer_text = "".join(full_answer)
            _append_history({
                "timestamp": time.time(),
                "query": req.query,
                "answer": answer_text,
                "citations": citations,
                "document": store.doc_meta.file_name if store.doc_meta else None,
            })
            # Record the turn so the *next* question can see it as context -
            # this is what lets the assistant remember what was just discussed.
            runtime_state.append_turn(req.query, answer_text)

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")


def _stream_answer_safe(query: str, history: list):
    from backend.rag_engine import stream_answer
    try:
        yield from stream_answer(query, history)
    except Exception as e:
        logger.exception("Error while answering query")
        yield {"type": "error", "data": f"Unexpected error: {e}"}
        yield {"type": "done"}


@app.get("/api/history")
def get_history():
    return _load_history()


@app.delete("/api/history")
def clear_history():
    _save_history([])
    runtime_state.reset_conversation()
    return {"status": "cleared"}


@app.delete("/api/document")
def clear_document():
    get_store().reset()
    runtime_state.reset_conversation()
    return {"status": "cleared"}


app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
