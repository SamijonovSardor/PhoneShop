"""gemini-embedding-2 ni raw httpx bilan sinash."""
import sys
import io
import json

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import httpx
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(r"C:\Users\Win10\Desktop\phone-rag-bot\.env"))
api_key = os.getenv("OPENROUTER_API_KEY")

for model in ["google/gemini-embedding-2", "google/gemini-embedding-001"]:
    print(f"\n=== {model} ===")
    response = httpx.post(
        "https://openrouter.ai/api/v1/embeddings",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"input": "test", "model": model, "encoding_format": "float"},
        timeout=60.0,
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
