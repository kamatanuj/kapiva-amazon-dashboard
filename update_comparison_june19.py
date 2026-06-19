#!/usr/bin/env python3
"""
Update comparison.html for June 16 vs June 19, 2026 day-over-day analysis.
"""
import json
import re

def load_data(filename):
    with open(filename, 'r') as f:
        return json.load(f)['products']

prev_data = load_data('kapiva_data_2026-06-16.json')
curr_data = load_data('kapiva_data_2026-06-19.json')

prev_map = {p['asin']: p for p in prev_data}
curr_map = {p['asin']: p for p in curr_data}

# Compute deltas
total_reviews_added = 0
total_rating_change = 0.0
price_changes = 0
rows = []

for asin in curr_map:
    c = curr_map[asin]
    p = prev_map.get(asin, {})
    price_p = int(p.get('price', '500')) if p else 500
    price_c = int(c.get('price', '500'))
    rating_p = p.get('rating') if p else None
    rating_c = c.get('rating')
    reviews_p = p.get('reviews', 0) if p else 0
    reviews_c = c.get('reviews', 0)

    price_delta = price_c - price_p
    rating_delta = round((rating_c - rating_p), 2) if rating_c is not None and rating_p is not None else 0
    reviews_delta = reviews_c - reviews_p

    total_reviews_added += reviews_delta
    total_rating_change += rating_delta if rating_delta else 0
    if price_delta != 0:
        price_changes += 1

    def fmt_delta(delta, is_rating=False):
        if is_rating:
            if delta > 0:
                return f'<span class="up">+{delta:.2f}</span>'
            elif delta < 0:
                return f'<span class="down">{delta:.2f}</span>'
            else:
                return '<span class="neutral">0</span>'
        else:
            if delta > 0:
                return f'<span class="up">+{delta}</span>'
            elif delta < 0:
                return f'<span class="down">{delta}</span>'
            else:
                return '<span class="neutral">0</span>'

    rows.append({
        'name': c['name'],
        'asin': asin,
        'price_p': price_p,
        'price_c': price_c,
        'price_delta': fmt_delta(price_delta),
        'rating_p': rating_p,
        'rating_c': rating_c,
        'rating_delta': fmt_delta(rating_delta, is_rating=True),
        'reviews_delta': fmt_delta(reviews_delta)
    })

avg_rating_change = round(total_rating_change / len(rows), 2) if rows else 0

# Generate HTML
html = f'''\u003c!DOCTYPE html>
\u003chtml>
\u003chead>
    \u003cmeta charset="UTF-8">
    \u003cmeta name="viewport" content="width=device-width, initial-scale=1.0">
    \u003ctitle>Kapiva Data Comparison - June 16 vs June 19, 2026\u003c/title>
    \u003cstyle>
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
    \u003c/style>
\u003c/head>
\u003cbody>
    \u003ch1>Kapiva Product Data Comparison\u003c/h1>
    \u003cp class="header">Day-over-Day Analysis: June 16, 2026 vs June 19, 2026\u003cbr>Data sources: Scrape.do + Amazon.in + Previous Day Fallback\u003c/p>
    
    \u003cdiv class="summary">
        \u003cdiv class="summary-grid">
            \u003cdiv class="summary-item">
                \u003cdiv class="summary-value">{total_reviews_added:+d}\u003c/div>
                \u003cdiv class="summary-label">Total Reviews Added\u003c/div>
            \u003c/div>
            \u003cdiv class="summary-item">
                \u003cdiv class="summary-value">{avg_rating_change:+.2f}\u003c/div>
                \u003cdiv class="summary-label">Avg Rating Change\u003c/div>
            \u003c/div>
            \u003cdiv class="summary-item">
                \u003cdiv class="summary-value">{price_changes}\u003c/div>
                \u003cdiv class="summary-label">Price Changes\u003c/div>
            \u003c/div>
            \u003cdiv class="summary-item">
                \u003cdiv class="summary-value">{len(rows)}\u003c/div>
                \u003cdiv class="summary-label">Products Tracked\u003c/div>
            \u003c/div>
        \u003c/div>
    \u003c/div>
    
\u003ctable>
\u003ctr>
    \u003cth>Product Name\u003c/th>
    \u003cth>ASIN\u003c/th>
    \u003cth>June 16 Price\u003c/th>
    \u003cth>June 19 Price\u003c/th>
    \u003cth>Price Δ\u003c/th>
    \u003cth>June 16 Rating\u003c/th>
    \u003cth>June 19 Rating\u003c/th>
    \u003cth>Rating Δ\u003c/th>
    \u003cth>Reviews Δ\u003c/th>
\u003c/tr>
'''

for r in rows:
    rp = f"{r['rating_p']:.1f}★" if r['rating_p'] else "-"
    rc = f"{r['rating_c']:.1f}★" if r['rating_c'] else "-"
    html += f'''\u003ctr>
    \u003ctd>{r['name']}\u003c/td>
    \u003ctd>{r['asin']}\u003c/td>
    \u003ctd>₹{r['price_p']}\u003c/td>
    \u003ctd>₹{r['price_c']}\u003c/td>
    \u003ctd>{r['price_delta']}\u003c/td>
    \u003ctd>{rp}\u003c/td>
    \u003ctd>{rc}\u003c/td>
    \u003ctd>{r['rating_delta']}\u003c/td>
    \u003ctd>{r['reviews_delta']}\u003c/td>
\u003c/tr>
'''

html += f'''\u003c/table\u003e
\u003cdiv class="footer">
    \u003cp>Comparison generated by Hermes Agent | Data from Scrape.do + Amazon.in\u003c/p>
    \u003cp>June 19 data merged live direct scrape with previous-day fallback where live scrape returned empty values\u003c/p>
\u003c/div>
\u003c/body>
\u003c/html>
'''

with open('comparison.html', 'w') as f:
    f.write(html)

print("Updated comparison.html: June 16 vs June 19, 2026")
print(f"Summary: reviews added={total_reviews_added:+d}, rating change={avg_rating_change:+.2f}, price changes={price_changes}, products={len(rows)}")

# Save analysis summary text
with open('analysis_report_2026-06-19.txt', 'w') as f:
    f.write(f"Kapiva Daily Analysis - June 19, 2026 vs June 16, 2026\n")
    f.write(f"Total Reviews Added: {total_reviews_added:+d}\n")
    f.write(f"Avg Rating Change: {avg_rating_change:+.2f}\n")
    f.write(f"Price Changes: {price_changes}\n")
    f.write(f"Products Tracked: {len(rows)}\n")
    f.write("\nPer-product review deltas:\n")
    for r in rows:
        rp = f"{r['rating_p']:.1f}★" if r['rating_p'] else "-"
        rc = f"{r['rating_c']:.1f}★" if r['rating_c'] else "-"
        # strip HTML for text report
        rd = re.sub(r'<[^\u003e]+>', '', r['reviews_delta'])
        f.write(f"- {r['name']}: reviews {rd}, rating {rp} -> {rc}\n")

print("Saved analysis_report_2026-06-19.txt")
