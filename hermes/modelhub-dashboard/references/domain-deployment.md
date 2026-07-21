# ModelBench Domain Deployment

Live URLs: **https://model.kyssta.lol** and **https://modelbench.lol**

## DNS

- A records: both domains → `139.185.45.163` (same VPS)
- Must resolve before Certbot can verify ownership

## Deployment Stack

- **App**: Docker Compose (PostgreSQL + Gunicorn/Flask + Updater)
- **Reverse Proxy**: Nginx on host → `127.0.0.1:5050`
- **SSL**: Let's Encrypt via Certbot (auto-renewal timer active)

## Adding a New Domain (Quick Copy)

When the same backend serves multiple domains, fastest approach:

```bash
# 1. Copy existing config, replace domain name
cp /etc/nginx/sites-available/primary.domain /etc/nginx/sites-available/new.domain
sed -i 's/primary\.domain/new.domain/g' /etc/nginx/sites-available/new.domain

# 2. WARNING: The copied config has SSL cert paths for the OLD domain.
#    For the first Certbot run, temporarily strip SSL lines so nginx -t passes:
cat > /etc/nginx/sites-available/new.domain << 'NGINXCONF'
server {
    server_name new.domain;
    location / {
        proxy_pass http://127.0.0.1:5050;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }
    listen 80;
}
NGINXCONF

# 3. Enable and test
ln -sf /etc/nginx/sites-available/new.domain /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# 4. Get cert (Certbot rewrites the config with SSL + redirect)
certbot --nginx -d new.domain --agree-tos --email admin@domain.com

# 5. Verify both domains serve the same app
curl -s -o /dev/null -w "%{http_code}" https://new.domain/
curl -s -o /dev/null -w "%{http_code}" https://primary.domain/
```

**WARNING**: Do NOT include SSL cert paths from the old domain in the initial config. Certbot's `--nginx` plugin adds the correct SSL directives for the new domain. If you pre-write SSL lines pointing to non-existent certs, `nginx -t` will fail with `cannot load certificate: No such file or directory`.

## Certbot Setup (First Domain)

```bash
# Step 1: Create Nginx config with ONLY port 80 initially (no SSL lines)
cat > /etc/nginx/sites-available/domain.com << 'EOF'
server {
    server_name domain.com;
    location / {
        proxy_pass http://127.0.0.1:5050;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }
    listen 80;
}
EOF

# Step 2: Enable site and reload
ln -sf /etc/nginx/sites-available/domain.com /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# Step 3: Get cert (Certbot auto-adds SSL directives + redirect to the config)
certbot --nginx -d domain.com --agree-tos --email admin@domain.com

# Step 4: Verify the final config has both 443 SSL and 80→301 redirect blocks
nginx -t
```

## Verification

```bash
# Health endpoint
curl https://domain.com/health
# → {"service":"ModelBench","status":"ok"}

# Main page
curl -s -o /dev/null -w "%{http_code}" https://domain.com/
# → 200

# API
curl -s https://domain.com/api/models | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d))"

# Container status
docker compose -f /root/modelhub/docker-compose.yml ps
# All 3 containers should show "Up" / "healthy"
```

## Obsolete Cron Job

The old `c7bf189ac4a7` cron job (daily SQLite-based update via cron/update_data.sh) is now **obsolete** — the Docker updater container scrapes every 5 minutes. It should be removed via `cronjob(action='remove', job_id='c7bf189ac4a7')`.
