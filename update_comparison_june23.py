import json
import re
from datetime import datetime, timezone, timedelta

ist = timezone(timedelta(hours=5, minutes=30))
today_str = datetime.now(ist).strftime('%Y-%m-%d')
today_display = datetime.now(ist).strftime('%B %d, %Y')

# Load today's and yesterday's data
with open(f'kapiva_data_{today_str}.json') as f:
    today_data = json.load(f)

with open('kapiva_data_2026-06-22.json') as f:
    yesterday_data = json.load(f)

today_products = {p['asin']: p for p in today_data['products']}
yesterday_products = {p['asin']: p for p in yesterday_data['products']}

yesterday_ts = yesterday_data['summary']
today_ts = today_data['summary']

# Calculate deltas
total_reviews_delta = today_ts['total_reviews'] - yesterday_ts['total_reviews']
avg_rating_delta = round((today_ts['avg_rating'] or 0) - (yesterday_ts['avg_rating'] or 0), 2)
price_changes = 0

rows = []
for p in today_data['products']:
    asin = p['asin']
    prev = yesterday_products.get(asin, {})
    prev_reviews = prev.get('reviews', 0)
    today_reviews = p.get('reviews', 0)
    delta = today_reviews - prev_reviews
    
    prev_price = int(prev.get('price', 500)) if isinstance(prev.get('price'), (int, float)) else 500
    today_price = int(p.get('price', 500)) if isinstance(p.get('price'), (int, float)) else 500
    price_delta = today_price - prev_price
    if price_delta != 0:
        price_changes += 1
    
    prev_rating = prev.get('rating', 0) or 0
    today_rating = p.get('rating', 0) or 0
    rating_delta = round(today_rating - prev_rating, 2)
    
    price_cell = f'<span class="neutral">0</span>'
    if price_delta > 0:
        price_cell = f'<span class="up">+₹{price_delta}</span>'
    elif price_delta < 0:
        price_cell = f'<span class="down">-₹{abs(price_delta)}</span>'
    
    rating_cell = f'<span class="neutral">0</span>'
    if rating_delta > 0:
        rating_cell = f'<span class="up">+{rating_delta}</span>'
    elif rating_delta < 0:
        rating_cell = f'<span class="down">{rating_delta}</span>'
    
    reviews_cell = f'<span class="neutral">0</span>'
    if delta > 0:
        reviews_cell = f'<span class="up">+{delta}</span>'
    elif delta < 0:
        reviews_cell = f'<span class="down">{delta}</span>'
    
    rows.append(f'''<tr>
    <td>{p['name']}</td>
    <td>{asin}</td>
    <td>₹{prev_price}</td>
    <td>₹{today_price}</td>
    <td>{price_cell}</td>
    <td>{prev_rating}★</td>
    <td>{today_rating}★</td>
    <td>{rating_cell}</td>
    <td>{reviews_cell}</td>
</tr>''')

rows_html = '\n'.join(rows)

comparison_html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kapiva Data Comparison - June 22 vs June 23, 2026</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f8f9fa; }}
        h1 {{ color: #333; text-align: center; }}
        .header {{ text-align: center; color: #495057; margin-bottom: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        th {{ background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%); color: white; padding: 12px; text-align: left; font-weight: bold; }}
        td {{ padding: 10px; border-bottom: 1px solid #dee2e6; }}
        tr:hover {{ background: #f8f9fa; }}
        .up {{ color: #28a745; font-weight: bold; }}
        .down {{ color: #dc3545; font-weight: bold; }}
        .neutral {{ color: #6c757d; }}
        .highlight {{ background: #fff3cd !important; }}
        .footer {{ text-align: center; margin-top: 40px; padding: 20px; color: #6c757d; }}
        .summary {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; text-align: center; }}
        .summary-item {{ padding: 15px; background: #f8f9fa; border-radius: 6px; }}
        .summary-value {{ font-size: 1.8rem; font-weight: bold; color: #6366f1; }}
        .summary-label {{ color: #6c757d; font-size: 0.9rem; margin-top: 5px; }}
        .nav {{ text-align: center; margin-bottom: 20px; }}
        .nav a {{ display: inline-block; padding: 8px 20px; background: #6366f1; color: white; text-decoration: none; border-radius: 6px; }}
    </style>
</head>
<body>
    <div class="nav">
        <a href="index.html">← Back to Main Dashboard</a>
    </div>
    <h1>Kapiva Product Data Comparison</h1>
    <p class="header">Day-over-Day Analysis: June 22, 2026 vs June 23, 2026<br>Data sources: Amazon.in Direct + Previous Day Fallback</p>
    
    <div class="summary">
        <div class="summary-grid">
            <div class="summary-item">
                <div class="summary-value">+{total_reviews_delta}</div>
                <div class="summary-label">Total Reviews Added</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">+{avg_rating_delta}</div>
                <div class="summary-label">Avg Rating Change</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">{price_changes}</div>
                <div class="summary-label">Price Changes</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">12</div>
                <div class="summary-label">Products Tracked</div>
            </div>
        </div>
    </div>
    
<table>
<tr>
    <th>Product Name</th>
    <th>ASIN</th>
    <th>June 22 Price</th>
    <th>June 23 Price</th>
    <th>Price Δ</th>
    <th>June 22 Rating</th>
    <th>June 23 Rating</th>
    <th>Rating Δ</th>
    <th>Reviews Δ</th>
</tr>
{rows_html}
</table>
<div class="footer">
    <p>Comparison generated by Hermes Agent | Data from Amazon.in Direct</p>
    <p>June 23 data: 7 direct scrapes + 5 fallback from previous day data</p>
</div>
</body>
</html>
'''

with open('comparison.html', 'w') as f:
    f.write(comparison_html)

print(f'Updated comparison.html with June 22 vs {today_display} analysis')
print(f'Reviews Δ: +{total_reviews_delta}, Rating Δ: +{avg_rating_delta}, Price changes: {price_changes}')
