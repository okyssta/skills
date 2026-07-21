# Web Extraction Fallbacks (when browser/Firecrawl/web_search are down)

When all three standard tools fail — browser timeout, Firecrawl payment
required, web_search out of credits, or the site IP-blocks your datacenter
— curl against the page's internal JSON API, the Wayback Machine, or a
lightweight search engine can still get the job done.

## Decision tree

```
Data needed from a website?
├─ Standard tools available? → use them
└─ Blocked (browser timeout, Firecrawl 402, search down, IP-blocked)?
   ├─ Need search? → try DuckDuckGo Lite
   ├─ Need page content? → curl the URL directly, look for JSON endpoints
   ├─ IP-blocked (Reddit, etc)? → try Wayback Machine (web.archive.org)
   ├─ Need structured data? → find the JSON API the page itself consumes
   └─ Need GitHub repo data? → use `gh api search/repositories`
```

## 1. DuckDuckGo Lite (search fallback)

When `web_search` is unavailable, DuckDuckGo's lightweight search page
works with plain curl:

```bash
curl -sL "https://lite.duckduckgo.com/lite?q=your+search+term" \
  -H "User-Agent: Mozilla/5.0"
```

Pipe through sed to strip HTML tags and grep for relevant results.
The Lite version returns minimal HTML with actual search results in
plain anchor tags — no JS, no heavy DOM, no CloudFlare.

## 2. Curl the page and find its JSON API

Many modern sites load their data from a JSON endpoint that the JS
widget on the page consumes. It's often faster and more reliable than
scraping HTML.

### Step-by-step

```bash
# 1. Fetch the page HTML, extract JS variable assignments and API URLs
curl -sL "https://example.com/page" | grep -oP '(fetch|axios|\.get|\.post)\s*\(\s*['"'"'][^'"'"']+' | head -5

# 2. Look for script tags containing JSON data or endpoint URLs
curl -sL "https://example.com/page" | grep -oP 'https?://[^"'"'"' ]*\.json'

# 3. Hit the found JSON endpoint directly
curl -sL "https://www.oracle.com/a/ocom/docs/oci-free-tier_v1.json"
```

### Real example (Oracle Free Tier)

```bash
# The free tier page loads its spec table from this JSON file:
curl -sL "https://www.oracle.com/a/ocom/docs/oci-free-tier_v1.json"
# → Returns structured array of {Featured_Product, Free_Period,
#    Product_Category, fields: {Service_Name}, Description,
#    Monthly_Free_Amount}
```

### Real example (Steam)

See `indie-game-research` skill — Steam exposes `storesearch` and
`appdetails` API endpoints that return clean JSON.

## 3. Identify JSON endpoint patterns

Common naming conventions for internal APIs:

- `/a/ocom/docs/*.json` (Oracle — note the `a/` prefix for assets)
- `data-*` attributes in HTML that reference API URLs
- `window.__INITIAL_STATE__` or `window.__DATA__` in page source
- `/api/v1/`, `/rest/`, `/graphql` paths
- Endpoints referenced in `<script>` tags with `fetch()` or `axios`

## 4. GitHub API fallback (when web_search/web_extract/browser are down)

When you need GitHub repository data — trending repos, star counts, README
content — and all standard scraping tools fail (Firecrawl 402, browser
timeout, web_search out of credits), the `gh` CLI's authenticated API access
is a reliable fallback.

**Prerequisites:** `gh auth status` must show logged in. The unauthenticated
REST API rate-limits at 60 req/hr per IP — authenticated gets 5,000 req/hr.

### Search repos by stars

```bash
# Top repos created since 2024, sorted by stars
gh api search/repositories --method GET \
  -f q="created:2024-01-01..2026-12-31" \
  -f sort="stars" -f order="desc" -f per_page="30" \
  --jq '.items[] | "\(.full_name) | ⭐\(.stargazers_count) | \(.language // "N/A") | \(.description // "N/A") | created: \(.created_at[:10])"'
```

Key parameters:
- `q="created:2024-01-01..2024-12-31"` — date filter (required to avoid dwarfed-by-all-time results)
- `sort="stars"` — star-based sort (only option for search)
- `per_page="30"` — max per page (GitHub limit). Page with `-f page="2"`
- `--jq` — field extraction on JSON output. Pipe through `head -30` for pagination.

### Page through results

```bash
gh api search/repositories --method GET \
  -f q="created:2024-01-01..2026-12-31" \
  -f sort="stars" -f order="desc" -f per_page="30" -f page="2" \
  --jq '.items[] | "\(.full_name) | ⭐\(.stargazers_count)"'
```

### Get a repo's README content

```bash
gh api repos/$OWNER/$REPO/readme --jq '.content' | base64 -d | head -60
```

The API returns base64-encoded content. Always pipe through `base64 -d`.

### Get repo metadata

```bash
gh api repos/$OWNER/$REPO --jq '{name, stargazers_count, language, description, created_at}'
```

### Time-period star velocity comparison

To understand which periods saw the most growth, query by half-year:

```bash
for period in "2024-01-01..2024-06-30" "2024-07-01..2024-12-31" \
              "2025-01-01..2025-06-30" "2025-07-01..2025-12-31"; do
  echo "=== $period ==="
  gh api search/repositories --method GET \
    -f q="created:$period" -f sort="stars" -f order="desc" -f per_page="5" \
    --jq '.items[] | "\(.full_name) | ⭐\(.stargazers_count) | created: \(.created_at[:10])"'
done
```

### Pitfalls

- **Base64 padding**: `gh api <path>/readme` returns content with standard
  base64 padding. `base64 -d` handles it on Linux, `base64 -D` on macOS.
- **`per_page` max is 100**, but for responsive output stick to 30. The
  `total_count` field in search results gives true total — paginate with
  `page=N` to walk through.
- **README API returns the rendered README**, not the raw file. For raw
  content, use `gh api repos/$OWNER/$REPO/contents/README.md` instead
  (still base64-encoded).
- **Rate limits**: 5,000 authenticated req/hr for all `gh api` calls.
  Each search counts as one request. If hitting limits, cache results
  to disk with `> /tmp/github-scan-$(date +%s).json`.

## 5. Parse the HTML for structured hints

```bash
# Extract JSON embedded in script tags (common SPA pattern)
curl -sL "https://example.com" | grep -oP 'window\.__DATA__\s*=\s*\{[^}]+'

# Find API URLs in the page
curl -sL "https://example.com" | grep -oP '["'"'"'](/api/[^"'"'"']+)["'"'"']' | sort -u

# Find product/card data in data attributes
curl -sL "https://example.com" | grep -oP 'data-[a-z-]+="[^"]*"' | sort -u
```

## 6. DNS resolution workaround (when curl fails but dig works)

Sometimes curl returns `Could not resolve host` even though `dig` resolves
the domain normally. This happens with stale DNS caches, split-horizon DNS,
or resolver mismatch in container/cloud environments.

### Workaround: `curl --resolve`

```bash
# 1. Get the IP
dig +short example.com

# 2. Bypass DNS resolution entirely
curl -s --resolve "www.example.com:443:192.124.249.13" \
  -A "Mozilla/5.0" "https://www.example.com/"
```

The `--resolve` flag overrides DNS resolution for that host:port pair.
Use it when curl can't resolve but dig succeeds — it avoids the OS
resolver entirely.

### Detect the issue

```bash
# If this works:
dig +short example.com
# But this fails:
curl -s "https://example.com"
# → DNS mismatch. Use --resolve.
```

### Pitfalls

- **Expired IPs**: The cached IP may be stale. Always verify with
  `dig +short` before pinning.
- **HTTPS**: Must specify port `:443` for TLS hosts. The certificate
  SAN must still match the hostname — `--resolve` bypasses DNS, not
  TLS verification.
- **CDNs/dynamic routing**: For sites behind CloudFlare/Akamai, the IP
  changes frequently. Re-resolve each session.
- **Only when dig works**: If dig itself fails, the issue is network
  connectivity, not DNS — check firewall/routing.

## 7. Wayback Machine (when the site IP-blocks you)

When a target site **IP-blocks your datacenter** (Reddit, some forums,
and CloudFlare-protected sites return `"Blocked"` / `403` for datacenter
IPs), the Wayback Machine at web.archive.org provides cached copies via
plain curl — no API key, no stealth tools, no rate limits.

### Quick fetch

```bash
# Fetch raw archived page (no Wayback header/frame)
curl -sL "https://web.archive.org/web/20250803040502if_/https://original.site/page"
```

The timestamp `20250803040502` = YYYYMMDDHHMMSS. Pick a date when the
page was likely alive. The `if_` suffix strips the Wayback navigation
frame — you get the raw HTML.

### CDX API: find available snapshots

```bash
curl -sL "https://web.archive.org/cdx/search/cdx?url=https://original.site/page&output=json" | jq '.[] | .[1]'
```

Returns an array of `[timestamp, original_url, status_code, ...]`. Pick
the most recent 200-status timestamp before the content was deleted or
moved.

### Reddit-specific pattern (tested from Oracle Cloud)

Reddit aggressively blocks datacenter IPs (Oracle, AWS, GCP). Old.reddit,
new.reddit, `.json` API — all return `Blocked` / `403`. No User-Agent
spoofing (including Googlebot) bypasses it.

**Solution:** Fetch via Wayback Machine:

```bash
# Step 1: Find snapshots via CDX
curl -sL "https://web.archive.org/cdx/search/cdx?url=https://www.reddit.com/r/SUBREDDIT/comments/ID/&output=json"

# Step 2: Pick a 200-status timestamp and fetch
curl -sL "https://web.archive.org/web/20250803040502if_/https://www.reddit.com/r/SUBREDDIT/comments/ID/"
```

The archived page contains the post body, comments, and metadata (score,
author). Strip scripts/styles via Python or grep for clean text.

**Pitfall:** The CDX API returns snapshots for the exact URL. If Reddit
redirected (e.g. `old.reddit.com` → `www.reddit.com`), try both URL forms.

### Limitations

| Problem | Workaround |
|---------|-----------|
| Page was never crawled | No Wayback fallback — try other caches (Google Cache, archive.is) |
| Snapshot shows "Blocked" too | Wayback archived the blocked response — pick an earlier timestamp |
| Content is JS-rendered (not in static HTML) | Wayback only captures initial HTML; dynamic content missing |
| Wayback returns 429 / rate-limited | Add `sleep 1` between requests. Use fewer CDX queries |
| Snapshot is hours/days old | Acceptable for most content extraction use cases |

### Other archive services

```bash
# Google Cache (different coverage than Wayback)
curl -sL "http://webcache.googleusercontent.com/search?q=cache:https://example.com/page" \
  -H "User-Agent: Mozilla/5.0"

# archive.today (paid, limited free tier)
# Note: archive.today blocks most automated access
```

## Final pitfalls
