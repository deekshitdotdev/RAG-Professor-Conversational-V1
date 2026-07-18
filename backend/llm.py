"""
Thin client for a locally running Ollama server. Streams tokens as they're
generated so the frontend can show them live, ChatGPT-style. Also exposes
model listing/switching and a one-shot vision call used for OCR.
"""
import base64
import json
import logging
from typing import Generator, List, Optional

import requests

import backend.config as config
import backend.runtime_state as runtime_state

logger = logging.getLogger("llm")


def list_installed_models() -> List[str]:
    try:
        resp = requests.get(f"{config.OLLAMA_HOST}/api/tags", timeout=5)
        resp.raise_for_status()
        return [m["name"] for m in resp.json().get("models", [])]
    except requests.exceptions.RequestException as e:
        logger.warning("Could not list Ollama models: %s", e)
        return []


def check_ollama_available():
    try:
        resp = requests.get(f"{config.OLLAMA_HOST}/api/tags", timeout=3)
        resp.raise_for_status()
        models = [m["name"] for m in resp.json().get("models", [])]
    except requests.exceptions.RequestException as e:
        return False, f"Cannot reach Ollama at {config.OLLAMA_HOST}. Is 'ollama serve' running? ({e})"

    chat_model = runtime_state.get_chat_model()
    if chat_model not in models:
        return False, f"Model '{chat_model}' isn't pulled yet. Run: ollama pull {chat_model}"
    return True, "ok"


def _generate_once(prompt: str, system: str, model: Optional[str]) -> Generator[str, None, None]:
    """Single call to /api/generate. Yields text chunks, and stashes the
    done_reason Ollama reported on the sentinel dict yielded last (internal
    use only - stream_generate below unwraps this)."""
    payload = {
        "model": model or runtime_state.get_chat_model(),
        "prompt": prompt,
        "system": system,
        "stream": True,
        "options": {
            "temperature": config.LLM_TEMPERATURE,
            "num_ctx": config.LLM_NUM_CTX,
            "num_predict": config.LLM_MAX_TOKENS,
        },
    }
    done_reason = None
    try:
        with requests.post(
            f"{config.OLLAMA_HOST}/api/generate", json=payload, stream=True, timeout=300
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                data = json.loads(line.decode("utf-8"))
                if "response" in data:
                    yield data["response"]
                if data.get("done"):
                    done_reason = data.get("done_reason")
                    break
    except requests.exceptions.RequestException as e:
        logger.error("Ollama generation failed: %s", e)
        yield f"\n\n[Error contacting local LLM: {e}]"
        done_reason = "error"
    yield {"__done_reason__": done_reason}


def stream_generate(prompt: str, system: str = "", model: Optional[str] = None) -> Generator[str, None, None]:
    """Streams tokens for a single answer. If Ollama stops because it hit
    num_predict (done_reason == "length") rather than because it actually
    finished, this transparently asks the model to continue from exactly
    where it left off, so callers never see an answer cut off mid-sentence.
    """
    accumulated = ""
    current_prompt = prompt

    for attempt in range(config.LLM_MAX_AUTO_CONTINUATIONS + 1):
        done_reason = None
        for item in _generate_once(current_prompt, system, model):
            if isinstance(item, dict):
                done_reason = item.get("__done_reason__")
                continue
            accumulated += item
            yield item

        if done_reason != "length":
            return  # finished normally, or errored - either way, stop here

        if attempt == config.LLM_MAX_AUTO_CONTINUATIONS:
            break  # give up rather than loop forever on a stuck generation

        logger.info("Answer hit the token cap, auto-continuing (attempt %d)", attempt + 1)
        current_prompt = (
            f"{prompt}\n\n---\n\nYou already began answering this. Your answer so far:\n\n"
            f"{accumulated}\n\n---\n\nContinue the answer above exactly from where it left "
            f"off. Do not repeat anything already written, do not restart, and do not add "
            f"a new preamble - just continue the sentence/thought naturally."
        )


def vision_extract_text(image_bytes: bytes, prompt: Optional[str] = None, model: Optional[str] = None) -> str:
    """One-shot (non-streaming) call to a vision model. Used for OCR of
    scanned PDF pages, and reusable for general image/screenshot questions."""
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    payload = {
        "model": model or runtime_state.get_vision_model(),
        "prompt": prompt or (
            "Transcribe all readable text from this image exactly as it appears, "
            "preserving line breaks and reading order. Output only the transcribed "
            "text, no commentary."
        ),
        "images": [image_b64],
        "stream": False,
        "options": {"temperature": 0.0},
    }
    resp = requests.post(
        f"{config.OLLAMA_HOST}/api/generate",
        json=payload,
        timeout=config.OCR_TIMEOUT_SECONDS,
    )
    resp.raise_for_status()
    return resp.json().get("response", "").strip()
