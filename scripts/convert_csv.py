"""smartphones.csv ni phones.json ga o'tkazish (transformatsiya).

Ishlatish:
    python -m scripts.convert_csv

Qiladigan ishlari:
  - BOM belgisini tozalaydi (utf-8-sig)
  - Stunlarni bizning schemaga moslashtiradi
  - Narxni INR -> USD ga konvertatsiya qiladi
  - Bo'sh qiymatlarni "Noma'lum" qilib belgilaydi
  - Har bir telefon uchun tabiiy tildagi description yaratadi
  - Unikal id generatsiya qiladi
  - Brend nomini chiroyli formatda saqlaydi (Apple, Samsung, ...)
"""
import csv
import json
import re
import sys
import io
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import settings

INR_TO_USD_RATE = 83.0
INPUT_CSV = Path(r"C:\Users\Win10\Desktop\smartphones.csv")
OUTPUT_JSON = PROJECT_ROOT / "data" / "phones.json"


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\([^)]*\)", "", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def safe_int(value: str) -> int | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def safe_float(value: str) -> float | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def inr_to_usd(price_inr: int) -> float:
    return round(price_inr / INR_TO_USD_RATE, 2)


def build_features(row: dict) -> list[str]:
    features: list[str] = []
    if row.get("5G_or_not", "").strip() == "1":
        features.append("5G qo'llab-quvvatlash")

    fast_avail = row.get("fast_charging_available", "").strip()
    if fast_avail == "1":
        fc_watt = safe_int(row.get("fast_charging", ""))
        if fc_watt:
            features.append(f"Tezkor zaryadlash {fc_watt}W")
        else:
            features.append("Tezkor zaryadlash")

    if row.get("extended_memory_available", "").strip() == "1":
        features.append("MicroSD bilan kengaytiriladigan xotira")

    if row.get("refresh_rate", "").strip():
        rr = safe_int(row["refresh_rate"])
        if rr and rr >= 90:
            features.append(f"{rr}Hz yangilanish chastotasi")

    if row.get("num_rear_cameras", "").strip():
        n = safe_int(row["num_rear_cameras"])
        if n and n >= 3:
            features.append(f"{n} ta orqa kamera")

    return features


def build_description(phone: dict, row: dict) -> str:
    model = phone["model"]
    display_name = f"{phone['brand']} {model}"

    parts: list[str] = [f"{display_name} telefoni."]

    if phone.get("price_usd"):
        parts.append(f"Narxi: ${phone['price_usd']} (taxminan {int(phone['price_usd'] * INR_TO_USD_RATE):,} INR).")

    specs: list[str] = []
    if phone.get("processor"):
        specs.append(f"protsessor {phone['processor']}")
    if phone.get("ram_gb"):
        specs.append(f"RAM {phone['ram_gb']} GB")
    if phone.get("storage_gb"):
        specs.append(f"ichki xotira {phone['storage_gb']} GB")
    if phone.get("screen_size"):
        specs.append(f"ekran {phone['screen_size']} dyuym")
    if phone.get("battery_mah"):
        specs.append(f"batareya {phone['battery_mah']} mAh")
    if phone.get("camera_mp"):
        specs.append(f"asosiy kamera {phone['camera_mp']} MP")
    if phone.get("os"):
        specs.append(f"operatsion tizim {phone['os']}")
    if row.get("primary_camera_front", "").strip():
        front = safe_int(row["primary_camera_front"])
        if front:
            specs.append(f"old kamera {front} MP")
    if specs:
        parts.append("Xususiyatlari: " + ", ".join(specs) + ".")

    if phone["features"]:
        parts.append("Qo'shimcha: " + ", ".join(phone["features"]) + ".")

    if row.get("avg_rating", "").strip():
        try:
            rating = float(row["avg_rating"])
            parts.append(f"Foydalanuvchilar reytingi: {rating}/10.")
        except ValueError:
            pass

    resolution_h = safe_int(row.get("resolution_height", ""))
    resolution_w = safe_int(row.get("resolution_width", ""))
    if resolution_h and resolution_w:
        parts.append(f"Ekran piksellari: {resolution_w}x{resolution_h}.")

    return " ".join(parts)


def transform_row(row: dict) -> dict | None:
    brand_raw = (row.get("brand_name") or "").strip()
    model = (row.get("model") or "").strip()
    price_inr = safe_int(row.get("price", ""))

    if not brand_raw or not model or price_inr is None:
        return None

    brand = brand_raw.title()
    storage = safe_int(row.get("internal_memory", ""))
    storage_part = f"-{storage}gb" if storage else ""

    model_clean = model
    model_l = model.lower()
    brand_l = brand.lower()
    if model_l.startswith(brand_l + " "):
        model_clean = model[len(brand) + 1:].strip()
    elif model_l.startswith(brand_l):
        model_clean = model[len(brand):].strip()

    phone_id = f"{slugify(brand)}-{slugify(model_clean)}{storage_part}"
    phone_id = re.sub(r"-+", "-", phone_id).strip("-")
    model = model_clean

    features = build_features(row)

    proc_brand = (row.get("processor_brand") or "").strip().title()
    proc_cores = safe_int(row.get("num_cores", ""))
    proc_speed = safe_float(row.get("processor_speed", ""))
    processor = None
    if proc_brand:
        proc_parts = [proc_brand]
        if proc_cores:
            proc_parts.append(f"{proc_cores} yadro")
        if proc_speed:
            proc_parts.append(f"{proc_speed} GHz")
        processor = " ".join(proc_parts)

    os_raw = (row.get("os") or "").strip()
    os_label = None
    if os_raw:
        os_map = {"android": "Android", "ios": "iOS", "other": "Boshqa"}
        os_label = os_map.get(os_raw.lower(), os_raw.title())

    phone = {
        "id": phone_id,
        "brand": brand,
        "model": model,
        "price_usd": inr_to_usd(price_inr),
        "ram_gb": safe_int(row.get("ram_capacity", "")),
        "storage_gb": storage,
        "screen_size": safe_float(row.get("screen_size", "")),
        "battery_mah": safe_int(row.get("battery_capacity", "")),
        "camera_mp": safe_int(row.get("primary_camera_rear", "")),
        "os": os_label,
        "processor": processor,
        "features": features,
    }
    phone["description"] = build_description(phone, row)
    return phone


def main() -> None:
    if not INPUT_CSV.exists():
        print(f"[XATO] CSV fayl topilmadi: {INPUT_CSV}")
        return

    print(f"[O'QISH] {INPUT_CSV}")
    with INPUT_CSV.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    print(f"[OK] {len(rows)} ta qator o'qildi")

    phones: list[dict] = []
    skipped = 0
    seen_ids: set[str] = set()
    duplicates = 0
    for row in rows:
        phone = transform_row(row)
        if phone is None:
            skipped += 1
            continue
        original_id = phone["id"]
        suffix = 1
        while phone["id"] in seen_ids:
            suffix += 1
            phone["id"] = f"{original_id}-{suffix}"
        if suffix > 1:
            duplicates += 1
        seen_ids.add(phone["id"])
        phones.append(phone)

    print(f"[OK] {len(phones)} ta telefon transformatsiya qilindi")
    if skipped:
        print(f"[OGOHLANTIRISH] {skipped} ta qator o'tkazib yuborildi (brand/model/price yo'q)")
    if duplicates:
        print(f"[OGOHLANTIRISH] {duplicates} ta dublikat id raqam bilan farqlandi")

    prices = [p["price_usd"] for p in phones if p.get("price_usd")]
    if prices:
        print(f"[INFO] Narxlar (USD): min=${min(prices):.2f}, max=${max(prices):.2f}, o'rtacha=${sum(prices)/len(prices):.2f}")

    print(f"[YOZISH] {OUTPUT_JSON}")
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_JSON.open("w", encoding="utf-8") as f:
        json.dump({"phones": phones}, f, ensure_ascii=False, indent=2)

    print(f"[OK] {len(phones)} ta telefon saqlandi")
    print()
    print("=== Namuna (birinchi 3 ta telefon) ===")
    for p in phones[:3]:
        print(f"\n  ID: {p['id']}")
        print(f"  {p['brand']} {p['model']} - ${p['price_usd']}")
        print(f"  {p['description'][:200]}...")


if __name__ == "__main__":
    main()
