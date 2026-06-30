"""Loyiha konfiguratsiyasi - .env fayldan sozlamalarni o'qiydi."""
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class Settings:
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    LLM_MODEL: str = os.getenv("LLM_MODEL", "meta-llama/llama-3.3-70b-instruct:free")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "openai/text-embedding-3-small")

    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "phones")

    PHONES_DATA_PATH: str = os.getenv("PHONES_DATA_PATH", "./data/phones.json")

    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "5"))

    APP_NAME: str = "PhoneShop RAG Bot"
    APP_URL: str = "https://github.com/your-username/phone-rag-bot"

    def validate(self) -> None:
        errors = []
        if not self.OPENROUTER_API_KEY or self.OPENROUTER_API_KEY.startswith("sk-or-v1-xxx"):
            errors.append("OPENROUTER_API_KEY to'g'ri sozlanmagan (.env faylni tekshiring)")
        if not self.TELEGRAM_BOT_TOKEN or self.TELEGRAM_BOT_TOKEN.startswith("1234567890"):
            errors.append("TELEGRAM_BOT_TOKEN to'g'ri sozlanmagan (.env faylni tekshiring)")
        if errors:
            raise ValueError("Konfiguratsiya xatolari:\n  - " + "\n  - ".join(errors))


settings = Settings()
