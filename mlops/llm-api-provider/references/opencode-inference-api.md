# OpenCode Inference API — Testing & Free Model Guide

Tested live against two endpoints:
- **Console endpoint:** `https://console.opencode.ai/inference/openai/v1/chat/completions`
- **Zen endpoint:** `https://opencode.ai/zen/v1/chat/completions`
API key used: `oc_sk_5f5de26c3507_LIEVQfbORZYJz8ekb6Bql7JkAfX3tJBb`.

## Base URLs

| Service | URL | Auth Method |
|---------|-----|-------------|
| Console OpenAI-compatible chat | `https://console.opencode.ai/inference/openai/v1/chat/completions` | `Authorization: Bearer <key>` (or none for `big-pickle`) |
| Console models list | `https://console.opencode.ai/inference/openai/v1/models` | `Authorization: Bearer <key>` |
| **Zen API** (free-gated models) | `https://opencode.ai/zen/v1/chat/completions` | **`x-api-key: <key>`** |
| Zen models list | `https://opencode.ai/zen/v1/models` | `x-api-key: <key>` |
| Go API (subscription) | `https://opencode.ai/zen/go/v1/chat/completions` | `x-api-key: <key>` |

## Authentication — Two Distinct Systems

**⚠️ CRITICAL: The same API key uses DIFFERENT auth headers depending on the endpoint.**

| Endpoint | Header | Example |
|----------|--------|---------|
| Console | `Authorization: Bearer <key>` | `Authorization: Bearer oc_sk_...` |
| Zen | **`x-api-key: <key>`** | `x-api-key: oc_sk_...` |

The console key (`oc_sk_...`) is a "service account key." It works on BOTH endpoints but with different auth headers. Using `Authorization: Bearer` on the Zen endpoint returns `{"error": "Invalid API key."}`.

**Key rule for console endpoint:** "Free chat models can be called without this header. Paid models require it." — but in practice, most models still reject unauthenticated requests unless the model ID is one of the special zero-cost public models (see below).

## Free Models With $0 Cost (per 1M tokens)

From [opencode.ai/docs/zen/](https://opencode.ai/docs/zen/):

| Model ID | Input | Output | Cached |
|----------|-------|--------|--------|
| `big-pickle` | Free | Free | Free |
| `deepseek-v4-flash-free` | Free | Free | Free |
| `mimo-v2.5-free` | Free | Free | Free |
| `north-mini-code-free` | Free | Free | Free |
| `nemotron-3-ultra-free` | Free | Free | Free |
| `hy3-free` | Free | Free | Free |

## Test Results — Which Endpoint + Auth Works for Each Model

### Working curl shape for Zen endpoint:
```bash
curl -X POST "https://opencode.ai/zen/v1/chat/completions" \
  -H "x-api-key: oc_sk_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4-flash-free",
    "messages": [{"role": "user", "content": "Your prompt"}],
    "max_tokens": 4000
  }'
```

### Per-Model Matrix

| Model | Console (no key) | Console (Bearer key) | Zen (x-api-key) | Notes |
|-------|-----------------|---------------------|-----------------|-------|
| **`big-pickle`** | ✅ Works | ✅ Works | ❌ Not on Zen | Maps to `deepseek-v4-flash`. Needs `max_tokens >= 2000`. Cost: `"0"`. |
| **`mimo-v2.5-free`** | ✅ Works (simple prompts) | ❌ 500 error | ❌ 500 error | Flaky 500s on complex prompts. |
| **`deepseek-v4-flash-free`** | ❌ Needs key+balance | ❌ $0.50 min balance | **✅ WORKS** | Cost `"0"`. Needs `max_tokens >= 4000` — deep reasoning phase then content. |
| **`nemotron-3-ultra-free`** | ❌ Needs key | ❌ $0.50 min | **✅ WORKS** | Cost `"0"`. Fast, clean output. |
| **`north-mini-code-free`** | ❌ Needs key | ❌ $0.50 min | **✅ WORKS** | Cost `"0"`. Simple responses. |
| **`hy3-free`** | ❌ Needs key | ❌ $0.50 min | **✅ WORKS** | Maps to `tencent/Hy3`. Cost `"0"`. |
| All paid models (`glm-5`, `kimi-k2.5`, etc.) | ❌ Needs key | ⚠️ Paid cost | ⚠️ Paid cost | NOT free — do not test unless explicitly asked. |

### Key Insight: Two-Tier Free Model System

OpenCode has two tiers of "free":

1. **Console free models** (`big-pickle`, `mimo-v2.5-free`) — work without any API key. Very limited selection.
2. **Zen free-gated models** (`deepseek-v4-flash-free`, `nemotron-3-ultra-free`, `north-mini-code-free`, `hy3-free`) — require an API key with a funded account (minimum $0.50 balance), accessed via the Zen endpoint with `x-api-key` header. Cost is `$0` per request, but the account must have credit to pass the balance gate.

## The $0.50 Minimum Balance Requirement

Even when using a valid API key with a model marked "free" (`deepseek-v4-flash-free`), the **console** endpoint blocks requests if the account has **less than $0.50 of billing credit**:

```json
{"type": "billing_insufficient_balance",
 "message": "Managed inference requires at least $0.50 of available billing credit",
 "minimum_balance_micro_cents": "5000000",
 "balance_micro_cents": "0"}
```

You need to add credit via https://opencode.ai/auth before any API-key-gated model works on the console endpoint. Once funded, use the **Zen endpoint** with `x-api-key` header to access free-gated models at $0 cost.

If the key has $0 balance, the Zen endpoint returns:
```json
{"error": "Managed inference requires at least $0.50 of available billing credit"}
```

## `big-pickle` Deep Dive

**Model ID:** `big-pickle`
**Endpoint:** `POST https://console.opencode.ai/inference/openai/v1/chat/completions`
**Auth:** None required (no API key header)
**Actual model:** `deepseek-v4-flash`
**Cost:** `"0"` on every response

### Working Curl

```bash
curl -X POST "https://console.opencode.ai/inference/openai/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "big-pickle",
    "messages": [{"role": "user", "content": "Write a haiku about coding"}],
    "max_tokens": 2000
  }'
```

### Token Behavior

- Uses ~1000+ tokens on **reasoning** before outputting visible content
- With `max_tokens: 2000`, `finish_reason: "stop"` works correctly — content appears after reasoning completes
- With `max_tokens < 500`, `finish_reason: "length"` — reasoning gets cut off, content is empty
- Response includes `reasoning_content` field (separate from `content`), plus `reasoning_tokens` in usage stats
- All `reasoning_tokens` count toward completion_tokens for billing (but cost = $0)

### Sample Response Shapes

**Works (2000+ max_tokens):**
```json
{
  "model": "deepseek-v4-flash",
  "choices": [{
    "message": {
      "content": "Actual visible output here",
      "reasoning_content": "Thinking step-by-step...",
      "role": "assistant"
    },
    "finish_reason": "stop"
  }],
  "cost": "0",
  "usage": {
    "completion_tokens": 120,
    "completion_tokens_details": { "reasoning_tokens": 106 }
  }
}
```

**Too few tokens:**
```json
{
  "choices": [{ "message": { "content": "", "reasoning_content": "Thinking..." }, "finish_reason": "length" }],
  "cost": "0"
}
```

## Rate Limits

**OpenCode Zen has no rate limits.** Confirmed by maintainer (@rekram1-node, [GH issue #2839](https://github.com/anomalyco/opencode/issues/2839)):

> *"there are no rate limits"*

Individual upstream providers may have their own limits (e.g., NVIDIA NIM ~40 RPM), but these are not enforced by OpenCode's gateway itself.

## Full Model List (48 models as of Jul 2026)

```text
GET https://console.opencode.ai/inference/openai/v1/models
Authorization: Bearer <api-key>
```

Categories:
- **GPT models:** gpt-5.5, gpt-5.5-pro, gpt-5.4, gpt-5.4-pro, gpt-5.4-mini, gpt-5.4-nano, gpt-5.3-codex, gpt-5.3-codex-spark, gpt-5.2, gpt-5.2-codex, gpt-5.1, gpt-5.1-codex, gpt-5.1-codex-max, gpt-5.1-codex-mini, gpt-5, gpt-5-codex, gpt-5-nano
- **Claude models:** claude-fable-5, claude-opus-4-8, claude-opus-4-7, claude-opus-4-6, claude-opus-4-5, claude-opus-4-1, claude-sonnet-5, claude-sonnet-4-6, claude-sonnet-4-5, claude-sonnet-4, claude-haiku-4-5
- **Gemini models:** gemini-3.5-flash, gemini-3.1-pro, gemini-3-flash
- **DeepSeek:** deepseek-v4-pro, deepseek-v4-flash, deepseek-v4-flash-free
- **MiniMax:** minimax-m3, minimax-m2.7, minimax-m2.5
- **GLM:** glm-5.2, glm-5.1, glm-5
- **Kimi:** kimi-k2.7-code, kimi-k2.6, kimi-k2.5
- **Qwen:** qwen3.6-plus, qwen3.5-plus
- **Grok:** grok-4.5, grok-build-0.1
- **Free/special:** big-pickle, mimo-v2.5-free, hy3-free, nemotron-3-ultra-free, north-mini-code-free

## Privacy Notes for Free Models

- **Big Pickle** (free period): data may be used to improve the model
- **DeepSeek V4 Flash Free**: data may be used to improve the model
- **MiMo-V2.5 Free**: data may be used to improve the model
- **North Mini Code Free**: data retained/used for model improvement — do not submit personal/confidential data
- **Nemotron 3 Ultra Free** (NVIDIA): trial use only, data logged for security/product improvement
