# Per-Model Pricing Model — Reference Data

Detailed cost analysis, internal rate calculations, and portfolio math for building an LLM API provider competing with OpenCode Go.

## Wholesale Pricing (mid-2026)

Prices per 1M tokens. Cached input rates are typically 13-20% of full input rate.

| Provider | Model | Full Input | Cached Input | Output | Source |
|----------|-------|-----------|-------------|--------|--------|
| DeepSeek | V4 Flash | $0.14 | $0.018 | $0.28 | api-docs.deepseek.com |
| DeepSeek | V4 Pro | $0.435 | $0.058 | $0.87 | api-docs.deepseek.com |
| Xiaomi | MiMo-V2.5 | $0.14 | $0.028 | $0.28 | mimo.mi.com |
| Xiaomi | MiMo-V2.5-Pro | $0.435 | $0.058 | $0.87 | mimo.mi.com |
| MiniMax | M2.7 | $0.18 | $0.024* | $0.72 | platform.minimax.io |
| MiniMax | M3 | $0.30 | $0.039* | $1.20 | platform.minimax.io |
| Alibaba | Qwen3.7 Plus | $0.32 | $0.064 | $1.28 | OpenRouter → Alibaba |
| Alibaba | Qwen3.6 Plus | $0.325 | $0.033 | $1.95 | OpenRouter → Alibaba |

*Estimated cache rate at 13% of full input (not officially published for MiniMax, derived from typical provider cache discounts).

## Per-Request Cost Calculation

Standard agentic coding request profile: **790 new input + 68,000 cached input + 295 output tokens**.

```python
def cost_per_request(model_data):
    return (790 * model_data["input"] + 
            68000 * model_data["cached"] + 
            295 * model_data["output"]) / 1_000_000
```

| Model | Cost per Request | Formula |
|-------|----------------|---------|
| DeepSeek V4 Flash | **$0.001417** | (790×0.14 + 68000×0.018 + 295×0.28)/1M |
| DeepSeek V4 Pro | **$0.004544** | (790×0.435 + 68000×0.058 + 295×0.87)/1M |
| MiMo-V2.5 | **$0.002097** | (790×0.14 + 68000×0.028 + 295×0.28)/1M |
| MiMo-V2.5-Pro | **$0.004544** | (790×0.435 + 68000×0.058 + 295×0.87)/1M |
| MiniMax M2.7 | **$0.001987** | (790×0.18 + 68000×0.024 + 295×0.72)/1M |
| MiniMax M3 | **$0.003243** | (790×0.30 + 68000×0.039 + 295×1.20)/1M |
| Qwen3.7 Plus | **$0.004982** | (790×0.32 + 68000×0.064 + 295×1.28)/1M |
| Qwen3.6 Plus | **$0.003042** | (790×0.325 + 68000×0.033 + 295×1.95)/1M |

**Note:** If using OpenRouter instead of direct provider APIs, add 10-20% to these costs for OpenRouter's markup.

## OpenCode Go Internal Rates (Reverse-Engineered)

From OpenCode Go's published per-model request limits and $12/5hr cap:

| Model | Requests/5hr | Internal Rate | Notes |
|-------|-------------|--------------|-------|
| DeepSeek V4 Flash | 31,650 | $0.000379 | **Loss leader** — 3.7x below wholesale |
| MiMo-V2.5 | 30,100 | $0.000399 | **Loss leader** — 5.3x below wholesale |
| MiMo-V2.5-Pro | 3,250 | $0.003692 | Near cost (1.23x wholesale) |
| DeepSeek V4 Pro | 3,450 | $0.003478 | Near cost (1.31x wholesale) |
| MiniMax M2.7 | 3,400 | $0.003529 | **Profitable** — 0.56x wholesale (cheaper!) |
| MiniMax M3 | 3,200 | $0.003750 | Profitable — 0.86x wholesale |
| Qwen3.7 Plus | 4,300 | $0.002791 | **Loss** — 1.79x wholesale |
| Qwen3.6 Plus | 3,300 | $0.003636 | **Profitable** — 0.84x wholesale |

Formula: `internal_rate = 12.0 / requests_per_5hr`

## Recommended Nectar Internal Rates

Set per-model rates that balance competitiveness with sustainability:

| Model | Wholesale | Nectar Rate | Margin | Requests/$10 (5hr) | vs OpenCode Go |
|-------|----------|------------|--------|-------------------|---------------|
| DeepSeek V4 Flash | $0.001417 | $0.001200 | -18% | 8,333 | 26% |
| MiMo-V2.5 | $0.002097 | $0.001800 | -16% | 5,556 | 18% |
| MiniMax M2.7 | $0.001987 | $0.002800 | **+29%** | 3,571 | **105%** |
| MiniMax M3 | $0.003243 | $0.004200 | **+23%** | 2,381 | 74% |
| DeepSeek V4 Pro | $0.004544 | $0.005500 | +17% | 1,818 | 53% |
| MiMo-V2.5-Pro | $0.004544 | $0.005500 | +17% | 1,818 | 56% |
| Qwen3.7 Plus | $0.004982 | $0.005500 | +9% | 1,818 | 42% |
| Qwen3.6 Plus | $0.003042 | $0.003800 | +20% | 2,632 | 80% |

**Key insight:** On MiniMax M2.7, users get MORE requests than OpenCode Go while Nectar makes 29% margin. This is your competitive moat.

## Blended Portfolio Math

Using estimated agentic coding usage mix (35% Flash, 15% MiMo V2.5, 20% MiniMax M2.7, 10% M3, 5% each for the rest):

- Blended wholesale cost/request: **$0.002388**
- Blended internal rate/request: **$0.002685**
- Portfolio margin: **11.1%**
- Requests per $10 cap (5hr): **~3,724**
- Requests per $50 cap (monthly): **~18,621**

### Per-User Scenarios (mixed usage)

| User Type | Req/mo | Wholesale Cost | Billed Usage | Net at $6.90 |
|-----------|--------|---------------|-------------|-------------|
| Light (weekend) | 2,000 | $4.78 | $5.37 | **+$2.12** |
| Casual | 5,000 | $11.94 | $13.42 | **-$5.04** |
| Regular | 10,000 | $23.88 | $26.85 | **-$16.98** |
| Medium | 20,000 | $47.76 | $50.00* | **-$40.86** |
| Heavy | 50,000 | $119.39 | $50.00* | **-$112.49** |

*Capped at $50/month max

### Worst-Case Model-Specific Loss

If a user maxes out the $50/month cap using ONLY one model:

| Model | Requests @ $50 | Wholesale Cost | Loss |
|-------|---------------|---------------|------|
| DeepSeek V4 Flash | 41,667 | $59.04 | -$52.14 |
| MiMo-V2.5 | 27,778 | $58.25 | -$51.35 |
| MiniMax M2.7 | 17,857 | $35.48 | -$28.58 |
| MiniMax M3 | 11,905 | $38.61 | -$31.71 |
| DeepSeek V4 Pro | 9,091 | $41.31 | -$34.41 |
| MiMo-V2.5-Pro | 9,091 | $41.31 | -$34.41 |
| Qwen3.7 Plus | 9,091 | $45.29 | -$38.39 |
| Qwen3.6 Plus | 13,158 | $40.03 | -$33.13 |

## Breakeven Analysis

Break-even user count depends heavily on the mix of light/medium/heavy users.

### 80% Light / 15% Medium / 5% Heavy mix

Users: 50 → cost $799.91, rev $345.00 → ❌ -$454.91
Breakeven: **~Never at $6.90** (requires ~$16/user/month)

### 90% Light / 8% Medium / 2% Heavy mix (ideal startup)

Users: 50 → cost $477.56, rev $345.00 → ❌ -$132.56
Users: 100 → cost $955.12, rev $690.00 → ❌ -$265.12
Breakeven at $6.90: Not achievable with this model lineup

### Minimum viable price per user

For 80/15/5 mix at 50 users: **~$16/user/month**
For 90/8/2 mix at 50 users: **~$9.55/user/month**

## Practical Recommendations

### Three-Tier Plan Structure

| Tier | Price | 5hr Cap | Weekly | Monthly | Best For |
|------|-------|--------|--------|---------|----------|
| Free | $0 | 500 req (MiniMax/Qwen only) | — | — | Try before buy |
| Starter | $6.90 | $10 | $25 | $50 | Budget-conscious |
| Pro | $12.00 | $12 | $30 | $60 | OC parity |

### Loss-Leader Management

DeepSeek Flash and MiMo V2.5 will lose money at any price below $12/month for a user who primarily uses those models. Mitigations:
1. **Set lower per-model request limits** for these models (not the dollar cap — the per-model cap)
2. **Promote MiniMax M2.7 as the default model** — it's profitable AND gives users better value than OC
3. **Use model routing** — default users to MiniMax, let them opt into Flash
4. **Accept the loss ceiling** — at $50/month cap, even Flash-only users max out at -$52.14/month
