import pandas as pd
import os
from utils import clean_lga_name
from config import RAW_DATA_DIR, CLEAN_DATA_DIR


def clean_population_data():
    os.makedirs(CLEAN_DATA_DIR, exist_ok=True)

    # --- Load the file ---
    # This is the September 2023 VIF release (LGA-only, no VIFSA sub-area
    # breakdown, figures rounded to nearest 10). It differs from the December 2023
    # second release used in initial manual exploration, but this is the version
    # currently discoverable via DataVic's automated catalog/API.
    # header=[8,9]: row 8 = year, row 9 = column labels (same position as before)
    vif_path = os.path.join(RAW_DATA_DIR, "VIF2023_LGA_Pop_Age_Sex_Projections_to_2036.xlsx")

    vif_population = pd.read_excel(
        vif_path,
        sheet_name="ERP_by_Age_Persons",
        header=[8, 9]
    )
    print("Shape after initial load:", vif_population.shape)

    # Flatten the two-row header into clean single column names
    def flatten_col(col):
        year, label = col
        label_clean = str(label).replace("\n", " ").replace('"', '').strip()
        if "LGA" in label_clean or label_clean == "VIFSA":
            return label_clean.replace("  ", " ")
        age_band = label_clean.replace("Persons", "").strip()
        return f"{int(year)}_{age_band}"

    vif_population.columns = [flatten_col(c) for c in vif_population.columns]

    # Keep only rows with a valid numeric LGA code
    # This automatically drops: the Victoria state-total row (blank LGA code),
    # any trailing blank/footer rows, and any stray notes rows —
    # without needing to know the exact row count in advance.
    vif_population = vif_population[pd.to_numeric(vif_population["LGA code"], errors="coerce").notna()]
    vif_population = vif_population.reset_index(drop=True)
    print("Shape after filtering to valid LGA rows:", vif_population.shape)
    print("Unique LGAs:", vif_population["LGA"].nunique())

    # --- Standardise LGA names ---
    vif_population["LGA_Name_Clean"] = vif_population["LGA"].apply(clean_lga_name)

    # Split the 10-14 age band (40% Primary, 60% Secondary) to create school cohorts
    years = [2026, 2031, 2036]
    records = []

    for y in years:
        for _, row in vif_population.iterrows():
            primary_total = row[f"{y}_5-9"] + row[f"{y}_10-14"] * 0.4
            secondary_total = row[f"{y}_10-14"] * 0.6 + row[f"{y}_15-19"]
            records.append({
                "LGA_Name_Clean": row["LGA_Name_Clean"],
                "Year": y,
                "Primary_Demand": primary_total,
                "Secondary_Demand": secondary_total
            })

    population_clean = pd.DataFrame(records)
    print("Population cohort shape:", population_clean.shape)

    population_clean["Primary_Demand"] = population_clean["Primary_Demand"].round(0)
    population_clean["Secondary_Demand"] = population_clean["Secondary_Demand"].round(0)

    # Export 
    output_path = os.path.join(CLEAN_DATA_DIR, "population_clean.csv")
    population_clean.to_csv(output_path, index=False)
    print(f"Exported: {output_path} — shape {population_clean.shape}")

    return population_clean


if __name__ == "__main__":
    clean_population_data()