import pandas as pd
import os
from utils import clean_lga_name
from config import RAW_DATA_DIR, CLEAN_DATA_DIR


def safe_read_csv(file_name):
    """Loads files by automatically choosing between UTF-8 and CP1252."""
    full_path = os.path.join(RAW_DATA_DIR, file_name)
    try:
        # Fallback to legacy Windows encoding (CP1252) if standard UTF-8-sig fails
        return pd.read_csv(full_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(full_path, encoding="cp1252")


def clean_enrolments_data():
    os.makedirs(CLEAN_DATA_DIR, exist_ok=True)

    # Load all three enrolment years safely
    enrol_2023 = safe_read_csv("dv355-VIC All Schools Enrolments 2023.csv")
    enrol_2024 = safe_read_csv("dv377_DataVic-AllSchoolsEnrolments-2024.csv")
    enrol_2025 = safe_read_csv("dv403-AllSchoolsEnrolments-2025.csv")

    # Clean column names (strip stray quotes and BOM artifacts)
    def clean_columns(df):
        new_cols = []
        for col in df.columns:
            c = col.replace('"', '').replace('ï»¿', '').strip()
            new_cols.append(c)
        df.columns = new_cols
        return df

    enrol_2023 = clean_columns(enrol_2023)
    enrol_2024 = clean_columns(enrol_2024)
    enrol_2025 = clean_columns(enrol_2025)

    # Align geography column names across years 
    enrol_2024 = enrol_2024.rename(columns={"DE_Admin_Region": "Region_Name", "DE_Admin_AREA": "Area_Name"})
    enrol_2025 = enrol_2025.rename(columns={"AREA_Name": "Area_Name"})

    for col in ["Region_Name", "LGA_Name", "Area_Name"]:
        if col not in enrol_2023.columns:
            enrol_2023[col] = pd.NA

    # Backfill 2023's missing LGA/Region/Area using 2025, then 2024 as fallback
    lga_lookup = enrol_2025[["School_No", "LGA_Name", "Region_Name", "Area_Name"]].drop_duplicates(subset="School_No")
    enrol_2023 = enrol_2023.drop(columns=["Region_Name", "LGA_Name", "Area_Name"])
    enrol_2023 = enrol_2023.merge(lga_lookup, on="School_No", how="left")

    lga_lookup_2024 = enrol_2024[["School_No", "LGA_Name", "Region_Name", "Area_Name"]].drop_duplicates(subset="School_No")
    enrol_2023 = enrol_2023.set_index("School_No")
    lga_lookup_2024_idx = lga_lookup_2024.set_index("School_No")
    enrol_2023["LGA_Name"] = enrol_2023["LGA_Name"].fillna(lga_lookup_2024_idx["LGA_Name"])
    enrol_2023["Region_Name"] = enrol_2023["Region_Name"].fillna(lga_lookup_2024_idx["Region_Name"])
    enrol_2023["Area_Name"] = enrol_2023["Area_Name"].fillna(lga_lookup_2024_idx["Area_Name"])
    enrol_2023 = enrol_2023.reset_index()

    # Manual fill for the remaining schools not found in 2024/2025 due to closures/renumbering
    manual_lga_map = {
        212: "Greater Shepparton", 524: "Maribyrnong", 1292: "Stonnington",
        1529: "Monash", 1225: "Mitchell", 2744: "East Gippsland",
        2805: "Horsham", 2956: "Yarra Ranges", 3426: "Swan Hill",
        3907: "Greater Shepparton", 4324: "Wellington", 4767: "East Gippsland",
        5401: "Moira", 8215: "East Gippsland",
    }
    enrol_2023["LGA_Name"] = enrol_2023["LGA_Name"].fillna(enrol_2023["School_No"].map(manual_lga_map))

    still_missing = enrol_2023["LGA_Name"].isnull().sum()
    print(f"2023 rows still missing LGA_Name after all backfill attempts: {still_missing}")

    # Concatenate all three years
    enrol_2023["Year"] = 2023
    enrol_2024["Year"] = 2024
    enrol_2025["Year"] = 2025

    fact_enrolments = pd.concat([enrol_2023, enrol_2024, enrol_2025], ignore_index=True)

    expected_rows = len(enrol_2023) + len(enrol_2024) + len(enrol_2025)
    assert len(fact_enrolments) == expected_rows, "Row count mismatch after concatenation!"
    print("Combined shape:", fact_enrolments.shape)
    print("Year breakdown:\n", fact_enrolments["Year"].value_counts().sort_index())

   # Clean School_Name across all years
    if "School_Name" in fact_enrolments.columns:
        fact_enrolments["School_Name"] = fact_enrolments["School_Name"].astype(str).str.replace(r"(St Mary)[^\w\s]+(s)", r"\1'\2", regex=True)

    # Standardise LGA names (handles nested double-parenthesis cases) 
    fact_enrolments["LGA_Name_Clean"] = fact_enrolments["LGA_Name"].apply(clean_lga_name)

    # Drop constant/unneeded columns 
    if "CENSUS_TYPE" in fact_enrolments.columns and fact_enrolments["CENSUS_TYPE"].nunique() == 1:
        fact_enrolments = fact_enrolments.drop(columns=["CENSUS_TYPE"])
        print("Dropped CENSUS_TYPE (constant column)")

    # Export
    output_path = os.path.join(CLEAN_DATA_DIR, "fact_enrolments.csv")
    fact_enrolments.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Exported: {output_path} — shape {fact_enrolments.shape}")

    return fact_enrolments


if __name__ == "__main__":
    clean_enrolments_data()
