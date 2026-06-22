# CLAUDE.md — C&B Trailers / QTS Idaho Code Repo

This file gives Claude context for working in this repository.

## What this repo is

Internal automation scripts for **C&B Trailers / Quality Trailer Sales (QTS Idaho)**. All scripts support product data management — scraping vendor sites, cleaning data, matching images, and building import-ready spreadsheets.

## Project overview

| Folder | Purpose |
|---|---|
| `webscraping/` | Scrapes product listings (SKU, name, price, description) from vendor sites into CSV |
| `csv_crossreferencing/` | Reconciles part numbers across OTP, SRTC, and internal master lists |
| `imageScraping/` | First-gen image scraper — finds and embeds product images into spreadsheets |
| `imageScraping2/` | Improved image pipeline with review/approval workflow |
| `visionLed/` | Dedicated scraper for visionled-lights.com using Playwright |

## Tech stack

- **Python 3** with `pandas`, `openpyxl`, `requests`, `beautifulsoup4`
- **Playwright** (async) for JavaScript-heavy pages (visionLed scraper)
- Output formats: `.csv`, `.xlsx`

## Key files

- Master parts list lives in `imageScraping2/MasterList_import_ready_.xlsx` (not in repo — too large; kept locally)
- `imageScraping2/review_tool.html` — open in browser to review image candidates before applying

## Notes for Claude

- Data files (`.csv`, `.xlsx`, `.json`) are excluded from git — work with Python scripts only unless asked otherwise
- The VisionLED scraper (`visionLed/visionled_scraper.py`) requires `playwright install chromium` to run
- When helping with scraping tasks, prefer `requests` + `BeautifulSoup` unless the site is JS-rendered
- Company contact: Ryan Gonzales — ryang@qtsidaho.com
