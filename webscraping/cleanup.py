import pandas as pd

# Load CSV
df = pd.read_csv("finalProducts9.csv")

# Remove empty rows
df = df.dropna(subset=["sku", "price"])

# Add title length column
df["title_length"] = df["name"].str.len()

# Sort longest titles first
df = df.sort_values(
    by="title_length",
    ascending=False
)

# Find duplicates BEFORE removing them
duplicates_mask = df.duplicated(
    subset=["sku", "price"],
    keep="first"
)

removed_rows = df[duplicates_mask]

# Print removed rows
print("\n--- REMOVED DUPLICATES ---\n")

for _, row in removed_rows.iterrows():
    print(
        f"REMOVED: "
        f"Name='{row['name']}' | "
        f"Price='{row['price']}' | "
        f"SKU='{row['sku']}'"
    )

# Remove duplicates
df_cleaned = df.drop_duplicates(
    subset=["sku", "price"],
    keep="first"
)

# Remove helper column
df_cleaned = df_cleaned.drop(columns=["title_length"])

# Save cleaned CSV
df_cleaned.to_csv(
    "finalProducts9_cleaned.csv",
    index=False
)

print("\n--- COMPLETE ---")
print(f"Original rows: {len(df)}")
print(f"Removed rows: {len(removed_rows)}")
print(f"Final rows: {len(df_cleaned)}")