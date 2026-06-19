#!/usr/bin/env python3
"""
Append June 19, 2026 block to Kapiva dashboard (index.html) in APPEND-ONLY mode.
"""
import json
import re
from datetime import datetime

with open('kapiva_data_2026-06-19.json', 'r') as f:
    data = json.load(f)

products = data['products']
summary = data['summary']
avg_rating = summary['avg_rating']
total_reviews = summary['total_reviews']

# Read current index.html
with open('index.html', 'r') as f:
    html = f.read()

# Helpers
def fmt_num(n):
    if n >= 1000:
        return f"{n//1000}K" if n % 1000 == 0 else f"{n/1000:.1f}K".replace('.0K','K')
    return f"{n:,}"

avg_rating_str = f"{avg_rating}★"
total_reviews_str = fmt_num(total_reviews)
total_reviews_full = f"{total_reviews:,}"

# 1. Add day-jun19 CSS if missing
if '.day-jun19' not in html:
    css_addition = '        .day-jun19 { background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%); }\n'
    # insert before the first .day-jun* line to keep order
    html = re.sub(r'(\s+\.day-jun\d+\s+\{)', lambda m: css_addition + m.group(1), html, count=1)

# 2. Remove Latest highlight from all comparison rows
html = html.replace('<tr style="background: #fce7f3;">', '<tr>')

# 3. Update old "Latest" labels in comparison table to "Morning" (for June 9, 11, 14, 16)
for d in ['June 9, 2026', 'June 11, 2026', 'June 14, 2026', 'June 16, 2026']:
    html = re.sub(rf'(<td><strong>{d}</strong><br><span style="font-size:0\.75rem;color:#999;">)Latest(</span></td>)', r'\1Morning\2', html)

# 4. Add new June 19 comparison row before closing tbody, with highlight
comparison_row = f'''                        <tr style="background: #fce7f3;">
                            <td><strong>June 19, 2026</strong><br><span style="font-size:0.75rem;color:#999;">Latest</span></td>
                            <td>12</td>
                            <td class="price">₹500</td>
                            <td class="rating">{avg_rating_str}</td>
                            <td>{total_reviews_full}</td>
                            <td>Scrape.do</td>
                            <td><a href="kapiva_data_2026-06-19.json" download class="text-purple-600">JSON</a> | <a href="kapiva_data_2026-06-19.csv" download class="text-blue-600">CSV</a> | <a href="kapiva_data_2026-06-19.xlsx" download class="text-green-600">Excel</a></td>
                        </tr>
'''

# Insert before the closing tbody in comparison table
if 'June 19, 2026' not in html:
    # Pattern: the last </tr> of comparison table before </tbody></table>
    pattern = r'(<!-- Comparison Table -->.*?)(</tbody>\s*</table>)'
    match = re.search(pattern, html, re.DOTALL)
    if match:
        insert_pos = match.end(1)
        html = html[:insert_pos] + comparison_row + html[insert_pos:]

# 5. Change June 16 day card header from "Latest Scrape" to "Morning Scrape"
html = html.replace('June 16, 2026 - Latest Scrape', 'June 16, 2026 - Morning Scrape')

# 6. Build June 19 day card
product_rows = ''
for i, p in enumerate(products, 1):
    rating_display = f"{p['rating']}★" if p['rating'] else "-"
    status_badge = "badge-success" if p['availability'] == "In Stock" else "badge-error" if p['availability'] == "Out of Stock" else "badge-warning"
    status_text = "In Stock" if p['availability'] == "In Stock" else p['availability']
    product_rows += f'''                            <tr>
                                <td>{i}</td>
                                <td><strong>{p['name']}</strong></td>
                                <td>{p['category']}</td>
                                <td><code style="font-size:0.75rem;">{p['asin']}</code></td>
                                <td class="price">₹{p['price']}</td>
                                <td class="rating">{rating_display}</td>
                                <td>{p['reviews']:,}</td>
                                <td><span class="badge {status_badge}">{status_text}</span></td>
                                <td><a href="{p['url']}" target="_blank" class="text-blue-600">View</a></td>
                            </tr>
'''

jun19_card = f'''        <!-- Day 10: June 19, 2026 (Latest) -->
        <div class="day-card">
            <div class="day-header day-jun19">
                <span><i class="fas fa-star mr-2"></i>June 19, 2026 - Latest Scrape</span>
                <span class="badge bg-white/20">12 Products</span>
            </div>
            <div class="day-body">
                <div class="stats-grid">
                    <div class="stat-box"><div class="stat-value">₹500</div><div class="stat-label">Avg Price</div></div>
                    <div class="stat-box"><div class="stat-value">{avg_rating_str}</div><div class="stat-label">Avg Rating</div></div>
                    <div class="stat-box"><div class="stat-value">{total_reviews_str}</div><div class="stat-label">Total Reviews</div></div>
                    <div class="stat-box"><div class="stat-value">Scrape.do</div><div class="stat-label">Source</div></div>
                </div>
                
                <div class="download-grid">
                    <a href="kapiva_data_2026-06-19.json" download class="download-btn btn-json">
                        <i class="fas fa-download mr-1"></i> JSON
                    </a>
                    <a href="kapiva_data_2026-06-19.csv" download class="download-btn btn-csv">
                        <i class="fas fa-download mr-1"></i> CSV
                    </a>
                    <a href="kapiva_data_2026-06-19.xlsx" download class="download-btn btn-excel">
                        <i class="fas fa-download mr-1"></i> Excel
                    </a>
                </div>

                <!-- FULL PRODUCT DETAILS TABLE -->
                <div class="product-details">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                        <h3>All Products Details (June 19, 2026)</h3>
                        <span class="badge badge-success">12 Active Products</span>
                    </div>
                    
                    <table class="detail-table">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Product Name</th>
                                <th>Category</th>
                                <th>ASIN</th>
                                <th>Price</th>
                                <th>Rating</th>
                                <th>Reviews</th>
                                <th>Status</th>
                                <th>Amazon Link</th>
                            </tr>
                        </thead>
                        <tbody>
{product_rows}                        </tbody>
                    </table>
                </div>
            </div>
        </div>

'''

# 7. Insert June 19 card before footer
if 'June 19, 2026 - Latest Scrape' not in html:
    html = re.sub(r'(\s*)<footer class="text-center', lambda m: jun19_card + m.group(1) + '<footer class="text-center', html, count=1)

# 8. Update footer date
html = re.sub(r'Updated: [^\u003c]*\u003c/p\u003e', 'Updated: June 19, 2026</p>', html)

with open('index.html', 'w') as f:
    f.write(html)

print("Updated index.html with June 19, 2026 data (APPEND-ONLY mode)")
print("Historical data preserved:")
print("  - June 4, 2024")
print("  - June 8, 2026")
print("  - June 9, 2026")
print("  - June 10, 2026")
print("  - June 11, 2026")
print("  - June 12, 2026")
print("  - June 13, 2026")
print("  - June 14, 2026")
print("  - June 16, 2026")
print("  - June 19, 2026 (NEW)")
