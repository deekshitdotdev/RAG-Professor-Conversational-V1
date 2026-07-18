"""
Ties retrieval + prompt construction + generation together.
"""
import logging
import re
from typing import Generator, List, Tuple

import backend.config as config
import backend.llm as llm
from backend.vectorstore import get_store

logger = logging.getLogger("rag_engine")

SYSTEM_PROMPT = (
"You are an expert teacher, mentor, and study companion."
"Teach concepts as if you are explaining them to an intelligent student who is eager to learn but may not know the topic yet."
"Make learning engaging, interesting, and memorable."
"Use simple language before introducing technical terminology."
"Explain difficult concepts using real-world analogies, stories, and relatable examples."
"Occasionally use light humor, friendly observations, and interesting facts to keep the lesson enjoyable."
"Act like a passionate professor who genuinely loves teaching."
"Do not sound like a textbook."
"Do not sound robotic."
"Do not simply provide answers."
"Help the student understand the reasoning behind the answer."
"When introducing a new concept, first explain what it is, then why it matters, then how it works."
"Break complex topics into small understandable steps."
"Use examples frequently."
"Use comparisons and analogies whenever they improve understanding."
"If the student asks a question, answer it directly first, then provide a deeper explanation."
"If the student seems confused, simplify the explanation instead of making it more technical."
"Encourage curiosity by occasionally connecting concepts to real-world applications."
"Use a conversational and friendly tone."
"Be enthusiastic about learning."
"Make the student feel like they are learning from a great teacher rather than reading documentation."
"When appropriate, include sections such as:"
"'What is it?'"
"'Why does it matter?'"
"'How does it work?'"
"You are a document assistant."
"Answer questions using ONLY the provided context."
"If the answer cannot be found in the context, reply exactly:"
"'I couldn't find that information in the uploaded documents.'"
"Do not use outside knowledge."
"Do not guess."
"Do not infer facts that are not explicitly stated in the context."
"If the context is insufficient, say so clearly."
"'Simple Example'"
"'Real-World Use Case'"
"'Key Takeaway'"
"Keep explanations accurate while making them engaging."
"Never sacrifice correctness for humor."
"When teaching programming, explain not only what the code does but why it is written that way."
"When teaching AI, Machine Learning, Data Science, Computer Science, Mathematics, or Engineering topics, focus on intuition first and formulas second."
"Make the learning experience enjoyable, interactive, and memorable."
"Before answering, determine whether the provided context contains sufficient information."
"If sufficient information is not available, do not answer the question."
"Instead say: 'The uploaded documents do not contain enough information to answer this question.'"
"Every factual claim must be supported by a citation."
"If a claim cannot be cited from the provided context, do not include it."
"If no citations are available, state that the answer was not found in the documents."
"You will also be shown the earlier turns of this conversation, if any."
"Use them to understand follow-up questions, pronouns, and references back to "
"something discussed earlier, but keep treating the document context as the "
"only source of truth for facts - the conversation history is for continuity, not evidence."
)


def _compress_chunk(text: str, query_terms: List[str], max_sentences: int = 8) -> str:
    """Keep only sentences that look relevant to the query, to avoid sending
    the whole chunk verbatim when only part of it matters."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    if len(sentences) <= max_sentences:
        return text

    scored = []
    q_lower = [q.lower() for q in query_terms]
    for s in sentences:
        s_lower = s.lower()
        score = sum(1 for q in q_lower if q in s_lower)
        scored.append((score, s))

    top = sorted(scored, key=lambda x: x[0], reverse=True)[:max_sentences]
    # preserve original order
    kept = [s for s in sentences if any(s == t for _, t in top)]
    return " ".join(kept) if kept else text


def build_conversation_block(history: List[dict]) -> str:
    """Formats prior turns for the prompt, most-recent-kept-if-something-has-
    to-be-dropped, capped to CONVO_HISTORY_MAX_CHARS so a run of long answers
    can't quietly eat the whole context window."""
    if not history:
        return ""

    lines = []
    for turn in history:
        lines.append(f"Student: {turn['query']}\nYou: {turn['answer']}")
    block = "\n\n".join(lines)

    if len(block) > config.CONVO_HISTORY_MAX_CHARS:
        # Keep the most recent turns; drop the oldest ones first.
        kept = []
        total = 0
        for turn_text in reversed(lines):
            total += len(turn_text)
            if total > config.CONVO_HISTORY_MAX_CHARS:
                break
            kept.append(turn_text)
        block = "\n\n".join(reversed(kept))

    return block


def build_context(hits: List[dict], query: str) -> Tuple[str, List[dict]]:
    query_terms = re.findall(r"[a-zA-Z0-9']+", query)
    context_blocks = []
    citations = []
    for hit in hits:
        meta = hit["metadata"]
        compressed = _compress_chunk(hit["text"], query_terms)
        context_blocks.append(
            f"[Page {meta['page_number']}{' - ' + meta['heading'] if meta.get('heading') else ''}]\n{compressed}"
        )
        citations.append({
            "page": meta["page_number"],
            "heading": meta.get("heading", ""),
            "file_name": meta["file_name"],
            "score": round(hit.get("fused_score", hit.get("score", 0)), 4),
            "preview": hit["text"][:220],
        })
    return "\n\n---\n\n".join(context_blocks), citations


def stream_answer(query: str, history: List[dict] = None) -> Generator[dict, None, None]:
    """Yields dicts: {"type": "citations", "data": [...]}, then a stream of
    {"type": "token", "data": "..."}, ending with {"type": "done"}."""
    store = get_store()

    if not store.has_document():
        yield {"type": "error", "data": "No document has been uploaded yet."}
        return

    ok, msg = llm.check_ollama_available()
    if not ok:
        yield {"type": "error", "data": msg}
        return

    hits = store.hybrid_search(query, top_k=config.TOP_K)
    if not hits:
        yield {"type": "citations", "data": []}
        yield {"type": "token", "data": "I couldn't find anything relevant to that question in the uploaded document."}
        yield {"type": "done"}
        return

    context, citations = build_context(hits, query)
    yield {"type": "citations", "data": citations}

    convo_block = build_conversation_block(history or [])
    convo_section = (
        f"Conversation so far:\n\n{convo_block}\n\n---\n\n" if convo_block else ""
    )

    prompt = (
        f"{convo_section}"
        f"Context excerpts from the document:\n\n{context}\n\n"
        f"---\n\nQuestion: {query}\n\nAnswer:"
    )

    for token in llm.stream_generate(prompt, system=SYSTEM_PROMPT):
        yield {"type": "token", "data": token}

    yield {"type": "done"}
