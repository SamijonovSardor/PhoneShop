"""Telegram bot - RAG tizimi bilan integratsiyalashgan.

Buyruqlar:
  /start  - Botni boshlash
  /help   - Yordam
  /count  - Bazadagi telefonlar soni
"""
import logging
from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from .config import settings
from .rag import rag
from .vector_store import vector_store

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


WELCOME_MESSAGE = (
    "Assalomu alaykum! Men **PhoneShop** yordamchisiman. 📱\n\n"
    "Menga o'zingiz xohlagan telefonni tavsiflab yozing, men esa kompaniya "
    "bazamizdan sizga eng mos variantlarni topib beraman.\n\n"
    "*Misol savollar:*\n"
    "• 300-400 dollar oralig'ida yaxshi kamera va katta batareyali telefon kerak\n"
    "• Samsung brendida 500 dollar gacha bo'lgan eng yaxshi model qaysi?\n"
    "• O'yin o'ynash uchun kuchli protsessorli telefon tavsiya qiling\n"
    "• 200 dollar ga qanaqa telefon olish mumkin?\n\n"
    "/help - yordam"
)

HELP_MESSAGE = (
    "*Yordam* ℹ️\n\n"
    "Bot sizning savolingizni tushunadi va kompaniya telefonlar "
    "bazasi asosida javob beradi.\n\n"
    "*Buyruqlar:*\n"
    "/start — Botni qayta boshlash\n"
    "/help — Yordam xabari\n"
    "/count — Bazadagi telefonlar soni\n\n"
    "*Maslahatlar:*\n"
    "• Byudjetingizni yozing (masalan: 300-400 dollar)\n"
    "• Brend yoki xususiyat ko'rsating (kamera, batareya, RAM)\n"
    "• Foydalanish maqsadingizni ayting (o'yin, foto, ish)"
)


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode=ParseMode.MARKDOWN)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_MESSAGE, parse_mode=ParseMode.MARKDOWN)


async def count_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        total = vector_store.count
        await update.message.reply_text(f"📚 Bazada jami *{total}* ta telefon mavjud.", parse_mode=ParseMode.MARKDOWN)
    except Exception as exc:
        logger.exception("Count xatosi")
        await update.message.reply_text(f"Xatolik yuz berdi: {exc}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_query = (update.message.text or "").strip()
    if not user_query:
        return

    chat_id = update.effective_chat.id
    logger.info("Foydalanuvchi [%s] savol: %s", chat_id, user_query)

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    try:
        result = rag.ask(user_query)
        answer = result["answer"]

        if result.get("sources"):
            sources_lines = []
            seen = set()
            for src in result["sources"]:
                meta = src.get("metadata", {}) or {}
                key = (meta.get("brand", ""), meta.get("model", ""))
                if key in seen:
                    continue
                seen.add(key)
                price = meta.get("price_usd", "?")
                sources_lines.append(f"• {meta.get('brand', '?')} {meta.get('model', '?')} — ${price}")
            if sources_lines:
                answer += "\n\n_Manzba:_\n" + "\n".join(sources_lines[:5])

        for chunk in _split_message(answer):
            await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
    except Exception as exc:
        logger.exception("RAG xatosi")
        await update.message.reply_text(
            "Kechirasiz, javob tayyorlashda xatolik yuz berdi. "
            "Birozdan so'ng qayta urinib ko'ring. 🙏"
        )


def _split_message(text: str, limit: int = 4000) -> list[str]:
    if len(text) <= limit:
        return [text]
    chunks, current = [], ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > limit:
            chunks.append(current)
            current = line
        else:
            current = f"{current}\n{line}" if current else line
    if current:
        chunks.append(current)
    return chunks


def build_application():
    if not settings.TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN .env faylda ko'rsatilmagan!")

    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("count", count_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    return app
