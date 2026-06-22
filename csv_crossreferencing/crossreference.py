import pandas as pd
import re

# LOAD FILES
df_main = pd.read_excel("MasterListQualityTrailer.xlsx")
df_vision = pd.read_excel("visionled_updated.xlsx")

# CLEAN COLUMN NAMES
df_main.columns = df_main.columns.str.strip().str.lower()
df_vision.columns = df_vision.columns.str.strip().str.lower()

print("MAIN:", df_main.columns.tolist())
print("vision:", df_vision.columns.tolist())

# COLUMN SETUP
main_sku_column = "sku"
main_mfg_column = "manufacturer sku"

vision_sku_column = "REF"

# CLEAN SKUs
df_main[main_sku_column] = df_main[main_sku_column].astype(str).str.strip()
df_vision[vision_sku_column] = df_vision[vision_sku_column].astype(str).str.strip()

# PREFIX CLEANER
def clean_sku(s):
    s = str(s).lower().strip()

    # remove common prefixes like OTP-, SRTC-, etc.
    s = re.sub(r'OTP-', '', s)

    return s

# PRE-CLEAN vision LIST (faster)
vision_parts = df_vision[vision_sku_column].dropna().tolist()

matches_found = 0

for i, main_row in df_main.iterrows():
#main_sku_column = sku
    main_sku = clean_sku(main_row[main_sku_column])

    matched_value = None

    for i, part_number in df_vision.iterrows():

        part_clean = clean_sku(part_number)

        if part_clean == main_sku or part_clean in main_sku:

            matched_value = part_number
            break

    if matched_value:

        df_main.at[i, main_mfg_column] = matched_value
        df_main.at[i, "image"] = df_vision[]
        print(f"MATCHED: {main_row[main_sku_column]} -> {matched_value}")

# SAVE OUTPUT
df_main.to_csv(
    "finalProducts6_with_manufacturer.csv",
    index=False
)

print("\n--- COMPLETE ---")
print(f"Matches Found: {matches_found}")
print("Saved as: finalProducts6_with_manufacturer.csv")