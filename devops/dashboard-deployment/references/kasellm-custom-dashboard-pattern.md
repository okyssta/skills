# Custom Dashboard Replacement Pattern

When the user wants a full rebrand ("rebrand everything, new UI, new stuff"), the cleanest approach is to **bypass LiteLLM's Next.js UI entirely** and serve a lightweight custom HTML dashboard from Nginx.

## Why this approach

- Patching the React/Next.js UI is fragile (minified JS, RSC payloads, compiled chunks)
- A single HTML file with inline CSS/JS has zero build step, loads instantly, and is trivial to customize
- Nginx can serve the static file directly while proxying API calls to LiteLLM

## Architecture

```
Browser → https://domain/ui/  → Nginx serves /var/www/custom/index.html
Browser → https://domain/v1/  → Nginx proxies → 127.0.0.1:4000 (LiteLLM)
Browser → https://domain/health → Nginx proxies → 127.0.0.1:4000
```

## Nginx config pattern

```nginx
server {
    listen 443 ssl http2;
    server_name your.domain.com;
    ssl_certificate /etc/letsencrypt/live/your.domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your.domain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Custom dashboard
    location /ui/ {
        alias /var/www/custom-dashboard/;
        try_files $uri $uri/ =404;
        add_header Cache-Control "no-cache";
    }
    location = /ui { return 301 /ui/; }

    # API proxy
    location /v1/ {
        if ($http_authorization = "") {
            return 401 '{"error":{"message":"Missing Authorization header"}}';
        }
        proxy_pass http://127.0.0.1:4000;
        proxy_http_version 1.1;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Authorization $http_authorization;
        proxy_read_timeout 300s;
    }

    location /v2/ { proxy_pass http://127.0.0.1:4000; ... }
    location /key/ { proxy_pass http://127.0.0.1:4000; ... }
    location /health/ { proxy_pass http://127.0.0.1:4000; }
    location = / { return 302 /ui/; }
}
```

**Pitfall**: `alias /path/to/file.html;` doubles the filename when the location has a trailing slash. Always use `alias /path/to/directory/;` with `try_files`.

## Dashboard design principles (personal use)

- **Single HTML file** — all CSS and JS inline, no build step
- **Matte dark theme** — flat colors (#0d1117 bg, #161b22 cards, #30363d borders, #58a6ff accent)
- **NO gradients, NO large rounded corners, NO shadows, NO animations** — flat and clean
- **Tab navigation** — Overview, Models, Keys, Quick Start, Settings
- **Auth** — Bearer token stored in localStorage, prompted on first visit
- **API integration** — fetch /v1/models, /health/liveliness, /key/list with auth header
- **Footer** — just "ProductName • Personal LLM Router"

## LiteLLM API endpoints the dashboard needs

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/health/liveliness` | GET | No | Health check (returns `"I'm alive!"`) |
| `/health` | GET | Yes | Detailed health with model endpoint status |
| `/v1/models` | GET | Yes | List available model names |
| `/user/info` | GET | Yes | User info: user_id, role, spend, teams |
| `/model/info` | GET | Yes | Detailed model info with params |
| `/v2/login` | POST | No | Login (returns `{redirect_url, token}`) |

**Endpoints that do NOT exist** (returns 404):
- `/v2/info` — use `/user/info` or `/health` instead
- `/key/list` — requires DB keys table setup
- `/key/generate` — requires DB keys table setup

**Note**: The login endpoint is `/v2/login`, NOT `/ui/login`. The UI's React app calls this internally.

## Browser verification pattern

After deploying a custom dashboard, use Playwright to verify every tab loads correctly:

```bash
cd /tmp && npm install playwright
node -e "
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  page.on('response', r => { if (r.status() >= 400) console.log('ERR', r.status(), r.url()); });
  await page.goto('https://domain/ui/', { timeout: 30000 });
  const input = await page.\$('input');
  if (input) { await input.fill(process.env.MASTER_KEY); await page.\$('button').then(b => b?.click()); }
  await page.waitForTimeout(5000);
  await page.screenshot({ path: '/tmp/dashboard.png', fullPage: true });
  await browser.close();
})();
"
```

Use `vision_analyze` on screenshots to check that data loads without red error text.
