# Student Bootstrap Strategy — AWS Credits + BYOK Timeline

Covers the tactical bootstrap strategy using AWS credits to buy 6-12 months of runway while building a user base, then transitioning to a sustainable BYOK model before credits expire.

## The Core Truth

**DeepSeek V4 Flash is the cheapest capable model on earth.** At $0.14/$0.28 per million tokens ($0.001417/req wholesale), there is no cheaper fallback. Every competitor sells Flash at near or below cost as a loss leader. A student running flat-rate pricing on Flash will lose ~$47/user/month on every heavy Flash abuser.

The only sustainable bootstrap: use AWS credits to buy TIME, then switch to BYOK Flash before credits run out.

## Phase 1: Bootstrap with AWS Credits (Months 1-6)

### Getting the Credits

| AWS Program | Credits | Who qualifies | How to get |
|------------|---------|--------------|-----------|
| AWS Free Tier | $0 (infra only) | Anyone | Sign up — 12mo free EC2/RDS |
| AWS Activate Standard | $1,000 | Any startup with business email | apply.aws.com/activate |
| AWS Activate Portfolio | $5,000-$25,000 | Accelerator/incubator startups | Through VC/accelerator |
| AWS EdStart | $1,000-$15,000 | Education technology startups | aws.amazon.com/education/edstart |

**Most realistic for a student:** $1,000 AWS Activate credits + 12-month free tier for infrastructure.

### Phase 1 Strategy

| Item | What | Cost |
|------|------|------|
| EC2 (LiteLLM + Flask) | AWS Free Tier t2.micro | $0 |
| RDS (PostgreSQL) | AWS Free Tier db.t2.micro | $0 |
| Redis on EC2 | Same EC2 instance | $0 |
| DeepSeek Flash via Bedrock | AWS credits cover usage | $0 |
| MiniMax M2.7 / other models | Direct API or second provider | $0-$10/mo |
| **Total monthly cost** | | **$0-10** |
| **Revenue from 50 users** | 50 × $6.90 | **$345/mo** |
| **In your pocket** | | **$335-345/mo** |

### How Far Credits Go

At $5,000 AWS credits using Bedrock DeepSeek ($0.002316/req — 63% more than direct):

| Users | % Heavy (30K reqs/mo) | Flash cost/mo | Credits cover |
|-------|----------------------|--------------|--------------|
| 25 | 20% (5 heavies) | $347 | ~14 months |
| 50 | 20% (10 heavies) | $694 | ~7 months |
| 50 | 40% (20 heavies) | $1,389 | ~3.6 months |
| 100 | 20% (20 heavies) | $1,389 | ~3.6 months |
| 100 | 40% (40 heavies) | $2,779 | ~1.8 months |

**Warning:** Bedrock charges 63% MORE than direct DeepSeek API. After credits run out, switch to direct API to cut costs by nearly half.

**Better use of credits:** Cover infrastructure only (EC2 + RDS = $30-50/mo saved). Use direct DeepSeek API for model access (63% cheaper). $1,000 credits on infra alone lasts 20-33 months. Direct API costs are paid from $6.90/user revenue.

## Phase 2: Transition (Months 6-9)

Before credits run out:
1. Switch Flash from Bedrock to direct DeepSeek API (63% cheaper) — or switch to BYOK
2. Transition heavy Flash users to BYOK (provide clear instructions)
3. Use the cash reserve from Phase 1 ($1,000-4,000) to cover any transition losses

### The BYOK Announcement Message

> "Nectar now supports bring-your-own-key for DeepSeek Flash and MiMo V2.5.
> Connect your DeepSeek API key for unlimited Flash access.
> Your $6.90 subscription still includes MiniMax M2.7, M3, Qwen Pro,
> and all premium models — plus the shared cache, auto-failover, and dashboard."

## Phase 3: Self-Sustaining (Month 9+)

| Item | Cost |
|------|------|
| VPS (from pocket) | $15-20/mo |
| Direct DeepSeek API (BYOK) | $0 (users pay) |
| Premium models (MiniMax, etc.) | $20-100/mo (covered by $6.90 revenue) |
| **Monthly cost** | **$35-120/mo** |
| **Revenue (100 users)** | **$690/mo** |
| **Profit** | **$570-655/mo** |

With 100 users on BYOK Flash + $6.90/mo each, Nectar is profitable from user 1 because it never pays for Flash.

## Backup Plan: What If Credits Run Out Early?

| Situation | Action |
|-----------|--------|
| Credits depleted at 25 users | Switch all Flash to BYOK immediately. Keep $6.90 plan for premium models. |
| Heavy users complain about BYOK | Offer pay-per-use Flash at $0.002/req (cost + 40%). Most won't use enough to notice. |
| Revenue below costs | Tighten Flash limits to 2K reqs/mo included. Offer "Flash Boost" add-on for $3/mo extra. |
| Can't sustain even infra | Shut down. You learned the business model and it cost you $50-100 max. That's cheaper than any MBA. |
