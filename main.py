import sys
import tkinter as tk
from pathlib import Path

# 実行時パスの設定
if getattr(sys, "frozen", False):
    # PyInstallerでビルドされた実行ファイルの場合
    PROJECT_DIR = Path(sys.executable).parent
    # 埋め込まれたリソースパス
    RESOURCE_DIR = Path(sys._MEIPASS)
else:
    # 通常のPythonスクリプトの場合
    PROJECT_DIR = Path(__file__).parent
    RESOURCE_DIR = PROJECT_DIR

# モジュールパスの追加
sys.path.append(str(PROJECT_DIR / "src"))

from src import ModeView


def main():
    """メインエントリーポイント"""
    try:
        root = tk.Tk()
        root.withdraw()  # メインウィンドウを非表示

        # モード選択画面を表示
        mode_view = ModeView(master=root)

        # アプリケーション開始
        root.mainloop()

    except Exception as e:
        import traceback

        error_msg = f"アプリケーション開始エラー:\n{str(e)}\n\n{traceback.format_exc()}"

        # エラーログファイルに出力
        error_log_path = PROJECT_DIR / "error.log"
        try:
            with open(error_log_path, "w", encoding="utf-8") as f:
                f.write(error_msg)
        except:
            pass

        # エラーダイアログ表示（可能であれば）
        try:
            import tkinter.messagebox as messagebox

            messagebox.showerror(
                "エラー", f"アプリケーションでエラーが発生しました。\n\n{str(e)}"
            )
        except:
            print(error_msg)

        sys.exit(1)


if __name__ == "__main__":
    main()
