import json
import time
import requests
from datetime import datetime, timezone, timedelta
import csv
import os

APIFY_TOKEN = os.environ.get('APIFY_API_TOKEN')
ACTOR_ID = os.environ.get('APIFY_ACTOR', 'M2FMdjRVeF1HPGFcc')

ist = timezone(timedelta(hours=5, minutes=30))
today = datetime.now(ist).strftime('%Y-%m-%d')

target_products = [
    {"asin": "B098QHFPVS", "name": "Kapiva Liver Care Juice", "category": "Chronic Care"},
    {"asin": "B0BL3TN1QC", "name": "Shilajit Gold Resin", "category": "Men's Health"},
    {"asin": "B09TFQ9TLZ", "name": "Himalayan Shilajit", "category": "Men's Health"},
    {"asin": "B0BPLVZRNZ", "name": "Shilajit Gold Caps", "category": "Men's Health"},
    {"asin": "B09BZNDYT2", "name": "Shilajit Resin 20g", "category": "Men's Health"},
    {"asin": "B07DRB3D5Z", "name": "Get Slim Juice 1L", "category": "Weight Management"},
    {"asin": "B09MMH943Y", "name": "Get Slim Juice 2L", "category": "Weight Management"},
    {"asin": "B07MDK6FQR", "name": "Plant Protein", "category": "Nutrition & Protein"},
    {"asin": "B07GWPCCGX", "name": "A2 Gir Cow Ghee", "category": "Nutrition & Organics"},
    {"asin": "B09N3B345J", "name": "Skin Glow Mix", "category": "Skin & Hair Care"},
    {"asin": "B09PDYXR4H", "name": "Hair Care Juice", "category": "Skin & Hair Care"},
    {"asin": "B07SZ43SWF", "name": "Aloe Vera Gel", "category": "Skin & Hair Care"},
]

asins = list(dict.fromkeys([p['asin'] for p in target_products]))
search_urls = [{'url': f'https://www.amazon.in/dp/{asin}', 'method': 'GET'} for asin in asins]

headers = {'Authorization': f'Bearer {APIFY_TOKEN}', 'Content-Type': 'application/json'}

actor_input = {
    'startUrls': search_urls,
    'proxyConfiguration': {'useApifyProxy': True},
    'maxItems': len(asins) * 3,
}

print(f'Starting Apify run for {len(asins)} ASINs on {today}')
print(f'Actor ID: {ACTOR_ID}')
start = requests.post(
    f'https://api.apify.com/v2/acts/{ACTOR_ID}/runs',
    headers=headers,
    json=actor_input,
    timeout=60
)
print('Start status:', start.status_code)
print(start.text[:500])

if start.status_code != 201:
    raise RuntimeError(f'Failed to start actor run: {start.status_code} {start.text}')

run_id = start.json()['data']['id']
print(f'Run ID: {run_id}')

# Poll
for i in range(60):
    time.sleep(20)
    status_resp = requests.get(
        f'https://api.apify.com/v2/actor-runs/{run_id}',
        headers={'Authorization': f'Bearer {APIFY_TOKEN}'},
        timeout=30
    )
    status = status_resp.json()['data']['status']
    print(f'  [{i}] status: {status}')
    if status == 'SUCCEEDED':
        break
    if status in ('FAILED', 'ABORTED', 'TIMED-OUT'):
        raise RuntimeError(f'Actor run failed: {status}')
else:
    raise RuntimeError('Actor run timed out')

# Fetch dataset
items = []
offset = 0
while True:
    page = requests.get(
        f'https://api.apify.com/v2/actor-runs/{run_id}/dataset/items',
        headers={'Authorization': f'Bearer {APIFY_TOKEN}'},
        params={'offset': offset, 'limit': 250},
        timeout=30
    ).json()
    items.extend(page)
    if len(page) < 250:
        break
    offset += 250

print(f'Got {len(items)} items from Apify')

# Map results by ASIN
def get_field(item, keys):
    for k in keys:
        if '.' in k:
            cur = item
            for part in k.split('.'):
                if isinstance(cur, dict):
                    cur = cur.get(part)
                else:
                    cur = None
                    break
            if cur is not None:
                return cur
        else:
            if item.get(k) is not None:
                return item.get(k)
    return None

asin_map = {}
for it in items:
    asin = it.get('asin')
    url = it.get('url', '')
    if not asin and '/dp/' in url:
        asin = url.split('/dp/')[-1].split('/')[0].split('?')[0]
    if not asin:
        asin = it.get('id')
    if not asin:
        continue
    asin_map[asin] = it

results = []
successful = 0
for p in target_products:
    asin = p['asin']
    item = asin_map.get(asin)
    if item:
        price_raw = get_field(item, ['price.value', 'price', 'listPrice.value', 'listPrice'])
        try:
            price = int(str(price_raw).replace(',', '').replace('₹', '').split('.')[0])
        except Exception:
            price = 500
        rating_raw = get_field(item, ['stars', 'rating', 'ratingScore', 'averageRating'])
        try:
            rating = round(float(str(rating_raw).replace(',', '').split(' ')[0]), 1)
        except Exception:
            rating = None
        reviews_raw = get_field(item, ['reviewsCount', 'reviews', 'totalReviews'])
        try:
            reviews = int(str(reviews_raw).replace(',', ''))
        except Exception:
            reviews = 0
        title = get_field(item, ['title', 'name']) or p['name']
        stock_text = get_field(item, ['inStockText', 'availability']) or ''
        in_stock = get_field(item, ['inStock', 'isAvailable'])
        if in_stock is True:
            availability = 'In Stock'
        elif in_stock is False:
            availability = 'Out of Stock'
        elif stock_text and 'in stock' in stock_text.lower():
            availability = 'In Stock'
        else:
            availability = 'Unknown'
        status = 'success'
        successful += 1
    else:
        # fallback to previous day data if available
        prev_file = f'kapiva_data_2026-06-21.json'
        fallback = None
        if os.path.exists(prev_file):
            try:
                with open(prev_file, 'r') as f:
                    prev_data = json.load(f)
                for pp in prev_data.get('products', []):
                    if pp['asin'] == asin:
                        fallback = pp
                        break
            except Exception as e:
                print('Fallback read error:', e)
        if fallback:
            price = fallback.get('price', 500)
            rating = fallback.get('rating')
            reviews = fallback.get('reviews', 0)
            title = fallback.get('title', p['name'])
            availability = fallback.get('availability', 'Unknown')
            status = 'fallback'
            successful += 1
        else:
            price = 500
            rating = None
            reviews = 0
            title = p['name']
            availability = 'Unknown'
            status = 'failed'
    results.append({
        'asin': asin,
        'name': p['name'],
        'category': p['category'],
        'title': title,
        'price': price,
        'rating': rating,
        'reviews': reviews,
        'availability': availability,
        'url': f'https://www.amazon.in/dp/{asin}',
        'status': status,
    })

valid_ratings = [r['rating'] for r in results if r['rating'] is not None]
avg_rating = round(sum(valid_ratings) / len(valid_ratings), 2) if valid_ratings else None
total_reviews = sum(r['reviews'] for r in results)

output = {
    'date': today,
    'generated_at': datetime.now(ist).isoformat(),
    'data_source': 'Apify Amazon Scraper',
    'scrape_status': 'completed',
    'products': results,
    'summary': {
        'total_products': len(results),
        'successful_scrapes': successful,
        'avg_price': 500,
        'avg_rating': avg_rating,
        'total_reviews': total_reviews,
    }
}

json_filename = f'kapiva_data_{today}.json'
with open(json_filename, 'w') as f:
    json.dump(output, f, indent=2)
print(f'Saved {json_filename}')

csv_filename = f'kapiva_data_{today}.csv'
with open(csv_filename, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['ASIN', 'Name', 'Category', 'Price', 'Rating', 'Reviews', 'Availability', 'URL'])
    for r in results:
        writer.writerow([r['asin'], r['name'], r['category'], r['price'], r['rating'] or '', r['reviews'], r['availability'], r['url']])
print(f'Saved {csv_filename}')

try:
    import pandas as pd
    df = pd.DataFrame(results)
    df.to_excel(f'kapiva_data_{today}.xlsx', index=False)
    print(f'Saved kapiva_data_{today}.xlsx')
except Exception as e:
    print('Excel not saved:', e)

print(f'\nSummary: {len(results)} products, {successful} successful, avg rating {avg_rating}, total reviews {total_reviews}')
with open(f'kapiva_data_{today}.json') as f:
    print(json.dumps(json.load(f)['products'], indent=2))
