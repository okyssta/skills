# Hermes WebSocket Auth Patch for Native Mobile Clients

## The Problem

When `hermes serve` binds to a non-loopback IP (`--host 0.0.0.0`), the auth gate engages and `/api/ws` **rejects** the `?token=` query parameter. Only `?internal=` and `?ticket=` are accepted in gated mode.

React Native's WebSocket API cannot set custom HTTP headers on the upgrade request (no `Authorization: Bearer` header). So `GatewayClient` sends `?token=<_SESSION_TOKEN>` as a query param, which gets a **403 Forbidden**.

## The Fix

Patch `_ws_auth_reason()` in `hermes_cli/web_server.py` to also accept `?token=` in gated mode.

### Location

```python
# File: /usr/local/lib/hermes-agent/hermes_cli/web_server.py
# Function: _ws_auth_reason() around line ~12735
```

### The Hunk

**Before (gated section, around line 12735):**
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

    token = ws.query_params.get("token", "")
```

**After:**
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

    token = ws.query_params.get("token", "")
```

### Key Changes

1. Changed `if not ticket: return "no_credential", "none"` to `if ticket:` (fall through to token check if no ticket)
2. Added `?token=` acceptance before the non-gated fallback

### Apply to the Right File

Hermes may be installed via git or pip. Find the correct file:

```bash
python3 -c "import hermes_cli.web_server; print(hermes_cli.web_server.__file__)"
```

### Restart After Patching

```bash
fuser -k 9119/tcp && sleep 2
HERMES_DASHBOARD_SESSION_TOKEN=your-token hermes serve --host 0.0.0.0 --port 9119 &
```

### Verification

```bash
# Install websocket-client first
pip install websocket-client -q

python3 -c "
import websocket
ws = websocket.create_connection(
    'ws://<host>:9119/api/ws?token=your-token', timeout=5)
print('WEBSOCKET CONNECTED!')
ws.send('{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"session.list\",\"params\":{}}')
print('Response:', ws.recv()[:300])
ws.close()
"
```

## Security Note

This patch re-enables the legacy `?token=` path in gated mode. Only use this for:
- Test/development servers
- Native mobile clients that cannot set WS headers
- Private networks (Tailscale, VPN)

For production, configure proper OAuth (Nous Portal) or username/password auth instead.
