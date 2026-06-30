"""gemini-embedding-2 da batch input muammosini tekshirish."""
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

texts = ["Apple iPhone 13", "Samsung Galaxy S21", "Xiaomi Redmi Note 10"]

print("=== Single input ===")
r1 = client.embeddings.create(input="test", model="google/gemini-embedding-2", encoding_format="float")
print(f"  data type: {type(r1.data)}, len: {len(r1.data) if r1.data else 'None'}")

print("\n=== Batch input (list) ===")
try:
    r2 = client.embeddings.create(input=texts, model="google/gemini-embedding-2", encoding_format="float")
    print(f"  data type: {type(r2.data)}, len: {len(r2.data) if r2.data else 'None'}")
    if r2.data:
        print(f"  first dim: {len(r2.data[0].embedding) if r2.data[0].embedding else 'None'}")
except Exception as e:
    print(f"  ERROR: {e}")

print("\n=== openai/text-embedding-3-small batch ===")
try:
    r3 = client.embeddings.create(input=texts, model="openai/text-embedding-3-small", encoding_format="float")
    print(f"  data type: {type(r3.data)}, len: {len(r3.data) if r3.data else 'None'}")
    if r3.data:
        print(f"  first dim: {len(r3.data[0].embedding) if r3.data[0].embedding else 'None'}")
except Exception as e:
    print(f"  ERROR: {e}")
