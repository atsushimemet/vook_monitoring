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


# """直近30日間のアカウントステータスを取得する"""
# ※30日は遡れる日数の上限
# 今日と指定日さかのぼった日付をyyyy/mm/ddの形式で取得する 標準時に設定
delta_days = 30
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
print(response)

list_endtimes = []
list_impressions = []
list_follower_count = []
list_reach = []
list_profile_views = []

for day_n in range(delta_days):
    list_endtimes.append(response[0]["values"][day_n]["end_time"])
    list_follower_count.append(response[0]["values"][day_n]["value"])
    list_impressions.append(response[1]["values"][day_n]["value"])
    list_profile_views.append(response[2]["values"][day_n]["value"])
    list_reach.append(response[3]["values"][day_n]["value"])

result = dict()
result["endtime"] = list_endtimes
result["follower_count"] = list_follower_count
result["profile_views"] = list_profile_views
result["impressions"] = list_impressions
result["reach"] = list_reach
result["follower"] = ""

# データフレームとして格納
df_account_status_in30days = pd.DataFrame(result)
print(df_account_status_in30days)

# # 時系列で並び替え
# df_account_status_in30days = df_account_status_in30days.sort_values(
#     by="endtime", ascending=False, ignore_index=True
# )

# # 既存で最新のファイルを取得
# path_name = "../data/output"
# file_names = glob.glob(path_name + "/account*")
# file_names_latest_date = sorted(file_names)[-1]
# file_names_latest_date
# df_file_latest = pd.read_csv(file_names_latest_date)

# # この実行で更新したdataframeと既存の最新dataframeを結合して重複排除する
# column_list = [
#     "endtime",
#     "follower_count",
#     "profile_views",
#     "impressions",
#     "reach",
#     "follower",
# ]
# df_account_st_main = pd.concat(
#     [df_file_latest, df_account_status_in30days], ignore_index=True
# )
# df_account_st_main = df_account_st_main.drop_duplicates(subset="endtime")
# df_account_st_main = df_account_st_main.sort_values(by="endtime", ascending=True)
# df_account_st_main = df_account_st_main[column_list]

# # 最新日付のフォロワー数が入っていないのでここで入力
# follower_today = user_info(
#     business_account_id=INSTAGRAM_ACCOUNT_ID,
#     token=ACCESS_TOKEN,
#     username=username,
#     fields=fields,
# )["followers_count"]
# len_df = len(df_account_st_main)
# df_account_st_main.iat[len_df - 1, 5] = follower_today

# # csvに書き出して保存
# today = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")[:8]
# df_account_st_main.to_csv(
#     "../data/output/account_status_vook_" + today + ".csv", index=False
# )
# # df_account_st_main.to_csv('../data/output/account_status_vook_231002x.csv', index=False)
# print("更新ファイルの日付:{}".format(today))

# """google　ドライブ　スプレッドシートへの出力 ~直近30日のアカウントのインサイト~"""

# start_cut = 335  # 元データは9月1日からだが、スプレッドシートに吐き出すのは二ヶ月前の1日からで良いので、start_cut日分はスプレッドシートに送らない
# json_file = "../instaapi/instagram-insght-vook-dd85f5af7f10.json"
# # 出力先スプレッドシートの名前
# work_book = "instagram_insight"
# # 出力先シートの名前
# work_sheet = "raw2"

# # (gcpで設定したJsonファイルを指定)
# wb = gspread.service_account(filename=json_file)
# # ワークブックを選択
# sh = wb.open(work_book)

# # #シート一覧を取得する
# # ws_list = sh.worksheets()

# # シートを指定する
# ws_raw2 = sh.worksheet(work_sheet)

# list_column2 = [
#     "endtime",
#     "follower_count",
#     "impressions",
#     "profile_views",
#     "reach",
#     "follower",
# ]

# # カラムを追加
# ws_raw2.update("A1:F1", [list_column2])
# # output_df1 = pd.DataFrame(df_out[list_column]).fillna(0)
# output_to_spsheet = df_account_st_main[list_column2][start_cut:].fillna(0)

# # シート変更範囲の指定
# value_chenge_pos1 = "A2:F{}".format(len(output_to_spsheet) + 1)

# ws_raw2.update(value_chenge_pos1, output_to_spsheet.to_numpy().tolist())
