"""ChromaDB vektor ombori - telefon ma'lumotlarini saqlash va qidirish."""
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from .config import settings, PROJECT_ROOT
from .embeddings import embeddings_client


class PhoneVectorStore:
    """Telefon katalogi uchun ChromaDB wrapper."""

    def __init__(self, persist_dir: Optional[str] = None, collection_name: Optional[str] = None) -> None:
        self.persist_dir = Path(persist_dir or settings.CHROMA_PERSIST_DIR)
        if not self.persist_dir.is_absolute():
            self.persist_dir = PROJECT_ROOT / self.persist_dir
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self.collection_name = collection_name or settings.CHROMA_COLLECTION_NAME

        self._client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True),
        )
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Telefon katalogi - RAG uchun"},
        )

    @property
    def count(self) -> int:
        return self._collection.count()

    def reset(self) -> None:
        """Kolleksiyani to'liq tozalash (qayta yuklash uchun)."""
        self._client.delete_collection(self.collection_name)
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Telefon katalogi - RAG uchun"},
        )

    def add_phones(self, phones: List[Dict[str, Any]]) -> int:
        """Telefonlarni vektor omboriga qo'shish.

        Har bir telefon uchun:
          - document: tabiiy tildagi tavsif (qidiruv uchun)
          - metadata: tarkibiy ma'lumotlar (narx, brand, ram va h.k.)
        """
        if not phones:
            return 0

        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []
        ids: List[str] = []

        for phone in phones:
            phone_id = str(phone.get("id") or phone.get("model", "")).strip().lower().replace(" ", "-")
            if not phone_id:
                continue

            documents.append(self._build_document(phone))
            metadatas.append(self._build_metadata(phone))
            ids.append(phone_id)

        existing = set(self._collection.get(ids=ids)["ids"]) if ids else set()
        new_ids = [i for i in ids if i not in existing]
        new_docs = [d for i, d in zip(ids, documents) if i in new_ids]
        new_metas = [m for i, m in zip(ids, metadatas) if i in new_ids]

        if not new_ids:
            return 0

        embeddings = embeddings_client.embed_documents(new_docs)
        self._collection.add(
            ids=new_ids,
            documents=new_docs,
            metadatas=new_metas,
            embeddings=embeddings,
        )
        return len(new_ids)

    @staticmethod
    def _build_document(phone: Dict[str, Any]) -> str:
        brand = phone.get("brand", "")
        model = phone.get("model", "")
        price = phone.get("price_usd", "?")
        currency = phone.get("currency", "USD")
        ram = phone.get("ram_gb", "?")
        storage = phone.get("storage_gb", "?")
        screen = phone.get("screen_size", "?")
        battery = phone.get("battery_mah", "?")
        camera = phone.get("camera_mp", "?")
        os_ = phone.get("os", "?")
        proc = phone.get("processor", "?")
        desc = phone.get("description", "")
        features = ", ".join(phone.get("features", []) or [])

        return (
            f"Telefon: {brand} {model}. "
            f"Narxi: {price} {currency}. "
            f"Xususiyatlari: RAM {ram} GB, xotira {storage} GB, "
            f"ekran {screen} dyuym, batareya {battery} mAh, "
            f"kamera {camera} MP, OS: {os_}, protsessor: {proc}. "
            f"Qo'shimcha: {features}. "
            f"Tavsif: {desc}"
        )

    @staticmethod
    def _build_metadata(phone: Dict[str, Any]) -> Dict[str, Any]:
        meta = {
            "brand": str(phone.get("brand", "")),
            "model": str(phone.get("model", "")),
            "price_usd": float(phone.get("price_usd", 0)),
            "ram_gb": int(phone.get("ram_gb", 0)),
            "storage_gb": int(phone.get("storage_gb", 0)),
        }
        for key in ("screen_size", "battery_mah", "camera_mp"):
            if phone.get(key) is not None:
                meta[key] = float(phone[key])
        return meta

    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """Foydalanuvchi savoli bo'yicha eng mos telefonlarni topish."""
        k = top_k or settings.TOP_K_RESULTS
        query_embedding = embeddings_client.embed_query(query)

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
        )

        hits: List[Dict[str, Any]] = []
        for i, doc_id in enumerate(results["ids"][0]):
            hits.append({
                "id": doc_id,
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if results.get("distances") else None,
            })
        return hits


vector_store = PhoneVectorStore()
