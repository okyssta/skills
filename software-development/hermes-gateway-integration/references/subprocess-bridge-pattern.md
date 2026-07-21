# Subprocess Bridge Pattern

When a Hermes platform's SDK is not Python (Node.js, Go, Rust, C#, etc.), the
adapter spawns a subprocess running that SDK and communicates over HTTP on a
local port. This is the same pattern WhatsApp uses (Baileys Node.js bridge).

## Architecture

```
Python Adapter (BasePlatformAdapter)        Subprocess (e.g. Node.js)
                                           ┌─────────────────────────┐
  subprocess.Popen ───────────────────────►│  http.createServer()    │
  env: env vars                            │  PORT=13000             │
  stderr → bridge.log                      │                         │
                                           │  GET /health           │
  poll every 500ms ───────────────────────►│  → {status, players}   │
                                           │                         │
  GET /messages ◄──────────────────────────│  GET /messages          │
  → [{player, message}]                    │  → message[] drain      │
                                           │                         │
  POST /send {text} ──────────────────────►│  POST /send             │
                                           │  bot.chat(text)         │
                                           └─────────────────────────┘
```

## Lifecycle

### Startup
1. `connect()` resolves the subprocess binary (e.g. `find_node_executable()`)
2. Ensures dependencies are installed (`npm install --production`)
3. Kills any stale process on the target port
4. Spawns the child process with `subprocess.Popen`
5. Polls `GET /health` up to 15s (1s interval) waiting for the bridge to respond
6. Kicks off async `_poll_loop()` (GET /messages every 500ms)
7. Calls `self._mark_connected()`

### Shutdown
1. Sets `self._running = False` (stops poll loop)
2. Calls `process.terminate()` → 1s wait → `process.kill()` if still alive
3. Closes aiohttp session and log file

### Inbound messages
Bridge queues chat events in an in-memory array. Python polls `/messages`
which returns all queued events and drains them (JSON array, each with
`{player, message, time}`). Python builds a `MessageEvent` and calls
`self.handle_message(event)`.

### Outbound messages
`send(chat_id, text)` → `POST /send` → bridge calls `bot.chat()` or
equivalent. Long text is chunked at the platform's message limit before
sending.

## Example: Node.js Bridge (Mineflayer)

```javascript
const mineflayer = require('mineflayer');
const http = require('http');

const MC_HOST     = process.env.MINECRAFT_SERVER;
const MC_PORT     = parseInt(process.env.MINECRAFT_PORT || '25565');
const MC_USERNAME = process.env.MINECRAFT_USERNAME || 'Bot';
const MC_AUTH     = (process.env.MINECRAFT_AUTH || 'offline').toLowerCase();
const BRIDGE_PORT = parseInt(process.env.MINECRAFT_BRIDGE_PORT || '13000');

let bot = null;
const msgQueue = [];

function connectBot() {
    bot = mineflayer.createBot({ host: MC_HOST, port: MC_PORT,
        username: MC_USERNAME, auth: MC_AUTH });

    bot.on('chat', (username, message) => {
        if (username === bot.username) return;
        msgQueue.push({ player: username, message, time: Date.now() });
    });

    bot.on('end', () => { /* reconnect after delay */ });
    bot.on('error', (err) => console.error(err.message));
}

const server = http.createServer((req, res) => {
    res.setHeader('Content-Type', 'application/json');
    if (req.method === 'GET' && req.url === '/health') {
        res.end(JSON.stringify({
            status: bot?.entity ? 'connected' : 'connecting',
            players: bot?.players ? Object.keys(bot.players) : [],
        }));
    } else if (req.method === 'GET' && req.url === '/messages') {
        res.end(JSON.stringify(msgQueue.splice(0)));
    } else if (req.method === 'POST' && req.url === '/send') {
        let body = '';
        req.on('data', c => body += c);
        req.on('end', () => {
            const { text, target } = JSON.parse(body);
            if (bot?.entity) bot.chat(text);
            res.end(JSON.stringify({ ok: true }));
        });
    } else {
        res.statusCode = 404;
        res.end(JSON.stringify({ error: 'not found' }));
    }
});
server.listen(BRIDGE_PORT, () => connectBot());
```

## Key Details

- **Port:** Use a fixed default port (13000) or allow override via env var
- **Stale process cleanup:** Kill any process listening on the target port on startup (`lsof -ti tcp:PORT -sTCP:LISTEN` → `os.kill(pid, SIGTERM)`)
- **Health check:** Bridge returns `{status: "connected" | "connecting", players: [...]}` — Python waits up to 15s for the server to respond, but doesn't hard-fail if MC connection isn't ready yet
- **Node.js discovery:** Use `find_node_executable("node")` from `hermes_constants` or fall back to `subprocess.run(["node", "--version"])`
- **Deps install:** Run `npm install --production --no-audit --no-fund` in the bridge directory on first startup
- **Logging:** Bridge stderr → `~/.hermes/logs/<platform>-bridge.log`

## Pitfalls

- **stdout PIPE blocks the subprocess**: If you use `stdout=subprocess.PIPE` in `subprocess.Popen` but never read from the pipe, the subprocess's stdout buffer fills (~64KB) and the child process blocks entirely — no event processing, no I/O. Always redirect stdout to a log file: `stdout=self._log_fh, stderr=subprocess.STDOUT`. Only use PIPE if you have a dedicated reader task.
- **Process tree cleanup**: `process.terminate()` only kills the direct child. The Node.js process may have its own child processes (e.g. Chromium for Puppeteer). Use `taskkill /T` on Windows or `killpg` on POSIX for complete teardown.
- **Port conflicts**: If two bridge instances run on the same port, the second will fail silently. Always attempt stale-process cleanup on startup (`lsof -ti tcp:PORT -sTCP:LISTEN`), and log the port being used.
- **npm install timing**: First startup is slow if deps aren't cached. Run `npm install` during `check_requirements()` or `connect()` and log progress.
- **Health check doesn't mean MC connected**: The bridge's `/health` returning `{"status":"connected"}` only means the HTTP server is up and Mineflayer connected. The Minecraft server may still kick the bot for illegal characters (emoji, § codes) after the health check passes — character filtering must happen in the Python adapter's `send()`.
