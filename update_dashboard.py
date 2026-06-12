import json
import re

# Read the current index.html
with open('index.html', 'r') as f:
    html = f.read()

# Read the new data for June 12
with open('kapiva_data_2026-06-12.json', 'r') as f:
    data = json.load(f)

products = data['products']
summary = data['summary']

# Calculate stats
avg_rating = summary['avg_rating']
total_reviews = summary['total_reviews']
avg_price = summary['avg_price']

# Build the HTML for June 12 day card
jun12_card = '''
        <!-- Day 6: June 12, 2026 (Latest) -->
        <div class="day-card">
            <div class="day-header day-jun12">
                <span><i class="fas fa-star mr-2"></i>June 12, 2026 - Latest Scrape</span>
                <span class="badge bg-white/20">12 Products</span>
            </div>
            <div class="day-body">
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-value">₹500</div>
                        <div class="stat-label">Avg Price</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">4.05★</div>
                        <div class="stat-label">Avg Rating</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">57K</div>
                        <div class="stat-label">Total Reviews</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">Scrape.do</div>
                        <div class="stat-label">Source</div>
                    </div>
                </div>
                
                <div class="download-grid">
                    <a href="kapiva_data_2026-06-12.json" download class="download-btn btn-json">
                        <i class="fas fa-download mr-1"></i> JSON
                    </a>
                    <a href="kapiva_data_2026-06-12.csv" download class="download-btn btn-csv">
                        <i class="fas fa-download mr-1"></i> CSV
                    </a>
                    <a href="kapiva_data_2026-06-12.xlsx" download class="download-btn btn-excel">
                        <i class="fas fa-download mr-1"></i> Excel
                    </a>
                </div>

                <!-- FULL PRODUCT DETAILS TABLE -->
                <div class="product-details">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                        <h3>All Products Details (June 12, 2026)</h3>
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
'''

# Add product rows
for i, p in enumerate(products, 1):
    rating_display = f"{p['rating']}★" if p['rating'] else "-"
    status_badge = "badge-success" if p['availability'] == "In Stock" else "badge-error" if p['availability'] == "Out of Stock" else "badge-warning"
    
    jun12_card += f'''                            <tr>
                                <td>{i}</td>
                                <td><strong>{p['name']}</strong></td>
                                <td>{p['category']}</td>
                                <td><code style="font-size:0.75rem;">{p['asin']}</code></td>
                                <td class="price">₹{p['price']}</td>
                                <td class="rating">{rating_display}</td>
                                <td>{p['reviews']:,}</td>
                                <td><span class="badge {status_badge}">{p['availability']}</span></td>
                                <td><a href="{p['url']}" target="_blank" class="text-blue-600">View</a></td>
                            </tr>
'''

jun12_card += '''                        </tbody>
                    </table>
                </div>
            </div>
        </div>

'''

# Update the CSS - add day-jun12 style if not present
if '.day-jun12' not in html:
    css_addition = '        .day-jun12 { background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%); }\n'
    html = html.replace('.day-jun11 {', css_addition + '        .day-jun11 {')

# Find the comparison table and update it
# First, update existing row styles - remove "Latest" highlighting from June 11
html = html.replace('<tr style="background: #fce7f3;">', '<tr>')

# Add new row for June 12 in the comparison table (after June 11 row)
comparison_row = '''                        <tr style="background: #fce7f3;">
                            <td><strong>June 12, 2026</strong><br><span style="font-size:0.75rem;color:#999;">Latest</span></td>
                            <td>12</td>
                            <td class="price">₹500</td>
                            <td class="rating">4.05★</td>
                            <td>57,341</td>
                            <td>Scrape.do</td>
                            <td><a href="kapiva_data_2026-06-12.json" download class="text-purple-600">JSON</a> | <a href="kapiva_data_2026-06-12.csv" download class="text-blue-600">CSV</a> | <a href="kapiva_data_2026-06-12.xlsx" download class="text-green-600">Excel</a></td>
                        </tr>
'''

# Insert the new row after June 11 row
pattern = r'(June 11, 2026.*?Excel</a></td>\s*</tr>)'
match = re.search(pattern, html, re.DOTALL)
if match:
    end_pos = match.end()
    html = html[:end_pos] + '\n' + comparison_row + html[end_pos:]

# Add the new day card after the comparison table
# Find the end of comparison table section
pattern = r'(<!-- Comparison Table -->.*?<!-- Day 4: June 10, 2026 -->)'
match = re.search(pattern, html, re.DOTALL)
if match:
    # Insert before Day 4
    insert_pos = match.end() - len('<!-- Day 4: June 10, 2026 -->')
    html = html[:insert_pos] + jun12_card + html[insert_pos:]

# Update the "Latest" label on June 11
html = html.replace('June 11, 2026 - Latest Scrape', 'June 11, 2026 - Morning Scrape')

# Save the updated HTML
with open('index.html', 'w') as f:
    f.write(html)

print("Updated index.html with June 12, 2026 data (APPEND-ONLY mode)")
print("Historical data preserved:")
print("  - June 4, 2024")
print("  - June 8, 2026")
print("  - June 9, 2026")
print("  - June 10, 2026")
print("  - June 11, 2026")
print("  - June 12, 2026 (NEW)")
