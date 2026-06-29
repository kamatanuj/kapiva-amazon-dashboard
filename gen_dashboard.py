#!/usr/bin/env python3
"""
Regenerate the Kapiva Amazon dashboard index.html from all JSON data files.
Reads every kapiva_data_YYYY-MM-DD.json + historical files, produces a complete
dashboard with day cards, product detail tables, and a comparison table.
"""
import json, os, re
from datetime import datetime

os.chdir('/root/kapiva')


def parse_price_int(p):
    try:
        return int(str(p).replace(',', '').replace('₹', '').split('.')[0])
    except Exception:
        return None


def format_price(p):
    if p is None:
        return 'N/A'
    try:
        return f'₹{int(str(p).replace(",","").replace("₹","").split(".")[0])}'
    except Exception:
        return str(p)


def normalize_product(p):
    """Normalize product dict from any schema to a common shape."""
    # Map alternative field names
    out = {}
    out['name'] = p.get('name') or p.get('title') or p.get('Product_Name') or p.get('Title') or ''
    out['category'] = p.get('category') or p.get('Category') or ''
    out['asin'] = p.get('asin') or p.get('ASIN') or ''
    out['price'] = p.get('price') if p.get('price') is not None else p.get('Price')
    out['rating'] = p.get('rating') if p.get('rating') is not None else p.get('Rating')
    out['reviews'] = p.get('reviews') if p.get('reviews') is not None else p.get('Reviews')
    out['availability'] = p.get('availability') or p.get('Stock') or p.get('stock') or 'Unknown'
    out['status'] = p.get('status', '')
    out['url'] = p.get('url') or f'https://www.amazon.in/dp/{out["asin"]}'
    return out


def normalize_data(data):
    """Normalize the whole data dict — compute summary if missing, normalize products."""
    products = data.get('products', [])
    products = [normalize_product(p) for p in products]
    data['products'] = products

    if 'summary' not in data or not data.get('summary'):
        # Compute from products
        prices = [parse_price_int(p['price']) for p in products]
        prices = [pr for pr in prices if pr is not None]
        ratings = [float(p['rating']) for p in products if p.get('rating') is not None]
        review_vals = []
        for p in products:
            r = p.get('reviews')
            if r is not None:
                try:
                    review_vals.append(int(r))
                except (ValueError, TypeError):
                    pass
        avg_price = round(sum(prices) / len(prices)) if prices else None
        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else None
        total_reviews = sum(review_vals) if review_vals else 0
        data['summary'] = {
            'avg_price': avg_price,
            'avg_rating': avg_rating,
            'total_reviews': total_reviews,
            'total_products': len(products),
        }

    if 'data_source' not in data:
        data['data_source'] = data.get('service', 'Amazon Scraper')

    return data


# ─── Collect all data files ───
data_files = []

# Regular daily files
for f in sorted(os.listdir('.')):
    m = re.match(r'kapiva_data_(\d{4}-\d{2}-\d{2})\.json$', f)
    if m:
        date_str = m.group(1)
        try:
            with open(f) as fh:
                data = json.load(fh)
            data_files.append((date_str, f, normalize_data(data)))
        except Exception as e:
            print(f'Skip {f}: {e}')

# Historical file
hist_file = 'kapiva_historical_2024-06-04.json'
if os.path.exists(hist_file):
    with open(hist_file) as fh:
        data_files.append(('2024-06-04', hist_file, normalize_data(json.load(fh))))

# June 8 special file
j8_file = 'kapiva_june8_2026.json'
if os.path.exists(j8_file):
    with open(j8_file) as fh:
        data_files.append(('2026-06-08', j8_file, normalize_data(json.load(fh))))

# Sort by date descending (newest first)
data_files.sort(key=lambda x: x[0], reverse=True)

print(f'Found {len(data_files)} data files')
for date_str, fname, data in data_files:
    s = data.get('summary', {})
    print(f'  {date_str}: avg_price=₹{s.get("avg_price","?")}, products={s.get("total_products","?")}')

# ─── Day card gradient colors ───
DAY_GRADIENTS = {
    '2026-06-29': 'linear-gradient(135deg, #059669 0%, #065f46 100%)',
    '2026-06-28': 'linear-gradient(135deg, #0d9488 0%, #0f766e 100%)',
    '2026-06-27': 'linear-gradient(135deg, #0f172a 0%, #334155 100%)',
    '2026-06-26': 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
    '2026-06-25': 'linear-gradient(135deg, #0ea5e9 0%, #0369a1 100%)',
    '2026-06-24': 'linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)',
    '2026-06-23': 'linear-gradient(135deg, #f43f5e 0%, #e11d48 100%)',
    '2026-06-22': 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)',
    '2026-06-21': 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    '2026-06-20': 'linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%)',
    '2026-06-19': 'linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)',
    '2026-06-16': 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
    '2026-06-14': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    '2026-06-13': 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    '2026-06-12': 'linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%)',
    '2026-06-11': 'linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)',
    '2026-06-10': 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
    '2026-06-09': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    '2026-06-08': 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
    '2024-06-04': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
}
DEFAULT_GRADIENT = 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)'


def format_reviews(n):
    if n is None:
        return '0'
    n = int(n)
    if n >= 1000:
        return f'{n/1000:.1f}K'
    return str(n)


def format_date_label(date_str):
    """Convert 2026-06-29 to 'June 29, 2026'"""
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%B %-d, %Y')
    except Exception:
        return date_str


def get_time_label(date_str, data):
    """Get the time label for the card."""
    gen_at = data.get('generated_at', '')
    if 'T' in gen_at:
        try:
            dt = datetime.fromisoformat(gen_at)
            hour = dt.hour
            if hour < 12:
                return 'Morning Scrape'
            elif hour < 17:
                return 'Afternoon Scrape'
            else:
                return 'Evening Scrape'
        except Exception:
            pass
    if date_str == '2024-06-04':
        return 'Historical'
    return 'Daily Scrape'


def escape_html(s):
    if s is None:
        return ''
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def generate_day_card(date_str, fname, data, css_class):
    """Generate HTML for a single day card with product details."""
    products = data.get('products', [])
    summary = data.get('summary', {})
    data_source = data.get('data_source', 'Amazon Scraper')
    date_label = format_date_label(date_str)
    time_label = get_time_label(date_str, data)

    avg_price = format_price(summary.get('avg_price'))
    avg_rating = summary.get('avg_rating')
    avg_rating_str = f'{avg_rating}★' if avg_rating else 'N/A'
    total_reviews = format_reviews(summary.get('total_reviews', 0))
    total_products = summary.get('total_products', len(products))

    # CSV/XLSX filenames derived from JSON filename
    base = fname.replace('.json', '')
    csv_name = base + '.csv'
    xlsx_name = base + '.xlsx'

    gradient = DAY_GRADIENTS.get(date_str, DEFAULT_GRADIENT)

    html = f'''<div class="day-card">
<div class="day-header" style="background: {gradient};">
<span><i class="fas fa-star mr-2"></i>{date_label} - {time_label}</span>
<span class="badge bg-white/20">{total_products} Products</span>
</div>
<div class="day-body">
<div class="stats-grid">
<div class="stat-box"><div class="stat-value">{avg_price}</div><div class="stat-label">Avg Price</div></div>
<div class="stat-box"><div class="stat-value">{avg_rating_str}</div><div class="stat-label">Avg Rating</div></div>
<div class="stat-box"><div class="stat-value">{total_reviews}</div><div class="stat-label">Total Reviews</div></div>
<div class="stat-box"><div class="stat-value" style="font-size:0.9rem;">{escape_html(data_source)}</div><div class="stat-label">Source</div></div>
</div>
<div class="download-grid">
<a href="{fname}" download class="download-btn btn-json"><i class="fas fa-download mr-1"></i> JSON</a>
<a href="{csv_name}" download class="download-btn btn-csv"><i class="fas fa-download mr-1"></i> CSV</a>
<a href="{xlsx_name}" download class="download-btn btn-excel"><i class="fas fa-download mr-1"></i> Excel</a>
</div>
<div class="product-details">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
<h3>All Products Details ({date_label})</h3>
<span class="badge badge-success">{total_products} Active Products</span>
</div>
<table class="detail-table">
<thead>
<tr><th>#</th><th>Product Name</th><th>Category</th><th>ASIN</th><th>Price</th><th>Rating</th><th>Reviews</th><th>Status</th><th>Amazon Link</th></tr>
</thead>
<tbody>
'''

    for i, p in enumerate(products, 1):
        name = escape_html(p.get('name', ''))
        category = escape_html(p.get('category', ''))
        asin = p.get('asin', '')
        price = format_price(p.get('price'))
        rating = p.get('rating')
        rating_str = f'{rating}★' if rating else 'N/A'
        reviews = format_reviews(p.get('reviews', 0))
        availability = p.get('availability', 'Unknown')
        status = p.get('status', '')
        url = p.get('url', f'https://www.amazon.in/dp/{asin}')

        # Badge for availability
        if 'in stock' in availability.lower():
            badge = 'badge-success'
            badge_text = 'In Stock'
        elif 'out' in availability.lower():
            badge = 'badge-error'
            badge_text = 'Out of Stock'
        elif status == 'interpolated':
            badge = 'badge-warning'
            badge_text = 'Interpolated'
        else:
            badge = 'badge-warning'
            badge_text = availability

        html += f'''<tr>
<td>{i}</td>
<td><strong>{name}</strong></td>
<td>{category}</td>
<td><code style="font-size:0.75rem;">{asin}</code></td>
<td class="price">{price}</td>
<td class="rating">{rating_str}</td>
<td>{reviews}</td>
<td><span class="badge {badge}">{badge_text}</span></td>
<td><a href="{url}" target="_blank" class="text-blue-600">View</a></td>
</tr>
'''

    html += '''</tbody>
</table>
</div>
</div>
</div>
'''
    return html


def generate_comparison_table(data_files):
    """Generate the day-wise comparison table."""
    html = '''<div class="day-card mt-8">
<div class="day-header" style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);">
<span><i class="fas fa-chart-line mr-2"></i>Day-wise Comparison</span>
</div>
<div class="day-body">
<table class="product-table">
<thead>
<tr>
<th>Date</th>
<th>Products</th>
<th>Avg Price</th>
<th>Avg Rating</th>
<th>Total Reviews</th>
<th>Source</th>
<th>Downloads</th>
</tr>
</thead>
<tbody>
'''

    for date_str, fname, data in data_files:
        summary = data.get('summary', {})
        products = data.get('products', [])
        date_label = format_date_label(date_str)
        time_label = get_time_label(date_str, data)

        avg_price = format_price(summary.get('avg_price'))
        avg_rating = summary.get('avg_rating')
        avg_rating_str = f'{avg_rating}★' if avg_rating else 'N/A'
        total_reviews = format_reviews(summary.get('total_reviews', 0))
        total_products = summary.get('total_products', len(products))
        data_source = data.get('data_source', 'Amazon Scraper')

        base = fname.replace('.json', '')
        csv_name = base + '.csv'
        xlsx_name = base + '.xlsx'

        html += f'''<tr>
<td><strong>{date_label}</strong><br/><span style="font-size:0.75rem;color:#999;">{time_label}</span></td>
<td>{total_products}</td>
<td class="price">{avg_price}</td>
<td class="rating">{avg_rating_str}</td>
<td>{total_reviews}</td>
<td>{escape_html(data_source)}</td>
<td><a class="text-purple-600" download="" href="{fname}">JSON</a> | <a class="text-blue-600" download="" href="{csv_name}">CSV</a> | <a class="text-green-600" download="" href="{xlsx_name}">Excel</a></td>
</tr>
'''

    html += '''</tbody>
</table>
</div>
</div>
'''
    return html


# ─── Build the full HTML ───
html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Kapiva Dashboard - Day-wise Data</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet"/>
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet"/>
<style>
        .day-card {{ background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px; overflow: hidden; }}
        .day-header {{ padding: 16px 20px; color: white; font-weight: bold; font-size: 1.1rem; display: flex; justify-content: space-between; align-items: center; }}
        .day-body {{ padding: 20px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 12px; margin-bottom: 16px; }}
        .stat-box {{ background: #f8fafc; padding: 12px; border-radius: 6px; text-align: center; }}
        .stat-value {{ font-size: 1.5rem; font-weight: bold; color: #1e293b; }}
        .stat-label {{ font-size: 0.75rem; color: #64748b; margin-top: 4px; }}
        .download-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }}
        .download-btn {{ padding: 10px; border-radius: 6px; text-decoration: none; color: white; text-align: center; font-size: 0.85rem; font-weight: 500; transition: transform 0.2s, box-shadow 0.2s; }}
        .download-btn:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
        .btn-json {{ background: #8b5cf6; }}
        .btn-csv {{ background: #3b82f6; }}
        .btn-excel {{ background: #10b981; }}
        .product-table {{ width: 100%; border-collapse: collapse; margin-top: 16px; font-size: 0.85rem; }}
        .product-table th {{ background: #f1f5f9; padding: 10px; text-align: left; font-weight: 600; color: #475569; }}
        .product-table td {{ padding: 10px; border-bottom: 1px solid #e2e8f0; }}
        .product-table tr:hover {{ background: #f8fafc; }}
        .badge {{ padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; font-weight: 600; }}
        .badge-success {{ background: #dcfce7; color: #166534; }}
        .badge-error {{ background: #fee2e2; color: #991b1b; }}
        .badge-warning {{ background: #fef3c7; color: #92400e; }}
        .price {{ font-weight: 600; color: #059669; }}
        .rating {{ color: #f59e0b; }}
        .product-details {{ margin-top: 20px; border-top: 2px solid #e2e8f0; padding-top: 20px; }}
        .product-details h3 {{ font-size: 1.1rem; font-weight: 600; color: #1e293b; margin-bottom: 12px; }}
        .detail-table {{ width: 100%; border-collapse: collapse; font-size: 0.8rem; }}
        .detail-table th {{ background: #f8fafc; padding: 8px; text-align: left; font-weight: 600; color: #475569; border-bottom: 2px solid #e2e8f0; }}
        .detail-table td {{ padding: 8px; border-bottom: 1px solid #e2e8f0; }}
        .detail-table tr:nth-child(even) {{ background: #f8fafc; }}
        .detail-table tr:hover {{ background: #e2e8f0; }}
    </style>
</head>
<body class="bg-gray-100">
<div class="container mx-auto px-4 py-6 max-w-6xl">
<!-- Header -->
<header class="text-center mb-8">
<h1 class="text-3xl font-bold text-gray-800"><i class="fas fa-calendar-alt mr-2 text-indigo-600"></i>Kapiva Dashboard</h1>
<p class="text-gray-600 mt-2">Day-wise Product Data with Download Options</p>
<div class="mt-4 flex justify-center gap-4">
<span class="px-4 py-2 bg-indigo-100 rounded-full text-sm"><i class="fas fa-file-code mr-1"></i> JSON</span>
<span class="px-4 py-2 bg-blue-100 rounded-full text-sm"><i class="fas fa-file-csv mr-1"></i> CSV</span>
<span class="px-4 py-2 bg-green-100 rounded-full text-sm"><i class="fas fa-file-excel mr-1"></i> Excel</span>
</div>
</header>
'''

# Generate day cards (newest first — already sorted)
for date_str, fname, data in data_files:
    html += generate_day_card(date_str, fname, data, '')

# Generate comparison table
html += generate_comparison_table(data_files)

# Footer
now_str = datetime.now().strftime('%B %d, %Y at %H:%M')
html += '''
<footer class="text-center mt-8 mb-4 text-gray-500 text-sm">
<p>Kapiva Amazon Price Tracker &bull; Data scraped via Apify Amazon Scraper</p>
<p class="mt-1">Last updated: ''' + now_str + ''' IST</p>
</footer>
</div>
<script>
(function() {
    function parseCardDate(card) {
        const headerText = card.querySelector('.day-header span')?.textContent || '';
        const match = headerText.match(/(January|February|March|April|May|June|July|August|September|October|November|December)\\s+(\\d{1,2}),\\s+(\\d{4})/);
        if (!match) return 0;
        return new Date(match[1] + ' ' + match[2] + ', ' + match[3]).getTime();
    }

    const container = document.querySelector('.container');
    if (!container) return;

    const header = container.querySelector('header');
    const footer = container.querySelector('footer');
    const cards = Array.from(container.querySelectorAll('.day-card:not(.mt-8)'));

    cards.sort(function(a, b) {
        return parseCardDate(b) - parseCardDate(a);
    });

    cards.forEach(function(card) {
        container.insertBefore(card, footer);
    });
})();
</script>
</body>
</html>
'''

with open('index.html', 'w') as f:
    f.write(html)

print(f'\\nGenerated index.html ({len(html)} bytes, {len(data_files)} day cards)')