# Key Stacking Guide — Multiplying Free Quotas

**How to use multiple API keys per provider to multiply rate limits 3-5x.**

---

## The Concept

Most free tiers limit by **API key**, not by user/account. By generating multiple keys for the same provider and adding them to `credential_pools`, Hermes rotates through them automatically when one hits its rate limit.

---

## How It Works

```yaml
credential_pools:
  openrouter:
    - env: OPENROUTER_API_KEY        # Key 1: 200 req/day
    - env: OPENROUTER_API_KEY_2      # Key 2: 200 req/day
    - env: OPENROUTER_API_KEY_3      # Key 3: 200 req/day
  groq:
    - env: GROQ_API_KEY              # Key 1: 1K req/day
    - env: GROQ_API_KEY_2            # Key 2: 1K req/day
```

When `OPENROUTER_API_KEY` hits 429, Hermes automatically tries `OPENROUTER_API_KEY_2`, then `OPENROUTER_API_KEY_3`. This is **credential pool rotation** — different from cross-provider fallback.

---

## Step-by-Step: Getting Multiple Keys

### OpenRouter (Best for stacking — 200 req/day per key)
1. Go to https://openrouter.ai/keys
2. Click "Create Key" → name it "hermes-1"
3. Create 2-3 more keys: "hermes-2", "hermes-3", "hermes-4"
4. Add to `.env`:
   ```
   OPENROUTER_API_KEY=sk-or-v1-xxxx
   OPENROUTER_API_KEY_2=sk-or-v1-yyyy
   OPENROUTER_API_KEY_3=sk-or-v1-zzzz
   ```

### Groq (1K req/day per key)
1. Go to https://console.groq.com/keys
2. Create multiple keys
3. Add to `.env`:
   ```
   GROQ_API_KEY=gsk_xxxx
   GROQ_API_KEY_2=gsk_yyyy
   ```

### Google AI Studio (1,500 RPD per key)
1. Go to https://aistudio.google.com/apikey
2. Create multiple API keys (different projects)
3. Add to `.env`:
   ```
   GOOGLE_API_KEY=AIzaSyxxxx
   GOOGLE_API_KEY_2=AIzaSyyyy
   ```

### NVIDIA NIM (40 RPM, credits-based)
1. Go to https://build.nvidia.com/
2. Generate multiple API keys
3. Add to `.env`:
   ```
   NVIDIA_API_KEY=xxxx
   NVIDIA_API_KEY_2=yyyy
   ```

### OpenCode Zen (Free period)
1. Go to https://opencode.ai/auth
2. Sign in, get API key
3. One key typically sufficient (unlimited during free period)

### NovitaAI (Free credits)
1. Go to https://novita.ai/
2. Sign up, get API key
2. Free credits on signup

### Hugging Face (Monthly credits)
1. Go to https://huggingface.co/settings/tokens
2. Create token with "Inference" permission
3. One token typically sufficient

### GitHub Models (GitHub token)
1. Go to https://github.com/settings/tokens
2. Create classic token with `models` scope
3. One token per GitHub account

---

## Multiplier Effect

| Provider | 1 Key | 3 Keys | 5 Keys | Notes |
|----------|-------|--------|--------|-------|
| OpenRouter | 50/day | 150/day | 250/day | $10 top-up makes each 1K/day |
| Groq | 1K/day | 3K/day | 5K/day | Token budget still binds |
| Google | 1.5K/day | 4.5K/day | 7.5K/day | Per-project limits |
| NVIDIA | Credits | 3x credits | 5x credits | Credits don't expire |

---

## Configuration in Hermes

### Option 1: Credential Pools (Automatic Rotation)
```yaml
credential_pools:
  openrouter:
    - env: OPENROUTER_API_KEY
    - env: OPENROUTER_API_KEY_2
    - env: OPENROUTER_API_KEY_3
  groq:
    - env: GROQ_API_KEY
    - env: GROQ_API_KEY_2
```

### Option 2: Multiple Fallback Entries (Explicit)
```yaml
fallback_providers:
  - provider: openrouter
    model: nvidia/nemotron-3-ultra-550b-a55b:free
    # Uses OPENROUTER_API_KEY
  - provider: openrouter
    model: nvidia/nemotron-3-ultra-550b-a55b:free
    # Uses OPENROUTER_API_KEY_2 (if configured in credential_pools)
```

**Credential pools are preferred** — they handle rotation automatically within the same provider entry.

---

## Best Practices

1. **Use different email/account per key** — Some providers track by account, not just key
2. **Label keys clearly** — "hermes-main", "hermes-backup-1", "hermes-backup-2"
3. **Monitor usage** — Check OpenRouter dashboard to see which key is being used
4. **Rotate periodically** — If a key gets flagged, replace it
5. **Don't over-stack** — 3-5 keys is plenty; more adds management overhead
6. **Combine with fallback chain** — Key stacking extends each layer; fallback chain moves to next layer

---

## Verification

```bash
# Check credential pools are loaded
hermes doctor

# Should show:
# ✓ OpenRouter API (multiple keys in pool)
# ✓ Groq API (multiple keys in pool)

# Test rotation by simulating rate limit (or wait for natural)
# Logs will show: "Rotating to next credential in pool: OPENROUTER_API_KEY_2"
```

---

## Pitfalls

- **Some providers track by IP/account** — Multiple keys from same IP may share limits
- **Google AI Studio** — Keys from same Google Cloud project share quota; use different projects
- **OpenRouter $10 top-up** — Applies per account, not per key. One top-up upgrades all keys on that account.
- **Credential pool rotation is same-provider only** — Cross-provider fallback uses `fallback_providers`
- **Keys in `.env` must match `env:` exactly** — Case sensitive

---

## Quick Reference: Keys Needed for 10x Free Capacity

| Provider | Keys to Create | Total Daily Reqs | Setup Time |
|----------|----------------|------------------|------------|
| OpenRouter | 5 | 250 (2,500 with $10) | 5 min |
| Groq | 3 | 3,000 | 3 min |
| Google AI Studio | 3 | 4,500 | 5 min |
| NVIDIA NIM | 3 | 3x credits | 3 min |
| **Total** | **14 keys** | **~10K+ req/day** | **~15 min** |

This gives you ~10x the free capacity of a single key setup.