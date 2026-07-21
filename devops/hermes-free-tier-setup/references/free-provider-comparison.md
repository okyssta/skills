# Free Provider Comparison — Detailed Reference

**Last Updated: July 2026** — Based on OpenRouter blog, cheahjs/free-llm-api-resources, provider docs

---

## Provider Quick Reference

| Provider | Free Models | RPM | RPD/Monthly | Context | Credit Card | Data Training | Best For |
|----------|-------------|-----|-------------|---------|-------------|---------------|----------|
| **OpenRouter** | 29+ (`:free`) | 20 | 50/day (1K*) | 1M | No | No | Variety, routing |
| **Groq** | Llama 3.3 70B, Gemma 2 9B, etc. | 30 | 1,000/day | 128K | No | No | Speed (320 tok/s) |
| **Google AI Studio** | Gemini 2.5 Flash, Flash-Lite | 15 | 1,500/day | 1M | No | Yes (ex-EU) | Long context |
| **NVIDIA NIM** | Nemotron, Llama variants | 40 | Free credits | 128K | No | No | Experimentation |
| **OpenCode Zen** | 5 free models | N/A | Unlimited* | Varies | No | Some models | Coding models |
| **NovitaAI** | 200+ models | N/A | Free credits | 262K | No | No | Cost-efficient |
| **Hugging Face** | 100K+ OSS | Var | Monthly creds | Model | No | No | Niche models |
| **GitHub Models** | GPT-4o, Claude 3.5, Llama, Phi | 15 | 150-1K/day | 128K | No | No | Frontier access |
| **Cloudflare Workers AI** | 20+ models | High | 10K neurons | 8K | No | No | Edge deployment |
| **Cohere** | Command R+ | 10-20 | ~100/day | 128K | No | No (non-comm) | RAG prototyping |
| **Mistral** | Codestral, Small/Large | Var | 1B tokens/mo | 256K | No | Yes (Exp tier) | High volume coding |
| **Cerebras** | Llama 3.3 70B | 30 | 1M tokens/day | 1M | No | No | Batch throughput |
| **Ollama (Local)** | Any model | ∞ | ∞ | 128K+ | N/A | N/A | Zero cost, privacy |

* OpenRouter: 1,000/day with $10 lifetime top-up
* OpenCode Zen: Free models during "limited time" period only

---

## Top Free Models by Category (July 2026)

### Reasoning / Orchestration
1. **NVIDIA Nemotron 3 Ultra** (OpenRouter/OpenCode Zen) — 550B MoE, 1M context, best overall
2. **NVIDIA Nemotron 3 Super** (OpenRouter) — 120B MoE, 12B active, 1M context
3. **OpenAI gpt-oss-120b** (OpenRouter) — 117B MoE, 5.1B active, 131K context

### Speed
1. **Llama 3.3 70B** (Groq) — 320 tok/s on LPU
2. **Llama 3.1 8B Instant** (Groq) — Fastest small model
3. **GPT-OSS 20B** (OpenRouter) — Fast MoE for auxiliary tasks

### Coding
1. **Poolside Laguna M.1** (OpenRouter) — Flagship coding agent, 256K context
2. **Poolside Laguna XS 2.1** (OpenRouter) — 33B-A3B, FP8 quant
3. **Cohere North Mini Code** (OpenRouter/OpenCode Zen) — 3B active, 256K
4. **OpenCode Zen MiMo-V2.5** — Coding optimized
5. **Qwen3.5 27B** (Ollama/NovitaAI) — Strong tool calling

### Long Context
1. **Gemini 2.5 Flash** (Google AI Studio) — 1M context, 1,500 RPD
2. **Nemotron 3 Ultra/Super** — 1M context via OpenRouter
3. **Cerebras Llama 3.3 70B** — 1M context, 1M tokens/day

### Multimodal (Vision)
1. **Gemma 4 31B** (OpenRouter/NovitaAI) — Images + text, 256K, Apache 2.0
2. **Gemma 4 26B A4B** (OpenRouter) — MoE, 3.8B active, video support
3. **Nemotron 3 Nano Omni** (OpenRouter) — Text/image/video/audio input

### Local (Zero Cost)
1. **Qwen3.5 27B** (Ollama) — Best overall, 16GB VRAM at Q4
2. **Qwen3 8B** (Ollama) — Best for 8GB VRAM
3. **Llama 4 Scout 17B** (Ollama) — 512K context
4. **Gemma 4 12B** (Ollama) — Strong reasoning per parameter

---

## Signup URLs

| Provider | API Key URL |
|----------|-------------|
| OpenRouter | https://openrouter.ai/keys |
| Groq | https://console.groq.com/keys |
| Google AI Studio | https://aistudio.google.com/apikey |
| NVIDIA NIM | https://build.nvidia.com/ |
| OpenCode Zen | https://opencode.ai/auth |
| NovitaAI | https://novita.ai/ |
| Hugging Face | https://huggingface.co/settings/tokens |
| GitHub Models | https://github.com/settings/tokens |
| Cloudflare | https://dash.cloudflare.com/profile/api-tokens |
| Kimi/Moonshot | https://platform.moonshot.cn/ |
| Cohere | https://dashboard.cohere.com/api-keys |
| Mistral | https://console.mistral.ai/api-keys |
| Cerebras | https://cloud.cerebras.ai/ |

---

## Estimated Hermes Tasks/Day (with 6-20K token overhead)

| Provider | Tasks/Day | Binding Constraint |
|----------|-----------|-------------------|
| Groq | 25-50 | 500K token budget on 70B |
| OpenRouter | 15-30 | 200 req limit |
| Google AI Studio | 20-40 | 1,500 RPD |
| OpenCode Zen | Unlimited | Free models only |
| Local Ollama | Unlimited | Hardware |

---

## Key Stacking Multipliers

| Keys | OpenRouter | Groq | Google |
|------|------------|------|--------|
| 1 | 50/day | 1K/day | 1.5K/day |
| 3 | 150/day | 3K/day | 4.5K/day |
| 5 | 250/day | 5K/day | 7.5K/day |

*Each key has independent rate limits. Credential pools auto-rotate on same-provider errors.*