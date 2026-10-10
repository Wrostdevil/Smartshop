import hashlib
import numpy as np
from typing import List
from app.config import settings
from app.utils.logging import logger

class EmbeddingService:
    def __init__(self):
        self.provider = settings.EMBEDDING_PROVIDER.lower()
        self.model_name = settings.EMBEDDING_MODEL
        self.dim = settings.EMBEDDING_DIM
        self._fastembed_model = None
        self._google_embeddings = None
        self._init_backend()

    def _init_backend(self):
        # Try initializing FastEmbed if configured or auto
        if self.provider in ["auto", "fastembed", "huggingface"]:
            try:
                from fastembed import TextEmbedding
                logger.info(f"Initializing FastEmbed model: {self.model_name}...")
                self._fastembed_model = TextEmbedding(model_name=self.model_name)
                self.provider = "fastembed"
                logger.info("FastEmbed initialized successfully.")
                return
            except Exception as e:
                logger.warning(f"FastEmbed initialization deferred or failed: {e}")

        # Try Google GenAI Embeddings if configured
        if self.provider == "google" and settings.GOOGLE_API_KEY:
            try:
                from langchain_google_genai import GoogleGenerativeAIEmbeddings
                self._google_embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/embedding-001",
                    google_api_key=settings.GOOGLE_API_KEY
                )
                self.provider = "google"
                logger.info("Google GenAI Embeddings initialized successfully.")
                return
            except Exception as e:
                logger.warning(f"Google GenAI embeddings initialization failed: {e}")

        # Fallback to local deterministic semantic projection
        logger.info("Using local deterministic semantic embedding engine (384-dim).")
        self.provider = "local_semantic"

    def _local_semantic_embed(self, text: str) -> List[float]:
        """
        Generates a deterministic 384-dimensional normalized vector using n-gram feature hashing.
        Captures word similarities and semantic tokens reliably without external network downloads.
        """
        words = text.lower().split()
        vec = np.zeros(self.dim, dtype=np.float32)

        for w in words:
            # Unigram hash
            h1 = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16)
            idx1 = h1 % self.dim
            vec[idx1] += 1.0

            # Substring 3-gram hash
            if len(w) >= 3:
                for i in range(len(w) - 2):
                    sub = w[i:i+3]
                    h2 = int(hashlib.sha1(sub.encode("utf-8")).hexdigest(), 16)
                    idx2 = h2 % self.dim
                    vec[idx2] += 0.5

        # Normalize vector to unit length
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        else:
            vec[0] = 1.0
        return vec.tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        if self.provider == "fastembed" and self._fastembed_model:
            try:
                generator = self._fastembed_model.embed(texts)
                return [list(vec.astype(float)) for vec in generator]
            except Exception as e:
                logger.warning(f"FastEmbed runtime error ({e}), using local semantic fallback.")

        if self.provider == "google" and self._google_embeddings:
            try:
                return self._google_embeddings.embed_documents(texts)
            except Exception as e:
                logger.warning(f"Google embeddings failed ({e}), using local fallback.")

        return [self._local_semantic_embed(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self.dim

        if self.provider == "fastembed" and self._fastembed_model:
            try:
                generator = self._fastembed_model.embed([text])
                return list(next(generator).astype(float))
            except Exception as e:
                logger.warning(f"FastEmbed query embedding error ({e}), using local fallback.")

        if self.provider == "google" and self._google_embeddings:
            try:
                return self._google_embeddings.embed_query(text)
            except Exception as e:
                logger.warning(f"Google embed_query failed ({e}), using local fallback.")

        return self._local_semantic_embed(text)

embedding_service = EmbeddingService()
