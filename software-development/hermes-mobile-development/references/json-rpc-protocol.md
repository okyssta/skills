# Hermes TUI Gateway JSON-RPC Protocol

## WebSocket Endpoint
```
ws://<host>:9119/api/ws?token=<session_token>
```

## Message Format
Standard JSON-RPC 2.0. Requests include `jsonrpc`, `id`, `method`, `params`. Responses echo the `id`. Server-sent events use `jsonrpc`, `method: "event"`, `params: {type, payload, session_id}`.

## Complete Method Catalog

### Session Management
| Method | Params | Returns |
|--------|--------|---------|
| `session.create` | `{}` | `{session_id, stored_session_id, message_count, messages, info}` |
| `session.list` | `{limit?, offset?}` | `{sessions: [{id, title, created_at, model, message_count, status, preview}]}` |
| `session.resume` | `{session_id}` | Session history + messages |
| `session.history` | `{session_id}` | `{messages, session_id}` |
| `session.delete` | `{session_id}` | `{ok: true}` |
| `session.steer` | `{session_id, message}` | Streams events |
| `session.interrupt` | `{session_id}` | `{ok: true}` |
| `session.compress` | `{session_id}` | `{ok: true}` |
| `session.title` | `{session_id}` | `{title}` |
| `session.active_list` | `{}` | Active live sessions |
| `session.activate` | `{session_id}` | Switch active session |

### Chat
| Method | Params | Returns |
|--------|--------|---------|
| `prompt.submit` | `{message, session_id?}` | Streams events (delta, tool.start, etc.) |
| `prompt.background` | `{message, session_id?}` | Runs in background |

### Model & Config
| Method | Params | Returns |
|--------|--------|---------|
| `model.list` | `{}` | Available models |
| `config.get` | `{key?}` | Config |
| `config.set` | `{key, value}` | `{ok: true}` |
| `commands.catalog` | `{}` | List slash commands |
| `command.dispatch` | `{command: "/model claude"}` | Executes slash command |

### Interrupts
| Method | Params | Returns |
|--------|--------|---------|
| `clarify.respond` | `{id, response}` | Continues agent turn |
| `approval.respond` | `{id, approved: bool}` | `{ok: true}` |
| `sudo.respond` | `{id, password}` | `{ok: true}` |
| `secret.respond` | `{id, value}` | `{ok: true}` |

### Status
| Method | Params | Returns |
|--------|--------|---------|
| `status` | `{}` | Server status (version, gateway, sessions) |

### Subagent
| Method | Params | Returns |
|--------|--------|---------|
| `delegation.status` | `{}` | Active subagents |
| `subagent.interrupt` | `{id}` | Stop subagent |
| `process.stop` | `{id}` | Stop process |

## Complete Event Catalog

| Event | Payload Shape | Description |
|-------|--------------|-------------|
| `gateway.ready` | `{skin}` | Connection established, skin config |
| `session.info` | `{session_id, title, ..}` | Session metadata |
| `message.start` | `{session_id}` | Agent started generating |
| `message.delta` | `{content, session_id}` | Streaming text chunk |
| `message.complete` | `{session_id, usage?}` | Message done |
| `thinking.delta` | `{content}` | Thinking tokens |
| `reasoning.delta` | `{content}` | Reasoning tokens |
| `tool.start` | `{id, name, args}` | Tool started |
| `tool.progress` | `{name, status, id}` | Tool progress |
| `tool.complete` | `{id, name, result, summary?}` | Tool finished |
| `tool.generating` | — | Tool generating output |
| `clarify.request` | `{id, question, options?}` | Needs input |
| `approval.request` | `{id, command, message}` | Needs approval |
| `sudo.request` | `{id, command}` | Needs sudo |
| `secret.request` | `{id, key, prompt?}` | Needs secret |
| `background.complete` | `{result}` | Background task done |
| `error` | `{message}` | Error occurred |
| `skin.changed` | `{name, colors}` | Theme changed |

## WebSocket URL Construction

```typescript
function buildChatWsUrl(backendUrl: string, token: string, profile?: string): string {
  const base = backendUrl.replace(/\/+$/, '')
  const wsScheme = base.startsWith('https') ? 'wss:' : 'ws:'
  const host = base.replace(/^https?:\/\//, '')
  const params = { token }
  if (profile) params.profile = profile
  return `${wsScheme}//${host}/api/ws?${new URLSearchParams(params)}`
}
```

## Auth Endpoints

```
GET /api/status
→ { auth_required: bool, auth_providers: string[], version: string, gateway_running: bool }

POST /api/auth/login
Body: { username, password }
→ { token, token_type }
```
