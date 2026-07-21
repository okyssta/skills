# Deploying a LiteLLM/OpenAI-Compatible Proxy Behind Nginx

Use this reference when a user asks to fork/clone/run an LLM gateway "here" and expose it on a domain. The key lesson is to finish with a running, verified service, not only a fork or plan.

## Expected workflow

1. Confirm the repo is cloned locally and remotes are correct.
2. Install runtime dependencies in an isolated venv under the clone.
3. Create a minimal LiteLLM config with safe aliases; prefer stable aliases like `llm-free`, `llm-free-fast`, and `llm-free-code` instead of provider-specific model IDs in downstream clients.
4. Store provider keys and the LiteLLM master key in a private env file such as `~/.config/litellm-free.env`; never commit it.
5. Run the proxy bound to localhost first and verify `/health/liveliness`, `/v1/models`, and `/v1/chat/completions`.
6. Install a user systemd service with `Restart=always` and verify it stays active.
7. Add an Nginx site for the requested domain, proxying to the localhost port with long read/send timeouts.
8. Use certbot to enable HTTPS when serving HTTPS on a named domain.
9. Verify the public domain with an authenticated OpenAI-compatible chat completion.
10. If Hermes should use it, add a named custom provider with `base_url: https://<domain>[:port]/v1`, `key_env: LITELLM_MASTER_KEY`, `api_mode: chat_completions`.

## Known-good LiteLLM service shape

```ini
[Unit]
Description=LiteLLM Free Model Router for Hermes
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/path/to/litellm
EnvironmentFile=/root/.config/litellm-free.env
ExecStart=/path/to/litellm/.venv/bin/python /path/to/litellm/litellm/proxy/proxy_cli.py --config /path/to/litellm/llm-free.config.yaml --host 127.0.0.1 --port 4000
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

## Standard HTTPS Nginx site shape

```nginx
server {
    listen 80;
    server_name llm.example.com;

    location / {
        proxy_pass http://127.0.0.1:4000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
        client_max_body_size 50m;
    }
}
```

Then run:

```bash
nginx -t
systemctl reload nginx
certbot --nginx -d llm.example.com --non-interactive --agree-tos --email admin@example.com --redirect
```

## Unusual-port deployment pattern

If the user does not want the proxy served on standard 80/443, keep LiteLLM bound to localhost and expose one or more unusual Nginx TLS listeners. The URL must include the port; DNS cannot bind a domain to a TCP port by itself.

Good candidates to try:

- `8443` primary HTTPS alternate
- `38443` high alternate HTTPS port
- `2053` and `2087` if the client/network allows Cloudflare-like alternate HTTPS ports
- `8080`, `18080`, or `38080` as HTTP redirect ports to the chosen HTTPS alternate

Example:

```nginx
server {
    listen 8443 ssl;
    listen 38443 ssl;
    listen 2053 ssl;
    listen 2087 ssl;
    server_name llm.example.com;

    ssl_certificate /etc/letsencrypt/live/llm.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/llm.example.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location = /health/liveliness {
        proxy_pass http://127.0.0.1:4000/health/liveliness;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ^~ /v1/ {
        if ($http_authorization = "") {
            return 401 '{"error":"missing Authorization: Bearer token"}';
        }
        proxy_pass http://127.0.0.1:4000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header Authorization $http_authorization;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
        client_max_body_size 50m;
    }

    location / {
        return 404;
    }
}

server {
    listen 8080;
    listen 18080;
    listen 38080;
    server_name llm.example.com;
    return 301 https://$host:8443$request_uri;
}
```

For standard ports, either leave them alone for another app, redirect them to the unusual port, or return `444` to close the connection. If you return `444`, verify with `curl --resolve` locally and with the public hostname; some curl output will show `000` or `Empty reply from server`, which is expected.

## Unusual ports and dashboard UI

For non-standard-port deployments and source-checkout dashboard fixes, see `references/litellm-unusual-ports-and-ui.md`. Key reminders:

- DNS cannot include a port; users must open URLs like `https://llm.example.com:8443/`.
- If `/ui` returns 500 with a missing `litellm/proxy/_experimental/out` directory, build `ui/litellm-dashboard` with `npm ci && npm run build`, copy `out/` into `litellm/proxy/_experimental/out`, restart LiteLLM, and proxy `/ui`, `/litellm-asset-prefix/`, and `/sso/` through Nginx.
- When a user says ports look closed, verify listeners, host firewall, public DNS, external fetch/TCP checks, and Nginx access logs before changing cloud/network config. If outside IPs hit Nginx with `200`, the remaining failure is likely on the user's client/network or outbound port policy.

## Verification commands

Avoid piping curl directly into an interpreter. Save JSON to a file, then parse it.

```bash
set -a; . /root/.config/litellm-free.env; set +a
curl -fsS https://llm.example.com:8443/health/liveliness
curl -fsS https://llm.example.com:8443/v1/models \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -o /tmp/llm-models.json
python3 -c 'import json; print([m["id"] for m in json.load(open("/tmp/llm-models.json"))["data"]])'
curl -fsS https://llm.example.com:8443/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"llm-free","messages":[{"role":"user","content":"Reply with exactly OK."}],"max_tokens":64}' \
  -o /tmp/llm-chat.json
python3 -c 'import json; print(json.load(open("/tmp/llm-chat.json"))["choices"][0]["message"].get("content"))'
```

Also verify from outside the machine if possible. Hermes `web_extract` can be a useful second path for simple health URLs. If a browser screenshot says `DNS_PROBE_POSSIBLE` or `DNS address could not be found`, do not assume a port/firewall issue; first compare authoritative/public resolver output:

```bash
dig @1.1.1.1 llm.example.com A +short
dig @8.8.8.8 llm.example.com A +short
```

If public resolvers resolve but the user's browser does not, tell them to clear local DNS/browser cache or try another network. If `curl` from the server succeeds but the user cannot reach a nonstandard port, suspect a client/ISP/cloud security-list block and add additional commonly allowed alternate ports or fall back to 443 with a hidden path.

## Firewall and cloud network checks

Local Linux firewalls are only one layer. Check all of these before claiming a port is open to the user:

```bash
ss -ltnp | grep -E ':8443|:38443|:4000|:80|:443'
ufw status verbose 2>/dev/null || true
iptables -S INPUT 2>/dev/null | sed -n '1,80p'
nft list ruleset 2>/dev/null | grep -E 'hook input|policy|dport'
```

On cloud VMs, the provider security list / network security group may still block unusual ports even if `iptables` is open. If CLI credentials are unavailable, make the uncertainty explicit and provide the exact inbound rules needed: TCP from the user's source or `0.0.0.0/0` to the selected ports.

## Systemd service rename pattern

When renaming a LiteLLM service (e.g. `litellm-free` → `kase-free`):

```bash
# 1. Create new service file with updated Description
cat > ~/.config/systemd/user/kase-free.service << 'EOF'
[Unit]
Description=KaseLLM Free Model Router for Hermes
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/path/to/litellm
EnvironmentFile=/root/.config/litellm-free.env
ExecStart=/path/to/litellm/.venv/bin/python /path/to/litellm/litellm/proxy/proxy_cli.py \
  --config /path/to/litellm/llm-free.config.yaml --host 127.0.0.1 --port 4000
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF

# 2. Enable new service
systemctl --user daemon-reload
systemctl --user enable kase-free.service

# 3. Stop old service (get user consent first — brief interruption)
systemctl --user stop litellm-free.service

# 4. Start new service
systemctl --user start kase-free.service

# 5. Verify
systemctl --user status kase-free.service
curl -fsS http://127.0.0.1:4000/health/liveliness
```

Note: The `EnvironmentFile` path and config file path don't need to change with the service name. Only the service file name and `Description` change.

## Free-model caveats

Free model names and rate limits are provider policy, not a durable guarantee. Treat free model routing as best-effort: configure multiple zero-cost deployments, low RPM caps, cooldowns, and fail closed instead of silently switching to paid inference.
