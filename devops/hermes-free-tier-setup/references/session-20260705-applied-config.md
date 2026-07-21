# Session 2026-07-05: Free-Tier Config Applied & Verified

## What Was Done

1. **Applied the free-tier config template** (`config-free-tier.yaml` → `config.yaml`)
2. **Ran `hermes doctor --fix`** — migrated config to v33, registered 5 custom providers
3. **Verified API connectivity** — OpenRouter, Groq, Google, OpenCode Zen all ✅
4. **Tested primary model** — Nemotron 3 Ultra (OpenRouter) responded correctly
5. **Removed unused LiteLLM custom provider** — user doesn't need the proxy
6. **Cleaned up `LITELLM_MASTER_KEY`** from `.env`

## Keys Present (Active Fallbacks)

| Key | Provider | Fallbacks Unlocked |
|-----|----------|-------------------|
| `OPENROUTER_API_KEY` | openrouter | #1 Nemotron Super, #3 Laguna M.1, #6 North Mini Code, #7 Gemma 4 31B, #8 GPT-OSS 120B, #9 Laguna XS |
| `GROQ_API_KEY` | groq | #2 Llama 3.3 70B (320 tok/s) |
| `GOOGLE_API_KEY` | gemini | #4 Gemini 2.5 Flash (1M context) |
| `OPENCODE_ZEN_API_KEY` | opencode-zen | #11 MiMo-V2.5, #12 North Mini Free, #13 Nemotron Ultra Free, #14 Big Pickle, #15 DeepSeek V4 Flash |

## Keys Missing (Locked Fallbacks)

| Missing Key | Provider | Fallbacks Locked |
|-------------|----------|-----------------|
| `NVIDIA_API_KEY` | nvidia | #10 Nemotron 3 Ultra (NIM) |
| `NOVITA_API_KEY` | novita | #16 Gemma 4 31B backup |
| `HF_TOKEN` | huggingface | #17 Llama 3.3 70B |
| `GITHUB_MODELS_TOKEN` | github-models | #18 GPT-4o |
| `CLOUDFLARE_API_TOKEN` | cloudflare | #19 Llama 3.3 70B edge |
| `KIMI_API_KEY` | kimi-coding | #20 Kimi K2.6 |
| `OLLAMA_API_KEY` + Ollama running | ollama-local | #5 Qwen3.5 27B local |

## Effective Active Chain (14 providers)

1. Main: **Nemotron 3 Ultra** (OpenRouter)
2. **Nemotron 3 Super** (OpenRouter)
3. **Llama 3.3 70B** (Groq) — 320 tok/s
4. **Laguna M.1** (OpenRouter) — coding
5. **Gemini 2.5 Flash** (Google) — 1M context
6. **North Mini Code** (OpenRouter)
7. **Gemma 4 31B** (OpenRouter) — multimodal
8. **GPT-OSS 120B** (OpenRouter)
9. **Laguna XS 2.1** (OpenRouter)
10. **MiMo-V2.5 Free** (OpenCode Zen)
11. **North Mini Code Free** (OpenCode Zen)
12. **Nemotron 3 Ultra Free** (OpenCode Zen)
13. **Big Pickle** (OpenCode Zen)
14. **DeepSeek V4 Flash Free** (OpenCode Zen)

## Verification Commands Used

```bash
# Apply config
cp /root/.hermes/config-free-tier.yaml /root/.hermes/config.yaml
hermes doctor --fix

# Test primary
timeout 30 hermes chat -q "Say OK and nothing else"

# Test individual providers
hermes chat -q "Say OK" --provider groq
hermes chat -q "Say OK" --provider gemini
hermes chat -q "Say OK" --provider opencode-zen
```

## Custom Providers After Cleanup

```yaml
providers:
  ollama-local:
    api: http://localhost:11434/v1
    default_model: qwen3.5:27b
  vllm-local:
    api: http://localhost:8000/v1
  sglang-local:
    api: http://localhost:30000/v1
  lmstudio-local:
    api: http://localhost:1234/v1
```

## Notes

- **14 active fallbacks** is sufficient for uninterrupted free usage
- OpenCode Zen provides 5 extra coding-optimized models during free period
- Key stacking (adding `_2`, `_3` keys) would multiply limits 3-5x
- Local Ollama (`qwen3.5:27b`) recommended for true unlimited fallback — needs 16GB VRAM