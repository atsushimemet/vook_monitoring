import sys


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
