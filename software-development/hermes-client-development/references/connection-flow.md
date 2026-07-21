# Hermes Connection Flow

> How a custom client connects to `hermes serve` — from first touch to live chat.

## Sequence

```
┌──────────┐          ┌──────────────────┐
│  Client  │          │  hermes serve    │
│  (phone) │          │  (remote host)   │
└────┬─────┘          └────────┬─────────┘
     │                         │
     │  1. GET /api/status     │
     │────────────────────────►│
     │◄────────────────────────│
     │  { auth_required: true, │
     │    auth_providers:      │
     │      ["basic"],         │
     │    agent_version:       │
     │      "0.18.2",          │
     │    gateway_running:true,│
     │    active_sessions: 2 } │
     │                         │
     │  ── [Detect "basic"     │
     │      provider, show     │
     │      login form]        │
     │                         │
     │  2. POST /api/auth/login│
     │     {username, password}│
     │────────────────────────►│
     │◄────────────────────────│
     │  { token: "eyJ...",     │
     │    token_type: "bearer"}│
     │                         │
     │  ── [Store token in     │
     │      secure storage]    │
     │                         │
     │  3. WebSocket connect   │
     │     ws://host:9119/     │
     │     api/ws?token=eyJ... │
     │────────────────────────►│
     │◄────────────────────────│
     │  { jsonrpc: "2.0",      │
     │    method: "gateway.    │
     │    ready",              │
     │    params: {} }         │
     │                         │
     │  4. session.create      │
     │────────────────────────►│
     │◄────────────────────────│
     │  { session_id: "...",   │
     │    title: null }        │
     │                         │
     │  5. prompt.submit       │
     │────────────────────────►│
     │◄─ message.delta (stream)│
     │◄─ tool.start            │
     │◄─ tool.complete         │
     │◄─ message.complete      │
     │◄─ { result, id }        │
```

## Endpoint Reference

### GET /api/status

**Response:**
```json
{
  "agent_version": "0.18.2",
  "auth_required": true,
  "auth_providers": ["basic", "oauth"],
  "auth_methods": {
    "basic": {"has_username": true},
    "oauth": {"provider": "nous"}
  },
  "gateway_running": true,
  "active_sessions": 2,
  "profiles": ["default", "worker"]
}
```

**Auth provider meanings:**
- `["basic"]` — username/password login form
- `["oauth"]` — OAuth browser flow (Nous Portal or custom OIDC)
- `["basic", "oauth"]` — both available, client picks
- `[]` — no auth required (loopback/localhost only)

### POST /api/auth/login

**Request:**
```json
{"username": "admin", "password": "strong-password"}
```

**Response (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Response (401):**
```json
{"detail": "Invalid credentials"}
```

### WS /api/ws

**Connection:** `ws://<host>:9119/api/ws?token=<session_token>`

After connecting, the server sends `gateway.ready` event. Then send JSON-RPC requests.

**Optional profile targeting:** `ws://<host>:9119/api/ws?token=<token>&profile=worker`

### WS /api/pty (NOT for custom clients)

Used by the dashboard's xterm.js terminal tab. Spawns `hermes --tui` as a child process behind a POSIX pseudo-terminal. Not suitable for standard chat clients — use `/api/ws` instead.

## Env Vars Reference

### On the Backend (hermes serve)

| Variable | Purpose | Required? |
|----------|---------|-----------|
| `API_SERVER_ENABLED=true` | Enable OpenAI-compatible HTTP on port 8642 | No |
| `API_SERVER_KEY=...` | Bearer token for HTTP API | If `API_SERVER_ENABLED` |
| `API_SERVER_PORT=8642` | Custom port for HTTP API | No |
| `HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin` | Username for auth gate | For basic auth |
| `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=...` | Password for auth gate | For basic auth |
| `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD_HASH=...` | scrypt hash instead of plaintext | Alternative |
| `HERMES_DASHBOARD_BASIC_AUTH_SECRET=...` | Stable signing secret (keeps sessions across restarts) | Recommended |
| `HERMES_DASHBOARD_SESSION_TOKEN=...` | Static bearer token (no login needed) | Alternative to OAuth/basic |

## CORS

The server restricts CORS to localhost origins only:
- `http://localhost:9119` / `http://127.0.0.1:9119`
- `http://localhost:3000` / `http://127.0.0.1:3000`
- `http://localhost:5173` / `http://127.0.0.1:5173` (Vite dev server)

Custom ports are added automatically. For mobile, **CORS does not apply to WebSocket** — the WS `Origin` header check allows `null` origin (what Electron file:// pages send) and loopback origins.

## Security Notes

1. **Never expose a basic-auth backend to the public internet.** Use OAuth (Nous Portal) or put it behind Tailscale/WireGuard.
2. **Bind to a tailscale IP** (`--host 100.x.x.x`) for trusted network access.
3. **Always set `HERMES_DASHBOARD_BASIC_AUTH_SECRET`** to a stable random value — otherwise all sessions expire on every restart.
4. **Token storage on the client must be encrypted** (iOS Keychain, Android Keystore, expo-secure-store).
5. **Rate limiting** is built in — the auth gate rate-limits login attempts.
