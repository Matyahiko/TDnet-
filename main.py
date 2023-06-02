import time
import requests
import json
import random
import os
from pypdf import PdfReader
import schedule

class TdnetDownloader:
    def __init__(self, max_retries=5):
        self.max_retries = max_retries

    def get_url(self, URL):
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

    def download_pdf(self, data):
        total = len(data)
        count = 0
        failed_downloads = []

        for d in data:
            if d["company_code"][-1] == "0":
                retries = 0
                success = False

                while retries < self.max_retries and not success:
                    try:
                        pdf = requests.get(d["document_url"])
                        time.sleep(random.randint(6, 15))

                        date = d["pubdate"].split(" ")
                        name = date[0] + "_" + d["company_code"]
                        file_path = f"rawdata/{name}.pdf"

                        with open(file_path, "wb") as f:
                            f.write(pdf.content)

                        if self.validate_pdf(file_path):
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

    def validate_pdf(self, file_path):
        try:
            with open(file_path, "rb") as f:
             pdf = PdfReader(f)
             num_pages = len(pdf.pages)
            return num_pages > 0
        except Exception as e:
            print(f"Error validating PDF at {file_path}: {e}")
            return False

    def retry_failed_downloads(self):
        # Load the failed downloads
        if not os.path.exists("path_to_failed_downloads.json"):
            print("No failed downloads to retry.")
            return

        with open("path_to_failed_downloads.json", "r") as f:
            failed_downloads = json.load(f)

        # Remove the failed downloads file
        os.remove("path_to_failed_downloads.json")

        # Retry the downloads
        self.download_pdf(failed_downloads)

    def run(self):
        start_date = time.strftime("%Y%m%d", time.localtime(time.time() - 60 * 60 * 24 * 30))
        end_date = time.strftime("%Y%m%d", time.localtime(time.time()))

        # Set the limit of data to fetch
        limit = 10000

        URL = f"https://webapi.yanoshin.jp/webapi/tdnet/list/{start_date}-{end_date}.json?limit={limit}"

        # Fetch data from the URL
        data = self.get_url(URL)

        # Download PDF files
        self.download_pdf(data)

        # Retry failed downloads
        self.retry_failed_downloads()
"""
if __name__ == "__main__":
    downloader = TdnetDownloader(max_retries=5)
    downloader.run()
    
"""
downloader = TdnetDownloader(max_retries=5)
schedule.every().week.do(downloader.run())

while True:
    schedule.run_pending()
    time.sleep(1)
