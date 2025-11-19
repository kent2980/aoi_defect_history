"""
アプリケーション定数定義モジュール
"""

# リトライ設定
MAX_RETRIES = 3  # 最大リトライ回数
RETRY_DELAY = 1.0  # リトライ間隔（秒）

# タイムアウト設定
CSV_EXPORT_TIMEOUT = 30  # CSVエクスポート処理のタイムアウト（秒）
THREAD_POOL_MAX_WORKERS = 1  # スレッドプールの最大ワーカー数

# 画像処理設定
MAX_IMAGE_WIDTH = 800  # 最大画像幅（ピクセル）
MAX_IMAGE_HEIGHT = 600  # 最大画像高さ（ピクセル）

# データベース設定
DB_NAME = "aoi_data.db"  # SQLiteデータベースファイル名

# UI設定
MIN_WINDOW_WIDTH = 1200  # 最小ウィンドウ幅（ピクセル）
MIN_WINDOW_HEIGHT = 800  # 最小ウィンドウ高さ（ピクセル）

