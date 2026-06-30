"""OpenRouter mavjud embedding modellarni to'liq qidirish."""
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import httpx
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(r"C:\Users\Win10\Desktop\phone-rag-bot\.env"))
api_key = os.getenv("OPENROUTER_API_KEY")

response = httpx.get(
    "https://openrouter.ai/api/v1/models",
    headers={"Authorization": f"Bearer {api_key}"},
    timeout=30.0,
)
data = response.json()
models = data.get("data", [])

print(f"Jami modellar: {len(models)}\n")

keywords = ["embed", "vector", "ada", "text-embed", "gemini", "cohere"]
seen = set()
for m in models:
    mid = m["id"].lower()
    for kw in keywords:
        if kw in mid:
            if mid not in seen:
                print(f"  {m['id']}")
                seen.add(mid)
            break

print()
print("=== Birinchi 30 ta model (barchasi) ===")
for m in models[:30]:
    print(f"  {m['id']}")
