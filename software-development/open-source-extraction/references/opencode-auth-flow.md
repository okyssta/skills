# OpenCode / Nectar Auth & API Flow Reference

This document captures the auth/provider flow discovered during forking OpenCode into the Nectar CLI. The flow is complex, spans 3+ layers, and failed with opaque "Invalid API key" errors until traced end-to-end.

## Architecture Overview

```
User Config (nectar.json / opencode.json)
  └─ provider.opencode.options.apiKey = "sk-..."
       │
       ▼
Config Provider Plugin (config/plugin/provider.ts)
  └─ Writes provider.options on Info type (NOT request.body)
       │
       ▼
Provider.Service State (opencode/src/provider/provider.ts)
  └─ Info.options.apiKey available via mergeDeep from config
       │
       ▼
resolveSDK(model, state, envs)
  ├─ options = { ...provider.options }       ← picks up apiKey from config
  ├─ options["baseURL"] ??= model.api.url    ← comes from models.dev catalog!
  ├─ options["apiKey"] ??= provider.key      ← provider.key = credential system (not config)
  └─ createOpenAICompatible(options)         ← @ai-sdk/openai-compatible constructor
       │
       ▼
AI SDK sends: POST {baseURL}/chat/completions
  Headers: Authorization: Bearer {apiKey}
```

## Two API Endpoints, Two Auth Methods

The OpenCode ecosystem has TWO inference endpoints with different auth:

| Endpoint | Auth Header | Where Used |
|---|---|---|
| `https://console.opencode.ai/inference/openai/v1` | `Authorization: Bearer <key>` | Remote config `api` field, **works with Bearer token** |
| `https://opencode.ai/zen/v1` | `x-api-key: <key>` | models.dev catalog `api` field, **rejects Bearer token** |

**Critical trap**: The models.dev catalog (`https://models.dev/api.json`) points to the Zen API. But the `@ai-sdk/openai-compatible` provider sends `Authorization: Bearer` (not `x-api-key`). This mismatch causes the opaque "Invalid API key" error.

**Fix applied in Nectar fork**: In `resolveSDK()`, override the baseURL for opencode provider models:

```typescript
// In opencode/src/provider/provider.ts, inside resolveSDK's baseURL iife():
if (model.providerID === "opencode" || model.providerID === "nectar") {
  url = "https://console.opencode.ai/inference/openai/v1"
}
```

## Why API Key from Config Does NOT Flow to the Credential System

This is the most confusing part. The user's config sets `apiKey` in `provider.opencode.options`. This correctly flows to `provider.options.apiKey` in the Provider State. But there are two parallel paths:

### Path A: OAuth / Credential System (what the code expects)

The opencode plugin (`plugin/provider/opencode.ts`) has a `load()` function that:
1. Checks `ctx.integration.connection.active("opencode")` — only works with OAuth flow
2. If connected, resolves the credential and fetches remote config from `{server}/api/config`
3. The remote config provides the correct API endpoint URL and model configurations

Without an active OAuth connection, `load()` sets `providers = undefined` — no remote config is loaded.

### Path B: API Key from Config (what we want to work)

The user's config API key goes into `provider.options.apiKey` but:
1. `load()` doesn't check for it (only checks OAuth)
2. `withoutCredentials()` in the opencode plugin STRIPS `apiKey` from `request.body`
3. The `hasKey` check only looks at `process.env.OPENCODE_API_KEY`, OAuth credential, or `request.body.apiKey`
4. So `hasKey` evaluates to false, and the code sets `apiKey = "public"` which enables all models but with wrong auth

### Path C: What Actually Makes It Work (Nectar fix)

The key insight: `@ai-sdk/openai-compatible` accepts `apiKey` in its settings and internally converts it to `Authorization: Bearer <key>`. So even though the credential system doesn't see it, the AI SDK provider DOES get the API key from `provider.options`.

The fixes needed are:
1. Force the correct API base URL (console endpoint, not Zen) at the `resolveSDK` level
2. Ensure `provider.options.apiKey` flows to the AI SDK constructor (it already does via `options = { ...provider.options }`)
3. The `hasKey` check in the opencode plugin should also look at `provider.options.apiKey` (or `process.env.OPENCODE_API_KEY`)

## The `openaiCompatible` Lowerer Gap

The `ConfigProviderOptionsV1` lowerer system (in `v1/config/provider-options.ts`) has per-SDK-package handlers:

| Handler | Package | Handles `apiKey` → `Authorization`? |
|---|---|---|
| `openai` | `@ai-sdk/openai` | ✅ Yes (creates Bearer header) |
| `openaiCompatible` | `@ai-sdk/openai-compatible` | ❌ No (passes through raw) |
| `anthropic` | `@ai-sdk/anthropic` | ✅ Yes (`x-api-key` header) |
| `google` | `@ai-sdk/google` | ✅ Yes (`x-goog-api-key` header) |

The `openaiCompatible` lowerer's `provider()` function does NOT convert `apiKey` to `Authorization: Bearer`. This means even if the API key flows through the config system, it won't be in the HTTP headers unless the AI SDK provider's constructor handles it.

**Fix**: In `openaiCompatible.provider()`, add the `Authorization` header:

```typescript
const openaiCompatible: Lowerer = {
  provider(options) {
    return {
      ...direct(options, ["baseURL", "apiKey"]),
      url: string(options.baseURL),
      headers: compact({
        Authorization: bearer(options.apiKey),
        ...headers(options.headers),
      }),
    }
  },
  request(options) { ... }
}
```

**Note**: The `provider()` function is apparently NOT called in practice — the code calls `lowerer.request()` instead. The actual API key flows to the AI SDK via the constructor options, not via the lowerer headers. This fix is defensive but may not be the primary path.

## Plugin Execution Order (Timing Trap)

Plugin effects run concurrently. The `load()` function in the opencode plugin runs BEFORE the config-provider plugin processes the user's config. This means:

1. `load()` runs first → no OAuth credential → `providers = undefined`
2. Config-provider plugin runs → sets `provider.options.apiKey` from user config
3. But `load()` doesn't re-run

The opencode plugin only re-fetches on `Integration.Event.ConnectionUpdated` events, not on config changes.

## Models.dev Catalog vs Remote Config

The models are sourced from TWO places:

1. **models.dev catalog** (`https://models.dev/api.json`) — provides model metadata (names, capabilities, costs) and the **Zen API endpoint**
2. **Remote config** (`{server}/api/config`) — provides the **Console API endpoint** and additional model configuration

Without the remote config (no OAuth), the models.dev catalog is used, which points to the wrong endpoint (Zen).

## Checklist for Fork Auth Fixes

When forking OpenCode as a standalone CLI:

- [ ] Override `model.api.url` for opencode provider models in `resolveSDK()` to use Console endpoint
- [ ] Ensure `provider.options.apiKey` from user config reaches the AI SDK constructor
- [ ] Fix `hasKey` check to also look at `provider.options.apiKey`
- [ ] Consider adding `apiKey` → `Authorization` header conversion in `openaiCompatible` lowerer
- [ ] Test with Bearer auth against console endpoint directly: `curl -H "Authorization: Bearer <key>" https://console.opencode.ai/inference/openai/v1/chat/completions`
- [ ] Test that no credential/OAuth is needed for the basic flow
- [ ] Handle the `@nectar/plugin` 404 from background dependency install by configuring `plugins: {}` in the default config or suppressing the warning
