#!/usr/bin/env python3
import json

# Load today's scraped data
with open('/root/kapiva/kapiva_data_2026-06-25.json', 'r') as f:
    data = json.load(f)

# Load June 24 data for comparison
with open('/root/kapiva/kapiva_data_2026-06-24.json', 'r') as f:
    prev_data = json.load(f)

# Calculate real avg price
prices = [p['price'] for p in data['products'] if p['price']]
avg_price = round(sum(prices) / len(prices)) if prices else 0
avg_rating = data['summary']['avg_rating']
total_reviews = data['summary']['total_reviews']

# Format total reviews for display
def format_reviews(n):
    if n >= 1000:
        return f"{n/1000:.1f}K"
    return str(n)

def format_reviews_short(n):
    if n >= 1000:
        return f"{round(n/1000, 1)}K"
    return str(n)

# Build day-over-day comparison
prev_products = {p['asin']: p for p in prev_data['products']}
price_changes = []
for p in data['products']:
    prev_p = prev_products.get(p['asin'])
    if prev_p:
        old_price = prev_p['price']
        new_price = p['price']
        if old_price and new_price:
            change = new_price - old_price
            pct = round((change / old_price) * 100, 1) if old_price else 0
            color = 'red' if change > 0 else ('green' if change < 0 else 'gray')
            price_changes.append({
                'name': p['name'],
                'old_price': old_price,
                'new_price': new_price,
                'change': change,
                'pct': pct,
                'color': color
            })

# Build the new day card HTML
products = data['products']
day_card = '''<!-- Day: June 25, 2026 (Morning) -->
        <div class="day-card">
            <div class="day-header day-jun25">
                <span><i class="fas fa-star mr-2"></i>June 25, 2026 - Morning Scrape</span>
                <span class="badge bg-white/20">12 Products</span>
            </div>
            <div class="day-body">
                <div class="stats-grid">
                    <div class="stat-box"><div class="stat-value">\u20b9''' + str(avg_price) + '''</div><div class="stat-label">Avg Price</div></div>
                    <div class="stat-box"><div class="stat-value">''' + str(avg_rating) + '''\u2605</div><div class="stat-label">Avg Rating</div></div>
                    <div class="stat-box"><div class="stat-value">''' + format_reviews(total_reviews) + '''</div><div class="stat-label">Total Reviews</div></div>
                    <div class="stat-box"><div class="stat-value">Apify Amazon Scraper</div><div class="stat-label">Source</div></div>
                </div>
                <div class="download-grid">
                    <a href="kapiva_data_2026-06-25.json" download class="download-btn btn-json"><i class="fas fa-download mr-1"></i> JSON</a>
                    <a href="kapiva_data_2026-06-25.csv" download class="download-btn btn-csv"><i class="fas fa-download mr-1"></i> CSV</a>
                    <a href="kapiva_data_2026-06-25.xlsx" download class="download-btn btn-excel"><i class="fas fa-download mr-1"></i> Excel</a>
                </div>
                <div class="product-details">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                        <h3>All Products Details (June 25, 2026)</h3>
                        <span class="badge badge-success">12 Active Products</span>
                    </div>
                    <table class="detail-table">
                        <thead>
                            <tr><th>#</th><th>Product Name</th><th>Category</th><th>ASIN</th><th>Price</th><th>Rating</th><th>Reviews</th><th>Status</th><th>Amazon Link</th></tr>
                        </thead>
                        <tbody>'''

for i, p in enumerate(products, 1):
    badge = 'badge-success' if 'In Stock' in p['availability'] else ('badge-error' if 'Out' in p['availability'] else 'badge-warning')
    reviews_str = format_reviews_short(p['reviews'])
    day_card += '''
                            <tr>
                                <td>''' + str(i) + '''</td>
                                <td><strong>''' + p['name'] + '''</strong></td>
                                <td>''' + p['category'] + '''</td>
                                <td><code style="font-size:0.75rem;">''' + p['asin'] + '''</code></td>
                                <td class="price">\u20b9''' + str(p['price']) + '''</td>
                                <td class="rating">''' + str(p['rating']) + '''\u2605</td>
                                <td>''' + reviews_str + '''</td>
                                <td><span class="badge ''' + badge + '''">''' + p['availability'] + '''</span></td>
                                <td><a href="https://www.amazon.in/dp/''' + p['asin'] + '''" target="_blank" class="text-blue-600">View</a></td>
                            </tr>'''

# Summary row
day_card += '''
                            <tr style="background:#f1f5f9; font-weight:600;">
                                <td>\u2014</td>
                                <td><strong>Summary</strong></td>
                                <td>12 Products</td>
                                <td>\u2014</td>
                                <td class="price">\u20b9''' + str(avg_price) + ''' avg</td>
                                <td class="rating">''' + str(avg_rating) + '''\u2605 avg</td>
                                <td>''' + format_reviews(total_reviews) + ''' total</td>
                                <td><span class="badge badge-success">12 In Stock</span></td>
                                <td><span class="badge badge-warning">0 Unknown</span> <span class="badge badge-error">0 Out</span></td>
                            </tr>
                        </tbody>
                    </table>'''

# Day-over-day comparison section
day_card += '''
                    <!-- Day-over-day comparison: June 25 vs June 24 -->
                    <div style="margin-top:20px; padding:15px; background:#f8fafc; border-radius:8px; border:1px solid #e2e8f0;">
                        <h4 style="margin:0 0 10px 0; color:#334155;">\U0001f4ca Day-over-Day Price Changes (June 25 vs June 24)</h4>
                        <table class="detail-table" style="font-size:0.9rem;">
                            <thead>
                                <tr><th>Product</th><th>June 24 Price</th><th>June 25 Price</th><th>Change</th><th>% Change</th><th>Trend</th></tr>
                            </thead>
                            <tbody>'''

for ch in price_changes:
    color_map = {'red': '#dc2626', 'green': '#16a34a', 'gray': '#6b7280'}
    bg_map = {'red': '#fef2f2', 'green': '#f0fdf4', 'gray': '#f9fafb'}
    trend_icon = '\U0001f4c8' if ch['color'] == 'red' else ('\U0001f4c9' if ch['color'] == 'green' else '\u27a1\ufe0f')
    change_sign = '+' if ch['change'] > 0 else ''
    pct_sign = '+' if ch['pct'] > 0 else ''
    day_card += '''
                                <tr style="background:''' + bg_map[ch['color']] + ''';">
                                    <td><strong>''' + ch['name'] + '''</strong></td>
                                    <td>\u20b9''' + str(ch['old_price']) + '''</td>
                                    <td>\u20b9''' + str(ch['new_price']) + '''</td>
                                    <td style="color:''' + color_map[ch['color']] + '''; font-weight:600;">''' + change_sign + '''\u20b9''' + str(ch['change']) + '''</td>
                                    <td style="color:''' + color_map[ch['color']] + '''; font-weight:600;">''' + pct_sign + str(ch['pct']) + '''%</td>
                                    <td>''' + trend_icon + '''</td>
                                </tr>'''

# Summary of changes
increases = [c for c in price_changes if c['change'] > 0]
decreases = [c for c in price_changes if c['change'] < 0]
no_change = [c for c in price_changes if c['change'] == 0]
day_card += '''
                                <tr style="background:#f1f5f9; font-weight:600;">
                                    <td colspan="6">
                                        Summary: ''' + str(len(increases)) + ''' price increase(s), ''' + str(len(decreases)) + ''' decrease(s), ''' + str(len(no_change)) + ''' no change
                                    </td>
                                </tr>
                        </tbody>
                    </table>
                    </div>
                </div>
            </div>
        </div>'''

print(f"Day card generated: {len(day_card)} chars")
print(f"Avg price: Rs {avg_price}")
print(f"Price changes: {len(increases)} up, {len(decreases)} down, {len(no_change)} same")
print(f"Total reviews: {total_reviews}")

# Save the day card for insertion
with open('/tmp/june25_card.html', 'w') as f:
    f.write(day_card)

# Also print the changes summary
print("\n--- Price Changes ---")
for ch in price_changes:
    change_sign = '+' if ch['change'] > 0 else ''
    pct_sign = '+' if ch['pct'] > 0 else ''
    print(f"  {ch['name']}: Rs {ch['old_price']} -> Rs {ch['new_price']} ({change_sign}Rs {ch['change']}, {pct_sign}{ch['pct']}%)")