# Hermes Gateway JSON-RPC Protocol Reference

Full method and event catalog for the tui_gateway protocol served by `hermes serve` at `/api/ws`.

## Methods (Client → Server)

### Chat

| Method | Params | Returns | Description |
|--------|--------|---------|-------------|
| `prompt.submit` | `{message, session_id?, model?}` | Stream of events | Send a message. Returns `message.start`, `message.delta`, `message.complete`, and tool events |
| `prompt.background` | `{message, session_id?}` | Stream of events | Run in background, results delivered via `background.complete` |
| `session.steer` | `{session_id, message}` | Stream of events | Inject a message mid-turn without interrupting |

### Sessions

| Method | Params | Returns | Description |
|--------|--------|---------|-------------|
| `session.create` | `{}` | `{session_id, title?, created_at}` | Create a new session |
| `session.list` | `{limit?, offset?}` | `{sessions: [...]}` | List saved sessions |
| `session.active_list` | `{}` | `{sessions: [{id, title, status}]}` | List currently-active sessions |
| `session.activate` | `{session_id}` | `{ok: true}` | Switch active session |
| `session.close` | `{session_id}` | `{ok: true}` | Close an active session |
| `session.resume` | `{session_id}` | `{history: [{role, content}], session_id}` | Load a session's full transcript |
| `session.delete` | `{session_id}` | `{ok: true}` | Delete a session |
| `session.history` | `{session_id}` | `{messages: [...]}` | Get full message history |
| `session.title` | `{session_id, title?}` | `{title}` | Get or set session title |
| `session.usage` | `{session_id}` | `{tokens, cost}` | Token/cost breakdown |
| `session.status` | `{session_id}` | `{status, model, message_count}` | Session status info |
| `session.compress` | `{session_id}` | `{ok: true}` | Compress context window |
| `session.branch` | `{session_id}` | `{session_id: new_id}` | Fork the session |
| `session.interrupt` | `{session_id}` | `{ok: true}` | Stop current agent turn |

### Models & Config

| Method | Params | Returns | Description |
|--------|--------|---------|-------------|
| `model.list` | `{}` | `{models: [...]}` | Available models |
| `model.switch` | `{model, provider?}` | `{ok: true}` | Switch default model |
| `config.get` | `{key?}` | `{config}` | Read config (section or all) |
| `config.set` | `{key, value}` | `{ok: true}` | Write a config value |
| `commands.catalog` | `{}` | `{commands: [...]}` | List available slash commands |
| `command.resolve` | `{command}` | `{type, ...}` | Resolve a slash command string |
| `command.dispatch` | `{command}` | Stream of events or result | Execute a slash command |

### Interrupts (Human-in-the-Loop)

| Method | Params | Returns | Description |
|--------|--------|---------|-------------|
| `clarify.respond` | `{id, response}` | Continues agent turn | Answer an agent clarification |
| `approval.respond` | `{id, approved}` | `{ok: true}` | Approve or deny dangerous command |
| `sudo.respond` | `{id, password}` | `{ok: true}` | Provide sudo password |
| `secret.respond` | `{id, value}` | `{ok: true}` | Provide a secret/credential |

### Utility

| Method | Params | Returns | Description |
|--------|--------|---------|-------------|
| `cli.exec` | `{command}` | `{output, exit_code}` | Run a CLI command on the backend |
| `reload.mcp` | `{}` | `{ok: true}` | Reload MCP servers |
| `reload.env` | `{}` | `{ok: true}` | Reload .env variables |
| `process.stop` | `{pid}` | `{ok: true}` | Stop a background process |
| `delegation.status` | `{}` | `{agents: [...]}` | List active subagents |
| `subagent.interrupt` | `{id}` | `{ok: true}` | Stop a subagent |
| `terminal.resize` | `{cols, rows}` | `{ok: true}` | Resize PTY (for terminal clients) |
| `clipboard.paste` | `{}` | `{text}` | Read clipboard content |
| `image.attach` | `{image}` | `{ok: true}` | Attach an image to the session |
| `spawn_tree.save` | `{name}` | `{ok: true}` | Save subagent tree config |
| `spawn_tree.load` | `{name}` | `{spawn_tree}` | Load subagent tree config |
| `spawn_tree.list` | `{}` | `{spawn_trees: [...]}` | List saved spawn tree configs |

## Events (Server → Client)

Streamed as `{"jsonrpc": "2.0", "method": "event", "params": {"type": "event.name", "payload": {...}, "session_id": "..."}}`

### Chat Events

| Event | Payload | Description |
|-------|---------|-------------|
| `message.start` | `{session_id}` | Agent started generating a response |
| `message.delta` | `{content, session_id}` | Streaming text chunk — accumulate for display |
| `message.complete` | `{session_id, usage?}` | Response finished, usage info available |
| `thinking.delta` | `{content, session_id}` | Thinking/reasoning token stream |
| `reasoning.delta` | `{content}` | Reasoning chain chunk |
| `reasoning.available` | `{full_reasoning}` | Full reasoning text available |

### Tool Events

| Event | Payload | Description |
|-------|---------|-------------|
| `tool.start` | `{id, name, args}` | Tool execution started |
| `tool.progress` | `{id, name, status}` | Progress update during tool run |
| `tool.complete` | `{id, name, result, summary?}` | Tool finished |
| `tool.generating` | `{id, name}` | Tool generating output (long-running) |

### Interrupt Events

| Event | Payload | Description |
|-------|---------|-------------|
| `clarify.request` | `{id, question, options?}` | Agent needs clarification |
| `approval.request` | `{id, command, message}` | Dangerous command needs approval |
| `sudo.request` | `{id, command}` | Sudo access required |
| `secret.request` | `{id, key, prompt?}` | Secret/credential needed |

### Session Events

| Event | Payload | Description |
|-------|---------|-------------|
| `session.info` | `{session_id, title?, status}` | Session state changed |
| `gateway.ready` | `{}` | Backend is ready for requests |
| `status.update` | `{status, message?}` | Generic status update |
| `background.complete` | `{session_id, result}` | Background task finished |
| `error` | `{code, message, session_id?}` | An error occurred |
| `skin.changed` | `{skin}` | TUI skin changed (terminal clients) |

## REST Endpoints

These are HTTP endpoints served alongside the WebSocket.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/status` | GET | Server info, auth state, gateway status |
| `/api/auth/login` | POST | Username/password → token |
| `/api/sessions` | GET | List sessions (REST alternative) |
| `/api/sessions/{id}` | DELETE | Delete session |
| `/api/config/raw` | GET | Raw config.yaml |
| `/api/health` | GET | Health check (`{"status": "ok"}`) |

## Auth Response

```json
POST /api/auth/login
{"username": "admin", "password": "strong-password"}
→ {"token": "eyJ...", "token_type": "bearer"}
```

## OpenAI-Compatible API Server (Alternative)

The gateway can also serve an OpenAI-compatible HTTP API on port 8642 when `API_SERVER_ENABLED=true` is set in the backend's `.env`.

| Endpoint | Purpose |
|----------|---------|
| `POST /v1/chat/completions` | Standard OpenAI chat (streaming SSE) |
| `POST /v1/responses` | Stateful responses API |
| `POST /v1/runs` | Start a long-running run |
| `GET /v1/runs/{id}/events` | SSE stream of lifecycle events |
| `GET /v1/models` | List models |
| `GET /health` | Health check |

This is useful for language-agnostic clients and existing OpenAI-compatible frontends, but lacks the real-time tool events and interrupt handling of the WebSocket protocol.
