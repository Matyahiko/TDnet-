import time
import requests
import json
import random
import os
from PyPDF2 import PdfFileReader
import schedule
import time

MAX_RETRIES = 5

def get_url(URL):
    res = requests.get(URL)
    response_loads = json.loads(res.content)
    data_list = [data["Tdnet"] for data in response_loads["items"]]

    # pubdate, company_code, document_urlを抽出して辞書にまとめ、リストに格納
    extracted_data = [
        {
            "pubdate": item["pubdate"],
            "company_code": item["company_code"],
            "document_url": item["document_url"]
        } for item in data_list]

    # Save the extracted data
    with open("path_to_extracted_data.json", "w") as f:
        json.dump(extracted_data, f, indent=4)
        
    return extracted_data

def download_pdf(data, max_retries):
    total = len(data)
    count = 0
    failed_downloads = []

    for d in data:
        if d["company_code"][-1] == "0":
            retries = 0
            success = False

            while retries < max_retries and not success:
                try:
                    pdf = requests.get(d["document_url"])
                    time.sleep(random.randint(6, 15))

                    date = d["pubdate"].split(" ")
                    name = date[0] + "_" + d["company_code"]
                    file_path = f"row_pdf/{name}.pdf"

                    with open(file_path, "wb") as f:
                        f.write(pdf.content)

                    if validate_pdf(file_path):
                        success = True
                        count += 1
                        progress = int(count / total * 100)
                        print(f"Progress: {progress}%")
                    else:
                        retries += 1
                        os.remove(file_path)  # ダウンロードした壊れたファイルを削除
                        print(f"Failed to validate {file_path}. Retrying download.")

                except Exception as e:
                    print(f"Failed to download {d['document_url']}: {e}")
                    retries += 1

            if not success:
                failed_downloads.append(d)

    # Save the failed downloads
    if failed_downloads:
        with open("path_to_failed_downloads.json", "w") as f:
            json.dump(failed_downloads, f, indent=4)

    return failed_downloads

def validate_pdf(file_path):
    try:
        with open(file_path, "rb") as f:
            pdf = PdfFileReader(f)
            num_pages = pdf.getNumPages()
            return num_pages > 0
    except Exception:
        return False

def retry_failed_downloads(max_retries):
    # Load the failed downloads
    if not os.path.exists("path_to_failed_downloads.json"):
        print("No failed downloads to retry.")
        return

    with open("path_to_failed_downloads.json", "r") as f:
        failed_downloads = json.load(f)

    # Remove the failed downloads file
    os.remove("path_to_failed_downloads.json")

    # Retry the downloads
    download_pdf(failed_downloads, max_retries)


def run_code():
    start_date = time.strftime("%Y%m%d", time.localtime(time.time() - 60 * 60 * 24 * 30))
    end_date = time.strftime("%Y%m%d", time.localtime(time.time()))
    
    # Set the limit of data to fetch
    limit = 10000

    URL = f"https://webapi.yanoshin.jp/webapi/tdnet/list/{start_date}-{end_date}.json?limit={limit}"

    # Fetch data from the URL
    data = get_url(URL)

    # Set the maximum number of retries
    max_retries = 5
        
    # Download PDF files
    download_pdf(data, max_retries)

    # Retry failed downloads
    retry_failed_downloads(max_retries)


schedule.every().week.do(run_code)


while True:
    schedule.run_pending()
    time.sleep(1)