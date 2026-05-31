import pandas as pd
from dateutil import parser

# LOAD
vu = pd.read_csv("ophtalmo_vus_clean.csv")
op = pd.read_csv("ophtalmo_operes_clean.csv")


def parse_and_get_age(date_str):
    """Parse date in various formats and calculate age"""
    if pd.isna(date_str):
        return None

    try:
        date_str = str(date_str).strip()

        # If it's just a year (4 digits)
        if date_str.isdigit() and len(date_str) == 4:
            return 2026 - int(date_str)

        # Try to parse as full date
        # Use dayfirst=True for European format (day/month/year)
        birth_date = parser.parse(date_str, dayfirst=True)
        return 2026 - birth_date.year

    except (ValueError, TypeError, parser.ParserError):
        return None


# -----------------------------
# FACT SCREENING
# -----------------------------
fact_screening = vu.copy()

fact_screening = fact_screening.rename(
    columns={"od": "acuite_od", "og": "acuite_og", "conclusion": "diagnostic"}
)

# création âge
fact_screening["age"] = fact_screening["date_naissance"].apply(parse_and_get_age)

# -----------------------------
# FACT SURGERY
# -----------------------------
fact_surgery = op.copy()

fact_surgery = fact_surgery.rename(columns={"type": "procedure"})

fact_surgery["age"] = fact_surgery["date_naissance"].apply(parse_and_get_age)

# normalisation status chirurgie
fact_surgery["status"] = "completed"

# -----------------------------
# EXPORT
# -----------------------------
fact_screening.to_csv("FACT_OPHTALMO_SCREENING.csv", index=False)
fact_surgery.to_csv("FACT_OPHTALMO_SURGERY.csv", index=False)

print("✔ FACT tables générées")
