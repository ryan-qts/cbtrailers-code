import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import json
import re
import csv
import os

file_name = "finalProducts8.csv"

file_exists = os.path.exists(file_name)

products = []
subCategories = ["trailer-couplers-1", "trailer-jacks", "trailer-coupler-jack-accessories", "trailer-straps-chains-binders", "trailer-e-track-accessories", "trailer-tie-down-anchors-winches", "trailer-toolboxes", "landscape-trailer-accessories", "trailer-formed-bumpers-brackets-pockets", "trailer-cut-plate-parts", "trailer-channel-tube-pipe", "trailer-ramps", "trailer-springs-hinges", "trailer-latches-handles", "trailer-bolts-screws-rivets", "trailer-adhesive-tape-caulk", "trailer-decals-stickers", "trailer-hydraulics", "horse-trailer-specific", "trailer-windows-doors-vents", "recreational-vehicles-rvs", "tow-vehicle"]
headers = {"User-Agent": "Mozilla/5.0"}
with open(file_name, "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "price", "sku"])

    if not file_exists:
        writer.writeheader()
    for subCategory in subCategories:
        pages = 1
        while True:
            url = f"https://www.ordertrailerparts.com/collections/{subCategory}?page={pages}"
            print(f"Scraping page {pages}")
            headers = {"User-Agent": "Mozilla/5.0"}

            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                print(f"Failed page {url} - {response.status_code}")
                break
            soup = BeautifulSoup(response.content, "html.parser")

            product_cards = soup.select(".prod-th")
            print(f"Products on Page = {len(product_cards)}")
            if not product_cards:
                print(f"No products found: {subCategory} page {pages}")
                break

            for card in product_cards:
                print("-Product-")
                time.sleep(0.75)
                try:
                    # card itself is the link
                    product_link = card["href"]
                    product_link = "https://www.ordertrailerparts.com" + product_link
                    print(product_link)

                    name_element = card.select_one(".title")
                    name = name_element.get_text(strip=True) if name_element else "N/A"


                    product_response = requests.get(product_link, headers=headers)

                    product_soup = BeautifulSoup(product_response.content, "html.parser")

                    # CHECK FOR VARIANTS
                    variant_select = product_soup.select_one("#productSelect-product-template")

                    if variant_select:

                        variant_options = variant_select.select("option")

                        # Only process products with multiple variants
                        if len(variant_options) > 1:

                            print(f"Found {len(variant_options)} variants")

                            for option in variant_options:

                                variant_name = option.get_text(" ", strip=True)

                                sku = option.get("data-sku", "N/A").strip()

                                # Extract price
                                price = "N/A"

                                variant_text = option.get_text(" ", strip=True)

                                # Extract price from text
                                price_match = re.search(r"\$\s*([\d.,]+)", variant_text)

                                if price_match:
                                    price = price_match.group(1)
                                else:
                                    price = "N/A"

                                # Remove price from variant name
                                variant_name = re.sub(r"-\s*\$.*", "", variant_text).strip()

                                writer.writerow({
                                    "name": f"{name} - {variant_name}",
                                    "price": price,
                                    "sku": sku
                                })

                                products.append({
                                    "name": f"{name} - {variant_name}",
                                    "price": price,
                                    "sku": sku
                                })

                                print(f"Added Variant: {variant_name}")

                            continue

                    # NORMAL PRODUCT FALLBACK
                    sku_element = product_soup.select_one(".sku-info")
                    price_element = product_soup.select_one(".product-price")

                    if sku_element:
                        sku = sku_element.get_text(strip=True)
                        sku = sku.replace("SKU:", "").strip()
                    else:
                        sku = "N/A"

                    if price_element:
                        price = price_element.get_text(strip=True)
                        price = price.replace("$ ", "").strip()
                    else:
                        price = "N/A"


                    print(f"Added: {name} and {price} and {sku}")
                except Exception as e:
                    print(e)
            pages += 1
            time.sleep(3)
