import tkinter as tk
from .repair_view import RepairView
from .aoi_view import AOIView  

class ModeView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mode View")
        # 画面中央に配置
        width = 300
        height = 200
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        self.label = tk.Label(self, text="工程選択", font=("Arial", 16))
        self.label.pack(pady=10)

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=10)
        self.create_buttons()

    def create_buttons(self):
        modes = [("AOI検査", self.on_manufacture), ("修理", self.on_inspect)]
        for mode, command in modes:
            button = tk.Button(self.button_frame, text=mode, command=command, width=15, height=2)
            button.pack(pady=5)
        
    def on_manufacture(self):
        print("AOI検査モードが選択されました。")
        self.withdraw()  # destroyではなく非表示にする
        app = AOIView(master=self)
        app.grab_set()   # 必要ならモーダルに
    
    def on_inspect(self):
        print("修理モードが選択されました。")
        self.withdraw()  # destroyではなく非表示にする
        app = RepairView(master=self)
        app.grab_set()   # 必要ならモーダルに

