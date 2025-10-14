from tkinter import simpledialog
import tkinter as tk


class ItemCodeChangeDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(
            master,
            text="データが取得できませんでした。新しい品目コードを入力してください。",
        ).grid(row=0, columnspan=2)

        # 品目コードエントリ
        tk.Label(master, text="品目コード:").grid(row=2, column=0, sticky="w")
        self.item_code_entry = tk.Entry(master)
        self.item_code_entry.grid(row=2, column=1, padx=5, pady=5)

        return self.item_code_entry  # 初期フォーカスをエントリに設定

    def apply(self):
        self.result = self.item_code_entry.get()
