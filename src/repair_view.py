import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import ttk
from PIL import Image, ImageTk
import os
from datetime import datetime
from pandas import DataFrame
from pathlib import Path
import configparser
import pandas as pd
import re
from dataclasses import asdict
from typing import List
from .defect_info import DefectInfo
from .repaird_info import RepairdInfo

PROJECT_DIR = Path(__file__).parent.parent


class RepairView(tk.Toplevel):
    def __init__(self, fillColor = "white", master=None):
        super().__init__(master)
        self.title("AOI 製品経歴書")
        # 最大化表示
        self.option_add("*Background", "white")
        self.option_add("*Entry.Background", "white")
        self.option_add("*Label.Background", "white")
        self.state('zoomed')
        self.configure(bg="white")

        # 座標の塗りつぶし色
        self.fillColor = fillColor

        # ディレクトリ設定
        self.image_directory = None
        self.data_directory = None

        # 設定読み込み
        self.__read_settings()

        # UI描画
        self.create_menu()
        self.create_header()
        self.create_defect_info_area()
        self.create_widgets_area()
        self.create_canvas_widgets()
        self.create_defect_list_widgets()

        # 現在の座標情報
        self.current_coordinates = None
        
        # リスト
        self.defect_list:List[DefectInfo] = []
        self.repaird_list:List[RepairdInfo] = []

        # 基板番号
        self.current_board_index = 1
        self.total_boards = 1
        self.update_board_label()

        # 品目コード,指図,画像パス
        self.current_item_code = None
        self.current_lot_number = None
        self.current_image_path = None
        self.current_image_filename = None

        # ユーザー名
        self.user_name = None

        # ユーザー切り替え
        self.change_user()

    def __read_settings(self):
        """ """
        settings_path = PROJECT_DIR / "settings.ini"
        if settings_path.exists():
            # 設定ファイルを読み込み
            config = configparser.ConfigParser()
            config.read(settings_path, encoding="utf-8")
            # 例: 画像ディレクトリとデータディレクトリを取得
            self.image_directory = config['DIRECTORIES'].get('image_directory', '')
            self.data_directory = config['DIRECTORIES'].get('data_directory', '')

    def create_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="画像を開く", command=self.open_image)
        menubar.add_cascade(label="ファイル", menu=file_menu)
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="設定", command=self.open_settings)
        menubar.add_cascade(label="設定", menu=settings_menu)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="不良名一覧", command=self.show_defect_mapping)
        menubar.add_cascade(label="ヘルプ", menu=help_menu)
        self.config(menu=menubar)
    
    def create_header(self):
        # ヘッダーフレーム
        header_frame = tk.Frame(self, height=50)
        header_frame.pack(fill=tk.X,pady=10)
        
        # フォント（Yu Gothic UI, Meiryo, Segoe UI）
        font_title = ("Yu Gothic UI", 16, "bold")
        font_label = ("Yu Gothic UI", 10)
        font_value = ("Yu Gothic UI", 10)
        
        # タイトルラベル
        title_label = tk.Label(header_frame, text="AOI 製品経歴書", font=font_title, relief="solid", borderwidth=1)
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
        info_frame.pack(fill=tk.X,padx=10)
        
        # 下線のみ追加
        underline = tk.Frame(info_frame, bg="black", height=1)
        underline.pack(fill=tk.X, side=tk.BOTTOM)
        
        # ロット切り替えボタン
        lot_change_button = tk.Button(info_frame, text="指図切替", font=("Yu Gothic UI", 8), command=self.change_lot)
        lot_change_button.pack(side=tk.LEFT, padx=5, pady=[0,2])
        
        # 機種名
        model_label = tk.Label(info_frame, text="機種名: ", font=font_label)
        model_label.pack(side=tk.LEFT, padx=10)
        self.model_label_value = tk.Label(info_frame,width=30, font=font_value, anchor="w")
        self.model_label_value.pack(side=tk.LEFT)
        
        # 基板名
        board_label = tk.Label(info_frame, text="基板名: ", font=font_label)
        board_label.pack(side=tk.LEFT, padx=10)
        self.board_label_value = tk.Label(info_frame, width=15, font=font_value, anchor="w")
        self.board_label_value.pack(side=tk.LEFT)

        # 面
        side_label = tk.Label(info_frame, text="面: ", font=font_label)
        side_label.pack(side=tk.LEFT, padx=10)
        self.side_label_value = tk.Label(info_frame, width=5, font=font_value, anchor="w")
        self.side_label_value.pack(side=tk.LEFT)
        
        # 指図
        lot_label = tk.Label(info_frame, text="指図: ", font=font_label)
        lot_label.pack(side=tk.LEFT, padx=10)
        self.lot_label_value = tk.Label(info_frame, width=12, font=font_value, anchor="w")
        self.lot_label_value.pack(side=tk.LEFT)

        # ユーザーフレーム
        user_frame = tk.Frame(right_frame)
        user_frame.pack(fill=tk.X,padx=10)

        # 下線のみ追加
        underline_user = tk.Frame(user_frame, bg="black", height=1)
        underline_user.pack(fill=tk.X, side=tk.BOTTOM)

        # ユーザー切り替えボタン
        user_change_button = tk.Button(user_frame, text="ユーザー切替", font=("Yu Gothic UI", 8), command=self.change_user)
        user_change_button.pack(side=tk.LEFT, padx=5, pady=[0,2])

        # AOI担当
        aoi_user_label = tk.Label(user_frame, text="AOI担当: ", font=font_label)
        aoi_user_label.pack(side=tk.LEFT, padx=10)
        self.aoi_user_label_value = tk.Label(user_frame, font=font_value, anchor="w", width=10)
        self.aoi_user_label_value.pack(side=tk.LEFT)

        # 修理担当
        repair_user_label = tk.Label(user_frame, text="修理担当: ", font=font_label)
        repair_user_label.pack(side=tk.LEFT, padx=10)
        self.repair_user_label_value = tk.Label(user_frame, font=font_value, anchor="w", width=10)
        self.repair_user_label_value.pack(side=tk.LEFT)

        # 目視担当
        inspect_user_label = tk.Label(user_frame, text="目視担当: ", font=font_label)
        inspect_user_label.pack(side=tk.LEFT, padx=10)
        self.inspect_user_label_value = tk.Label(user_frame, font=font_value, anchor="w", width=10)
        self.inspect_user_label_value.pack(side=tk.LEFT)

    def create_defect_info_area(self):

        self.info_frame = tk.Frame(self)
        self.info_frame.pack(fill=tk.X, padx=10, pady=5)
        
         # 不良情報入力フレーム
        self.defect_info_frame = tk.LabelFrame(self.info_frame, text="不良情報入力", font=("Yu Gothic UI", 10))
        self.defect_info_frame.pack(side=tk.LEFT, padx=40)

        # 番号
        no_label = tk.Label(self.defect_info_frame, text="No: ", font=("Yu Gothic UI", 12))
        no_label.pack(side=tk.LEFT, padx=10)
        self.no_value = tk.Label(self.defect_info_frame, text="1", font=("Yu Gothic UI", 12), width=4)
        self.no_value.pack(side=tk.LEFT, padx=10)

        # リファレンス
        rf_label = tk.Label(self.defect_info_frame, text="リファレンス: ", font=("Yu Gothic UI", 12))
        rf_label.pack(side=tk.LEFT, padx=10) 
        self.rf_entry = tk.Label(self.defect_info_frame, font=("Yu Gothic UI", 12), width=10, anchor="w")
        self.rf_entry.pack(side=tk.LEFT, padx=10)

        # 不良項目
        defect_label = tk.Label(self.defect_info_frame, text="不良項目: ", font=("Yu Gothic UI", 12))
        defect_label.pack(side=tk.LEFT, padx=10)
        self.defect_entry = tk.Label(self.defect_info_frame, font=("Yu Gothic UI", 12), width=15, anchor="w")
        self.defect_entry.pack(side=tk.LEFT, padx=10)

        # 分類
        parts_type_label = tk.Label(self.defect_info_frame, text="分類: ", font=("Yu Gothic UI", 12))
        parts_type_label.pack(side=tk.LEFT, padx=10)
        self.parts_type_entry = tk.Label(self.defect_info_frame, font=("Yu Gothic UI", 12), width=6, anchor="w")
        self.parts_type_entry.pack(side=tk.LEFT, padx=10)

        # 「C/R」ボタン
        chip_button = tk.Button(self.defect_info_frame, text="C/R", font=("Yu Gothic UI", 10), command=self.on_chip_button)
        chip_button.pack(side=tk.LEFT, padx=5, pady=5)

        # 「異形」ボタン
        other_button = tk.Button(self.defect_info_frame, text="異形", font=("Yu Gothic UI", 10), command=self.on_other_button)
        other_button.pack(side=tk.LEFT, padx=5, pady=5)

        # 修理済みボタン
        repair_button = tk.Button(self.defect_info_frame, text="修理済み", font=("Yu Gothic UI", 10), command=self.on_repaired)
        repair_button.pack(side=tk.LEFT, padx=5, pady=5)

        # 基板操作フレーム
        board_control_frame = tk.LabelFrame(self.info_frame, text="基板切替", font=("Yu Gothic UI", 10))
        board_control_frame.pack(side=tk.RIGHT, padx=[0, 50])
        
        # 基板Noラベル
        self.board_no_label = tk.Label(board_control_frame, text="1 / 1 枚", font=("Yu Gothic UI", 12))
        self.board_no_label.pack(side=tk.LEFT, padx=[5, 5])
        # 前の基板ボタン
        prev_board_button = tk.Button(board_control_frame, text="<< 前へ", font=("Yu Gothic UI", 10), command=self.prev_board)
        prev_board_button.pack(side=tk.LEFT, padx=[10,5], pady=5)


        # 次の基板ボタン
        next_board_button = tk.Button(board_control_frame, text="次へ >>", font=("Yu Gothic UI", 10), command=self.next_board)
        next_board_button.pack(side=tk.LEFT, padx=[5, 10], pady=5)

    def create_widgets_area(self):
        self.widgets_frame = tk.Frame(self)
        self.widgets_frame.pack(fill=tk.X, expand=True, padx=10)

    def create_canvas_widgets(self):
        self.canvas = tk.Canvas(self.widgets_frame, bg="white",width=900, height=450)
        self.canvas.pack(side=tk.LEFT, expand=True)
        # 左クリック処理をバインド
        self.canvas.bind("<Button-1>", self.on_canvas_click)
    
    def create_defect_list_widgets(self):
        self.defect_list_frame = tk.Frame(self.widgets_frame)
        self.defect_list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=10)
        # Treeviewの作成
        columns = ("No", "RF", "不良項目", "分類", "修理")
        self.defect_listbox = ttk.Treeview(self.defect_list_frame, columns=columns, show="headings")
        col_widths = {"No": 10, "RF": 30, "不良項目": 90, "分類": 15, "修理": 15}
        for col in columns:
            self.defect_listbox.heading(col, text=col)
            self.defect_listbox.column(col, width=col_widths[col], anchor="center")
        # TreeviewとScrollbarをFrame内で横並びに配置
        self.defect_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(self.defect_list_frame, orient=tk.VERTICAL, command=self.defect_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.defect_listbox.configure(yscrollcommand=scrollbar.set)
        # Treeviewの選択イベントをバインド
        self.defect_listbox.bind("<<TreeviewSelect>>", self.on_defect_select)


    def open_image(self):
        """ 画像を開くダイアログを表示し、選択された画像をcanvasに表示 """
        filepath = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"), ("All Files", "*.*")]
        )
        if not filepath:
            return
        try:
            self.current_image_path = filepath
            image = Image.open(filepath)
            image.thumbnail((self.canvas.winfo_width(), self.canvas.winfo_height()))
            self.photo_image = ImageTk.PhotoImage(image)
            self.canvas.delete("all")
            self.canvas.create_image(self.canvas.winfo_width()//2, self.canvas.winfo_height()//2, image=self.photo_image, anchor="center")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image:\n{e}")

    def open_select_image(self, filepath: str):
        """ 指定されたファイルパスの画像をcanvasに表示 """
        if not filepath:
            return
        try:
            self.current_image_path = filepath
            image = Image.open(filepath)
            image.thumbnail((self.canvas.winfo_width(), self.canvas.winfo_height()))
            self.photo_image = ImageTk.PhotoImage(image)
            self.canvas.delete("all")
            self.canvas.create_image(self.canvas.winfo_width()//2, self.canvas.winfo_height()//2, image=self.photo_image, anchor="center")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image:\n{e}")

    def on_defect_select(self, event):
        """ defect_listboxで選択されたアイテムの情報をエントリに表示し、canvasに座標マーカーを表示 """
        # 選択中のアイテムを取得
        selected_item = self.defect_listbox.selection()
        if selected_item:
            # 選択中のアイテムの値を取得
            item_values = self.defect_listbox.item(selected_item[0], "values")
            self.no_value.config(text=item_values[0])   # No列を表示
            self.rf_entry.config(text=item_values[1])     # RFエントリに値を設定
            self.defect_entry.config(text=item_values[2])     # 不良項目エントリに値を設定
            index = int(item_values[0]) - 1 # Noは1始まりなので-1してインデックスに変換
            defect_item = self.defect_list[index]   # defect_listから選択中のアイテムを取得
            x, y = defect_item.x, defect_item.y   # X, Y座標を取得
            
            # canvasに座標マーカーを表示
            if x is not None and y is not None:
                r = 5
                # 既存の座標マーカーを削除
                self.canvas.delete("coordinate_marker")
                # 新しい座標マーカーを追加
                self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=self.fillColor, tags="coordinate_marker")
    
    def defect_number_update(self):
        filter_defect_list = [d for d in self.defect_list if d.current_board_index == self.current_board_index]
        max_len = len(filter_defect_list)
        self.no_value.config(text=str(max_len + 1))

    def defect_list_insert(self, item: DefectInfo):
        self.defect_list.append(item)
        print(item)
        self.defect_listbox.insert("", "end", values=[item.defect_number, item.reference, item.defect_name, "", ""])
        self.defect_number_update()
        print("[DEBUG] Current Defect List:")
        for item in self.defect_list:
            print(item)

    def defect_list_delete(self, index, tree_index: str):
        del self.defect_list[index]
        self.defect_listbox.delete(tree_index)
        self.defect_listbox_no_reset()
        self.defect_number_update()
        # canvasの座標マーカーを削除
        self.canvas.delete("coordinate_marker")
        print("[DEBUG] Current Defect List after deletion:")
        for item in self.defect_list:
            print(item)
    
    def read_defect_list_csv(self, filepath: str):
        """ CSVファイルから不良リストを読み込み、defect_listに設定 """
        try:
            df = DataFrame(pd.read_csv(filepath))
            self.defect_list = [DefectInfo(**row) for row in df.to_dict(orient="records")]
            self.update_defect_listbox()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read defect list from CSV:\n{e}")
        
    def defect_listbox_no_reset(self):
        # self.defect_listboxのNo列を再設定
        for idx, item in enumerate(self.defect_listbox.get_children(), start=1):
            values = list(self.defect_listbox.item(item, "values"))
            values[0] = idx
            self.defect_listbox.item(item, values=values)
        # self.defect_listのNo列を再設定
        for idx, item in enumerate(self.defect_list, start=1):
            self.defect_list[idx - 1] = (str(idx),) + item[1:]

    def on_canvas_click(self, event):
        # canvasに画像がない場合は何もしない
        if not hasattr(self, 'photo_image'):
            return
        # 不具合情報を初期化
        self.rf_entry.delete(0, tk.END)
        self.defect_entry.delete(0, tk.END)
        self.defect_number_update()
        # クリック位置の座標を取得
        x, y = event.x, event.y
        self.current_coordinates = (x, y)
        # クリック位置に小さな円を描画
        r = 5
        # 既存の座標マーカーを削除
        self.canvas.delete("coordinate_marker")
        # 新しい座標マーカーを追加
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=self.fillColor, tags="coordinate_marker")
        
    def update_defect_listbox(self):
        # defect_listboxをdefect_listの内容で更新
        self.defect_listbox.delete(*self.defect_listbox.get_children())
        for item in self.defect_list:
            if self.current_board_index == item.current_board_index:
                self.defect_listbox.insert("", "end", values=[item.defect_number, item.reference, item.defect_name, "", ""], tags=item.unique_id)
        self.defect_number_update()
    
    def update_index(self):
        items = self.defect_list
        # itemsから1つ目の要素をlistで取得
        indices = [item.current_board_index for item in items if isinstance(item.current_board_index, int)]
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
        if self.current_board_index == self.total_boards:
            messagebox.showinfo("Info", "これ以上次の基板はありません。")
            return
        if not self.current_image_filename:
            raise ValueError("Current image filename is not set.")
        # 不良リストをCSVに保存
        self.defect_list_to_csv()
        # 画面を更新
        self.current_board_index = self.current_board_index + 1
        self.total_boards = max(self.total_boards, self.current_board_index)
        self.update_board_label()
        # treeviewを初期化
        self.update_defect_listbox()
        self.defect_number_update()
    
    def defect_list_to_csv(self):
        """ defect_listをCSVファイルに保存 """
        try:
            df = DataFrame([asdict(item) for item in self.defect_list])
            basename = self.create_csv_filename()
            df.to_csv(os.path.join(self.data_directory, basename), index=False, encoding="utf-8-sig")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save defect list to CSV:\n{e}")

    def update_board_label(self):
        self.board_no_label.config(text=f"{self.current_board_index} / {self.total_boards} 枚")

    def create_csv_filename(self):
        """ 指図に対応するCSVファイル名を生成 """
        if not self.current_lot_number:
            raise ValueError("Current lot number is not set.")
        if not self.current_image_filename:
            raise ValueError("Current image filename is not set.")
        return f"{self.current_lot_number}_{self.current_image_filename}.csv"

    def read_csv_path(self):
        """ 指図に対応するCSVファイルのパスを取得 """
        if not self.current_image_filename:
            raise ValueError("Current image filename is not set.")
        csv_filename = self.create_csv_filename()
        csv_path = os.path.join(self.data_directory, csv_filename)
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        return csv_path

    def open_settings(self):
        """ 設定ダイアログを開く """
        dialog = SettingsDialog(self)
        new_settings = dialog.result
        project_dir = PROJECT_DIR
        print(f"[DEBUG] Project Directory: {project_dir}")
        if new_settings:
            # 新しい設定を適用
            self.image_directory = new_settings[0]
            self.data_directory = new_settings[1]
            # 設定ファイルが存在しない場合は新規作成
            settings_path = project_dir / "settings.ini"
            if not settings_path.exists():
                # 新しい設定を保存
                config = configparser.ConfigParser()
                config['DIRECTORIES'] = {
                    'image_directory': new_settings[0],
                    'data_directory': new_settings[1]
                }
                with open(settings_path, "w", encoding="utf-8") as configfile:
                    config.write(configfile)
            
            messagebox.showinfo("Info", f"新しい設定: {new_settings[0]}, {new_settings[1]} に変更されました。")
        else:
            messagebox.showinfo("Info", "設定の変更がキャンセルされました。")

    def change_lot(self):
        """ 品目コードと指図を変更するダイアログを開く """

        # ユーザーが未設定の場合は警告を表示して終了
        if not self.is_set_user():
            messagebox.showwarning("Warning", "AOI担当が設定されていません。ユーザーを設定してください。")
            return

        # 品目コードと指図を入力するダイアログを表示
        dialog = LotChangeDialog(self)
        if not hasattr(dialog, 'result') or not dialog.result:
            messagebox.showinfo("Info", "品目コードと指図の変更がキャンセルされました。")
            return
            
        self.current_item_code = dialog.result[0].upper()
        self.current_lot_number = dialog.result[1]

        if self.is_validation_lot_name(self.current_lot_number) is False:
            messagebox.showwarning("Warning", "指図の形式が不正です。例: 1234567-10")
            self.current_item_code = None
            self.current_lot_number = None
            return

        # 画像ディレクトリからitem_codeから始まる画像を探して表示
        if self.image_directory and self.current_item_code:
            for filename in os.listdir(self.image_directory):
                if filename.startswith(self.current_item_code):
                    self.current_image_path = os.path.join(self.image_directory, filename)
                    self.open_select_image(self.current_image_path)
                    break
            # 画像が見つからなかった場合
            if not self.current_image_path:
                self.current_image_path = None
                self.current_item_code = None
                self.current_lot_number = None
                messagebox.showwarning("Warning", "指定された品目コードに対応する画像が見つかりません。")
                return

        # 画像名から機種情報を取得
        if self.current_image_path:
            baseName = os.path.basename(self.current_image_path).split(".")[0]
            self.current_image_filename = baseName
            parts = baseName.split('_')
            model_name = parts[1] if len(parts) > 1 else ""
            board_name = parts[2] if len(parts) > 2 else ""
            side_label = parts[3] if len(parts) > 3 else ""

        # 指図に対応するCSVファイルのパスを取得
        try:
            csv_path = self.read_csv_path()
        except FileNotFoundError:
            self.current_item_code = None
            self.current_lot_number = None
            self.current_image_path = None
            self.current_image_filename = None
            self.canvas.delete("all")
            self.defect_list = []
            messagebox.showwarning("Warning", "指定された品目コードと指図に対応するCSVファイルが見つかりません。")
            return

        # 各ラベルを更新
        self.model_label_value.config(text=model_name)
        self.board_label_value.config(text=board_name)
        self.side_label_value.config(text=side_label)
        self.lot_label_value.config(text=self.current_lot_number)

        try:
            # csvパスの取得
            csv_path = self.read_csv_path()
            # csvパスが取得できたら不良リストを読み込み
            if csv_path:
                self.current_board_index = 1
                self.read_defect_list_csv(csv_path)
                self.update_index()
                self.update_board_label()
                self.defect_number_update()
                self.aoi_user_label_value.config(text=self.defect_list[0].aoi_user)
        except FileNotFoundError as e:
            # 不良リストを初期化
            self.defect_list = []
            self.update_defect_listbox()
            self.update_index()
            self.update_board_label()
            self.defect_number_update()

        if not (self.current_lot_number and self.current_item_code):
            messagebox.showinfo("Info", "品目コードと指図の変更がキャンセルされました。")
            return
    
    def create_repaird_list(self):
        if len(self.defect_list) == 0:
            raise ValueError("Defect list is empty.")
        for defect in self.defect_list:
            self.repaird_list.append(RepairdInfo(
                id=defect.unique_id,
            ))

    def is_validation_lot_name(self, lot_name: str) -> bool:
        """ 指図名のバリデーション """
        if not lot_name:
            return False
        regex = r'^\d{7}-10$|^\d{7}-20$'
        return bool(re.match(regex, lot_name))

    def change_user(self):
        """ ユーザー名を変更するダイアログを開く """
        dialog = ChangeUserDialog(self)
        if not hasattr(dialog, 'result') or not dialog.result:
            messagebox.showinfo("Info", "ユーザー名の変更がキャンセルされました。")
            return
        user_id = dialog.result.upper()

        # user.csvをDataFrameで読み込み
        user_csv_path = PROJECT_DIR / "user.csv"
        if not user_csv_path.exists():
            raise FileNotFoundError(f"user.csv not found at {user_csv_path}")
        df = pd.read_csv(user_csv_path)
        user_ids = df['id'].tolist()
        # user_ids内の要素を文字列に変換
        user_ids = [str(uid) for uid in user_ids]
        if user_id not in user_ids:
            messagebox.showerror("Error", f"ユーザーID: {user_id} は存在しません。")
            return
        # ユーザーIDに対応する名前を取得

        matching_rows = df.loc[df['id'] == user_id, 'name']
        if matching_rows.empty:
            messagebox.showerror("Error", f"ユーザーID: {user_id} は存在しません。")
            return
        self.user_name = matching_rows.values[0]
        # AOI担当ラベルを更新
        self.repair_user_label_value.config(text=self.user_name)
    
    def is_set_user(self) -> bool:
        """ ユーザー名が設定されているか確認 """
        user = self.repair_user_label_value.cget("text")
        return bool(user)

    def convert_defect_name(self):
        """ 不良項目名を変換する """
        defect_number = self.defect_entry.get()
        if not defect_number:
            return
        # defect_numberがintに変換できない場合は例外をスロー
        if not defect_number.isdigit():
            print(f"[DEBUG] Defect number '{defect_number}' is not a valid integer.")
            return
        defect_number = int(defect_number)
        # defect_mapping.csvをDataFrameで読み込み
        mapping_csv_path = PROJECT_DIR / "defect_mapping.csv"
        if not mapping_csv_path.exists():
            raise FileNotFoundError(f"defect_mapping.csv not found at {mapping_csv_path}")
        df = pd.read_csv(mapping_csv_path)
        # defect_numberがdfの'alias'列に存在するか確認
        if defect_number in df['no'].values:
            # 対応する'name'列の値を取得してエントリに設定
            standard_name = df.loc[df['no'] == defect_number, 'name'].values[0]
            self.defect_entry.delete(0, tk.END)
            self.defect_entry.insert(0, standard_name)
    
    def show_defect_mapping(self):
        """ 不良名一覧を表示する """
        mapping_csv_path = PROJECT_DIR / "defect_mapping.csv"
        if not mapping_csv_path.exists():
            raise FileNotFoundError(f"defect_mapping.csv not found at {mapping_csv_path}")
        df = pd.read_csv(mapping_csv_path)
        df = df.dropna()
        # dfのno列をfloatだった場合にintに変換
        df['no'] = df['no'].apply(lambda x: int(x) if isinstance(x, float) and x.is_integer() else x)
        mapping_text = "\n".join([f"{row['no']}: {row['name']}" for _, row in df.iterrows()])
        messagebox.showinfo("不良名一覧", mapping_text)

    def on_repaired(self):
        """ 修理済みボタンが押されたときの処理 """
        selected_item = self.defect_listbox.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "修理済みにする不良項目を選択してください。")
            return
        item_values = self.defect_listbox.item(selected_item[0], "values")
        item_tags = self.defect_listbox.item(selected_item[0], "tags")
        repaird = item_values[4]
        if repaird == "":
            repaird = "済"
        elif repaird == "済":
            repaird = ""
        # Treeviewの選択中のアイテムの修理列を更新
        self.defect_listbox.item(selected_item[0], values=(item_values[0], item_values[1], item_values[2], item_values[3], repaird))
        
    def on_chip_button(self):
        """ C/Rボタンが押されたときの処理 """
        selected_item = self.defect_listbox.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "C/Rにする不良項目を選択してください。")
            return
        item_values = self.defect_listbox.item(selected_item[0], "values")
        self.defect_listbox.item(selected_item[0], values=(item_values[0], item_values[1], item_values[2], "C/R", item_values[4]))
        # 分類ラベルを更新
        self.parts_type_entry.config(text="C/R")

    def on_other_button(self):
        """ 異形ボタンが押されたときの処理 """
        selected_item = self.defect_listbox.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "異形にする不良項目を選択してください。")
            return
        item_values = self.defect_listbox.item(selected_item[0], "values")
        self.defect_listbox.item(selected_item[0], values=(item_values[0], item_values[1], item_values[2], "異形", item_values[4]))
        # 分類ラベルを更新
        self.parts_type_entry.config(text="異形")

class LotChangeDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="新しい品目コードと指図を入力してください。").grid(row=0, columnspan=2)
        
        # 品目コードエントリ
        tk.Label(master, text="品目コード:").grid(row=1, column=0, sticky="w")
        self.item_code_entry = tk.Entry(master)
        self.item_code_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # 指図エントリ
        tk.Label(master, text="指図:").grid(row=2, column=0, sticky="w")
        self.lot_entry = tk.Entry(master)
        self.lot_entry.grid(row=2, column=1, padx=5, pady=5)

        # Enterキーでlot_entryにフォーカスを移動
        self.item_code_entry.bind("<Return>", self.on_enter)
        
        return self.item_code_entry  # 初期フォーカスをエントリに設定

    def apply(self):
        self.result = self.item_code_entry.get(), self.lot_entry.get()

    def on_enter(self, event):
        self.lot_entry.focus_set()  # lot_entryにフォーカスを移動
        return "break"  # イベントの伝播を停止

class SettingsDialog(simpledialog.Dialog):

    def __init__(self, parent):
        self.__read_settings()
        super().__init__(parent, title="設定")
    
    def __read_settings(self):
        project_dir = PROJECT_DIR
        settings_path = project_dir / "settings.ini"
        if settings_path.exists():
            config = configparser.ConfigParser()
            config.read(settings_path, encoding="utf-8")
            self.current_image_directory = config['DIRECTORIES'].get('image_directory', '')
            self.current_data_directory = config['DIRECTORIES'].get('data_directory', '')
        else:
            self.current_image_directory = ''
            self.current_data_directory = ''

    def body(self, master):
        tk.Label(master, text="データの保存場所を指定してください。").grid(row=0, columnspan=3, pady=10)
        
        # 画像ディレクトリ設定
        tk.Label(master, text="画像ディレクトリ:").grid(row=1, column=0, sticky="w")
        self.setting1_entry = tk.Entry(master, width=50)
        self.setting1_entry.grid(row=1, column=1, padx=5, pady=5)
        self.setting1_entry.insert(0, self.current_image_directory)
        tk.Button(master, text="参照", command=self.select_image_directory).grid(row=1, column=2, padx=5)
        
        # データディレクトリ設定
        tk.Label(master, text="データディレクトリ:").grid(row=2, column=0, sticky="w")
        self.setting2_entry = tk.Entry(master, width=50)
        self.setting2_entry.grid(row=2, column=1, padx=5, pady=5)
        self.setting2_entry.insert(0, self.current_data_directory)
        tk.Button(master, text="参照", command=self.select_data_directory).grid(row=2, column=2, padx=5)
        
        return self.setting1_entry  # 初期フォーカスをエントリに設定

    def select_image_directory(self):
        directory = filedialog.askdirectory(title="画像ディレクトリを選択してください")
        if directory:
            self.setting1_entry.delete(0, tk.END)
            self.setting1_entry.insert(0, directory)

    def select_data_directory(self):
        directory = filedialog.askdirectory(title="データディレクトリを選択してください")
        if directory:
            self.setting2_entry.delete(0, tk.END)
            self.setting2_entry.insert(0, directory)

    def apply(self):
        self.result = self.setting1_entry.get(), self.setting2_entry.get()

class ChangeUserDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="新しいユーザーIDを入力してください。").grid(row=0, columnspan=2)
        
        # ユーザーエントリ
        tk.Label(master, text="ユーザーID:").grid(row=1, column=0, sticky="w")
        self.user_entry = tk.Entry(master)
        self.user_entry.grid(row=1, column=1, padx=5, pady=5)
        
        return self.user_entry  # 初期フォーカスをエントリに設定

    def apply(self):
        self.result = self.user_entry.get()