# Consumer-Side Model Selection from Subscription Plans

When the user asks "which model should I use on my $X/mo plan?" — treat it as a burn-rate analysis backed by actual usage data, not opinion.

## Prerequisites

Before recommending, gather:

1. **Actual usage data** — `hermes insights --days 30` for session counts, token volume, model breakdown, platform breakdown
2. **Plan limits** — web_extract the plan's docs page for per-model request limits, dollar caps, and pricing tiers
3. **Billing cycle** — when does it reset? How much remaining?

## The Burn Rate Calculation

```python
# Given: 29% used in 11 days, 19 days remaining
daily_burn = 0.29 / 11      # ~2.6%/day
remaining_budget = 1 - 0.29 # ~71% left
projected_end = remaining_budget / daily_burn + elapsed_days

# Dollar-value check
monthly_cap = 60  # from plan docs
used_dollars = monthly_cap * 0.29
remaining_dollars = monthly_cap - used_dollars
days_until_empty = remaining_dollars / (used_dollars / elapsed_days)
```

## The $60 vs $15 Bucket Problem

Every plan has per-model multipliers. Models with a small usage bucket (e.g. $15) cannot sustain a user who has already burned significant cap on cheaper models:

- If user is at 29% ($17.40 used) on Flash ($60 bucket), switching to a $15-bucket model means they've **already exceeded that model's limit** (115% of $15 consumed)
- Only models with the FULL monthly bucket matching the user's current burn are safe
- **Rule: never recommend a $15-bucket model to a user who's already burned >20% of their cap**

## Work Profile Analysis

Match the user's platform breakdown to model strengths:

| Platform % | Profile | Model Priority |
|------------|---------|----------------|
| 80%+ cron/subagent | Automated, routing work | Cheapest reliable (Flash/MiMo) — no benefit from expensive models |
| 40%+ interactive (Discord/CLI) | Reasoning-heavy | Premium models (Qwen3.7+, Kimi code, M3) earn their cost |
| Mixed (50/50) | Default | Mid-tier (Qwen3.7 Plus, MiniMax M3) — balances quality and budget |

## Selection Rules

1. **Filter by bucket first** — only models matching the user's full monthly cap are eligible
2. **Filter by burn rate** — remaining budget must last the rest of the billing cycle at current burn × model's cost multiplier
3. **Rank by work relevance** — match model's strength domain to the user's primary platform
4. **Check request limits** — even with dollar headroom, a model with 4,770 req/mo (Qwen3.7 Max) could feel tight for heavy users
5. **Give hard numbers** — "At $1.58/day burn and $42.60 remaining, you'd use ~55%. Won't run out."

## User Preference: Conservative Data-Backed Recommendations

This user WILL hold you accountable if they run out of usage mid-cycle. Their tolerance for speculative recommendations is zero.

- Show the **exact computation** — dollar burn rate, remaining budget, projected end-of-cycle usage
- Lead with **hard numbers before reasoning** — "X req/mo, $Y remaining, Z days: safe." Then explain why
- When uncertain, **round down**: "Your burn rate X, model Y costs Zx more per request → you'd hit 80% by reset" (not "you'd probably be fine")
- Always include the **safest fallback model** alongside any premium recommendation
- Never recommend a model without checking: "can they finish their billing cycle on this?"
- Phrase as: "At your burn rate, model X uses Y% of cap → safe. Model Z uses W% → risky."

## OpenCode Go Model Bucket Reference

| Model | Monthly Cap ($) | Req/mo | Strength |
|-------|----------------|--------|----------|
| DeepSeek V4 Flash | $60 | 158,150 | Cheapest, fast |
| MiMo-V2.5 | $60 | 150,400 | Flash-tier, good reasoning |
| MiniMax M2.7 | $60 | 17,000 | Strong all-rounder |
| **MiniMax M3** | **$60** | **16,000** | **Quality pick, safe** |
| **Qwen3.7 Plus** | **$60** | **21,600** | **Best coding value, safe** |
| Qwen3.6 Plus | $60 | 16,300 | Good budget option |
| GLM-5.2/5.1 | $60 | 4,300 | High quality, low count |
| Kimi K2.7 Code | $60 | 9,250 | Coding-specialized |
| Kimi K2.6 | $60 | 5,750 | Coding, fewer reqs |
| Qwen3.7 Max | $60 | 4,770 | Best quality, tight count |
| DeepSeek V4 Pro | **$15** | 17,150 | DO NOT recommend after 20% usage |
| MiMo-V2.5-Pro | **$15** | 16,300 | DO NOT recommend after 20% usage |
| Kimi K3 | **$15** | 680 | DO NOT recommend after 20% usage |
| Grok 4.5 | **$15** | 380 | DO NOT recommend after 20% usage |
