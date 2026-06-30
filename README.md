# PhoneShop RAG Telegram Bot 📱

Kompaniya telefonlar katalogi asosida foydalanuvchiga **Retrieval-Augmented Generation (RAG)** orqali aqlli tavsiyalar beruvchi Telegram bot. Suhbat tarixini eslab qoladi va shaxsiy tavsiyalar beradi.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue)

## ✨ Xususiyatlari

- 🔍 **Semantik qidiruv** — foydalanuvchi savolini tushunadi, kalit so'z bilan cheklanmaydi
- 🤖 **RAG pipeline** — LLM faqat bazadagi ma'lumotlar asosida javob beradi (hallucination kamaytirilgan)
- 🧠 **Suhbat tarixi** — har bir foydalanuvchi uchun alohida kontekst saqlanadi (SQLite, persistent)
- 🌐 **OpenRouter** — 300+ LLM va embedding modellarni qo'llab-quvvatlaydi
- 💬 **O'zbek tilida** — bot va javoblar to'liq o'zbekcha
- 💾 **ChromaDB** — lokal vektor ombor (server kerak emas)
- ⚡ **Batch + Retry** — katta datasetlar uchun ishonchli embedding
- 🧪 **9 ta test** — RAG va Memory modullari uchun

## 🏗 Arxitektura

```
Foydalanuvchi → Telegram → Bot (memory bilan)
                            ↓
                    RAG Pipeline
                    ┌─────────────┐
                    │ 1. Embedding │  ← OpenRouter (gemini-embedding-2)
                    │ 2. Retrieval │  ← ChromaDB (top 5 natija)
                    │ 3. Augment   │  ← Tarix + Kontekst
                    │ 4. Generate  │  ← OpenRouter (DeepSeek v4 Flash)
                    └─────────────┘
                            ↓
                      O'zbekcha javob
```

**Jarayon:**
1. Foydalanuvchi savolini yozadi
2. Savol + suhbat tarixi → embedding (OpenRouter)
3. ChromaDB dan eng mos 5 ta telefon topiladi
4. Topilgan telefonlar + tarix → LLM ga kontekst sifatida
5. LLM kontekst asosida o'zbekcha javob generatsiya qiladi
6. Suhbat tarixiga saqlanadi (kelajakdagi suhbatlar uchun)

## 📁 Loyiha strukturasi

```
phone-rag-bot/
├── data/
│   ├── phones.json              # 980 ta telefon (CSV dan konvertatsiya)
│   └── conversations.db         # Suhbat tarixi (SQLite, avtomatik)
├── src/
│   ├── config.py                # .env dan sozlamalar
│   ├── embeddings.py            # OpenRouter embedding (batch + retry)
│   ├── vector_store.py          # ChromaDB wrapper
│   ├── rag.py                   # RAG pipeline (system prompt + retrieval + LLM)
│   ├── memory.py                # SQLite conversation memory
│   └── bot.py                   # Telegram bot
├── scripts/
│   ├── ingest.py                # phones.json → ChromaDB
│   ├── convert_csv.py           # smartphones.csv → phones.json
│   ├── analyze_dataset.py       # Dataset statistikasi
│   ├── verify_phones.py         # phones.json tekshirish
│   ├── check_status.py          # ChromaDB holati
│   └── check_models.py          # OpenRouter modellari
├── tests/
│   ├── test_rag.py              # RAG testlari (3 ta)
│   └── test_memory.py           # Memory testlari (6 ta)
├── main.py                      # Botni ishga tushirish
├── .env.example                 # Sozlamalar namunasi
└── requirements.txt
```

## 🚀 O'rnatish

### 1. Reponi klonlash
```bash
git clone https://github.com/SamijonovSardor/PhoneShop.git
cd PhoneShop
```

### 2. Virtual muhit yaratish (tavsiya)
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
`.env.example` dan `.env` yarating:
```bash
cp .env.example .env       # macOS/Linux
copy .env.example .env     # Windows
```

`.env` faylini tahrirlang:

```env
# 1. OpenRouter API kalit — https://openrouter.ai/keys
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx

# 2. LLM modeli (chat uchun)
LLM_MODEL=deepseek/deepseek-v4-flash

# 3. Embedding modeli (qidiruv uchun)
EMBEDDING_MODEL=google/gemini-embedding-2

# 4. @BotFather dan olingan bot tokeni
TELEGRAM_BOT_TOKEN=1234567890:AAxxxxxxxxxxxxx

# 5. Qidiruv natijalari soni (standart: 5)
TOP_K_RESULTS=5
```

### 5. Telefonlar bazasini yuklash
```bash
python -m scripts.ingest
```
⏱ Birinchi marta **2-3 daqiqa** vaqt oladi (980 ta telefon embedding).

### 6. Botni ishga tushirish
```bash
python main.py
```

Telegram'da botga `/start` yozing!

## 💬 Foydalanish

### Bot buyruqlari

| Buyruq | Vazifasi |
|---|---|
| `/start` | Botni boshlash, xush kelibsiz xabari |
| `/help` | Yordam va buyruqlar ro'yxati |
| `/count` | Bazadagi jami telefonlar soni |
| `/source` | Oxirgi javobda ishlatilgan telefonlar |
| `/clear` | Suhbat tarixini tozalash |
| `/stats` | Statistika (bazadagi telefonlar, userlar, sizning tarixingiz) |

### Misol savollar

- `300-400$ li yaxshi kamera va katta batareyali telefon`
- `Samsung 5G 500$ gacha`
- `O'yin uchun eng kuchli protsessorli telefon`
- `iPhone eng arzoni qaysi?`
- `Xiaomi 8GB RAM li arzon telefon`

### Suhbat konteksti

Bot suhbat tarixingizni eslaydi (oxirgi 6 ta xabar):

```
👤 300-400$ li yaxshi telefon kerak
🤖 Vivo V19, Realme 7 Pro, Redmi Note 10 Lite...

👤 Bular orasida eng arzonini ayt
🤖 Eng arzoni - Redmi Note 10 Lite ($144)
    [oldingi suhbat konteksti ishlatildi]

👤 /clear
🤖 🧹 Suhbat tarixingiz tozalandi.
```

## 📊 Hozirgi dataset

- **980 ta telefon**, **46 brend**: Apple, Samsung, Xiaomi, Google, OnePlus, Oppo, Vivo, Huawei, Honor, Nokia, Motorola, Sony, Poco, Realme, Redmi, Infinix, Tecno, Asus, Lenovo, ZTE va boshqalar
- **Narxlar**: $42 - $7,831 (USD ga konvertatsiya qilingan, 1 USD ≈ 83 INR)
- **O'rtacha narx**: ~$392
- **300-400 USD oraliqda**: 136 ta telefon
- **22 ta xususiyat**: narx, reyting, 5G, protsessor, batareya, tezkor zaryadlash, RAM, xotira, ekran, refresh rate, kameralar, OS, rezolyutsiya

## ⚙️ Sozlamalar

| Parametr | Tavsif | Standart |
|---|---|---|
| `LLM_MODEL` | OpenRouter LLM | `meta-llama/llama-3.3-70b-instruct:free` |
| `EMBEDDING_MODEL` | OpenRouter embedding | `openai/text-embedding-3-small` |
| `TOP_K_RESULTS` | Qidiruv natijalari soni | `5` |
| `CHROMA_PERSIST_DIR` | ChromaDB saqlash papkasi | `./chroma_db` |
| `CHROMA_COLLECTION_NAME` | Kolleksiya nomi | `phones` |
| `PHONES_DATA_PATH` | Ma'lumotlar fayli | `./data/phones.json` |

### Tavsiya etiladigan modellar

**Bepul LLM:**
- `meta-llama/llama-3.3-70b-instruct:free`
- `deepseek/deepseek-chat-v3-0324:free`
- `google/gemini-2.0-flash-exp:free`

**Pullik (tez va arzon):**
- `deepseek/deepseek-v4-flash` (hozirda ishlatilayotgan)
- `openai/gpt-4o-mini`
- `anthropic/claude-3.5-haiku`

**Embedding:**
- `google/gemini-embedding-2` — 3072 dim (hozirda ishlatilayotgan)
- `openai/text-embedding-3-small` — 1536 dim, $0.02/M token
- `qwen/qwen3-embedding-8b` — 4096 dim

## 🧪 Testlar

```bash
# RAG testlari (3 ta) - production ma'lumotlarga tegmaydi
python -m tests.test_rag

# Memory testlari (6 ta) - alohida DB bilan
python -m tests.test_memory
```

**Test natijalari:**
- `test_rag.py`: 3/3 ✓ (JSON struktura, document format, qidiruv mantig'i)
- `test_memory.py`: 6/6 ✓ (qo'shish/olish, sliding window, clear, alohida chat, role validatsiya, persistence)

## 📞 O'z ma'lumotlaringizni qo'shish

### Variant 1: CSV fayl orqali (tavsiya)

`smartphones.csv` faylini tahrirlang yoki o'zingiznikini qo'ying:

```bash
python -m scripts.convert_csv   # CSV → JSON (INR → USD, tavsif yaratish)
python -m scripts.ingest        # JSON → ChromaDB
```

`convert_csv.py` quyidagilarni qiladi:
- ✅ UTF-8 BOM belgisini tozalaydi
- ✅ Stunlarni moslashtiradi (`brand_name` → `brand`, `internal_memory` → `storage_gb`, ...)
- ✅ Narxni INR dan USD ga o'tkazadi (kurs: 1 USD ≈ 83 INR)
- ✅ Har bir telefon uchun avtomatik tavsif yaratadi
- ✅ Brand/model dublikatlarini tozalaydi
- ✅ Dublikat ID larni raqam bilan farqlaydi

### Variant 2: JSON faylni qo'lda tahrirlash

`data/phones.json` faylini tahrirlang:

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

Keyin:
```bash
python -m scripts.ingest
```

## 🛠 Texnologiyalar

- **Python 3.10+** — asosiy til
- **python-telegram-bot 21+** — Telegram Bot API
- **OpenAI SDK 2.x** — OpenRouter bilan ishlash uchun (OpenAI-mos API)
- **ChromaDB** — vektor ombor (lokal, persistent)
- **SQLite** — conversation memory
- **python-dotenv** — konfiguratsiya

## 🔒 Xavfsizlik

- `.env` fayli git'ga **kirmaydi** (`.gitignore` orqali)
- API kalitlar va token hech qachon commit qilinmaydi
- Suhbat tarixi lokal DB'da saqlanadi, serverga yuborilmaydi

## 📄 Litsenziya

MIT

## 🤝 Hissa qo'shish

Pull request'lar xush kelibsiz! Katta o'zgarishlar uchun avval issue oching.

## 📞 Aloqa

- **GitHub**: [SamijonovSardor](https://github.com/SamijonovSardor)
- **Repo**: [PhoneShop](https://github.com/SamijonovSardor/PhoneShop)
