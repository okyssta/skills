# LiteLLM Admin UI on Unusual Ports: Runbook

Use when exposing a LiteLLM/OpenAI-compatible proxy on a non-standard public HTTPS port such as `:8443`, `:38443`, `:2053`, or `:2087`, especially when the dashboard must work in a browser.

## Key lessons

- DNS cannot bind a hostname to a port. Users must include the port in the URL, e.g. `https://llm.example.com:8443/ui/`.
- Preserve the original Host header including the port. If Nginx sends `Host: llm.example.com` instead of `Host: llm.example.com:8443`, LiteLLM may generate bad redirects like `https://llm.example.com/ui/login/...` that fall back to port 443.
- LiteLLM's Admin UI is not just static HTML. The UI calls backend routes such as `/v2/login` and `/litellm/.well-known/litellm-ui-config`; if Nginx only proxies `/ui` and `/v1`, the browser sees errors like `Unexpected token '<', "<html> <h"... is not valid JSON` because it received an Nginx HTML 404 instead of JSON.
- Admin UI username/password login requires a database for UI session/virtual-key generation. Without DB, real login can fail with `Authentication Error, Not connected to DB!` even though API calls using the master key work.
- A source-built LiteLLM checkout may not include the built dashboard assets. `/ui` can 500 with `StaticFiles directory '.../litellm/proxy/_experimental/out' does not exist` until the dashboard is built and copied.

## Known-good Nginx headers for unusual HTTPS ports

Inside every proxied LiteLLM location, use:

```nginx
proxy_set_header Host $http_host;
proxy_set_header X-Forwarded-Host $http_host;
proxy_set_header X-Forwarded-Port $server_port;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header Authorization $http_authorization;
```

`$http_host` is the important part: it keeps `host:port` intact.

## Routes to proxy for the dashboard

At minimum, public Nginx should proxy:

```nginx
location ^~ /ui { proxy_pass http://127.0.0.1:4000; ... }
location ^~ /litellm-asset-prefix/ { proxy_pass http://127.0.0.1:4000; ... }
location ^~ /sso/ { proxy_pass http://127.0.0.1:4000; ... }
location ^~ /v2/ { proxy_pass http://127.0.0.1:4000; ... }
location ^~ /litellm/ { proxy_pass http://127.0.0.1:4000; ... }
location ^~ /get/ { proxy_pass http://127.0.0.1:4000; ... }
location ^~ /public/ { proxy_pass http://127.0.0.1:4000; ... }
location ^~ /user/ { proxy_pass http://127.0.0.1:4000; ... }
location ^~ /key/ { proxy_pass http://127.0.0.1:4000; ... }
location ^~ /team/ { proxy_pass http://127.0.0.1:4000; ... }
location ^~ /model/ { proxy_pass http://127.0.0.1:4000; ... }
location ^~ /config/ { proxy_pass http://127.0.0.1:4000; ... }
```

Avoid relying only on a regex `location ~ ...` if a later prefix/fallback location may preempt what the UI expects. Verify the exact failing browser endpoint with Nginx access logs, then add an explicit prefix location.

## Build the Admin UI assets from a source checkout

From the LiteLLM repo:

```bash
cd /path/to/litellm/ui/litellm-dashboard
npm ci
npm run build
rm -rf /path/to/litellm/litellm/proxy/_experimental/out
mkdir -p /path/to/litellm/litellm/proxy/_experimental
cp -r out /path/to/litellm/litellm/proxy/_experimental/out
systemctl --user restart litellm-free.service
```

Verify:

```bash
curl -LsS -o /tmp/ui.html -w '%{http_code} %{content_type}\n' http://127.0.0.1:4000/ui/
```

Expected: `200 text/html`.

## Local PostgreSQL + Prisma for Admin UI login

LiteLLM UI login needs `DATABASE_URL`. One workable local setup:

```bash
apt-get update
apt-get install -y postgresql postgresql-contrib
pg_ctlcluster 16 main start
DB_PASS=$(python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(32))
PY
)
su - postgres -c "psql -v ON_ERROR_STOP=1" <<SQL
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'litellm') THEN
      CREATE ROLE litellm LOGIN PASSWORD '$DB_PASS';
   ELSE
      ALTER ROLE litellm WITH LOGIN PASSWORD '$DB_PASS';
   END IF;
END
\$\$;
SELECT 'CREATE DATABASE litellm OWNER litellm' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'litellm')\gexec
GRANT ALL PRIVILEGES ON DATABASE litellm TO litellm;
SQL
```

Add to the private LiteLLM env file:

```bash
DATABASE_URL=postgresql://litellm:<password>@127.0.0.1:5432/litellm
```

Then in the LiteLLM venv:

```bash
cd /path/to/litellm
. .venv/bin/activate
python -m pip install prisma psycopg2-binary
set -a; . /path/to/litellm.env; set +a
python -m prisma generate --schema=litellm/proxy/schema.prisma
python -m prisma db push --schema=litellm/proxy/schema.prisma --accept-data-loss
systemctl --user restart litellm-free.service
```

## Verification sequence

```bash
# Dashboard static page
curl -k -LsS -o /tmp/ui.html -w '%{http_code} %{content_type}\n' https://llm.example.com:8443/ui/

# Dashboard config must be JSON, not an HTML 404
curl -k -sS -o /tmp/uiconfig.json -w '%{http_code} %{content_type}\n' https://llm.example.com:8443/litellm/.well-known/litellm-ui-config

# Login failure must be JSON 401, not HTML
curl -k -sS -o /tmp/login.json -w '%{http_code} %{content_type}\n' \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"wrong"}' \
  https://llm.example.com:8443/v2/login

# Real login should return JSON with token/redirect_url
set -a; . /path/to/litellm.env; set +a
curl -k -sS -o /tmp/login-real.json -w '%{http_code} %{content_type}\n' \
  -H 'Content-Type: application/json' \
  -d "{\"username\":\"admin\",\"password\":\"$LITELLM_MASTER_KEY\"}" \
  https://llm.example.com:8443/v2/login
```

Expected:

- `/ui/` -> `200 text/html`
- `/litellm/.well-known/litellm-ui-config` -> `200 application/json`
- wrong `/v2/login` -> `401 application/json`
- real `/v2/login` -> `200 application/json` with a token

## Diagnosing claimed closed ports

Check both local and external evidence:

```bash
ss -ltnp | grep -E ':8443|:38443|:2053|:2087|:4000'
iptables -S INPUT
nft list ruleset | grep -E 'hook input|policy|dport'
dig @1.1.1.1 +short llm.example.com A
curl -vk https://llm.example.com:8443/health/liveliness
```

If server-side curl and external web fetchers reach the port but the user cannot, it is usually client-side DNS/network policy or outbound non-standard-port filtering. If broad browser compatibility is required, use port 443 with a less-obvious path plus bearer auth instead of unusual ports.
