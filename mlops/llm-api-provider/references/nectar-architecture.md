# Nectar API — Full Build Notes

## Architecture

```
User → Nginx :80 (or :8080 for dev)
         │
         ▼
Flask App (port 5000) — Gunicorn
    │  Auth + sub-limit check
    │  Usage logging to PostgreSQL
    │  Stripe billing webhooks
    │  Admin dashboard
    │
    ▼
LiteLLM Proxy (port 4000)
    │  Model routing to providers
    │  Auto-failover on 5xx
    │  Latency-based routing
    │  Redis caching (shared cross-user)
    │
    ├──► DeepSeek (paid — Flash, Pro)
    ├──► NVIDIA NIM (free — Nemotron, Llama, MiniMax, DeepSeek R1)
    ├──► Groq (free — Llama 3.3, Qwen3)
    ├──► Mistral (free — Medium 3.5, Codestral)
    ├──► SiliconFlow (paid fallback — GLM, Kimi)
    └──► OpenRouter (free fallback — Qwen Coder, Nemotron)
```

## Docker Compose Services

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| postgres | postgres:16-alpine | 5432 | User data, usage tracking |
| redis | redis:7-alpine | 6379 | Cache, rate limiting |
| litellm | ghcr.io/berriai/litellm:main-latest | 4000 | LLM proxy with routing |
| nectar-api | Custom Flask build | 5000 | Auth, billing, dashboard |
| nginx | nginx:alpine | 8080 | Reverse proxy (optional in dev) |

## LiteLLM Config Notes

- Model names must match what the provider expects in the `model` field of litellm_params
- For NVIDIA NIM: use format `openai/nvidia/<model-name>` with `api_base: https://integrate.api.nvidia.com/v1`
- For OpenRouter free: append `:free` suffix to model name
- Set `routing_strategy: latency-based-routing` for best performance
- Fallbacks array in `router_settings` defines which models to try when primary fails

## Database Issue

**Important:** LiteLLM's Prisma migrations connect to the same PostgreSQL database and can drop custom tables. Do NOT use postgres init scripts for custom tables. Instead, create them from the Flask app on startup:

```python
def init_db_tables():
    """Called at module level — before gunicorn workers fork."""
    execute("CREATE TABLE IF NOT EXISTS users (...)")
    execute("CREATE TABLE IF NOT EXISTS api_keys (...)")
    # etc.
```

Also seed the admin user from here, not from env vars in templates.

## Required Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `DEEPSEEK_API_KEY` | Yes (for paid models) | DeepSeek API access |
| `NVIDIA_API_KEY` | No (free) | NVIDIA NIM — Nemotron, Llama, etc |
| `GROQ_API_KEY` | No (free) | Groq LPU inference |
| `MISTRAL_API_KEY` | No (free) | Mistral free tier |
| `OPENROUTER_API_KEY` | No (free fallback) | OpenRouter free models |
| `SILICONFLOW_API_KEY` | No (paid fallback) | SiliconFlow for GLM, Kimi |
| `STRIPE_SECRET_KEY` | For billing | Stripe API |
| `SKIPE_PUBLISHABLE_KEY` | For billing | Stripe client-side |
| `STRIPE_STARTER_PRICE_ID` | For billing | Stripe product ID |
| `STRIPE_PRO_PRICE_ID` | For billing | Stripe product ID |
| `STRIPE_POWER_PRICE_ID` | For billing | Stripe product ID |
| `NECTAR_ADMIN_EMAIL` | No | Admin login email |
| `NECTAR_ADMIN_PASSWORD` | No | Admin login password |

## Startup Process

1. PostgreSQL starts → runs init-db.sql (creates LiteLLM-compatible extensions)
2. Redis starts
3. LiteLLM starts → connects to PostgreSQL → runs Prisma migrations → connects to Redis
4. Flask app starts → creates custom tables + admin user → starts gunicorn workers
5. Nginx starts → reverse proxy to Flask app

## File Structure

```
/root/nectar/
├── docker-compose.yml
├── .env                      # NOT committed
├── .env.example
├── README.md
├── flask_app/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py                # Main Flask app (routes, auth, sub-limits, proxy)
│   ├── billing.py            # Stripe webhooks
│   ├── database.py           # PostgreSQL connection pool
│   ├── models.py             # User/API key/usage operations
│   ├── sub_limits.py         # Sub-limit enforcement
│   ├── static/style.css
│   └── templates/
│       ├── index.html
│       ├── signup.html
│       ├── login.html
│       ├── dashboard.html
│       ├── setup.html
│       ├── pricing.html
│       ├── admin.html
│       └── admin_user.html
├── litellm/
│   └── config.yaml           # Provider definitions + routing
├── nginx/
│   └── default.conf
└── scripts/
    ├── init-db.sql           # PostgreSQL init (creates extensions only)
    └── setup.sh              # One-command deploy
```

## Test Commands

```bash
# Health
curl http://localhost:5000/health

# Models
curl http://localhost:5000/v1/models

# Signup
curl -X POST http://localhost:5000/signup \
  -d "email=test@test.com&password=test1234&plan=starter"

# Login
curl -c cookies.txt -X POST http://localhost:5000/login \
  -d "email=test@test.com&password=test1234"

# Dashboard
curl -b cookies.txt http://localhost:5000/dashboard

# Admin
curl -b cookies.txt http://localhost:5000/admin
```

## Git Setup

```bash
cd /root/nectar
git init
git add -A
git commit -m "Initial Nectar API build"

# Push to private remote
gh repo create nectar --private --push
# OR
git remote add origin git@your-server:nectar.git
git push -u origin master
```
