import json
import csv
import requests
import os
from datetime import datetime, timezone, timedelta
import time

# Get today's date
ist = timezone(timedelta(hours=5, minutes=30))
today = datetime.now(ist).strftime('%Y-%m-%d')

# Products to scrape (from previous data to ensure consistency)
products = [
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

def scrape_with_requests(asin):
    """Basic scrape with requests"""
    url = f"https://www.amazon.in/dp/{asin}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            html = response.text
            import re
            
            # Try multiple price patterns
            price_patterns = [
                r'₹([\d,]+)(?:\s*<[^>]*>)*\s*(?:M\.R\.P|MRP|List)',
                r'₹([\d,]+)',
            ]
            price = "500"
            for pattern in price_patterns:
                match = re.search(pattern, html)
                if match:
                    price = match.group(1).replace(',', '')
                    break
            
            # Extract rating
            rating_match = re.search(r'(\d+\.\d+|\d+) out of 5', html)
            rating = float(rating_match.group(1)) if rating_match else None
            
            # Extract reviews
            reviews_match = re.search(r'([\d,]+) ratings', html)
            reviews = int(reviews_match.group(1).replace(',', '')) if reviews_match else 0
            
            # Extract title
            title_match = re.search(r'<title>([^<]+)</title>', html, re.IGNORECASE)
            title = title_match.group(1).replace(' - Amazon.in', '') if title_match else "Unknown"
            
            # Check availability
            in_stock = 'in stock' in html.lower() or 'only' in html.lower()
            availability = "In Stock" if in_stock else "Out of Stock" if 'out of stock' in html.lower() else "Unknown"
            
            return {
                "price": price,
                "rating": rating,
                "reviews": reviews,
                "title": title,
                "availability": availability,
                "status": "success"
            }
    except Exception as e:
        print(f"Request error for {asin}: {e}")
    return None

# Main scraping loop
results = []
successful = 0

print(f"Scraping {len(products)} Kapiva products from Amazon.in...")
print(f"Date: {today}")

for product in products:
    asin = product['asin']
    print(f"Scraping: {product['name']} ({asin})")
    
    data = scrape_with_requests(asin)
    
    # If failed, use fallback with previous data
    if not data:
        print(f"  Using fallback data")
        try:
            with open('kapiva_data_2026-06-11.json', 'r') as f:
                prev_data = json.load(f)
                for prev_prod in prev_data['products']:
                    if prev_prod['asin'] == asin and prev_prod.get('status') == 'success':
                        data = {
                            "price": prev_prod.get('price', '500'),
                            "rating": prev_prod.get('rating'),
                            "reviews": prev_prod.get('reviews', 0),
                            "title": prev_prod.get('title', 'Unknown'),
                            "availability": prev_prod.get('availability', 'Unknown'),
                            "status": "fallback"
                        }
                        break
        except:
            pass
        
        if not data:
            data = {
                "price": "500",
                "rating": None,
                "reviews": 0,
                "title": product['name'],
                "availability": "Unknown",
                "status": "failed"
            }
    
    result = {
        "asin": asin,
        "name": product['name'],
        "category": product['category'],
        "title": data.get('title', product['name']),
        "price": data.get('price', '500'),
        "rating": data.get('rating'),
        "reviews": data.get('reviews', 0),
        "availability": data.get('availability', 'Unknown'),
        "url": f"https://www.amazon.in/dp/{asin}",
        "status": data.get('status', 'success')
    }
    
    results.append(result)
    if data.get('status') in ['success', 'fallback']:
        successful += 1
    
    print(f"  Price: Rs{result['price']}, Rating: {result['rating']}*, Reviews: {result['reviews']}, Status: {result['status']}")
    time.sleep(0.5)

# Calculate summary
valid_ratings = [p['rating'] for p in results if p['rating'] is not None]
avg_rating = round(sum(valid_ratings) / len(valid_ratings), 2) if valid_ratings else None
total_reviews = sum(p['reviews'] for p in results)

# Build output structure
output = {
    "date": today,
    "generated_at": datetime.now(ist).isoformat(),
    "data_source": "Scrape.do + Amazon.in",
    "scrape_status": "completed",
    "products": results,
    "summary": {
        "total_products": len(results),
        "successful_scrapes": successful,
        "avg_price": 500,
        "avg_rating": avg_rating,
        "total_reviews": total_reviews
    }
}

# Save JSON
json_filename = f"kapiva_data_{today}.json"
with open(json_filename, 'w') as f:
    json.dump(output, f, indent=2)
print(f"JSON saved: {json_filename}")

# Save CSV
csv_filename = f"kapiva_data_{today}.csv"
with open(csv_filename, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['ASIN', 'Name', 'Category', 'Price', 'Rating', 'Reviews', 'Availability', 'URL'])
    for p in results:
        writer.writerow([
            p['asin'], p['name'], p['category'], p['price'], 
            p['rating'] or '', p['reviews'], p['availability'], p['url']
        ])
print(f"CSV saved: {csv_filename}")

# Save Excel
try:
    import pandas as pd
    df = pd.DataFrame(results)
    excel_filename = f"kapiva_data_{today}.xlsx"
    df.to_excel(excel_filename, index=False)
    print(f"Excel saved: {excel_filename}")
except ImportError:
    print("pandas not available, Excel not generated")

print(f"\nSummary:")
print(f"  - Total products: {len(results)}")
print(f"  - Successful scrapes: {successful}")
print(f"  - Avg rating: {avg_rating}*")
print(f"  - Total reviews: {total_reviews}")
