"""OpenRouter API orqali embedding yaratish.

OpenRouter OpenAI-ga mos API taqdim etadi, shuning uchun openai SDK
bilan maxsus base_url orqali ishlaydi.
"""
import time
import logging
from typing import List
from openai import OpenAI
from .config import settings

logger = logging.getLogger(__name__)

BATCH_SIZE = 64
MAX_RETRIES = 3
RETRY_DELAY = 2.0


class OpenRouterEmbeddings:
    """OpenRouter orqali vektor embedding hosil qilish."""

    def __init__(self, model: str | None = None) -> None:
        self.model = model or settings.EMBEDDING_MODEL
        self._client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
        )

    def embed_query(self, text: str) -> List[float]:
        """Bitta matn uchun embedding qaytaradi."""
        return self._embed_with_retry([text])[0]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Bir nechta matnlar uchun embeddinglar ro'yxatini qaytaradi.

        Katta hajmli matnlar uchun BATCH_SIZE ga bo'lib yuboradi va
        har bir batch uchun qayta urinish (retry) qiladi.
        """
        if not texts:
            return []
        all_embeddings: List[List[float]] = []
        total = len(texts)
        for start in range(0, total, BATCH_SIZE):
            batch = texts[start:start + BATCH_SIZE]
            logger.info(
                "Embedding batch %d-%d / %d (model=%s)",
                start + 1, min(start + BATCH_SIZE, total), total, self.model,
            )
            batch_embeddings = self._embed_with_retry(batch)
            all_embeddings.extend(batch_embeddings)
        return all_embeddings

    def _embed_with_retry(self, texts: List[str]) -> List[List[float]]:
        last_error: Exception | None = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = self._client.embeddings.create(
                    input=texts,
                    model=self.model,
                    encoding_format="float",
                )
                if not response.data:
                    raise ValueError("Bo'sh data qaytdi")
                return [item.embedding for item in response.data]
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Embedding urinish %d/%d muvaffaqiyatsiz: %s",
                    attempt, MAX_RETRIES, exc,
                )
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY * attempt)
        raise RuntimeError(
            f"Embedding {MAX_RETRIES} urinishdan keyin ham muvaffaqiyatsiz: {last_error}"
        )


embeddings_client = OpenRouterEmbeddings()
