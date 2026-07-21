#!/usr/bin/env python3
"""
WordPress Blog Auto-Poster Template
Posts blogs via WordPress REST API with SEO keyword injection.
Customize the TOPICS, KEYWORDS, and LOCATIONS for your site.
"""
import os
import sys
import json
import base64
import random
import requests
from datetime import datetime
from pathlib import Path

# ── CONFIGURE THESE ────────────────────────────────────────────────────────
WP_URL = "https://yoursite.co.uk"
WP_USER = "your-username"
WP_APP_PASSWORD = "xxxx xxxx xxxx xxxx xxxx xxxx"

CATEGORIES = [1]  # WordPress category IDs
COMMON_TAGS = [1, 2, 3]  # WordPress tag IDs

# Google Ads / target keywords (injected with 80% probability per keyword)
TARGET_KEYWORDS = [
    "example keyword 1",
    "example keyword 2",
    # add all your keywords here
]

# ── DO NOT EDIT BELOW (unless needed) ─────────────────────────────────────
WP_API = f"{WP_URL}/wp-json/wp/v2"
AUTH = base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()

# Blog topics rotation (edit these for your content)
TOPICS = [
    {"issue": "Example Issue", "device": "Phone", "focus": "screen"},
]

OUTPUT_DIR = Path("/tmp/blog-posts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = OUTPUT_DIR / "state.json"

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"posted_topics": [], "used_keywords": []}

def save_state(s):
    STATE_FILE.write_text(json.dumps(s, indent=2))

def get_unique_slug(base_slug):
    resp = requests.get(f"{WP_API}/posts", params={"slug": base_slug, "per_page": 1},
                        headers={"Authorization": f"Basic {AUTH}"}, timeout=10)
    if resp.status_code == 200 and not resp.json():
        return base_slug
    for i in range(2, 50):
        c = f"{base_slug}-{i}"
        r = requests.get(f"{WP_API}/posts", params={"slug": c, "per_page": 1},
                         headers={"Authorization": f"Basic {AUTH}"}, timeout=10)
        if r.status_code == 200 and not r.json():
            return c
    return f"{base_slug}-50"

def pick_keywords():
    return [kw for kw in TARGET_KEYWORDS if random.random() < 0.80]

def publish_post(title, content_html, excerpt, tag_ids, media_id=None):
    headers = {"Authorization": f"Basic {AUTH}", "Content-Type": "application/json"}
    payload = {
        "title": title, "content": content_html, "excerpt": excerpt,
        "status": "publish", "categories": CATEGORIES, "tags": tag_ids,
        "date": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    }
    if media_id:
        payload["featured_media"] = media_id
    r = requests.post(f"{WP_API}/posts", json=payload, headers=headers, timeout=30)
    return r.json() if r.status_code in (200, 201) else None

def main():
    keywords = pick_keywords()
    print(f"Keywords selected: {len(keywords)}")

    # === YOUR GENERATION LOGIC HERE ===
    # 1. Choose topic (avoid repeats using state)
    # 2. Generate HTML content
    # 3. Upload image (optional)
    # 4. Publish post

    result = publish_post(
        title="Your Post Title",
        content_html="<p>Your HTML content here</p>",
        excerpt="Your excerpt",
        tag_ids=COMMON_TAGS,
        media_id=None
    )

    if result:
        print(f"✅ Published: {result['link']}")
        return 0
    else:
        print("❌ Failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
