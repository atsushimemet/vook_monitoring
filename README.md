# このプロジェクトについて
このプロジェクトは、Instagramの [vook.vintagebook](https://www.instagram.com/vook.vintagebook/)アカウントからメディア情報とインサイトデータを取得し、分析するためのPythonスクリプトです。このツールは隔週のモニタリングアジェンダに利用されています。プロジェクトを使用することで、Instagramの投稿に関する詳細なデータ分析が可能になります。Googleスプレッドシートへの出力機能も含まれており、取得したデータを直接スプレッドシートに記録できます。

## ディレクトリ構成
```
.
├── config.py # 設定情報を保持するファイル
├── constant.py # 定数を定義するファイル
├── debug.py # デバッグ用スクリプト
├── googles
│ └── spread_sheet_exporter.py # スプレッドシートへの出力機能を提供するモジュール
├── local_config.py # ローカル環境専用の設定情報を保持するファイル
├── main.py.bak # バックアップ用のメインスクリプト
├── mypy.ini # mypy設定ファイル
├── requirements.txt # 依存関係を記録するファイル
├── services
│ ├── insight_service.py # インサイトデータ取得機能を提供するモジュール
│ └── media_service.py # メディア情報取得機能を提供するモジュール
├── setup.sh # 環境設定用スクリプト
├── tmp.txt # 一時ファイル
└── utilities
└── utils.py # 汎用的なユーティリティ関数を提供するモジュール
```
## インストール手順
1. このリポジトリをクローンまたはダウンロードします。
2. venvなどで仮想環境を作成します。
3. 必要なPythonパッケージをインストールします。以下のコマンドを実行してください:
    ```
    pip install -r requirements.txt
    ```
4. `config.py` と `constant.py` ファイルを編集し、必要な設定を行ってください。
## 使用方法
1. `main.py` スクリプトを実行します。これにより、設定に基づいてInstagramからメディア情報とインサイトデータが取得されます。

    ```
    python main.py
    ```
2. スクリプトが実行されると、標準出力にメディアの基本情報とインサイトデータが表示されます。
3. スプレッドシートへの出力を行いたい場合は、`googles/spread_sheet_exporter.py` 内の `SpreadSheetExporter` クラスを使用してください。この機能を使用するには、Google Cloud Platformでサービスアカウントを作成し、ダウンロードしたJSONキーファイルのパスを指定する必要があります。
## 注意事項
- このプロジェクトは、Instagramの公式APIを使用しています。APIの利用制限に注意してください。
- スプレッドシートへの出力機能を使用するには、Google Cloud Platformでの設定が必要です。
