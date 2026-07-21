# LiteLLM Deployment Pitfalls

## Admin UI requires UI_USERNAME and UI_PASSWORD env vars

**Symptom**: Login at `/ui/login/` returns "Invalid credentials used to access UI. Check 'UI_USERNAME', 'UI_PASSWORD' in .env file" even with the correct master key.

**Cause**: LiteLLM's Admin UI uses separate `UI_USERNAME` and `UI_PASSWORD` environment variables for dashboard login — the `LITELLM_MASTER_KEY` is for API authentication, not the dashboard.

**Fix**: Add both to the `.env` file (e.g. `~/.config/litellm-free.env`):

```
UI_USERNAME=admin
UI_PASSWORD=your-strong-password-here
```

Then restart the service:
```bash
systemctl --user restart kase-free.service
```

**Verify** with the `/v2/login` endpoint (this is what the UI calls):
```bash
curl -sk -X POST https://your-domain/v2/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}' \
  -w "\nHTTP %{http_code}"
# Should return {"redirect_url":"...","token":"eyJ..."} with HTTP 200
```

## Recovering lost env secrets from a running process

If you accidentally overwrite the env file, recover the original values from the running process before restarting:

```bash
PID=$(pgrep -f "proxy_cli.py" | head -1)
cat /proc/$PID/environ | tr '\0' '\n' | grep "LITELLM_MASTER_KEY="
cat /proc/$PID/environ | tr '\0' '\n' | grep "OPENCODE_ZEN_API_KEY="
# ... etc
```

Then write them back to the env file. **Never restart the service before recovering** — the old env vars are lost once the process exits.

## Updating Hermes provider URL when changing ports

When moving LiteLLM from an unusual port (e.g. `:8443`) to standard HTTPS (port 443, no port in URL), update the Hermes provider config:

```bash
# In ~/.hermes/config.yaml, change:
#   base_url: https://llm.example.com:8443/v1
# To:
#   base_url: https://llm.example.com/v1
sed -i 's|https://llm.example.com:8443/v1|https://llm.example.com/v1|g' ~/.hermes/config.yaml
```

No Hermes restart needed — the config is re-read on next request.

## Env file duplication when appending

**Pitfall**: Running `echo 'VAR=val' >> file.env` twice creates duplicate entries. The last value wins for most env parsers, but some (like systemd's `EnvironmentFile`) may behave unexpectedly.

**Fix**: Always check before appending:
```bash
grep -c "UI_USERNAME" /root/.config/litellm-free.env || echo 'UI_USERNAME=admin' >> /root/.config/litellm-free.env
```
