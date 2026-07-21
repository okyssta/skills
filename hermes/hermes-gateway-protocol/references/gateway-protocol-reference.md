# Gateway Protocol — Full Method & Event Reference

> Source: `tui_gateway/server.py` in hermes-agent source.
> This is a condensed reference for building custom clients. For the canonical list, read `tui_gateway/server.py` directly.

## Methods (Client → Server)

### Session Management
```
session.create({}) → {session_id, title, created_at}
session.list({limit?: int, offset?: int}) → {sessions: SessionInfo[]}
session.resume({session_id}) → {history: Message[], session_id, title}
session.delete({session_id}) → {ok: true}
session.history({session_id, limit?: int}) → {messages: Message[]}
session.title({session_id}) → {title: string}
session.active_list({}) → {sessions: ActiveSession[]}
session.activate({session_id}) → {ok: true}
session.close({session_id}) → {ok: true}
session.branch({session_id}) → {session_id: string}
session.status({session_id}) → {status, model, usage, ...}
session.usage({session_id}) → {prompt_tokens, completion_tokens, total_tokens}
session.steer({session_id, message})  → streams events
session.interrupt({session_id}) → {ok: true}
session.compress({session_id}) → {ok: true}
```

### Chat
```
prompt.submit({message, session_id?, images?, files?}) → streams events
prompt.background({message, session_id?}) → ← no direct response (events fire later)
```

### Commands & Config
```
command.dispatch({command: "/model claude-sonnet-4", session_id?}) → streams events
commands.catalog({}) → {commands: CommandDef[]}
config.get({key?: string}) → {config: any}
config.set({key, value, session_id?}) → {ok: true}
```

### Interrupt Responses
```
clarify.respond({id, response, session_id?}) → continues agent turn
approval.respond({id, approved: bool, session_id?}) → {ok: true}
sudo.respond({id, password, session_id?}) → {ok: true}
secret.respond({id, value, session_id?}) → {ok: true}
```

### System
```
status({}) → {agent_version, auth_required, auth_providers, ...}
model.list({}) → {models: ModelInfo[]}
cli.exec({command}) → {output: string}
reload.mcp({}) → {ok: true}
reload.env({}) → {ok: true}
process.stop({}) → {ok: true}
```

### Delegation / Multi-Agent
```
delegation.status({}) → {agents: SubAgentInfo[]}
subagent.interrupt({id}) → {ok: true}
spawn_tree.save({}) → {id: string}
spawn_tree.list({}) → {trees: SpawnTree[]}
spawn_tree.load({id}) → {tree: SpawnTree}
```

### Terminal (PTY)
```
terminal.resize({cols: int, rows: int}) → {ok: true}
clipboard.paste({}) → {text: string}
image.attach({path: string}) → {ok: true}
```

## Events (Server → Client, no `id` field)

All events have shape: `{"jsonrpc": "2.0", "method": "event", "params": {"type": "...", "payload": {...}, "session_id": "..."}}`

### Chat Lifecycle
```
message.start  → {session_id}
message.delta  → {content: string, session_id}
message.complete → {session_id, usage?: {prompt_tokens, completion_tokens, total_tokens}}
thinking.delta → {content: string, session_id}
reasoning.delta → {content: string, session_id}
```

### Tool Execution
```
tool.start     → {id: string, name: string, args: object, session_id}
tool.progress  → {id: string, name: string, status: string, session_id}
tool.complete  → {id: string, name: string, result: string, summary?: string, session_id}
tool.generating → {id: string, name: string, session_id}
```

### Interrupts (human-in-the-loop)
```
clarify.request  → {id: string, question: string, options?: string[], session_id}
approval.request → {id: string, command: string, message?: string, session_id}
sudo.request     → {id: string, command: string, session_id}
secret.request   → {id: string, key: string, prompt?: string, session_id}
```

### Session & System
```
gateway.ready    → {}
session.info     → {session_id, status: string, ...}
status.update    → {session_id, status: string}
background.complete → {session_id}
error            → {message: string, code?: int, session_id?}
skin.changed     → {skin: string, session_id}
```

## SessionInfo Shape
```
{
  id: string
  title?: string
  created_at: string (ISO 8601)
  updated_at?: string
  model?: string
  message_count?: int
  token_count?: int
  profile?: string
  status?: 'idle' | 'working' | 'needs_you'
  preview?: string
}
```

## Message Shape (from `session.history`)
```
{
  role: 'user' | 'assistant' | 'system' | 'tool'
  content: string
  timestamp?: string
  tool_calls?: [{id, name, args, result?}]
}
```

## REST Endpoints

### GET /api/status
Returns `ServerStatus`:
```json
{
  "agent_version": "0.18.2",
  "auth_required": true,
  "auth_providers": ["basic"],
  "gateway_running": true,
  "active_sessions": 2,
  "auth_methods": {
    "basic": {"has_username": true}
  }
}
```

### POST /api/auth/login
Request: `{"username": "...", "password": "..."}` → `{"token": "eyJ...", "token_type": "bearer"}`

### GET /health
Returns `{"status": "ok"}`

## WebSocket URL Construction

```
ws://<host>:<port>/api/ws?token=<session_token>[&profile=<profile_name>]
wss://<host>:<port>/api/ws?token=<session_token>[&profile=<profile_name>]
```

The `@hermes/shared` package provides `buildHermesWebSocketUrl()` and `buildChatWsUrl()` helpers.

## Auth Providers (Server-side config)

| Provider | Config | When to use |
|----------|--------|-------------|
| **basic** | `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` + `_PASSWORD` in `.env` | Trusted networks, Tailscale |
| **oauth** | `hermes dashboard register` → OAuth client | Public internet, VPS |
| **token** | `HERMES_DASHBOARD_SESSION_TOKEN` in `.env` | Programmatic / static clients |

## Key Env Vars for Remote Access

```
# Required for the backend:
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=<strong-password>
HERMES_DASHBOARD_BASIC_AUTH_SECRET=<stable-random>   # prevents logout on restart

# Optional static token:
HERMES_DASHBOARD_SESSION_TOKEN=my-token
```

## Source Files in Hermes Repo

| File | Purpose |
|------|---------|
| `tui_gateway/server.py` | Method handler implementation + event definitions |
| `tui_gateway/ws.py` | WebSocket transport (mounts at /api/ws) |
| `tui_gateway/transport.py` | Transport abstraction (stdio, WS) |
| `apps/shared/src/json-rpc-gateway.ts` | Reference TypeScript client (desktop + dashboard) |
| `apps/shared/src/websocket-url.ts` | URL construction helpers |
| `hermes_cli/web_server.py` | FastAPI server + route mounting (health, status, auth, WS, PTY) |
| `gateway/platforms/api_server.py` | OpenAI-compatible HTTP API (port 8642) |
