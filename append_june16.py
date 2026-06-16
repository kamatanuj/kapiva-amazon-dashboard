#!/usr/bin/env python3
import json
import re
from datetime import datetime, timezone, timedelta

ist = timezone(timedelta(hours=5, minutes=30))
today_str = '2026-06-16'
today_display = 'June 16, 2026'

def format_number(n):
    if n >= 1000:
        return f"{n//1000}K"
    return str(n)

# Load today's data
with open('kapiva_data_2026-06-16.json') as f:
    data = json.load(f)

products = data['products']
summary = data['summary']

# Stats
avg_price = summary['avg_price']
avg_rating = summary['avg_rating']
total_reviews = summary['total_reviews']

# Read current index.html
with open('index.html', 'r') as f:
    html = f.read()

# Add day-jun16 CSS if not present
if '.day-jun16' not in html:
    css_addition = '        .day-jun16 { background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%); }\n'
    html = html.replace('.day-jun4 {', css_addition + '        .day-jun4 {')

# Remove any previous "Latest" highlighting from comparison table
html = re.sub(r'<tr style="background: #fce7f3;">', '<tr>', html)

# Also update existing "Latest" labels to "Morning" in day headers
html = html.replace('June 14, 2026 - Latest Scrape', 'June 14, 2026 - Morning Scrape')

# Build new day card HTML
day_card = f'''
        <!-- Day 9: June 16, 2026 (Latest) -->
        <div class="day-card">
            <div class="day-header day-jun16">
                <span><i class="fas fa-star mr-2"></i>June 16, 2026 - Latest Scrape</span>
                <span class="badge bg-white/20">{len(products)} Products</span>
            </div>
            <div class="day-body">
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-value">₹{avg_price}</div>
                        <div class="stat-label">Avg Price</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{avg_rating}★</div>
                        <div class="stat-label">Avg Rating</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{format_number(total_reviews)}</div>
                        <div class="stat-label">Total Reviews</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">Scrape.do</div>
                        <div class="stat-label">Source</div>
                    </div>
                </div>
                
                <div class="download-grid">
                    <a href="kapiva_data_2026-06-16.json" download class="download-btn btn-json">
                        <i class="fas fa-download mr-1"></i> JSON
                    </a>
                    <a href="kapiva_data_2026-06-16.csv" download class="download-btn btn-csv">
                        <i class="fas fa-download mr-1"></i> CSV
                    </a>
                    <a href="kapiva_data_2026-06-16.xlsx" download class="download-btn btn-excel">
                        <i class="fas fa-download mr-1"></i> Excel
                    </a>
                </div>

                <!-- FULL PRODUCT DETAILS TABLE -->
                <div class="product-details">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                        <h3>All Products Details (June 16, 2026)</h3>
                        <span class="badge badge-success">{len(products)} Active Products</span>
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
'''

for i, p in enumerate(products, 1):
    rating_display = f"{p['rating']}★" if p.get('rating') else "-"
    status = p['availability']
    if status == 'In Stock':
        status_badge = 'badge-success'
    elif status == 'Out of Stock':
        status_badge = 'badge-error'
    else:
        status_badge = 'badge-warning'
    
    day_card += f'''                            <tr>
                                <td>{i}</td>
                                <td><strong>{p['name']}</strong></td>
                                <td>{p['category']}</td>
                                <td><code style="font-size:0.75rem;">{p['asin']}</code></td>
                                <td class="price">₹{p['price']}</td>
                                <td class="rating">{rating_display}</td>
                                <td>{p['reviews']:,}</td>
                                <td><span class="badge {status_badge}">{status}</span></td>
                                <td><a href="{p['url']}" target="_blank" class="text-blue-600">View</a></td>
                            </tr>
'''

day_card += '''                        </tbody>
                    </table>
                </div>
            </div>
        </div>
'''

# Build new comparison table row with Latest highlighting
comparison_row = f'''
                        <tr style="background: #fce7f3;">
                            <td><strong>June 16, 2026</strong><br><span style="font-size:0.75rem;color:#999;">Latest</span></td>
                            <td>{len(products)}</td>
                            <td class="price">₹{avg_price}</td>
                            <td class="rating">{avg_rating}★</td>
                            <td>{total_reviews:,}</td>
                            <td>Scrape.do</td>
                            <td><a href="kapiva_data_2026-06-16.json" download class="text-purple-600">JSON</a> | <a href="kapiva_data_2026-06-16.csv" download class="text-blue-600">CSV</a> | <a href="kapiva_data_2026-06-16.xlsx" download class="text-green-600">Excel</a></td>
                        </tr>
'''

# Insert comparison row after June 14 row
pattern = r'(June 14, 2026.*?Excel</a></td>\s*</tr>)'
match = re.search(pattern, html, re.DOTALL)
if match:
    end_pos = match.end()
    html = html[:end_pos] + '\n' + comparison_row + html[end_pos:]

# Insert day card before footer
footer_pattern = r'(\s*<footer class="text-center)'
match = re.search(footer_pattern, html, re.DOTALL)
if match:
    insert_pos = match.start()
    html = html[:insert_pos] + '\n' + day_card + html[insert_pos:]

# Update footer updated date
html = re.sub(r'Updated: June \d+, \d{4}', 'Updated: June 16, 2026', html)

# Save updated HTML
with open('index.html', 'w') as f:
    f.write(html)

print(f"Updated index.html with June 16, 2026 data (APPEND-ONLY mode)")
print(f"Historical data preserved through June 14, 2026")
print(f"New day card added: {len(products)} products, ₹{avg_price}, {avg_rating}★, {total_reviews:,} reviews")
