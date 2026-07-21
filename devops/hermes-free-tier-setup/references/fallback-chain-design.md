# Fallback Chain Design — Reasoning & Architecture

**Why 20 layers? How the order was determined.**

---

## Design Principles

1. **Preserve reasoning quality** — Fallback order degrades gracefully from best reasoning to acceptable
2. **Diversify failure modes** — Different providers fail differently (rate limits vs outages vs auth)
3. **Specialization per layer** — Each fallback adds a capability (speed, coding, context, local)
4. **Local last resort** — Zero-cost unlimited fallback that never fails due to API issues
5. **Auxiliary-aware** — Fallback chain also serves auxiliary tasks on `auto`

---

## Layer-by-Layer Rationale

### Layer 1-2: OpenRouter Nemotron Family (Best Reasoning)
- **Nemotron 3 Ultra** (550B MoE) — Best free model overall, 1M context, excels at orchestration
- **Nemotron 3 Super** (120B MoE) — 12B active, same 1M context, faster, 50% more tokens
- *Why first:* Highest quality reasoning, same provider (OpenRouter), seamless switch

### Layer 3: Groq Llama 3.3 70B (Speed Specialist)
- 320 tok/s on LPU hardware
- 1K req/day, 500K token budget
- *Why third:* Different infrastructure (LPU), fails independently of OpenRouter
- *Tradeoff:* Shorter context (128K), token budget binds before request limit

### Layer 4: Poolside Laguna M.1 (Coding Specialist)
- Best free coding agent model
- 256K context, tool calling optimized
- *Why fourth:* Specialized capability for coding tasks when primary fails

### Layer 5: Google Gemini 2.5 Flash (Long Context)
- 1M context window
- 1,500 RPD (generous)
- *Why fifth:* Different provider (Google), 1M context for large document tasks
- *Caveat:* API key method only (OAuth banned for third-party)

### Layer 6: Local Ollama Qwen3.5 27B (Unlimited Zero-Cost)
- No rate limits, no API keys, no network dependency
- 128K context (configurable)
- *Why sixth:* Ultimate fallback — works when all cloud APIs fail
- *Requirement:* 16GB VRAM, hardware dependent

### Layer 7-10: OpenRouter Specialized Free Models
- **Cohere North Mini Code** — 3B active, coding specialist
- **Gemma 4 31B** — Multimodal (vision fallback)
- **GPT-OSS 120B** — OpenAI's open MoE, different architecture
- **Laguna XS 2.1** — Fast coding, FP8 quantized
- *Why 7-10:* Same provider (OpenRouter), different model families, no new credentials needed

### Layer 11: NVIDIA NIM (Direct NVIDIA)
- Nemotron 3 Ultra direct from NVIDIA
- Free credits, 40 RPM
- *Why eleventh:* Different endpoint, credits don't expire

### Layer 12: OpenCode Zen (5 Free Coding Models)
- MiMo-V2.5, North Mini Code, Nemotron 3 Ultra, Big Pickle, DeepSeek V4 Flash
- Unlimited during free period
- *Why twelfth:* Curated coding models, different routing

### Layer 13: NovitaAI (Cost-Efficient)
- Gemma 4 31B, 262K context
- Free credits on signup
- *Why thirteenth:* Different provider, good pricing if scaling

### Layer 14: Hugging Face (Community Models)
- Llama 3.3 70B via Inference Providers
- Monthly free credits
- *Why fourteenth:* Access to niche/small models

### Layer 15: GitHub Models (Frontier Access)
- GPT-4o, Claude 3.5 Sonnet, Llama, Phi
- 150-1K/day via GitHub token
- *Why fifteenth:* Frontier models for free (limited)

### Layer 16: Cloudflare Workers AI (Edge)
- Llama 3.3 70B at edge
- 10K neurons/day
- *Why sixteenth:* Edge deployment, different infrastructure

### Layer 17: Kimi/Moonshot (Long Context Specialist)
- 128K+ context free tier
- *Why seventeenth:* Long context alternative to Gemini

---

## Cross-Provider Failure Independence

| Failure Mode | OpenRouter | Groq | Google | NVIDIA | Local |
|--------------|------------|------|--------|--------|-------|
| Rate limit | ✓ | ✓ | ✓ | ✓ | Never |
| Provider outage | ✓ | ✓ | ✓ | ✓ | Never |
| Auth failure | ✓ | ✓ | ✓ | ✓ | Never |
| Model deprecation | ✓ | ✓ | ✓ | ✓ | Never |
| Network partition | ✓ | ✓ | ✓ | ✓ | Never |

**Key insight:** Each provider has independent infrastructure. A Groq outage doesn't affect OpenRouter. Local never fails due to external issues.

---

## Auxiliary Task Fallback Integration

When auxiliary tasks run on `provider: auto`, they follow:
```
Main provider + main model → auxiliary.<task>.fallback_chain →
fallback_providers / fallback_model → built-in auxiliary discovery chain
```

The 20-layer `fallback_providers` chain serves as the shared fallback for all auxiliary tasks on `auto`. This means:
- Vision fails on Gemma 4 31B → tries Nemotron Nano Omni → then falls to fallback_providers chain
- Compression fails on GPT-OSS 20B → tries Nemotron Nano → then falls to fallback_providers chain

**Design decision:** Per-task `fallback_chain` handles task-specific fallbacks first (e.g., vision → multimodal models), then the shared chain catches everything else.

---

## Key Stacking vs Fallback Chain

| Aspect | Credential Pools (Key Stacking) | Fallback Chain |
|--------|--------------------------------|----------------|
| Purpose | Multiply same-provider quota | Switch to different provider/model |
| Trigger | Same-provider rate limit (429) | Any provider error (429, 500, 401, 404) |
| Config | `credential_pools` in config.yaml | `fallback_providers` in config.yaml |
| Order | Round-robin / sequential | Explicit priority order |
| Independence | Same provider, different keys | Different providers entirely |

**Both work together:** Key stacking extends each layer's capacity. Fallback chain moves to next layer when a layer is exhausted.

---

## Monitoring & Alerting

Track these metrics to know when fallback activates:
- `hermes doctor` — shows provider connectivity
- Dashboard Usage analytics — shows which models actually ran
- Rate limit headers in API responses — `x-ratelimit-remaining-requests`
- Log messages — "Fallback activated: openrouter → groq"

---

## Maintenance Schedule

- **Monthly:** Check OpenRouter free model list (models rotate)
- **Quarterly:** Verify all provider free tiers still active
- **On fallback activation:** Investigate why primary failed (rate limit? outage? model deprecated?)
- **When adding keys:** Update `credential_pools` and test rotation