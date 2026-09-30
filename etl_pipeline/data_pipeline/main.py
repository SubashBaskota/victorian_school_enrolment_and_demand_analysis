from extract import download_all_files
from clean_schools import clean_schools_data
from clean_enrolments import clean_enrolments_data
from clean_population import clean_population_data


def run_phase1():
    print("=" * 60)
    print("PHASE 1: EXTRACTION")
    print("=" * 60)
    download_all_files()

    print("\n" + "=" * 60)
    print("PHASE 1: CLEANING — SCHOOLS")
    print("=" * 60)
    clean_schools_data()

    print("\n" + "=" * 60)
    print("PHASE 1: CLEANING — ENROLMENTS")
    print("=" * 60)
    clean_enrolments_data()

    print("\n" + "=" * 60)
    print("PHASE 1: CLEANING — POPULATION")
    print("=" * 60)
    clean_population_data()

    print("\n" + "=" * 60)
    print("PHASE 1 COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_phase1()