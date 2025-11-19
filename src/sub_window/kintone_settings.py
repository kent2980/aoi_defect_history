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

        # 入力検証
        if not all([api_token, subdomain, app_id]):
            messagebox.showwarning(
                "警告", "すべての項目を入力してください。"
            )
            return

        # 環境変数として設定（推奨方法）
        # 注意: 現在のプロセスでのみ有効。永続化するには.envファイルを更新する必要がある
        try:
            os.environ["KINTONE_SUBDOMAIN"] = subdomain
            os.environ["KINTONE_APP_ID"] = app_id
            os.environ["KINTONE_API_TOKEN"] = api_token

            messagebox.showinfo(
                "情報",
                "Kintone設定を環境変数に設定しました。\n"
                "永続化するには、.envファイルに以下を追加してください：\n"
                f"KINTONE_SUBDOMAIN={subdomain}\n"
                f"KINTONE_APP_ID={app_id}\n"
                f"KINTONE_API_TOKEN={api_token}"
            )

            self.result = True
        except Exception as e:
            messagebox.showerror("エラー", f"環境変数の設定に失敗しました: {e}")
            self.result = False

        self.destroy()

    def on_cancel(self):
        """キャンセルボタンがクリックされたときの処理"""
        self.result = None
        self.destroy()

    def init_input_fields(self):
        """既存の設定を読み込み、入力フィールドに初期値を設定"""
        # 環境変数から優先的に取得
        api_token = os.getenv("KINTONE_API_TOKEN")
        subdomain = os.getenv("KINTONE_SUBDOMAIN")
        app_id = os.getenv("KINTONE_APP_ID")

        # 環境変数が設定されていない場合は、フォールバックとして設定ファイルを試行
        if not all([api_token, subdomain, app_id]):
            try:
                project_root = Path(__file__).resolve().parent.parent.parent
                config_path = project_root / "kintone_settings.ini"
                if config_path.exists():
                    config = FileManager.load_kintone_settings_file(config_path)
                    if config:
                        api_token = api_token or config.get("api_token", "")
                        subdomain = subdomain or config.get("subdomain", "")
                        app_id = app_id or config.get("app_id", "")
            except Exception as e:
                print(f"警告: 設定ファイルの読み込みに失敗しました: {e}")

        # 入力フィールドに値を設定
        if api_token:
            self.api_token_entry.insert(0, api_token)
        if subdomain:
            self.subdomain_entry.insert(0, subdomain)
        if app_id:
            self.app_id_entry.insert(0, app_id)
