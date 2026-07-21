# Request-Volume Threshold Analysis

Why 95% of real users never hit per-model request limits, even when your limits are 70-80% lower than OpenCode Go's.

## Agentic Coding Speed

Real human using agentic coding:

| Metric | Value |
|--------|-------|
| Requests per minute | 4-12 (each tool call takes 5-15s) |
| Requests per hour | 240-720 (at sustained use) |
| Typical daily session | 500-3,000 requests (not continuous) |
| Power user (all-day agents) | 3,000-6,000 requests |
| Bot / script abuse | 8,000+ in 5 hours (25+ req/min sustained) |

## Flash Model Threshold Comparison

At $12/5hr dollar cap with different internal rates:

| Provider | Internal Rate | 5hr Limit | Req/min sustained | Hits cap in real use? |
|----------|--------------|-----------|-------------------|----------------------|
| OpenCode Go (loss-leader) | $0.000379/req | 31,650 | 105 req/min | No -- even bots struggle |
| Nectar (cost+10%) | $0.001559/req | 7,698 | 26 req/min | No -- 26/min > 12/min human speed |
| Nectar (conservative, +29%) | $0.002800/req | 4,286 | 14 req/min | No -- 14/min > 12/min human speed |
| Nectar (premium models) | $0.005500/req | 2,182 | 7 req/min | **Barely** -- 7/min < 12/min top end |

## Real-World Consumption (Nectar cost+10% Flash rate)

| Scenario | Req | Duration | Cap consumed ($12 5hr) | % of cap | Real user notices? |
|----------|-----|----------|----------------------|----------|-------------------|
| Quick bug fix | 30 | 30 min | $0.05 | 0.4% | No |
| Small feature | 150 | 2 hr | $0.23 | 1.9% | No |
| Half-day coding | 500 | 5 hr | $0.78 | 6.5% | No |
| Full day coding | 1,200 | 8 hr | $1.87 | 15.6% | No |
| Power user | 3,000 | 12 hr | $4.68 | 39% | No |
| Extreme user | 6,000 | 16 hr | $9.35 | 78% | Nearing cap |
| Bot | 8,000 | 5 hr | $12.47 | **104%** | **Capped** |

**Takeaway:** Even at Nectar's higher Flash rate (cost+10%), a real human doing 12 hours of non-stop coding uses only 39% of the $12 5hr window. The cap only blocks automated scripts doing 25+ req/min sustained.

## Monthly Cap Dynamics

| User type | Req/mo | Wholesale cost | Revenue | Net |
|-----------|--------|---------------|---------|-----|
| Light (500/mo) | 500 | $0.71 | $6.90 | **+$6.19** |
| Regular (3K/mo) | 3,000 | $4.25 | $6.90 | **+$2.65** |
| Medium (10K/mo) | 10,000 | $14.17 | $6.90 | **-$7.27** |
| Heavy (30K/mo) | 30,000 | $42.51 | $6.90 | **-$35.61** |
| Maxed ($60 cap) | 38,485 | $54.53 | $6.90 | **-$47.63** |

## Why Flash Is Different (The Floor Model)

DeepSeek V4 Flash at $0.14/$0.28 per M tokens is the cheapest capable coding model on earth. There is no cheaper model to route to. This changes the economics:

| Other models | You can route to a cheaper fallback | Flash has none |
|-------------|-----------------------------------|----------------|
| MiniMax M3 ($0.30/$1.20) | Route to Flash ($0.14/$0.28) | -- |
| DeepSeek Pro ($0.44/$0.87) | Route to Flash ($0.14/$0.28) | -- |
| Qwen3.7 Plus ($0.32/$1.28) | Route to Flash ($0.14/$0.28) | -- |
| **Flash itself** | **Nowhere cheaper** | **Flash IS the floor** |

Because Flash is the floor, it attracts the worst adverse selection. A user who gets $60/month of Flash access for $6.90 saves ~$35/month vs paying DeepSeek directly. Heavy users gravitate toward it.

## Adverse Selection: The 80% Heavy Trap

**If you price too low, 80% of your users will be heavy users who cost you money.**

| User type | What they pay | What they consume | Cost to you | Net |
|-----------|-------------|-------------------|------------|-----|
| Light (500 reqs/mo) | $6.90 | 500 Flash reqs = $0.71 | $0.71 | **+$6.19** |
| Heavy (30K reqs/mo) | $6.90 | 30K Flash reqs = $42.51 | $42.51 | **-$35.61** |
| Maxed ($60 cap) | $6.90 | 38,485 Flash reqs = $54.53 | $54.53 | **-$47.63** |

At 100 users with 80% heavy Flash users:
- 80 heavies x -$47.63 = -$3,810.40
- 20 lights x +$6.19 = +$123.80
- **Total: -$3,686.60/month**

No flat-rate plan survives this. The only fix: BYOK Flash or pay-per-use.

## Key Numbers Reference

| Model | Wholesale/req | OC Internal Rate | Nectar cost+10% | Notes |
|-------|-------------|----------------|-----------------|-------|
| DeepSeek V4 Flash | $0.001417 | $0.000379 | $0.001559 | **Floor -- cheapest model on earth** |
| MiMo-V2.5 | $0.002097 | $0.000399 | $0.002307 | Second cheapest |
| MiniMax M2.7 | $0.001987 | $0.003529 | $0.002186 | Nectar's star: better than OC |
| MiniMax M3 | $0.003243 | $0.004200 | $0.003567 | |
| DeepSeek V4 Pro | $0.004544 | $0.003478 | $0.004998 | |
| MiMo-V2.5-Pro | $0.004544 | $0.003692 | $0.004998 | |
| Qwen3.7 Plus | $0.004982 | $0.002791 | $0.005480 | |
| Qwen3.6 Plus | $0.003042 | $0.003636 | $0.003346 | Profitable at OC rate |

## Marketing Lever

Key line to use in comparisons:

> "OpenCode Go's 31,650 Flash requests per 5 hours sounds generous -- until you realize no human makes 105 requests per minute. At 4-12 requests per minute (normal coding), you use 0.4-6.5% of the cap in a full session. The extra 93% headroom only benefits bots and API abusers who cost the entire pool money."

## When Per-Model Limits Actually Bind

The per-model limits matter for:
1. **Multi-session automation** -- CI/CD pipelines, batch processing, code review bots
2. **Test suites** -- Running 10,000+ automated test generations
3. **Abuse** -- Someone trying to resell API access or mine tokens
4. **Never:** A human developer doing normal daily coding work
