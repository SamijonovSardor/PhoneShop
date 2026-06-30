"""Embedding modellarni sinab ko'rish."""
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from openai import OpenAI
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(r"C:\Users\Win10\Desktop\phone-rag-bot\.env"))

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

candidates = [
    "openai/text-embedding-3-small",
    "openai/text-embedding-3-large",
    "openai/text-embedding-ada-002",
    "qwen/qwen3-embedding-0.6b",
    "qwen/qwen3-embedding-8b",
    "google/gemini-embedding-001",
    "google/gemini-embedding-2",
    "cohere/embed-english-v3.0",
    "cohere/embed-multilingual-v3.0",
]

for model in candidates:
    try:
        response = client.embeddings.create(
            input="test",
            model=model,
            encoding_format="float",
        )
        dim = len(response.data[0].embedding)
        print(f"  [OK]   {model:45s} -> dim={dim}")
    except Exception as e:
        err = str(e)[:80]
        print(f"  [FAIL] {model:45s} -> {err}")
