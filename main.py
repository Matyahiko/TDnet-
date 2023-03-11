import time
import requests
import json
import random


def get_url(URL):
    print("A")
    res = requests.get(URL)
    response_loads = json.loads(res.content)
    data_list = [data["Tdnet"] for data in response_loads["items"]]
     # pubdate, company_code, document_urlを抽出して辞書にまとめ、リストに格納
    extracted_data = []
    for item in data_list:
            extracted_item = {
                "pubdate": item["pubdate"],
                "company_code": item["company_code"],
                "document_url": item["document_url"]
            }
            extracted_data.append(extracted_item)
        
    print(extracted_data)
 
    
    with open("###################\\extracted_data.json", "w") as f:
        json.dump(extracted_data, f, indent=4)
        
   
    return 0

def get_pdf():
      with open("##################\\extracted_data.json", "r") as f:
        data = json.load(f)
        total = len(data)
        count = 0
        #print(type(data))
      for d in data:
         if d["company_code"][-1] == "0":
             pdf = requests.get(d["document_url"])
             count += 1
             progress = int(count / total * 100)
             print(f"Progress: {progress}%")

             time.sleep(random.randint(6, 15))
            
             date = d["pubdate"].split(" ")
             name = date[0] + "_" + d["company_code"]
             with open("row_pdf\\" + name + ".pdf", "wb") as f:
                f.write(pdf.content)
                
                return 0
    
    
    


if __name__ =="__main__":
    #今日から一か月前
    d = time.strftime("%Y%m%d", time.localtime(time.time() - 60 * 60 * 24 * 30))
    nd = time.strftime("%Y%m%d", time.localtime(time.time()))
    #取得数上限
    limit = 10

    URL = "https://webapi.yanoshin.jp/webapi/tdnet/list/"+d+"-"+nd+".json?limit="+str(limit)
    #print(URL)
    
    #urlリストを更新するなら1
    if (0):
        get_url(URL)
        #print(data_list)
        
    #pdfをダウンロードするなら1
    if (0):
        get_pdf()