"""phones.json tekshirish skripti."""
import json
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

data = json.load(open(r'C:\Users\Win10\Desktop\phone-rag-bot\data\phones.json', encoding='utf-8'))
phones = data['phones']
print(f'Jami: {len(phones)} ta telefon')
print()
print('=== Apple iPhone 13 namunalari ===')
for p in phones:
    name = p['model'].lower()
    if 'iphone 13' in name and 'pro' not in name and 'mini' not in name and 'plus' not in name:
        print(f'  {p["id"]}: {p["model"]} - ${p["price_usd"]}')
print()
print('=== 300-400 USD oralig ida telefonlar ===')
in_range = [p for p in phones if 300 <= (p.get('price_usd') or 0) <= 400]
print(f'Soni: {len(in_range)} ta')
for p in in_range[:5]:
    print(f'  {p["brand"]} {p["model"]} - ${p["price_usd"]} ({p.get("ram_gb")}GB RAM)')
print()
print('=== To\'liq tavsif namunasi ===')
for p in phones:
    if 'iphone 13' in p['model'].lower() and 'pro max' in p['model'].lower():
        print(f'Model: {p["brand"]} {p["model"]}')
        print(f'Narxi: ${p["price_usd"]}')
        print(f'Tavsif: {p["description"]}')
        break
