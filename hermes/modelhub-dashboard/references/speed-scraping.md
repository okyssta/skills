# Speed/TPS Scraping from OpenRouter Pages (chromium --dump-dom)

The OpenRouter API returns `null` for all speed/throughput/latency fields. However, the JS-rendered web pages at `https://openrouter.ai/{slug}` show real tok/s values per provider in a React table. Use `chromium-browser --headless --dump-dom` to get the fully rendered DOM.

## Why Not the API?

- `/api/v1/models` — `top_provider` has no speed data
- `/api/v1/models/{slug}/endpoints` — `throughput_last_30m` and `latency_last_30m` are null for every model
- The web page renders per-provider speed data from a different internal source

## Extraction Function

```python
def get_speed(slug):
    url = f"https://openrouter.ai/{slug}"
    try:
        html = subprocess.run(
            ["chromium-browser", "--headless", "--dump-dom", "--no-sandbox",
             "--disable-gpu", "--virtual-time-budget=5000", url],
            capture_output=True, text=True, timeout=30
        ).stdout
    except:
        return None
    tps_values = [float(m.group(1)) for m in re.finditer(r'>(\d+(?:\.\d+)?)\s*(?:tok/s|tps)<', html)]
    return max(tps_values) if tps_values else None
```

Key flags: `--dump-dom` runs JS; `--virtual-time-budget=5000` waits 5s for React rendering.

## Regex: `>(\d+(?:\.\d+)?)\s*(?:tok/s|tps)<`

Captures values like `">48 tok/s<"` or `">26 tps<"` from the provider throughput table cells. Returns `max()` across all providers for that model.

## Batch Approach (505 models, ~22 min)

Run on the **host** (chromium isn't inside Docker). Two-step: scrape to JSON, then import.

### Step 1: Extract slugs + scrape

```bash
docker compose exec -T db psql -U modelbench -d modelbench -t -A \
  -c "SELECT slug FROM models WHERE speed_tps = 0 OR speed_tps IS NULL;" > /tmp/slugs.txt

python3 /root/modelhub/cron/scrape_speed.py
```

Script at `cron/scrape_speed.py` reads `/tmp/slugs.txt`, writes `/tmp/speed_results.json`. Runs 3 chromium instances parallel via `ThreadPoolExecutor`.

### Step 2: Import to PostgreSQL

```bash
python3 -c "
import json, subprocess
d = json.load(open('/tmp/speed_results.json'))
with_speed = {k:v for k,v in d.items() if v}
for i in range(0, len(with_speed), 50):
    batch = list(with_speed.items())[i:i+50]
    sql = ';'.join(f\"UPDATE models SET speed_tps={v}, updated_at=NOW() WHERE slug='{k}'\" for k,v in batch)
    subprocess.run(['docker','compose','-f','/root/modelhub/docker-compose.yml',
        'exec','-T','db','psql','-U','modelbench','-d','modelbench','-c',sql])
    print(f'Imported {min(i+50, len(with_speed))}/{len(with_speed)}')
"
```

## Results (latest run)

- 342/505 models had speed data
- Average TPS: 65.3 tok/s
- 163 models without data (very new/old/niche providers)

## Performance Card on Model Pages

The template handles both cases:

```html
{% if model.speed_tps %}
  <strong>{{'%.1f'|format(model.speed_tps)}} <small>tok/s</small></strong>
{% else %}
  <strong>Not reported</strong>
{% endif %}
```

## Re-running

To refresh all speed data:
```bash
docker compose exec -T db psql -U modelbench -d modelbench -c \
  "UPDATE models SET speed_tps = 0 WHERE speed_tps > 0;"
# Then re-run steps 1-2 above
```
