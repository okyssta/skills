# Hermes TUI Gateway JSON-RPC Protocol Reference

> This is the protocol that `hermes --tui`, the desktop app, and the dashboard Chat tab all speak. Any custom client can speak it too — over WebSocket at `/api/ws`.

## Transport

- **WebSocket:** `ws://<host>:9119/api/ws?token=<session_token>`
- **Format:** Newline-delimited JSON (one JSON object per message, terminated by `\n`)
- **Spec:** JSON-RPC 2.0 (requests, notifications, responses, events)

## Authentication

All messages flow over a single authenticated WebSocket. The token is obtained via:

1. `POST /api/auth/login` (username/password) → `{token}`
2. Static token via `HERMES_DASHBOARD_SESSION_TOKEN` env var
3. OAuth browser flow

## Methods (Client → Server)

### prompt.submit

Send a message to the agent. The primary chat method.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "prompt.submit",
  "params": {
    "message": "What's the weather in London?",
    "session_id": "abc123",         // optional — creates new if omitted
    "files": ["path/to/image.png"], // optional — file attachments
    "model": "claude-sonnet-4"      // optional — per-message model override
  },
  "id": 1
}
```

**Response:** Streaming — multiple events follow (see Events below), then a final result.

### prompt.background

Submit a prompt to run in the background. Returns immediately with a task handle.

### session.steer

Inject a message mid-turn without waiting for the current turn to finish.

### session.create

Create a new chat session.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "session.create",
  "params": {},
  "id": 1
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "session_id": "20260708_123456_a1b2c3",
    "title": null,
    "created_at": "2026-07-08T12:00:00Z"
  }
}
```

### session.list

List recent sessions.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "session.list",
  "params": {
    "limit": 20,
    "offset": 0,
    "profile": "default"  // optional — filter by profile
  },
  "id": 1
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "sessions": [
      {
        "session_id": "20260708_123456_a1b2c3",
        "title": "API design discussion",
        "model": "claude-sonnet-4",
        "message_count": 12,
        "token_count": 4520,
        "created_at": "2026-07-08T12:00:00Z",
        "last_active": "2026-07-08T14:30:00Z",
        "status": "idle"  // idle | working | needs_you
      }
    ]
  }
}
```

### session.resume

Resume a session and load its history.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "session.resume",
  "params": {
    "session_id": "20260708_123456_a1b2c3"
  },
  "id": 1
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "session_id": "20260708_123456_a1b2c3",
    "title": "API design discussion",
    "history": [
      {"role": "user", "content": "Hello"},
      {"role": "assistant", "content": "Hi! How can I help?"}
    ]
  }
}
```

### session.history

Get the full transcript of a session.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "session.history",
  "params": {"session_id": "abc123"},
  "id": 1
}
```

### session.close

Close an active session (does not delete it).

### session.delete

Delete a session permanently.

### session.interrupt

Stop the current agent turn.

### session.compress

Compress the context window to reduce token usage.

### session.title

Generate or regenerate the session title from conversation content.

### session.status

Get current session state (active model, running tools, etc.).

### session.usage

Get token usage for a session.

### session.branch

Fork the session at a given point, creating a new branch.

### model.list

List available models.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "model.list",
  "params": {},
  "id": 1
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "models": [
      {"id": "claude-sonnet-4", "provider": "anthropic"},
      {"id": "gpt-5", "provider": "openai"}
    ],
    "current": "claude-sonnet-4"
  }
}
```

### command.dispatch

Execute a slash command.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "command.dispatch",
  "params": {"command": "/model claude-sonnet-4"},
  "id": 1
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "type": "send",          // send | notice | prefill
    "message": "/model claude-sonnet-4",
    "notice": "⊙ Model set to claude-sonnet-4"
  }
}
```

### commands.catalog

List all available slash commands.

### clarify.respond

Respond to a pending clarify prompt (the agent asked a question).

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "clarify.respond",
  "params": {
    "id": "clarify_1",
    "response": "Python 3.12"
  },
  "id": 1
}
```

### approval.respond

Approve or deny a dangerous command request.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "approval.respond",
  "params": {
    "id": "approval_1",
    "approved": true
  },
  "id": 1
}
```

### sudo.respond

Provide sudo/root password for a privileged command.

### secret.respond

Provide a secret/credential value the agent requested.

### config.get

Read configuration values.

### config.set

Set configuration values.

### cli.exec

Execute a CLI command directly (bypassing the agent).

### reload.mcp

Reload MCP server configurations.

### reload.env

Reload environment variables.

### process.stop

Stop a background process.

### delegation.status

List running subagents and their status.

### subagent.interrupt

Stop a specific subagent.

### status

Get comprehensive backend status (same as REST `/api/status`).

### terminal.resize

Resize a terminal session (only relevant for PTY).

## Events (Server → Client)

These are JSON-RPC **notifications** (no `id` field) pushed by the server during a `prompt.submit` call.

### message.delta

A text chunk of the assistant's streaming response.

```json
{
  "jsonrpc": "2.0",
  "method": "message.delta",
  "params": {
    "content": "The weather in London is currently 18°C",
    "session_id": "abc123",
    "done": false
  }
}
```

### message.complete

The assistant's message finished.

```json
{
  "jsonrpc": "2.0",
  "method": "message.complete",
  "params": {
    "session_id": "abc123",
    "usage": {
      "prompt_tokens": 150,
      "completion_tokens": 200,
      "total_tokens": 350
    }
  }
}
```

### tool.start

A tool call began.

```json
{
  "jsonrpc": "2.0",
  "method": "tool.start",
  "params": {
    "name": "web_search",
    "args": {"query": "London weather"},
    "id": "tool_1",
    "session_id": "abc123"
  }
}
```

### tool.progress

A tool call reported progress.

```json
{
  "jsonrpc": "2.0",
  "method": "tool.progress",
  "params": {
    "name": "web_search",
    "id": "tool_1",
    "status": "Fetching results..."
  }
}
```

### tool.complete

A tool call finished.

```json
{
  "jsonrpc": "2.0",
  "method": "tool.complete",
  "params": {
    "name": "web_search",
    "id": "tool_1",
    "result": "...",
    "duration_ms": 1234
  }
}
```

### approval.request

Backend needs user approval for a dangerous command.

```json
{
  "jsonrpc": "2.0",
  "method": "approval.request",
  "params": {
    "id": "approval_1",
    "command": "rm -rf /data/cache",
    "message": "This will delete all cached files. Proceed?",
    "session_id": "abc123"
  }
}
```

Respond with `approval.respond`.

### clarify.request

Backend needs clarification from the user.

```json
{
  "jsonrpc": "2.0",
  "method": "clarify.request",
  "params": {
    "id": "clarify_1",
    "question": "Which Python version should I use?",
    "options": ["3.11", "3.12", "3.13"],
    "session_id": "abc123"
  }
}
```

Respond with `clarify.respond`.

### sudo.request

Backend needs sudo credentials.

### secret.request

Backend needs a secret/credential value.

### gateway.ready

Backend initialized and ready for requests.

### error

An error occurred.

```json
{
  "jsonrpc": "2.0",
  "method": "error",
  "params": {
    "code": 500,
    "message": "Model API returned 401",
    "session_id": "abc123"
  }
}
```

## Complete Method Catalog

Below is the full list of methods the tui_gateway exposes. The desktop app and TUI use all of them; a custom client typically only needs a subset.

### Session Methods
- `session.create` — new empty session
- `session.list` — list recent sessions
- `session.active_list` — list currently-open sessions (process-local)
- `session.activate` — switch active session
- `session.resume` — load session history
- `session.close` — close active session
- `session.history` — get full transcript
- `session.delete` — delete permanently
- `session.title` — auto-generate title
- `session.usage` — get token usage
- `session.status` — get live state
- `session.compress` — compress context
- `session.branch` — fork at a point
- `session.interrupt` — stop current turn
- `session.steer` — inject mid-turn

### Prompt Methods
- `prompt.submit` — send message (primary)
- `prompt.background` — send to background

### Interrupt Response Methods
- `clarify.respond` — answer clarify prompt
- `sudo.respond` — provide sudo password
- `secret.respond` — provide secret value
- `approval.respond` — approve/deny command

### Command Methods
- `command.dispatch` — execute slash command
- `commands.catalog` — list slash commands

### Config Methods
- `config.get` — read config
- `config.set` — write config

### Model Methods
- `model.list` — list models
- `model.switch` — switch model

### Delegation Methods
- `delegation.status` — list subagents
- `subagent.interrupt` — stop subagent

### Utility Methods
- `status` — backend status
- `cli.exec` — execute CLI command
- `reload.mcp` — reload MCP servers
- `reload.env` — reload env vars
- `process.stop` — stop background process
- `spawn_tree.save/list/load` — save/restore agent spawns
- `terminal.resize` — resize terminal (PTY only)
- `clipboard.paste` — paste clipboard content
- `image.attach` — attach image file
