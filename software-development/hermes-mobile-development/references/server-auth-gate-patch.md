# Server Auth Gate Patch for Mobile WebSocket Connections

## Problem
React Native WebSocket cannot set custom HTTP headers (`Authorization`, `X-Hermes-Session-Token`). The only way to pass auth credentials is via URL query parameters (`ws://host/api/ws?token=...`).

By default, `hermes serve` in **gated mode** (non-loopback bind without `--insecure`) rejects `?token=` for WebSocket upgrades. Only `?ticket=` (single-use browser ticket) and `?internal=` (process-lifetime credential) are accepted.

## The WS Patch

**File:** `hermes_cli/web_server.py`  
**Function:** `_ws_auth_reason()` (line ~12700 in the original, varies by version)

### Before (gated section, inside `if auth_required:`):
```python
        ticket = ws.query_params.get("ticket", "")
        if not ticket:
            return "no_credential", "none"

        try:
            consume_ticket(ticket)
            return None, "ticket"
        except TicketInvalid as exc:
            audit_log(
                AuditEvent.WS_TICKET_REJECTED,
                reason=str(exc),
                ip=(ws.client.host if ws.client else ""),
                path=ws.url.path,
            )
            return "ticket_invalid", "ticket"
```

### After:
```python
        ticket = ws.query_params.get("ticket", "")
        if ticket:
            try:
                consume_ticket(ticket)
                return None, "ticket"
            except TicketInvalid as exc:
                audit_log(
                    AuditEvent.WS_TICKET_REJECTED,
                    reason=str(exc),
                    ip=(ws.client.host if ws.client else ""),
                    path=ws.url.path,
                )
                return "ticket_invalid", "ticket"

        # Mobile app support: accept ?token=<_SESSION_TOKEN> for native
        # clients that cannot set custom WebSocket headers (React Native).
        token = ws.query_params.get("token", "")
        if token:
            if hmac.compare_digest(token.encode(), _SESSION_TOKEN.encode()):
                return None, "token"
            audit_log(
                AuditEvent.WS_TICKET_REJECTED,
                reason="token_mismatch",
                ip=(ws.client.host if ws.client else ""),
                path=ws.url.path,
            )
            return "token_mismatch", "token"
```

## REST API Auth Patch

The same `_require_token()` function in `web_server.py` (line ~368) also needs patching for REST endpoint access in gated mode. Without it, `X-Hermes-Session-Token` and `Authorization: Bearer` are silently ignored and all non-public endpoints return 401.

**Function:** `_require_token()` (line ~368)

### Before:
```python
def _require_token(request: Request) -> None:
    if getattr(request.app.state, "auth_required", False):
        if getattr(request.state, "session", None) is not None:
            return
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not _has_valid_session_token(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
```

### After:
```python
def _require_token(request: Request) -> None:
    if getattr(request.app.state, "auth_required", False):
        # Gate is authoritative — check OAuth session first
        if getattr(request.state, "session", None) is not None:
            return
        # Mobile app support: also accept session token header
        if _has_valid_session_token(request):
            return
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not _has_valid_session_token(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
```

## Alternative: PUBLIC_API_PATHS

Add endpoints to `hermes_cli/dashboard_auth/public_paths.py` to bypass auth entirely:

```python
PUBLIC_API_PATHS: frozenset[str] = frozenset({
    # ... existing paths ...
    "/api/model/options",
    "/api/model/auxiliary",
    "/api/model/moa",
    "/api/analytics/models",
})
```

Changes to this file take effect immediately (no server restart needed).

## Applying the Patch

1. Find the installed `web_server.py`:
   ```bash
   python3 -c "import hermes_cli.web_server; print(hermes_cli.web_server.__file__)"
   ```

2. Edit both `_ws_auth_reason()` and `_require_token()` — the exact line numbers differ between versions

3. Find and edit `public_paths.py` (same directory, `dashboard_auth/public_paths.py`)

4. Clear Python cache to force reload:
   ```bash
   find /usr/local/lib/hermes-agent -name "__pycache__" -path "*web_server*" -exec rm -rf {} +
   find /usr/local/lib/hermes-agent -name "web_server*.pyc" -delete
   find /usr/local/lib/hermes-agent -name "__pycache__" -path "*dashboard_auth*" -exec rm -rf {} +
   ```

5. Restart the server:
   ```bash
   fuser -k 9119/tcp
   HERMES_DASHBOARD_SESSION_TOKEN=your-token hermes serve --host 0.0.0.0 --port 9119
   ```

## Verification

### Test WS
```python
import websocket
ws = websocket.create_connection(
    'ws://localhost:9119/api/ws?token=your-token',
    timeout=5
)
print('WS CONNECTED')
ws.close()
```

### Test REST
```bash
curl -s -H "X-Hermes-Session-Token: your-token" \
  http://localhost:9119/api/analytics/models | head
```

## Notes
- The `auth_providers` field in `/api/status` (showing `['nous']` etc.) is unrelated to WS token auth — it reflects configured auth plugins for the web UI login flow
- The `HERMES_DASHBOARD_SESSION_TOKEN` env var must be set before starting the server
- Without the env var, the server generates a random token each start (via `secrets.token_urlsafe(32)`)
- Reading config and retrieving model options/auxiliary tasks does NOT change server state — making them public is low risk for dev deployments
