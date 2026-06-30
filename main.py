"""Telegram botni ishga tushirish."""
import asyncio
import logging
from src.config import settings
from src.bot import build_application


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    print("🔧 Konfiguratsiya tekshirilmoqda...")
    try:
        settings.validate()
    except ValueError as exc:
        print(f"\n❌ {exc}\n")
        print("💡 .env faylni to'g'ri to'ldiring (namuna uchun .env.example ga qarang).")
        return

    print(f"✅ Sozlamalar OK. LLM: {settings.LLM_MODEL}, Embedding: {settings.EMBEDDING_MODEL}")
    print(f"📚 Vektor omborida: {__import__('src.vector_store', fromlist=['vector_store']).vector_store.count} ta telefon")

    app = build_application()
    print("🚀 Bot ishga tushdi. To'xtatish uchun Ctrl+C bosing.")
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
