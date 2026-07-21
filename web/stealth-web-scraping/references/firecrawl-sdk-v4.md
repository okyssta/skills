# Firecrawl SDK v4 API Reference

## Breaking changes from v3

| v3 | v4 | Notes |
|----|-----|-------|
| `app.scrape_url(url)` | `app.scrape(url)` | Method renamed |
| Returns `dict` | Returns `Document` (pydantic) | Access via attributes, not dict methods |
| `result["markdown"]` | `result.markdown` | Pydantic attribute access |
| `result.get("metadata")` | `result.metadata` | Pydantic attribute access |

## Document object structure

```python
result = app.scrape("https://example.com")

# result is firecrawl.v2.types.Document
result.metadata          # DocumentMetadata object
result.metadata.title    # str
result.metadata.description  # str
result.metadata.sourceURL    # str
result.markdown          # str (clean markdown content)
result.html              # str (raw HTML, if requested)
result.links             # list of links
result.warning           # str or None
```

## Self-hosted URL

When running locally, pass `api_url` instead of `api_key`:

```python
app = FirecrawlApp(api_url="http://localhost:3002")
```

No API key needed for self-hosted unless USE_DB_AUTHENTICATION=true.

## Docker Compose v2 requirement

Firecrawl's docker-compose.yaml uses `${VAR:+default}` bash parameter
expansion which is NOT supported by docker-compose v1 (the Python
package). You MUST use docker compose v2 (the Go plugin):

```bash
# Check version
docker compose version  # should show v2.x

# If v1 only, install v2 plugin:
mkdir -p /usr/local/lib/docker/cli-plugins
curl -SL "https://github.com/docker/compose/releases/latest/docker-compose-linux-$(uname -m)" \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
```

## Self-hosted environment (.env)

Minimal .env for local firecrawl:

```
REDIS_URL=redis://redis:6379
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres
USE_DB_AUTHENTICATION=false
NUM_WORKERS_PER_QUEUE=4
CRAWL_CONCURRENT_REQUESTS=5
MAX_CONCURRENT_JOBS=3
BROWSER_POOL_SIZE=3
LOGGING_LEVEL=info
```

Optional (for LLM-powered features):
- OPENAI_API_KEY / OPENAI_BASE_URL
- MODEL_NAME / MODEL_EMBEDDING_NAME
- OLLAMA_BASE_URL (for local LLMs)
