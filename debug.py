import sys

import pandas as pd

from config import *
from constant import *
from services.insight_service import create_media_insight_list
from services.media_service import (
    create_media_id_list,
    create_media_info_df,
    postprocess,
    user_media_info,
)


def exclude_isreel_bfrbusinessacct(results: list) -> list:
    s = "isReel or bfrBusinessAcct"
    return [x for x in results if x != s]


def results_checker(results: list) -> None:
    """resultsの中身が変じゃないかtmp.txtでチェック"""
    original_stdout = sys.stdout  # 標準出力を保持
    with open("tmp.txt", "w") as f:
        sys.stdout = f  # 標準出力をファイルにリダイレクト
        print(results)
    # 標準出力を元に戻す
    sys.stdout = original_stdout


def main():
    result = user_media_info(business_account_id, token, username, media_fields)
    df_media_info = create_media_info_df(result)
    list_media_id = create_media_id_list(result)
    p_basic_info = basic_info()
    results = create_media_insight_list(list_media_id, p_basic_info)
    results = exclude_isreel_bfrbusinessacct(results)
    results_checker(results)
    df_media_insight = pd.DataFrame(results)
    df_media = postprocess(df_media_info, df_media_insight)
    print(df_media.head())
    print(df_media.shape)
    # SpreadSheetExporter(df_media).update()


if __name__ == "__main__":
    main()
