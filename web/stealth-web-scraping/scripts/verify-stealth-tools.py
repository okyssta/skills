#!/usr/bin/env python3
"""
Verify stealth browser tools are installed and working.
Run: python3 scripts/verify-stealth-tools.py
"""
import sys
import subprocess
import importlib


def check_import(name, package=None):
    """Check if a Python package can be imported."""
    try:
        importlib.import_module(package or name)
        print(f"  ✓ {name} — importable")
        return True
    except ImportError as e:
        print(f"  ✗ {name} — NOT installed: {e}")
        return False


def check_binary(name, path):
    """Check if a binary exists and is executable."""
    import os
    if os.path.isfile(path) and os.access(path, os.X_OK):
        print(f"  ✓ {name} — found at {path}")
        return True
    else:
        print(f"  ✗ {name} — not found at {path}")
        return False


def test_cloakbrowser():
    """Quick functional test of CloakBrowser."""
    try:
        from cloakbrowser import launch
        browser = launch(headless=True)
        page = browser.new_page()
        page.goto("https://example.com")
        title = page.title()
        browser.close()
        assert "Example" in title, f"Unexpected title: {title}"
        print(f"  ✓ CloakBrowser functional test passed (title: {title})")
        return True
    except Exception as e:
        print(f"  ✗ CloakBrowser functional test FAILED: {e}")
        return False


def test_undetected():
    """Quick functional test of undetected-chromedriver."""
    try:
        import undetected_chromedriver as uc
        import os

        chromedriver_path = "/root/.local/share/uc-chromedriver/chromedriver"
        if not os.path.exists(chromedriver_path):
            print("  ⚠ undetected-chromedriver: chromedriver not at expected path")
            print("    Run the ARM64 fix from references/arm64-chromedriver-fix.md")
            return False

        options = uc.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = uc.Chrome(
            options=options,
            use_subprocess=True,
            browser_executable_path="/snap/bin/chromium",
            driver_executable_path=chromedriver_path,
        )
        driver.get("https://example.com")
        title = driver.title
        driver.quit()
        assert "Example" in title, f"Unexpected title: {title}"
        print(f"  ✓ undetected-chromedriver functional test passed (title: {title})")
        return True
    except Exception as e:
        print(f"  ✗ undetected-chromedriver functional test FAILED: {e}")
        return False


def test_firecrawl():
    """Quick functional test of Firecrawl self-hosted."""
    try:
        from firecrawl import FirecrawlApp
        app = FirecrawlApp(api_url="http://localhost:3002")
        result = app.scrape("https://example.com")
        title = result.metadata.title
        assert "Example" in title, f"Unexpected title: {title}"
        print(f"  ✓ Firecrawl functional test passed (title: {title})")
        return True
    except Exception as e:
        print(f"  ✗ Firecrawl functional test FAILED: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Stealth Web Scraping — Verification")
    print("=" * 60)

    results = []

    print("\n📦 Package imports:")
    results.append(check_import("cloakbrowser"))
    results.append(check_import("undetected_chromedriver"))
    results.append(check_import("firecrawl"))

    print("\n🔧 Binaries:")
    results.append(check_binary("chromium-browser", "/usr/bin/chromium-browser"))
    results.append(check_binary("chromium (snap)", "/snap/bin/chromium"))
    results.append(check_binary("ARM64 chromedriver", "/root/.local/share/uc-chromedriver/chromedriver"))

    print("\n🧪 Functional tests:")
    results.append(test_cloakbrowser())
    results.append(test_undetected())
    results.append(test_firecrawl())

    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    if all(results):
        print(f"ALL {total} CHECKS PASSED ✓")
    else:
        print(f"{passed}/{total} checks passed, {total - passed} FAILED")
        sys.exit(1)
