# OpenCode CLI Architecture — Model System

When you extract OpenCode's codebase (MIT, `anomalyco/opencode`) into a standalone project like `nectar-v2/`, understanding its model system is essential for customizing free-tier vs paid-tier access.

## Architecture Overview

```
User runs "opencode"
        │
        ▼
src/index.ts  →  yargs CLI (scriptName "nectar")
        │
        ▼
Provider layer loads models from catalog
        │
        ├── https://models.dev/api.json  ← REMOTE catalog (all models + prices)
        │   └── Cached locally at ~/.cache/nectar/models.json (5min TTL)
        │
        └── OPENCODE_MODELS_PATH env var  ← LOCAL snapshot (bundled JSON)
        │
        ▼
Each provider's custom() loader runs (provider.ts lines 168-500+)
        │
        ├── "nectar" provider  ← THE KEY: checks for API key
        │   ├── Has key → All models available
        │   └── No key → Deletes models with cost.input > 0 (free only)
        │
        ├── "openrouter" — sets HTTP-Referer/X-Title headers → "https://nectar.ai/"
        ├── "nvidia" — sets bill-invoke-origin, referrer headers
        ├── "llmgateway" — referrer headers
        └── (all bundled SDK providers)
        │
        ▼
AI SDK abstraction (@ai-sdk/*)  →  actual API calls
```

## models.dev Catalog

The catalog at `https://models.dev/api.json` returns:

```ts
Record<string, Provider>

interface Provider {
  id: string
  name: string
  env: string[]          // env var names for API keys
  npm?: string           // npm package for the AI SDK provider
  models: Record<string, Model>
}

interface Model {
  id: string
  name: string
  cost?: { input: number; output: number; cache_read?: number; cache_write?: number }
  limit: { context: number; input?: number; output: number }
  status?: "alpha" | "beta" | "deprecated"
  // plus capabilities, modalities, etc.
}
```

**Key fact:** A model is "free" when `cost.input === 0`. The SaaS provider (nectar.ai) defines this in their models.dev catalog.

The CLI fetches this from `source = Flag.OPENCODE_MODELS_URL || "https://models.dev"` via `GET {source}/api.json`. Cache TTL is 5 minutes with a background refresh every 60 minutes.

## The "nectar" Provider — Free Model Gate (provider.ts)

Located in `packages/opencode/src/provider/provider.ts`, lines 179-201:

```ts
nectar: Effect.fnUntraced(function* (input: Info) {
  const env = yield* dep.env()
  const hasKey = iife(() => {
    if (input.env.some((item) => env[item])) return true
    return false
  })
  const ok =
    hasKey ||
    Boolean(yield* dep.auth(input.id)) ||
    Boolean((yield* dep.config()).provider?.["nectar"]?.options?.apiKey)

  if (!ok) {
    for (const [key, value] of Object.entries(input.models)) {
      if (value.cost.input === 0) continue   // ← KEEP free models
      delete input.models[key]                // ← DELETE paid models
    }
  }

  return {
    autoload: Object.keys(input.models).length > 0,
    options: ok ? {} : { apiKey: *** },
  }
}),
```

**What this means:** When a user has no Nectar API key configured, only models with `cost.input === 0` survive. The CLI still loads, still works — just with free models only. This is the entitlement mechanism.

## How the UI Shows "Free" (footer.command.tsx)

```tsx
// Line 963
model.cost?.input === 0 && provider.id === "nectar"
    ? "Free"   // ← "Free" badge in model selector
    : ...
```

Models from the `nectar` provider with `cost.input === 0` get a "Free" label. Model sorting also prioritizes `nectar` provider models first (lines 980-984).

## Bundled AI SDK Providers (provider.ts lines 107-134)

These are dynamically imported at runtime:

| NPM Package | Provider |
|-------------|----------|
| `@ai-sdk/amazon-bedrock` | AWS Bedrock |
| `@ai-sdk/anthropic` | Anthropic (Claude) |
| `@ai-sdk/azure` | Azure OpenAI |
| `@ai-sdk/google` | Google Gemini |
| `@ai-sdk/google-vertex` | Google Vertex AI |
| `@ai-sdk/openai` | OpenAI |
| `@ai-sdk/openai-compatible` | Generic OpenAI-compatible |
| `@ai-sdk/mistral` | Mistral |
| `@ai-sdk/groq` | Groq |
| `@ai-sdk/deepinfra` | DeepInfra |
| `@ai-sdk/cerebras` | Cerebras |
| `@ai-sdk/cohere` | Cohere |
| `@ai-sdk/togetherai` | TogetherAI |
| `@ai-sdk/perplexity` | Perplexity |
| `@ai-sdk/xai` | xAI (Grok) |
| `@ai-sdk/vercel` | Vercel |
| `@openrouter/ai-sdk-provider` | OpenRouter |
| `venice-ai-sdk-provider` | Venice |
| `gitlab-ai-provider` | GitLab |
| `@ai-sdk/github-copilot` | GitHub Copilot |
| `@ai-sdk/gateway` | AI Gateway |
| `@ai-sdk/alibaba` | Alibaba (Qwen) |

**For a rebranded CLI:** You don't need to change these — they're already working. You just need to either (a) host your own models.dev catalog, or (b) bundle a local snapshot via `OPENCODE_MODELS_PATH`.

## OpenAI-Compatible Provider Profiles (openai-compatible-profile.ts)

Pre-configured provider endpoints for OpenAI-compatible APIs:

```ts
export const profiles = {
  baseten:     { baseURL: "https://inference.baseten.co/v1" },
  cerebras:    { baseURL: "https://api.cerebras.ai/v1" },
  deepinfra:   { baseURL: "https://api.deepinfra.com/v1/openai" },
  deepseek:    { baseURL: "https://api.deepseek.com/v1" },
  fireworks:   { baseURL: "https://api.fireworks.ai/inference/v1" },
  groq:        { baseURL: "https://api.groq.com/openai/v1" },
  openrouter:  { baseURL: "https://openrouter.ai/api/v1" },
  togetherai:  { baseURL: "https://api.together.xyz/v1" },
  xai:         { baseURL: "https://api.x.ai/v1" },
}
```

Each is exported as a ready-to-use provider facade: `OpenAICompatible.groq.model(...)`, `OpenAICompatible.deepseek.model(...)`, etc.

## CLI Binary Pipeline

```
src/index.ts  →  yargs CLI entry point
       │
bun run script/build.ts  →  bun build --compile
       │
       ▼
Static binary: opencode-linux-x64, opencode-darwin-arm64, etc.
       │
       ▼
bin/opencode  →  Shell wrapper that locates + spawns the compiled binary
                 from node_modules/<platform-package>/bin/opencode
```

The build script (packages/opencode/script/build.ts) uses `bun build --compile` with:
- `createSolidTransformPlugin()` for JSX in terminal
- Embedded Web UI bundle (packages/app/dist)
- Multi-platform targets (linux x64/arm64, darwin x64/arm64, windows x64)

## Environment Flags

| Flag | Effect |
|------|--------|
| `OPENCODE_MODELS_URL` | Override models.dev API URL |
| `OPENCODE_MODELS_PATH` | Load models from local JSON file |
| `OPENCODE_DISABLE_MODELS_FETCH` | Skip remote fetch entirely |
| `OPENCODE_PURE` | Run without external plugins |
| `OPENCODE_PRINT_LOGS` | Print logs to stderr |
| `OPENCODE_LOG_LEVEL` | Log level (DEBUG/INFO/WARN/ERROR) |
| `AGENT=1` | Set by CLI middleware |
| `OPENCODE=1` | Set by CLI middleware |
| `OPENCODE_PID` | Process PID |

## Already Rebranded as "nectar"

The extracted `nectar-v2/` codebase is already rebranded from "opencode" to "nectar":

- `src/index.ts`: `scriptName("nectar")`
- UI logo references: `"nectar "` prefix check
- Cache path: `~/.cache/nectar/models.json`
- HTTP headers: `"HTTP-Referer": "https://nectar.ai/"`, `"X-Title": "nectar"`
- Models.dev service: `USER_AGENT = "nectar/${InstallationChannel}/..."`, `Service class: "@nectar/ModelsDev"`
- i18n strings: "Free models provided by Nectar"

## Rebundling Free Models for Your Own CLI

Option A — **Host your own models.dev**: Set `OPENCODE_MODELS_URL` to your API. Define providers + models with `cost.input: 0` for free models. The native nectar provider logic handles the rest.

Option B — **Bundle a local snapshot**: Set `OPENCODE_MODELS_PATH` to a JSON file with your catalog. The CLI loads from disk and never fetches remote. Use `OPENCODE_DISABLE_MODELS_FETCH=true` to prevent accidental remote calls.

Option C — **Use the existing models.dev**: The extracted code already points to `https://models.dev` (nectar.ai's catalog). Free models defined there will work out of the box. Paid models require a nectar.ai API key configured by the user.

## Retry / Free Tier Upsell (session/retry.ts)

When a user without a subscription hits a cap or rate limit, the error handling shows an upsell:

- `FreeUsageLimitError` → "Free usage exceeded, subscribe to Go" → links to `https://nectar.ai/go`
- `GoUsageLimitError` → "Go limit reached" → links to workspace settings page
- `GO_UPSELL_URL = "https://nectar.ai/go"`

These URLs are in the source and should be changed for a rebranded CLI.

## Key Files Summary

| File | Purpose |
|------|---------|
| `packages/opencode/src/index.ts` | CLI entry point (yargs) |
| `packages/opencode/src/provider/provider.ts` | All provider/model loading, auth, free gate |
| `packages/opencode/src/provider/model-status.ts` | Model status schema |
| `packages/opencode/src/cli/cmd/run/footer.command.tsx` | Model selector UI, "Free" badge |
| `packages/opencode/src/session/retry.ts` | Free tier limits, upsell messaging |
| `packages/opencode/script/build.ts` | Build pipeline (Bun compile) |
| `packages/opencode/bin/opencode` | Shell wrapper launcher |
| `packages/core/src/models-dev.ts` | models.dev catalog fetcher + cache |
| `packages/llm/src/providers/` | Low-level provider implementations |
| `packages/llm/src/providers/openai-compatible-profile.ts` | Pre-configured provider endpoints |
