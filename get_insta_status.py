import datetime
import glob

import gspread
import pandas as pd
import requests

from local_config import *

version = "v17.0"


def basic_info():
    # 初期
    config = dict()
    # アクセストークン※facebook開発アプリから取得
    config["access_token"] = ACCESS_TOKEN
    # アプリID※facebook開発アプリから取得
    config["app_id"] = APP_ID
    # アプリシークレット※facebook開発アプリから取得
    config["app_secret"] = APP_SECRET
    # インスタグラムビジネスアカウントID※facebook開発アプリから取得
    config["instagram_account_id"] = INSTAGRAM_ACCOUNT_ID
    # APIバージョン
    config["version"] = version
    # 【修正不要】graphドメイン
    config["graph_domain"] = "https://graph.facebook.com/"
    # 【修正不要】エンドポイント
    config["endpoint_base"] = config["graph_domain"] + config["version"] + "/"
    # 出力
    return config

    # リクエスト


params = basic_info()  # リクエストパラメータ

# アクセス情報
business_account_id = INSTAGRAM_ACCOUNT_ID
token = ACCESS_TOKEN
username = USER_NAME
fields = "name,username,biography,follows_count,followers_count,media_count"
media_fields = "timestamp,permalink,media_url,like_count,comments_count,caption"
period = "day"


# ユーザー情報を取得する
def user_info(
    business_account_id=INSTAGRAM_ACCOUNT_ID,
    token=ACCESS_TOKEN,
    username=username,
    fields=fields,
):
    request_url = (
        "https://graph.facebook.com/"
        + version
        + "/{business_account_id}?fields=business_discovery.username({username}){{{fields}}}&access_token={token}".format(
            business_account_id=business_account_id,
            username=username,
            fields=fields,
            token=token,
        )
    )
    #     print(request_url)
    response = requests.get(request_url)
    return response.json()["business_discovery"]


# 昨日のアカウントステータスを取得する
delta_days = 1
today = datetime.datetime.today()
date_delta = datetime.datetime.today() - datetime.timedelta(days=delta_days)
yyyymmdd_td = "{yyyy}/{mm}/{dd}".format(yyyy=today.year, mm=today.month, dd=today.day)
yyyymmdd_delta = "{yyyy}/{mm}/{dd}".format(
    yyyy=date_delta.year, mm=date_delta.month, dd=date_delta.day
)
print("今日の日付：", yyyymmdd_td)
print("遡った日付：", yyyymmdd_delta)

# エンドポイントURLの作成
metric = ["follower_count", "impressions", "profile_views", "reach"]
metric_for_url = ""
for mt in metric:
    metric_for_url += mt + "%2C"
metric_for_url = metric_for_url.rstrip("%2C")

request_url = (
    params["endpoint_base"]
    + params["instagram_account_id"]
    + "/insights?access_token="
    + params["access_token"]
    + "&metric="
    + metric_for_url
    + "&period=day"
    + "&since="
    + yyyymmdd_delta
    + "&until="
    + yyyymmdd_td
)
response = requests.get(request_url).json()["data"]

day_n = delta_days - 1
end_time_yesterday = response[0]["values"][day_n]["end_time"]
follower_count_yesterday = response[0]["values"][day_n]["value"]
impressions_yesterday = response[1]["values"][day_n]["value"]
profile_views_yesterday = response[2]["values"][day_n]["value"]
reach_yesterday = response[3]["values"][day_n]["value"]
# 最新日付のフォロワー数のみ別で取得し、昨日のデータとして取り扱う。
follower_today = user_info(
    business_account_id=INSTAGRAM_ACCOUNT_ID,
    token=ACCESS_TOKEN,
    username=username,
    fields=fields,
)["followers_count"]

# 新しい行のデータを辞書形式で定義
yesterday_row = {
    "endtime": [end_time_yesterday],
    "follower_count": [follower_count_yesterday],
    "impressions": [impressions_yesterday],
    "profile_views": [profile_views_yesterday],
    "reach": [reach_yesterday],
    "follower": [follower_today],
}

# 新しいインデックスを取得（既存のデータフレームの長さ）
df_yesterday = pd.DataFrame(yesterday_row)

json_file = "./instagram-insght-vook-dd85f5af7f10.json"
# 出力先スプレッドシートの名前
work_book = "instagram_insight"
# 出力先シートの名前
work_sheet = "raw2"
# (gcpで設定したJsonファイルを指定)
wb = gspread.service_account(filename=json_file)
# ワークブックを選択
sh = wb.open(work_book)
ws_raw2 = sh.worksheet(work_sheet)
# シートの全データを辞書形式で取得
data_yesterday = ws_raw2.get_all_records()
# pandasのデータフレームに変換
df_bfr_yesterday = pd.DataFrame(data_yesterday)
df_last = pd.concat([df_bfr_yesterday, df_yesterday], ignore_index=True)
# # #シート変更範囲の指定
value_chenge_pos1 = "A2:F{}".format(len(df_last) + 1)
# ws_raw2.update(value_chenge_pos1, df_last.to_numpy().tolist())
