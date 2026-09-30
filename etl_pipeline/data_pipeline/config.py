import os

DATASETS = [
    "dataset/victorian-government-school-zones-2026",
    "dataset/school-locations-2025",
    "dataset/vif2023-lga-population-age-sex-projections-to-2036",
    "dataset/all-schools-fte-enrolments-feb-2023-victoria",
    "dataset/all-schools-fte-enrolments-feb-2024-victoria",
    "dataset/all-schools-fte-enrolments-feb-2025-victoria"
]

BASE_PORTAL_URL = "https://discover.data.vic.gov.au"
STANDARD_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-AU,en;q=0.9",
}

STRICT_HEADERS = {
    **STANDARD_HEADERS,
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.planning.vic.gov.au/",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "raw_data")
CLEAN_DATA_DIR = os.path.join(PROJECT_ROOT, "etl_pipeline", "clean_data")