#!/usr/bin/env python3
"""
eBay OAuth Token Generator

Run this once to obtain a user access token for the Trading API.
Saves token to .env file.

Prerequisites:
- eBay Developer Account
- App ID (Client ID), Cert ID (Client Secret), RuName (Redirect URI)
- Set these as environment variables or edit the CONFIG section below
"""

import os
import sys
import urllib.parse
import webbrowser
import http.server
import socketserver
import requests
from pathlib import Path
from dotenv import load_dotenv, set_key

# ==================== CONFIGURATION ====================
# Option 1: Set as environment variables (recommended)
# Option 2: Edit these values directly
APP_ID = os.getenv("EBAY_APP_ID", "YOUR_APP_ID_HERE")
CERT_ID = os.getenv("EBAY_CERT_ID", "YOUR_CERT_ID_HERE")
RU_NAME = os.getenv("EBAY_RU_NAME", "YOUR_RUNAME_HERE")  # e.g., "YourApp-YourName"

# Scopes needed for Trading API
SCOPES = [
    "https://api.ebay.com/oauth/api_scope/sell.inventory",
    "https://api.ebay.com/oauth/api_scope/sell.fulfillment",
    "https://api.ebay.com/oauth/api_scope/commerce.identity.readonly",
    "https://api.ebay.com/oauth/api_scope/sell.analytics.readonly",
    "https://api.ebay.com/oauth/api_scope/sell.marketing.readonly",
    "https://api.ebay.com/oauth/api_scope/sell.account.readonly",
]

ENV_FILE = Path(__file__).resolve().parent / ".env"
TOKENS_FILE = Path(__file__).resolve().parent / "ebay_tokens.txt"

# ==================== OAUTH FLOW ====================
class OAuthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        self.server.auth_code = params.get("code", [None])[0]
        self.server.auth_error = params.get("error", [None])[0]
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        if self.server.auth_code:
            self.wfile.write(b"<h1>Authorization successful!</h1><p>You can close this window.</p>")
        else:
            self.wfile.write(f"<h1>Authorization failed</h1><p>Error: {self.server.auth_error}</p>".encode())
        # Shutdown after handling
        threading.Thread(target=self.server.shutdown).start()
    
    def log_message(self, format, *args):
        pass  # Suppress log output

def get_authorization_code():
    """Open browser and capture authorization code from redirect."""
    auth_url = (
        "https://auth.ebay.com/oauth2/authorize"
        f"?client_id={APP_ID}"
        f"&redirect_uri={urllib.parse.quote(RU_NAME)}"
        f"&response_type=code"
        f"&scope={urllib.parse.quote(' '.join(SCOPES))}"
    )
    
    print(f"Opening browser for eBay authorization...")
    print(f"If browser doesn't open, visit:\n{auth_url}\n")
    webbrowser.open(auth_url)
    
    # Start local server to catch redirect
    with socketserver.TCPServer(("", 8080), OAuthHandler) as httpd:
        print("Waiting for authorization callback on http://localhost:8080...")
        httpd.auth_code = None
        httpd.auth_error = None
        httpd.serve_forever()
        
        if httpd.auth_error:
            raise Exception(f"Authorization failed: {httpd.auth_error}")
        if not httpd.auth_code:
            raise Exception("No authorization code received")
        
        return httpd.auth_code

def exchange_code_for_token(auth_code):
    """Exchange authorization code for access + refresh tokens."""
    token_url = "https://api.ebay.com/identity/v1/oauth2/token"
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": RU_NAME,
    }
    auth = (APP_ID, CERT_ID)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    resp = requests.post(token_url, data=data, auth=auth, headers=headers)
    resp.raise_for_status()
    return resp.json()

def refresh_access_token(refresh_token):
    """Refresh an expired access token."""
    token_url = "https://api.ebay.com/identity/v1/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "scope": " ".join(SCOPES),
    }
    auth = (APP_ID, CERT_ID)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    resp = requests.post(token_url, data=data, auth=auth, headers=headers)
    resp.raise_for_status()
    return resp.json()

def main():
    # Check config
    if "YOUR_" in APP_ID or "YOUR_" in CERT_ID or "YOUR_" in RU_NAME:
        print("ERROR: Please set EBAY_APP_ID, EBAY_CERT_ID, EBAY_RU_NAME environment variables")
        print("or edit the CONFIG section in this script.")
        sys.exit(1)
    
    # Load existing tokens if any
    load_dotenv(ENV_FILE)
    refresh_token = os.getenv("EBAY_REFRESH_TOKEN")
    
    if refresh_token:
        print("Found existing refresh token. Attempting to refresh...")
        try:
            tokens = refresh_access_token(refresh_token)
            print("Token refreshed successfully!")
        except Exception as e:
            print(f"Refresh failed: {e}")
            print("Falling back to full OAuth flow...")
            refresh_token = None
    
    if not refresh_token:
        # Full OAuth flow
        auth_code = get_authorization_code()
        tokens = exchange_code_for_token(auth_code)
        print("Tokens obtained successfully!")
    
    # Save tokens
    access_token = tokens["access_token"]
    refresh_token = tokens.get("refresh_token", refresh_token)
    expires_in = tokens.get("expires_in", 7200)
    
    # Save to .env
    set_key(ENV_FILE, "EBAY_ACCESS_TOKEN", access_token)
    if refresh_token:
        set_key(ENV_FILE, "EBAY_REFRESH_TOKEN", refresh_token)
    set_key(ENV_FILE, "EBAY_TOKEN_EXPIRES_IN", str(expires_in))
    
    # Save to ebay_tokens.txt (format used by analysis scripts)
    with open(TOKENS_FILE, "w") as f:
        f.write(f"{access_token}\n")
    if refresh_token:
        with open(TOKENS_FILE, "a") as f:
            f.write(f"# Refresh token: {refresh_token}\n")
    
    print(f"\nAccess token saved to: {ENV_FILE}")
    print(f"Access token also saved to: {TOKENS_FILE}")
    print(f"Token expires in: {expires_in} seconds ({expires_in/3600:.1f} hours)")
    print("\nUse this token in ebay_tokens.txt for the analysis scripts.")
    print("When token expires, run this script again to refresh.")

if __name__ == "__main__":
    import threading
    main()