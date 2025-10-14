from tkinter import simpledialog
import tkinter as tk


class LotChangeDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="新しい指図を入力してください。").grid(
            row=0, columnspan=2
        )

        # 指図エントリ
        tk.Label(master, text="指図:").grid(row=2, column=0, sticky="w")
        self.lot_entry = tk.Entry(master)
        self.lot_entry.grid(row=2, column=1, padx=5, pady=5)

        return self.lot_entry  # 初期フォーカスをエントリに設定

    def apply(self):
        self.result = self.lot_entry.get()
