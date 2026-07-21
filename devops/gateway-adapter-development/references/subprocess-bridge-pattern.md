# Subprocess Bridge Pattern for Gateway Adapters

Some platforms (WhatsApp, Minecraft) require a native-process bridge — the protocol
library only exists in Node.js (Mineflayer, Baileys) and can't run in the Python
gateway process. The solution: Python adapter spawns a Node.js subprocess that
runs a tiny HTTP server, and the two communicate over localhost HTTP.

## Architecture

```
Hermes Gateway (Python)
  ┌──────────────────────────────────────┐
  │  YourPlatformAdapter                  │
  │  (BasePlatformAdapter)                │
  │                                       │
  │  connect():                            │
  │    1. Find node executable            │
  │    2. npm install in bridge dir       │
  │    3. subprocess.Popen(bridge.js)     │
  │    4. Poll GET /health (15s timeout)  │
  │    5. Start _poll_loop() task         │
  │                                       │
  │  _poll_loop():                        │
  │    GET /messages every 500ms          │
  │    → build MessageEvent               │
  │    → self.handle_message(event)       │
  │                                       │
  │  send(chat_id, text):                 │
  │    POST /send {text, target}          │
  │                                       │
  │  disconnect():                        │
  │    kill subprocess (SIGTERM→SIGKILL)  │
  └──────────────┬───────────────────────┘
                 │ HTTP (localhost)
                 ▼
  ┌──────────────────────────────────────┐
  │  bridge/index.js                      │
  │  Node.js Subprocess                   │
  │                                       │
  │  HTTP Server:                         │
  │    GET  /health  → {status, players}  │
  │    GET  /messages → drain msgQueue[]  │
  │    POST /send    → bot.chat(text)     │
  │                                       │
  │  Platform Library (mineflayer/...)    │
  │    connects to external service       │
  │    queues incoming messages           │
  └──────────────────────────────────────┘
```

## When to Use This Pattern

- The platform SDK/library only exists for Node.js (or another language)
- The protocol requires persistent TCP connection (not webhooks)
- You need to run a "bot" or "client" that joins the platform as a user
- The platform adapter needs to stay online continuously, not just respond to webhooks

## Bridge HTTP Contract

The bridge must expose exactly three endpoints:

### GET /health
Returns bridge status. Python adapter polls this up to 15 seconds after spawning.

**Response:**
```json
{
  "status": "connected" | "connecting",
  "players": ["player1", "player2"],
  "username": "BotName"
}
```

### GET /messages
Returns and drains the message queue. Python adapter polls this every ~500ms.

**Response:** Array of message objects:
```json
[
  { "player": "Steve", "message": "hello", "time": 1712345678000 },
  { "player": "Alex", "message": "hi bot", "time": 1712345679000 }
]
```

### POST /send
Sends a message from Hermes. Python adapter calls this for each response chunk.

**Request:**
```json
{
  "text": "@Steve Hello!",
  "target": "steve"
}
```

**Response:** `{"ok": true}`

## Python Adapter Pattern

### connect()

```python
async def connect(self, *, is_reconnect: bool = False) -> bool:
    self._running = True
    node = _find_node()                          # find node executable
    if not node: return False

    _ensure_bridge_deps(self.bridge_dir)          # npm install --production
    _kill_port(self.bridge_port)                  # kill stale process on port

    # Spawn bridge
    env = os.environ.copy()
    env["BRIDGE_PORT"] = str(self.bridge_port)    # pass config via env
    self._process = subprocess.Popen(
        [node, bridge_script], env=env, 
        stdout=subprocess.PIPE, stderr=log_file,
    )

    # Wait for health check
    import aiohttp
    self._http_session = aiohttp.ClientSession()
    for _ in range(15):                          # up to 15 seconds
        await asyncio.sleep(1)
        if self._process.poll() is not None:      # bridge died
            return False
        try:
            async with self._http_session.get(f"http://127.0.0.1:{port}/health", timeout=2) as r:
                if r.status == 200: break
        except: continue
    else:
        return False                              # didn't come up

    self._poll_task = asyncio.create_task(self._poll_loop())
    self._mark_connected()
    return True
```

### send()

```python
async def send(self, chat_id: str, text: str, **kwargs) -> SendResult:
    if not self._http_session:
        return SendResult(False, error="no bridge")
    limit = self.MAX_MESSAGE_LENGTH - len(chat_id) - 4  # room for @player prefix
    chunks = [text[i:i+limit] for i in range(0, len(text), limit)]
    for i, chunk in enumerate(chunks):
        display = f"@{chat_id} {chunk}" if len(chunks) == 1 else f"@{chat_id} [{i+1}/{len(chunks)}] {chunk}"
        try:
            async with self._http_session.post(
                f"http://127.0.0.1:{self.bridge_port}/send",
                json={"text": display, "target": chat_id}, timeout=5,
            ) as r: await r.json()
        except Exception as e:
            return SendResult(False, error=str(e))
        await asyncio.sleep(0.3)   # rate limit between chunks
    return SendResult(True)
```

### _poll_loop()

```python
async def _poll_loop(self):
    while self._running and self._http_session:
        try:
            async with self._http_session.get(
                f"http://127.0.0.1:{self.bridge_port}/messages", timeout=10,
            ) as r:
                if r.status == 200:
                    for m in await r.json():
                        await self._handle_incoming(m)
        except asyncio.CancelledError: break
        except Exception: pass
        await asyncio.sleep(0.5)
```

### disconnect()

```python
async def disconnect(self):
    self._running = False
    if self._poll_task: self._poll_task.cancel()
    if self._process:
        try:
            self._process.terminate()
            await asyncio.sleep(1)
            if self._process.poll() is None: self._process.kill()
        except ProcessLookupError: pass
    if self._http_session: await self._http_session.close()
    if self._log_fh: self._log_fh.close()
```

## Node.js Bridge Pattern

Minimal bridge using Node's built-in `http` module (no Express dependency):

```javascript
const mineflayer = require('mineflayer');   // or platform-specific lib
const http = require('http');

const PORT = parseInt(process.env.MINECRAFT_BRIDGE_PORT || '13000');
let bot = null;
const msgQueue = [];

function connectBot() {
    bot = mineflayer.createBot({
        host: process.env.MINECRAFT_SERVER,
        port: parseInt(process.env.MINECRAFT_PORT || '25565'),
        username: process.env.MINECRAFT_USERNAME || 'HermesBot',
        auth: (process.env.MINECRAFT_AUTH || 'offline').toLowerCase(),
    });
    bot.on('chat', (username, message) => {
        if (username === bot.username) return;    // skip self
        msgQueue.push({ player: username, message, time: Date.now() });
    });
    bot.on('end', () => { bot = null; setTimeout(connectBot, 10000); });
    bot.on('error', (err) => console.error(err.message));
}

const server = http.createServer((req, res) => {
    res.setHeader('Content-Type', 'application/json');
    
    if (req.method === 'GET' && req.url === '/health') {
        res.end(JSON.stringify({
            status: bot?.entity ? 'connected' : 'connecting',
            players: bot?.entity ? Object.keys(bot.players) : [],
        }));
        return;
    }
    
    if (req.method === 'GET' && req.url === '/messages') {
        res.end(JSON.stringify(msgQueue.splice(0)));  // drain
        return;
    }
    
    if (req.method === 'POST' && req.url === '/send') {
        let body = '';
        req.on('data', c => body += c);
        req.on('end', () => {
            const { text, target } = JSON.parse(body);
            if (bot?.entity) bot.chat(text);  // or /tell target
            res.end(JSON.stringify({ ok: true }));
        });
        return;
    }
    
    res.statusCode = 404;
    res.end(JSON.stringify({ error: 'not found' }));
});

server.listen(PORT, () => {
    console.log(`Bridge listening on port ${PORT}`);
    connectBot();
});
```

## Bridge Directory Structure

Inside the plugin directory:

```
~/.hermes/plugins/<platform>/
├── plugin.yaml           # Plugin metadata + env vars
├── adapter.py            # Python adapter (see above)
├── __init__.py           # re-exports register()
└── bridge/
    ├── index.js           # Node.js bridge (see above)
    └── package.json       # Single dep: mineflayer or platform lib
```

## Plugin Registration

The `register()` function in `adapter.py` registers the platform:

```python
def register(ctx):
    ctx.register_platform(
        name="minecraft",
        label="Minecraft",
        adapter_factory=lambda cfg: MinecraftPlatformAdapter(cfg),
        check_fn=check_requirements,                    # has node + bridge dir?
        required_env=["MINECRAFT_ENABLED", "MINECRAFT_SERVER"],
        install_hint="Requires Node.js — run: apt install nodejs npm",
        env_enablement_fn=_env_enablement,              # reads env → config
        allowed_users_env="MINECRAFT_ALLOWED_USERS",
        allow_all_env="MINECRAFT_ALLOW_ALL_USERS",
        max_message_length=256,
        emoji="⛏",
        platform_hint="You are chatting via Minecraft. 256-char limit...",
    )
```

## Key Pitfalls

| Issue | Symptom | Fix |
|-------|---------|-----|
| Stale process on port | Bridge start timeout | `_kill_port()` before spawning |
| Bridge dies without notice | HTTP errors on every poll | Check `process.poll()` during health wait |
| npm install failed | Bridge script not found | Run `_ensure_bridge_deps()` before spawn |
| Message queue grows unbounded | Memory leak | Drain queue on every `/messages` GET |
| Bridge stdout not consumed | Backpressure, deadlock | Pipe stdout to log file, not subprocess.PIPE |
| Port collision with another adapter | Wrong bridge receives messages | Use unique port per adapter via config |

## Existing Adapters Using This Pattern

- **WhatsApp** (`plugins/platforms/whatsapp/`) — Baileys Node.js bridge
- **Minecraft** (`~/.hermes/plugins/minecraft/`) — Mineflayer Node.js bridge
