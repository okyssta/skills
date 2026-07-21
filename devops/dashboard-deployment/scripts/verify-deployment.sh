#!/usr/bin/env bash
# Verify Hermes dashboard deployment

set -euo pipefail

DOMAIN="${1:-}"
if [[ -z "$DOMAIN" ]]; then
    echo "Usage: $0 <domain>"
    exit 1
fi

echo "=== Verifying deployment for $DOMAIN ==="
echo

# 1. Check DNS resolution
echo "1. DNS resolution..."
if host "$DOMAIN" >/dev/null 2>&1; then
    echo "   ✓ $DOMAIN resolves"
else
    echo "   ✗ $DOMAIN does not resolve"
    exit 1
fi

# 2. Check HTTP -> HTTPS redirect
echo "2. HTTP to HTTPS redirect..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN" --max-time 10 || echo "000")
if [[ "$HTTP_CODE" == "301" ]]; then
    echo "   ✓ HTTP redirects to HTTPS (301)"
else
    echo "   ✗ HTTP redirect failed (code: $HTTP_CODE)"
    exit 1
fi

# 3. Check HTTPS accessibility
echo "3. HTTPS accessibility..."
HTTPS_CODE=$(curl -s -L -o /dev/null -w "%{http_code}" "https://$DOMAIN" --max-time 10 || echo "000")
if [[ "$HTTPS_CODE" == "200" ]]; then
    echo "   ✓ HTTPS returns 200"
else
    echo "   ✗ HTTPS failed (code: $HTTPS_CODE)"
    exit 1
fi

# 4. Check SSL certificate
echo "4. SSL certificate..."
CERT_INFO=$(echo | openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" 2>/dev/null | openssl x509 -noout -dates 2>/dev/null || echo "")
if [[ -n "$CERT_INFO" ]]; then
    echo "   ✓ Valid SSL certificate:"
    echo "$CERT_INFO" | sed 's/^/      /'
else
    echo "   ✗ SSL certificate check failed"
    exit 1
fi

# 5. Check dashboard content (should redirect to Nous login)
echo "5. Dashboard content..."
CONTENT=$(curl -s -L "https://$DOMAIN" --max-time 10 | head -50)
if echo "$CONTENT" | grep -q "Nous Portal\|oauth/authorize\|login"; then
    echo "   ✓ Shows Nous Portal login (OAuth working)"
else
    echo "   ⚠ Unexpected content (may be OK if already authenticated)"
    echo "$CONTENT" | head -5 | sed 's/^/      /'
fi

# 6. Check Hermes dashboard process
echo "6. Hermes dashboard process..."
if pgrep -f "hermes dashboard.*9119" >/dev/null; then
    echo "   ✓ Hermes dashboard process running"
else
    echo "   ⚠ No hermes dashboard process found on port 9119"
fi

# 7. Check Nginx
echo "7. Nginx status..."
if systemctl is-active --quiet nginx; then
    echo "   ✓ Nginx is active"
else
    echo "   ✗ Nginx is not running"
    exit 1
fi

echo
echo "=== All checks passed ==="
echo "Dashboard available at: https://$DOMAIN"