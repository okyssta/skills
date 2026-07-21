# OpenCode Free Models Reference (2026-06-30)

Source: `https://models.dev/api.json` → `opencode` provider → filtered by `cost.input=0` AND `cost.output=0`

## Free Models on OpenCode Provider

| Model | Context | Reasoning | Tools | Vision | Best For |
|-------|---------|-----------|-------|--------|----------|
| **north-mini-code-free** ⭐ | 256K | ✅ | ✅ | ❌ | **Code-focused, bug fixing** |
| **mimo-v2-pro-free** | 1M | ✅ | ✅ | ✅ | General purpose + vision |
| **nemotron-3-ultra-free** | 1M | ✅ | ✅ | ❌ | Large context reasoning |
| **ring-2.6-1t-free** | 262K | ✅ | ✅ | ❌ | General reasoning |
| **kimi-k2.5-free** | 262K | ✅ | ✅ | ✅ | Multimodal |
| **minimax-m3-free** | 204K | ✅ | ✅ | ❌ | General |
| **deepseek-v4-flash-free** | 200K | ✅ | ✅ | ❌ | Fast inference |
| **grok-code** | 256K | ✅ | ✅ | ✅ | Coding + vision |
| **glm-4.7-free** | 204K | ✅ | ✅ | ❌ | Chinese/English |
| **qwen3.6-plus-free** | 262K | ✅ | ✅ | ✅ | Multilingual + vision |
| **minimax-m3-free** | 204K | ✅ | ✅ | ❌ | Chinese/English |
| **deepseek-v4-flash-free** | 200K | ✅ | ✅ | ❌ | Fast inference |
| **minimax-m2.5-free** | 204K | ✅ | ✅ | ❌ | General |
| **minimax-m2.1-free** | 204K | ✅ | ✅ | ❌ | General |
| **mimo-v2-flash-free** | 262K | ✅ | ✅ | ❌ | Fast inference |
| **trinity-large-preview-free** | 131K | ❌ | ✅ | ❌ | Basic tasks |
| **big-pickle** | 200K | ✅ | ✅ | ❌ | General |
| **qwen3.6-plus-free** | 262K | ✅ | ✅ | ✅ | Multilingual + vision |
| **mimo-v2-omni-free** | 262K | ✅ | ✅ | ✅ | Multimodal |
| **glm-5-free** | 204K | ✅ | ✅ | ❌ | General |
| **nemotron-3-super-free** | 204K | ✅ | ✅ | ❌ | Reasoning |
| **ling-2.6-flash-free** | 262K | ❌ | ✅ | ❌ | Fast inference |

## Model Selection Guidelines

### For Automated Bug Fixing (AUTO-FIX-BUGS)
**Best: `north-mini-code-free`**
- Specifically trained for code tasks ("code" in name)
- 256K context (sufficient for large files + repo context)
- Reasoning enabled (can think through complex bugs)
- Tools enabled (can run terminal, search, edit files)
- Vision not needed for text-based bug fixing
- $0 cost - completely free

### For Vision + Code Tasks
**Best: `mimo-v2-pro-free` or `grok-code`**
- Both have vision + tools + reasoning
- `mimo-v2-pro-free`: 1M context, free
- `grok-code`: 256K context, free

### For Maximum Context (Free)
**Best: `mimo-v2-pro-free` (1M) or `nemotron-3-ultra-free` (1M)**
- Both have 1M+ context windows
- Both have reasoning + tools

### Provider Selection
- **Use `opencode` provider** with free models (not `opencode-go`)
- `opencode-go` requires paid models like `mimo-v2.5`
- `opencode` provider has 71 models total, 20+ free

## How to Query Free Models Programmatically

```python
import requests

resp = requests.get('https://models.dev/api.json', timeout=15)
data = resp.json()
opencode = data.get('opencode', {})
models = opencode.get('models', {})

free_models = []
for mid, mdata in models.items():
    cost = mdata.get('cost', {})
    inp = cost.get('input', 0) if isinstance(cost, dict) else 0
    out = cost.get('output', 0) if isinstance(cost, dict) else 0
    if inp == 0 and out == 0:
        limit = mdata.get('limit', {})
        ctx = limit.get('context', 0) if isinstance(limit, dict) else 0
        reasoning = mdata.get('reasoning', False)
        tool = mdata.get('tool_call', False)
        attachment = mdata.get('attachment', False)
        free_models.append({
            'id': mid,
            'context': ctx,
            'reasoning': reasoning,
            'tools': tool,
            'vision': attachment
        })
```

## Usage in Cron Jobs

When creating cron jobs with free OpenCode models:

```python
cronjob("create", {
    "name": "AUTO-FIX-BUGS",
    "schedule": "every 90 minutes",
    "prompt": "Automated bug-fixer for NousResearch/hermes-agent...",
    "provider": "opencode",
    "model": "north-mini-code-free",  # Free, code-specialized
    "toolsets": ["terminal", "file", "search"],
    "deliver": "origin"
})
```

## Notes

- Models.dev data is cached by Hermes (1 hour TTL)
- Use `PROVIDER_TO_MODELS_DEV` mapping: `opencode` → `opencode`
- Free models may have rate limits or availability changes
- Always test model availability before scheduling production jobs