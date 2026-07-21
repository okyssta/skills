#!/usr/bin/env python3
"""
WordPress Blog Poster with GPT Image Mini
Posts daily repair guide blogs to a WordPress site via REST API
with AI-generated images using OpenAI's gpt-image-1 model.
"""

import os
import sys
import json
import base64
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/root/.hermes/.env')

# ============================================================
# CONFIGURATION - UPDATE THESE FOR YOUR SITE
# ============================================================
WP_URL = os.getenv("WP_URL", "https://your-site.com")
WP_USER = os.getenv("WP_USER", "your-username")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "your-app-password")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Derived
WP_API = f"{WP_URL}/wp-json/wp/v2"
AUTH_HEADER = base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()

# Output directory for state and logs
OUTPUT_DIR = Path(os.getenv("BLOG_OUTPUT_DIR", "/root/.hermes/cron/output/daily-blog"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = OUTPUT_DIR / "posted_state.json"

# ============================================================
# TOPIC DEFINITIONS - CUSTOMIZE FOR YOUR NICHE
# ============================================================
BLOG_TOPICS = [
    {
        "issue": "Issue One",
        "device": "Device",
        "focus": "focus-keyword",
        "tags": [1, 2, 3],  # WordPress tag IDs
        "categories": [10, 20],  # WordPress category IDs
    },
    # Add more topics...
]

# ============================================================
# IMAGE PROMPT TEMPLATE - CUSTOMIZE FOR YOUR STYLE
# ============================================================
def generate_image_prompt(topic):
    """Generate prompt for GPT Image mini model."""
    issue = topic["issue"]
    device = topic["device"]
    focus = topic.get("focus", "repair")
    
    prompts = {
        "focus-keyword": f"Close-up cinematic shot of {issue.lower()} on {device.lower()} "
                          f"on a dark industrial repair bench, "
                          f"dramatic black and red lighting, deep shadows, "
                          f"premium tech repair aesthetic, "
                          f"visible macro detail of component, "
                          f"no text, no watermark, 1536x1024",
    }
    
    return prompts.get(focus, f"Close-up cinematic shot of {issue} repair on {device.lower()} "
                                f"on a dark industrial repair bench, "
                                f"professional tools, dramatic lighting, "
                                f"no text, no watermark, 1536x1024")

# ============================================================
# CONTENT GENERATION - CUSTOMIZE YOUR POST FORMAT
# ============================================================
def generate_blog_content(topic):
    """Generate blog content matching your site's format."""
    issue = topic["issue"]
    device = topic["device"]
    
    title = f"How to Fix {issue} at Home – When to Book Professional Repair"
    slug = f"{issue.lower().replace(' ', '-')}-2"
    hero_text = f"Fix {issue} at Home – Safe First Steps"
    
    intro = f"Experiencing {issue.lower()} can be frustrating..."
    
    # YOUR EXACT HTML STRUCTURE HERE
    content = f'''<div class="your-hero-class">
    <p class="your-title-class">{hero_text}</p>
</div>

<p class="mb-6">{intro}</p>

<h2 class="your-h2-class">01. Why the {issue} Happens</h2>
<p class="mb-6">Understanding the root cause...</p>

<h2 class="your-h2-class">02. Safe First Steps to Try at Home</h2>
<ul class="your-list-class">
    <li>Power off the device completely and wait 30 seconds.</li>
    <li>Inspect for visible damage, debris, or liquid indicators.</li>
    <li>If applicable, try a different charger, cable, or power outlet.</li>
    <li>For touch/display issues, gently clean the screen with a microfiber cloth.</li>
</ul>

... YOUR REMAINING SECTIONS ...

<div class="your-cta-class">
    <p class="mb-4">Ready to get your device fixed?</p>
    <a href="https://your-site.com/start-repair/" class="your-btn-class">START REPAIR</a>
</div>

<div class="your-discount-class">
    <p class="mb-4">ISSUE STILL PERSISTS? GET 10% DISCOUNT! 😉</p>
    <a href="https://your-site.com/locations/" class="your-btn-class">FIND NEAREST STORE</a>
</div>'''
    
    excerpt = f"Fix {issue.lower()} at Home – Safe First Steps Experiencing {issue.lower()} can be frustrating..."
    
    return {
        "title": title,
        "slug": slug,
        "content": content,
        "excerpt": excerpt,
        "tags": topic["tags"],
        "categories": topic["categories"],
        "date": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    }

# ============================================================
# STATE MANAGEMENT - ANTI-REPEAT LOGIC
# ============================================================
def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"posted_topics": [], "last_post_date": None}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_today_topic():
    """Select topic avoiding repeats."""
    state = load_state()
    posted = set(state.get("posted_topics", []))
    
    for topic in BLOG_TOPICS:
        topic_key = f"{topic['issue']}|{topic['device']}"
        posted.add(topic_key)
            state["posted_topics"] = list(posted)
            state["last_post_date"] = datetime.utcnow().strftime("%Y-%m-%d")
            save_state(state)
            return topic
    
    # All used - reset
    state["posted_topics"] = []
    state["last_post_date"] = datetime.utcnow().strftime("%Y-%m-%d")
    save_state(state)
    return BLOG_TOPICS[0]

# ============================================================
# IMAGE GENERATION - GPT IMAGE MINI
# ============================================================
def generate_image(prompt):
    """Generate image using GPT Image mini (gpt-image-1)."""
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-image-1",
        "prompt": prompt,
        "size": "1536x1024",
        "quality": "low",
        "n": 1
    }
    response = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers=headers, json=payload, timeout=60
    )
    if response.status_code == 200:
        b64_data = response.json()["data"][0]["b64_json"]
        return base64.b64decode(b64_data)
    return None

def upload_media(image_data, filename):
    """Upload image to WordPress media library."""
    headers = {
        "Authorization": f"Basic {AUTH_HEADER}",
        "Content-Type": "image/png",
        "Content-Disposition": f'attachment; filename="{filename}"'
    }
    response = requests.post(f"{WP_API}/media", headers=headers, data=image_data, timeout=30)
    if response.status_code in (200, 201):
        return response.json()["id"]
    return None

# ============================================================
# POST CREATION
# ============================================================
def create_post(post_data, featured_media_id):
    """Create WordPress post."""
    headers = {
        "Authorization": f"Basic {AUTH_HEADER}",
        "Content-Type": "application/json"
    }
    payload = {
        "title": post_data["title"],
        "slug": post_data["slug"],
        "content": post_data["content"],
        "excerpt": post_data["excerpt"],
        "status": "publish",
        "categories": post_data["categories"],
        "tags": post_data["tags"],
        "featured_media": featured_media_id,
        "date": post_data["date"],
        "format": "standard"
    }
    response = requests.post(f"{WP_API}/posts", headers=headers, json=payload, timeout=30)
    if response.status_code in (200, 201):
        return response.json()
    return None

# ============================================================
# MAIN
# ============================================================
def main():
    print(f"[{datetime.utcnow().isoformat()}] Starting blog post...")
    
    topic = get_today_topic()
    post_data = generate_blog_content(topic)
    
    print("Generating image...")
    image_prompt = generate_image_prompt(topic)
    image_data = generate_image(image_prompt)
    if not image_data:
        return 1
    
    filename = f"{post_data['slug']}-{datetime.utcnow().strftime('%Y%m%d')}.png"
    media_id = upload_media(image_data, filename)
    if not media_id:
        return 1
    
    result = create_post(post_data, media_id)
    if result:
        print(f"✅ Published: {result['link']}")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())