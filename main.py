import datetime

import gspread
import pandas as pd
import requests

from config import *
from constant import *
from googles.spread_sheet_exporter import SpreadSheetExporter
from local_config import *
from services.insight_service import create_media_insight_list
from services.media_service import (
    create_media_id_list,
    create_media_info_df,
    postprocess,
    user_media_info,
)
from utilities.utils import exclude_isreel_bfrbusinessacct, results_checker


def main2():
    version = "v17.0"
    fields = "name,username,biography,follows_count,followers_count,media_count"
    # 昨日のアカウントステータスを取得する
    delta_days = 1

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

    # ユーザー情報を取得する
    def user_info(
        business_account_id=INSTAGRAM_ACCOUNT_ID,
        token=ACCESS_TOKEN,
        username=USER_NAME,
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

    today = datetime.datetime.today()
    date_delta = datetime.datetime.today() - datetime.timedelta(days=delta_days)
    yyyymmdd_td = "{yyyy}/{mm}/{dd}".format(
        yyyy=today.year, mm=today.month, dd=today.day
    )
    yyyymmdd_delta = "{yyyy}/{mm}/{dd}".format(
        yyyy=date_delta.year, mm=date_delta.month, dd=date_delta.day
    )

    # エンドポイントURLの作成
    metric = ["follower_count", "impressions", "profile_views", "reach"]
    metric_for_url = ""
    for mt in metric:
        metric_for_url += mt + "%2C"
    metric_for_url = metric_for_url.rstrip("%2C")

    params = basic_info()  # リクエストパラメータ
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
    end_time_yesterday = response[0]["values"][0]["end_time"]
    follower_count_yesterday = response[0]["values"][0]["value"]
    impressions_yesterday = response[1]["values"][0]["value"]
    profile_views_yesterday = response[2]["values"][0]["value"]
    reach_yesterday = response[3]["values"][0]["value"]
    # 最新日付のフォロワー数のみ別で取得し、昨日のデータとして取り扱う。
    follower_today = user_info()["followers_count"]

    # 新しい行のデータを辞書形式で定義
    yesterday_row = {
        "endtime": [end_time_yesterday],
        "follower_count": [follower_count_yesterday],
        "impressions": [impressions_yesterday],
        "profile_views": [profile_views_yesterday],
        "reach": [reach_yesterday],
        "follower": [follower_today],
    }
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

    # NOTE:当月末予測をスプレッドシートで描画するために、G列に手動更新列があることに対する暫定対応
    # 必要なキー（列名）を指定
    required_keys = [
        "endtime",
        "follower_count",
        "impressions",
        "profile_views",
        "reach",
        "follower",
    ]
    # 欠損がないレコードのみを抽出
    filtered_data = [
        record
        for record in data_yesterday
        if all(record.get(key) not in (None, "") for key in required_keys)
    ]

    # シート変更範囲の指定
    value_chenge_pos1 = "A{}:F{}".format(len(filtered_data) + 2, len(filtered_data) + 2)
    ws_raw2.update(value_chenge_pos1, df_yesterday.to_numpy().tolist())


def main(event, context):
    result = user_media_info(business_account_id, token, username, media_fields)
    df_media_info = create_media_info_df(result)
    list_media_id = create_media_id_list(result)
    p_basic_info = basic_info()
    results = create_media_insight_list(list_media_id, p_basic_info)
    results = exclude_isreel_bfrbusinessacct(results)
    # results_checker(results)
    df_media_insight = pd.DataFrame(results)
    df_media = postprocess(df_media_info, df_media_insight)
    print(df_media.head())
    print(df_media.shape)
    SpreadSheetExporter(df_media).update()
    main2()


if __name__ == "__main__":
    main(1, 1)
