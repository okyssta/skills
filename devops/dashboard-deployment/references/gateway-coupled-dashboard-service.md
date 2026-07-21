# Gateway-coupled dashboard service

Use this pattern when the user expects the web dashboard to come back automatically whenever the Hermes gateway is started or restarted.

## User systemd unit

Create `~/.config/systemd/user/hermes-dashboard.service`:

```ini
[Unit]
Description=Hermes Agent Web Dashboard
After=network-online.target
Wants=network-online.target
PartOf=hermes-gateway.service

[Service]
Type=simple
ExecStart=/usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main dashboard --host 0.0.0.0 --port 9119 --skip-build --no-open
WorkingDirectory=/root/.hermes
Environment="HOME=/root"
Environment="USER=root"
Environment="LOGNAME=root"
Environment="PATH=/usr/local/lib/hermes-agent/venv/bin:/usr/local/lib/hermes-agent/node_modules/.bin:/root/.hermes/node/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="VIRTUAL_ENV=/usr/local/lib/hermes-agent/venv"
Environment="HERMES_HOME=/root/.hermes"
Environment="HERMES_DASHBOARD_PUBLIC_URL=https://your.domain.com"
EnvironmentFile=-/root/.hermes/.env
Restart=always
RestartSec=5
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=90
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target hermes-gateway.service
```

Then:

```bash
systemctl --user daemon-reload
systemctl --user enable --now hermes-dashboard.service
systemctl --user enable hermes-gateway.service
```

`WantedBy=hermes-gateway.service` creates `hermes-gateway.service.wants/hermes-dashboard.service`, so starting the gateway pulls in the dashboard. `PartOf=hermes-gateway.service` makes gateway stop/restart propagate to the dashboard.

## Public domain / host-header pitfall

When Nginx proxies a public domain such as `https://your.domain.com` to dashboard port `9119`, binding the dashboard to `127.0.0.1` can produce:

```text
HTTP/1.1 400 Bad Request
{"detail":"Invalid Host header. Dashboard requests must use the hostname the server was bound to."}
```

The dashboard validates Host headers. For reverse-proxied public domains, bind the dashboard to `0.0.0.0` and rely on the dashboard auth gate plus Nginx/firewall controls. Register OAuth first:

```bash
hermes dashboard register --redirect-uri https://your.domain.com/auth/callback
```

This writes `HERMES_DASHBOARD_OAUTH_CLIENT_ID` and `HERMES_DASHBOARD_PUBLIC_URL` to `.env`.

## Verification

```bash
systemctl --user show hermes-dashboard.service -p ActiveState -p SubState -p MainPID -p PartOf -p WantedBy --no-pager
ss -ltnp | grep ':9119\b'
curl -sS -D - https://your.domain.com/ -o /tmp/dashboard.html | sed -n '1,40p'
curl -sS -D - 'https://your.domain.com/auth/login?provider=nous&next=%2F' -o /tmp/login.html | sed -n '1,60p'
```

Expected public-domain behavior before login is a `302` to `/auth/login?provider=nous&next=%2F`, then a `302` from that URL to Nous Portal OAuth with `redirect_uri=https://your.domain.com/auth/callback`.

## Gateway-session caveat

Do not run `systemctl --user restart hermes-gateway.service` from inside a live gateway-handled tool call: restarting the gateway kills the command subtree before it can finish. If you need to apply a dashboard-only unit change while operating from the gateway, restart only the dashboard service, or terminate the dashboard MainPID and let `Restart=always` bring it back.