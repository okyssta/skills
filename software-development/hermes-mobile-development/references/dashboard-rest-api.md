# Dashboard REST API for Mobile Clients

## Overview

The Hermes web dashboard exposes REST API endpoints for model management, analytics, and configuration. These can be consumed from a mobile app to build a feature-rich dashboard.

## Auth for REST Endpoints

### Non-Gated Mode (loopback / --insecure)
The `X-Hermes-Session-Token` header or legacy `Authorization: Bearer <token>` works directly:
```typescript
fetch('http://host:9119/api/model/options', {
  headers: { 'X-Hermes-Session-Token': 'your-token' }
})
```

### Gated Mode (default for --host 0.0.0.0)
In gated mode, `_require_token()` short-circuits to only check `request.state.session` (the OAuth cookie). Token headers are **ignored** unless you patch the function.

**Patch location:** `hermes_cli/web_server.py` → function `_require_token()` (line ~368)

**The fix:** Add a `_has_valid_session_token(request)` check before the 401:

```python
def _require_token(request: Request) -> None:
    if getattr(request.app.state, "auth_required", False):
        if getattr(request.state, "session", None) is not None:
            return
        # ← ADD THIS:
        if _has_valid_session_token(request):
            return
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not _has_valid_session_token(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
```

### Alternative: PUBLIC_API_PATHS
Add endpoints to the allowlist in `hermes_cli/dashboard_auth/public_paths.py` to bypass auth entirely. Only safe for read-only data:

```python
PUBLIC_API_PATHS: frozenset[str] = frozenset({
    # ... existing paths ...
    "/api/model/options",
    "/api/model/auxiliary",
    "/api/model/moa",
    "/api/analytics/models",
})
```

This file is re-read on every request (no restart needed in development).

## Key Endpoints

### Model Info (Public)
```
GET /api/model/info
→ { model: "deepseek-v4-flash", provider: "opencode-go",
    capabilities: { supports_tools: true, supports_vision: false,
                    supports_reasoning: true, context_window: 1000000 } }
```

### Model Options
```
GET /api/model/options
→ { providers: [{ slug: "opencode-go", name: "...", is_current: bool,
                  models: ["model1", "model2"] }] }
```

### Auxiliary Tasks
```
GET /api/model/auxiliary
→ { tasks: [{ task: "vision", provider: "opencode-go", model: "mimo-v2.5" },
            { task: "web_extract", provider: "openrouter", model: "..." }] }
```

### Mixture of Agents
```
GET /api/model/moa
→ { default_preset: "default", active_preset: "",
    presets: { default: { enabled: true,
      reference_models: [{ provider: "...", model: "..." }] } } }
```

### Model Analytics
```
GET /api/analytics/models?days=30
→ { models: [{ model: "deepseek-v4-flash", provider: "opencode-go",
               sessions: 102, input_tokens: 123456, output_tokens: 7890,
               last_used_at: 1783071337 }] }
```

### Set Model
```
POST /api/model/set  { "model": "new-model", "provider": "provider" }
```

## Data Flow for a Model Dashboard

```
┌────────────┐    GET /api/model/info       ┌──────────────┐
│  Mobile    │─────── public ──────────────→│  Hermes      │
│  App       │    GET /api/analytics/models │  Serve       │
│  (React    │─────── X-Hermes-Session-Token│  (FastAPI)   │
│   Native)  │    GET /api/model/options    │              │
│            │─────── (gated/patch) ───────→│              │
└────────────┘                              └──────────────┘
```

The mobile app should call these via `fetch()` with the session token. Batch requests with `Promise.all()` to avoid waterfall loading.
