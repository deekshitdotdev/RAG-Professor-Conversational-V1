"""
Embedding model wrapper. Runs on CPU by default (see config.py for why) -
falls back to a smaller model automatically if the primary one fails to
load (e.g. no internet on very first run and no cached weights yet).
"""
import logging
from typing import List

import torch
from sentence_transformers import SentenceTransformer

import backend.config as config

logger = logging.getLogger("embeddings")


class EmbeddingModel:
    def __init__(self):
        self.device = self._resolve_device()
        self.model_name = config.EMBEDDING_MODEL
        try:
            self.model = SentenceTransformer(self.model_name, device=self.device)
        except Exception as e:
            logger.warning(
                "Failed to load %s (%s). Falling back to %s.",
                self.model_name, e, config.EMBEDDING_MODEL_FALLBACK,
            )
            self.model_name = config.EMBEDDING_MODEL_FALLBACK
            self.model = SentenceTransformer(self.model_name, device=self.device)
        logger.info("Embedding model '%s' loaded on %s", self.model_name, self.device)

    @staticmethod
    def _resolve_device() -> str:
        requested = config.EMBEDDING_DEVICE
        if requested == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA requested for embeddings but not available. Using CPU.")
            return "cpu"
        return requested

    def encode(self, texts: List[str], is_query: bool = False) -> List[List[float]]:
        if not texts:
            return []
        # bge models recommend an instruction prefix for queries only
        if is_query and "bge" in self.model_name.lower():
            texts = [f"Represent this sentence for searching relevant passages: {t}" for t in texts]
        embeddings = self.model.encode(
            texts,
            batch_size=config.EMBEDDING_BATCH_SIZE,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embeddings.tolist()


_embedding_model_singleton: EmbeddingModel | None = None


def get_embedding_model() -> EmbeddingModel:
    global _embedding_model_singleton
    if _embedding_model_singleton is None:
        _embedding_model_singleton = EmbeddingModel()
    return _embedding_model_singleton
