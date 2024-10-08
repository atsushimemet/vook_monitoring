import numpy as np
import requests

from constant import metric


def media_insight(media_id, p_basic_info, metric=metric):
    """media IDからインサイトを取得する関数"""
    # リクエスト先のurl作成
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

    response = requests.get(request_url).json()
    err_msg1 = (
        "(#100) Incompatible metrics (impressions, total_interactions) with reel media"
    )
    err_msg2 = "(#100) metric[3] must be one of the following values: impressions, reach, replies, saved, video_views, likes, comments, shares, plays, total_interactions, follows, profile_visits, profile_activity, navigation, ig_reels_video_view_total_time, ig_reels_avg_watch_time, clips_replays_count, ig_reels_aggregated_all_plays_count"
    err_msg3 = "(#100) The Media Insights API does not support the impressions metric for this media product type."
    err_msg4 = "ビジネスアカウントへの変更前に投稿されたメディア"
    if response.get("error") and (
        response["error"]["message"] == err_msg1
        or response["error"]["message"] == err_msg2
        or response["error"]["message"] == err_msg3
        or response["error"]["error_user_title"] == err_msg4
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
    response_reshape["total_interactions"] = response[3]["values"][0]["value"]
    return response_reshape


def create_media_insight_list(list_media_id: list, p_basic_info: dict) -> list:
    """全てのmediaIDでインサイトを取得する"""
    results = []
    for i, nom in enumerate(np.arange(len(list_media_id))):
        print(f"\r{i+1} / {len(list_media_id)}", end="")
        media_id = list_media_id[nom]
        out = media_insight(media_id, p_basic_info)
        results.append(out)
    return results
