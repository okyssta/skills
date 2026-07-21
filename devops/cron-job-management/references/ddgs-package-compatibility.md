# DDGS Package Compatibility (duckduckgo_search → ddgs)

## Problem
The `duckduckgo_search` package was renamed to `ddgs`. Hermes web_tools.py and the
ddgs plugin both checked only for `import ddgs`, causing `ImportError` when the
legacy package was installed but not detected.

## Symptoms
- web_search_tool returns `"success": false` with firecrawl/429 errors
- `_ddgs_package_importable()` returns False despite duckduckgo_search being importable  
- Agent falls back to paid APIs (firecrawl) or fails entirely

## Fix Locations

### 1. tools/web_tools.py
```python
def _ddgs_package_importable() -> bool:
    try:
        import ddgs
        return True
    except ImportError:
        pass
    try:
        from duckduckgo_search import DDGS  # Also check legacy package
        return True
    except ImportError:
        return False
```

### 2. plugins/web/ddgs/provider.py
The `is_available()` and `search()` methods both need the same fallback:
```python
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS  # Legacy fallback
```

## Resolution Steps
1. Install `ddgs` package: `pip install ddgs` (preferred) OR
2. Patch both files to accept legacy package name
3. Set `hermes config set web.backend ddgs` if firecrawl key exists but is rate-limited

## Session: 2026-07-18
- Firecrawl key `fc-da...` existed with no credits
- DuckDuckGo search worked after installing `ddgs` package
- Root cause: package rename broke autodetect