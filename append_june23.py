import json
import re
from datetime import datetime, timezone, timedelta

ist = timezone(timedelta(hours=5, minutes=30))
today_str = datetime.now(ist).strftime('%Y-%m-%d')
today_display = datetime.now(ist).strftime('%B %d, %Y')

with open('index.html', 'r') as f:
    html = f.read()

with open(f'kapiva_data_{today_str}.json', 'r') as f:
    data = json.load(f)

products = data['products']
summary = data['summary']

def fmt_num(n):
    if n >= 1000:
        return f"{n/1000:.1f}K".replace('.0K', 'K')
    return str(n)

# Add CSS for new day
css_class = 'day-jun23'
css_entry = '        .day-jun23 { background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%); }\n'
if '.day-jun23' not in html:
    html = html.replace('.day-jun4 {', css_entry + '        .day-jun4 {')

# Remove existing "Latest" marker from comparison table for June 22
for d in ['June 22, 2026', 'June 21, 2026', 'June 20, 2026']:
    html = re.sub(
        rf'<tr style="background: #fce7f3;">\s*<td><strong>{re.escape(d)}</strong>.*?</tr>',
        '',
        html,
        flags=re.DOTALL
    )

# Change June 22 label from "Latest" to "Morning"
html = html.replace(
    '<td><strong>June 22, 2026</strong><br><span style="font-size:0.75rem;color:#999;">Latest</span></td>',
    '<td><strong>June 22, 2026</strong><br><span style="font-size:0.75rem;color:#999;">Morning</span></td>'
)

# Add new Latest row at top of comparison table
comparison_row = f'''                        <tr style="background: #fce7f3;">
                            <td><strong>{today_display}</strong><br><span style="font-size:0.75rem;color:#999;">Latest</span></td>
                            <td>{summary['total_products']}</td>
                            <td class="price">₹{summary['avg_price']}</td>
                            <td class="rating">{summary['avg_rating']}★</td>
                            <td>{fmt_num(summary['total_reviews'])}</td>
                            <td>Amazon.in Direct</td>
                            <td><a href="kapiva_data_{today_str}.json" download class="text-purple-600">JSON</a> | <a href="kapiva_data_{today_str}.csv" download class="text-blue-600">CSV</a> | <a href="kapiva_data_{today_str}.xlsx" download class="text-green-600">Excel</a></td>
                        </tr>
'''

html = html.replace('<tbody>\n                        <tr>\n                            <td><strong>June 4, 2024</strong>', '<tbody>\n' + comparison_row + '                        <tr>\n                            <td><strong>June 4, 2024</strong>')

# Build detail rows
in_stock_count = sum(1 for p in products if p['availability'] == 'In Stock')
unknown_count = sum(1 for p in products if p['availability'] == 'Unknown')
out_count = sum(1 for p in products if p['availability'] == 'Out of Stock')

detail_rows = []
for i, p in enumerate(products, 1):
    rating_display = f"{p['rating']}★" if p['rating'] else "-"
    reviews_disp = fmt_num(p['reviews']) if p['reviews'] else "0"
    if p['availability'] == 'In Stock':
        status_badge = 'badge-success'
    elif p['availability'] == 'Out of Stock':
        status_badge = 'badge-error'
    else:
        status_badge = 'badge-warning'
    detail_rows.append(f'''                            <tr>
                                <td>{i}</td>
                                <td><strong>{p['name']}</strong></td>
                                <td>{p['category']}</td>
                                <td><code style="font-size:0.75rem;">{p['asin']}</code></td>
                                <td class="price">₹{p['price']}</td>
                                <td class="rating">{rating_display}</td>
                                <td>{reviews_disp}</td>
                                <td><span class="badge {status_badge}">{p['availability']}</span></td>
                                <td><a href="{p['url']}" target="_blank" class="text-blue-600">View</a></td>
                            </tr>''')

detail_rows.append(f'''                            <tr style="background:#f1f5f9; font-weight:600;">
                                <td>—</td>
                                <td><strong>Summary</strong></td>
                                <td>{len(products)} Products</td>
                                <td>—</td>
                                <td class="price">₹{summary['avg_price']} avg</td>
                                <td class="rating">{summary['avg_rating']}★ avg</td>
                                <td>{fmt_num(summary['total_reviews'])} total</td>
                                <td><span class="badge badge-success">{in_stock_count} In Stock</span></td>
                                <td><span class="badge badge-warning">{unknown_count} Unknown</span> <span class="badge badge-error">{out_count} Out</span></td>
                            </tr>''')

rows_html = '\n'.join(detail_rows)

new_card = f'''        <!-- Day: {today_display} (Latest) -->
        <div class="day-card">
            <div class="day-header day-jun23">
                <span><i class="fas fa-star mr-2"></i>{today_display} - Morning Scrape</span>
                <span class="badge bg-white/20">{summary['total_products']} Products</span>
            </div>
            <div class="day-body">
                <div class="stats-grid">
                    <div class="stat-box"><div class="stat-value">₹{summary['avg_price']}</div><div class="stat-label">Avg Price</div></div>
                    <div class="stat-box"><div class="stat-value">{summary['avg_rating']}★</div><div class="stat-label">Avg Rating</div></div>
                    <div class="stat-box"><div class="stat-value">{fmt_num(summary['total_reviews'])}</div><div class="stat-label">Total Reviews</div></div>
                    <div class="stat-box"><div class="stat-value">Amazon.in Direct</div><div class="stat-label">Source</div></div>
                </div>
                <div class="download-grid">
                    <a href="kapiva_data_{today_str}.json" download class="download-btn btn-json"><i class="fas fa-download mr-1"></i> JSON</a>
                    <a href="kapiva_data_{today_str}.csv" download class="download-btn btn-csv"><i class="fas fa-download mr-1"></i> CSV</a>
                    <a href="kapiva_data_{today_str}.xlsx" download class="download-btn btn-excel"><i class="fas fa-download mr-1"></i> Excel</a>
                </div>
                <div class="product-details">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                        <h3>All Products Details ({today_display})</h3>
                        <span class="badge badge-success">{summary['total_products']} Active Products</span>
                    </div>
                    <table class="detail-table">
                        <thead>
                            <tr><th>#</th><th>Product Name</th><th>Category</th><th>ASIN</th><th>Price</th><th>Rating</th><th>Reviews</th><th>Status</th><th>Amazon Link</th></tr>
                        </thead>
                        <tbody>
{rows_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

'''

html = html.replace('<footer class="text-center mt-8 text-gray-500 text-sm">', new_card + '<footer class="text-center mt-8 text-gray-500 text-sm">')
html = re.sub(r'Updated: [^<]+</p>', f'Updated: {today_display}</p>', html)

with open('index.html', 'w') as f:
    f.write(html)

print(f'Updated index.html with {today_display} data')
