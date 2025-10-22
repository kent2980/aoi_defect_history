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

from src import AOIView


def main():
    """メインエントリーポイント"""
    try:
        # ルートウィンドウを作成（非表示）
        root = tk.Tk()
        root.withdraw()  # ルートウィンドウは非表示

        # AOIViewを作成（UIはまだ作成されない）
        aoi_view = None

        def initialize_aoi_view():
            """メインループ開始後にAOIViewを初期化"""
            nonlocal aoi_view
            aoi_view = AOIView(master=root, fillColor="red")

            # AOIViewが閉じられたらアプリケーション終了
            def on_aoi_close():
                root.quit()
                root.destroy()

            aoi_view.protocol("WM_DELETE_WINDOW", on_aoi_close)

        # メインループ開始後にAOIViewを初期化
        root.after(100, initialize_aoi_view)

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
