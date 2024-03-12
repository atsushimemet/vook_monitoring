import numpy as np
import pandas as pd
import requests

from config import ACCESS_TOKEN, INSTAGRAM_ACCOUNT_ID, username, version
from constant import media_fields


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
