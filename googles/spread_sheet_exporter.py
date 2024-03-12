import gspread


class SpreadSheetExporter:
    """googleドライブスプレッドシートへの出力 ~各投稿のインサイト~"""

    def __init__(self, df_media):
        self.json_file = "./instagram-insght-vook-dd85f5af7f10.json"
        # 出力先スプレッドシートの名前
        self.work_book = "instagram_insight"
        # 出力先シートの名前
        self.work_sheet = "raw"
        self.list_column = [
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
        self.df_media = df_media

    def _preprocess(self):
        # (gcpで設定したJsonファイルを指定)
        wb = gspread.service_account(filename=self.json_file)
        # ワークブックを選択
        sh = wb.open(self.work_book)
        self.ws_raw1 = sh.worksheet(self.work_sheet)

    def update(self):
        self._preprocess()
        # カラムを追加
        self.ws_raw1.update("A1:J1", [self.list_column])
        output_to_spsheet = self.df_media[self.list_column].fillna(0)
        # シート変更範囲の指定
        value_chenge_pos1 = "A2:J{}".format(len(output_to_spsheet) + 1)
        self.ws_raw1.update(value_chenge_pos1, output_to_spsheet.to_numpy().tolist())
