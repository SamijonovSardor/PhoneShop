"""RAG pipeline uchun lokal test (API chaqiruvsiz).

Faqat vektor omborining qidiruv mantig'ini tekshiradi.
To'liq RAG testi uchun OPENROUTER_API_KEY kerak va scripts/ingest.py
orqali avval ma'lumotlarni yuklash kerak.
"""
import json
import shutil
import sys
import io
import tempfile
import gc
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.vector_store import vector_store
from src.vector_store import PhoneVectorStore


def test_document_formatting() -> None:
    """Telefon hujjati to'g'ri formatlanayotganini tekshirish."""
    sample = {
        "brand": "TestBrand", "model": "TestModel", "price_usd": 299,
        "ram_gb": 8, "storage_gb": 128, "screen_size": 6.5,
        "battery_mah": 5000, "camera_mp": 50,
        "os": "Android 14", "processor": "Test CPU",
        "features": ["5G", "NFC"],
        "description": "Test telefon tavsifi",
    }
    doc = vector_store._build_document(sample)
    meta = vector_store._build_metadata(sample)
    assert "TestBrand TestModel" in doc, "Brand va model hujjatda bo'lishi kerak"
    assert "299 USD" in doc, "Narx hujjatda bo'lishi kerak"
    assert meta["price_usd"] == 299.0
    assert meta["ram_gb"] == 8
    print("[OK] Document formatting test o'tdi")


def test_search_with_mock_embeddings() -> None:
    """Mock embedding bilan qidiruv mantig'ini test qilish.

    Bu test ALOHIDA test collection ishlatadi, asosiy ma'lumotlarga tegmaydi.
    Haqiqiy embedding sifatini test qilmaydi.
    """
    from src import embeddings as emb_module

    original_embed_docs = emb_module.embeddings_client.embed_documents
    original_embed_query = emb_module.embeddings_client.embed_query

    sample = emb_module.embeddings_client.embed_query("test")
    fake_dim = len(sample)

    emb_module.embeddings_client.embed_documents = lambda texts: [
        [0.1] * fake_dim for _ in texts
    ]
    emb_module.embeddings_client.embed_query = lambda text: [0.1] * fake_dim

    test_phones = [
        {
            "id": "test-phone-1", "brand": "TestBrand", "model": "Budget A",
            "price_usd": 200, "ram_gb": 4, "storage_gb": 64,
        },
        {
            "id": "test-phone-2", "brand": "TestBrand", "model": "Flagship Z",
            "price_usd": 1000, "ram_gb": 12, "storage_gb": 256,
        },
    ]

    tmp_dir = Path(tempfile.mkdtemp(prefix="rag_test_"))
    try:
        test_store = PhoneVectorStore(
            persist_dir=tmp_dir,
            collection_name="test_phones",
        )
        added = test_store.add_phones(test_phones)
        assert added == 2, f"2 ta telefon qo'shish kerak edi, {added} qo'shildi"
        print(f"[OK] {added} ta test telefoni alohida collection ga qo'shildi")

        hits = test_store.search("arzon telefon", top_k=2)
        assert len(hits) == 2, f"2 ta natija topish kerak edi, {len(hits)} topildi"
        assert all("metadata" in h for h in hits)
        print(f"[OK] Search {len(hits)} ta natija qaytardi")
        print(f"[OK] Asosiy vektor ombori tegilmadi: {vector_store.count} ta hujjat")
        print("[OK] Search test muvaffaqiyatli (to'liq RAG uchun OPENROUTER_API_KEY kerak)")

        del test_store
        gc.collect()
    finally:
        emb_module.embeddings_client.embed_documents = original_embed_docs
        emb_module.embeddings_client.embed_query = original_embed_query
        try:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass
        print("[OK] Test ma'lumotlari tozalandi")


def test_json_structure() -> None:
    """phones.json fayl strukturasi to'g'riligini tekshirish."""
    data_path = PROJECT_ROOT / "data" / "phones.json"
    with data_path.open(encoding="utf-8") as f:
        data = json.load(f)
    phones = data["phones"] if isinstance(data, dict) else data
    required_fields = {"id", "brand", "model", "price_usd"}
    for phone in phones:
        missing = required_fields - set(phone.keys())
        assert not missing, f"Telefon {phone.get('id')} da maydonlar yo'q: {missing}"
    print(f"[OK] phones.json strukturasi to'g'ri ({len(phones)} ta telefon)")


if __name__ == "__main__":
    print("[TEST] Testlar boshlanmoqda...\n")
    test_json_structure()
    print()
    test_document_formatting()
    print()
    test_search_with_mock_embeddings()
    print("\n[SUCCESS] Barcha testlar muvaffaqiyatli o'tdi!")
