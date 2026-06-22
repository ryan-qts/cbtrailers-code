import requests
import pandas as pd
from bs4 import BeautifulSoup
import time

import csv
import os

file_name = "finalProducts6.csv"

file_exists = os.path.exists(file_name)

products = []
subCategories = ["trailer-springs-hinges"]
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

                    sku_element = product_soup.select_one(".sku-info")
                    price_element = product_soup.select_one(".product-price")

                    if sku_element:
                        sku = sku_element.get_text(strip=True) if sku_element else "N/A"
                        sku = sku.replace("SKU:", "").strip()
                    else:
                        sku = "N/A"

                    if price_element:
                        price = price_element.get_text(strip=True) if price_element else "N/A"
                        price = price.replace("$ ", "").strip()
                    else:
                        price = "N/A"

                    writer.writerow({
                        "name": name,
                        "price": price,
                        "sku": sku
                    })

                    products.append({"name": name, "price": price, "sku": sku})
                    print(f"Added: {name} and {price} and {sku}")
                except Exception as e:
                    print(e)
            pages += 1
            time.sleep(3)
