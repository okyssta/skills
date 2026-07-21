#!/usr/bin/env python3
"""
WordPress Schema Validator
Extracts and validates all JSON-LD schema blocks from a WordPress site.
Usage: python3 validate-schema.py https://example.com
"""
import sys
import json
import re
import requests

def validate_schema(url):
    resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    html = resp.text
    
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
    print(f"Found {len(blocks)} JSON-LD blocks on {url}\n")
    
    errors = 0
    for i, block in enumerate(blocks):
        try:
            data = json.loads(block)
            at_type = data.get('@type', 'MISSING')
            at_context = data.get('@context', 'MISSING')
            name = data.get('name', data.get('title', ''))
            if isinstance(name, str) and len(name) > 60:
                name = name[:57] + '...'
            
            if at_context not in ('https://schema.org', 'https://schema.org/'):
                print(f"  [{i}] ❌ @context={at_context} | @type={at_type} | {name}")
                errors += 1
            else:
                print(f"  [{i}] ✅ @context=✓ | @type={at_type} | {name}")
        except json.JSONDecodeError as e:
            print(f"  [{i}] ❌ JSON PARSE ERROR: {e}")
            errors += 1
    
    print(f"\n{'='*50}")
    print(f"Total: {len(blocks)} blocks, {errors} errors")
    if errors == 0:
        print("✅ ALL SCHEMAS VALID")
    else:
        print(f"❌ {errors} schema(s) need fixing")
    
    return errors == 0

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    sys.exit(0 if validate_schema(url) else 1)
