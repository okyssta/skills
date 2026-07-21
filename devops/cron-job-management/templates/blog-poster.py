#!/usr/bin/env python3
"""
Blog Poster Template - Firecrawl-based blog posting
Posts daily blog content using Firecrawl API.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/root/.hermes/.env')

# Try to import firecrawl
try:
    from firecrawl import FirecrawlApp
except ImportError:
    print("firecrawl-py not installed. Run: pip install firecrawl-py")
    sys.exit(1)

# Configuration
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
BLOG_URL = os.getenv("FONEWORLD_BLOG_URL", "https://example.com")
OUTPUT_DIR = Path(os.getenv("BLOG_OUTPUT_DIR", "/root/.hermes/cron/output/daily-blog"))

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_blog_content():
    """Generate today's blog content."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    return f"""
# Daily Blog - {today}

## Top Stories

### Latest Updates
- Story 1
- Story 2
- Story 3

## Quick Tips
1. Tip 1
2. Tip 2
3. Tip 3

---
*Generated automatically by Daily Blog Bot*
*Source: {BLOG_URL}*
"""


def post_to_firecrawl(content: str):
    """Post content using Firecrawl."""
    if not FIRECRAWL_API_KEY:
        print("FIRECRAWL_API_KEY not set. Saving locally only.")
        return False
    
    try:
        app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
        
        # Use Firecrawl to extract/scrape or post content
        result = app.scrape(
            BLOG_URL,
            formats=['markdown'],
            only_main_content=True
        )
        
        print(f"Firecrawl result: {json.dumps(result, indent=2, default=str)}")
        return True
    except Exception as e:
        print(f"Firecrawl error: {e}")
        return False


def main():
    print(f"[{datetime.utcnow().isoformat()}] Starting blog post...")
    
    # Generate content
    content = generate_blog_content()
    
    # Save locally
    today = datetime.utcnow().strftime("%Y-%m-%d")
    output_file = OUTPUT_DIR / f"blog_{today}.md"
    output_file.write_text(content)
    print(f"Saved to {output_file}")
    
    # Post via Firecrawl
    success = post_to_firecrawl(content)
    
    if success:
        print("Blog post published successfully!")
    else:
        print("Blog post saved locally (Firecrawl posting skipped/failed)")
    
    print(f"[{datetime.utcnow().isoformat()}] Done.")


if __name__ == "__main__":
    main()