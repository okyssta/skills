# Subscription Audit — Worked Example

This is a real session transcript anonymized as a reference. Use it as a template for conducting your own provider health + subscription audits.

## Session Transcript

**Trigger:** User asks "looking at my current hermes usage what subscription can fulfil my needs"

### Phase 1: Clarify Target

**Pitfall:** The agent initially assumed "subscription" meant Hermes/Nous Portal.
**Correction from user:** "not hermes like chatgpt, z.ai, other subs" → user meant external AI service subscriptions.

**Rule:** Always ask/confirm which type of subscription: Hermes/Nous Portal vs external AI services (ChatGPT, Claude, Z.AI, DeepSeek, etc.). They are completely separate budget lines.

### Phase 2: Gather Usage Data

```bash
# Primary: 30-day usage volume
hermes insights --days 30

# Output showed:
# - 481 sessions in 11 active days (~44/day)
# - 1.76B total tokens
# - 195.6M input / 8.8M output
# - 20,727 tool calls
# - Models: deepseek-v4-flash (848M), nemotron-3-ultra-550b:free (327M),
#           mimo-v2.5 (299M), gpt-5.5 (145M), north-mini-code-free (85M)
# - Platforms: cron (286), subagent (106), discord (85), cli (4)
```

### Phase 3: Audit Provider Auth Health

```bash
# Active credentials and their status
hermes auth list

# Output showed:
# - openrouter: rate-limited (429), 59min cooldown remaining
# - opencode-zen: 4 keys all auth failed (401) — dead
# - openai-codex: usage_limit_reached — exhausted
# - gemini: rate-limited (429)
# - opencode-go: WORKING (free endpoint, default provider)
# - github copilot: 5 pooled keys, working
# - nvidia: working
# - openai-api: has key set (but unknown billing status)
```

### Phase 4: Map Pain Points to Subscriptions

| Pain point | Root cause | Best fix | $ |
|-----------|------------|---------|---|
| OpenRouter 429s | Hitting free-tier 200 req/day limit | $5-20 OpenRouter credits | $5-20 |
| OpenCode Zen all 401 | Free endpoint expired | Drop from fallback, use OR instead | $0 |
| Codex exhausted | ChatGPT Pro monthly cap hit | Wait for reset or switch to API key | $0-20 |
| Gemini 429 | Free tier rate limit | Switch to OpenRouter-routed Gemini | $0 |
| No Claude access | No Anthropic key/account | Claude Pro $20 + `hermes proxy` | $20/mo |

### Phase 5: Calculate Dollar Figures

Heavy user scenario (44 sessions/day, ~4.8B tokens/month projected):

**Scenario 1 — Keep using free deepseek-v4-flash (via opencode-go), just fix fallbacks:**
- $5-10 on OpenRouter credits → unlocks fallback rate limits for when primary fails
- Fix the 4 dead opencode-zen keys in config
- Total: **$5-10/mo**

**Scenario 2 — Move bulk work to paid deepseek-v4-flash:**
- DeepSeek API: $0.09/M in / $0.18/M out
- At 4.8B tokens/month (est.): ~$50-70/mo on DeepSeek alone
- Total: **$50-70/mo**

**Scenario 3 — Mix: free primary + paid fallbacks:**
- Keep deepseek-v4-flash free via opencode-go
- Add $10-20 OpenRouter credits for fallback via Claude/GPT-5.5 on critical sessions
- Total: **$10-20/mo**

### Key Lessons from This Audit

1. **Free endpoints can keep running alongside paid ones** — the user's opencode-go → deepseek-v4-flash was working fine. Only the fallbacks were broken.
2. **OpenRouter credits fix multiple providers at once** — one top-up unblocks Claude, Gemini, GLM, DeepSeek, and every other model OR routes — because the fallback chain already routes through OpenRouter.
3. **Always check `hermes auth list` before recommending new subscriptions** — they might already have a key that just needs billing added.
4. **Individual model pricing via OpenRouter:** `openrouter.ai/<provider>/<model-name>` shows current per-token rates.
5. **The cheapest paid fix is often DeepSeek API direct** — $0.09/M in is cheaper than almost any other paid model by 3-10x.
