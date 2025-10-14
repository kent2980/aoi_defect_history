from tkinter import simpledialog
import tkinter as tk


class ChangeUserDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="新しいユーザーIDを入力してください。").grid(
            row=0, columnspan=2
        )

        # ユーザーエントリ
        tk.Label(master, text="ユーザーID:").grid(row=1, column=0, sticky="w")
        self.user_entry = tk.Entry(master)
        self.user_entry.grid(row=1, column=1, padx=5, pady=5)

        return self.user_entry  # 初期フォーカスをエントリに設定

    def apply(self):
        self.result = self.user_entry.get()
