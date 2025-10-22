import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
import os
from datetime import datetime, timezone
from pathlib import Path
import configparser
import pandas as pd
from pandas import DataFrame
import re
from typing import List
import threading
import shutil
from concurrent.futures import ThreadPoolExecutor
import time

from aoi_data_manager import (
    FileManager,
    KintoneClient,
    DefectInfo,
    RepairdInfo,
    SqlOperations,
)
from .sub_window import SettingsWindow, KintoneSettings
from .dialog import LotChangeDialog, ChangeUserDialog, ItemCodeChangeDialog
from .utils import get_project_dir, get_csv_file_path, get_config_file_path
from pathlib import Path
from ktec_smt_schedule import SMTSchedule

PROJECT_DIR = get_project_dir()


class AOIView(tk.Toplevel):
    """AOI製品経歴書ウィンドウ"""

    def __init__(self, fillColor="white", master=None):
        """
        コンストラクタ

        ### Args:
        - fillColor (str): 塗りつぶし色
        - master (tk.Tk): 親ウィンドウ
        """
        super().__init__(master)

        # ウィンドウ設定
        self.title("AOI 製品経歴書")  # タイトル設定
        self.option_add("*Background", "white")  # 背景色を白に設定
        self.option_add("*Entry.Background", "white")  # Entryの背景色を白に設定
        self.option_add("*Label.Background", "white")  # Labelの背景色を白に設定
        self.state("zoomed")  # ウィンドウを最大化
        self.configure(bg="white")  # 背景色を白に設定

        # ウィンドウの最小サイズを設定
        self.minsize(1200, 800)  # 最小幅1200px、最小高さ800px

        # 閉じるボタン押下時の処理を設定
        self.protocol("WM_DELETE_WINDOW", self.__before_close)

        # ウィンドウリサイズイベントをバインド
        self.bind("<Configure>", self.on_window_resize)

        # 座標の塗りつぶし色
        self.fillColor = fillColor

        # 画像の実際のサイズを保持
        self.original_image_size = None  # (width, height)
        self.displayed_image_size = None  # (width, height)
        self.image_offset = None  # (x_offset, y_offset)

        # ディレクトリ設定
        self.image_directory = None  # 画像ディレクトリ
        self.data_directory = None  # データディレクトリ
        self.schedule_directory = None  # 計画書ディレクトリ
        self.shared_directory = None  # 共有ディレクトリ

        # Kintone関連
        self.kintone_client: KintoneClient = None  # Kintoneクライアント
        self.is_kintone_connected: bool = False

        # SMTスケジュール関連
        self.schedule_df: DataFrame = None
        self.is_read_schedule: bool = False

        # UI要素の宣言
        self.serial_entry = None
        self.model_label_value = None
        self.board_label_value = None
        self.side_label_value = None
        self.lot_label_value = None
        self.line_label_value = None
        self.aoi_user_label_value = None
        self.repair_user_label_value = None
        self.inspect_user_label_value = None
        self.info_frame = None
        self.defect_info_frame = None
        self.no_value = None
        self.rf_entry = None
        self.defect_entry = None
        self.board_no_label = None
        self.widgets_frame = None
        self.canvas = None
        self.defect_list_frame = None
        self.defect_listbox = None
        self.status_frame = None
        self.status_label = None
        self.status_right_frame = None
        self.smt_status_label = None
        self.connection_label = None
        self.photo_image = None

        # 画像とプロジェクト関連
        self.current_coordinates = None
        self.current_line_name: str = None
        self.current_item_code: str = None
        self.current_lot_number: str = None
        self.current_image_path: str = None
        self.current_image_filename: str = None
        self.user_name: str = None

        # データリスト
        self.defect_list: List[DefectInfo] = []
        self.repaird_list: List[RepairdInfo] = []

        # 基板番号
        self.current_board_index = 1
        self.total_boards = 1

        # 内部制御変数
        self._update_scheduled = None

        # 設定読み込み
        self.__read_settings()

        # sqlite3データベース
        self.db_name = None
        self.sqlite_db = None
        self.shared_sqlite_db = None
        self.sqlite_db_path = None
        self.shared_db_path = None
        self.__create_sqlite_db()

        # UIの作成
        self.create_ui()

    def create_ui(self):
        """UI要素を作成する"""
        # Kintoneクライアントの初期化
        self.init_kintone_client()

        # キントーン接続確認（非同期）
        self.kintone_connected_async()

        # UI描画
        self.create_menu()
        self.create_header()
        self.create_defect_info_area()
        self.create_widgets_area()
        self.create_canvas_widgets()
        self.create_defect_list_widgets()
        self.create_status_bar()

        # SMTスケジュール非同期読み込み開始（ステータスバー作成後）
        self.__read_smt_schedule_async()

        # 基板ラベルの初期化
        self.update_board_label()

        # ユーザー切り替え
        self.change_user()

    def __before_close(self):
        """閉じる前の処理"""
        if len(self.defect_list) > 0:
            try:
                self.post_kintone_record_async(self.defect_list)
            except ValueError as e:
                print(e)
                messagebox.showerror("送信エラー", f"API送信エラー:{e}")
            # データベースにアイテムを追加
            self.__insert_defect_info_to_db(self.defect_list)
            # SQLiteデータベースを閉じる
            self.sqlite_db.close()
            # 差分を共有データベースにマージ
            SqlOperations.merge_target_database(
                self.data_directory, self.shared_directory, self.db_name
            )
        self.destroy()

    def __read_settings(self):
        """ """
        settings_path = get_config_file_path("settings.ini")
        if settings_path.exists():
            # 設定ファイルを読み込み
            config = configparser.ConfigParser()
            config.read(settings_path, encoding="utf-8")
            # 例: 画像ディレクトリとデータディレクトリを取得
            self.image_directory = config["DIRECTORIES"].get("image_directory", "")
            self.data_directory = config["DIRECTORIES"].get("data_directory", "")
            self.schedule_directory = config["DIRECTORIES"].get(
                "schedule_directory", ""
            )
            self.shared_directory = config["DIRECTORIES"].get("shared_directory", "")

    def __read_smt_schedule_async(self):
        """SMTスケジュールを非同期で読み込み"""

        def _read_schedule():
            """SMTスケジュールを読み込む"""
            try:
                # ステータスバーの更新
                self.after(0, lambda: self.update_smt_status("読み込み中...", "orange"))
                self.after(
                    0, lambda: self.update_status("SMTスケジュールを読み込み中...")
                )
                # スケジュール情報の取得
                if self.schedule_directory:
                    # スケジュール情報のDataFrame取得
                    self.schedule_df = SMTSchedule.get_lot_infos(
                        self.schedule_directory, 1, 9
                    )
                    # スケジュール情報の読み込み完了
                    self.is_read_schedule = True
                    # スケジュール情報のCSVパスを取得
                    output_path = PROJECT_DIR / "smt_schedule.csv"
                    # CSVファイルに出力
                    self.schedule_df.to_csv(
                        output_path, index=False, encoding="utf-8-sig"
                    )

                    # 成功時のステータスバー更新
                    self.after(
                        0, lambda: self.update_smt_status("読み込み完了", "green")
                    )
                    self.after(
                        0,
                        lambda: self.update_status(
                            "SMTスケジュールの読み込みが完了しました"
                        ),
                    )
                else:
                    # ディレクトリ未設定時
                    self.after(0, lambda: self.update_smt_status("未設定", "gray"))
                    self.after(
                        0,
                        lambda: self.update_status(
                            "スケジュールディレクトリが設定されていません"
                        ),
                    )
                    print("スケジュールディレクトリが設定されていません。")
            except Exception as e:
                # エラー時の処理
                error_msg = f"SMTスケジュール読み込みエラー: {e}"
                self.after(0, lambda: self.update_smt_status("エラー", "red"))
                self.after(0, lambda: self.safe_update_status(error_msg))
                print(error_msg)

        # バックグラウンドスレッドで実行
        thread = threading.Thread(target=_read_schedule, daemon=True)
        thread.start()

    def __create_sqlite_db(self):
        """SQLiteデータベースを作成"""
        self.db_name = "aoi_data.db"
        if self.shared_directory:
            self.shared_db_path = os.path.join(self.shared_directory, self.db_name)
            if os.path.exists(self.shared_db_path):
                # 共有データをローカルにコピー
                shutil.copy(self.shared_db_path, self.data_directory)
            else:
                # 新しいデータベースを共有ディレクトリに作成
                self.shared_sqlite_db = SqlOperations(self.shared_directory, db_name)
                self.shared_sqlite_db.create_tables()
        if self.data_directory:
            self.sqlite_db_path = os.path.join(self.data_directory, self.db_name)
            self.sqlite_db = SqlOperations(self.data_directory, self.db_name)
            self.sqlite_db.create_tables()

    def __insert_defect_info_to_db(self, defect_info: List[DefectInfo]):
        """不良情報をSQLiteデータベースに挿入"""
        if self.sqlite_db:
            try:
                self.sqlite_db.merge_insert_defect_infos(defect_info)
            except Exception as e:
                print(f"データベースマージ挿入エラー: {e}")

    def __remove_defect_info_from_db(self, defect_info: DefectInfo):
        """不良情報をSQLiteデータベースから削除"""
        if self.sqlite_db:
            try:
                self.sqlite_db.delete_defect_info(defect_info.id)
            except Exception as e:
                print(f"データベース削除エラー: {e}")

    def init_kintone_client(self):
        """キントーンクライアントの初期化"""
        kintone_settings_path = get_config_file_path("kintone_settings.ini")
        kintone_settings = FileManager.load_kintone_settings_file(
            kintone_settings_path.as_posix()
        )
        self.kintone_client = KintoneClient(
            subdomain=kintone_settings.get("subdomain"),
            app_id=kintone_settings.get("app_id"),
            api_token=kintone_settings.get("api_token"),
        )

    def kintone_connected_async(self) -> bool:
        """キントーン接続を非同期で確認"""

        def _check_connection():
            try:
                connected = self.kintone_client.is_connected()
                self.is_kintone_connected = connected
                status_msg = "キントーン接続済み" if connected else "キントーン未接続"
                self.after(0, lambda: self.update_connection_status(connected))
                self.after(0, lambda: self.safe_update_status(status_msg))
            except Exception as e:
                error_msg = f"キントーン接続エラー: {e}"
                self.after(0, lambda: self.update_connection_status(False))
                self.after(0, lambda: self.safe_update_status(error_msg))
                print(error_msg)

        # バックグラウンドスレッドで実行
        thread = threading.Thread(target=_check_connection, daemon=True)
        thread.start()

    def create_menu(self):
        """メニューの作成"""

        # メニューバーの作成
        menubar = tk.Menu(self)

        # ファイルメニュー
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="画像を開く", command=self.open_image)
        menubar.add_cascade(label="ファイル", menu=file_menu)
        # 設定メニュー
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="設定", command=self.open_settings)
        menubar.add_cascade(label="設定", menu=settings_menu)
        # キントーン設定メニュー
        kintoneMenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="キントーン設定", menu=kintoneMenu)
        kintoneMenu.add_command(label="API設定", command=self.open_kintone_settings)
        # ヘルプメニュー
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="不良名一覧", command=self.show_defect_mapping)
        menubar.add_cascade(label="ヘルプ", menu=help_menu)

        # メニューバーをウィンドウに設定
        self.config(menu=menubar)

    def create_header(self):
        # ヘッダーフレーム - 固定高さで上部に配置
        header_frame = tk.Frame(self, height=80)  # 高さを80pxに調整
        header_frame.pack(fill=tk.X, pady=5)  # 上下パディングを削減
        header_frame.pack_propagate(False)  # 高さ固定

        # フォント（Yu Gothic UI, Meiryo, Segoe UI）
        font_title = ("Yu Gothic UI", 16, "bold")
        font_label = ("Yu Gothic UI", 10)
        font_value = ("Yu Gothic UI", 10)

        # タイトルラベル
        title_label = tk.Label(
            header_frame,
            text="AOI 製品経歴書",
            font=font_title,
            relief="solid",
            borderwidth=1,
        )
        title_label.pack(side=tk.LEFT, padx=10, pady=10, ipadx=15)

        # シリアルエントリ
        serial_label = tk.Label(header_frame, text="シリアルNo:", font=font_label)
        serial_label.pack(side=tk.LEFT, padx=10)
        self.serial_entry = tk.Entry(header_frame, font=font_value)
        self.serial_entry.pack(side=tk.LEFT, padx=10)

        # right_frame
        right_frame = tk.Frame(header_frame)
        right_frame.pack(side=tk.RIGHT, padx=20)

        # インフォフレーム
        info_frame = tk.Frame(right_frame)
        info_frame.pack(fill=tk.X, padx=10)

        # 下線のみ追加
        underline = tk.Frame(info_frame, bg="black", height=1)
        underline.pack(fill=tk.X, side=tk.BOTTOM)

        # ロット切り替えボタン
        lot_change_button = tk.Button(
            info_frame,
            text="指図切替",
            font=("Yu Gothic UI", 8),
            command=self.change_lot,
        )
        lot_change_button.pack(side=tk.LEFT, padx=5, pady=[0, 2])

        # 機種名
        model_label = tk.Label(info_frame, text="機種名: ", font=font_label)
        model_label.pack(side=tk.LEFT, padx=10)
        self.model_label_value = tk.Label(
            info_frame, width=30, font=font_value, anchor="w"
        )
        self.model_label_value.pack(side=tk.LEFT)

        # 基板名
        board_label = tk.Label(info_frame, text="基板名: ", font=font_label)
        board_label.pack(side=tk.LEFT, padx=10)
        self.board_label_value = tk.Label(
            info_frame, width=15, font=font_value, anchor="w"
        )
        self.board_label_value.pack(side=tk.LEFT)

        # 面
        side_label = tk.Label(info_frame, text="面: ", font=font_label)
        side_label.pack(side=tk.LEFT, padx=10)
        self.side_label_value = tk.Label(
            info_frame, width=5, font=font_value, anchor="w"
        )
        self.side_label_value.pack(side=tk.LEFT)

        # 指図
        lot_label = tk.Label(info_frame, text="指図: ", font=font_label)
        lot_label.pack(side=tk.LEFT, padx=10)
        self.lot_label_value = tk.Label(
            info_frame, width=12, font=font_value, anchor="w"
        )
        self.lot_label_value.pack(side=tk.LEFT)

        # ユーザーフレーム
        user_frame = tk.Frame(right_frame)
        user_frame.pack(fill=tk.X, padx=10)

        # 下線のみ追加
        underline_user = tk.Frame(user_frame, bg="black", height=1)
        underline_user.pack(fill=tk.X, side=tk.BOTTOM)

        # ユーザー切り替えボタン
        user_change_button = tk.Button(
            user_frame,
            text="ユーザー切替",
            font=("Yu Gothic UI", 8),
            command=self.change_user,
        )
        user_change_button.pack(side=tk.LEFT, padx=5, pady=[0, 2])

        # 生産ライン
        line_label = tk.Label(user_frame, text="生産ライン: ", font=font_label)
        line_label.pack(side=tk.LEFT, padx=10)
        self.line_label_value = tk.Entry(
            user_frame, font=font_value, width=10, justify="center"
        )
        self.line_label_value.pack(side=tk.LEFT)

        # AOI担当
        aoi_user_label = tk.Label(user_frame, text="AOI担当: ", font=font_label)
        aoi_user_label.pack(side=tk.LEFT, padx=10)
        self.aoi_user_label_value = tk.Label(
            user_frame, font=font_value, anchor="w", width=10
        )
        self.aoi_user_label_value.pack(side=tk.LEFT)

        # 修理担当
        repair_user_label = tk.Label(user_frame, text="修理担当: ", font=font_label)
        repair_user_label.pack(side=tk.LEFT, padx=10)
        self.repair_user_label_value = tk.Label(
            user_frame, font=font_value, anchor="w", width=10
        )
        self.repair_user_label_value.pack(side=tk.LEFT)

        # 目視担当
        inspect_user_label = tk.Label(user_frame, text="目視担当: ", font=font_label)
        inspect_user_label.pack(side=tk.LEFT, padx=10)
        self.inspect_user_label_value = tk.Label(
            user_frame, font=font_value, anchor="w", width=10
        )
        self.inspect_user_label_value.pack(side=tk.LEFT)

    def create_defect_info_area(self):

        self.info_frame = tk.Frame(self)
        # 固定高さで配置
        self.info_frame.pack(fill=tk.X, padx=10, pady=(5, 10))

        # 不良情報入力フレーム
        self.defect_info_frame = tk.LabelFrame(
            self.info_frame, text="不良情報入力", font=("Yu Gothic UI", 10)
        )
        self.defect_info_frame.pack(side=tk.LEFT, padx=40)

        # 番号
        no_label = tk.Label(
            self.defect_info_frame, text="No: ", font=("Yu Gothic UI", 12)
        )
        no_label.pack(side=tk.LEFT, padx=10)
        self.no_value = tk.Label(
            self.defect_info_frame, text="1", font=("Yu Gothic UI", 12), width=4
        )
        self.no_value.pack(side=tk.LEFT, padx=10)

        # リファレンス
        rf_label = tk.Label(
            self.defect_info_frame, text="リファレンス: ", font=("Yu Gothic UI", 12)
        )
        rf_label.pack(side=tk.LEFT, padx=10)
        self.rf_entry = tk.Entry(self.defect_info_frame, font=("Yu Gothic UI", 12))
        self.rf_entry.pack(side=tk.LEFT, padx=10)

        # 不良項目
        defect_label = tk.Label(
            self.defect_info_frame, text="不良項目: ", font=("Yu Gothic UI", 12)
        )
        defect_label.pack(side=tk.LEFT, padx=10)
        self.defect_entry = tk.Entry(self.defect_info_frame, font=("Yu Gothic UI", 12))
        self.defect_entry.pack(side=tk.LEFT, padx=10)
        self.defect_entry.bind("<Return>", lambda event: self.convert_defect_name())

        # 保存ボタン
        save_button = tk.Button(
            self.defect_info_frame,
            text="保存",
            font=("Yu Gothic UI", 10),
            command=self.save_defect_info,
        )
        save_button.pack(side=tk.LEFT, padx=20, pady=5)

        # 削除ボタン
        delete_button = tk.Button(
            self.defect_info_frame,
            text="削除",
            font=("Yu Gothic UI", 10),
            command=self.delete_defect_info,
        )
        delete_button.pack(side=tk.LEFT, padx=10, pady=5)

        # 基板操作フレーム
        board_control_frame = tk.LabelFrame(
            self.info_frame, text="基板切替", font=("Yu Gothic UI", 10)
        )
        board_control_frame.pack(side=tk.RIGHT, padx=[0, 50])

        # 基板Noラベル
        self.board_no_label = tk.Label(
            board_control_frame, text="1 / 1 枚", font=("Yu Gothic UI", 12)
        )
        self.board_no_label.pack(side=tk.LEFT, padx=[5, 5])
        # 前の基板ボタン
        prev_board_button = tk.Button(
            board_control_frame,
            text="<< 前へ",
            font=("Yu Gothic UI", 10),
            command=self.prev_board,
        )
        prev_board_button.pack(side=tk.LEFT, padx=[10, 5], pady=5)

        # 次の基板ボタン
        next_board_button = tk.Button(
            board_control_frame,
            text="次へ >>",
            font=("Yu Gothic UI", 10),
            command=self.next_board,
        )
        next_board_button.pack(side=tk.LEFT, padx=[5, 10], pady=5)

    def create_widgets_area(self):
        self.widgets_frame = tk.Frame(self)
        # fill=tk.BOTHとexpand=Trueでフレーム全体を使用可能領域に拡張
        self.widgets_frame.pack(fill=tk.BOTH, expand=True, padx=10)

    def create_canvas_widgets(self):
        # 固定サイズを削除し、可変サイズに変更
        self.canvas = tk.Canvas(self.widgets_frame, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        # 左クリック処理をバインド
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Canvasサイズ変更イベントをバインド
        self.canvas.bind("<Configure>", self.on_canvas_resize)

    def create_defect_list_widgets(self):
        self.defect_list_frame = tk.Frame(self.widgets_frame)
        # 固定幅を削除し、最小幅を設定
        self.defect_list_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # フレームの最小幅を設定
        self.defect_list_frame.config(width=350)
        self.defect_list_frame.pack_propagate(False)  # サイズ固定

        # Treeviewの作成
        columns = ("No", "RF", "不良項目", "修理")
        self.defect_listbox = ttk.Treeview(
            self.defect_list_frame, columns=columns, show="headings"
        )
        col_widths = {"No": 40, "RF": 80, "不良項目": 150, "修理": 40}
        for col in columns:
            self.defect_listbox.heading(col, text=col)
            self.defect_listbox.column(col, width=col_widths[col], anchor="center")

        # TreeviewとScrollbarをFrame内で横並びに配置
        self.defect_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(
            self.defect_list_frame,
            orient=tk.VERTICAL,
            command=self.defect_listbox.yview,
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.defect_listbox.configure(yscrollcommand=scrollbar.set)
        # Treeviewの選択イベントをバインド
        self.defect_listbox.bind("<<TreeviewSelect>>", self.on_defect_select)

    def create_status_bar(self):
        """ステータスバーを作成"""
        self.status_frame = tk.Frame(self, relief=tk.SUNKEN, bd=1)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # ステータスメッセージラベル
        self.status_label = tk.Label(
            self.status_frame, text="準備完了", font=("Yu Gothic UI", 9), anchor="w"
        )
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)

        # 右側の情報表示エリア
        self.status_right_frame = tk.Frame(self.status_frame)
        self.status_right_frame.pack(side=tk.RIGHT, padx=5, pady=2)

        # SMTスケジュール読み込み状況
        self.smt_status_label = tk.Label(
            self.status_right_frame,
            text="SMT計画表: 待機中",
            font=("Yu Gothic UI", 9),
            fg="orange",
        )
        self.smt_status_label.pack(side=tk.RIGHT, padx=10)

        # 接続状況インジケータ
        self.connection_label = tk.Label(
            self.status_right_frame, text="● 未接続", font=("Yu Gothic UI", 9), fg="red"
        )
        self.connection_label.pack(side=tk.RIGHT, padx=10)

    def update_status(self, message: str):
        """ステータスメッセージを更新"""
        try:
            # ウィジェットが存在し、まだ有効かチェック
            if hasattr(self, "status_label") and self.status_label.winfo_exists():
                self.status_label.config(text=message)
        except tk.TclError:
            # ウィジェットが既に破棄されている場合は何もしない
            pass

    def safe_update_status(self, message: str):
        """安全なステータス更新（非同期処理用）"""
        try:
            # ウィンドウ自体が存在するかチェック
            if hasattr(self, "winfo_exists") and self.winfo_exists():
                self.update_status(message)
        except (tk.TclError, AttributeError):
            # ウィンドウが既に破棄されている場合は何もしない
            pass

    def update_smt_status(self, status: str, color: str = "black"):
        """SMTスケジュール読み込み状況を更新"""
        try:
            if (
                hasattr(self, "smt_status_label")
                and self.smt_status_label.winfo_exists()
            ):
                self.smt_status_label.config(text=f"SMT計画表: {status}", fg=color)
        except tk.TclError:
            pass

    def update_connection_status(self, connected: bool):
        """接続状況を更新"""
        try:
            if (
                hasattr(self, "connection_label")
                and self.connection_label.winfo_exists()
            ):
                if connected:
                    self.connection_label.config(
                        text="● キントーンAPI接続済み", fg="green"
                    )
                else:
                    self.connection_label.config(text="● キントーンAPIエラー", fg="red")
        except tk.TclError:
            pass

    def on_window_resize(self, event):
        """ウィンドウリサイズ時の処理"""
        # self以外のウィジェットのConfigureイベントは無視
        if event.widget != self:
            return

        # Canvas内に画像がある場合は再描画
        if hasattr(self, "current_image_path") and self.current_image_path:
            # 少し遅延させて処理（連続リサイズ時の負荷軽減）
            self.after(100, self._delayed_image_update)

    def on_canvas_resize(self, event):
        """Canvasリサイズ時の処理"""
        # Canvas内に画像がある場合は再描画
        if hasattr(self, "current_image_path") and self.current_image_path:
            # 少し遅延させて処理（連続リサイズ時の負荷軽減）
            self.after(100, self._delayed_image_update)

    def _delayed_image_update(self):
        """遅延画像更新処理（連続呼び出し防止）"""
        if hasattr(self, "_update_scheduled"):
            return

        self._update_scheduled = True

        def _update():
            try:
                if hasattr(self, "current_image_path") and self.current_image_path:
                    self.open_select_image(self.current_image_path)
            finally:
                if hasattr(self, "_update_scheduled"):
                    delattr(self, "_update_scheduled")

        self.after(50, _update)

    def canvas_to_relative_coords(self, canvas_x: int, canvas_y: int) -> tuple:
        """Canvas座標を画像の相対座標（0.0～1.0）に変換"""
        if not self.displayed_image_size or not self.image_offset:
            return None, None

        # Canvas座標から画像内座標に変換
        img_x = canvas_x - self.image_offset[0]
        img_y = canvas_y - self.image_offset[1]

        # 画像境界チェック
        if (
            img_x < 0
            or img_y < 0
            or img_x >= self.displayed_image_size[0]
            or img_y >= self.displayed_image_size[1]
        ):
            return None, None

        # 相対座標に変換（0.0～1.0）
        rel_x = img_x / self.displayed_image_size[0]
        rel_y = img_y / self.displayed_image_size[1]

        return rel_x, rel_y

    def relative_to_canvas_coords(self, rel_x: float, rel_y: float) -> tuple:
        """相対座標（0.0～1.0）をCanvas座標に変換"""
        if not self.displayed_image_size or not self.image_offset:
            return None, None

        # 表示されている画像内の座標に変換
        img_x = rel_x * self.displayed_image_size[0]
        img_y = rel_y * self.displayed_image_size[1]

        # Canvas座標に変換
        canvas_x = img_x + self.image_offset[0]
        canvas_y = img_y + self.image_offset[1]

        return int(canvas_x), int(canvas_y)

    def open_image(self):
        """画像を開くダイアログを表示し、選択された画像をcanvasに表示"""
        filepath = filedialog.askopenfilename(
            filetypes=[
                ("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"),
                ("All Files", "*.*"),
            ]
        )
        if not filepath:
            return
        try:
            self.current_image_path = filepath
            image = Image.open(filepath)
            image.thumbnail((self.canvas.winfo_width(), self.canvas.winfo_height()))
            self.photo_image = ImageTk.PhotoImage(image)
            self.canvas.delete("all")
            self.canvas.create_image(
                self.canvas.winfo_width() // 2,
                self.canvas.winfo_height() // 2,
                image=self.photo_image,
                anchor="center",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image:\n{e}")

    def open_select_image(self, filepath: str):
        """指定されたファイルパスの画像をcanvasに表示"""
        if not filepath:
            return
        try:
            self.current_image_path = filepath
            image = Image.open(filepath)

            # 元画像のサイズを保存
            self.original_image_size = image.size

            # Canvas実際のサイズを取得
            self.canvas.update_idletasks()  # サイズ情報を確実に取得
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # Canvasサイズが取得できない場合（初期化時など）はデフォルト値を使用
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 800  # デフォルト幅
                canvas_height = 400  # デフォルト高さ

            # 画像のアスペクト比を計算
            img_width, img_height = image.size
            img_aspect = img_width / img_height
            canvas_aspect = canvas_width / canvas_height

            # アスペクト比を維持しつつ、Canvasに最適なサイズを計算
            if img_aspect > canvas_aspect:
                # 画像が横長の場合、幅を基準にリサイズ
                new_width = canvas_width
                new_height = int(canvas_width / img_aspect)
            else:
                # 画像が縦長の場合、高さを基準にリサイズ
                new_height = canvas_height
                new_width = int(canvas_height * img_aspect)

            # 画像をリサイズ（アスペクト比保持、拡大・縮小両対応）
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.displayed_image_size = image.size

            # 画像の中央配置のためのオフセット計算
            self.image_offset = (
                (canvas_width - self.displayed_image_size[0]) // 2,
                (canvas_height - self.displayed_image_size[1]) // 2,
            )

            self.photo_image = ImageTk.PhotoImage(image)
            self.canvas.delete("all")

            # 画像を中央に配置
            self.canvas.create_image(
                canvas_width // 2,
                canvas_height // 2,
                image=self.photo_image,
                anchor="center",
            )

            # 既存の座標マーカーを再描画
            # self.redraw_coordinate_markers()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image:\n{e}")

    def draw_coordinate_marker(
        self, rel_x: float, rel_y: float, tag="coordinate_marker"
    ):
        """相対座標に基づいて座標マーカーを描画"""
        # 相対座標をCanvas座標に変換
        canvas_x, canvas_y = self.relative_to_canvas_coords(rel_x, rel_y)

        if canvas_x is None or canvas_y is None:
            return

        # マーカーのサイズ
        r = 5

        # 既存のマーカーを削除
        self.canvas.delete(tag)

        # 新しいマーカーを追加
        self.canvas.create_oval(
            canvas_x - r,
            canvas_y - r,
            canvas_x + r,
            canvas_y + r,
            fill=self.fillColor,
            outline="red",
            width=2,
            tags=tag,
        )

    def redraw_coordinate_markers(self):
        """既存の不良座標マーカーを再描画"""
        # defect_listが空の場合は何もしない
        if not self.defect_list:
            return

        # 現在の基板の不良リストを取得
        current_defects = [
            d
            for d in self.defect_list
            if d.current_board_index == self.current_board_index
        ]

        # 全ての座標マーカーをクリア
        self.canvas.delete("defect_marker")

        # 各不良座標にマーカーを描画
        for i, defect in enumerate(current_defects):
            if defect.x is not None and defect.y is not None:
                # 相対座標として扱う
                self.draw_coordinate_marker(
                    defect.x, defect.y, tag=f"defect_marker_{i}"
                )

    def on_defect_select(self, event):
        """defect_listboxで選択されたアイテムの情報をエントリに表示し、canvasに座標マーカーを表示"""
        # 選択中のアイテムを取得
        selected_item = self.defect_listbox.selection()
        if selected_item:
            # 選択中のアイテムの値を取得
            item_values = self.defect_listbox.item(selected_item[0], "values")
            self.no_value.config(text=item_values[0])  # No列を表示
            self.rf_entry.delete(0, tk.END)  # RFエントリをクリア
            self.rf_entry.insert(0, item_values[1])  # RFエントリに値を設定
            self.defect_entry.delete(0, tk.END)  # 不良項目エントリをクリア
            self.defect_entry.insert(0, item_values[2])  # 不良項目エントリに値を設定
            index = int(item_values[0]) - 1  # Noは1始まりなので-1してインデックスに変換
            defect_item = self.defect_list[
                index
            ]  # defect_listから選択中のアイテムを取得

            # 相対座標を取得
            rel_x, rel_y = defect_item.x, defect_item.y  # 相対座標として扱う
            self.current_coordinates = (rel_x, rel_y)  # 現在の座標を更新

            # canvasに座標マーカーを表示
            if rel_x is not None and rel_y is not None:
                self.draw_coordinate_marker(rel_x, rel_y)

    def defect_number_update(self):
        filter_defect_list = [
            d
            for d in self.defect_list
            if d.current_board_index == self.current_board_index
        ]
        max_len = len(filter_defect_list)
        self.no_value.config(text=str(max_len + 1))

    def defect_list_insert(self, item: DefectInfo):
        self.defect_list.append(item)
        self.defect_listbox.insert(
            "", "end", values=[item.defect_number, item.reference, item.defect_name, ""]
        )
        self.defect_number_update()

    def defect_list_delete(self, index, tree_index: str):
        del self.defect_list[index]
        self.defect_listbox.delete(tree_index)
        self.defect_listbox_no_reset()
        self.defect_number_update()
        # canvasの座標マーカーを削除
        self.canvas.delete("coordinate_marker")

    def defect_list_update(self, index: str, item: DefectInfo):
        # indexが数値に変換可能か確認
        if not index.isdigit():
            messagebox.showerror("Error", "不良番号が不正です。")
            return
        index = int(index)
        self.defect_list[index - 1] = item
        self.defect_listbox.item(
            self.defect_listbox.get_children()[index - 1],
            values=[item.defect_number, item.reference, item.defect_name, ""],
        )
        self.defect_number_update()
        # canvasの座標マーカーを削除
        self.canvas.delete("coordinate_marker")

    def exists_defect_listbox(self, defect_number: str) -> bool:
        """defect_listboxに指定された不良番号が存在するか確認"""
        for item in self.defect_listbox.get_children():
            values = self.defect_listbox.item(item, "values")
            if values[0] == defect_number:
                return True
        return False

    def read_defect_list_csv(self, filepath: str):
        """CSVファイルから不良リストを読み込み、defect_listに設定"""
        try:
            # ライブラリを使用して不良データを取得
            self.defect_list = FileManager.read_defect_csv(filepath)

            # 修理データを取得
            repaird_path = FileManager.create_repaird_csv_path(
                self.data_directory, self.current_lot_number
            )
            self.repaird_list = FileManager.read_repaird_csv(repaird_path)
            self.update_defect_listbox()
        except Exception as e:
            raise Exception(e)

    def read_defect_list_db(self):
        """SQLiteデータベースから不良リストを読み込み、defect_listに設定"""
        try:
            if self.sqlite_db:
                self.defect_list = self.sqlite_db.get_defect_info_by_lot(
                    self.current_lot_number
                )
                self.update_defect_listbox()
        except Exception as e:
            raise Exception(e)

    def save_defect_info(self):
        """保存ボタンを押したときの処理"""

        # データディレクトリが有効か確認
        if not self.exist_data_directory():
            messagebox.showerror(
                "Error",
                "データディレクトリに接続できませんでした。ネットワークへの接続を確認してください。",
            )
            return

        # 不良番号を不良名に変換
        self.convert_defect_name()
        # 各種情報を取得
        insert_date = datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )  # 登録日時
        current_board_index = self.current_board_index  # 現在の基板番号
        defect_number = self.no_value.cget("text")  # 不良番号
        rf = self.rf_entry.get().upper()  # リファレンス
        defect_name = self.defect_entry.get()  # 不良項目
        serial = self.serial_entry.get()  # シリアルNo
        aoi_user = self.aoi_user_label_value.cget("text")  # AOI担当
        model_code = self.current_item_code if self.current_item_code else ""
        lot_number = self.current_lot_number if self.current_lot_number else ""
        model_name = self.model_label_value.cget("text")
        board_name = self.board_label_value.cget("text")
        side_label = self.side_label_value.cget("text")
        model_label = model_name + " " + board_name
        board_label = model_label + " " + side_label

        # 相対座標を取得（既に相対座標として保存されている）
        rel_x, rel_y = (
            self.current_coordinates if self.current_coordinates else (None, None)
        )

        # 入力チェック
        if not rf or not defect_name:
            messagebox.showwarning("Warning", "RFと不良項目を入力してください。")
            return
        if rel_x is None or rel_y is None:
            messagebox.showwarning("Warning", "基板上の座標をクリックしてください。")
            return

        # defect_listに追加（相対座標で保存）
        defect = DefectInfo(
            line_name=self.current_line_name,
            current_board_index=current_board_index,
            defect_number=defect_number,
            reference=rf,
            defect_name=defect_name,
            x=rel_x,  # 相対座標（0.0～1.0）
            y=rel_y,  # 相対座標（0.0～1.0）
            insert_datetime=insert_date,
            serial=serial,
            aoi_user=aoi_user,
            model_code=model_code,
            lot_number=lot_number,
            model_label=model_label,
            board_label=board_label,
        )

        if self.exists_defect_listbox(defect_number):
            self.defect_list_update(defect_number, defect)
        else:
            self.defect_list_insert(defect)

        # 入力エントリを初期化
        self.rf_entry.delete(0, tk.END)
        self.defect_entry.delete(0, tk.END)

        # 既存の座標マーカーを削除
        self.canvas.delete("coordinate_marker")

        # sqlteデータベースに登録
        self.__insert_defect_info_to_db(self.defect_list)

        # キントーンにデータを登録
        self.post_kintone_record_async(self.defect_list)

    def delete_defect_info(self):
        selected_item = self.defect_listbox.selection()
        if selected_item:
            # Treeview内の全アイテムIDリスト
            items = self.defect_listbox.get_children()
            # インデックス（0始まり）
            index = items.index(selected_item[0])
            defect_item = self.defect_list[index]
            kintone_record_id = defect_item.kintone_record_id
            self.delete_kintone_record_async(kintone_record_id)
            self.defect_list_delete(index, selected_item[0])
            self.rf_entry.delete(0, tk.END)
            self.defect_entry.delete(0, tk.END)
            # データベースから削除
            self.__remove_defect_info_from_db(defect_item)
            messagebox.showinfo("Info", "不良情報を削除しました。")
        else:
            messagebox.showwarning("Warning", "リストから不良情報を選択してください。")

    def defect_listbox_no_reset(self):
        # self.defect_listboxのNo列を再設定
        for idx, item in enumerate(self.defect_listbox.get_children(), start=1):
            values = list(self.defect_listbox.item(item, "values"))
            values[0] = idx
            self.defect_listbox.item(item, values=values)
        # self.defect_listのNo列を再設定
        for idx, item in enumerate(self.defect_list, start=1):
            item.defect_number = str(idx)

    def on_canvas_click(self, event):
        # canvasに画像がない場合は何もしない
        if not hasattr(self, "photo_image") or not self.displayed_image_size:
            return

        # canvasに座標がある場合は削除
        self.canvas.delete("coordinate_marker")

        # Canvas座標を相対座標に変換
        rel_x, rel_y = self.canvas_to_relative_coords(event.x, event.y)

        # 画像外をクリックした場合は何もしない
        if rel_x is None or rel_y is None:
            messagebox.showinfo("Info", "画像内をクリックしてください。")
            return

        # 不具合情報を初期化
        self.rf_entry.delete(0, tk.END)
        self.defect_entry.delete(0, tk.END)
        self.defect_number_update()

        # 相対座標を保存
        self.current_coordinates = (rel_x, rel_y)

        # 座標マーカーを表示
        self.draw_coordinate_marker(rel_x, rel_y)

    def update_defect_listbox(self):
        # defect_listboxをdefect_listの内容で更新
        self.defect_listbox.delete(*self.defect_listbox.get_children())
        for item in self.defect_list:
            id = item.id
            find_repaird = [r for r in self.repaird_list if r.id == id]
            if self.current_board_index == item.current_board_index:
                if len(find_repaird) > 0:
                    repaird_item = find_repaird[0]
                    repaird_str = "済" if repaird_item.is_repaird == "修理済み" else ""
                    self.defect_listbox.insert(
                        "",
                        "end",
                        values=[
                            item.defect_number,
                            item.reference,
                            item.defect_name,
                            repaird_str,
                        ],
                    )
                else:
                    self.defect_listbox.insert(
                        "",
                        "end",
                        values=[
                            item.defect_number,
                            item.reference,
                            item.defect_name,
                            "",
                        ],
                    )
        self.defect_number_update()

    def update_index(self):
        items = self.defect_list
        # itemsから1つ目の要素をlistで取得
        indices = [
            item.current_board_index
            for item in items
            if isinstance(item.current_board_index, int)
        ]
        self.total_boards = max(indices) if indices else 1
        self.current_board_index = 1

    def prev_board(self):
        if self.current_board_index > 1:
            self.current_board_index = self.current_board_index - 1
            self.update_board_label()
            # treeviewを初期化
            self.update_defect_listbox()
            self.defect_number_update()
        else:
            messagebox.showinfo("Info", "これ以上前の基板はありません。")

    def next_board(self):
        """次の基板へ切り替え処理"""
        # 現在の指図に対応するCSVファイルを読み込み
        if not self.current_image_filename:
            raise ValueError("Current image filename is not set.")
        # データディレクトリが有効か確認
        if not self.exist_data_directory():
            messagebox.showerror(
                "Error",
                "データディレクトリに接続できませんでした。ネットワークへの接続を確認してください",
            )
            return

        # データベースにアイテムを追加
        self.__insert_defect_info_to_db(self.defect_list)

        # 画面を更新
        self.current_board_index = self.current_board_index + 1
        self.total_boards = max(self.total_boards, self.current_board_index)
        self.update_board_label()
        # treeviewを初期化
        self.update_defect_listbox()
        self.defect_number_update()

    def exist_data_directory(self):
        """データディレクトリが存在するか確認"""
        if not self.data_directory or not os.path.exists(self.data_directory):
            return False
        return True

    def defect_list_to_csv_async(self) -> bool:
        """
        非同期にdefect_listをCSVファイルに保存

        Returns:
            bool: 保存処理の成功/失敗を返す
        """
        # 結果を格納する変数
        result = {"success": False}

        def _defect_list_to_csv():
            max_retries = 3
            retry_delay = 1.0  # 秒

            file_path = FileManager.create_defect_csv_path(
                self.data_directory,
                self.current_lot_number,
                self.current_image_filename,
            )

            for attempt in range(max_retries):
                try:
                    FileManager.save_defect_csv(self.defect_list, file_path)
                    # 🔧 修正: 成功時はステータスを更新して終了
                    self.after(
                        0,
                        lambda: self.safe_update_status(
                            f"不良データを保存しました: {os.path.basename(file_path)}"
                        ),
                    )
                    result["success"] = True
                    return

                except PermissionError as pe:
                    if attempt < max_retries - 1:
                        # 🔧 修正: リトライ時のメッセージ
                        message = f"ファイルが使用中です。{retry_delay}秒後に再試行します... ({attempt + 1}/{max_retries})"
                        print(message)
                        self.after(0, lambda msg=message: self.safe_update_status(msg))
                        time.sleep(retry_delay)
                        continue
                    else:
                        # 🔧 修正: 最終的に失敗した場合
                        error_msg = (
                            f"ファイルが他のアプリケーション（Excel等）で開かれています。\n"
                            f"ファイルを閉じてから再試行してください:\n{file_path}"
                        )
                        self.after(
                            0,
                            lambda: messagebox.showerror(
                                "ファイル保存エラー", error_msg
                            ),
                        )
                        self.after(
                            0,
                            lambda: self.safe_update_status(
                                "ファイル保存に失敗しました（ファイル使用中）"
                            ),
                        )
                        result["success"] = False
                        return

                except OSError as oe:
                    if oe.errno == 13:  # Permission denied
                        error_msg = f"ファイルアクセス権限がありません: {file_path}"
                        self.after(
                            0,
                            lambda: messagebox.showerror(
                                "アクセス権限エラー", error_msg
                            ),
                        )
                    else:
                        error_msg = f"ファイル保存中にOSエラーが発生しました: {oe}"
                        self.after(
                            0, lambda: messagebox.showerror("OSエラー", error_msg)
                        )
                    self.after(
                        0,
                        lambda: self.safe_update_status(
                            "ファイル保存に失敗しました（OSエラー）"
                        ),
                    )
                    result["success"] = False
                    return

                except Exception as e:
                    error_msg = f"ファイル保存中に予期しないエラーが発生しました: {e}"
                    self.after(0, lambda: messagebox.showerror("保存エラー", error_msg))
                    self.after(
                        0, lambda: self.safe_update_status("ファイル保存に失敗しました")
                    )
                    result["success"] = False
                    return

        # ThreadPoolExecutorを使用して結果を取得
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_defect_list_to_csv)
            try:
                # スレッドの完了を待機（タイムアウト設定可能）
                future.result(timeout=30)  # 30秒でタイムアウト
            except Exception as e:
                self.after(
                    0,
                    lambda: messagebox.showerror(
                        "保存エラー", f"保存処理がタイムアウトしました: {e}"
                    ),
                )
                result["success"] = False

        return result["success"]

    def update_board_label(self):
        self.board_no_label.config(
            text=f"{self.current_board_index} / {self.total_boards} 枚"
        )

    def read_csv_path(self):
        """指図に対応するCSVファイルのパスを取得"""
        if not self.current_image_filename:
            raise ValueError("Current image filename is not set.")
        return FileManager.create_defect_csv_path(
            self.data_directory, self.current_lot_number, self.current_image_filename
        )

    def open_settings(self):
        """設定ダイアログを開く"""
        dialog = SettingsWindow(self)
        self.wait_window(dialog)  # ダイアログが閉じるまで待機
        new_settings = dialog.result
        project_dir = get_project_dir()
        if new_settings:
            # 新しい設定を適用
            self.image_directory = new_settings[0]
            self.data_directory = new_settings[1]
            self.schedule_directory = new_settings[2]
            # 設定ファイルが存在しない場合は新規作成
            settings_path = get_config_file_path("settings.ini")
            if not settings_path.exists():
                # 新しい設定を保存
                config = configparser.ConfigParser()
                config["DIRECTORIES"] = {
                    "image_directory": new_settings[0],
                    "data_directory": new_settings[1],
                    "schedule_directory": new_settings[2],
                    "shared_directory": new_settings[3],
                }
                with open(settings_path, "w", encoding="utf-8") as configfile:
                    config.write(configfile)
            else:
                # 既存の設定ファイルを更新
                config = configparser.ConfigParser()
                config.read(settings_path, encoding="utf-8")
                config["DIRECTORIES"]["image_directory"] = new_settings[0]
                config["DIRECTORIES"]["data_directory"] = new_settings[1]
                config["DIRECTORIES"]["schedule_directory"] = new_settings[2]
                config["DIRECTORIES"]["shared_directory"] = new_settings[3]

                with open(settings_path, "w", encoding="utf-8") as configfile:
                    config.write(configfile)

            messagebox.showinfo(
                "Info",
                f"新しい設定: {new_settings[0]}, {new_settings[1]}, {new_settings[2]} に変更されました。",
            )
        else:
            messagebox.showinfo("Info", "設定の変更がキャンセルされました。")

    def __search_schedule_df_item(self, lot_number: str) -> dict:
        """SMTスケジュールから品目コードを検索"""

        # SMT計画表が読み込まれていない場合はNoneを返す
        if self.is_read_schedule is False:
            messagebox.showwarning("Warning", "SMT計画表が読み込まれていません。")
            return None

        # self.schedule_dfからレコードを抽出して最初のレコードを辞書に変換
        records = self.schedule_df[self.schedule_df["lot_number"] == lot_number]
        if records.empty:
            return None
        return records.iloc[0].to_dict()

    def change_lot(self):
        """指図変更処理"""

        # ユーザーが未設定の場合は警告を表示して終了
        if not self.is_set_user():
            messagebox.showwarning(
                "Warning", "AOI担当が設定されていません。ユーザーを設定してください。"
            )
            return

        # API送信
        if len(self.defect_list) > 0:
            try:
                self.post_kintone_record_async(self.defect_list)
            except ValueError as e:
                print(e)
                messagebox.showerror("送信エラー", f"API送信エラー:{e}")

        # defect_listをCSVに保存
        if len(self.defect_list) > 0:
            # データベースにアイテムを追加
            self.__insert_defect_info_to_db(self.defect_list)

        # すべての座標マーカーを削除
        self.canvas.delete("all")

        # データリストを事前に初期化
        self.defect_list = []
        self.repaird_list = []
        self.current_coordinates = None

        # 指図を入力するダイアログを表示
        dialog = LotChangeDialog(self)
        if not hasattr(dialog, "result") or not dialog.result:
            messagebox.showinfo("Info", "指図の変更がキャンセルされました。")
            return

        # 指図を取得
        self.current_lot_number = dialog.result

        # 指図形式のバリデーション
        if self.is_validation_lot_name(self.current_lot_number) is False:
            messagebox.showwarning("Warning", "指図の形式が不正です。例: 1234567-10")
            self.current_item_code = None
            self.current_lot_number = None
            return

        # item_code, line_nameを取得する
        schedule_item = self.__search_schedule_df_item(self.current_lot_number)
        self.current_item_code = schedule_item.get("model_code")
        self.current_line_name = schedule_item.get("machine_name")

        # item_codeが見つからなかった場合
        if not self.current_item_code:
            # アイテムコード入力ダイアログを表示
            itemDialog = ItemCodeChangeDialog(self)
            if not hasattr(itemDialog, "result") or not itemDialog.result:
                messagebox.showinfo("Info", "品目コードの入力がキャンセルされました。")
                self.current_item_code = None
                self.current_lot_number = None
                return
            # 入力されたitem_codeを設定
            self.current_item_code = itemDialog.result.upper()

        # 画像ディレクトリからitem_codeから始まる画像を探して表示
        try:
            filename = FileManager.get_image_path(
                self.image_directory, self.current_lot_number, self.current_item_code
            )
            self.current_image_path = os.path.join(self.image_directory, filename)

            # 画像表示（defect_listが空であることを確認済み）
            self.open_select_image(self.current_image_path)
        except FileNotFoundError as e:
            # 画像が見つからなかった場合
            if not self.current_image_path:
                self.current_image_path = None
                self.current_item_code = None
                self.current_lot_number = None
                messagebox.showwarning(
                    "Warning", "指定された品目コードに対応する画像が見つかりません。"
                )
                return
        except ValueError:
            # ロットナンバーの形式が不正な場合
            messagebox.showwarning("Warning", "指図の形式が不正です。例: 1234567-10")
            self.current_item_code = None
            self.current_lot_number = None
            return

        # 画像名から機種情報を取得
        if self.current_image_path:
            baseName = os.path.basename(self.current_image_path).split(".")[0]
            self.current_image_filename = baseName
            try:
                parts = FileManager.parse_image_filename(baseName)
                model_name = parts[0]
                board_name = parts[1]
                side_label = parts[2]
            except ValueError:
                # 画像名の形式が不正な場合,エラーメッセージを表示
                messagebox.showwarning(
                    "Warning",
                    "画像ファイル名の形式が不正です。正しい設定例: Y8470722R_20_CN-SNDDJ0CJ_411CA_S面.jpg",
                )
                return

        # 各ラベルを更新
        self.line_label_value.delete(0, tk.END)
        self.line_label_value.insert(0, self.current_line_name or "")
        self.model_label_value.config(text=model_name)
        self.board_label_value.config(text=board_name)
        self.side_label_value.config(text=side_label)
        self.lot_label_value.config(text=self.current_lot_number)

        # ステータスバーの更新
        self.update_status(
            f"品目コード: {self.current_item_code}、指図: {self.current_lot_number} に変更されました。"
        )

        try:
            # csvパスの取得
            csv_path = self.read_csv_path()
            # csvパスが取得できたら不良リストを読み込み
            if csv_path:
                self.current_board_index = 1
                # self.read_defect_list_csv(csv_path)
                self.read_defect_list_db()
                self.update_index()
                self.update_board_label()
                self.defect_number_update()
        except FileNotFoundError as e:
            # FileNotFoundExceptionの場合も明示的に空にする
            self.defect_list = []
            self.repaird_list = []
            self.update_defect_listbox()
            self.update_index()
            self.update_board_label()
            self.defect_number_update()

        if not (self.current_lot_number and self.current_item_code):
            messagebox.showinfo(
                "Info", "品目コードと指図の変更がキャンセルされました。"
            )
            return

    def is_validation_lot_name(self, lot_name: str) -> bool:
        """指図名のバリデーション"""
        if not lot_name:
            return False
        regex = r"^\d{7}-10$|^\d{7}-20$"
        return bool(re.match(regex, lot_name))

    def change_user(self):
        """ユーザー名を変更するダイアログを開く"""
        dialog = ChangeUserDialog(self)
        if not hasattr(dialog, "result") or not dialog.result:
            messagebox.showinfo("Info", "ユーザー名の変更がキャンセルされました。")
            return

        user_id = dialog.result.upper()
        user_csv_path = get_csv_file_path("user.csv")

        try:
            df = FileManager.read_user_csv(str(user_csv_path))
            user_ids = [str(uid) for uid in df["id"].tolist()]

            if user_id not in user_ids:
                messagebox.showerror("Error", f"ユーザーID: {user_id} は存在しません。")
                return

            matching_rows = df.loc[df["id"] == user_id, "name"]
            if matching_rows.empty:
                messagebox.showerror("Error", f"ユーザーID: {user_id} は存在しません。")
                return

            self.user_name = matching_rows.values[0]
            self.aoi_user_label_value.config(text=self.user_name)
        except Exception as e:
            messagebox.showerror("Error", f"ユーザー情報の読み込みエラー: {e}")

    def is_set_user(self) -> bool:
        """ユーザー名が設定されているか確認"""
        user = self.aoi_user_label_value.cget("text")
        return bool(user)

    def convert_defect_name(self):
        """不良項目名を変換する"""
        defect_number = self.defect_entry.get()
        if not defect_number or not defect_number.isdigit():
            return

        defect_number = int(defect_number)
        mapping_csv_path = PROJECT_DIR / "defect_mapping.csv"

        try:
            df = FileManager.read_defect_mapping(str(mapping_csv_path))
            if defect_number in df["no"].values:
                standard_name = df.loc[df["no"] == defect_number, "name"].values[0]
                self.defect_entry.delete(0, tk.END)
                self.defect_entry.insert(0, standard_name)
        except Exception as e:
            print(f"Error converting defect name: {e}")

    def show_defect_mapping(self):
        """不良名一覧を表示する"""
        mapping_csv_path = PROJECT_DIR / "defect_mapping.csv"
        if not mapping_csv_path.exists():
            raise FileNotFoundError(
                f"defect_mapping.csv not found at {mapping_csv_path}"
            )
        df = pd.read_csv(mapping_csv_path, encoding="utf-8-sig")
        df = df.dropna()
        # dfのno列をfloatだった場合にintに変換
        df["no"] = df["no"].apply(
            lambda x: int(x) if isinstance(x, float) and x.is_integer() else x
        )
        mapping_text = "\n".join(
            [f"{row['no']}: {row['name']}" for _, row in df.iterrows()]
        )
        messagebox.showinfo("不良名一覧", mapping_text)

    def open_kintone_settings(self):
        """キントーン設定画面を開く"""
        dialog = KintoneSettings(self)
        self.wait_window(dialog)  # ダイアログが閉じるまで待機
        result = dialog.result
        if result:
            self.init_kintone_client()
            self.kintone_connected_async()

    def post_kintone_record_async(self, defect_list: List[DefectInfo]):
        """Kintoneにレコードを送信する非同期処理"""

        # キントーンAPIに接続されていない場合は終了
        if self.is_kintone_connected is False:
            # 🔧 修正: self.after()を使用してメインスレッドで実行
            self.after(
                0,
                lambda: self.safe_update_status(
                    "キントーンAPIに接続されていない為、レコードの登録が失敗しました。"
                ),
            )
            return

        def _send_request():
            """Kintoneにレコードを送信する処理"""
            try:
                # キントーンにレコードを送信
                updated_defect_list = self.kintone_client.post_defect_records(
                    defect_list
                )
                # 送信後のdefect_listを更新
                self.defect_list = updated_defect_list
                # 成功したらステータスバーを更新
                count = len(updated_defect_list)
                # 🔧 修正: self.after()を使用してメインスレッドで実行
                if count > 0:
                    self.after(
                        0,
                        lambda: self.safe_update_status(
                            "キントーンアプリにレコードを登録しました。"
                        ),
                    )
            except Exception as e:
                # 🔧 修正: self.after()を使用してメインスレッドでエラー処理
                error_msg = f"API送信エラー: {e}"
                self.after(0, lambda: self.safe_update_status(error_msg))
                print(error_msg)  # ログ出力のみ

        # 別スレッドで非同期処理
        thread = threading.Thread(target=_send_request, daemon=True)
        thread.start()

    def delete_kintone_record_async(self, record_id: str):
        """Kintoneレコードを削除"""

        # キントーンAPIに接続されていない場合は終了
        if self.is_kintone_connected is False:
            # 🔧 修正: self.after()を使用してメインスレッドで実行
            self.after(
                0,
                lambda: self.safe_update_status(
                    "キントーンAPIに接続されていない為、レコードの削除が失敗しました。"
                ),
            )
            return

        def _delete_request():
            """Kintoneレコードを削除する処理"""
            try:
                # キントーンにレコードを削除
                self.kintone_client.delete_record(record_id)
                # 🔧 修正: self.after()を使用してメインスレッドで実行
                self.after(
                    0,
                    lambda: self.safe_update_status(
                        "キントーンアプリからレコードを削除しました。"
                    ),
                )
            except Exception as e:
                # 🔧 修正: self.after()を使用してメインスレッドでエラー処理
                error_msg = f"API削除エラー: {e}"
                self.after(0, lambda: self.safe_update_status(error_msg))
                print(error_msg)  # ログ出力のみ

        # 別スレッドで非同期処理
        thread = threading.Thread(target=_delete_request, daemon=True)
        thread.start()
