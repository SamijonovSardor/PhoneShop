"""OpenRouter API orqali embedding yaratish.

OpenRouter OpenAI-ga mos API taqdim etadi, shuning uchun openai SDK
bilan maxsus base_url orqali ishlaydi.
"""
from typing import List
from openai import OpenAI
from .config import settings


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
        response = self._client.embeddings.create(
            input=text,
            model=self.model,
            encoding_format="float",
        )
        return response.data[0].embedding

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Bir nechta matnlar uchun embeddinglar ro'yxatini qaytaradi."""
        if not texts:
            return []
        response = self._client.embeddings.create(
            input=texts,
            model=self.model,
            encoding_format="float",
        )
        return [item.embedding for item in response.data]


embeddings_client = OpenRouterEmbeddings()
