# Gateway Inbound Message Pipeline & Debounce/Merge Pitfalls

## Three Root Causes for Issue #59582

Bug #59582 ("WhatsApp draft reply not updating from latest inbound message")
has **three distinct root causes** that can fire independently or together:

1. **Interrupt-vs-pending race** (drain loop) — The agent receives the
   *older* message text because the interrupt message is discarded when a
   pending event exists. See checklist item #6 below.

2. **`message_id` not updated in merge** — The bot *quotes* the wrong
   (older) message because `merge_pending_message_event` doesn't update
   `message_id` from the latest event. See the "Debounce/Merge Pitfall"
   section and checklist item #5 below.

3. **Baileys bridge text batching** — The WhatsApp Baileys bridge adapter
   (`plugins/platforms/whatsapp/adapter.py`) batches rapid-fire text messages
   in `_enqueue_text_event` before dispatching them to `handle_message`.
   Unlike the base-adapter `_queue_text_debounce`, the bridge adapter's custom
   batch logic **never** updates `message_id` or `reply_to_message_id` from
   later events. When the batch flushes, the event still carries the *first*
   message's IDs. See "Baileys Bridge Text Batching Gap" below.

Symptom #1 produces agent output like "This turn didn't include new message
text — I used the earlier inbound." Symptom #2 produces a reply that quotes
the wrong user message. Symptom #3 produces a reply that quotes the wrong
user message even when the agent **is not busy** (the messages arrived so
close together that they were batched before dispatch). Both #2 and #3 can
appear in the same session when rapid follow-ups arrive while the agent
is busy.

## Message Flow (WhatsApp Cloud Example)

```
Webhook POST (_handle_webhook)
  → _dispatch_payload
    → _build_message_event_from_cloud  (raw JSON → MessageEvent)
      → rich_sent_store.record()       (index inbound text by wamid)
      → _last_inbound_wamid_by_chat    (cache latest wamid for typing indicator)
    → handle_message(event)            (base adapter: gate + queue/dispatch)
      ├─ session NOT active → _start_session_processing → _process_message_background
      └─ session IS active  → merge into pending/debounce → processed after current turn
        → _process_message_background
          → _message_handler(event)    (→ _handle_message in run.py)
            → _handle_message_with_agent
              → _prepare_inbound_message_text(event)
                → event.text + notes + reply context + media enrichment
              → _run_agent(message_text, ...)
```

## Key Data Structures

| Field | Where Set | Purpose |
|---|---|---|
| `_last_inbound_wamid_by_chat` | `_build_message_event_from_cloud` | Latest wamid per chat for typing/read receipts |
| `_pending_messages` (Dict[str, MessageEvent]) | `handle_message` busy path | Queued follow-up while agent runs |
| `TextDebounceState.event` | `_queue_text_debounce` | Accumulated event during debounce window |
| `rich_sent_store` | `_build_message_event_from_cloud` (inbound) + `send` (outbound) | wamid→text index for reply-to resolution |

## The Debounce/Merge Pitfall

When a session is active and a new TEXT message arrives, `handle_message` routes
it through either `_queue_text_debounce` (if `busy_text_mode == "queue"`) or
`merge_pending_message_event` (plain queue path).

### `_queue_text_debounce` (base.py ~line 4234)

Creates a `TextDebounceState(event=event)`. On subsequent messages in the
debounce window, it mutates `state.event` **in-place**:

```python
# Line ~4266
if event.text:
    state.event.text = (
        f"{state.event.text}\n{event.text}"
        if state.event.text
        else event.text
    )
latest_message_id = getattr(event, "message_id", None)
latest_anchor = latest_message_id or getattr(event, "reply_to_message_id", None)
if latest_message_id is not None:
    state.event.message_id = str(latest_message_id)
if latest_anchor is not None and hasattr(state.event, "reply_to_message_id"):
    state.event.reply_to_message_id = str(latest_anchor)
```

**Known gap**: Only `message_id` and `reply_to_message_id` are carried forward.
Fields NOT updated from the latest event:
- `reply_to_text` (quoted message text resolution)
- `reply_to_is_own_message` (quoted author flag)
- `raw_message` (raw platform payload)
- `timestamp`
- `media_urls` / `media_types`

This means if message B replies to a different message than message A, the
reply context fields remain stale from message A. The agent receives message
B's text but message A's reply context.

### `merge_pending_message_event` (base.py ~line 2064)

When `merge_text=True` (TEXT→TEXT), text is appended:
```python
existing.text = f"{existing.text}\n{event.text}" if existing.text else event.text
return  # ← returns WITHOUT updating message_id!
```
**Critical gap**: `message_id` is NOT updated from the latest event. The
merged pending event retains the FIRST message's `message_id`. When the
agent later processes this merged event, `_reply_anchor_for_event(event)`
returns the stale first message's wamid — so the bot's reply quotes the
wrong (older) message. This is the root cause of bug #59582 ("WhatsApp
draft reply not updating from latest inbound message").

Contrast with `_queue_text_debounce` which DOES update `message_id`:
```python
# _queue_text_debounce (base.py ~4272)
latest_message_id = getattr(event, "message_id", None)
if latest_message_id is not None:
    state.event.message_id = str(latest_message_id)
```

Other fields also not updated (same gap as debounce): `reply_to_text`,
`reply_to_is_own_message`, `raw_message`, `timestamp`, `media_urls` /
`media_types`.

### Baileys Bridge `_enqueue_text_event` (plugins/platforms/whatsapp/adapter.py ~line 1282)

The WhatsApp Baileys bridge adapter uses its own text batching mechanism
independent of the base adapter's `_queue_text_debounce` or
`merge_pending_message_event`. It runs **before** `handle_message` is
ever called — while the agent is idle — as a debounce for rapid-fire
text messages:

```python
def _enqueue_text_event(self, event: MessageEvent) -> None:
    key = self._text_batch_key(event)
    existing = self._pending_text_batches.get(key)
    chunk_len = len(event.text or "")
    if existing is None:
        event._last_chunk_len = chunk_len
        self._pending_text_batches[key] = event     # first message
    else:
        if event.text:
            existing.text = f"{existing.text}\n{event.text}"  # append text only
        existing._last_chunk_len = chunk_len
        if event.media_urls:
            existing.media_urls.extend(event.media_urls)
            existing.media_types.extend(event.media_types)
        # message_id, reply_to_message_id, reply_to_text,
        # reply_to_is_own_message, raw_message, timestamp
        # are NEVER updated from the later event!
```

**Critical gap**: Unlike `_queue_text_debounce` (which carries forward
`message_id` and `reply_to_message_id`), the bridge's `_enqueue_text_event`
updates **nothing** except `text`, `media_urls`, and `media_types`. The
batched event retains every identity field from the first message.
When `_flush_text_batch` eventually calls `handle_message(event)`, the
event still carries the first message's `message_id` and
`reply_to_message_id`. The agent's reply quotes the wrong message.

This path is unique because it fires when the agent is **not busy** — the
messages simply arrived within the debounce window (default ~500-600ms).
It is the most commonly triggered code path for two rapid WhatsApp texts.

**Fix pattern**: After appending text, mirror what `_queue_text_debounce`
does — carry forward `message_id` and `reply_to_message_id` from the
latest event:

```python
# In _enqueue_text_event, after appending text:
if event.text:
    existing.text = f"{existing.text}\n{event.text}" if existing.text else event.text
    # Carry forward identity fields from the latest event
    latest_mid = getattr(event, "message_id", None)
    if latest_mid is not None:
        existing.message_id = str(latest_mid)
    latest_anchor = latest_mid or getattr(event, "reply_to_message_id", None)
    if latest_anchor is not None and hasattr(existing, "reply_to_message_id"):
        existing.reply_to_message_id = str(latest_anchor)
```

### Fix pattern

When patching any of the three merge paths, carry forward from the **latest** event:
```python
for attr in ("reply_to_text", "reply_to_is_own_message", "raw_message", "timestamp"):
    val = getattr(event, attr, None)
    if val is not None:
        setattr(state.event, attr, val)
```

For `merge_pending_message_event` specifically, also update `message_id`:
```python
latest_mid = getattr(event, "message_id", None)
if latest_mid is not None:
    existing.message_id = str(latest_mid)
latest_rid = getattr(event, "reply_to_message_id", None)
if latest_rid is not None and hasattr(existing, "reply_to_message_id"):
    existing.reply_to_message_id = str(latest_rid)
```

## `rich_sent_store` — Reply Context Resolution

WhatsApp Cloud webhook `context` carries only the quoted message's `id` and
`from` — never its text. The adapter resolves text from `rich_sent_store`:

```python
reply_to_text = rich_sent_store.lookup(chat_id, reply_to_id)
```

This store is populated on:
- **Inbound**: `_build_message_event_from_cloud` calls `rich_sent_store.record(chat_id, wamid, body)`
- **Outbound**: `send()` calls `rich_sent_store.record(chat_id, last_message_id, formatted)`

If a reply references a wamid the gateway never saw (e.g. from before restart),
`reply_to_text` is None — this is expected and handled by run.py (no
disambiguation prefix injected).

## Debugging Checklist for Adapter Issues

1. **Message text missing or stale**: Check if the event went through debounce
   merge. Add logging at `_queue_text_debounce` entry to see which fields
   are carried forward.

2. **Reply context wrong**: Verify `rich_sent_store.lookup()` returns the
   expected text. Check if the wamid was indexed (inbound record or outbound
   send).

3. **Typing indicator on wrong message**: Check `_last_inbound_wamid_by_chat`
   — it should hold the latest accepted inbound's wamid, not a filtered one.
   Note: the typing indicator refresh reads this shared cache, so it can
   jump to a newer message mid-processing (confusing UX but technically
   correct — marking the latest message as read).

4. **Pending message lost**: Check the late-arrival drain path in
   `_process_message_background` (line ~5288). If `existing_task is not
   current_task`, the event is re-queued — verify it's not stuck.

5. **Bot replies to wrong message after rapid follow-ups**: Check if the
   pending event's `message_id` matches the user's latest message. If two
   text messages arrived while the agent was busy, `merge_pending_message_event`
   may have kept the first message's `message_id`. See bug #59582.

6. **Agent receives older message text instead of latest (interrupt-vs-pending
   race)**: When `busy_input_mode == "interrupt"` (the default) and TWO or
   more messages arrive while the agent is busy, both the FIFO queue AND the
   interrupt path fire for the latest message. After the agent completes, the
   drain loop at `gateway/run.py:19125-19142` runs:

   ```python
   pending_event = _dequeue_pending_event(adapter, session_key)
   pending_event = self._promote_queued_event(session_key, adapter, pending_event)
   if result.get("interrupted") and not pending_event and result.get("interrupt_message"):
       # ... use interrupt_message (the newer text)
   elif pending_event:
       # ... use pending_event.text (the OLDER text)
   ```

   The guard `not pending_event` means that when BOTH an interrupt message
   (newer) AND a pending event (older) exist, the `elif` branch fires and the
   **older** pending event is used as the next turn. The interrupt message —
   the user's latest text — is silently discarded.

   **Scenario:**
   1. Agent running. Message A arrives → queued in `_pending_messages` slot.
   2. Message B arrives → queued in FIFO overflow → `running_agent.interrupt(event.text)` fires with B's text.
   3. Agent interrupted, returns `{"interrupted": True, "interrupt_message": "B text"}`.
   4. Drain loop: dequeues A from slot → `pending_event = A`.
   5. `result.get("interrupted")` True, but `not pending_event` is False → `elif` fires.
   6. A's text is used as the next turn. B is deferred to a future drain.

   **Fix pattern:** Change the condition so the interrupt message takes
   precedence, and re-queue any stale pending event:

   ```python
   if result.get("interrupted") and result.get("interrupt_message"):
       interrupt_message = result.get("interrupt_message")
       if _is_control_interrupt_message(interrupt_message):
           logger.info("Ignoring control interrupt: %s", interrupt_message)
       else:
           pending = interrupt_message
           if pending_event:
               self._queue_or_replace_pending_event(session_key, pending_event)
   if not pending and pending_event:
       # ... existing pending_event processing ...
   ```

   **Diagnostic log lines to grep for:**
   - `"PRIORITY interrupt for session"` — confirms interrupt was triggered
   - `"Processing queued message after agent completion"` — confirms drain loop picked up a pending event
   - `"Ignoring control interrupt message"` — confirms a control interrupt (stop/reset) was received

   The agent's own output when this bug fires often includes phrases like
   "This turn didn't include new message text" or "I used the earlier inbound"
   — the LLM observes it received stale text and reports it to the user.
