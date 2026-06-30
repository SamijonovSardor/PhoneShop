"""ChromaDB holatini tekshirish."""
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from src.vector_store import vector_store
print(f"ChromaDB da hujjatlar soni: {vector_store.count}")
print(f"Saqlash papkasi: {vector_store.persist_dir}")

import json
with open(r"C:\Users\Win10\Desktop\phone-rag-bot\data\phones.json", encoding="utf-8") as f:
    phones = json.load(f)["phones"]
print(f"phones.json da telefonlar: {len(phones)}")
print(f"Embedding qilinmagan: {len(phones) - vector_store.count} ta")
