"""
OTP Product Image Fetch - Selenium + Google Images
====================================================
Uses a real visible Chrome browser to search Google Images.

Requirements:
    pip install selenium openpyxl webdriver-manager

Usage:
    python fetch_images.py
"""

import json, os, random, re, time, openpyxl
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote_plus

INPUT_FILE = r"C:\Users\jerem\PyCharmMiscProject\scrape\imageScraping2\MasterList_import_ready_.xlsx"
CANDIDATES_FILE = r"C:\Users\jerem\PyCharmMiscProject\scrape\imageScraping2\image_candidates.json"
REVIEWED_FILE = r"C:\Users\jerem\PyCharmMiscProject\scrape\imageScraping2\image_reviewed.json"
DELAY_MIN = 3.0
DELAY_MAX = 5.5

BAD_DOMAINS = [
    'pinterest', 'instagram', 'facebook', 'twitter', 'tiktok', 'tumblr',
    'reddit', 'wikipedia', 'wikimedia', 'blogspot', 'shutterstock', 'getty',
    'istock', 'dreamstime', 'alamy', 'depositphotos', 'freepik', 'unsplash',
    'pexels', 'stock.adobe', 'bigstock', '123rf', 'pixabay', 'craiyon',
    'explicit', 'adult', 'xxx', 'porn', 'nude', 'people.com', 'ibtimes',
    'gamerant', 'autoevolution', 'rubylovesyou', 'pictoa', 'nba.com',
]

NOISE = {
    'the', 'for', 'with', 'and', 'or', 'in', 'of', 'a', 'an', 'w', 'x',
    'assy', 'qty', 'each', 'blk', 'wht', 'dia', 'hgt', 'diam', 'assembly',
    'inch', 'inches', 'lbs', 'lb', 'ft', 'mm', 'cm', 'ga', 'gauge',
}


def make_query(name, mfr_sku=""):
    q = re.sub(r'[\"\'""″′(){}\[\],/\\]', ' ', name)
    q = re.sub(r'\b\d+[\./]?\d*\s*[xX]\s*[\d.]+\b', ' ', q)
    q = re.sub(r'\b\d+\.?\d*\s*(?:ga|GA|lbs?|in|ft|mm)\b', ' ', q)
    q = re.sub(r'\b\.\d+\b', ' ', q)
    q = re.sub(r'\s+', ' ', q).strip()
    words = [w for w in q.split()
             if len(w) >= 3 and w.lower() not in NOISE and not re.match(r'^\d+$', w)]
    core = ' '.join(words[:5])
    if mfr_sku and len(mfr_sku) > 3 and not re.match(r'^\d+\.?\d*$', mfr_sku):
        sku = mfr_sku.strip().lstrip('\u200e')
        return f"{sku} {' '.join(words[:3])} trailer part"
    return f"{core} trailer part"


def is_bad(url):
    return any(d in url.lower() for d in BAD_DOMAINS)


def make_driver():
    opts = Options()
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument("--lang=en-US")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


def get_google_images(driver, query):
    url = f"https://www.google.com/search?q={quote_plus(query)}&tbm=isch&safe=active"
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-id], img.rg_i, div.isv-r"))
        )
    except Exception:
        time.sleep(3)

    time.sleep(random.uniform(1.0, 2.0))

    results = []
    try:
        image_data = driver.execute_script("""
            const results = [];
            const seen = new Set();
            const allText = document.documentElement.innerHTML;
            const matches = allText.matchAll(/"ou":"(https?:[^"\\\\]+)"/g);
            for (const m of matches) {
                const url = m[1];
                if (!seen.has(url)) {
                    seen.add(url);
                    results.push({ full: url, thumb: url });
                }
            }
            // Also grab encrypted thumbnails as fallback
            const thumbs = [];
            document.querySelectorAll('img').forEach(img => {
                const src = img.src || '';
                if (src.includes('encrypted-tbn') && !seen.has(src)) {
                    seen.add(src);
                    thumbs.push({ full: src, thumb: src });
                }
            });
            return results.length > 0 ? results : thumbs;
        """)

        seen = set()
        for item in image_data:
            url = item.get('full', '')
            if not url or url in seen or is_bad(url):
                continue
            if not re.search(r'\.(jpg|jpeg|png|webp)', url, re.IGNORECASE):
                # allow encrypted-tbn thumbnails even without extension
                if 'encrypted-tbn' not in url:
                    continue
            seen.add(url)
            results.append(item)
            if len(results) >= 6:
                break

    except Exception as e:
        print(f"    Error extracting images: {e}")

    return results


def load_candidates():
    if os.path.exists(CANDIDATES_FILE):
        with open(CANDIDATES_FILE, encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_candidates(c):
    with open(CANDIDATES_FILE, 'w', encoding='utf-8') as f:
        json.dump(c, f, indent=2, ensure_ascii=False)


def main():
    print(f"Loading {INPUT_FILE}...")
    wb = openpyxl.load_workbook(INPUT_FILE)
    ws = wb.active

    # Build header map — handles None/extra columns safely
    header_map = {}
    for i, cell in enumerate(ws[1]):
        if cell.value and cell.value not in header_map:
            header_map[cell.value] = i  # 0-based

    print(f"Columns found: {[k for k in header_map.keys() if k]}")

    required = ['image', 'item_type', 'name', 'manufacturer sku']
    for col in required:
        if col not in header_map:
            print(f"ERROR: column '{col}' not found in spreadsheet!")
            return

    img_i = header_map['image']
    type_i = header_map['item_type']
    name_i = header_map['name']
    mfr_i = header_map['manufacturer sku']

    candidates = load_candidates()
    reviewed = set()
    if os.path.exists(REVIEWED_FILE):
        with open(REVIEWED_FILE, encoding='utf-8') as f:
            reviewed = set(json.load(f).keys())

    all_rows = []
    for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if str(row[type_i] or '').strip() != 'Product':
            continue
        if str(row[img_i] or '').strip():
            continue
        name = str(row[name_i] or '').strip()
        if not name:
            continue
        all_rows.append((row_num, name, str(row[mfr_i] or '').strip()))

    todo = [r for r in all_rows if str(r[0]) not in candidates and str(r[0]) not in reviewed]

    print(f"Products needing images : {len(all_rows)}")
    print(f"Already fetched         : {len(candidates)}")
    print(f"Already reviewed        : {len(reviewed)}")
    print(f"To fetch now            : {len(todo)}\n")

    if not todo:
        print("Nothing left to fetch — open review_tool.html to review.")
        return

    print("Opening Chrome... (a browser window will appear, don't close it)\n")
    driver = make_driver()

    try:
        driver.get("https://www.google.com/")
        time.sleep(2)

        for i, (row_num, name, mfr_sku) in enumerate(todo):
            # Close any extra tabs
            while len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[-1])
                driver.close()
            driver.switch_to.window(driver.window_handles[0])

            key = str(row_num)
            query = make_query(name, mfr_sku)

            print(f"[{i + 1}/{len(todo)}] {name[:55]}")
            print(f"  Query: {query[:70]}")

            results = get_google_images(driver, query)
            print(f"  Results: {len(results)}")

            candidates[key] = {
                "row": row_num,
                "name": name,
                "mfr_sku": mfr_sku,
                "query": query,
                "results": results
            }

            if (i + 1) % 15 == 0:
                save_candidates(candidates)
                print(f"  → Checkpoint saved ({len(candidates)} total)\n")

            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        save_candidates(candidates)
        driver.quit()
        found = sum(1 for v in candidates.values() if v.get('results'))
        print(f"\nDone! {found}/{len(candidates)} with results.")
        print("Open review_tool.html and load image_candidates.json")


if __name__ == "__main__":
    main()
