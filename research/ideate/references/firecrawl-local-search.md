# Using Local Firecrawl for Web Research

The local Firecrawl instance provides search without API keys when running at `localhost:3002`.

## Basic search

```bash
curl -s http://localhost:3002/v1/search -X POST \
  -H 'Content-Type: application/json' \
  -d '{"query":"your search query here"}'
```

## Search + parse in one shot

```bash
curl -s http://localhost:3002/v1/search -X POST \
  -H 'Content-Type: application/json' \
  -d '{"query":"cli tool that does X"}' | python3 -c "
import sys,json
d=json.load(sys.stdin)
for x in d['data'][:5]:
    print(f'{x[\"title\"]}\n  {x[\"url\"]}\n  {x[\"description\"][:200]}\n')
"
```

## Custom result count

Adjust the slice on `d['data']`:

```python
# 8 results instead of 5
for x in d['data'][:8]:
```

## Tips

- Firecrawl uses web indexing, not real-time search. Recent content may be stale.
- Structural search queries (site:github.com) do not work via Firecrawl.
- If Firecrawl is down: `docker restart firecrawl-api-1`.

## When to use

- Checking if a product/tool/idea already exists
- Looking for GitHub repos by description
- General web research where search engine operators are not needed
