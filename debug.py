import requests

from local_config import *

# アクセス情報
business_account_id = INSTAGRAM_ACCOUNT_ID
token = ACCESS_TOKEN
username = USER_NAME
fields = "name,username,biography,follows_count,followers_count,media_count"
media_fields = "timestamp,permalink,media_url,like_count,comments_count,caption"
period = "day"


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
    fields=media_fields,
):
    """メディア情報を取得する"""
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
    response = requests.get(request_url)
    return response.json()["business_discovery"]


def user_media_info(business_account_id, token, username, media_fields):
    """メディア情報を取得する"""
    all_response = []
    result = media_info()
    all_response.append(result["media"]["data"])
    print(result["media"]["paging"]["cursors"].keys())
    import sys

    sys.exit()
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


def main():
    p_basic_info = basic_info()
    user_media_info(business_account_id, token, username, media_fields)


if __name__ == "__main__":
    main()
