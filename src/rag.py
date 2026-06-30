"""RAG (Retrieval-Augmented Generation) pipeline.

Jarayon:
  1. Foydalanuvchi savolini embeddingga aylantiramiz
  2. Vektor omboridan eng mos telefonlarni topamiz
  3. Topilgan telefonlarni kontekst sifatida LLM ga beramiz
  4. LLM kontekst asosida javob generatsiya qiladi
"""
from typing import List, Dict, Any
from openai import OpenAI
from .config import settings
from .vector_store import vector_store


SYSTEM_PROMPT = """Sen PhoneShop kompaniyasining aqlli yordamchisisan.
Vazifang: faqat berilgan KONTEKST (telefonlar katalogi) asosida foydalanuvchiga
o'zbek tilida aniq, foydali va do'stona javob berish.

QOIDALAR:
1. Faqat kontekstda berilgan ma'lumotlardan foydalan. Tashqi bilim ishlatma.
2. Agar kontekstda foydalanuvchi so'ragan telefon yoki xususiyat bo'lmasa,
   halol ayt: "Kechirasiz, bazamizda bunday telefon topilmadi" va
   o'xshash tavsiyalar ber.
3. Narxlarni doimo $ belgisi bilan ko'rsat (masalan: $350). Boshqa valyuta ishlatma.
4. Tavsiya berayotganda telefonning BRENDI, MODELI, NARXI va asosiy
   xususiyatlarini (RAM, xotira, kamera, batareya, ekran) albatta ko'rsat.
5. Foydalanuvchining byudjeti va ehtiyojiga moslab, eng yaxshi 1-3 variantni tavsiya qil.
6. Agar foydalanuvchi byudjet ko'rsatsa, FAQAT shu oraliqdagi telefonlarni tavsiya qil.
7. Foydalanuvchiga qaysi brend yoki model kerakligini aniqlashtiruvchi savol ber, agar
   so'rov juda umumiy bo'lsa (masalan: "yaxshi telefon" desа).
8. Javobni qisqa, lekin to'liq va tushunarli qilib yoz. Emoji ishlatish mumkin.
"""


class RAGPipeline:
    def __init__(self) -> None:
        self._client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
        )
        self._model = settings.LLM_MODEL
        self._store = vector_store

    def _format_context(self, hits: List[Dict[str, Any]]) -> str:
        if not hits:
            return "(Kontekst bo'sh - bazada tegishli telefon topilmadi)"
        lines = []
        for i, hit in enumerate(hits, start=1):
            meta = hit.get("metadata", {}) or {}
            lines.append(
                f"[{i}] {meta.get('brand', '?')} {meta.get('model', '?')} — "
                f"narxi ${meta.get('price_usd', '?')}, "
                f"RAM {meta.get('ram_gb', '?')} GB, "
                f"xotira {meta.get('storage_gb', '?')} GB, "
                f"ekran {meta.get('screen_size', '?')}\", "
                f"batareya {meta.get('battery_mah', '?')} mAh, "
                f"kamera {meta.get('camera_mp', '?')} MP"
            )
        return "\n".join(lines)

    def ask(self, user_query: str, top_k: int | None = None) -> Dict[str, Any]:
        hits = self._store.search(user_query, top_k=top_k)
        context = self._format_context(hits)

        user_message = (
            f"FOYDALANUVCHI SAVOLI:\n{user_query}\n\n"
            f"KONTEKST (bazadan topilgan telefonlar):\n{context}"
        )

        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.4,
            max_tokens=900,
        )
        answer = response.choices[0].message.content or ""
        return {"answer": answer.strip(), "sources": hits}


rag = RAGPipeline()
