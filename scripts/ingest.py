"""Ma'lumotlarni bazaga yuklash (ingestion) skripti.

Ishlatish:
    python -m scripts.ingest

Bu skript data/phones.json fayldan telefonlarni o'qib,
embedding hosil qilib ChromaDB ga saqlaydi.
"""
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import settings, PROJECT_ROOT
from src.vector_store import vector_store


def load_phones(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Ma'lumotlar fayli topilmadi: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "phones" in data:
        return data["phones"]
    if isinstance(data, list):
        return data
    raise ValueError("JSON strukturasi noto'g'ri. 'phones' massivini kutmoqda.")


def main() -> None:
    data_path = Path(settings.PHONES_DATA_PATH)
    if not data_path.is_absolute():
        data_path = PROJECT_ROOT / data_path

    print(f"📂 Ma'lumotlar fayli: {data_path}")
    phones = load_phones(data_path)
    print(f"📱 Yuklangan telefonlar: {len(phones)}")

    print("♻️  Eski kolleksiya tozalanmoqda...")
    vector_store.reset()

    print("🔄 Embeddinglar hisoblanmoqda va bazaga qo'shilmoqda...")
    added = vector_store.add_phones(phones)
    print(f"✅ Bazaga qo'shildi: {added} ta telefon")
    print(f"📊 Jami hujjatlar: {vector_store.count}")


if __name__ == "__main__":
    main()
