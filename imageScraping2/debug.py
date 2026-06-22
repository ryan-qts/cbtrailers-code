import requests
import re

session = requests.Session()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Warm up
session.get("https://www.bing.com/", headers=HEADERS, timeout=10)

# Search for a trailer part
query = "fender step trailer"
r = session.get(
    "https://www.bing.com/images/search",
    params={"q": query, "form": "HDRSC2"},
    headers=HEADERS,
    timeout=15
)

html = r.text
print(f"Status: {r.status_code}, Length: {len(html)}")

# Try every JSON-like pattern we can think of
patterns = {
    "murl &quot;":  r'murl&quot;:&quot;(https?://[^&]+?)&quot;',
    "murl escaped": r'murl\\u0022:\\u0022(https?://[^\\]+?)\\u0022',
    "iurl":         r'"iurl":"(https?://[^"]+)"',
    "imgurl":       r'imgurl=(https?://[^&"]+)',
    "src http":     r'src="(https?://[^"]+\.(?:jpg|jpeg|png|webp)[^"]*)"',
    "mediaUrl":     r'"mediaUrl":"(https?://[^"]+)"',
    "any jpg":      r'https?://(?!.*bing\.com)[^\s"\'<>&]+\.(?:jpg|jpeg|png|webp)',
}

for name, pat in patterns.items():
    matches = re.findall(pat, html, re.IGNORECASE)
    # filter out bing's own assets
    matches = [m for m in matches if 'bing.com/sa' not in m and 'bing.com/rp' not in m]
    print(f"\n{name}: {len(matches)} matches")
    for m in matches[:3]:
        print(f"  {m[:100]}")

# Dump surrounding context of first real image URL found
print("\n\n--- Context around first external image ---")
for pat in [r'murl', r'"iurl"', r'imgurl=']:
    idx = html.find(pat)
    if idx > 0:
        print(f"Pattern '{pat}' at {idx}:")
        print(repr(html[idx:idx+300]))
        print()
        break

# Save full HTML for manual inspection
with open(r"C:\Users\jerem\PyCharmMiscProject\scrape\imageScraping2\bing_debug.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Full HTML saved to bing_debug.html — open it in a text editor and search for a .jpg URL")