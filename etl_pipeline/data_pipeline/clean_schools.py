import pandas as pd
import os
from utils import clean_lga_name
from config import RAW_DATA_DIR, CLEAN_DATA_DIR


def clean_schools_data():
    os.makedirs(CLEAN_DATA_DIR, exist_ok=True)

    #Load School Locations
    schools = pd.read_csv(os.path.join(RAW_DATA_DIR, "dv402-SchoolLocations2025.csv"), encoding="utf-8-sig")
    print("Loaded schools:", schools.shape)

    #Clean up the text data values
    if "School_Name" in schools.columns:
        schools["School_Name"] = schools["School_Name"].astype(str).str.replace(r"(St Mary)[^\w\s]+(s)", r"\1'\2", regex=True)

    #Drop unnecessary admin/postal columns
    drop_cols = [
        "Address_Line_2", "Address_State",
        "Postal_Address_Line_1", "Postal_Address_Line_2",
        "Postal_Town", "Postal_State", "Postal_Postcode",
        "Full_Phone_No"
    ]
    schools = schools.drop(columns=[c for c in drop_cols if c in schools.columns])
    print("Shape after dropping admin/postal columns:", schools.shape)

    #Missing value check
    missing_coords = schools[["X", "Y"]].isnull().sum()
    print("Missing X:", missing_coords["X"], "| Missing Y:", missing_coords["Y"])

    if missing_coords["X"] > 0 or missing_coords["Y"] > 0:
        print("WARNING: some schools are missing coordinates — review before mapping in Power BI")

    #Missing value check: LGA_Name
    missing_lga = schools["LGA_Name"].isnull().sum()
    print(f"Missing LGA_Name: {missing_lga} out of {len(schools)}")

    #Clean LGA names
    schools["LGA_Name_Clean"] = schools["LGA_Name"].apply(clean_lga_name)
    print("\nSample cleaned LGA names:")
    print(schools[["LGA_Name", "LGA_Name_Clean"]].drop_duplicates().head(10))

    #Check for duplicate School_No across Education Sectors
    dupes = schools[schools.duplicated(subset="School_No", keep=False)]
    if len(dupes) > 0:
        print(f"\nNOTE: {len(dupes)} rows share a School_No with another row across different "
              f"Education_Sector values (e.g. Government vs Independent). This is expected — "
              f"School_No is only unique WITHIN a sector, not globally. Downstream joins must "
              f"use School_No + Education_Sector together.")

    #Export
    output_path = os.path.join(CLEAN_DATA_DIR, "schools_clean.csv")
    schools.to_csv(output_path, index=False, encoding='utf-8')
    print(f"\nExported: {output_path} — shape {schools.shape}")

    return schools


if __name__ == "__main__":
    clean_schools_data()
