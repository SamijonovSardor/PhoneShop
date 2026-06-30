"""Dataset tahlil skripti."""
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import csv
from pathlib import Path

csv_path = Path(r'C:\Users\Win10\Desktop\smartphones.csv')
with csv_path.open(encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

print(f'Jami yozuvlar: {len(rows)}')
print(f'Stunlar soni: {len(rows[0])}')
print(f'Stunlar: {list(rows[0].keys())}')
print()

prices = []
for r in rows:
    try:
        prices.append(int(r['price']))
    except (ValueError, KeyError):
        pass
print(f'Narxlar (INR): min={min(prices):,}, max={max(prices):,}, ortacha={sum(prices)//len(prices):,}')
print(f'Narxlar (USD ~83 INR): min=${min(prices)/83:.2f}, max=${max(prices)/83:.2f}')
print()

print('=== Bosh qiymatlar (har bir ustun) ===')
for col in rows[0].keys():
    empty = sum(1 for r in rows if not r[col] or r[col].strip() == '')
    print(f'  {col:30s}: {empty:4d} ta bosh ({empty*100/len(rows):5.1f}%)')
print()

brands = sorted(set(r['brand_name'] for r in rows))
print(f'Brendlar soni: {len(brands)}')
print(f'Brendlar: {", ".join(brands)}')
print()

ratings = []
for r in rows:
    try:
        ratings.append(float(r['avg_rating']))
    except (ValueError, KeyError):
        pass
if ratings:
    print(f'Reyting: min={min(ratings)}, max={max(ratings)}, ortacha={sum(ratings)/len(ratings):.2f}')

oss = sorted(set(r['os'] for r in rows if r['os']))
print(f'OS turlari: {oss}')
