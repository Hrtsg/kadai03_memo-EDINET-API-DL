import os
import time
import zipfile

import pandas as pd
import requests

import japanize_matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

API_ENDPOINT = "https://disclosure.edinet-fsa.go.jp/api/v2"  # v2を使用する


def save_csv(docID, type=5):
    # """EDINETからデータを取得してフォルダに保存する

    # Args:
    #     docID (str): DocID
    # """
    assert type in [1, 2, 3, 4, 5], "typeの指定が間違っている"
    if type == 1:
        print(f"{docID}のXBRLデータを取得中")
    elif type == 2:
        print(f"{docID}のpdfデータを取得中")
    elif type in {3, 4}:
        print(f"{docID}のデータを取得中")
    elif type == 5:
        print(f"{docID}のcsvデータを取得中")
        time.sleep(5)

#EDINETのAPIにつなぐためのKeyを設定する。 
    r = requests.get(
        f"{API_ENDPOINT}/documents/{docID}",
        {
            "type": type,
            "Subscription-Key": os.environ.get("EDINET_API_KEY"),
        },
    )

# データをCSVにダウンロードする。
    if r is None:
        print("データの取得に失敗しました。csvFlag==1かどうか確認してください。")
    else:
        os.makedirs(f"{docID}", exist_ok=True)
        temp_zip = "uuid_89FD71B5_CD7B_4833-B30D‗5AA5006097E2.zip"

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

for docID in docID_dict.values():
    save_csv(docID, type=5)

dfs = []

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
all_data.head()

# CSVで落としたデータをプロットする。
def compare_company_IR(data, contextId, elementId, elementJpName):
    plot_data = data.query(f"要素ID=='{elementId}' and コンテキストID=='{contextId}'").copy()
    plot_data[elementJpName] = pd.to_numeric(plot_data["値"])
    sns.barplot(data=plot_data, x="会社名", y=elementJpName)
    plt.ylabel(elementJpName)
    plt.show()


compare_company_IR(
    all_data,
    "CurrentQuarterDuration",
    "jpcrp_cor:BasicEarningsLossPerShareSummaryOfBusinessResults",
    "EPS",
)

compare_company_IR(all_data, "CurrentYTDDuration", "jppfs_cor:GrossProfit", "粗利益")

