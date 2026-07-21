# Plugin Debugging Checklist

Common failure modes when building a new Hermes gateway platform plugin, in order of likelihood.

## 1. Plugin isn't discovered

```bash
cd /usr/local/lib/hermes-agent && python3 -c "
from hermes_cli.plugins import discover_plugins
from gateway.platform_registry import platform_registry
discover_plugins()
e = platform_registry.get('my_platform')
print('Registered:', list(platform_registry.registry.keys()))
"
```

Check:
- `~/.hermes/plugins/<name>/plugin.yaml` exists with correct `kind: platform`
- `__init__.py` exports `register` from adapter
- `register(ctx)` calls `ctx.register_platform(...)`

## 2. `send()` crashes with TypeError

```
TypeError: MinecraftPlatformAdapter.send() missing 1 required positional argument: 'text'
```

**Fix:** Change parameter name from `text` to `content`. The base class signature is:
```python
async def send(self, chat_id, content, reply_to=None, metadata=None, **kwargs) -> SendResult:
```

The gateway calls it with `content=...` as a keyword argument.

## 3. Subprocess connects then stops responding

Bot connects to the server, health endpoint works, but no messages flow after a minute.

**Root cause:** Bridge's stdout is piped (`stdout=subprocess.PIPE`) but never read. The pipe buffer fills (~64KB on Linux) and Node.js event loop blocks entirely. All I/O stops — chat events, movement, HTTP server — until something drains the pipe.

**Fix:** Redirect stdout to the log file:
```python
self._process = subprocess.Popen(
    [node, bridge_script], env=env,
    stdout=self._log_fh, stderr=subprocess.STDOUT,
)
```

**Signs this is happening:** Bridge logs stop appearing mid-way. `curl -s http://127.0.0.1:PORT/health` still works (the HTTP server had its last response buffered), but `/messages` returns stale data that was already there before the block.

## 4. Regex `\xa7` in raw strings causes crash

```
re.error: bad escape \x at position 0
```

**Fix:** In raw Python strings (`r"..."`), `\x` is not processed as a hex escape — it's literal. Python's `re` module then sees `\x` as an invalid regex escape. Use either:
- The literal character: `"§"` (U+00A7) in a non-raw string
- Unicode escape in a non-raw string: `"\u00a7"`
- A raw string with the character itself: `r"§"` (works, raw strings preserve the literal)

**Wrong:** `r"\xa7[0-9a-f]"` — tried to match literal `\xa7`
**Right:** `"\u00a7[0-9a-f]"` or `"§[0-9a-f]"`

## 5. Bot connects then gets kicked immediately

```
Illegal characters in chat
```

**Root cause:** Non-ASCII characters in the message. Minecraft's default chat filter rejects characters outside printable ASCII (U+0020-U+007E). Common culprits:
- Emoji in `send_typing()`: `🤔 Thinking...` → strip to `"Thinking..."`
- Unicode formatting in responses: `§lbold§r`, `→`, `✓`, `🚀`
- Smart quotes: `"` and `"` (U+201C/U+201D)
- Dashes: `—` (U+2014 em dash)

**Fix:** ASCII-encode with replacement before sending:
```python
text = text.encode("ascii", "replace").decode("ascii")
```

**Server config:** Some servers have `allow-illegal-characters` setting. But fixing the adapter is more portable.

## 6. `platform_hint` causes the LLM to use formatting that gets rejected

If the hint says "Use § codes for formatting" or "You can use emoji", the LLM will use them. If the server rejects those characters, the bot gets kicked.

**Fix:** Keep the hint conservative — tell the LLM the constraints, not the possibilities:
```python
platform_hint="Plain text only. No markdown, no bold, no colors, no emoji."
```

The LLM follows the hint literally. If you describe features, it uses them. If you describe limits, it avoids them.

## 7. Tool progress doesn't appear

If tool progress (terminal commands, file edits) aren't showing up in the platform:

**Fix:** Set `notice_delivery: private` in the extra config, and implement `send_private_notice()` that sends via the platform's private message mechanism:

```python
extra = {
    ...
    "notice_delivery": "private",
}
```

And in the adapter:
```python
async def send_private_notice(self, chat_id, user_id, content, ...) -> SendResult:
    """Send tool progress via platform's private message (e.g., /tell in Minecraft)."""
    return await self.send(chat_id, content, ...)
```

## 8. Commands don't work with `/` prefix

Minecraft intercepts all messages starting with `/` at the server level — the bot never sees them.

**Fix:** Use a non-conflicting prefix like `$` or `!`, and make it optional (not a gate):

```python
# In _handle_incoming:
if self.prefix and message.startswith(self.prefix):
    clean = message[len(self.prefix):].strip()  # Strip prefix for commands
else:
    clean = message  # Normal chat — still forward it
```

## 9. Long messages get truncated or rejected

If responses > 256 chars (or the platform's limit) are rejected:

**Fix:** Set `max_message_length` in `register()` and chunk in `send()`:

```python
ctx.register_platform(
    ...,
    max_message_length=256,
)
```

```python
async def send(self, chat_id, content, ...):
    limit = self.MAX_MESSAGE_LENGTH  # inherits from max_message_length
    chunks = [content[i:i+limit] for i in range(0, len(content), limit)]
    for i, chunk in enumerate(chunks):
        prefix = f"[{i+1}/{len(chunks)}] " if len(chunks) > 1 else ""
        await self._send_single(chat_id, prefix + chunk)
```

## 10. Platform hint about player name prefix

If you remove the player name prefix from responses (e.g., from `@player msg` to just `msg`), update the platform_hint accordingly. Otherwise the LLM keeps prefacing responses with "Hey PlayerName!" thinking the platform needs it.
