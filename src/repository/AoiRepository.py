from pathlib import Path
from aoi_data_manager import (
    FileManager,
    KintoneClient,
    SqlOperations,
)
from PIL.Image import logger
from src.utils import get_config_file_path
import configparser
from src.sub_window.settings_window import PROJECT_DIR
from typing import List
from aoi_data_manager import DefectInfo
import threading
import os
from tkinter import messagebox


class AoiRepository:

    settings_path: Path
    sqlite_dir: Path
    sqlite_ops: SqlOperations | None
    kintone_client: KintoneClient | None
    schedule_directory: Path | None
    file_manager: FileManager
    image_root: Path

    def __init__(
        self,
        settings_path: Path,
        sqlite_dir: Path,
        schedule_directory: Path,
        image_root: Path,
    ):
        self.settings_path = settings_path
        self.sqlite_dir = sqlite_dir
        self.schedule_directory = schedule_directory
        self.image_root = image_root
        self.file_manager = FileManager()
        self.kintone_client = KintoneClient()
        self.sqlite_ops = SqlOperations()

    def read_settings(self) -> None:
        """設定ファイルを読み込み（クラウドファースト構成）"""
        settings_path = get_config_file_path("settings.ini")
        if settings_path.exists():
            # 設定ファイルを読み込み
            config = configparser.ConfigParser()
            config.read(settings_path, encoding="utf-8")
            # config["DIRECTORIES"]が存在する場合
            if "DIRECTORIES" in config:
                # 画像ディレクトリとデータディレクトリを取得
                self.image_directory = config["DIRECTORIES"].get("image_directory", "")
                self.data_directory = config["DIRECTORIES"].get("data_directory", "")
                self.schedule_directory = config["DIRECTORIES"].get(
                    "schedule_directory", ""
                )
                # shared_directoryは非推奨（後方互換性のため読み込むが使用しない）
                self.shared_directory = config["DIRECTORIES"].get(
                    "shared_directory", ""
                )
                if self.shared_directory:
                    # 警告を表示（非推奨）
                    logger.warning(
                        "shared_directoryの設定は非推奨です。"
                        "クラウドファースト構成ではKintone APIを使用します。"
                    )

    def create_sqlite_db(self) -> None:
        """
        SQLiteデータベースを作成（クラウドファースト構成）

        ローカルSQLiteはキャッシュ/オフライン対応としてのみ使用します。
        主要なデータ保存先はKintone APIです。
        """
        self.db_name = "aoi_data.db"
        db_connected = False
        db_type = "キャッシュ"
        self.sqlite_db_dir = PROJECT_DIR

        try:
            # ローカルデータベースの作成（キャッシュ/オフライン対応用）
            self.sqlite_db = SqlOperations(self.sqlite_db_dir, self.db_name)
            self.sqlite_db.create_tables()
            db_connected = True

            # 接続状態をステータスバーに反映
            self.safe_update_sqlite_status(db_connected, db_type)
        except Exception as e:
            logger.error(f"SQLiteデータベース作成エラー: {e}", exc_info=True)
            self.safe_update_sqlite_status(False, db_type)
            # ローカルDBのエラーは警告のみ（Kintone APIが主要なため）
            self.safe_update_status(
                "ローカルキャッシュの作成に失敗しました（Kintone APIは使用可能です）"
            )

    def read_defect_list_db(self) -> None:
        """
        SQLiteデータベースから不良リストを読み込み、defect_listに設定

        クラウドファースト構成では、Kintone APIから優先的に読み込みます。
        オフライン時やKintone APIが利用できない場合のみローカルDBを使用します。
        """
        try:
            # まずKintone APIから読み込みを試行
            if self.is_kintone_connected and self.kintone_client:
                try:
                    # Kintone APIから指図番号でデータを取得
                    # 注意: aoi_data_managerにget_defect_records_by_lotのようなメソッドが必要
                    # 現在は実装されていない可能性があるため、フォールバックとしてローカルDBを使用
                    self.defect_list = self.__read_defect_list_from_kintone()
                    if self.defect_list:
                        self.update_defect_listbox()
                        # ローカルDBにキャッシュとして保存
                        if self.sqlite_db:
                            self.sqlite_db.merge_insert_defect_infos(self.defect_list)
                        return
                except Exception as e:
                    logger.warning(
                        f"Kintone APIからの読み込みに失敗しました（ローカルDBを使用）: {e}",
                        exc_info=True,
                    )

            # フォールバック: ローカルSQLiteデータベースから読み込み
            if self.sqlite_db:
                self.defect_list = self.sqlite_db.get_defect_info_by_lot(
                    self.current_lot_number
                )
                self.update_defect_listbox()
        except Exception as e:
            raise Exception(e)

    def insert_defect_info_to_db_async(self, defect_info: List[DefectInfo]) -> None:
        """不良情報を非同期でSQLiteデータベースに挿入"""

        def _task():
            """非同期挿入タスク"""
            if self.sqlite_db:
                try:
                    self.sqlite_db.merge_insert_defect_infos(defect_info)
                except Exception as e:
                    logger.error(f"データベースマージ挿入エラー: {e}", exc_info=True)

        thread = threading.Thread(target=_task, daemon=True)
        thread.start()

    def remove_defect_info_from_db_async(self, defect_info: DefectInfo) -> None:
        """不良情報を非同期でSQLiteデータベースから削除"""

        def _task() -> None:
            if self.sqlite_db:
                try:
                    self.sqlite_db.delete_defect_info(defect_info.id)
                except Exception as e:
                    logger.error(f"データベース削除エラー: {e}", exc_info=True)

        thread = threading.Thread(target=_task, daemon=True)
        thread.start()

    def init_kintone_client(self) -> None:
        """キントーンクライアントの初期化（環境変数から読み込み）"""
        # 環境変数からKintone設定を取得
        kintone_subdomain = os.getenv("KINTONE_SUBDOMAIN")
        kintone_app_id = os.getenv("KINTONE_APP_ID")
        kintone_api_token = os.getenv("KINTONE_API_TOKEN")

        # 環境変数が設定されていない場合は、フォールバックとして設定ファイルを試行
        if not all([kintone_subdomain, kintone_app_id, kintone_api_token]):
            try:
                kintone_settings_path = get_config_file_path("kintone_settings.ini")
                if kintone_settings_path.exists():
                    kintone_settings = FileManager.load_kintone_settings_file(
                        kintone_settings_path.as_posix()
                    )
                    kintone_subdomain = kintone_subdomain or kintone_settings.get(
                        "subdomain"
                    )
                    kintone_app_id = kintone_app_id or kintone_settings.get("app_id")
                    kintone_api_token = kintone_api_token or kintone_settings.get(
                        "api_token"
                    )
            except Exception as e:
                logger.warning(
                    f"設定ファイルの読み込みに失敗しました: {e}", exc_info=True
                )

        if not all([kintone_subdomain, kintone_app_id, kintone_api_token]):
            # 設定が不完全な場合は、接続不可状態として初期化
            self.kintone_client = None
            self.is_kintone_connected = False
            return

        try:
            kintone_app_id = int(kintone_app_id)
        except ValueError:
            # アラート
            messagebox.showerror("エラー", "KintoneアプリIDが数値ではありません。")
            return

        self.kintone_client = KintoneClient(
            subdomain=kintone_subdomain,
            app_id=kintone_app_id,
            api_token=kintone_api_token,
        )
