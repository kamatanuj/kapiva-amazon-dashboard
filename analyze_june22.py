import json
from datetime import datetime, timezone, timedelta

ist = timezone(timedelta(hours=5, minutes=30))
today_str = datetime.now(ist).strftime('%Y-%m-%d')
today_display = datetime.now(ist).strftime('%B %d, %Y')

with open(f'kapiva_data_{today_str}.json') as f:
    today_data = json.load(f)

with open('kapiva_data_2026-06-21.json') as f:
    prev_data = json.load(f)

prev_map = {p['asin']: p for p in prev_data['products']}

total_reviews_added = 0
price_changes = 0
product_lines = []

for p in today_data['products']:
    prev = prev_map.get(p['asin'], {})
    review_delta = p['reviews'] - prev.get('reviews', p['reviews'])
    price_delta = ''
    if prev.get('price') and p['price'] != prev.get('price'):
        price_changes += 1
        price_delta = f"price {prev['price']} -> {p['price']}"
    total_reviews_added += review_delta
    line = f"- {p['name']}: reviews +{review_delta}, rating {p['rating']}* -> {p['rating']}*"
    if price_delta:
        line += f", {price_delta}"
    product_lines.append(line)

avg_rating_today = today_data['summary']['avg_rating']
avg_rating_prev = prev_data['summary']['avg_rating']
rating_change = round(avg_rating_today - avg_rating_prev, 2) if avg_rating_prev else 0

report = f"""Kapiva Daily Analysis - {today_display} vs June 21, 2026
Total Reviews Added: +{total_reviews_added}
Avg Rating Change: {rating_change:+.2f}
Price Changes: {price_changes}
Products Tracked: {today_data['summary']['total_products']}

Per-product review deltas:
""" + '\n'.join(product_lines) + '\n'

filename = f"analysis_report_{today_str}.txt"
with open(filename, 'w') as f:
    f.write(report)

print(report)
print(f"Saved {filename}")
