import json, re, glob
from datetime import datetime, timezone, timedelta

ist = timezone(timedelta(hours=5, minutes=30))
today_str = datetime.now(ist).strftime('%Y-%m-%d')
today_display = datetime.now(ist).strftime('%B %d, %Y')

def fmt_num(n):
    if n >= 1000:
        return f"{n/1000:.1f}K".replace('.0K', 'K')
    return str(n)

# Load all available date data files
data_files = sorted(glob.glob('kapiva_data_*.json'))
historical_file = 'kapiva_historical_2024-06-04.json'
june8_file = 'kapiva_june8_2026.json'

all_data = []

# Load historical
try:
    with open(historical_file) as f:
        d = json.load(f)
    all_data.append(("June 4, 2024", "Historical", "13", "₹899", "4.0★", "47,000", "Apify/ScrapingBee",
                      historical_file.replace('.json','')))
except: pass

try:
    with open(june8_file) as f:
        d = json.load(f)
    all_data.append(("June 8, 2026", "Morning", "11", "₹500", "4.1★", "15,000", "Scrape.do",
                      june8_file.replace('.json','')))
except: pass

# Load date-based data files
date_label_map = {}
for fp in reversed(data_files):
    try:
        with open(fp) as f:
            d = json.load(f)
        date_str = d.get('date', '')
        if not date_str:
            continue
        # Parse date into display
        parts = date_str.split('-')
        if len(parts) == 3:
            y, m, dnum = parts
            month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December']
            display = f"{month_names[int(m)]} {int(dnum)}, {y}"
        else:
            display = date_str
        
        src = d.get('data_source', 'Unknown').split('+')[0].strip()
        s = d.get('summary', {})
        total = s.get('total_products', 12)
        price = s.get('avg_price', 500)
        rating = s.get('avg_rating', 'N/A')
        reviews = s.get('total_reviews', 0)
        
        base = fp.replace('.json', '')
        all_data.append((display, '', str(total), f"₹{price}", f"{rating}★", fmt_num(reviews), src, base))
    except: pass

# Sort: newest first
def sort_key(item):
    name = item[0]
    if '2024' in name:
        return "0"
    # Parse month day
    m = re.search(r'(June|July|August|September)\s+(\d+)', name)
    if m:
        return f"{m.group(2):>03}"
    return "0"

all_data.sort(key=sort_key, reverse=True)

# Assign labels
for i, item in enumerate(all_data):
    display = item[0]
    if i == 0:
        label = "Latest"
    elif display == "June 4, 2024":
        label = "Historical"
    elif "today" in str(today_display) or display == today_display:
        label = "Latest"
    else:
        label = "Morning"
    all_data[i] = (display, label, item[2], item[3], item[4], item[5], item[6], item[7])

# Read index.html
with open('index.html') as f:
    html = f.read()

# Find comparison table tbody
start_idx = html.find('<table class="product-table">')
tbody_start = html.find('<tbody>', start_idx)
tbody_end = html.find('</tbody>', tbody_start)

# Build new tbody rows
rows = []
for display, label, products, price, rating, reviews, source, base in all_data:
    highlight = ' style="background: #fce7f3;"' if label == "Latest" else ''
    # Build download links
    dl_links = f'<a class="text-purple-600" download="" href="{base}.json">JSON</a> | <a class="text-blue-600" download="" href="{base}.csv">CSV</a> | <a class="text-green-600" download="" href="{base}.xlsx">Excel</a>'
    rows.append(f'''<tr{highlight}>
<td><strong>{display}</strong><br/><span style="font-size:0.75rem;color:#999;">{label}</span></td>
<td>{products}</td>
<td class="price">{price}</td>
<td class="rating">{rating}</td>
<td>{reviews}</td>
<td>{source}</td>
<td>{dl_links}</td>
</tr>''')

new_tbody = '<tbody>\n\n\n\n\n\n\n\n\n\n' + '\n'.join(rows) + '\n</tbody>'

html = html[:tbody_start] + new_tbody + html[tbody_end+8:]

with open('index.html', 'w') as f:
    f.write(html)

print(f'Comparison table rebuilt with {len(all_data)} dates')
for display, label, *_ in all_data:
    print(f'  {display} - {label}')
