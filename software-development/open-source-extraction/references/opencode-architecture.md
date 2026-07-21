# OpenCode Codebase Architecture (for Forking)

**Covers:** Package layout, free model pipeline, provider integration, CLI build, key overrides.

**Source:** anomalyco/opencode (MIT, TypeScript monorepo, Bun-based)

---

## Package Hierarchy

```
opencode/ (main binary)
├── bin/opencode               ← Shell wrapper: finds compiled binary, spawns it
├── src/index.ts               ← CLI entry point (yargs), commands: run, serve, auth, etc.
├── src/provider/provider.ts   ← THE engine — 1981 lines, manages ALL providers + models
├── src/provider/model-status.ts
├── src/session/                ← Agent session orchestration
├── src/cli/cmd/run.ts         ← "opencode run" command
├── src/cli/cmd/run/footer.command.tsx  ← Model selector UI showing "Free" badge
├── src/cli/cmd/providers.ts   ← Provider auth flows (OAuth, API key)
├── src/session/retry.ts       ← Rate limit / free tier error handling
├── src/session/llm/           ← LLM request routing (AI SDK vs native)
├── src/server/                ← HTTP API server + WebSocket
├── src/plugin/                ← Plugin system for providers, auth, tools
├── src/mcp/                   ← MCP integration
├── src/tool/                  ← Built-in tools (grep, read, code-mode, etc.)

@opencode-ai/core             ← Agent engine
├── src/models-dev.ts          ← Models.dev catalog fetcher + cache manager
├── src/provider/              ← Provider / Model V2 schemas
├── src/database/              ← SQLite (Bun/Node)
├── src/pty/                   ← PTY (Bun/Node)
├── src/session/               ← Session management
├── src/effect/                ← Effect-ts layer composition
├── src/installation/version.ts
└── src/global.ts              ← Cache paths (~/.cache/nectar/)

@opencode-ai/tui               ← Terminal UI (Ink/React-for-terminal)
└── src/app.tsx                ← TUI app shell

@opencode-ai/llm               ← LLM provider definitions (low-level)
├── src/providers/             ← Provider facades
│   ├── openai-compatible.ts   ← Generic + family providers (Groq, DeepSeek, etc.)
│   ├── openai-compatible-profile.ts  ← Provider profiles (base URLs)
│   ├── openrouter.ts          ← OpenRouter custom adapter
│   ├── anthropic.ts
│   ├── google.ts
│   ├── openai.ts
│   └── ...
├── src/protocols/             ← Protocol adapters (OpenAI chat, Anthropic, Gemini, etc.)
│   ├── openai-compatible-chat.ts
│   ├── anthropic-messages.ts
│   └── gemini.ts
└── src/route/                 ← Route composition (protocol + endpoint + auth + framing)

@opencode-ai/sdk               ← API client SDK (for tools/clients to connect)

@opencode-ai/schema            ← Wire/storage schemas

@opencode-ai/plugin            ← Plugin API types
```

---

## Free Model Pipeline (The Core Feature)

```
1. CLI starts
       │
2. ModelsDev.Service.get()           ← Fetches https://models.dev/api.json
       │                                (cached to ~/.cache/nectar/models.json, 5m TTL)
       │                                Returns Record<providerID, Provider>
       ▼
3. provider.ts: layer()              ← Builds provider registry from catalog
       │
       ├── Merge config providers    ← cfg.provider from local config
       ├── Load env API keys          ← GROQ_API_KEY, MISTRAL_API_KEY, etc.
       ├── Load saved auths           ← From auth store
       │
       ├── Run custom(dep) functions  ← Provider-specific loaders
       │    │
       │    ├── nectar()              ← KEY: checks for Nectar API key
       │    │   ├── Has key?  → keep all models (paid + free)
       │    │   └── No key?   → DELETE models where cost.input > 0
       │    │                     Keep only cost=0 models (FREE)
       │    │
       │    ├── nvidia()              ← Sets Nectar headers
       │    ├── openrouter()          ← Sets Nectar referrer headers
       │    └── ...other providers...
       │
       ▼
4. UI shows model selector    ← footer.command.tsx
       │    model.cost?.input === 0 && provider.id === "nectar" → "Free" badge
       │
       ▼
5. User selects model → Direct API call via @ai-sdk/* ← No proxy
```

### Key Files for the Pipeline

| File | What It Does |
|------|-------------|
| `packages/core/src/models-dev.ts` | Fetches `https://models.dev/api.json`, caches locally, refreshes every 60m. Overridable with `OPENCODE_MODELS_URL`, `OPENCODE_MODELS_PATH` env vars. |
| `packages/opencode/src/provider/provider.ts` | The 1981-line god file. Builds provider registry, runs custom loaders, manages model lifecycle. |
| `packages/opencode/src/provider/provider.ts` lines 179-201 | **Nectar provider** — the free model gate. No API key? Deletes non-zero-cost models. |
| `packages/opencode/src/cli/cmd/run/footer.command.tsx` lines 963 | UI shows "Free" tag: `model.cost?.input === 0 && provider.id === "nectar"` |
| `packages/opencode/src/session/retry.ts` | Handles `FreeUsageLimitError` and `GoUsageLimitError` from Nectar backend. "Subscribe to Go" upsell. |

### The models.dev Catalog

The catalog at `https://models.dev/api.json` returns a JSON blob of shape:

```typescript
Record<string, {
  id: string
  name: string
  api?: string
  npm?: string
  env: string[]               // Env vars to check for API keys
  models: Record<string, {   // Model definitions
    id: string
    name: string
    cost?: { input: number, output: number, cache_read?: number, cache_write?: number }
    limit: { context: number, output: number }
    status?: "alpha" | "beta" | "deprecated"
    // ...capabilities, modalities, etc.
  }>
}>
```

Models with `cost: { input: 0, output: 0 }` are FREE. Models with cost > 0 are PAID and require a Nectar API key.

**You can override the catalog with:**
- `OPENCODE_MODELS_URL` — point to your own catalog API
- `OPENCODE_MODELS_PATH` — point to a local JSON file (bundle with binary)
- `OPENCODE_DISABLE_MODELS_FETCH=true` — skip remote fetch entirely

---

## Provider Integration System

### Bundled AI SDK Providers (provider.ts lines 107-134)

All are lazily imported via dynamic `import()`:

```
@ai-sdk/amazon-bedrock       @ai-sdk/anthropic
@ai-sdk/azure                @ai-sdk/google
@ai-sdk/google-vertex        @ai-sdk/openai
@ai-sdk/openai-compatible    @ai-sdk/mistral
@ai-sdk/groq                 @ai-sdk/xai
@ai-sdk/deepinfra            @ai-sdk/cerebras
@ai-sdk/cohere               @ai-sdk/togetherai
@ai-sdk/perplexity           @ai-sdk/vercel
@ai-sdk/alibaba              @ai-sdk/gateway
@openrouter/ai-sdk-provider  venice-ai-sdk-provider
gitlab-ai-provider           @ai-sdk/github-copilot
@ai-sdk/google-vertex/anthropic
@ai-sdk/amazon-bedrock/mantle
```

### OpenAI-Compatible Family (openai-compatible-profile.ts)

These use the `@ai-sdk/openai-compatible` adapter with a base URL and provider name:

```typescript
baseten:    https://inference.baseten.co/v1
cerebras:   https://api.cerebras.ai/v1
deepinfra:  https://api.deepinfra.com/v1/openai
deepseek:   https://api.deepseek.com/v1
fireworks:  https://api.fireworks.ai/inference/v1
groq:       https://api.groq.com/openai/v1
openrouter: https://openrouter.ai/api/v1
togetherai: https://api.together.xyz/v1
xai:        https://api.x.ai/v1
```

### Custom Provider Loaders (provider.ts lines 168-478)

Each provider can have a custom loader function that returns:
- `autoload: boolean` — whether to load even without an API key
- `options` — SDK options (headers, region, etc.)
- `getModel` — custom model selection logic
- `vars` — env vars to provide
- `discoverModels` — dynamic model discovery

The `nectar` provider (lines 179-201) is the most important custom loader — it's the free model gate.

---

## CLI Binary Build

The CLI is compiled as a **single static binary** using `bun build --compile`:

```
packages/opencode/script/build.ts
    │
    ├── Creates embedded Web UI bundle (packages/app/dist → embedded as imports)
    ├── bun build --compile ./src/index.ts  →  opencode-linux-x64
    └── Outputs platform-specific binaries: opencode-<os>-<arch>[-musl][-baseline]
```

The shell wrapper (`packages/opencode/bin/opencode`) finds the binary in `node_modules/` and spawns it. It detects:
- Platform (linux/darwin/windows)
- Architecture (x64/arm64)
- AVX2 support (for x86_64 baseline variant selection)
- musl libc (Alpine Linux)

### For a Fork

Replace the `bin/opencode` wrapper's binary name resolution. The build script at `script/build.ts` compiles against `./src/index.ts`. The imports system (`exports`/`imports` in package.json) handles Bun/Node dual platform paths via the `#imports` map.

---

## Key Env Vars / Override Flags

| Env / Flag | Effect |
|-----------|--------|
| `OPENCODE_MODELS_URL` | Override models.dev API URL |
| `OPENCODE_MODELS_PATH` | Load model catalog from local JSON file |
| `OPENCODE_DISABLE_MODELS_FETCH` | Skip remote models.dev fetch (use bundled/snapshot only) |
| `OPENCODE_BIN_PATH` | Force specific binary path |
| `OPENCODE_PURE` | Run without external plugins |
| `OPENCODE_PRINT_LOGS` | Print logs to stderr |
| `OPENCODE_LOG_LEVEL` | Log level (DEBUG/INFO/WARN/ERROR) |
| `OPENCODE_CHANNEL` | Installation channel (affects user agent) |
| `AGENT` / `OPENCODE` | Set by CLI at startup |
| `GROQ_API_KEY` | Groq provider |
| `MISTRAL_API_KEY` | Mistral provider |
| `OPENROUTER_API_KEY` | OpenRouter provider |
| `NVIDIA_API_KEY` | NVIDIA NIM provider |
| `DEEPSEEK_API_KEY` | DeepSeek provider |
| `GOOGLE_API_KEY` | Google Gemini provider |

---

## Free Tier / Go Subscription Enforcement

In `packages/opencode/src/session/retry.ts`:

```typescript
export const GO_UPSELL_MESSAGE = "Free usage exceeded, subscribe to Go"
export const GO_UPSELL_URL = "https://nectar.ai/go"
```

When the Nectar backend returns a `FreeUsageLimitError`, the CLI shows:
- Title: "Free limit reached"
- Message: "Subscribe to Nectar Go for reliable access to the best open-source models, starting at $5/month."
- Label: "subscribe" with link to nectar.ai/go

When a `GoUsageLimitError` is returned (paid plan hit its cap), it shows:
- Rate limit details with reset timer
- Link to workspace settings to enable usage from balance

The retry system handles:
- `FreeUsageLimitError` → upsell to Go subscription
- `GoUsageLimitError` → show cap details with reset timer
- `429` rate limits → exponential backoff
- `5xx` server errors → retry with backoff
- Context overflow → no retry (user must start new session)

---

## Nectar-Specific Configuration (Already in the Code)

The codebase is already configured with Nectar branding in several places:

```typescript
// provider.ts - Nectar custom provider (line 179)
nectar: Effect.fnUntraced(function* (input: Info) { ... })

// provider.ts - OpenRouter headers (line 458)
"HTTP-Referer": "https://nectar.ai/"
"X-Title": "nectar"

// provider.ts - NVIDIA headers (line 468)
"HTTP-Referer": "https://nectar.ai/"
"X-Title": "nectar"
"X-BILLING-INVOKE-ORIGIN": "Nectar"

// provider.ts - Vercel headers (line 479)
"http-referer": "https://nectar.ai/"
"x-title": "nectar"

// models-dev.ts - User agent (line 18)
USER_AGENT = `nectar/${InstallationChannel}/${InstallationVersion}/${Flag.OPENCODE_CLIENT}`

// model loaded layer class @nectar/ModelsDev (line 121)
class Service extends Context.Service<Service, Interface>()("@nectar/ModelsDev") {}
```

---

## For a Fork: What to Change

| What | Where | How |
|------|-------|-----|
| **CLI name** | `src/index.ts` | Change `scriptName("nectar")` |
| **Model catalog** | `packages/core/src/models-dev.ts` | Change `source = Flag.OPENCODE_MODELS_URL` default |
| **Free model catalog** | Bundle a local JSON | Set `OPENCODE_MODELS_PATH` at compile time |
| **Nectar provider behavior** | `provider.ts` nectar() loader | Change API key check, default free models |
| **Go subscription URLs** | `retry.ts` | Change `GO_UPSELL_URL` |
| **Cache paths** | `packages/core/src/global.ts` | Change `~/.cache/nectar/` |
| **Headers** | `provider.ts` custom loaders | Change nectar.ai references |
| **Binary name** | `bin/opencode` + `script/build.ts` | Change binary naming |
| **Package names** | All `package.json` | Change `@opencode-ai/*` → `@yourbrand/*` (careful: breaks workspace resolution) |
| **Icons/Theme** | `packages/app/src/asset/` | Replace SVG logos |

The easiest first step: set `OPENCODE_MODELS_PATH` to a bundled JSON file with only free models, and leave models.dev entirely optional.
