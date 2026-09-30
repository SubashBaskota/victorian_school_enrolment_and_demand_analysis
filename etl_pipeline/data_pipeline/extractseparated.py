import os
import requests
from urllib.parse import unquote
from bs4 import BeautifulSoup
from config import DATASETS, BASE_PORTAL_URL, STANDARD_HEADERS, STRICT_HEADERS, RAW_DATA_DIR


def download_all_files():
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    print("Saving files to:", RAW_DATA_DIR)
    print("Running extraction...\n")

    for dataset in DATASETS:
        target_webpage = f"{BASE_PORTAL_URL}/{dataset}"
        print(f"Scanning: {dataset}...")

        try:
            page_response = requests.get(target_webpage, headers=STANDARD_HEADERS, timeout=10)

            if page_response.status_code == 200:
                soup = BeautifulSoup(page_response.text, 'html.parser')
                found_asset = False

                for element in soup.find_all('a', href=True):
                    link_url = element['href']

                    if any(ext in link_url.lower() for ext in ['.csv', '.zip', '.xlsx']):
                        found_asset = True
                        filename = unquote(link_url.split('/')[-1].split('?')[0])
                        if not filename or '.' not in filename:
                            ext = '.zip' if 'zip' in link_url.lower() else ('.xlsx' if 'xlsx' in link_url.lower() else '.csv')
                            filename = f"{dataset.split('/')[-1]}{ext}"

                        destination_path = os.path.join(RAW_DATA_DIR, filename)
                        print(f"   Link found: {link_url}")

                        download_headers = STRICT_HEADERS if "planning.vic.gov.au" in link_url else {**STANDARD_HEADERS, "Referer": target_webpage}
                        file_stream = requests.get(link_url, headers=download_headers, stream=True, timeout=15)

                        if file_stream.status_code == 200:
                            with open(destination_path, "wb") as f:
                                for chunk in file_stream.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            print(f"   Saved to: {destination_path}\n")
                        else:
                            print(f"   Download failed (HTTP {file_stream.status_code})\n")
                        break

                if not found_asset:
                    print("   No matching download links found.\n")
            else:
                print(f"Page request failed. Status: {page_response.status_code}\n")

        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}\n")

    print("Extraction complete.")


if __name__ == "__main__":
    download_all_files()