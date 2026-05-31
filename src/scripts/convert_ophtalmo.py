import pandas as pd

file_path = "data/input/Excel_Ophtalmologie.xlsx"

# Lire le fichier Excel (tous les sheets)
xls = pd.ExcelFile(file_path)

print("Sheets disponibles :", xls.sheet_names)

# Boucle sur chaque sheet
for sheet in xls.sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet)

    # Nettoyage léger des noms de colonnes
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Nom de sortie CSV sécurisé
    output_file = f"ophtalmologie_{sheet.lower().replace(' ', '_')}.csv"

    df.to_csv(output_file, index=False, encoding="utf-8")

    print(f"Export terminé : {output_file} ({len(df)} lignes)")
