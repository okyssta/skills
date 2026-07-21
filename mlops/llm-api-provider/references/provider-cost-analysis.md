# LLM Provider Cost Analysis Reference

## DeepSeek Official Pricing (2026)

| Model | Cache Hit Input | Cache Miss Input | Output |
|-------|----------------|-----------------|--------|
| DeepSeek V4 Flash | $0.0028/M | $0.14/M | $0.28/M |
| DeepSeek V4 Pro | $0.0036/M | $0.44/M | $0.87/M |

## OpenCode Go Published Per-Request Token Counts

| Model | Uncached Input | Cached Input | Output |
|-------|---------------|-------------|--------|
| DeepSeek V4 Flash | 790 | 68,000 | 280 |
| DeepSeek V4 Pro | 750 | 82,000 | 290 |
| MiniMax M3 | 510 | 56,000 | 190 |
| Kimi K2.6 | 870 | 55,000 | 200 |
| GLM-5.2 | 700 | 52,000 | 150 |
| MiMo V2.5 | 830 | 71,500 | 295 |

## Cost Per Request (Worst-Case, No Cross-User Cache)

| Model | Input Cost | Output Cost | Total |
|-------|-----------|-------------|-------|
| DeepSeek V4 Flash | $0.00963 | $0.00008 | **~$0.00971** |
| DeepSeek V4 Pro | $0.03600 | $0.00025 | **~$0.03625** |
| MiniMax M3 | $0.01695 | $0.00023 | **~$0.01722** |

## Cost Per Request (With Cross-User Shared Cache — 97% Hit Rate)

| Model | Input Cost (97% cached) | Output Cost | Total |
|-------|----------------------|-------------|-------|
| DeepSeek V4 Flash | ~$0.00029 | $0.00008 | **~$0.00037** |
| DeepSeek V4 Pro | ~$0.00110 | $0.00025 | **~$0.00135** |

## Competitor Pricing Table

| Service | Entry Price | Real Price | Cap/Usage | Notes |
|---------|------------|-----------|-----------|-------|
| OpenCode Go | $5 (month 1) | **$10/mo** | $60/mo value | $5 is loss leader, doubles to $10 |
| Command Code Go | $1/mo | **$1/mo** | $10 credits | taste-1 model only. $15/mo for real models |
| Command Code Pro | $15/mo | **$15/mo** | $30 credits | Real model access |
| Freebuff | Free | **Free** | 5hrs/day DeepSeek Flash | Ad-supported |
| OpenRouter | Free tier | **Pay-as-you-go** | 50 free req/day | 5.5% fee on credits |

## Breakeven Scenarios (at $6.90/mo, $60 cap, with cache optimization)

| Users | Light % | Heavy % | Monthly Cost | Monthly Revenue | Profit |
|-------|---------|---------|-------------|-----------------|--------|
| 5 | 80% | 20% | ~$13 | $34.50 | **+$21** |
| 5 | 60% | 40% | ~$37 | $34.50 | **-$3** |
| 10 | 80% | 20% | ~$28 | $69.00 | **+$41** |
| 10 | 60% | 40% | ~$58 | $69.00 | **+$11** |
| 20 | 80% | 20% | ~$55 | $138.00 | **+$83** |

## Free LLM API Backends (Permanent Free Tiers)

| Provider | Signup | Rate Limit | Models |
|----------|--------|------------|--------|
| NVIDIA NIM (build.nvidia.com) | Free dev account | ~40 RPM, no daily cap | Nemotron 3 Ultra/Super/Nano, Llama 3.1 405B, MiniMax M2.7, DeepSeek R1 |
| Groq | Free account | 30 RPM, 1,000 RPD | Llama 3.3 70B, Qwen3 32B, GPT-OSS 120B |
| Mistral AI | Free account | ~1B tokens/month | Mistral Medium 3.5, Codestral, Mistral Small 4 |
| OpenRouter (:free) | Free account | 20 RPM, 200 RPD | ~22 free models |
| Google Gemini (AI Studio) | Free account | 15 RPM, 1,500 RPD | Gemini 2.5 Flash, 3.5 Flash, 2.5 Pro |
| Cloudflare Workers AI | Free account | 10K neurons/day | 50+ models (Llama, Qwen, GLM, Kimi) |
