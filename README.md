# PhoneShop RAG Telegram Bot 📱

Kompaniya telefonlar katalogi asosida foydalanuvchiga **Retrieval-Augmented Generation (RAG)** orqali aqlli tavsiyalar beruvchi Telegram bot.

## ✨ Xususiyatlari

- 🔍 **Semantik qidiruv** — foydalanuvchi savolini tushunadi, kalit so'z bilan cheklanmaydi
- 🤖 **RAG pipeline** — LLM faqat bazadagi ma'lumotlar asosida javob beradi (hallucination kamaytirilgan)
- 🌐 **OpenRouter** — bir nechta LLM va embedding modellarni qo'llab-quvvatlaydi
- 💬 **O'zbek tilida** — bot va javoblar o'zbekcha
- 💾 **ChromaDB** — lokal vektor ombor (server kerak emas)

## 🏗 Arxitektura

```
Foydalanuvchi → Telegram → RAG Pipeline → Vector Store (ChromaDB)
                                  ↓
                          OpenRouter API (LLM + Embeddings)
```

Jarayon:
1. Foydalanuvchi savolini yozadi (masalan: "300-400$ telefon kerak, kamera yaxshi bo'lsin")
2. Savol embeddingga aylantiriladi (OpenRouter orqali)
3. ChromaDB dan eng mos 5 ta telefon topiladi
4. Topilgan telefonlar kontekst sifatida LLM ga beriladi
5. LLM kontekst asosida o'zbekcha javob generatsiya qiladi

## 📁 Loyiha strukturasi

```
phone-rag-bot/
├── data/
│   └── phones.json         # 980 ta telefon (CSV dan konvertatsiya)
├── src/
│   ├── config.py          # Sozlamalar
│   ├── embeddings.py      # OpenRouter embeddinglar
│   ├── vector_store.py    # ChromaDB
│   ├── rag.py             # RAG pipeline
│   └── bot.py             # Telegram bot
├── scripts/
│   ├── ingest.py          # phones.json → ChromaDB ga yuklash
│   ├── convert_csv.py     # smartphones.csv → phones.json (transformatsiya)
│   ├── analyze_dataset.py # Dataset tahlili
│   └── verify_phones.py   # phones.json tekshirish
├── tests/
│   └── test_rag.py        # Mock testlar
├── main.py                # Botni ishga tushirish
├── .env.example           # Sozlamalar namunasi
└── requirements.txt
```

## 🚀 O'rnatish

### 1. Reponi klonlash va papkaga kirish
```bash
cd phone-rag-bot
```

### 2. Virtual muhit yaratish
```bash
python -m venv venv
venv\Scripts\activate         # Windows
source venv/bin/activate      # macOS/Linux
```

### 3. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 4. Sozlamalarni to'ldirish
`.env.example` faylidan `.env` yarating va to'ldiring:

```env
# OpenRouter dan olingan API kalit (https://openrouter.ai/keys)
OPENROUTER_API_KEY=sk-or-v1-...

# LLM modeli (bepul: meta-llama/llama-3.3-70b-instruct:free)
LLM_MODEL=meta-llama/llama-3.3-70b-instruct:free

# Embedding modeli
EMBEDDING_MODEL=openai/text-embedding-3-small

# @BotFather dan olingan bot tokeni
TELEGRAM_BOT_TOKEN=1234567890:AA...
```

### 5. Telefonlar bazasini yuklash

**Variant A:** Tayyor `phones.json` fayldan (hozir 980 ta telefon bor):
```bash
python -m scripts.ingest
```

**Variant B:** O'zingizning CSV faylingizdan yangilash:
```bash
# 1) smartphones.csv ni data/phones.json ga o'tkazish
python -m scripts.convert_csv

# 2) Embedding hosil qilib ChromaDB ga saqlash
python -m scripts.ingest
```

`scripts/convert_csv.py` quyidagilarni qiladi:
- UTF-8 BOM belgisini tozalaydi
- Stunlarni moslashtiradi (brand_name → brand, internal_memory → storage_gb, ...)
- Narxni INR dan USD ga o'tkazadi (kurs: 1 USD ≈ 83 INR)
- Har bir telefon uchun tabiiy tildagi tavsif yaratadi
- Dublikat id larni raqam bilan farqlaydi

### 6. Botni ishga tushirish
```bash
python main.py
```

## 💬 Foydalanish

Botdan foydalanish uchun Telegram'da `/start` bosing va savolingizni yozing.

### Misol savollar:
- `300-400$ oralig'ida yaxshi kamera va katta batareyali telefon kerak`
- `Samsung brendida 500$ gacha bo'lgan eng yaxshi model qaysi?`
- `O'yin o'ynash uchun kuchli protsessorli telefon tavsiya qiling`
- `200$ ga qanaqa telefon olish mumkin?`
- `iPhone va Samsung o'rtasida qaysi biri yaxshi?`

## 📞 O'z ma'lumotlaringizni qo'shish

### Variant 1: CSV fayl orqali (tavsiya)

`smartphones.csv` faylini tahrirlang yoki o'zingiznikini qo'ying, keyin:
```bash
python -m scripts.convert_csv   # CSV → JSON transformatsiya
python -m scripts.ingest        # JSON → ChromaDB
```

### Variant 2: JSON faylni qo'lda tahrirlash

`data/phones.json` faylini tahrirlang. Har bir telefon uchun:

```json
{
  "id": "nokia-xr21",
  "brand": "Nokia",
  "model": "XR21",
  "price_usd": 350,
  "ram_gb": 6,
  "storage_gb": 128,
  "screen_size": 6.49,
  "battery_mah": 4800,
  "camera_mp": 64,
  "os": "Android 13",
  "processor": "Snapdragon 695",
  "features": ["IP68/IP69K", "Tezkor zaryadlash", "5G"],
  "description": "O'ta chidamli, suvga va changga chidamli telefon."
}
```

O'zgartirgandan keyin qayta ingest qiling:
```bash
python -m scripts.ingest
```

## 📊 Hozirgi dataset haqida

- **980 ta telefon**, **46 brend**: Apple, Samsung, Xiaomi, Google, OnePlus, Oppo, Vivo, Huawei, Honor, Nokia, Motorola, Sony, Poco, Realme, Redmi, Infinix, Tecno, Asus, Lenovo, ZTE va boshqalar
- **Narxlar**: $42 - $7,831 (USD ga konvertatsiya qilingan, 1 USD ≈ 83 INR)
- **O'rtacha narx**: ~$392
- **300-400 USD oraliq**: 136 ta telefon
- **22 ta xususiyat**: narx, reyting, 5G, protsessor brand/tezligi/yadrolari, batareya, tezkor zaryadlash, RAM, xotira, ekran o'lchami, refresh rate, kameralar soni, OS, rezolyutsiya

## ⚙️ Sozlamalar

| Parametr | Tavsif | Standart |
|---|---|---|
| `LLM_MODEL` | OpenRouter LLM modeli | `meta-llama/llama-3.3-70b-instruct:free` |
| `EMBEDDING_MODEL` | OpenRouter embedding modeli | `openai/text-embedding-3-small` |
| `TOP_K_RESULTS` | Qidiruv natijalari soni | `5` |
| `CHROMA_COLLECTION_NAME` | ChromaDB kolleksiya nomi | `phones` |

### Tavsiya etiladigan modellar:

**Bepul LLM:**
- `meta-llama/llama-3.3-70b-instruct:free`
- `google/gemini-2.0-flash-exp:free`
- `deepseek/deepseek-chat-v3-0324:free`

**Pullik (arzon):**
- `openai/gpt-4o-mini`
- `anthropic/claude-3.5-haiku`

**Embedding:**
- `openai/text-embedding-3-small` — sifatli va arzon
- `openai/text-embedding-3-large` — eng yaxshi sifat

## 🛠 Texnologiyalar

- **Python 3.10+**
- **python-telegram-bot** — Telegram API
- **OpenAI SDK + OpenRouter** — LLM va embeddings
- **ChromaDB** — Vektor ombor
- **Pydantic + python-dotenv** — Konfiguratsiya

## 📄 Litsenziya

MIT
