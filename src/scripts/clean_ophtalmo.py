import pandas as pd
import re


def clean_columns(df):
    df.columns = (
        df.columns.str.replace("\n", "", regex=True)
        .str.replace(" ", "_")
        .str.replace("__", "_")
        .str.lower()
    )
    return df


def clean_text(x):
    if pd.isna(x):
        return x
    return str(x).replace("\n", " ").strip()


def extract_eye(value):
    if pd.isna(value):
        return None
    v = str(value).lower()
    if "od" in v:
        return "OD"
    if "og" in v:
        return "OG"
    return None


# -------------------------
# LOAD FILES (raw read)
# -------------------------
file_op = "opere.csv"
file_vu = "vu.csv"

op = pd.read_csv(file_op, sep=",", engine="python")
vu = pd.read_csv(file_vu, sep=",", engine="python")

# -------------------------
# CLEAN COLUMNS
# -------------------------
op = clean_columns(op)
vu = clean_columns(vu)

# -------------------------
# CLEAN TEXT FIELDS
# -------------------------
for col in op.columns:
    op[col] = op[col].apply(clean_text)

for col in vu.columns:
    vu[col] = vu[col].apply(clean_text)

# -------------------------
# FIX TELEPHONE
# -------------------------
if "telephone" in op.columns:
    op["telephone"] = op["telephone"].astype(str).str.replace(".0", "")

if "telephone" in vu.columns:
    vu["telephone"] = vu["telephone"].astype(str).str.replace(".0", "")

# -------------------------
# NORMALISATION AGE / DATE NAISSANCE
# -------------------------
for df in [op, vu]:
    if "date__naissance" in df.columns:
        df["date_naissance"] = pd.to_datetime(
            df["date__naissance"], errors="coerce", dayfirst=True
        )

# -------------------------
# EXTRACTION OEIL
# -------------------------
if "type" in op.columns:
    op["eye"] = op["type"].apply(extract_eye)

# -------------------------
# EXPORT CLEAN CSV
# -------------------------
op.to_csv("ophtalmo_operes_clean.csv", index=False)
vu.to_csv("ophtalmo_vus_clean.csv", index=False)

print("✔ Nettoyage terminé")
