# Custom Providers Pipeline — Investigation Guide

## Config Structure

```yaml
custom_providers:
  - name: My_Combo
    base_url: http://localhost:20128/v1
    api_key: sk-xxx
    model: my_combo              # singular: the "active" model
    models:                       # dict: per-model config (context_length, etc.)
      my_combo:
        context_length: 1000000
      nvidia/z-ai/glm-5.2:
        context_length: 1000000
    discover_models: false        # KEY: set false to preserve models: list
```

## Pipeline (tracing order)

| Step | File | Line | What it does |
|------|------|------|-------------|
| 1 | `hermes_cli/config.py` | `_normalize_custom_provider_entry()` ~4580 | Normalizes entry, preserves `models` dict |
| 2 | `hermes_cli/config.py` | `get_compatible_custom_providers()` ~4814 | Deduplicates, merges `providers:` dict entries |
| 3 | `hermes_cli/inventory.py` | `load_picker_context()` ~79 | Builds `ConfigContext` with `custom_providers` list |
| 4 | `hermes_cli/inventory.py` | `build_models_payload()` ~111 | Calls `list_authenticated_providers()`, deduplicates aggregators |
| 5 | `hermes_cli/model_switch.py` | `list_authenticated_providers()` ~1447 | Main model listing logic |
| 5a | `hermes_cli/model_switch.py` | Section 4 ~2128 | Groups custom_providers by (url, credential, mode), adds `model:` + `models:` keys |
| 5b | `hermes_cli/model_switch.py` | Section 4 probe ~2315 | If `should_probe=True`, fetches live `/models` and REPLACES configured models |
| 5c | `hermes_cli/model_switch.py` | `_save_discovered_models_to_config()` ~104 | POST-probe writeback: persists discovered models to config.yaml on disk. ⚠️ Unconditionally overwrites dict-form `models` with flat list (bug #67841, fixed in PR #67878) |
| 6 | `tui_gateway/server.py` | `model.options` JSON-RPC ~12367 | Desktop picker calls this |
| 7 | `hermes_cli/web_server.py` | `GET /api/model/options` ~4270 | REST alternative for Dashboard |
| 8 | UI renders | `model-picker.tsx` / `ModelPickerDialog.tsx` | Displays `provider.models` list |

## Key Functions to Read

- `_normalize_custom_provider_entry(entry)` — config.py:4580 — Normalizes a single entry
- `_declared_model_ids(value)` — model_switch.py:55 — Extracts model IDs from dict/list/string
- `list_authenticated_providers()` — model_switch.py:1447 — The main model listing function
- `_can_probe_custom_provider()` — model_switch.py:1527 — Decides if probing is allowed
- `fetch_api_models()` — models.py:3598 — Hits `/models` endpoint
- `_save_discovered_models_to_config()` — model_switch.py:104 — Writes probe results back to disk (⚠️ dict-form trap)

## Probing Decision Logic

```
should_probe = (
    _can_probe_custom_provider(row_is_current)  # Desktop: probe_current_custom_provider
    AND bool(api_url)                            # must have an endpoint
    AND (bool(api_key) OR not grp["models"])     # api_key present → always probe
    AND grp.get("discover_models", True)         # explicit opt-out available
)
```

When probing succeeds: `grp["models"] = live_models` (line 2331) — replaces everything.

## Desktop Probe Flags

```python
# Normal picker open (non-refresh):
probe_custom_providers=False           # don't probe non-current providers
probe_current_custom_provider=True     # DO probe the active one

# Explicit refresh:
probe_custom_providers=True
probe_current_custom_provider=False    # (redundant since all are probed)
```

## Debugging Steps

1. **Confirm config parsing**: Run `_normalize_custom_provider_entry(entry)` — check `models` key is present
2. **Confirm compatible merge**: Run `get_compatible_custom_providers(config)` — check models dict preserved
3. **Check probing condition**: Trace `should_probe` in Section 4 — is `api_key` set? Is `discover_models` true?
4. **Check probe result**: Mock `fetch_api_models` to see what the endpoint returns vs what's configured
5. **Check UI filter**: In `model-picker.tsx` line 181, providers with zero models are filtered out
6. **Check config.yaml writeback**: If probing succeeds, inspect `config.yaml` — has `_save_discovered_models_to_config` replaced your dict-form `models` with a flat list?

## Common Misconfigurations

- **Missing `discover_models: false`**: Most common cause. Endpoint's `/models` response replaces configured subset.
- **`models:` as list instead of dict**: Older configs may use `models: [id1, id2]` — `_normalize_custom_provider_entry` converts lists to dict shape, but values lose context_length overrides.
- **Endpoint doesn't return models via `/models`**: Probe fails silently → configured models preserved (this is correct behavior).
- **Provider slug collision**: If the custom provider slug matches a built-in (e.g., `openai`), section 4 skips it to avoid shadowing. The `slug` is derived from `name` via `custom_provider_slug()`.
- **`_save_discovered_models_to_config` writeback**: Even if the UI handles dict-form models correctly, the post-probe writeback to config.yaml can still destroy your curated metadata. Set `discover_models: false` until you're on a version with PR #67878.
