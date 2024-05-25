from flask import Flask, jsonify
import os
import time
import zipfile
import pandas as pd
import requests

app = Flask(__name__)

API_ENDPOINT = "https://disclosure.edinet-fsa.go.jp/api/v2"

# """EDINETからデータを取得してフォルダに保存する

    # Args:
    #     docID (str): DocID
    # """

def save_csv(docID, type=5):
    if type == 1:
        print(f"{docID}のXBRLデータを取得中")
    elif type == 2:
        print(f"{docID}のpdfデータを取得中")
    elif type in {3, 4}:
        print(f"{docID}のデータを取得中")
    elif type == 5:
        print(f"{docID}のcsvデータを取得中")
        time.sleep(5)

    r = requests.get(
        f"{API_ENDPOINT}/documents/{docID}",
        {
            "type": type,
            "Subscription-Key": os.environ.get("EDINET_API_KEY"),
        },
    )

    if r is None:
        print("データの取得に失敗しました。csvFlag==1かどうか確認してください。")
    else:
        os.makedirs(f"{docID}", exist_ok=True)
        temp_zip = "temp.zip"

        with open(temp_zip, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)

        with zipfile.ZipFile(temp_zip) as z:
            z.extractall(f"{docID}")

        os.remove(temp_zip)

docID_dict = {
    "商船三井": "S100STH6",
    "日本郵船": "S100SS7P",
    "玉井商船株式会社": "S100STLS",
    "川崎汽船": "S100SRTI",
    "飯野海運": "S100SP9O",
}

@app.route('/start', methods=['GET'])
def start():
    dfs = []
    for docID in docID_dict.values():
        save_csv(docID, type=5)

    for companyName, docID in docID_dict.items():
        csv_savedir = os.path.join(docID, "XBRL_TO_CSV")
        filelist = [f for f in os.listdir(csv_savedir) if f.startswith("jpcrp")]
        if len(filelist) > 0:
            df = pd.read_csv(
                os.path.join(csv_savedir, filelist[0]), encoding="utf-16", sep="\t"
            )
            df["会社名"] = [companyName for _ in range(df.shape[0])]
            dfs.append(df)

    all_data = pd.concat(dfs)
    return jsonify(all_data.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)
