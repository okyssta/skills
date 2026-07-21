# Shopify Cart & Shipping Testing

## Overview
Techniques for programmatically testing Shopify store carts and checking shipping rates, useful when cross-referencing eBay listings against your Shopify stores.

## Direct Cart URL (Bypasses Bot Detection)
Shopify's AJAX `/cart/add.js` endpoint is often blocked by Cloudflare bot protection after 2-3 rapid requests (HTTP 429). **Direct cart URL** bypasses this:

```
https://{store}/cart/VARIANT_ID1:QTY1,VARIANT_ID2:QTY2,...
```

### Example
```bash
curl -sL -A "Mozilla/5.0" -c cookies.txt \
  "https://www.example.com/cart/42664654045269:1,42636988186709:1,42621340581973:1" \
  -o /dev/null
```

### How it works
- GET request (not POST) — avoids AJAX-specific bot filters
- Shopify processes it as a session-based cart update
- Works with standard browser cookies
- Returns 302 redirect on success (follow with `-L`)

### Check cart contents
```bash
curl -s -A "Mozilla/5.0" -b cookies.txt \
  "https://www.example.com/cart.js" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'{d[\"item_count\"]} items, \${float(d[\"total_price\"])/100:.2f}')"
```

### Get variant IDs
```bash
# From products.json
curl -s "https://www.example.com/products.json?limit=50" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for p in data['products'][:10]:
    v = p['variants'][0]
    print(f\"{v['id']} | \${v['price']} | {p['title'][:60]} | avail={v['available']}\")
"
```

## Checking Shipping Rates — Limitations

### Old API (often deprecated)
Shopify's legacy `/cart/shipping_rates.json` and `/cart/prepare_shipping_rates.json` endpoints **no longer work** on stores using:
- Shopify Checkout Extensibility
- Shop Pay
- New checkout UI (post-2024)

These return `{"error":["There was a problem calculating your shipping rates..."]}`.

### Why
Modern Shopify stores calculate shipping exclusively within the checkout flow (JS-rendered). There's no REST API to get rates without completing checkout steps.

### What works for getting rate info
1. **Shipping policy page**: `https://{store}/policies/shipping-policy.html` — often has flat-rate details
2. **Manual browser checkout**: Add items via cart URL, go to checkout, enter address, see rates rendered
3. **Storefront API GraphQL** (requires a Storefront API access token, not always publicly available):
   ```
   POST /api/2024-01/graphql.json
   Headers: X-Shopify-Storefront-Access-Token: {token}
   ```

### Known Shipping Rate Patterns (from real stores)
| Store | Express | Standard |
|-------|---------|----------|
| ozarmour.co | $24.95 base + $15/item (capped $69.99) | Carrier-calculated (AusPost/TNT) |
| beekeepinggear.com.au | Available at checkout | Carrier-calculated (AusPost/Sendle) |

## Product Data Extraction (without API key)
```bash
# Get all products with prices, variants, weights, availability
curl -s "https://www.example.com/products.json?limit=250" > products.json

# Product fields available: id, title, handle, body_html, product_type, vendor,
# tags, variants[].price, variants[].grams, variants[].available, variants[].sku,
# images[].src
```

## Pitfalls

### 1. Cloudflare Rate Limiting
- After ~3 AJAX requests (POST/GET to `/cart/add.js`, `/cart.js`, `/cart/update.js`) the session gets HTTP 429 with Cloudflare challenge page
- **Fix**: Use direct cart URL (GET `/cart/ID:QTY,...`) instead of POST-based AJAX calls
- Read cart with `/cart.js` only after a 3+ second delay from the last request

### 2. Server IP Location Mismatch
- If your server is in UAE, Singapore, or other non-AU location, Shopify detects the IP country
- The cart defaults to the detected country's currency and pricing (server-timing header: `country;desc=\"AE\"`)
- Shipping rate calculations will be **international**, not domestic Australian
- **Impact**: you can't reliably get domestic AU shipping rates from non-AU servers
- **Workaround**: check the shipping policy page for flat rates, or use a browser/VPN in Australia

### 3. Shop Pay / Checkout Extensibility
- Stores using Shopify's newest checkout (Shop Pay) block all REST API shipping endpoints
- The checkout flow is a JS-rendered SPA — no simple HTTP automation possible
- The redirect chain is: `/checkout` → `shop.app/checkout/{store_id}/cn/{token}/en-au/shoppay` → back to `/checkouts/cn/{token}/en-au`
- `checkout.json` and `checkouts/{token}.json` both return HTML, not JSON
- **No workaround** without a real browser

### 4. Checkout Token Extraction
The checkout token is in the redirect URL: `/checkouts/{mode}/{token}/{locale}`
```bash
curl -sL -D headers.txt "https://store.com/checkout"
grep -i "location:" headers.txt | grep -oP 'checkouts/\w+/\K[a-zA-Z0-9]+'
```

### 5. Cart Clear Between Tests
Always clear the cart between test combinations:
```bash
curl -s "https://store.com/cart/clear"
# or
curl -s -X POST "https://store.com/cart/clear.js"
```

## Relating to eBay Listings
When cross-referencing eBay listings with Shopify products:
- Shopify `variants[].grams` gives product weight (in grams)
- This is the same weight that should appear as `Package Weight` on eBay
- The direct cart URL lets you verify shipping costs for eBay-listed items without placing real orders
