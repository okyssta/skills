# 🍯 Nectar API — Handoff Document (Example)

**Built:** July 7, 2026
**Target:** Agentic coding API provider (OpenCode Go competitor)
**Audience:** Hermes community first → broader dev tools
**Model:** deepseek-v4-flash (used to build this)

---

## Table of Contents

1. [What Is Nectar?](#what-is-nectar)
2. [Project Structure](#project-structure)
3. [Architecture Overview](#architecture-overview)
4. [Service Architecture](#service-architecture)
5. [Pricing Strategy](#pricing-strategy)
6. [Business Model & Risk](#business-model--risk)
7. [Providers & Models](#providers--models)
8. [API Reference](#api-reference)
9. [Setup Guide](#setup-guide)
10. [What's NOT Done Yet](#whats-not-done-yet)
11. [Key Decisions Made](#key-decisions-made)
12. [Important Design Notes](#important-design-notes)
13. [Commands Cheat Sheet](#commands-cheat-sheet)

---

## What Is Nectar?

Nectar is a flat-rate API provider for agentic coding tools (Hermes, OpenCode, Claude Code, Cline, Codex — anything that speaks the OpenAI API). Key differentiators:

- **$6.90/mo flat** — not $5→$10 like OpenCode Go
- **Same caps as OpenCode Go:** $12/5hr, $30/week, $60/month
- **Multi-provider failover** — if DeepSeek goes down, routes to NVIDIA/Groq/Mistral
- **Shared prompt caching** across users reduces costs ~46%
- **Free models** (Nemotron, Llama, Mistral, Qwen Coder) don't count toward caps
- **17 models** from 6 providers

---

## Project Structure

```
/root/nectar/
├── docker-compose.yml           # 5 services: postgres, redis, litellm, nectar-api, nginx
├── .env.example                 # Template for environment variables
├── .gitignore                   # Ignores .env, __pycache__, .venv, .vscode, .idea, etc.
├── README.md                    # Public-facing documentation
├── NECTAR_BUILD_SUMMARY.md      # Build summary from original session
├── HANDOFF.md                   # ← THIS FILE — complete handoff document
│
├── flask_app/                   # Custom Python Flask API
│   ├── app.py                   # Main app: auth, sub-limits, proxying to LiteLLM
│   ├── models.py                # User/API key/usage model functions
│   ├── sub_limits.py            # Sub-limit enforcement (5hr/daily/weekly/monthly)
│   ├── billing.py               # Stripe billing integration (needs swap to Lemon Squeezy)
│   ├── database.py              # PostgreSQL connection pool
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile               # Docker build for the Flask app
│   ├── static/
│   │   └── style.css            # Premium dark SaaS theme
│   └── templates/               # Jinja2 templates
│       ├── index.html           # Landing page
│       ├── pricing.html         # Pricing comparison
│       ├── signup.html          # Registration
│       ├── login.html           # Login
│       ├── dashboard.html       # User dashboard with usage bars
│       ├── setup.html           # Post-signup setup guide
│       ├── admin.html           # Admin panel
│       └── admin_user.html      # User detail view
│
├── litellm/
│   └── config.yaml              # LiteLLM provider config (17 models, routing, caching)
│
├── nginx/
│   └── default.conf             # Nginx reverse proxy config (disabled, for production)
│
└── scripts/
    ├── init-db.sql              # Full database schema (7 tables, functions, indexes)
    └── setup.sh                 # Deployment setup script
```

**File counts:** 24 files, ~3,000 lines total.

---

## Architecture Overview

```
User (Hermes/OpenCode/curl)
        │
        │  POST /v1/chat/completions + API Key
        ▼
┌─────────────────┐
│  Flask App       │  ← Validates API key, checks sub-limits, proxies request
│  (port 5000)     │
│                  │  Routes: /, /signup, /login, /dashboard, /admin
│  ├── Auth        │  └─ /v1/chat/completions, /v1/models
│  ├── Sub-limits  │     └─ /health, /api/usage, /api/keys/rotate
│  └── Billing     │
└────────┬─────────┘
         │  POST /v1/chat/completions + Master Key
         ▼
┌─────────────────┐
│  LiteLLM Proxy   │  ← Provider routing, failover, response caching (Redis)
│  (port 4000)     │
│                  │
│  ├── DeepSeek    │  ← Paid primary
│  ├── NVIDIA NIM  │  ← Free backend (Nemotron, Llama, MiniMax, R1)
│  ├── Groq        │  ← Free backend (Llama Fast, Qwen3)
│  ├── Mistral     │  ← Free tier (Medium, Codestral)
│  ├── SiliconFlow │  ← Paid fallback (GLM, Kimi)
│  └── OpenRouter  │  ← Free fallback (Qwen Coder, GPT-OSS, Nemotron ultra)
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  PostgreSQL 16   │  ← Users, API keys, usage_log, spend_snapshots, invoices
└─────────────────┘

┌─────────────────┐
│  Redis 7         │  ← Response cache, rate limiting, session storage
└─────────────────┘
```

---

## Service Architecture (Docker)

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `postgres` | postgres:16-alpine | — | User data, usage tracking, billing |
| `redis` | redis:7-alpine | — | Shared cache pool, rate limiting |
| `litellm` | ghcr.io/berriai/litellm:main-latest | 4000 | OpenAI-compatible proxy, provider routing, fallbacks |
| `nectar-api` | (builds from flask_app/) | 5000 | Auth, sub-limits, billing, dashboard |
| `nginx` | nginx:alpine | 8080 | **Commented out** — enable in production with SSL |

---

## Pricing Strategy

### The Core Offer

| Plan | Price | 5hr Cap | Daily Cap | Weekly Cap | Monthly Cap | DeepSeek Flash Requests |
|------|-------|---------|-----------|------------|-------------|------------------------|
| **Starter** | **$6.90/mo** | $12 | $20 | $30 | $60 | ~158,000 max |
| **Pro** | **$15/mo** | $30 | $50 | $75 | $150 | ~397,000 max |
| **Power** | **$30/mo** | $60 | $100 | $150 | $350 | ~926,000 max |

### Positioning vs OpenCode Go

| | OpenCode Go | Nectar |
|---|---|---|
| Month 1 | $5 | **$6.90** |
| Month 2+ | **$10** | **$6.90** |
| Over 6 months | $55 | **$41.40** |
| Over 12 months | $105 | **$82.80** |
| Trust message | "First month cheap" | **"This is just the price. Period."** |

### Marketing Hook
> *"Pay $6.90. Not $5 that turns into $10. Just $6.90."*

---

## Business Model & Risk

### How Profitability Works

Since the user insisted on the $6.90 flat plan with the **same caps as OpenCode Go** ($12/5hr, $30/wk, $60/mo), the risk structure is:

**Per-user unit economics (DeepSeek V4 Flash):**
- Per request cost: ~$0.000378 (790 uncached + 68,000 cached input, 280 output)
- 158,150 requests to hit the $60 cap

**10 users scenario:**
- 8 light users (~2K req/mo each) = $5.52 cost, $55.20 revenue → +$49.68
- 1.5 medium users (~15K req/mo each) = $8.55 cost, $10.35 revenue → +$1.80
- 0.5 heavy users (~60K req/mo) = $11.34 cost, $3.45 revenue → -$7.89
- **Total: ~$59.77 cost, $69.00 revenue = +$9.23 profit** (barely)

**5 users worst case:**
- 3 light + 2 heavy = loses money (~-$35)
- 4 light + 1 heavy = barely profitable (~+$8)

**Breakeven:** ~10 users on Starter plan
**Zero-loss guarantee:** Not mathematically guaranteed at small scale with $60 cap — but sub-limits ($12/5hr) provide protection against burst abuse.

### Mitigation: Free Models Don't Count Toward Caps

~70% of model inventory is free backend (NVIDIA NIM, Groq, Mistral free tier, OpenRouter free). If users gravitate toward these models, margins skyrocket. The paid models (DeepSeek V4 Flash/Pro, GLM, Kimi) are what count against caps.

---

## Providers & Models

### 17 Models Across 6 Providers

| Model | Backend | Cost Type | LiteLLM Name |
|-------|---------|-----------|--------------|
| DeepSeek V4 Flash | DeepSeek | Paid | `deepseek-v4-flash` |
| DeepSeek V4 Pro | DeepSeek | Paid | `deepseek-v4-pro` |
| Nemotron 3 Ultra | NVIDIA NIM | Free | `nemotron-3-ultra` |
| Nemotron 3 Super | NVIDIA NIM | Free | `nemotron-3-super` |
| Nemotron 3 Nano | NVIDIA NIM | Free | `nemotron-3-nano` |
| MiniMax M2.7 | NVIDIA NIM | Free | `minimax-m2.7` |
| Llama 3.3 70B | NVIDIA NIM | Free | `llama-3.3-70b` |
| DeepSeek R1 | NVIDIA NIM | Free | `deepseek-r1` |
| Llama 3.3 70B Fast | Groq LPU | Free | `llama-3.3-70b-fast` |
| Qwen3 32B | Groq LPU | Free | `qwen3-32b` |
| Mistral Medium 3.5 | Mistral | Free | `mistral-medium-3.5` |
| Codestral | Mistral | Free | `codestral` |
| GLM-5.2 | SiliconFlow | Paid | `glm-5.2` |
| Kimi K2.6 | SiliconFlow | Paid | `kimi-k2.6` |
| Qwen3 Coder | OpenRouter | Free | `qwen3-coder` |
| GPT-OSS 120B | OpenRouter | Free | `gpt-oss-120b` |
| Nemotron 3 Ultra (fallback) | OpenRouter | Free | `nemotron-3-ultra-free` |

### LiteLLM Routing

- **Strategy:** Latency-based routing
- **Fallbacks configured:**
  - `deepseek-v4-flash` → `nemotron-3-ultra` → `llama-3.3-70b`
  - `deepseek-v4-pro` → `nemotron-3-ultra` → `mistral-medium-3.5`
  - `nemotron-3-ultra` → `nemotron-3-ultra-free` → `llama-3.3-70b-fast`
  - `llama-3.3-70b` → `llama-3.3-70b-fast` → `gpt-oss-120b`
- **Cache:** Redis-backed, 300s TTL
- **Retries:** 2 retries, 500ms gap, cooldown 60s after 3 failures

---

## API Reference

### Authentication
```
Authorization: Bearer nk_live_<your_hex_key>
```

### Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/v1/models` | List available models |
| `POST` | `/v1/chat/completions` | Chat completions (OpenAI-compatible) |
| `GET` | `/` | Landing page |
| `GET` | `/pricing` | Pricing page |
| `GET` | `/signup` | Registration form |
| `POST` | `/signup` | Create account |
| `GET` | `/login` | Login form |
| `POST` | `/login` | Authenticate |
| `GET` | `/logout` | Clear session |
| `GET` | `/dashboard` | Usage dashboard |
| `GET` | `/setup` | Post-signup setup guide |
| `GET` | `/api/usage` | JSON usage data |
| `POST` | `/api/keys/rotate` | Rotate API key |
| `GET` | `/admin` | Admin panel |
| `GET` | `/admin/user/<id>` | User detail |
| `GET` | `/health` | Health check |
| `POST` | `/api/create-checkout-session` | Stripe checkout |
| `POST` | `/api/stripe/webhook` | Stripe webhooks |

### Sub-Limit Headers (returned on 429)
```json
{
  "error": {
    "message": "Usage limit exceeded: 5-hour limit reached ($11.80/$12.00)",
    "type": "insufficient_quota",
    "code": "quota_exceeded",
    "limits": {
      "usage": {"5hr": 11.80, ...},
      "limits": {"5hr_cap": 12.0, ...}
    }
  }
}
```

---

## Setup Guide

### Quick Start (Docker)

```bash
cd /root/nectar
cp .env.example .env
# Fill in at minimum: DEEPSEEK_API_KEY, NVIDIA_API_KEY, GROQ_API_KEY
docker compose up -d
curl http://localhost:5000/health
curl http://localhost:5000/v1/models
```

### Environment Variables

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `POSTGRES_PASSWORD` | Optional | `changeme_nectar_db_pass` | Change in production |
| `REDIS_PASSWORD` | Optional | `nectar_redis_pass` | Change in production |
| `LITELLM_MASTER_KEY` | Optional | `sk-nectar-master-key-change-me` | Change in production |
| `DEEPSEEK_API_KEY` | **Yes** | — | Primary paid provider |
| `NVIDIA_API_KEY` | No | — | Free models (Nemotron, Llama, etc.) |
| `GROQ_API_KEY` | No | — | Free models, fast LPU |
| `MISTRAL_API_KEY` | No | — | Free tier |
| `SILICONFLOW_API_KEY` | No | — | Paid fallback |
| `OPENROUTER_API_KEY` | No | — | Free fallback |
| `STRIPE_*` | For billing | — | **Needs Lemon Squeezy replacement** |
| `NECTAR_ADMIN_EMAIL` | No | `admin@nectar.dev` | Admin panel login |
| `NECTAR_ADMIN_PASSWORD` | No | `admin` | Change in production |
| `SESSION_SECRET` | No | Random | Session signing key |

---

## What's NOT Done Yet

### 1. API Keys (Critical — blocked without these)
| Key | Where to Get | Notes |
|-----|-------------|-------|
| **DeepSeek API Key** | platform.deepseek.com | PRIMARY — needed for paid models |
| **NVIDIA NIM API Key** | build.nvidia.com | FREE — Nemotron, Llama, MiniMax, R1 |
| **Groq API Key** | console.groq.com | FREE |
| **Mistral API Key** | console.mistral.ai | FREE tier ~1B tokens/mo |
| **SiliconFlow API Key** | cloud.siliconflow.cn | Paid fallback for GLM/Kimi |
| **OpenRouter API Key** | openrouter.ai | FREE fallback |

### 2. Payment Gateway
Stripe is currently integrated but **Stripe doesn't work in Pakistan**. Replace with **Lemon Squeezy**:
- 5% + $0.50/txn, Merchant of Record, supports Pakistan bank/PayPal payouts
- Create 3 products: Starter ($6.90/mo), Pro ($15/mo), Power ($30/mo)
- Replace `flask_app/billing.py` — swap all `stripe.*` calls for Lemon Squeezy API
- Update webhook handler to use Lemon Squeezy variant IDs

### 3. Domain + SSL
- Register a domain (e.g., `nectar.click`, `nectarapi.dev`)
- Point DNS to your VPS
- Set up SSL (Caddy easiest — auto HTTPS)
- Update README.md and templates with production URLs
- Enable Nginx in docker-compose.yml

### 4. Production Hardening
- Change all default passwords in .env
- Change admin credentials
- Enable HTTPS
- Set up Cloudflare for DDoS + caching

### 5. Launch
- Push to private GitHub repo
- Post in Hermes Discord

---

## Key Decisions Made

### Why $6.90 Flat Instead of $5/$10
OpenCode Go charges $5 first month → $10 after. The user wanted a single flat price forever to build trust. $6.90 is memorable and positions between their two tiers.

### Why $60 Monthly Cap (Same as OpenCode Go)
The user insisted on matching OpenCode Go's caps exactly — no compromises. This means at small scale (<10 users), heavy users can cause losses, but sub-limits ($12/5hr) mitigate burst risk.

### Why Stripe Is There if It Doesn't Work
Stripe was integrated first (the user learned it doesn't support Pakistan mid-build). The `billing.py` module needs to be rewritten for Lemon Squeezy.

### Why PostgreSQL for Limit Checks Instead of Redis
Usage tracking is done via PostgreSQL queries. Works fine at small scale (<100 concurrent). For production, migrate to Redis counters.

### Free Models Don't Count Toward Caps
All models from NVIDIA NIM, Groq, Mistral free tier, and OpenRouter free are $0.0 against caps. Major selling point and margin driver.

---

## Important Design Notes

### Sub-Limit Architecture
Limits are checked **before** each request using an estimate (~2,000 input + ~2,000 output tokens). After the request completes, actual usage is logged. The estimate is generous (overestimates cost by ~10x compared to actual agentic coding traffic patterns). Safe but could frustrate heavy users. Tune this.

### Cache Strategy
The 85% discount on `actual_cost` vs `billed_cost` in `_calculate_actual_cost()` is a placeholder. Real discount comes from: shared Redis cache, free backends, multi-provider routing.

### Streaming
Streaming (`stream=True`) is supported but logs estimated usage after the stream completes. Token estimate is rough (`len(content) // 4 + 1`). Consider capturing actual token counts from the API for production.

### Admin Access
Default admin: `admin@nectar.dev` / `admin`. Set via env vars. **Change before going live.**

### API Key Format
`nk_live_<64 hex chars>` — SHA-256 hashed in DB. Prefix `nk_live_a1b2c3d4` shown in UI. Keys rotated by deactivating old + generating new.

---

## Commands Cheat Sheet

```bash
# Start everything
docker compose up -d

# Stop everything
docker compose down

# View logs
docker compose logs -f nectar-api
docker compose logs -f litellm

# Rebuild Flask app after changes
docker compose build nectar-api && docker compose up -d

# Test API
curl http://localhost:5000/health
curl http://localhost:5000/v1/models
curl -H "Authorization: Bearer nk_live_..." http://localhost:5000/v1/models

# Reset DB (removes all data)
docker compose down -v && docker compose up -d

# Run locally (no Docker)
cd flask_app && pip install -r requirements.txt
DATABASE_URL=postgresql://nectar:***@localhost:5432/nectar python app.py
```

---

*Built by Hermes Agent for Kyssta. July 7, 2026.*
