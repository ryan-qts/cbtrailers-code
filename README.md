# C&B Trailers / Quality Trailer Sales — Code Repository

Internal tooling and automation scripts for C&B Trailers and Quality Trailer Sales (QTS Idaho).

## Projects

### `webscraping/`
Scripts for scraping product data from supplier/vendor websites. Extracts SKUs, names, prices, and descriptions into CSV format.

- `webscraper.py` — initial scraper
- `webscraper2.py` / `webscraper3.py` — iterative improvements with better parsing
- `cleanup.py` — deduplication and data cleaning on scraped CSVs

### `csv_crossreferencing/`
Cross-references product lists from multiple sources (OTP, SRTC, internal master list) to reconcile part numbers and manufacturers.

- `crossreference.py` — matches parts across CSVs and flags discrepancies

### `imageScraping/`
First-pass image scraper — matches product names to images from vendor sites and embeds them into the master parts spreadsheet.

- `webscraperImg.py` — scrapes images by product name
- `add_images_to_parts.py` — merges image URLs into the master parts list

### `imageScraping2/`
Improved image pipeline with a manual review tool for quality control.

- `fetch_images.py` — fetches image candidates for each part
- `apply_images.py` — applies approved images to the master list
- `debug.py` — diagnostics for fetch failures
- `review_tool.html` — browser-based tool for reviewing/approving image matches

### `visionLed/`
Scraper for [VisionLED Lights](https://visionled-lights.com) — extracts product listings, prices, and specs into spreadsheet format.

- `visionled_scraper.py` — Playwright-based scraper (headless Chromium)
- `websiteScraper.py` — earlier BeautifulSoup version
- `diagnose.py` — product matching diagnostics

## Setup

```bash
pip install pandas openpyxl beautifulsoup4 requests playwright
playwright install chromium
```

## Contact

Ryan Gonzales — ryang@qtsidaho.com
