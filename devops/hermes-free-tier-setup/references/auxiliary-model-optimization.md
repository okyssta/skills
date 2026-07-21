# Auxiliary Model Optimization — Task-Specific Model Selection

**Why each auxiliary task gets its own optimized free model instead of using the main model.**

---

## The Problem: Auxiliary Tasks Burn Primary Quota

Hermes runs 11 auxiliary tasks that can fire on every turn:
- Vision (image analysis)
- Compression (context summarization)
- Web Extract (page summarization)
- Title Generation (session titles)
- Approval (smart command approval)
- Skills Hub (skill search)
- MCP (tool routing)
- Triage Specifier (task expansion)
- Kanban Decomposer (task breakdown)
- Profile Describer (profile descriptions)
- Curator (skill review)

If all run on the main model (Nemotron 3 Ultra), you burn expensive reasoning tokens on tasks that don't need it. A 1M context model summarizing a 50K token page is wasteful.

---

## Optimization Strategy: Right Model for Right Task

| Task | Needs | Best Free Model | Why |
|------|-------|-----------------|-----|
| **Vision** | Multimodal (image+text) | Gemma 4 31B | Only free multimodal with 256K context, Apache 2.0 |
| **Compression** | Speed, not reasoning | GPT-OSS 20B | Fast MoE, 5.1B active, good summarization |
| **Web Extract** | Speed, not reasoning | GPT-OSS 20B | Same as compression — summarization doesn't need reasoning |
| **Title Gen** | Cheap, frequent, fast | Gemma 4 26B MoE | 3.8B active, MoE efficiency, 256K context |
| **Approval** | Reasoning, not speed | Nemotron Nano 30B | 3B active MoE, good judgment at low cost |
| **Skills Hub** | Lightweight | Auto → GPT-OSS 20B | Rare, light queries |
| **MCP** | Lightweight | Auto → GPT-OSS 20B | Rare, light queries |
| **Triage Spec** | Reasoning | Nemotron Nano 30B | Needs to expand specs intelligently |
| **Kanban Decomp** | Strong reasoning | Nemotron 3 Super | Complex task breakdown needs reasoning |
| **Profile Describer** | Cheap, fast | Gemma 4 26B MoE | Short output, frequent |
| **Curator** | Can run long | GPT-OSS 20B | Reviews skills, can take minutes — use cheap model |

---

## Fallback Chain Design for Auxiliary Tasks

Each task has a task-specific `fallback_chain` that tries:
1. **Task-specialized model** (e.g., vision → multimodal models)
2. **Shared fallback_providers chain** (the 20-layer main chain)
3. **Built-in auxiliary discovery** (OpenRouter → Nous → Custom → Codex → etc.)

### Vision Fallback Chain
```
Gemma 4 31B (primary, multimodal)
    ↓
Gemini 2.5 Flash (multimodal, 1M context)
    ↓
Nemotron 3 Nano Omni (multimodal, 30B-A3B)
    ↓
Big Pickle (OpenCode Zen, unknown capabilities)
    ↓
NovitaAI Gemma 4 31B (different provider)
    ↓
→ fallback_providers chain
```

### Compression/Web Extract Fallback Chain
```
GPT-OSS 20B (fast MoE)
    ↓
Nemotron 3 Nano 30B (3B active MoE)
    ↓
Nemotron Nano 9B (smallest Nemotron)
    ↓
Groq Llama 3.1 8B Instant (320 tok/s)
    ↓
Gemini 2.5 Flash Lite (cheap, fast)
    ↓
OpenCode Zen DeepSeek V4 Flash Free
    ↓
NovitaAI Gemma 4 26B
    ↓
→ fallback_providers chain
```

### Title Generation Fallback Chain
```
Gemma 4 26B MoE (MoE efficiency)
    ↓
Ring 2.6 (small, fast)
    ↓
Nemotron 3 Nano 30B
    ↓
Groq Llama 3.1 8B Instant
    ↓
OpenCode Zen North Mini Code Free
    ↓
NovitaAI Gemma 4 26B
    ↓
→ fallback_providers chain
```

---

## Cost Savings Calculation

Assuming typical agent session:
- 10 user turns
- 3 vision calls (screenshots)
- 5 compression calls (context > 50%)
- 2 web extracts
- 10 title generations
- 5 approval checks

**Using main model (Nemotron 3 Ultra) for all:**
- ~500K tokens on primary model per session
- At 200 req/day OpenRouter limit → ~0.4 sessions/day

**Using optimized auxiliary models:**
- Vision: Gemma 4 31B (free, separate quota)
- Compression: GPT-OSS 20B (free, separate quota)
- Web Extract: GPT-OSS 20B (free, separate quota)
- Title Gen: Gemma 4 26B (free, separate quota)
- Approval: Nemotron Nano 30B (free, separate quota)
- Primary model only for: main reasoning, Kanban, Triage, Curator
- ~50K tokens on primary model per session
- At 200 req/day → ~4 sessions/day (**10x improvement**)

---

## Configuration Pattern

```yaml
auxiliary:
  vision:
    provider: openrouter
    model: google/gemma-4-31b-it:free
    fallback_chain:
      - provider: gemini
        model: gemini-2.5-flash
      - provider: openrouter
        model: nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free
      - provider: openrouter
        model: google/gemma-4-26b-a4b-it:free

  compression:
    provider: openrouter
    model: openai/gpt-oss-20b:free
    fallback_chain:
      - provider: openrouter
        model: nvidia/nemotron-3-nano-30b-a3b:free
      - provider: groq
        model: llama-3.1-8b-instant
```

**Key settings per task:**
- `timeout` — Vision/compression need longer (120s/60s), titles need short (30s)
- `download_timeout` — Vision needs image download time (30s)
- `fallback_chain` — Task-specific before shared chain

---

## Monitoring Auxiliary Usage

```bash
# Check which auxiliary models are actually running
hermes dashboard → Models page → Usage analytics

# Look for:
# - aux · vision → google/gemma-4-31b-it:free
# - aux · compression → openai/gpt-oss-20b:free
# - aux · title_generation → google/gemma-4-26b-a4b-it:free
```

If you see `aux · vision → nvidia/nemotron-3-ultra-550b-a55b:free`, the override didn't apply — check config syntax.

---

## When to Override vs Use Auto

| Scenario | Action |
|----------|--------|
| Main model lacks capability (no vision) | **Must override** — vision on auto will fail |
| Main model is expensive reasoning model | **Should override** — save quota |
| Main model is already cheap/fast (e.g., Groq 8B) | **Auto is fine** — no savings from override |
| Task is rare (Skills Hub, MCP) | **Auto is fine** — minimal impact |
| Task is frequent (Title Gen, Compression) | **Must override** — biggest savings |

---

## OpenCode Zen Auxiliary Models

OpenCode Zen free models can serve auxiliary tasks:
- **Big Pickle** — Vision fallback (unknown multimodal capability)
- **DeepSeek V4 Flash Free** — Compression/web extract (fast)
- **North Mini Code Free** — Title gen/approval (coding-optimized)
- **Nemotron 3 Ultra Free** — Kanban decomposer (reasoning)

Add to `fallback_chain` for each task as shown in config template.