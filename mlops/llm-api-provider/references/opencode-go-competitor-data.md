# OpenCode Go — Competitor Reference Data

Source: https://opencode.ai/docs/go/ (July 2026)

## Pricing

- **$5 first month**, then **$10/mo** thereafter
- Ratio: **6:1** ($10 price → $60 monthly cap)

## Usage Limits

| Period | Dollar Cap |
|--------|-----------|
| 5 hours | $12 |
| Weekly | $30 |
| Monthly | $60 |

Beyond limits: if user has Zen balance, can enable "Use balance" fallback.

## Available Models (13)

| Model | Endpoint Style |
|-------|---------------|
| GLM-5.2 | OpenAI-compatible |
| GLM-5.1 | OpenAI-compatible |
| Kimi K2.7 Code | OpenAI-compatible |
| Kimi K2.6 | OpenAI-compatible |
| MiMo-V2.5 | OpenAI-compatible |
| MiMo-V2.5-Pro | OpenAI-compatible |
| MiniMax M3 | Anthropic-compatible |
| MiniMax M2.7 | Anthropic-compatible |
| Qwen3.7 Max | Anthropic-compatible |
| Qwen3.7 Plus | Anthropic-compatible |
| Qwen3.6 Plus | Anthropic-compatible |
| DeepSeek V4 Pro | OpenAI-compatible |
| DeepSeek V4 Flash | OpenAI-compatible |

## Model Pricing (per 1M tokens)

| Model | Input | Output | Cached Read |
|-------|-------|--------|-------------|
| GLM-5.2 | $1.40 | $4.40 | $0.26 |
| GLM-5.1 | $1.40 | $4.40 | $0.26 |
| Kimi K2.7 Code | $0.95 | $4.00 | $0.19 |
| Kimi K2.6 | $0.95 | $4.00 | $0.16 |
| MiMo V2.5 | $0.14 | $0.28 | $0.0028 |
| MiMo V2.5 Pro | $1.74 | $3.48 | $0.0145 |
| MiniMax M3 | $0.30 | $1.20 | $0.06 |
| MiniMax M2.7 | $0.30 | $1.20 | $0.06 |
| Qwen3.7 Max | $2.50 | $7.50 | $0.50 |
| Qwen3.7 Plus (≤256K) | $0.40 | $1.60 | $0.04 |
| Qwen3.7 Plus (>256K) | $1.20 | $4.80 | $0.12 |
| Qwen3.6 Plus (≤256K) | $0.50 | $3.00 | $0.05 |
| Qwen3.6 Plus (>256K) | $2.00 | $6.00 | $0.10 |
| DeepSeek V4 Pro | $1.74 | $3.48 | $0.0145 |
| DeepSeek V4 Flash | $0.14 | $0.28 | $0.0028 |

## Estimated Requests Per Limit Period (by model)

| Model | Per 5hr | Per Week | Per Month |
|-------|---------|----------|-----------|
| GLM-5.2 | 880 | 2,150 | 4,300 |
| Kimi K2.7 Code | 1,350 | 4,630 | 9,250 |
| MiMo-V2.5 | 30,100 | 75,200 | 150,400 |
| MiniMax M3 | 3,200 | 8,000 | 16,000 |
| Qwen3.7 Max | 950 | 2,390 | 4,770 |
| DeepSeek V4 Flash | 31,650 | 79,050 | 158,150 |
| DeepSeek V4 Pro | 3,450 | 8,550 | 17,150 |

## Example Avg Request Patterns (OpenCode Go observed)

| Model | Input | Cached | Output |
|-------|-------|--------|--------|
| DeepSeek V4 Flash | 790 | 68,000 | 280 |
| DeepSeek V4 Pro | 750 | 82,000 | 290 |
| MiMo-V2.5 | 830 | 71,500 | 295 |
| Qwen3.7 Plus | 500 | 57,000 | 190 |
| MiniMax M3 | 510 | 56,000 | 190 |

## API Endpoint

```
POST https://opencode.ai/zen/go/v1/chat/completions
```

Models for OpenAI-compatible use `"model": "deepseek-v4-flash"` etc.

## Notes

- Models hosted in US, EU, Singapore
- Providers follow zero-retention policy
- OpenCode Go is **optional** — you can use OpenCode with any BYOK provider
