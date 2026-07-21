# Google Maps Storefront Capture

Capture real storefront/interior photos from Google Maps business listings
for multi-location SEO projects (store directories, GBP photo audits,
competitor research).

## Prerequisites

```bash
pip install playwright
# Or use existing playwright from node_modules
```

## How It Works

Google Maps place pages render per-store detail panels with real user-uploaded
storefront/interior photos. Playwright navigates to each store's search URL
and screenshots the detail panel. Works without API keys.

## Script Pattern

```python
import asyncio
from playwright.async_api import async_playwright

STORES = [
    # (slug, search_name, address_fragment)
    ("derby", "Fone World Derby", "Derbion DE1 2PG"),
    ("oxford", "Fone World Oxford", "29 Queen St OX1 1ER"),
]

OUTPUT_DIR = "/path/to/output"

async def capture_all():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"]
        )
        for slug, name, address in STORES:
            page = await browser.new_page(viewport={"width": 1400, "height": 900})
            query = f"https://www.google.com/maps/search/{name.replace(' ', '+')}+{address.replace(' ', '+')}"
            await page.goto(query, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(4000)  # let panels render
            await page.screenshot(path=f"{OUTPUT_DIR}/gmaps-{slug}.png")
            await page.close()
        await browser.close()

asyncio.run(capture_all())
```

## Pitfalls

1. **Search vs Detail page.** The `maps/search/` URL may show a search results
   list instead of the single-store detail page. `maps/place/` URLs with
   coordinates are more reliable but need lat/lng from schema or pre-lookup.
   When a search yields multiple results, the screenshot shows the list — still
   useful (ratings, addresses, phone numbers visible for each).

2. **Non-logged-in limited view.** Google serves a truncated view to
   non-logged-in users. The place detail panel (photo, rating, hours, phone)
   still renders, but full photo galleries may be hidden.

3. **Arabic/RTL locale.** On ARM64 servers, locale or IP-based routing may
   serve Google Maps in Arabic (right-to-left layout). Screenshots still
   capture all business info — the photos and data are the same.

4. **IP-based rate limiting.** Google Maps has rate limits for unauthenticated
   requests. For 15+ stores, sequential capture works fine (1 request every
   10 seconds). For hundreds, add delays or rotate residential IPs.

5. **Permanently closed locations.** Some stores show "Permanently closed".
   The listing data (photos, address, phone) is still captured correctly.

## When to Use vs Alternatives

- **Playwright screenshots** (this method): Need the actual storefront photo
  from Google Maps for a small number of locations. Fast, no API key.
- **Google Places API**: Need structured photo data, reviews, metrics at scale.
  Requires a Google Cloud API key with Places API enabled (billing).
- **Street View Static API**: Need exterior building photos via Street View.
  Requires API key, less reliable for mall/kiosk stores without Street View.
- **Web_extract / Firecrawl**: Need the text content/location data without
  the visual photo. More reliable for non-logged-in rate limits.
