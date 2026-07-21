# Provider Test Names for `--provider` Flag

**Use with:** `hermes chat -q "test" --provider <name>`

---

## Standard Providers (from `fallback_providers`)

| Config Entry | Provider Name | Notes |
|--------------|---------------|-------|
| `provider: openrouter` | `openrouter` | Primary, Nemotron 3 Ultra |
| `provider: groq` | `groq` | Speed fallback, Llama 3.3 70B |
| `provider: gemini` | `gemini` | Long context, Gemini 2.5 Flash |
| `provider: nvidia` | `nvidia` | NIM credits, Nemotron 3 Ultra |
| `provider: opencode-zen` | `opencode-zen` | 5 free coding models |
| `provider: novita` | `novita` | Cost-efficient backup |
| `provider: huggingface` | `huggingface` | Community models |
| `provider: github-models` | `github-models` | Frontier models (GPT-4o, Claude 3.5) |
| `provider: cloudflare` | `cloudflare` | Edge deployment |
| `provider: kimi-coding` | `kimi-coding` | Long context Kimi |

---

## Custom Providers (from `providers:` section)

| Config Name | Provider Flag | Default Model |
|-------------|---------------|---------------|
| `litellm-free` | `custom:litellm-free` | `llm-free` |
| `ollama-local` | `custom:ollama-local` | `qwen3.5:27b` |
| `vllm-local` | `custom:vllm-local` | `local-model` |
| `sglang-local` | `custom:sglang-local` | `local-model` |
| `lmstudio-local` | `custom:lmstudio-local` | `local-model` |

---

## Quick Test Commands

```bash
# Primary
hermes chat -q "Say OK" --provider openrouter

# Speed fallback
hermes chat -q "Say OK" --provider groq

# Long context
hermes chat -q "Say OK" --provider gemini

# Coding specialists
hermes chat -q "Say OK" --provider opencode-zen

# Your LiteLLM proxy
hermes chat -q "Say OK" --provider custom:litellm-free

# Local Ollama (if running)
hermes chat -q "Say OK" --provider custom:ollama-local
```

---

## Verify All at Once

```bash
./scripts/verify-free-tier.sh
```