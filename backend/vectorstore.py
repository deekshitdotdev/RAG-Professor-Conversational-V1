"""
Persistent vector storage (ChromaDB) + an in-memory BM25 index, fused with
Reciprocal Rank Fusion for hybrid semantic + keyword search.

Since this app handles one document at a time, uploading a new file resets
the collection. Nothing is lost for the *previous* document other than the
index itself (the original file was already deleted after ingestion, per
the "never keep uploaded files" requirement).
"""
import logging
import re
import time
from typing import List, Optional

import chromadb
from chromadb.config import Settings
from rank_bm25 import BM25Okapi

import backend.config as config
from backend.embeddings import get_embedding_model
from backend.ingestion import Chunk, Document

logger = logging.getLogger("vectorstore")

_TOKEN_RE = re.compile(r"[a-zA-Z0-9']+")


def _tokenize(text: str) -> List[str]:
    return _TOKEN_RE.findall(text.lower())


class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=str(config.CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self._get_or_create_collection()
        self.bm25: Optional[BM25Okapi] = None
        self.bm25_corpus_ids: List[str] = []
        self.doc_meta: Optional[Document] = None
        self.last_embed_seconds: float = 0.0
        self._rebuild_bm25_from_existing()

    def _get_or_create_collection(self):
        return self.client.get_or_create_collection(
            name=config.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def _rebuild_bm25_from_existing(self):
        """On startup, if a document was already indexed in a previous run,
        rebuild the BM25 index from what's already in Chroma."""
        try:
            existing = self.collection.get(include=["documents", "metadatas"])
            if existing and existing.get("ids"):
                docs = existing["documents"]
                self.bm25_corpus_ids = existing["ids"]
                self.bm25 = BM25Okapi([_tokenize(d) for d in docs])
                logger.info("Restored BM25 index for %d existing chunks", len(docs))
        except Exception as e:
            logger.warning("Could not restore BM25 index: %s", e)

    def reset(self):
        """Wipe the collection for a fresh single-document upload."""
        try:
            self.client.delete_collection(config.COLLECTION_NAME)
        except Exception:
            pass
        self.collection = self._get_or_create_collection()
        self.bm25 = None
        self.bm25_corpus_ids = []
        self.doc_meta = None

    def index_document(self, document: Document):
        self.reset()
        embedder = get_embedding_model()

        ids, texts, metadatas = [], [], []
        for chunk in document.chunks:
            cid = f"{document.sha256[:12]}-{chunk.chunk_index}"
            ids.append(cid)
            texts.append(chunk.text)
            metadatas.append({
                "doc_id": document.sha256[:12],
                "file_name": document.file_name,
                "extension": document.extension,
                "page_number": chunk.page_number,
                "heading": chunk.heading,
                "chunk_index": chunk.chunk_index,
                "sha256": document.sha256,
            })

        if not texts:
            raise ValueError("Document produced no chunks to index.")

        logger.info("Embedding started for %s: %d chunks on %s", document.file_name, len(texts), embedder.device)
        t0 = time.time()
        vectors = embedder.encode(texts, is_query=False)
        embed_seconds = round(time.time() - t0, 2)
        logger.info("Embedding finished for %s in %.2fs", document.file_name, embed_seconds)

        self.collection.add(ids=ids, embeddings=vectors, documents=texts, metadatas=metadatas)
        self.last_embed_seconds = embed_seconds

        self.bm25_corpus_ids = ids
        self.bm25 = BM25Okapi([_tokenize(t) for t in texts])
        self.doc_meta = document

        logger.info("Indexed %d chunks for %s", len(texts), document.file_name)

    def has_document(self) -> bool:
        return self.collection.count() > 0

    def vector_search(self, query: str, top_k: int) -> List[dict]:
        embedder = get_embedding_model()
        query_vec = embedder.encode([query], is_query=True)[0]
        results = self.collection.query(
            query_embeddings=[query_vec],
            n_results=min(top_k, max(1, self.collection.count())),
            include=["documents", "metadatas", "distances"],
        )
        hits = []
        for i, cid in enumerate(results["ids"][0]):
            hits.append({
                "id": cid,
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "score": 1 - results["distances"][0][i],  # cosine distance -> similarity
            })
        return hits

    def bm25_search(self, query: str, top_k: int) -> List[dict]:
        if not self.bm25:
            return []
        scores = self.bm25.get_scores(_tokenize(query))
        ranked = sorted(
            zip(self.bm25_corpus_ids, scores), key=lambda x: x[1], reverse=True
        )[:top_k]

        all_data = self.collection.get(ids=[cid for cid, _ in ranked], include=["documents", "metadatas"])
        by_id = {
            cid: (doc, meta)
            for cid, doc, meta in zip(all_data["ids"], all_data["documents"], all_data["metadatas"])
        }
        hits = []
        for cid, score in ranked:
            if cid in by_id and score > 0:
                doc, meta = by_id[cid]
                hits.append({"id": cid, "text": doc, "metadata": meta, "score": float(score)})
        return hits

    def hybrid_search(self, query: str, top_k: int = config.TOP_K) -> List[dict]:
        vec_hits = self.vector_search(query, config.CANDIDATE_K)
        bm25_hits = self.bm25_search(query, config.CANDIDATE_K)

        # Reciprocal Rank Fusion
        rrf_scores: dict = {}
        chunk_lookup: dict = {}
        for rank_list in (vec_hits, bm25_hits):
            for rank, hit in enumerate(rank_list):
                rrf_scores[hit["id"]] = rrf_scores.get(hit["id"], 0.0) + 1.0 / (config.RRF_K + rank + 1)
                chunk_lookup[hit["id"]] = hit

        fused = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [{**chunk_lookup[cid], "fused_score": score} for cid, score in fused]


_store_singleton: Optional[VectorStore] = None


def get_store() -> VectorStore:
    global _store_singleton
    if _store_singleton is None:
        _store_singleton = VectorStore()
    return _store_singleton
