import requests
import pandas as pd
from bs4 import BeautifulSoup
import time

products = []
pages = 1
while True:
    url = f"https://www.ordertrailerparts.com/collections/trailer-axles-spindles?page={pages}"
    print(f"Scraping page {pages}")
    response = requests.get(url)

    if response.status_code == 200:
        print("URL - Valid")
    soup = BeautifulSoup(response.content, "html.parser")
    product_cards = soup.select(".prod-th")
    print(f"Products on Page = {len(product_cards)}")
    if len(product_cards) == 0:
        print("Error - no products found")
        break

    for card in product_cards:
        print("-Product-")
        try:
            name = card.select_one(".title").get_text(strip=True)
            price = card.select_one(".price-money").get_text(strip=True)
            products.append({"name": name, "price": price})
            print(f"Added: {name} and {price}")
        except Exception as e:
            print(e)
    pages += 1
    time.sleep(1)
df = pd.DataFrame(products)
df.to_csv("products.csv", index=False)