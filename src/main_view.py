import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import ttk
from PIL import Image, ImageTk
import os
from datetime import datetime
from pandas import DataFrame

class MainView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AOI 製品経歴書")
        # 最大化表示
        self.option_add("*Background", "white")
        self.option_add("*Entry.Background", "white")
        self.option_add("*Label.Background", "white")
        self.state('zoomed')
        self.configure(bg="white")
        self.create_menu()
        self.create_header()
        self.create_defect_info_area()
        self.create_widgets_area()
        self.create_canvas_widgets()
        self.create_defect_list_widgets()

        # 現在の座標情報
        self.current_coordinates = None
        # 不具合リスト
        self.defect_list = []
        # 基板番号
        self.current_board_index = 1
        self.total_boards = 1
        self.update_board_label()

    def create_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Image", command=self.open_image)
        menubar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menubar)
    
    def create_header(self):
        # ヘッダーフレーム
        header_frame = tk.Frame(self, height=50)
        header_frame.pack(fill=tk.X,pady=10)
        
        # フォント（Yu Gothic UI, Meiryo, Segoe UI）
        font_title = ("Yu Gothic UI", 16, "bold")
        font_label = ("Yu Gothic UI", 12)
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
        # 機種名
        model_label = tk.Label(info_frame, text="機種名: ", font=font_label)
        model_label.pack(side=tk.LEFT, padx=10)
        model_label_value = tk.Label(info_frame,width=40, text="MA-E350/LAD REV.2#ECOMOTT", font=font_value, anchor="w")
        model_label_value.pack(side=tk.LEFT)
        # 基板名
        board_label = tk.Label(info_frame, text="基板名: ", font=font_label)
        board_label.pack(side=tk.LEFT, padx=10)
        board_label_value = tk.Label(info_frame, width=20, text="PL_KYM_AD集合基板", font=font_value, anchor="w")
        board_label_value.pack(side=tk.LEFT)
        # 指図
        lot_label = tk.Label(info_frame, text="指図: ", font=font_label)
        lot_label.pack(side=tk.LEFT, padx=10)
        lot_label_value = tk.Label(info_frame, width=12, text="1197949-10", font=font_value, anchor="w")
        lot_label_value.pack(side=tk.LEFT)

        # ユーザーフレーム
        user_frame = tk.Frame(right_frame)
        user_frame.pack(fill=tk.X,padx=10)

        # 下線のみ追加
        underline_user = tk.Frame(user_frame, bg="black", height=1)
        underline_user.pack(fill=tk.X, side=tk.BOTTOM)

        # AOI担当
        aoi_user_label = tk.Label(user_frame, text="AOI担当: ", font=font_label)
        aoi_user_label.pack(side=tk.LEFT, padx=10)
        aoi_user_label_value = tk.Label(user_frame, text="山田太郎", font=font_value, anchor="w", width=10)
        aoi_user_label_value.pack(side=tk.LEFT)

        # 精査担当
        inspect_user_label = tk.Label(user_frame, text="精査担当: ", font=font_label)
        inspect_user_label.pack(side=tk.LEFT, padx=10)
        inspect_user_label_value = tk.Label(user_frame, text="佐藤花子", font=font_value, anchor="w", width=10)
        inspect_user_label_value.pack(side=tk.LEFT)
    
    def create_defect_info_area(self):

        self.info_frame = tk.Frame(self)
        self.info_frame.pack(fill=tk.X, padx=10, pady=5)
        
         # 不良情報入力フレーム
        self.defect_info_frame = tk.LabelFrame(self.info_frame, text="不良情報入力", font=("Yu Gothic UI", 10))
        self.defect_info_frame.pack(side=tk.LEFT, padx=10)

        # 番号
        no_label = tk.Label(self.defect_info_frame, text="No: ", font=("Yu Gothic UI", 12))
        no_label.pack(side=tk.LEFT, padx=10)
        self.no_value = tk.Label(self.defect_info_frame, text="1", font=("Yu Gothic UI", 12), width=4)
        self.no_value.pack(side=tk.LEFT, padx=10)

        # リファレンス
        rf_label = tk.Label(self.defect_info_frame, text="リファレンス: ", font=("Yu Gothic UI", 12))
        rf_label.pack(side=tk.LEFT, padx=10) 
        self.rf_entry = tk.Entry(self.defect_info_frame, font=("Yu Gothic UI", 12))
        self.rf_entry.pack(side=tk.LEFT, padx=10)

        # 不良項目
        defect_label = tk.Label(self.defect_info_frame, text="不良項目: ", font=("Yu Gothic UI", 12))
        defect_label.pack(side=tk.LEFT, padx=10)
        self.defect_entry = tk.Entry(self.defect_info_frame, font=("Yu Gothic UI", 12))
        self.defect_entry.pack(side=tk.LEFT, padx=10)

        # 保存ボタン
        save_button = tk.Button(self.defect_info_frame, text="保存", font=("Yu Gothic UI", 10), command=self.save_defect_info)
        save_button.pack(side=tk.LEFT, padx=20, pady=5)

        # 削除ボタン
        delete_button = tk.Button(self.defect_info_frame, text="削除", font=("Yu Gothic UI", 10), command=self.delete_defect_info)
        delete_button.pack(side=tk.LEFT, padx=10, pady=5)

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
        self.defect_list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        # Treeviewの作成
        columns = ("No", "RF", "不良項目", "修理")
        self.defect_listbox = ttk.Treeview(self.defect_list_frame, columns=columns, show="headings")
        col_widths = {"No": 10, "RF": 30, "不良項目": 90, "修理": 10}
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
        filepath = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"), ("All Files", "*.*")]
        )
        if not filepath:
            return
        try:
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
            self.rf_entry.delete(0, tk.END)             # RFエントリをクリア
            self.rf_entry.insert(0, item_values[1])     # RFエントリに値を設定
            self.defect_entry.delete(0, tk.END) # 不良項目エントリをクリア
            self.defect_entry.insert(0, item_values[2]) # 不良項目エントリに値を設定
            index = int(item_values[0]) - 1 # Noは1始まりなので-1してインデックスに変換
            defect_item = self.defect_list[index]   # defect_listから選択中のアイテムを取得
            x, y = defect_item[4], defect_item[5]   # X, Y座標を取得
            
            # canvasに座標マーカーを表示
            if x is not None and y is not None:
                r = 5
                # 既存の座標マーカーを削除
                self.canvas.delete("coordinate_marker")
                # 新しい座標マーカーを追加
                self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="red", tags="coordinate_marker")
    
    def defect_number_update(self):
        filter_defect_list = [d for d in self.defect_list if d[0] == self.current_board_index]
        max_len = len(filter_defect_list)
        self.no_value.config(text=str(max_len + 1))

    def defect_list_insert(self, item: tuple):
        self.defect_list.append(item)
        self.defect_listbox.insert("", "end", values=[item[1], item[2], item[3]])
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

    def save_defect_info(self):
        insert_date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        current_board_index = self.current_board_index
        defect_number = self.no_value.cget("text")
        rf = self.rf_entry.get()
        defect = self.defect_entry.get()
        x, y = self.current_coordinates if self.current_coordinates else (None, None)
        if not rf or not defect:
            messagebox.showwarning("Warning", "RFと不良項目を入力してください。")
            return
        if x is None or y is None:
            messagebox.showwarning("Warning", "基板上の座標をクリックしてください。")
            return
        defect = (current_board_index, defect_number, rf, defect, x, y, insert_date)
        self.defect_list_insert(defect)
        # 入力エントリを初期化
        self.rf_entry.delete(0, tk.END)
        self.defect_entry.delete(0, tk.END)
        # 既存の座標マーカーを削除
        self.canvas.delete("coordinate_marker")
        
    def delete_defect_info(self):
        selected_item = self.defect_listbox.selection()
        if selected_item: 
            # Treeview内の全アイテムIDリスト
            items = self.defect_listbox.get_children()
            # インデックス（0始まり）
            index = items.index(selected_item[0])
            self.defect_list_delete(index, selected_item[0])
            self.rf_entry.delete(0, tk.END)
            self.defect_entry.delete(0, tk.END)
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
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="red", tags="coordinate_marker")
        
    def update_defect_listbox(self):
        # defect_listboxをdefect_listの内容で更新
        self.defect_listbox.delete(*self.defect_listbox.get_children())
        for item in self.defect_list:
            if self.current_board_index == item[0]:
                self.defect_listbox.insert("", "end", values=[item[1], item[2], item[3]])
        self.defect_number_update()

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
        path = "C:\\Users\\kentaroyoshida\\Documents\\image_coords_app"
        # defect_listを出力する
        df = DataFrame(self.defect_list, columns=["board_index", "No", "RF", "不良項目", "X", "Y", "日付"])
        # CSVとして保存
        df.to_csv(os.path.join(path, "defect_list.csv"), index=False, encoding="utf-8-sig")
        self.current_board_index = self.current_board_index + 1
        self.total_boards = max(self.total_boards, self.current_board_index)
        self.update_board_label()
        # treeviewを初期化
        self.update_defect_listbox()
        self.defect_number_update()

    def update_board_label(self):
        self.board_no_label.config(text=f"{self.current_board_index} / {self.total_boards} 枚")