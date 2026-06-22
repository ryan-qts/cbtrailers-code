import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import re


# =========================
# LOAD MASTER CSV
# =========================

df_main = pd.read_csv("master.csv")

# normalize columns
df_main.columns = df_main.columns.str.strip().str.lower()

# ensure required columns exist
if "image" not in df_main.columns:
    df_main["image"] = ""

if "name" not in df_main.columns:
    raise Exception("Column 'name' not found in CSV")

# force string types
df_main["image"] = df_main["image"].fillna("").astype(str)
df_main["name"] = df_main["name"].fillna("").astype(str)

# =========================
# NAME CLEANER
# =========================

def clean_name(s):

    s = str(s).lower().strip()

    # normalize wording
    s = s.replace("w/", "with")

    # remove commas
    s = s.replace(",", "")

    # remove periods
    s = s.replace(".", "")

    # remove quotes
    s = s.replace('"', "")

    # remove apostrophes
    s = s.replace("'", "")

    # remove out of stock text
    s = s.replace("- out of stock", "")

    # collapse spaces
    s = re.sub(r"\s+", " ", s)

    return s.strip()

# create cleaned comparison column
df_main["clean_name"] = df_main["name"].apply(clean_name)

# =========================
# SHOPIFY COLLECTIONS
# =========================

subCategories = [
    "trailer-axles-spindles",
    "trailer-hubs-drums-caps",
    "trailer-brakes",
    "trailer-bearings-races-seals",
    "trailer-suspension",
    "trailer-tire-wheel-combos",
    "trailer-steel-wheels"
    "trailer-aluminum-wheels",
    "trailer-tires",
    "trailer-center-caps-lugnuts-misc",
    "trailer-incandescent-lights-bulb",
    "trailer-led-lights",
    "trailer-reflectors-tape-misc",
    "trailer-wire-harnesses-connectors",
    "trailer-chargers-electrical-accessories",
    "trailer-couplers-1",
    "trailer-jacks",
    "trailer-coupler-jack-accessories",
    "trailer-straps-chains-binders",
    "trailer-e-track-accessories",
    "trailer-tie-down-anchors-winches",
    "trailer-toolboxes",
    "landscape-trailer-accessories",
    "trailer-formed-bumpers-brackets-pockets",
    "trailer-cut-plate-parts",
    "trailer-channel-tube-pipe",
    "trailer-ramps",
    "trailer-springs-hinges",
    "trailer-latches-handles",
    "trailer-bolts-screws-rivets",
    "trailer-adhesive-tape-caulk",
    "trailer-decals-stickers",
    "trailer-hydraulics",
    "horse-trailer-specific",
    "trailer-windows-doors-vents",
    "recreational-vehicles-rvs",
    "tow-vehicle"
]

headers = {
    "User-Agent": "Mozilla/5.0"
}

matches_found = 0

# =========================
# SCRAPE LOOP
# =========================

for subCategory in subCategories:

    pages = 1

    while True:

        url = (
            f"https://www.ordertrailerparts.com/"
            f"collections/{subCategory}?page={pages}"
        )

        print(f"\nScraping: {url}")

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Failed page: {url}")
            break

        soup = BeautifulSoup(response.content, "html.parser")

        product_cards = soup.select(".prod-th")

        if not product_cards:
            print("No more products found")
            break

        # =========================
        # PRODUCT LOOP
        # =========================

        for card in product_cards:
            time.sleep(0.75)

            try:

                product_link = (
                    "https://www.ordertrailerparts.com"
                    + card["href"]
                )

                print(product_link)

                name_element = card.select_one(".title")

                base_name = (
                    name_element.get_text(strip=True)
                    if name_element else "N/A"
                )

                # =========================
                # OPEN PRODUCT PAGE
                # =========================

                product_response = requests.get(
                    product_link,
                    headers=headers
                )

                product_soup = BeautifulSoup(
                    product_response.content,
                    "html.parser"
                )

                # =========================
                # GET IMAGE
                # =========================

                image_url = ""

                image_element = product_soup.select_one(
                    "#product-shot img"
                )

                # fallback selector
                if not image_element:
                    image_element = product_soup.select_one(
                        ".product-main-image img"
                    )

                # extract URL
                if image_element:

                    image_url = (
                            image_element.get("src")
                            or image_element.get("data-src")
                            or ""
                    )

                    # fix Shopify protocol-less URLs
                    if image_url.startswith("//"):
                        image_url = "https:" + image_url

                    # remove thumbnail sizing
                    image_url = re.sub(
                        r'_(\d+x\d+)(\.\w+)',
                        r'\2',
                        image_url
                    )

                    print(f"IMAGE FOUND: {image_url}")

                else:

                    print("NO IMAGE FOUND")

                image_formula = f"=IMAGE(\"{image_url}\")"

                # =========================
                # VARIANT PRODUCTS
                # =========================

                variant_select = product_soup.select_one(
                    "#productSelect-product-template"
                )

                if variant_select:

                    variant_options = variant_select.select("option")

                    # multiple variants
                    if len(variant_options) > 1:

                        print(f"Variants Found: {len(variant_options)}")

                        for option in variant_options:


                            variant_text = option.get_text(
                                " ",
                                strip=True
                            )

                            # remove price
                            variant_name = re.sub(
                                r"-\s*\$.*",
                                "",
                                variant_text
                            ).strip()

                            # build full variant name
                            full_name = (
                                f"{base_name} - {variant_name}"
                            )

                            clean_full_name = clean_name(full_name)

                            # MATCH AGAINST CSV
                            matches = (
                                df_main["clean_name"]
                                == clean_full_name
                            )

                            if matches.any():

                                df_main.loc[
                                    matches,
                                    "image"
                                ] = image_formula

                                print(
                                    f"MATCHED IMAGE: "
                                    f"{clean_full_name}"
                                )

                                matches_found += matches.sum()

                            else:

                                print(
                                    f"NO MATCH: "
                                    f"{clean_full_name}"
                                )

                        # done with variants
                        continue

                # =========================
                # NORMAL PRODUCT
                # =========================

                clean_base_name = clean_name(base_name)

                matches = (
                    df_main["clean_name"]
                    == clean_base_name
                )

                if matches.any():

                    df_main.loc[
                        matches,
                        "image"
                    ] = image_formula

                    print(
                        f"MATCHED IMAGE: "
                        f"{clean_base_name}"
                    )

                    matches_found += matches.sum()

                else:

                    print(
                        f"NO MATCH: "
                        f"{clean_base_name}"
                    )

            except Exception as e:

                print(f"ERROR: {e}")

        pages += 1

        time.sleep(2)

# =========================
# CLEANUP
# =========================

# remove helper column
df_main.drop(columns=["clean_name"], inplace=True)

# save output
df_main.to_excel(
    "master_with_images.xlsx",
    index=False
)

print("\n=========================")
print("COMPLETE")
print("=========================")
print(f"Images Matched: {matches_found}")
print("Saved: master_with_images.csv")