# LiteLLM unusual-port deployment and dashboard UI notes

Use these notes when exposing a local LiteLLM proxy on non-standard ports or when the LiteLLM admin UI/dashboard returns 500/404.

## Non-standard public ports

DNS cannot bind a hostname to a port. If the user wants to avoid ports 80/443, the URL must include the port, e.g.:

```text
https://llm.example.com:8443/
https://llm.example.com:8443/v1
```

A practical Nginx shape is:

- LiteLLM itself stays private on `127.0.0.1:4000`.
- Nginx listens publicly on one or more unusual HTTPS ports such as `8443`, `38443`, `2053`, `2087`.
- Optional unusual HTTP ports such as `8080`, `18080`, `38080` redirect to the primary HTTPS port.
- Standard `80`/`443` can return `444` or redirect, but if the user needs broad browser/network compatibility, `443` is still the most reliable choice.

Example listen block:

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

    location = /health/liveliness { proxy_pass http://127.0.0.1:4000/health/liveliness; }
    location ^~ /v1/ { proxy_pass http://127.0.0.1:4000; }
}
```

## Diagnosing “ports are closed”

Check from several layers before changing config:

```bash
ss -ltnp | grep -E ':8443|:38443|:2053|:2087|:4000'
ufw status verbose || true
systemctl is-active firewalld || true
iptables -S INPUT
nft list ruleset | grep -E 'hook input|policy|dport'
dig @1.1.1.1 +short llm.example.com A
dig @8.8.8.8 +short llm.example.com A
curl -fsS https://llm.example.com:8443/health/liveliness
```

Use an external web fetch or third-party TCP checker when available, then inspect `/var/log/nginx/access.log`. If access logs show outside IPs returning `200`, the server and cloud ingress are reachable; a single user still failing is likely client DNS cache, ISP/router policy, VPN/adblock/security software, or outbound non-standard port blocking.

## LiteLLM dashboard / UI build pitfall

In a source checkout, `/ui` may fail with:

```text
RuntimeError: StaticFiles directory '.../litellm/proxy/_experimental/out' does not exist
```

Fix by building the dashboard and copying its static export to the path LiteLLM serves:

```bash
cd /path/to/litellm/ui/litellm-dashboard
npm ci
npm run build
rm -rf /path/to/litellm/litellm/proxy/_experimental/out
mkdir -p /path/to/litellm/litellm/proxy/_experimental
cp -r out /path/to/litellm/litellm/proxy/_experimental/out
systemctl --user restart litellm-free.service
```

**CRITICAL PITFALL**: The proxy reads UI from `litellm/proxy/_experimental/out/`, NOT from `ui/litellm-dashboard/out/`. When rebranding or patching the UI, always patch files in `_experimental/out/`. Patching `ui/litellm-dashboard/out/` has zero effect on what users see. This is the single most time-wasting mistake in LiteLLM UI customization.

Then expose these paths through Nginx in addition to `/v1/` and health:

```nginx
location = /ui { return 301 https://$host:8443/ui/; }
location ^~ /ui { proxy_pass http://127.0.0.1:4000; }
location ^~ /litellm-asset-prefix/ { proxy_pass http://127.0.0.1:4000; }
location ^~ /sso/ { proxy_pass http://127.0.0.1:4000; }
```

Verify:

```bash
curl -LsS -o /tmp/ui.html -w '%{http_code} %{content_type}\n' https://llm.example.com:8443/ui/
curl -fsS https://llm.example.com:8443/health/liveliness
```

The dashboard URL needs the trailing slash: `/ui/`.

## Rebranding the compiled UI (no rebuild needed)

To replace all visible branding (e.g. "LiteLLM" → "KaseLLM") in a pre-built static export, patch the files in `_experimental/out/` directly. This works on minified JS and RSC payload `.txt` files without breaking functionality:

```bash
OUT=/path/to/litellm/litellm/proxy/_experimental/out

# Replace brand name in HTML, JS, and RSC payload files
find "$OUT" -type f \( -name "*.html" -o -name "*.js" -o -name "*.txt" \) \
  -exec grep -l "LiteLLM" {} \; \
  -exec sed -i 's/LiteLLM/KaseLLM/g' {} +

# Verify zero references remain
grep -rl "LiteLLM" "$OUT" --include="*.html" --include="*.js" --include="*.txt" | wc -l
# Should print 0
```

After patching, no service restart is needed — the static files are served directly by FastAPI's `StaticFiles`.

## Injecting dark mode into pre-built static HTML

To add a dark/light theme toggle without rebuilding the Next.js app, inject a CSS file and a toggle script into all HTML files in `out/`:

1. Create `dark-mode.css` in `out/_next/static/chunks/` with Ant Design dark theme overrides (dark backgrounds, light text for `.ant-card`, `.ant-table`, `.ant-layout-sider`, `.ant-input`, etc.)
2. Create `dark-toggle.js` in the same directory — a self-contained IIFE that loads the CSS, reads/writes `localStorage` for theme preference, and appends a floating toggle button (`position:fixed; bottom:20px; right:20px`)
3. Inject the script tag into every HTML file:
```bash
find "$OUT" -name "*.html" -exec \
  sed -i 's|</head>|<script src="/litellm-asset-prefix/_next/static/chunks/dark-toggle.js"></script></head>|' {} \;
```

## Standard port + backup unusual ports pattern

When the user wants `https://domain.com` (no port) but also wants unusual ports as fallback, use separate Nginx `server` blocks sharing the same cert:

```nginx
# Primary: standard HTTPS
server {
    listen 443 ssl http2;
    server_name llm.example.com;
    ssl_certificate /etc/letsencrypt/live/llm.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/llm.example.com/privkey.pem;
    # ... proxy rules to 127.0.0.1:4000 ...
}

# HTTP redirect
server {
    listen 80;
    server_name llm.example.com;
    return 301 https://$host$request_uri;
}

# Backup: unusual ports (same cert, same proxy rules)
server {
    listen 8443 ssl;
    listen 38443 ssl;
    listen 2053 ssl;
    listen 2087 ssl;
    server_name llm.example.com;
    ssl_certificate /etc/letsencrypt/live/llm.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/llm.example.com/privkey.pem;
    # ... same proxy rules ...
}
```
