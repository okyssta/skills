# Hermes Gateway WebSocket Auth Mechanism

Deep dive on how `hermes serve` authenticates WebSocket upgrades, extracted from `hermes_cli/web_server.py`.

## Auth Decision Flow

```
_ws_auth_reason(ws)
  │
  ├─ Auth required? (app.state.auth_required)
  │    │
  │    ├─ YES (gated mode — public bind, no --insecure)
  │    │    │
  │    │    ├─ ?internal=...  → consume_internal_credential()  [server-spawned children]
  │    │    ├─ ?token=...     → PATCHED: hmac.compare_digest() [desktop/mobile clients]
  │    │    ├─ ?ticket=...    → consume_ticket()               [browser SPA, single-use, 30s TTL]
  │    │    └─ nothing        → "no_credential" → 403
  │    │
  │    └─ NO (loopback/insecure mode)
  │         │
  │         └─ ?token=...  → hmac.compare_digest(token, _SESSION_TOKEN)
  │
  └─ Result: (None, credential_type) = accept, (reason, credential_type) = reject
```

## Credential Types

| Param | Source | Use Case | Multi-use? | TTL |
|-------|--------|----------|------------|-----|
| `?ticket=` | `POST /api/auth/ws-ticket` | Browser SPA connecting to `/api/ws` | No (single shot) | 30s |
| `?internal=` | Server env `HERMES_DESKTOP_INTERNAL_TOKEN` | PTY child → `/api/ws` | Yes | Process lifetime |
| `?token=` | Server env `HERMES_DASHBOARD_SESSION_TOKEN` | Legacy/patched — desktop/mobile clients | Yes | Process lifetime |
| `Authorization: Bearer` | Header | REST API calls | Yes | Process lifetime |

## The Gated Mode Issue

When `hermes serve` binds to `0.0.0.0` (public), `app.state.auth_required` becomes `True`. In this mode, the `?token=` query param is **explicitly rejected** for WebSocket upgrades (code comment in `_ws_auth_reason()`: "The legacy `?token=` path is unconditionally rejected in gated mode").

**This breaks native mobile and desktop clients** because:
- React Native WebSocket API cannot set custom headers (`Authorization: Bearer`)
- Query params are the only auth transport for RN WebSocket
- The browser SPA ticket flow (`POST /api/auth/ws-ticket` then `?ticket=`) requires cookie-based session auth, which mobile apps don't have
- Desktop apps are simplest with `?token=` and no login form

## The Patch (Tested and Verified)

In `hermes_cli/web_server.py` → `_ws_auth_reason()`, add token check **inside** the `if auth_required:` block, before the ticket check:

```python
    # in hermes_cli/web_server.py, around line 15270
    
    if auth_required:
        from hermes_cli.dashboard_auth.audit import AuditEvent, audit_log
        from hermes_cli.dashboard_auth.ws_tickets import (
            TicketInvalid,
            consume_internal_credential,
            consume_ticket,
        )

        internal = ws.query_params.get("internal", "")
        if internal:
            try:
                consume_internal_credential(internal)
                return None, "internal"
            except TicketInvalid as exc:
                audit_log(...)
                return "internal_invalid", "internal"

        # ── ADD THIS BLOCK ──
        # Desktop/mobile clients: accept ?token=<SESSION_TOKEN> in gated mode
        token = ws.query_params.get("token", "")
        if token and hmac.compare_digest(token.encode(), _SESSION_TOKEN.encode()):
            return None, "token"

        ticket = ws.query_params.get("ticket", "")
        if not ticket:
            return "no_credential", "none"
        ...
```

The token value comes from `HERMES_DASHBOARD_SESSION_TOKEN` in `~/.hermes/.env`.

## Finding the Right File to Patch

⚠️ **CRITICAL PITFALL**: Hermes may have multiple copies. The running code is at the **installed** location, NOT a dev checkout:

```bash
# Confirm which file is actually loaded:
python3 -c "import hermes_cli.web_server; print(hermes_cli.web_server.__file__)"

# Typical result (installed copy):
# → /usr/local/lib/hermes-agent/hermes_cli/web_server.py

# NOT this (dev checkout):
# → /root/hermes-agent/hermes_cli/web_server.py
```

Always patch the file returned by `__file__`. Patching a dev copy does nothing.

## Verifying the Patch

```python
import asyncio, json
from websockets.asyncio.client import connect

async def test():
    async with connect('ws://127.0.0.1:9119/api/ws?token=test-token-hermes-mobile-2026') as ws:
        ready = await asyncio.wait_for(ws.recv(), timeout=5)
        data = json.loads(ready)
        assert data.get('method') == 'event' and data.get('params', {}).get('type') == 'gateway.ready'
        print('WS auth OK — gateway.ready received')

asyncio.run(test())
```

Expected: `WS auth OK — gateway.ready received`
Failure: `websockets.exceptions.InvalidStatus: HTTP 403` → patch not in the right file.

## Restarting After Patch

```bash
# Kill the running hermes dashboard process
fuser -k 9119/tcp

# Start fresh
hermes dashboard --host 0.0.0.0 --port 9119 --skip-build --no-open
```

Note: the main `hermes gateway` process may auto-restart the dashboard. If so, kill the main gateway too and let it re-spawn, or run `hermes dashboard` separately.
