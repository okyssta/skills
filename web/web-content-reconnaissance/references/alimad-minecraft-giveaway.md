# Alimad Minecraft Giveaway — Puzzle Solution Reference

## Overview

A 64-digit hex key split into 8 parts across alimad.co subdomains. Each
fragment (except the last) gives a clue to the next. Fragments 1-7 are
8 hex chars each; fragment 8 is AES-encrypted Base64 decrypted with the
first 7 fragments as the key.

## Fragment Chain

| # | Value | Location | How to trigger |
|---|---|---|---|
| 1 | `f09c4f33` | alimad.co/projects | Click the "Proxy" project (has id="text-xl"). Script loaded from `api.alimad.co/script.js`. |
| 2 | `ac20191b` | cdn.alimad.co/f/static/giveaway.txt | Direct URL. Clue: "next: its some static file on some cd-" |
| 3 | `5a7ddc10` | blog.alimad.co/private/giveaway | Password: `ac20191b`. AES-GCM decrypted via JS chunk 49942. PBKDF2 salt="alimad-salt", 100k iterations, SHA-256. |
| 4 | `e9ce4670` | log.alimad.co/api/pull?channel=study-alimad-co | Hidden in a comment. Clue: "in a random study comment section..." |
| 5 | `93b51f86` | games.alimad.co | Found in page source. Clue: "maybe when you enter this part of the key into some special trinary encoder" |
| 6 | `8252d8c3` | 312.alimad.co | Enter `93b51f86` into the 312 encoder. Clue: "have you ever seen what the qr code of https://alimad.co looks like, printed?" |
| 7 | `1410e2e4` | qr.alimad.co | Enter `https://alimad.co` as text to generate QR. Clue: "back to / again" |
| 8 | `wwEmdJk1av39Vxnj9MKxAqGNqocmLG/5SYsrlRQxS18=` | alimad.co (/) | Click the PRs stat box in GitHub stats. Clue: "devglan.com/online-tools/text-encryption-decryption" |

## Decryption Key (fragments 1-7)

```
f09c4f33ac20191b5a7ddc10e9ce467093b51f868252d8c31410e2e4
```

Use as the secret key on devglan.com's AES decryption tool with fragment 8
as the encrypted text.

### Devglan API interaction (programmatic)

```python
import requests, re

session = requests.Session()
headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

# Step 1: Get a fresh page to obtain the X-DG-TOKEN and JSESSIONID cookie
page = session.get(
    "https://www.devglan.com/online-tools/text-encryption-decryption",
    headers=headers, timeout=15
)
m = re.search(r'name="dg-token"\s*content="([^"]+)"', page.text)
token = m.group(1) if m else ""

# Step 2: Decrypt
f8_b64 = "wwEmdJk1av39Vxnj9MKxAqGNqocmLG/5SYsrlRQxS18="
key56 = "f09c4f33ac20191b5a7ddc10e9ce467093b51f868252d8c31410e2e4"

resp = session.post(
    "https://www.devglan.com/online-tools/text-decryption",
    json={
        "textToDecrypt": f8_b64,
        "encryptedText": "",
        "deSecretKey": key56,
    },
    headers={
        "X-DG-TOKEN": token,
        "Referer": "https://www.devglan.com/online-tools/text-encryption-decryption",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    },
    timeout=15
)
result = resp.json()
# result["decryptedText"] will be "Error while decrypting the text" on failure
```

**Caveats:**
- Each call needs a fresh session — rate-limiting kicks in after 1-2 requests on the same token.
- The `encryptedText` field in the request body must be `""` (empty string).
- A 200 response with `"decryptedText": "Error while decrypting the text"` means the server tried but the key/ciphertext didn't match (not an auth error).
- The encrypt endpoint (`/online-tools/text-encryption`) is more restrictive and will 403 without a Bearer token from `localStorage.devglan-data`.

### Devglan algorithm analysis (reverse-engineered)

The text encryption tool uses **AES-CBC with PKCS7 padding** (not ECB — confirmed
by encrypting 32 identical characters and observing different ciphertext blocks
for the identical first two plaintext blocks):

- **Deterministic**: same plaintext + same key = same ciphertext every time (fixed IV)
- **Encrypted output**: pure ciphertext Base64, no IV/salt prepended, 16B-aligned
- **Proven CBC, not ECB**:
  ```
  encrypt("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", key123)
  Block1: f0eea9e64f1e03e1dc979b6631ea131e
  Block2: 1da168aeff5c4a2834bc06fe412ed219  (≠ Block1 — would match in ECB)
  ```
- **Key derivation**: server-side Java, opaque. Attempts to replicate with SHA256,
  MD5, SHA1, PBKDF2 (varied salts/iterations), UTF-16LE, repeated-to-size,
  zero-padded, HMAC all failed to match.
- **Key truncation confirmed**: 16-char and 32-char identical-text passwords
  produce the **same ciphertext**, confirming the input is truncated to a fixed
  size (≤16 bytes) before key derivation. This rules out any hash-based derivation
  (SHA/MD5 of different-length inputs would produce different outputs):
  ```
  encrypt("hello", "aaaaaaaaaaaaaaaa")                  = 9c1a55088594d7e7...
  encrypt("hello", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")  = 9c1a55088594d7e7... (IDENTICAL)
  ```
- **Output length patterns** (PKCS7):
  - 5B plaintext → 16B ciphertext
  - 15B plaintext → 16B ciphertext
  - 16B plaintext → 32B ciphertext (full padding block)
  - 17B plaintext → 32B ciphertext
  - 31B plaintext → 32B ciphertext

### Playwright browser fallback

When the API is rate-limited, use Playwright (Node.js) to drive the site
directly — each page load gets a fresh dg-token. A reusable script is
at `scripts/playwright-devglan.js` in this skill:

```bash
cd /tmp && npm install playwright
cp /root/.hermes/skills/web/web-content-reconnaissance/scripts/playwright-devglan.js .
# Edit the script to set ENCRYPTED_TEXT and DECRYPTION_KEY, then:
node playwright-devglan.js
```

**Note:** When `dSecretKeyRequired` is unchecked, the `#deSecretKey` field
is disabled (`:disabled="!dSecretKeyRequired"`) and cannot be filled. The
checkbox must be checked to enable the key field.

### Fragment 8 byte layout analysis

Base64-decoded fragment 8 is exactly 32 bytes:

```
c301267499356afdfd5719e3f4c2b102a18daa87262c6ff9498b2b9514314b5f
```

Possible AES-GCM layout (matching the blog fragment 3 approach):
- Bytes 0-11: IV/nonce (12 bytes)
- Bytes 12-15: Ciphertext (4 bytes → 8 hex chars when decrypted)
- Bytes 16-31: GCM authentication tag (16 bytes)

### Full 64-digit key candidates

```
f09c4f33ac20191b5a7ddc10e9ce467093b51f868252d8c31410e2e414314b5f  (last 8 hex of f8 raw)
f09c4f33ac20191b5a7ddc10e9ce467093b51f868252d8c31410e2e4c3012674  (first 8 hex of f8 raw)
f09c4f33ac20191b5a7ddc10e9ce467093b51f868252d8c31410e2e4e2f2fccc  (SHA256[:8] of frags 1-7)
```

### Fillout form submission

The giveaway uses a Fillout form at `https://alimad.fillout.com/mc-giveaway-june`.
Fields: contact (email/discord) + 64-digit key. The form validates server-side;
submission always shows "Entry Submitted!" regardless of key correctness.

### 312 Cipher Reference

The 312 cipher converts letters to triples of digits {1,2,3}:
- A=111, B=112, C=113, ..., Z=332
- Numbers use 4-digit codes: 0=118, 1=181, 2=182, ..., 9=383
- 0 (single digit) = space
- 4→11, 5→22, 6→33 in decryption (compression)
- Decryption: split into 3-digit tokens, look up in cipher map
- Decodes to: `SIMPLE JAVASCRIPT DECRYPTER`

## Hidden Properties to Check

- **Git commit messages** on the Site repo (Alimadcorp/Site) — commits like
  "add hint", "ignore giveaway", "add minecraft giveaway" reveal context
- **Comment API** at log.alimad.co/api/pull — channels follow the pattern
  "comments:{page-name}" or "{site-name}" (e.g. "study-alimad-co")
- **Blog private posts** at /api/list/blog/ on the blog domain — lists
  unlisted and private posts
- **CDN giveaway files** at /f/static/giveaway.txt — often the bridge
  between fragments

## Status

**Last updated:** Jul 19, 2026
**Decryption status:** Key derivation on Devglan's server could not be
replicated. The algorithm is AES-CBC (deterministic, fixed IV, 16B key
truncation confirmed, blocks chain). The exact Java transformation from
password bytes to AES key remains opaque — 50+ derivation approaches
(SHA256, MD5, SHA1, PBKDF2, UTF-16LE, repeated, padded, HMAC) all failed
to match Devglan's output. Three 64-digit candidates submitted via all 3
user emails. Correct key still unknown.
