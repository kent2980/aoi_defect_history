import tkinter as tk
from pathlib import Path

from aoi_data_manager import FileManager


class KintoneSettings(tk.Toplevel):
    """キントーン設定ウィンドウ"""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("キントーン設定")
        self.transient(parent)
        self.grab_set()
        # ここにキントーン設定用のウィジェットを追加
        label = tk.Label(self, text="キントーンのAPI設定をここに追加してください")
        label.pack(pady=20)

        # 入力フィールドとラベルの作成
        self.create_input_fields()
        self.create_buttons()

        # 既存の設定を読み込み、入力フィールドに初期値を設定
        self.init_input_fields()

        # ウィンドウを中央に配置
        self.center_window()

    def center_window(self):
        """ウィンドウを画面中央に配置"""
        # ウィンドウのサイズを更新
        self.update_idletasks()
        # ウィンドウの幅と高さを取得
        width = self.winfo_width()
        height = self.winfo_height()
        # 画面の幅と高さを取得
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        # 中央の座標を計算
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        # ウィンドウ位置を設定
        self.geometry(f"+{x}+{y}")
        # ウィンドウサイズを設定
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_input_fields(self):
        """キントーン設定の入力フィールドを作成"""
        frame = tk.Frame(self)
        frame.pack(pady=10)

        # 例: APIトークン入力フィールド
        tk.Label(frame, text="APIトークン:").grid(
            row=0, column=0, sticky="e", padx=5, pady=5
        )
        self.api_token_entry = tk.Entry(frame, width=50)
        self.api_token_entry.grid(row=0, column=1, padx=5, pady=5)

        # 例: ドメイン入力フィールド
        tk.Label(frame, text="サブドメイン:").grid(
            row=1, column=0, sticky="e", padx=5, pady=5
        )
        self.subdomain_entry = tk.Entry(frame, width=50)
        self.subdomain_entry.grid(row=1, column=1, padx=5, pady=5)

        # 例: アプリID入力フィールド
        tk.Label(frame, text="アプリID:").grid(
            row=2, column=0, sticky="e", padx=5, pady=5
        )
        self.app_id_entry = tk.Entry(frame, width=50)
        self.app_id_entry.grid(row=2, column=1, padx=5, pady=5)

    def create_buttons(self):
        """OKとキャンセルボタンを作成"""
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)

        ok_button = tk.Button(button_frame, text="OK", command=self.on_ok, width=10)
        ok_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(
            button_frame, text="キャンセル", command=self.on_cancel, width=10
        )
        cancel_button.pack(side=tk.LEFT, padx=5)

    def on_ok(self):
        """OKボタンがクリックされたときの処理"""
        # 入力された設定を取得
        api_token = self.api_token_entry.get()
        subdomain = self.subdomain_entry.get()
        app_id = self.app_id_entry.get()

        # ここで設定を保存する処理を追加
        print("APIトークン:", api_token)
        print("サブドメイン:", subdomain)
        print("アプリID:", app_id)

        self.result = False

        # 設定ファイルを保存する
        project_root = Path(__file__).resolve().parent.parent.parent
        config_path = project_root / "kintone_settings.ini"
        is_result = FileManager.create_kintone_settings_file(
            settings_path=config_path,
            api_token=api_token,
            subdomain=subdomain,
            app_id=app_id,
        )
        if is_result:
            print("キントーン設定が保存されました。")
        else:
            print("キントーン設定の保存に失敗しました。")

        self.result = True

        self.destroy()

    def on_cancel(self):
        """キャンセルボタンがクリックされたときの処理"""
        self.result = None
        self.destroy()

    def init_input_fields(self):
        """既存の設定を読み込み、入力フィールドに初期値を設定"""
        project_root = Path(__file__).resolve().parent.parent.parent
        config_path = project_root / "kintone_settings.ini"
        config = FileManager.load_kintone_settings_file(config_path)
        if config:
            print(config)
            self.api_token_entry.insert(0, config["api_token"])
            self.subdomain_entry.insert(0, config["subdomain"])
            self.app_id_entry.insert(0, config["app_id"])
