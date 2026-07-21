# LiteLLM Smart Routing Configuration

## Pattern: multiple backends per model name with auto-fallback

When you have multiple free API providers, register them under the **same model name**. LiteLLM's router automatically load-balances and fails over between them.

```yaml
model_list:
  # All three backends share model name "kase-free"
  # Router picks one per request (simple-shuffle) and retries on others if it fails
  - model_name: kase-free
    litellm_params:
      model: openai/nemotron-3-ultra-free
      api_base: https://provider1.example/v1
      api_key: os.environ/PROVIDER1_KEY
      rpm: 3
      timeout: 120

  - model_name: kase-free
    litellm_params:
      model: openai/deepseek-v4-flash-free
      api_base: https://provider2.example/v1
      api_key: os.environ/PROVIDER2_KEY
      rpm: 3
      timeout: 120

  - model_name: kase-free
    litellm_params:
      model: openai/mimo-v2.5-free
      api_base: https://provider3.example/v1
      api_key: os.environ/PROVIDER3_KEY
      rpm: 3
      timeout: 120

router_settings:
  routing_strategy: simple-shuffle  # Round-robin with randomization
  num_retries: 3                    # Retry on different backend if one fails
  timeout: 120                      # Per-request timeout (seconds)
  cooldown_time: 300                # Skip failed backend for 5 minutes
  allowed_fails: 2                  # Failures before cooldown triggers
  retry_after: 5                    # Seconds between retries
  enable_pre_call_checks: true      # Check RPM limits before sending

litellm_settings:
  drop_params: true                 # Drop unsupported params instead of erroring
  request_timeout: 120
  set_verbose: false
```

## Model group strategy

Create multiple model names for different use cases:

| Model name | Purpose | Backends |
|-----------|---------|----------|
| `kase-free` | Best general purpose | All providers |
| `kase-fast` | Speed-first | Fastest providers only |
| `kase-code` | Code-specialized | Code-optimized providers |
| `kase-smart` | Auto-fallback across everything | ALL providers (most resilient) |

For Hermes, use `kase-smart` — it tries every backend before giving up.

## How the failover works

1. Request arrives for `kase-free`
2. Router picks a backend via `simple-shuffle`
3. If the backend returns 429/500/timeout → router retries on the **next** backend
4. After `allowed_fails` failures on one backend → it enters cooldown for `cooldown_time` seconds
5. During cooldown, that backend is skipped entirely
6. After cooldown, it's retried again

This means: **if one provider is down, requests automatically route to others. No manual intervention needed.**

## General settings for personal use

```yaml
general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY  # API auth key
  disable_spend_logs: true                     # No spend tracking needed
  ui_username: os.environ/UI_USERNAME         # Dashboard login
  ui_password: os.environ/UI_PASSWORD         # Dashboard login
```

## Environment file

```bash
# ~/.config/kasellm.env
LITELLM_MASTER_KEY=sk-your-master-key
PROVIDER1_KEY=sk-provider1-key
PROVIDER2_KEY=sk-provider2-key
PROVIDER3_KEY=sk-provider3-key
DATABASE_URL=postgresql://user:pass@127.0.0.1:5432/litellm
UI_USERNAME=admin
UI_PASSWORD=your-strong-password
```

## Verifying routing works

```bash
# Test that the model responds (picks a random backend)
curl -sk https://domain/v1/chat/completions \
  -H "Authorization: Bearer $MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"kase-smart","messages":[{"role":"user","content":"hello"}],"max_tokens":10}'

# Check which models are registered
curl -sk https://domain/v1/models -H "Authorization: Bearer $MASTER_KEY" | jq '.data[].id'

# Check health
curl -sk https://domain/health/liveliness
```
