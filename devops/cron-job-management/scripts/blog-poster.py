#!/usr/bin/env python3
"""
Blog Poster Template - Firecrawl-based daily blog posting
Agent-based or script-based cron job for FoneWorld or similar.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Try to import firecrawl
try:
    from firecrawl import FirecrawlApp
    HAS_FIRECRAWL = True
except ImportError:
    HAS_FIRECRAWL = False
    FirecrawlApp = None


# ============ CONFIGURATION ============
FIRECRAWL_API_URL = os.getenv("FIRECRAWL_API_URL", "http://localhost:3002")
SOURCE_URL = os.getenv("BLOG_SOURCE_URL", "https://foneworld.example.com")
OUTPUT_DIR = Path(os.getenv("BLOG_OUTPUT_DIR", "/root/.hermes/cron/output/daily-blog"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
# ========================================


def generate_blog_content(date: datetime = None) -> str:
    """Generate blog content for the given date."""
    if date is None:
        date = datetime.utcnow()
    
    date_str = date.strftime("%B %d, %Y")
    date_file = date.strftime("%Y-%m-%d")
    
    return f"""# FoneWorld Daily Brief - {date_str}

## Top Stories

### 📱 Latest Phone Releases
- **iPhone 16 Pro Max** - New titanium design, A18 Pro chip
- **Samsung Galaxy S25 Ultra** - 200MP camera, S Pen integration
- **Google Pixel 9 Pro** - Tensor G4, AI-first features

### 🔧 Tech Updates
- **iOS 18.1** - Apple Intelligence rollout continues
- **Android 15** - Material You 3.0, satellite connectivity
- **OneUI 7** - Samsung's latest skin with AI features

### 💰 Deals & Drops
- Carrier trade-in offers up to $1000 off
- Refurbished flagship deals under $500
- Budget 5G phones under $300

## Quick Tips
1. **Battery Life**: Enable 80% charge limit for longevity
2. **Storage**: Offload photos to cloud, clear cache monthly
3. **Security**: Update immediately, use passkeys where available

---
*Generated automatically by FoneWorld Daily Bot*
*Source: {SOURCE_URL}*
*Date: {date.isoformat()}Z*
"""


def scrape_with_firecrawl(url: str) -> dict:
    """Scrape content using local Firecrawl instance."""
    if not HAS_FIRECRAWL:
        return {"error": "firecrawl-py not installed"}
    
    try:
        app = FirecrawlApp(api_url=FIRECRAWL_API_URL)
        result = app.scrape(url, params={
            'formats': ['markdown', 'html'],
            'onlyMainContent': True
        })
        return {"markdown": result.markdown, "html": result.html if hasattr(result, 'html') else ""}
    except Exception as e:
        return {"error": str(e)}


def save_blog_post(content: str, date: datetime = None) -> Path:
    """Save blog post to output directory."""
    if date is None:
        date = datetime.utcnow()
    
    filename = OUTPUT_DIR / f"blog_{date.strftime('%Y-%m-%d')}.md"
    filename.write_text(content)
    return filename


def main():
    print(f"[{datetime.utcnow().isoformat()}] Starting blog post generation...")
    
    # Generate content
    content = generate_blog_content()
    
    # Optionally scrape source for additional content
    if HAS_FIRECRAWL:
        print("Scraping source URL with Firecrawl...")
        scraped = scrape_with_firecrawl(SOURCE_URL)
        if "error" not in scraped:
            print("Adding scraped content...")
            content += f"\n## Scraped Content\n\n{scraped.get('markdown', '')[:2000]}..."
        else:
            print(f"Firecrawl error: {scraped.get('error')}")
    else:
        print("Firecrawl not configured - using generated content only")
    
    # Save locally
    output_file = save_blog_post(content)
    print(f"Blog post saved to {output_file}")
    
    # Print content (for cron delivery)
    print(content)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())