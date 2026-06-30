"""Gemini embedding formatini tekshirish."""
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(r"C:\Users\Win10\Desktop\phone-rag-bot\.env"))

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

for model in ["google/gemini-embedding-2", "google/gemini-embedding-001", "openai/text-embedding-3-small"]:
    print(f"\n=== {model} ===")
    try:
        response = client.embeddings.create(
            input="Samsung telefon yaxshi",
            model=model,
        )
        print(f"Response type: {type(response)}")
        print(f"Response data type: {type(response.data)}")
        print(f"Response data length: {len(response.data) if response.data else 'None'}")
        if response.data and len(response.data) > 0:
            item = response.data[0]
            print(f"Item keys: {dir(item)}")
            print(f"Item.embedding type: {type(item.embedding)}")
            if item.embedding:
                print(f"Embedding dim: {len(item.embedding)}")
    except Exception as e:
        print(f"ERROR: {e}")
