# OpenRouter API Scraping Patterns

The OpenRouter `/api/v1/models` endpoint returns ~350 models with pricing, benchmarks, and metadata. It's the best single source for model comparison data.

## Key API Structure

```
GET https://openrouter.ai/api/v1/models
```

Returns a JSON blob with a `data` array. Each entry has:

- `id`: slug like `"openai/gpt-5.6-sol"` or `"~anthropic/claude-latest"` (tilde-prefixed = aliases)
- `name`: human name like `"OpenAI: GPT-5.6 Sol"`
- `pricing`: `{"prompt": "0.000005", "completion": "0.00003", "input_cache_read": "...", ...}` — **strings**, sometimes `null` or missing
- `architecture`: `{"modality": "text+image+file->text", "input_modalities": [...], "output_modalities": [...]}` — sometimes a bare string like `"text->text"` instead of a dict
- `top_provider`: `{"context_length": 1050000, "max_completion_tokens": 128000, ...}` — sometimes `null`
- `benchmarks`: `{"artificial_analysis": {"intelligence_index": 58.9, "coding_index": 77.4, "agentic_index": 54}, "design_arena": [...]}` — sometimes empty dict
- `context_length`: int, sometimes 0
- `knowledge_cutoff`: string or null
- `reasoning`: `{"mandatory": true/false, "default_enabled": true, "supported_efforts": [...]}` — sometimes missing

## Null/None Defensive Patterns

Every field can be `null` from the JSON API. Defensive defaults:
```python
pricing = m.get('pricing') or {}          # defensive against explicit null
arch = m.get('architecture') or {}        # arch can be a string, not a dict
top_provider = m.get('top_provider') or {}  # sometimes null
benchmarks = m.get('benchmarks') or {}     # sometimes empty/absent
```

## Pricing Conversion

Pricing values are **per-token** as strings. Convert to per-1M-tokens:
```python
try:
    raw = pricing.get('prompt', 0)
    price_prompt = float(raw) * 1000000 if raw else 0.0
except (TypeError, ValueError):
    price_prompt = 0.0
```

## Safe Score Computation

Benchmark values can be `None` or `0`:
```python
coding = aa.get('coding_index') if isinstance(aa, dict) else None
intelligence = aa.get('intelligence_index') if isinstance(aa, dict) else None

# Safe arithmetic
ci = float(coding or 0)
cc = float(coding or 0)
valid_scores = [s for s in [ci, cc] if s > 0]
overall = round(sum(valid_scores) / len(valid_scores), 1) if valid_scores else 0.0
```

## Upsert Strategy

Two tiers of data quality:
1. **Curated models** (source='curated'): hand-set benchmark scores preserved. OpenRouter only fills in pricing/providers/context if empty.
2. **Scraped models** (source='openrouter'): fully updated from API on each scrape.

Check: `existing.source == 'curated'` before deciding update scope.

## Per-Model Error Isolation

Wrap each model's processing in a try/except so one malformed entry doesn't kill the whole batch:
```python
count = 0
errors = 0
for m in models_data:
    try:
        # ... process model ...
        count += 1
    except Exception as e:
        logger.warning(f"Skipping {slug}: {e}")
        errors += 1
        continue
```

## Developer Detection from Slug

Slug prefixes map to developers. Maintain a dict:
```python
dev_map = {
    'openai': 'OpenAI', 'anthropic': 'Anthropic',
    'google': 'Google', 'meta-llama': 'Meta',
    'deepseek': 'DeepSeek', 'qwen': 'Alibaba (Qwen)',
    'x-ai': 'xAI', 'mistral': 'Mistral AI',
    'yi': '01.AI (Yi)', 'zhipu': 'Zhipu AI',
    # etc.
}
```
