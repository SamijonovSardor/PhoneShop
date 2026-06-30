"""RAG tizimining test qidiruvi."""
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from src.vector_store import vector_store

queries = [
    "300-400 dollar yaxshi kamera va katta batareyali telefon",
    "Samsung 5G 500 dollar gacha",
    "Xiaomi 8GB RAM li arzon telefon",
    "iPhone eng arzoni",
    "O'yin uchun kuchli protsessorli telefon",
]

for q in queries:
    print(f"\n=== Qidiruv: '{q}' ===")
    hits = vector_store.search(q, top_k=3)
    for hit in hits:
        meta = hit["metadata"]
        price = meta.get("price_usd", "?")
        ram = meta.get("ram_gb", "?")
        battery = meta.get("battery_mah", "?")
        print(f"  - {meta.get('brand')} {meta.get('model')} - ${price} (RAM {ram}GB, batareya {battery}mAh)")
