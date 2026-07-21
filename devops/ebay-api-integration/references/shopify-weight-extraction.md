# Shopify Product Weight Extraction

## Overview
When matching eBay listings to internal product data, Shopify stores provide product weights via their JSON API. This covers extracting weight data and matching it to eBay listings.

## Shopify JSON API

Every Shopify store exposes product data including weights via two approaches:

### Approach A: Per-Product (`/products/<handle>.json`)

Best for known handles or one-off lookups.

```python
import json, urllib.request

url = "https://www.beekeepinggear.com.au/products/bee-brush.json"
resp = urllib.request.urlopen(url, timeout=15)
data = json.loads(resp.read())

product = data["product"]
for v in product["variants"]:
    weight_kg = v.get("weight", 0)
    weight_unit = v.get("weight_unit", "")
    grams = v.get("grams", 0)
```

### Approach B: Bulk (`/products.json` paginated) — PREFERRED for full catalog

Simpler and faster than sitemap + per-product lookups. Fetches ALL products with weights in one paginated stream. Works even for stores with auto-generated handles.

```python
def get_all_shopify_products(base_url):
    all_prods = []
    page = 1
    while True:
        url = f'{base_url}/products.json?limit=250&page={page}'
        resp = urllib.request.urlopen(url, timeout=15)
        data = json.loads(resp.read())
        if not data['products']:
            break
        all_prods.extend(data['products'])
        if len(data['products']) < 250:
            break
        page += 1
    return all_prods

# Usage — merge both stores
bg = get_all_shopify_products("https://www.beekeepinggear.com.au")  # 622 prods
oz = get_all_shopify_products("https://ozarmour.co")               # 805 prods
all_shopify = bg + oz
```

Each product entry contains `variants[0].grams` — the weight in grams.

### Limitations
- **Weights available** per variant in grams/weight/weight_unit fields
- **Dimensions NOT available** in Shopify product JSON — must parse body_html with regex or know them separately
- No auth required for public product pages
- `/products.json` has a 250-item page limit, but pagination is straightforward (page=1,2,3...)

## Finding Product Handles

### From Sitemap (XML Parsing — Preferred)

Use `xml.etree.ElementTree` with proper namespaces to parse Shopify's product sitemaps:

```python
import urllib.request
import xml.etree.ElementTree as ET

def parse_shopify_sitemap(sitemap_url, domain):
    """Parse Shopify product sitemap XML into handle→title index."""
    resp = urllib.request.urlopen(sitemap_url, timeout=30)
    root = ET.fromstring(resp.read())
    
    ns = {
        "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
        "image": "http://www.google.com/schemas/sitemap-image/1.1"
    }
    
    index = {}
    for url_el in root.findall("sm:url", ns):
        loc = url_el.find("sm:loc", ns)
        if loc is None or "/products/" not in loc.text:
            continue
        handle = loc.text.rstrip("/").split("/")[-1]
        
        # Get title from first image:title element
        img = url_el.find("image:image", ns)
        title = handle.replace("-", " ").title()  # fallback
        if img is not None:
            img_title = img.find("image:title", ns)
            if img_title is not None and img_title.text:
                title = img_title.text
        
        index[handle.lower()] = {"title": title, "url": loc.text, "domain": domain}
    
    return index

# Usage
bkg = parse_shopify_sitemap(
    "https://www.beekeepinggear.com.au/sitemap_products_1.xml",
    "www.beekeepinggear.com.au"
)
oza = parse_shopify_sitemap(
    "https://ozarmour.co/sitemap_products_1.xml",
    "ozarmour.co"
)
all_shopify = {**bkg, **oza}
```

**Why XML parsing beats grep/txt**: Shopify sitemaps are proper XML with `<image:title>` elements containing the actual product names. The web-extract tool flattens XML to text which loses the structure. Always fetch + parse the raw XML.

### Fuzzy Title Matching (eBay → Shopify)
```python
from difflib import SequenceMatcher

def find_best_shopify_match(ebay_title, shopify_index, min_score=0.4):
    """Find best Shopify product match for an eBay title."""
    ebay_lower = ebay_title.lower()
    best = None
    best_score = 0
    
    for handle, info in shopify_index.items():
        score = SequenceMatcher(None, ebay_lower, info["title"].lower()).ratio()
        if score > best_score:
            best_score = score
            best = (handle, info)
    
    if best and best_score >= min_score:
        return best, best_score
    return None, best_score
```
- >= 0.70: Clear match (apply weight/dims directly)
- 0.40-0.69: Ambiguous — verify manually (title differences common across marketplaces)
- < 0.40: Different product

### Handle-from-URL (for one-off lookups)
When you already know (or can guess) the handle:
```python
# Direct JSON lookup
url = f"https://store.com/products/{handle}.json"
```

### Obscured / Auto-Generated Handles
Some Shopify stores (e.g., ozarmour.co) use auto-generated handles like `oa3lmvbj` instead of descriptive slugs. The sitemap XML parsing approach handles these automatically because it maps every handle to its `<image:title>`. You cannot guess these handles — always use the sitemap.

### Simpler Title Matching (Alternative to SequenceMatcher)

For matching eBay titles to Shopify products, a three-tier string comparison often works better than SequenceMatcher (which can match unrelated common words):

```python
def match_product(ebay_title, shopify_products):
    """Match eBay title to Shopify product: exact → contains → word-overlap."""
    title_lower = ebay_title.lower().strip()
    
    # Tier 1: Exact match
    for p in shopify_products:
        if p['title'].lower().strip() == title_lower:
            return p
    
    # Tier 2: Contains match
    for p in shopify_products:
        st = p['title'].lower().strip()
        if title_lower in st or st in title_lower:
            return p
    
    # Tier 3: Word-overlap (≥3 common words)
    title_words = set(title_lower.split())
    best_match = None
    best_score = 0
    for p in shopify_products:
        sw = set(p['title'].lower().split())
        overlap = len(title_words & sw)
        if overlap > best_score and overlap >= 3:
            best_score = overlap
            best_match = p
    
    return best_match
```

**Real-world result** (OZ ARMOUR, Jul 2026): matched **168/169** missing-weight eBay listings to Shopify products using this approach.

### Fallback: Weight Estimation from Title

When no Shopify match exists, estimate weight from product keywords and price:

```python
def estimate_weight_from_title(title, price=None):
    """Heuristic weight estimation when no Shopify data available."""
    t = title.lower()
    p = float(price) if price else 0
    
    if any(w in t for w in ['suit', 'jacket', 'trouser']):
        if 'child' in t: return 1000
        if 'stout' in t: return 3000
        return 2000
    if any(w in t for w in ['glove', 'veil']):
        return 300
    if any(w in t for w in ['hive', 'beehive', 'bottom board']):
        return 5000
    if any(w in t for w in ['extractor', 'honey tank', 'creamer']):
        return 15000
    if any(w in t for w in ['fork', 'knife', 'tool', 'brush', 'cutter']):
        return 300
    if any(w in t for w in ['book', 'guide', 'manual']):
        return 500
    if 'frame' in t:
        return 2000
    # Fallback by price bracket
    if p > 1000: return 20000
    if p > 200: return 5000
    if p > 50: return 1000
    return 500
```

## Combined Matching Strategy (eBay → AU eBay → Shopify fallback)

When a seller has the same products listed on multiple eBay marketplaces (AU, US, UK) with different Item IDs, use this two-tier strategy:

```python
from difflib import SequenceMatcher

# Tier 1: Match US/UK item to AU eBay listing (gets weight + dimensions)
def match_via_au_ebay(ebay_title_lower, au_with_data):
    """Match US/UK item to an AU eBay listing that has weight+dims."""
    best_score = 0
    best_match = None
    for au_title, (weight, dims) in au_with_data.items():
        score = SequenceMatcher(None, ebay_title_lower, au_title).ratio()
        if score > best_score:
            best_score = score
            best_match = (au_title, weight, dims, score)
    return best_match

# Tier 2: Only if Tier 1 score < 0.65, try Shopify title match
def match_via_shopify(ebay_title, shopify_index):
    """Fallback: get weight only from Shopify store."""
    best_result, score = find_best_shopify_match(ebay_title, shopify_index)
    if best_result and score >= 0.4:
        handle, info = best_result
        weight = get_shopify_weight(handle, info["domain"])
        return weight, info["title"], info["url"], info["domain"], score
    return None

# Full pipeline
def resolve_item(item_id, ebay_title, site, au_with_data, shopify_index):
    result = match_via_au_ebay(ebay_title.lower(), au_with_data)
    
    if result and result[3] >= 0.65:
        # Complete data from AU eBay
        return {"weight": result[1], "dims": result[2], 
                "source": f"AU eBay match {result[3]:.2f}", 
                "needs_review": "no"}
    
    shop_result = match_via_shopify(ebay_title, shopify_index)
    if shop_result:
        return {"weight": shop_result[0], "dims": "",
                "source": f"Shopify {shop_result[4]:.2f}",
                "needs_review": "needs dims"}
    
    return {"weight": "", "dims": "", "source": "NOT FOUND",
            "needs_review": "MANUAL"}
```

**Real-world outcome** (OZ ARMOUR/APIARIST account, Jul 2026):
- 140 US/UK items needing data
- Tier 1 (AU eBay match): **108 items** — complete weight+dims retrieved
- Tier 2 (Shopify fallback): **32 items** — weight retrieved, needs dims manually
- **0 items** completely unresolved

## Multiple Shopify Stores

Sellers often run multiple Shopify stores for different regions or brands. Parse ALL sitemaps and merge the indexes:

```python
stores = {
    "beekeepinggear": "https://www.beekeepinggear.com.au/sitemap_products_1.xml",
    "ozarmour": "https://ozarmour.co/sitemap_products_1.xml",
}
all_shopify = {}
for name, url in stores.items():
    index = parse_shopify_sitemap(url, name)
    all_shopify.update(index)
```

When matching, the fuzzy title matcher will naturally pick the best match regardless of which store it came from. The `info["domain"]` field tracks the source.

## Cross-Site Product Matching (eBay AU ↔ US/UK)

Cross-listed items have different Item IDs per marketplace but same physical product. Weight/dims are **product-level** — identical across sites.

### Strategy
1. Extract AU items with known weight/dims from eBay API export
2. Apply two-tier matching (AU eBay → Shopify fallback)
3. Track what still needs manual dimensions

### Common Pitfall: Title Differences
Same products named differently across sites:
- AU: "Battery Operated Electric Uncapping Knife"
- US: "Electric Uncapping Knife — Made in USA, 220/240 Volts"
Score ~0.47 but same product. The SequenceMatcher threshold needs to be forgiving (0.40+ for Shopify match).

### Size of the Problem (Real-World Benchmark)
- ~140 US/UK items needing matching
- ~110s for full pipeline (parsing 2 sitemaps + ~35 Shopify JSON calls)
- 0.3s delay between Shopify JSON calls to avoid rate limiting
