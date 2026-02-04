import pandas as pd

# Read raw Orange Book CSV (no headers)
df = pd.read_csv("data/material.csv", header=None)

# Keep only rows that start with IPE
df = df[df[0].astype(str).str.startswith("IPE")].copy()

# Columns we need (by index, based on Orange Book format)
# 0  -> profile
# 2  -> mass per metre [kg/m]
# 15 -> Iy about y-y [cm^4]   (e.g. "278,000")
# 19 -> Wel,y [cm^3]         (e.g. "7,140")

df_clean = pd.DataFrame()
df_clean["profile"] = df[0]
df_clean["mass_kg_per_m"] = df[2].astype(float)

# Remove commas and convert units
df_clean["I_mm4"] = (
    df[15].astype(str).str.replace(",", "").astype(float) * 1e4
)
df_clean["W_mm3"] = (
    df[19].astype(str).str.replace(",", "").astype(float) * 1e3
)

# Write final materials.csv
df_clean.to_csv("data/materials.csv", index=False)

print("materials.csv created successfully")
print(df_clean.head())
