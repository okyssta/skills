# Steam API Research Reference

Use these when web_search credits are exhausted, for bulk game research, or when you need verified descriptions and metadata. Steam API is free and does not require authentication for store data.

## Primary endpoint: App Details

```bash
curl -s "https://store.steampowered.com/api/appdetails?appids=APPID" \
  -H "User-Agent: Mozilla/5.0"
```

Returns JSON with:
- `name`, `short_description`, `about_the_game` (HTML)
- `genres` (array of {id, description})
- `release_date` ({coming_soon, date})
- `developers`, `publishers`
- `metacritic` (score, url)
- `price_overview` ({currency, initial, final, discount_percent})

Extract quick fields:
```bash
curl -s "https://store.steampowered.com/api/appdetails?appids=APPID" \
  -H "User-Agent: Mozilla/5.0" | python3 -c "
import json, sys
data = json.load(sys.stdin)
aid = list(data.keys())[0]
if data[aid]['success']:
    d = data[aid]['data']
    print('NAME:', d.get('name'))
    print('SHORT:', d.get('short_description','')[:400])
    print('TAGS:', [t['description'] for t in d.get('genres',[])])
"
```

## Search by keyword

Returns HTML that you grep for app links:

```bash
curl -sL "https://store.steampowered.com/search/?term=${QUERY}&category1=998" \
  -H "User-Agent: Mozilla/5.0" 2>&1 | \
  grep -oP 'href="https://store.steampowered.com/app/[^"]+"' | head -10
```

Pass multiple queries to cast a wide net:
- Try synonyms and rephrasings of the core mechanic
- Search by theme + mechanic separately ("funeral game", then "delivery game")
- Search by genre + concept ("parking simulator", "dimensional game")

## Category 998

`category1=998` filters to **Games** (excludes software, DLC, soundtracks). Always include it.

## Description fallback (HTML parsing)

When the JSON API returns descriptions inside HTML tags, use regex extraction:

```bash
# og:description (clean, short)
m = re.search(r'<meta property="og:description" content="([^"]+)"', html)

# short_description from inline JSON (richer)
m = re.search(r'"short_description":"([^"]+)"', html)

# about_text (full description, may be truncated)
m = re.search(r'"about_text":"([^"]+)"', html)
```

## Research protocol for a new concept

1. **Search the core mechanic** — "hearse game", "delivery remains game", "funeral home game"
2. **Search adjacent mechanics** — "towing game", "cargo physics game", "physics delivery"
3. **Search the theme** — "death comedy game", "dark humor indie"
4. **Check each found game's app details** — verify if it's really a competitor or just same-word-different-game
5. **Build the comparison table** — Overlap column is the *appearance* of similarity; Difference column is the mechanical distinction that makes it not-a-clone

## When to use vs web_search

| Tool | When |
|------|------|
| web_search | Broad market awareness, recent releases, non-Steam platforms (itch.io, Game Pass), public sentiment, "has anyone made X" |
| Steam API | Verification of specific games, bulk comparison, descriptions, metadata, checking "is this actually a competitor" |
| Both | Always use Steam API to verify games found via web search |
