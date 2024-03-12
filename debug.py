import sys

import gspread
import numpy as np
import pandas as pd
import requests

from local_config import *

# アクセス情報
business_account_id = INSTAGRAM_ACCOUNT_ID
token = ACCESS_TOKEN
username = USER_NAME
fields = "name,username,biography,follows_count,followers_count,media_count"
media_fields = "timestamp,permalink,media_url,like_count,comments_count,caption"
period = "day"
metric = ["reach", "impressions", "saved", "engagement"]


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


def media_info(
    business_account_id=INSTAGRAM_ACCOUNT_ID,
    token=ACCESS_TOKEN,
    username=username,
    media_fields=media_fields,
    next_token=None,
):
    """メディア情報を取得する"""
    if next_token:
        base_url = "/{business_account_id}?fields=business_discovery.username({username}){{media.after({next_token}){{{media_fields}}}}}&access_token={token}"
    else:
        base_url = "/{business_account_id}?fields=business_discovery.username({username}){{media{{{media_fields}}}}}&access_token={token}"
    request_url = (
        "https://graph.facebook.com/"
        + version
        + base_url.format(
            business_account_id=business_account_id,
            username=username,
            media_fields=media_fields,
            token=token,
            next_token=next_token,
        )
    )
    response = requests.get(request_url)
    return response.json()["business_discovery"]


def user_media_info(business_account_id, token, username, media_fields):
    """メディア情報を取得する"""
    all_response = []
    result = media_info()
    all_response.append(result["media"]["data"])
    # 過去分がある場合は過去分全て取得する(1度に取得できる件数は25件)
    if "after" in result["media"]["paging"]["cursors"].keys():
        next_token = result["media"]["paging"]["cursors"]["after"]
        while next_token is not None:
            result = media_info(next_token=next_token)
            all_response.append(result["media"]["data"])
            if "after" in result["media"]["paging"]["cursors"].keys():
                next_token = result["media"]["paging"]["cursors"]["after"]
            else:
                next_token = None
    return all_response


def create_media_info_df(result: dict) -> pd.DataFrame:
    """結果をデータフレームに格納"""
    df_media_info = pd.DataFrame(result[0])
    for noc in np.arange(1, len(result)):
        output_per_call = pd.DataFrame(result[noc])
        df_media_info = pd.concat([df_media_info, output_per_call], ignore_index=True)
    return df_media_info


def create_media_id_list(result: dict) -> list:
    """ここで全投稿のmedia idのリストも作っておく"""
    list_media_id = []
    for noc in np.arange(len(result)):
        for nop in np.arange(len(result[noc])):
            media_id = result[noc][nop]["id"]
            list_media_id.append(media_id)
    return list_media_id


# media IDからインサイトを取得する関数
def media_insight(media_id, p_basic_info, metric=metric):
    """リクエスト先のurl作成"""
    metric_for_url = ""
    for mt in metric:
        metric_for_url += mt + "%2C"
    metric_for_url = metric_for_url.rstrip("%2C")
    request_url = (
        p_basic_info["endpoint_base"]
        + media_id
        + "/insights?access_token="
        + p_basic_info["access_token"]
        + "&metric="
        + metric_for_url
    )

    # response = requests.get(request_url).json()["data"]
    response = requests.get(request_url).json()
    err_msg1 = "(#100) Incompatible metrics (impressions, engagement) with reel media"
    err_msg2 = "ビジネスアカウントへの変更前に投稿されたメディア"
    if response.get("error") and (
        response["error"]["message"] == err_msg1
        or response["error"]["error_user_title"] == err_msg2
    ):
        return "isReel or bfrBusinessAcct"
    # try:
    response = response["data"]
    # except KeyError as e:
    #     print(e)
    #     print(response)
    response_reshape = dict()
    response_reshape["id"] = media_id
    response_reshape["reach"] = response[0]["values"][0]["value"]
    response_reshape["impressions"] = response[1]["values"][0]["value"]
    response_reshape["saved"] = response[2]["values"][0]["value"]
    response_reshape["engagement"] = response[3]["values"][0]["value"]
    return response_reshape


def postprocess(
    df_media_info: pd.DataFrame, df_media_insight: pd.DataFrame
) -> pd.DataFrame:
    """結合してカラムの順番整理"""
    df_media = pd.merge(df_media_info, df_media_insight, how="inner", on="id")
    return df_media.reindex(
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


def main():
    result = user_media_info(business_account_id, token, username, media_fields)
    df_media_info = create_media_info_df(result)
    list_media_id = create_media_id_list(result)
    p_basic_info = basic_info()
    # 全てのmediaIDでインサイトを取得する
    results = []
    for i, nom in enumerate(np.arange(len(list_media_id))):
        print(f"\r{i+1} / {len(list_media_id)}", end="")
        media_id = list_media_id[nom]
        out = media_insight(media_id, p_basic_info)
        results.append(out)
        break
    # print(result[0][0])
    # print(len(result[0]))
    df_media_insight = pd.DataFrame(results)
    print(df_media_insight.shape)
    print(df_media_insight.head())
    """結合してカラムの順番整理"""
    df_media = postprocess(df_media_info, df_media_insight)


if __name__ == "__main__":
    main()
