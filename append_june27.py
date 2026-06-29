#!/usr/bin/env python3
import json, re

with open('kapiva_data_2026-06-27.json', 'r') as f:
    data = json.load(f)
with open('kapiva_data_2026-06-26.json', 'r') as f:
    prev = json.load(f)

products = data['products']
prev_map = {p['asin']: p for p in prev['products']}

prices = [p['price'] for p in products]
avg_price = round(sum(prices) / len(prices)) if prices else 0
avg_rating = round(sum(p['rating'] for p in products) / len(products), 2)
total_reviews = sum(p['reviews'] for p in products)

def fmt_reviews(n):
    return f"{n / 1000:.1f}K" if n >= 1000 else str(n)

price_changes = []
for p in products:
    pr = prev_map.get(p['asin'])
    if pr:
        old = pr['price']
        new = p['price']
        change = new - old
        pct = round((change / old) * 100, 1) if old else 0
        color = 'red' if change > 0 else ('green' if change < 0 else 'gray')
        price_changes.append({'name': p['name'], 'old': old, 'new': new, 'change': change, 'pct': pct, 'color': color})

increases = [c for c in price_changes if c['change'] > 0]
decreases = [c for c in price_changes if c['change'] < 0]
no_change = [c for c in price_changes if c['change'] == 0]

rows_html = ''
for i, p in enumerate(products, 1):
    badge = 'badge-success' if 'In Stock' in p['availability'] else ('badge-error' if 'Out' in p['availability'] else 'badge-warning')
    reviews_str = fmt_reviews(p['reviews'])
    rows_html += f'''
                            <tr>
                                <td>{i}</td>
                                <td><strong>{p['name']}</strong></td>
                                <td>{p['category']}</td>
                                <td><code style="font-size:0.75rem;">{p['asin']}</code></td>
                                <td class="price">₹{p['price']}</td>
                                <td class="rating">{p['rating']}★</td>
                                <td>{reviews_str}</td>
                                <td><span class="badge {badge}">{p['availability']}</span></td>
                                <td><a href="https://www.amazon.in/dp/{p['asin']}" target="_blank" class="text-blue-600">View</a></td>
                            </tr>'''

comparison_row = f'''<tr style="background: #fce7f3;">
                            <td><strong>June 27, 2026</strong><br/><span style="font-size:0.75rem;color:#999;">Latest</span></td>
                            <td>{len(products)}</td>
                            <td class="price">₹{avg_price}</td>
                            <td class="rating">{avg_rating}★</td>
                            <td>{fmt_reviews(total_reviews)}</td>
                            <td>Apify Amazon Scraper</td>
                            <td><a class="text-purple-600" download="" href="kapiva_data_2026-06-27.json">JSON</a> | <a class="text-blue-600" download="" href="kapiva_data_2026-06-27.csv">CSV</a> | <a class="text-green-600" download="" href="kapiva_data_2026-06-27.xlsx">Excel</a></td>
                        </tr>'''

changes_html = ''
if price_changes:
    changes_html = '''
                    <div style="margin-top:20px; padding:15px; background:#f8fafc; border-radius:8px; border:1px solid #e2e8f0;">
                        <h4 style="margin:0 0 10px 0; color:#334155;">📊 Day-over-Day Price Changes (June 27 vs June 26)</h4>
                        <table class="detail-table" style="font-size:0.9rem;">
                            <thead>
                                <tr><th>Product</th><th>June 26 Price</th><th>June 27 Price</th><th>Change</th><th>% Change</th><th>Trend</th></tr>
                            </thead>
                            <tbody>'''
    for ch in price_changes:
        color_map = {'red': '#dc2626', 'green': '#16a34a', 'gray': '#6b7280'}
        bg_map = {'red': '#fef2f2', 'green': '#f0fdf4', 'gray': '#f9fafb'}
        icon = '📈' if ch['color'] == 'red' else ('📉' if ch['color'] == 'green' else '➡️')
        sign = '+' if ch['change'] > 0 else ''
        psign = '+' if ch['pct'] > 0 else ''
        changes_html += f'''
                                <tr style="background:{bg_map[ch['color']]};">
                                    <td><strong>{ch['name']}</strong></td>
                                    <td>₹{ch['old']}</td>
                                    <td>₹{ch['new']}</td>
                                    <td style="color:{color_map[ch['color']]}; font-weight:600;">{sign}₹{ch['change']}</td>
                                    <td style="color:{color_map[ch['color']]}; font-weight:600;">{psign}{ch['pct']}%</td>
                                    <td>{icon}</td>
                                </tr>'''
    changes_html += f'''
                                <tr style="background:#f1f5f9; font-weight:600;">
                                    <td colspan="6">Summary: {len(increases)} price increase(s), {len(decreases)} decrease(s), {len(no_change)} no change</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
'''

card = f'''<!-- Day: June 27, 2026 (Latest) -->
        <div class="day-card">
            <div class="day-header day-jun27">
                <span><i class="fas fa-star mr-2"></i>June 27, 2026 - Morning Scrape</span>
                <span class="badge bg-white/20">{len(products)} Products</span>
            </div>
            <div class="day-body">
                <div class="stats-grid">
                    <div class="stat-box"><div class="stat-value">₹{avg_price}</div><div class="stat-label">Avg Price</div></div>
                    <div class="stat-box"><div class="stat-value">{avg_rating}★</div><div class="stat-label">Avg Rating</div></div>
                    <div class="stat-box"><div class="stat-value">{fmt_reviews(total_reviews)}</div><div class="stat-label">Total Reviews</div></div>
                    <div class="stat-box"><div class="stat-value">Apify Amazon Scraper</div><div class="stat-label">Source</div></div>
                </div>
                <div class="download-grid">
                    <a href="kapiva_data_2026-06-27.json" download class="download-btn btn-json"><i class="fas fa-download mr-1"></i> JSON</a>
                    <a href="kapiva_data_2026-06-27.csv" download class="download-btn btn-csv"><i class="fas fa-download mr-1"></i> CSV</a>
                    <a href="kapiva_data_2026-06-27.xlsx" download class="download-btn btn-excel"><i class="fas fa-download mr-1"></i> Excel</a>
                </div>
                <div class="product-details">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                        <h3>All Products Details (June 27, 2026)</h3>
                        <span class="badge badge-success">{len(products)} Active Products</span>
                    </div>
                    <table class="detail-table">
                        <thead>
                            <tr><th>#</th><th>Product Name</th><th>Category</th><th>ASIN</th><th>Price</th><th>Rating</th><th>Reviews</th><th>Status</th><th>Amazon Link</th></tr>
                        </thead>
                        <tbody>{rows_html}
                            <tr style="background:#f1f5f9; font-weight:600;">
                                <td>—</td>
                                <td><strong>Summary</strong></td>
                                <td>{len(products)} Products</td>
                                <td>—</td>
                                <td class="price">₹{avg_price} avg</td>
                                <td class="rating">{avg_rating}★ avg</td>
                                <td>{fmt_reviews(total_reviews)} total</td>
                                <td><span class="badge badge-success">{len(products)} In Stock</span></td>
                                <td><span class="badge badge-warning">0 Unknown</span> <span class="badge badge-error">0 Out</span></td>
                            </tr>
                        </tbody>
                    </table>{changes_html}
                </div>
            </div>
        </div>'''

with open('index.html', 'r') as f:
    html = f.read()

css_addition = '        .day-jun27 { background: linear-gradient(135deg, #0f172a 0%, #334155 100%); }\n'
if '.day-jun27' not in html:
    html = html.replace('.day-jun4 {', css_addition + '        .day-jun4 {')

if '<!-- Day: June 27, 2026 (Latest) -->' not in html:
    html = html.replace('<!-- Comparison Table -->', '<!-- Day: June 27, 2026 (Latest) -->\n<!-- Comparison Table -->', 1)

# 1) Remove the pink "Latest" highlight from whatever row currently has it
html = html.replace('<tr style="background: #fce7f3;">', '<tr>', 1)

# 2) Insert June 27 as the first data row in the comparison table
if 'June 27, 2026' not in html:
    html = html.replace(
        '</tbody>\n<tr style="background:#f1f5f9; font-weight:600;">\n<td colspan="7"><strong>Historical Summary',
        '</tbody>\n' + comparison_row + '\n<tr style="background:#f1f5f9; font-weight:600;">\n<td colspan="7"><strong>Historical Summary',
        1
    )

# 4) Insert full day card right before the June 24 day-card
if html.count('day-jun27') < 2:
    html = html.replace(
        '<!-- Day: June 24, 2026 (Morning) -->',
        '<!-- Day: June 27, 2026 (Latest) -->' + '\n' + card + '\n' + '<!-- Day: June 24, 2026 (Morning) -->',
        1
    )

# 5) Update footer date to June 27
html = re.sub(
    r'<p>Kapiva Dashboard \| Data Source: Amazon\.in \| Updated: June \d{1,2}, 2026</p>',
    '<p>Kapiva Dashboard | Data Source: Amazon.in | Updated: June 27, 2026</p>',
    html
)

with open('index.html', 'w') as f:
    f.write(html)

print(f'index.html updated: avg ₹{avg_price}, rating {avg_rating}★, {fmt_reviews(total_reviews)} reviews, {len(products)} products')
print(f'Price changes: {len(increases)} up, {len(decreases)} down, {len(no_change)} same')
for ch in price_changes:
    sign = '+' if ch['change'] > 0 else ''
    print(f"  {ch['name']}: ₹{ch['old']} -> ₹{ch['new']} ({sign}₹{ch['change']}, {sign}{ch['pct']}%)")