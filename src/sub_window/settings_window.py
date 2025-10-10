import tkinter as tk
from tkinter import filedialog
import configparser
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent.parent


class SettingsWindow(tk.Toplevel):
    """設定ウィンドウ"""

    def __init__(self, parent):
        super().__init__(parent)
        print(PROJECT_DIR)
        self.title("設定")
        self.geometry("600x250")
        self.transient(parent)
        self.grab_set()

        self.result = None
        self.__read_settings()
        self.create_widgets()

        # ウィンドウを中央に配置
        self.center_window()

        # 初期フォーカス設定
        self.setting1_entry.focus_set()

    def __read_settings(self):
        project_dir = PROJECT_DIR
        settings_path = project_dir / "settings.ini"
        # 設定ファイルが存在しない場合は新規作成する
        if not settings_path.exists():
            config = configparser.ConfigParser()
            config["DIRECTORIES"] = {
                "image_directory": "",
                "data_directory": "",
                "schedule_directory": "",
            }
            with open(settings_path, "w", encoding="utf-8") as configfile:
                config.write(configfile)

        # 設定ファイルを読み込む
        if settings_path.exists():
            config = configparser.ConfigParser()
            config.read(settings_path, encoding="utf-8")
            self.current_image_directory = config["DIRECTORIES"].get(
                "image_directory", ""
            )
            self.current_data_directory = config["DIRECTORIES"].get(
                "data_directory", ""
            )
            self.current_schedule_directory = config["DIRECTORIES"].get(
                "schedule_directory", ""
            )
        else:
            self.current_image_directory = ""
            self.current_data_directory = ""
            self.current_schedule_directory = ""

    def create_widgets(self):
        # メインフレーム
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(main_frame, text="データの保存場所を指定してください。").grid(
            row=0, columnspan=3, pady=10
        )

        # 画像ディレクトリ設定
        tk.Label(main_frame, text="画像ディレクトリ:").grid(row=1, column=0, sticky="w")
        self.setting1_entry = tk.Entry(main_frame, width=50)
        self.setting1_entry.grid(row=1, column=1, padx=5, pady=5)
        self.setting1_entry.insert(0, self.current_image_directory)
        tk.Button(main_frame, text="参照", command=self.select_image_directory).grid(
            row=1, column=2, padx=5
        )

        # データディレクトリ設定
        tk.Label(main_frame, text="データディレクトリ:").grid(
            row=2, column=0, sticky="w"
        )
        self.setting2_entry = tk.Entry(main_frame, width=50)
        self.setting2_entry.grid(row=2, column=1, padx=5, pady=5)
        self.setting2_entry.insert(0, self.current_data_directory)
        tk.Button(main_frame, text="参照", command=self.select_data_directory).grid(
            row=2, column=2, padx=5
        )

        # スケジュールディレクトリ設定
        tk.Label(main_frame, text="スケジュールディレクトリ:").grid(
            row=3, column=0, sticky="w"
        )
        self.setting3_entry = tk.Entry(main_frame, width=50)
        self.setting3_entry.grid(row=3, column=1, padx=5, pady=5)
        self.setting3_entry.insert(0, self.current_schedule_directory)
        tk.Button(main_frame, text="参照", command=self.select_schedule_directory).grid(
            row=3, column=2, padx=5
        )

        # ボタンフレーム
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=4, columnspan=3, pady=20)

        # OKボタン
        ok_button = tk.Button(
            button_frame, text="OK", command=self.ok_clicked, width=10
        )
        ok_button.pack(side=tk.LEFT, padx=5)

        # キャンセルボタン
        cancel_button = tk.Button(
            button_frame, text="キャンセル", command=self.cancel_clicked, width=10
        )
        cancel_button.pack(side=tk.LEFT, padx=5)

    def center_window(self):
        """ウィンドウを画面中央に配置"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def select_image_directory(self):
        directory = filedialog.askdirectory(title="画像ディレクトリを選択してください")
        if directory:
            self.setting1_entry.delete(0, tk.END)
            self.setting1_entry.insert(0, directory)

    def select_data_directory(self):
        directory = filedialog.askdirectory(
            title="データディレクトリを選択してください"
        )
        if directory:
            self.setting2_entry.delete(0, tk.END)
            self.setting2_entry.insert(0, directory)

    def select_schedule_directory(self):
        directory = filedialog.askdirectory(
            title="スケジュールディレクトリを選択してください"
        )
        if directory:
            self.setting3_entry.delete(0, tk.END)
            self.setting3_entry.insert(0, directory)

    def ok_clicked(self):
        self.result = (
            self.setting1_entry.get(),
            self.setting2_entry.get(),
            self.setting3_entry.get(),
        )
        self.destroy()

    def cancel_clicked(self):
        self.result = None
        self.destroy()
