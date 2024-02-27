# https://vook-tokyo.slack.com/archives/C04P4S8NCJZ/p1708148174852639?thread_ts=1708148163.348379&cid=C04P4S8NCJZ

import gspread
import numpy as np
import pandas as pd
import requests

from local_config import *


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


params = basic_info()

"""各投稿のinformation(基本的な情報)を取得"""
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


# print(user_info(business_account_id,token,username,fields))


# メディア情報を取得する
def user_media_info(business_account_id, token, username, media_fields):
    all_response = []

    request_url = (
        "https://graph.facebook.com/"
        + version
        + "/{business_account_id}?fields=business_discovery.username({username}){{media{{{media_fields}}}}}&access_token={token}".format(
            business_account_id=business_account_id,
            username=username,
            media_fields=media_fields,
            token=token,
        )
    )
    #     print(request_url)
    response = requests.get(request_url)
    result = response.json()["business_discovery"]

    all_response.append(result["media"]["data"])

    # 過去分がある場合は過去分全て取得する(1度に取得できる件数は25件)
    if "after" in result["media"]["paging"]["cursors"].keys():
        next_token = result["media"]["paging"]["cursors"]["after"]
        while next_token is not None:
            request_url = (
                "https://graph.facebook.com/"
                + version
                + "/{business_account_id}?fields=business_discovery.username({username}){{media.after({next_token}){{{media_fields}}}}}&access_token={token}".format(
                    business_account_id=business_account_id,
                    username=username,
                    media_fields=media_fields,
                    token=token,
                    next_token=next_token,
                )
            )
            #             print(request_url)
            response = requests.get(request_url)
            result = response.json()["business_discovery"]
            all_response.append(result["media"]["data"])
            if "after" in result["media"]["paging"]["cursors"].keys():
                next_token = result["media"]["paging"]["cursors"]["after"]
            else:
                next_token = None

    return all_response


result = user_media_info(business_account_id, token, username, media_fields)

"""結果をデータフレームに格納"""
df_media_info = pd.DataFrame(result[0])
for noc in np.arange(1, len(result)):
    output_per_call = pd.DataFrame(result[noc])
    df_media_info = pd.concat([df_media_info, output_per_call], ignore_index=True)


"""ここで全投稿のmedia idのリストも作っておく"""
list_media_id = []
for noc in np.arange(len(result)):
    for nop in np.arange(len(result[noc])):
        media_id = result[noc][nop]["id"]
        list_media_id.append(media_id)
# print('最初の10個だけ表示：',list_media_id[:10])
# print('全投稿数：',len(list_media_id))

"""投稿ごとのさらに詳細なinsight(reach, saved, impressions, enagegement)を取得する
    ※これは各投稿IDごとにAPIコールが必要なため、処理に少し時間がかかる。改善方法を検討中"""

"""
***********************************************************************************
【APIエンドポイント】
https://graph.facebook.com/{graph-api-version}/{ig-media-id}/insights?metric={metric}
***********************************************************************************
"""


# media IDからインサイトを取得する関数
def media_insight(media_id):
    """リクエスト先のurl作成"""
    metric_for_url = ""
    for mt in metric:
        metric_for_url += mt + "%2C"
    metric_for_url = metric_for_url.rstrip("%2C")
    request_url = (
        params["endpoint_base"]
        + media_id
        + "/insights?access_token="
        + params["access_token"]
        + "&metric="
        + metric_for_url
    )

    response = requests.get(request_url).json()["data"]
    response_reshape = dict()
    response_reshape["id"] = media_id
    response_reshape["reach"] = response[0]["values"][0]["value"]
    response_reshape["impressions"] = response[1]["values"][0]["value"]
    response_reshape["saved"] = response[2]["values"][0]["value"]
    response_reshape["engagement"] = response[3]["values"][0]["value"]

    return response_reshape


metric = ["reach", "impressions", "saved", "engagement"]

"""本来は以下のコードだが、一部インスタ側エラーでインサイトを取得できないのでworkaround的に対応する"""
# 全てのmediaIDでインサイトを取得する
# results = []
# for nom in np.arange(len(list_media_id)):
#     media_id = list_media_id[nom]
#     out = media_insight(media_id)
#     results.append(out)


# 全てのmediaIDでインサイトを取得する※workaround対応ver
results = []
# poloの2/19以前の16投稿はきる
num_allposts = len(list_media_id)
date_cut = 16
for nom in np.arange(num_allposts - date_cut):
    media_id = list_media_id[nom]
    out = media_insight(media_id)
    results.append(out)

df_media_insight = pd.DataFrame(results)

"""結合してカラムの順番整理"""

df_media = pd.merge(df_media_info, df_media_insight, how="inner", on="id")
df_media = df_media.reindex(
    columns=[
        "id",
        "timestamp",
        "permalink",
        "media_url",
        "like_count",
        "saved",
        "reach",
        "impressions",
        "engagement",
        "caption",
    ]
)


"""google　ドライブ　スプレッドシートへの出力 ~各投稿のインサイト~"""

json_file = "../instaapi/instagram-insght-vook-dd85f5af7f10.json"
# 出力先スプレッドシートの名前
work_book = "instagram_insight"
# 出力先シートの名前
work_sheet = "raw"

# (gcpで設定したJsonファイルを指定)
wb = gspread.service_account(filename=json_file)
# ワークブックを選択
sh = wb.open(work_book)
# #シート一覧を取得する
# ws_list = sh.worksheets()
# シートを指定する
ws_raw1 = sh.worksheet(work_sheet)

list_column = [
    "id",
    "timestamp",
    "permalink",
    "media_url",
    "like_count",
    "saved",
    "reach",
    "impressions",
    "engagement",
    "caption",
]
# カラムを追加
ws_raw1.update("A1:J1", [list_column])
# output_df1 = pd.DataFrame(df_out[list_column]).fillna(0)
output_to_spsheet = df_media[list_column].fillna(0)

# シート変更範囲の指定
value_chenge_pos1 = "A2:J{}".format(len(output_to_spsheet) + 1)

ws_raw1.update(value_chenge_pos1, output_to_spsheet.to_numpy().tolist())
