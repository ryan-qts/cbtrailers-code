"""
diagnose.py — Run this FIRST to see what HTML VisionLED actually returns.
It prints all <a> tags that look like product links, and saves the raw HTML
to diagnose_products.html so you can inspect it in a browser.

Usage:
    python diagnose.py
"""

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

URL = "https://visionled-lights.com/products/"

print(f"Fetching {URL} ...\n")
r = requests.get(URL, headers=HEADERS, timeout=30)
print(f"Status: {r.status_code}")
print(f"Content-Type: {r.headers.get('Content-Type')}")
print(f"Response length: {len(r.text)} chars\n")

# Save raw HTML
with open("diagnose_products.html", "w", encoding="utf-8") as f:
    f.write(r.text)
print("Saved raw HTML → diagnose_products.html\n")

soup = BeautifulSoup(r.text, "lxml")

# ── Print ALL <a> tags containing "/products/" ──
print("=" * 60)
print("ALL <a href> containing '/products/':")
print("=" * 60)
found = 0
for a in soup.find_all("a", href=True):
    href = a["href"]
    if "/products/" in href and href.rstrip("/") != URL.rstrip("/"):
        print(f"  TEXT: {a.get_text(strip=True)[:60]!r}")
        print(f"  HREF: {href}")
        print(f"  CLASSES: {a.get('class')}")
        print()
        found += 1

print(f"Total product-like links found: {found}\n")

# ── Print the first <li class*='product'> block ──
print("=" * 60)
print("First <li> with 'product' in class:")
print("=" * 60)
li = soup.select_one("li[class*='product']")
if li:
    print(li.prettify()[:2000])
else:
    print("  None found — trying <article> ...")
    article = soup.select_one("article")
    if article:
        print(article.prettify()[:2000])
    else:
        print("  No <article> either.")

# ── Print pagination info ──
print("\n" + "=" * 60)
print("Pagination links:")
print("=" * 60)
for a in soup.select("a.page-numbers, a[href*='page']"):
    print(f"  {a.get_text(strip=True)!r} → {a['href']}")

# ── Check if page might be JS-rendered (very short body) ──
body_text = soup.get_text(strip=True)
print(f"\nBody text length: {len(body_text)}")
if len(body_text) < 500:
    print("WARNING: Page body is very short — site may require JavaScript to render products.")
    print("You may need Selenium or Playwright instead of requests.")
