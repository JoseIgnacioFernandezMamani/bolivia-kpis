#!/usr/bin/env python3
"""
Script de verificación simple para comprobar que Crawlee está correctamente instalado.
Ejecutar: python test_crawlee.py
"""
import asyncio
import sys
from pathlib import Path

print("════════════════════════════════════════════════════════════════")
print("  Crawlee Installation Test")
print("════════════════════════════════════════════════════════════════\n")

# Test 1: Import Crawlee
print("[1/5] Testing Crawlee import...", end=" ")
try:
    import crawlee
    print(f"✓ (version {crawlee.__version__})")
except ImportError as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# Test 2: Import Playwright
print("[2/5] Testing Playwright import...", end=" ")
try:
    from crawlee.playwright_crawler import PlaywrightCrawler
    print("✓")
except ImportError as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# Test 3: Import BeautifulSoup
print("[3/5] Testing BeautifulSoup import...", end=" ")
try:
    from bs4 import BeautifulSoup
    print("✓")
except ImportError as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# Test 4: Test basic Crawler creation
print("[4/5] Testing Crawler instantiation...", end=" ")
try:
    crawler = PlaywrightCrawler(
        max_requests_per_crawl=1,
        headless=True,
    )
    print("✓")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# Test 5: Test a simple crawl
print("[5/5] Testing simple crawl (example.com)...", end=" ")

async def test_crawl():
    """Test a simple crawl to verify everything works."""
    results = []
    
    crawler = PlaywrightCrawler(
        max_requests_per_crawl=1,
        headless=True,
        request_handler_timeout_secs=30,
    )
    
    @crawler.router.default_handler
    async def handler(context):
        title = await context.page.title()
        results.append({"url": context.request.url, "title": title})
    
    try:
        await crawler.run(["https://example.com"])
        return len(results) > 0
    except Exception as e:
        print(f"\n    Error during crawl: {e}")
        return False

try:
    success = asyncio.run(test_crawl())
    if success:
        print("✓")
    else:
        print("✗ No results captured")
        sys.exit(1)
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# All tests passed
print("\n════════════════════════════════════════════════════════════════")
print("  ✓ All tests passed!")
print("════════════════════════════════════════════════════════════════\n")
print("Crawlee is correctly installed and ready to use.")
print("\nNext steps:")
print("  1. Run the OEP spider: python -m bolivia_scraper oep_elections")
print("  2. Check the output: data/raw/oep_elections.jsonl")
print("  3. Read the docs: cat README.md\n")
