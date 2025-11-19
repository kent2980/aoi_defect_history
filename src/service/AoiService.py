from PIL.Image import logger
from repository import AoiRepository
from typing import List, Dict
from aoi_data_manager import DefectInfo, FileManager

from src.context import AoiContext
from src.dialog.item_code_change_dialog import ItemCodeChangeDialog
from src.dialog.lot_change_dialog import LotChangeDialog
from src.sub_window.settings_window import PROJECT_DIR
from src.utils import sanitize_file_path, validate_directory_path
from src.constants import MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT
from tkinter import messagebox
from datetime import datetime, timezone
import tkinter as tk
import os


class AoiService:
    repository: AoiRepository
    defect_list: List[DefectInfo]
    delete_defect_ids: List[str]
    serial_dict: Dict[int, str]
    current_context: AoiContext

    def __init__(self, repository: AoiRepository):
        self.repository = repository
        self.defect_list = []
        self.delete_defect_ids = []
        self.serial_dict = {}
        self.current_context = AoiContext()

    def save_defect_info(self) -> None:
        """保存ボタンを押したときの処理"""

        # データディレクトリが有効か確認
        if not self.exist_data_directory():
            messagebox.showerror(
                "Error",
                "データディレクトリに接続できませんでした。ネットワークへの接続を確認してください。",
            )
            return

        # 不良番号を不良名に変換
        self.convert_defect_name()
        # 各種情報を取得
        insert_date = datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )  # 登録日時
        current_board_index = self.current_board_index  # 現在の基板番号
        defect_number = self.no_value.cget("text")  # 不良番号
        rf = self.rf_entry.get().upper()  # リファレンス
        defect_name = self.defect_entry.get()  # 不良項目
        aoi_user = self.aoi_user_label_value.cget("text")  # AOI担当
        model_code = self.current_item_code if self.current_item_code else ""
        lot_number = self.current_lot_number if self.current_lot_number else ""
        model_name = self.model_label_value.cget("text")
        board_name = self.board_label_value.cget("text")
        side_label = self.side_label_value.cget("text")
        model_label = model_name + " " + board_name
        board_label = model_label + " " + side_label
        board_number_label = f"{lot_number}_{current_board_index}"
        serial = self.serial_dict.get(self.current_board_index, "")

        # 相対座標を取得（既に相対座標として保存されている）
        rel_x, rel_y = (
            self.current_coordinates if self.current_coordinates else (None, None)
        )

        # 入力チェック
        if not rf or not defect_name:
            messagebox.showwarning("Warning", "RFと不良項目を入力してください。")
            return
        if rel_x is None or rel_y is None:
            messagebox.showwarning("Warning", "基板上の座標をクリックしてください。")
            return

        # defect_listに追加（相対座標で保存）
        defect = DefectInfo(
            line_name=self.current_line_name,
            current_board_index=current_board_index,
            defect_number=defect_number,
            reference=rf,
            defect_name=defect_name,
            x=rel_x,  # 相対座標（0.0～1.0）
            y=rel_y,  # 相対座標（0.0～1.0）
            insert_datetime=insert_date,
            serial=serial,
            aoi_user=aoi_user,
            model_code=model_code,
            lot_number=lot_number,
            model_label=model_label,
            board_label=board_label,
            board_number_label=board_number_label,
        )

        if self.exists_defect_listbox(defect_number):
            self.defect_list_update(defect_number, defect)
        else:
            self.defect_list_insert(defect)

        # 座標画像を生成出力
        image_path = ""
        if self.data_directory:
            # ファイルパスをサニタイズ
            sanitized_data_dir = validate_directory_path(self.data_directory)
            output_dir_path = sanitized_data_dir / lot_number
            output_dir: str = str(output_dir_path)
            if not output_dir_path.exists():
                output_dir_path.mkdir(
                    parents=True, exist_ok=True
                )  # ディレクトリがなければ作成
            filename = f"{lot_number}_{current_board_index}_{defect_number}"
            try:
                image_path = FileManager.export_canvas_image_with_markers(
                    defect,
                    self.current_image_path,
                    output_dir,
                    filename,
                    marker_size=20,
                    font_size=12,
                    max_image_size=(MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT),
                    text_area_width=160,
                )
                success_msg = f"画像を保存しました: {image_path}"
                self.safe_update_status(success_msg)
            except ValueError as e:
                self.update_status(e)

        # defectにimage_pathを設定
        defect.image_path = image_path

        if self.exists_defect_listbox(defect_number):
            self.defect_list_update(defect_number, defect)
        else:
            self.defect_list_insert(defect)

        # 入力エントリを初期化
        self.rf_entry.delete(0, tk.END)
        self.defect_entry.delete(0, tk.END)

        # 既存の座標マーカーを削除
        self.canvas.delete("coordinate_marker")

        # クラウドファースト構成: Kintone APIに優先的に登録
        self.post_kintone_record_async(self.defect_list)

        # ローカルSQLiteにキャッシュとして登録（オフライン対応）
        self.__insert_defect_info_to_db_async(self.defect_list)

    def delete_defect_info(self) -> None:
        """削除ボタンを押したときの動作"""
        # 選択中のアイテムを取得
        selected_item = self.defect_listbox.focus()
        if selected_item:
            # Treeview内の全アイテムIDリスト
            items = self.defect_listbox.item(selected_item, "values")
            # 削除するアイテムのIDを取得
            remove_id = items[3]
            # defect_listから削除対象のアイテムを取得
            defect_item = [item for item in self.defect_list if item.id == remove_id][0]
            # ツリーからアイテムを削除
            self.defect_listbox.delete(selected_item)
            # リファレンス入力エリアを初期化
            self.rf_entry.delete(0, tk.END)
            # 不良名入力エリアを初期化
            self.defect_entry.delete(0, tk.END)
            # defect_listから対象のID要素を削除
            self.defect_list = [
                item for item in self.defect_list if item.id != remove_id
            ]
            # 画像を削除
            if self.data_directory:
                # ファイルパスをサニタイズ
                sanitized_data_dir = validate_directory_path(self.data_directory)
                output_dir_path = sanitized_data_dir / defect_item.lot_number
                output_dir: str = str(output_dir_path)
                filename = (
                    f"{defect_item.lot_number}_{defect_item.current_board_index}_"
                    f"{defect_item.defect_number}"
                )
                try:
                    msg = FileManager.delete_exported_image(output_dir, filename)
                    self.update_status(msg)
                except ValueError as e:
                    self.update_status(e)
            # defect_listの不良番号を振りなおす
            defect_index = None
            board_index = None
            for item in self.defect_list:
                if board_index != item.current_board_index:
                    board_index = item.current_board_index
                    defect_index = 1
                # 画像ファイルをリネーム
                ext = "png"
                # ファイルパスをサニタイズ
                sanitized_data_dir = validate_directory_path(self.data_directory)
                lot_dir = sanitized_data_dir / item.lot_number
                oldName = f"{item.lot_number}_{item.current_board_index}_{item.defect_number}.{ext}"
                old_path = lot_dir / oldName
                newName = (
                    f"{item.lot_number}_{item.current_board_index}_{defect_index}.{ext}"
                )
                newPath = lot_dir / newName
                # パストラバーサル攻撃を防ぐため、パスがlot_dir内にあることを確認
                if (
                    old_path.parent.resolve() == lot_dir.resolve()
                    and newPath.parent.resolve() == lot_dir.resolve()
                ):
                    os.rename(str(old_path), str(newPath))
                else:
                    raise ValueError("パストラバーサル攻撃が検出されました")
                # defect_numberを変更
                item.defect_number = defect_index
                defect_index = defect_index + 1
            # 削除IDリストに追加
            self.delete_defect_ids.append(remove_id)
            # kintoneからレコードを削除
            self.delete_kintone_record_async(defect_item.kintone_record_id)
            # データベースから削除
            self.__remove_defect_info_from_db_async(defect_item)
            # クラウドファースト構成: Kintone APIに優先的に更新
            self.post_kintone_record_async(self.defect_list)
            # ローカルSQLiteにキャッシュとして更新
            self.__insert_defect_info_to_db_async(self.defect_list)
            # ツリーのインデックスを振りなおす
            index = 1
            for item_id in self.defect_listbox.get_children():
                values = list(
                    self.defect_listbox.item(item_id, "values")
                )  # タプル→リストに変換（変更しやすいように）
                values[0] = str(index)
                self.defect_listbox.item(item_id, values=values)
                index = index + 1

            messagebox.showinfo("Info", "不良情報を削除しました。")
        else:
            messagebox.showwarning("Warning", "リストから不良情報を選択してください。")

    def change_lot(self):
        """指図変更処理"""

        # ユーザーが未設定の場合は警告を表示して終了
        if not self.is_set_user():
            messagebox.showwarning(
                "Warning", "AOI担当が設定されていません。ユーザーを設定してください。"
            )
            return

        # クラウドファースト構成: Kintone APIに優先的に送信
        if len(self.defect_list) > 0:
            try:
                self.post_kintone_record_async(self.defect_list)
            except ValueError as e:
                logger.error(f"API送信エラー: {e}", exc_info=True)
                messagebox.showerror("送信エラー", f"API送信エラー:{e}")

        # ローカルSQLiteにキャッシュとして保存（オフライン対応）
        if len(self.defect_list) > 0:
            self.__insert_defect_info_to_db_async(self.defect_list)

        # すべての座標マーカーを削除
        self.canvas.delete("all")

        # データリストを事前に初期化
        self.defect_list = []
        self.repaird_list = []
        self.current_coordinates = None

        # 指図を入力するダイアログを表示
        dialog = LotChangeDialog(self)
        if not hasattr(dialog, "result") or not dialog.result:
            messagebox.showinfo("Info", "指図の変更がキャンセルされました。")
            return

        # 指図を取得
        self.current_lot_number = dialog.result

        # 指図形式のバリデーション
        if self.is_validation_lot_name(self.current_lot_number) is False:
            messagebox.showwarning("Warning", "指図の形式が不正です。例: 1234567-10")
            self.current_item_code = None
            self.current_lot_number = None
            return

        # item_code, line_nameを取得する
        schedule_item = self.__search_schedule_df_item(self.current_lot_number)

        # schedule_itemが見つからない場合
        if not schedule_item:
            messagebox.showwarning("Warning", "SMT計画表に指図が見つかりません。")
            self.current_item_code = None
            self.current_lot_number = None
            return

        self.current_item_code = schedule_item.get("model_code")
        self.current_line_name = schedule_item.get("machine_name")

        # item_codeが見つからなかった場合
        if not self.current_item_code:
            # アイテムコード入力ダイアログを表示
            itemDialog = ItemCodeChangeDialog(self)
            if not hasattr(itemDialog, "result") or not itemDialog.result:
                messagebox.showinfo("Info", "品目コードの入力がキャンセルされました。")
                self.current_item_code = None
                self.current_lot_number = None
                return
            # 入力されたitem_codeを設定
            self.current_item_code = itemDialog.result.upper()

        # 画像ディレクトリからitem_codeから始まる画像を探して表示
        try:
            # ファイルパスをサニタイズ
            sanitized_image_dir = validate_directory_path(self.image_directory)
            filename = FileManager.get_image_path(
                str(sanitized_image_dir),
                self.current_lot_number,
                self.current_item_code,
            )
            # ファイル名もサニタイズ（パストラバーサル対策）
            sanitized_filename = sanitize_file_path(filename, str(sanitized_image_dir))
            self.current_image_path = str(sanitized_filename)

            # 画像表示（defect_listが空であることを確認済み）
            self.open_select_image(self.current_image_path)
        except FileNotFoundError as e:
            # 画像が見つからなかった場合
            if not self.current_image_path:
                self.current_image_path = None
                self.current_item_code = None
                self.current_lot_number = None
                messagebox.showwarning(
                    "Warning", "指定された品目コードに対応する画像が見つかりません。"
                )
                return
        except ValueError:
            # ロットナンバーの形式が不正な場合
            messagebox.showwarning("Warning", "指図の形式が不正です。例: 1234567-10")
            self.current_item_code = None
            self.current_lot_number = None
            return

        # 画像名から機種情報を取得
        if self.current_image_path:
            baseName = os.path.basename(self.current_image_path).split(".")[0]
            self.current_image_filename = baseName
            try:
                parts = FileManager.parse_image_filename(baseName)
                model_name = parts[0]
                board_name = parts[1]
                side_label = parts[2]
            except ValueError:
                # 画像名の形式が不正な場合,エラーメッセージを表示
                messagebox.showwarning(
                    "Warning",
                    "画像ファイル名の形式が不正です。正しい設定例: Y8470722R_20_CN-SNDDJ0CJ_411CA_S面.jpg",
                )
                return

        # 各ラベルを更新
        self.line_label_value.delete(0, tk.END)
        self.line_label_value.insert(0, self.current_line_name or "")
        self.model_label_value.config(text=model_name)
        self.board_label_value.config(text=board_name)
        self.side_label_value.config(text=side_label)
        self.lot_label_value.config(text=self.current_lot_number)

        # ステータスバーの更新
        self.update_status(
            f"品目コード: {self.current_item_code}、指図: {self.current_lot_number} に変更されました。"
        )

        try:
            # csvパスの取得
            csv_path = self.read_csv_path()
            # csvパスが取得できたら不良リストを読み込み
            if csv_path:
                # 基板番号を初期化
                self.current_board_index = 1
                # データベースからdefectListを読み込む
                self.read_defect_list_db()
                # defectListからserial_dictを作成
                self.create_serial_dict(self.defect_list)
                self.update_index()
                self.update_board_label()
                self.defect_number_update()
        except FileNotFoundError as e:
            # FileNotFoundExceptionの場合も明示的に空にする
            self.defect_list = []
            self.repaird_list = []
            self.update_defect_listbox()
            self.update_index()
            self.update_board_label()
            self.defect_number_update()

        if not (self.current_lot_number and self.current_item_code):
            messagebox.showinfo(
                "Info", "品目コードと指図の変更がキャンセルされました。"
            )
            return

        # クラウドファースト構成では共有SQLiteデータベースへのマージは不要
        # すべてのデータはKintone APIに保存されます

    def on_serial_enter(self, event):
        """シリアルエントリでEnterキーが押されたときの処理"""
        # 現在の基板インデックスを取得
        board_index = self.current_board_index
        serial = self.serial_entry.get()
        # defect_list内の該当基板インデックスのシリアルを更新
        for item in self.defect_list:
            if item.current_board_index == board_index:
                # シリアル番号を更新
                item.serial = serial
        # シリアルを保存
        self.serial_dict[self.current_board_index] = serial
        # シリアルエントリの内容をクリア
        self.serial_entry.delete(0, tk.END)
        # ステータスバーを更新
        self.update_status(f"シリアル番号を更新しました: {serial}")
        # クラウドファースト構成: Kintone APIに優先的に更新
        self.post_kintone_record_async(self.defect_list)
        # ローカルSQLiteにキャッシュとして更新
        self.__insert_defect_info_to_db_async(self.defect_list)

    def convert_defect_name(self):
        """不良項目名を変換する"""
        defect_number = self.defect_entry.get()
        if not defect_number or not defect_number.isdigit():
            return

        defect_number = int(defect_number)
        mapping_csv_path = PROJECT_DIR / "defect_mapping.csv"

        try:
            df = FileManager.read_defect_mapping(str(mapping_csv_path))
            if defect_number in df["no"].values:
                standard_name = df.loc[df["no"] == defect_number, "name"].values[0]
                self.defect_entry.delete(0, tk.END)
                self.defect_entry.insert(0, standard_name)
        except Exception as e:
            logger.error(f"不良名変換エラー: {e}", exc_info=True)

    def create_serial_dict(self, defect_list: List[DefectInfo]):
        """defectListからシリアル辞書を作成する"""
        self.serial_dict = {}
        for item in defect_list:
            self.serial_dict[item.current_board_index] = item.serial

    def remove_existing_defect_ids_from_delete_list(self):
        """
        self.defect_list内のidがself.delete_defect_idsに存在する場合、
        self.delete_defect_idsから削除する

        Returns:
            int: 削除されたIDの数
        """
        if not self.delete_defect_ids:
            return 0

        # defect_listから全てのidを取得（存在するIDのセット）
        existing_ids = {defect.id for defect in self.defect_list if defect.id}

        # delete_defect_idsから存在するIDをフィルタリング（削除対象を特定）
        ids_to_remove = [
            defect_id
            for defect_id in self.delete_defect_ids
            if defect_id in existing_ids
        ]

        # 削除対象のIDをdelete_defect_idsから除外
        for defect_id in ids_to_remove:
            self.delete_defect_ids.remove(defect_id)

        # 削除件数をログ出力
        if ids_to_remove:
            removed_count = len(ids_to_remove)
            return removed_count

        return 0

    def exist_data_directory(self):
        """データディレクトリが存在するか確認"""
        if not self.data_directory or not os.path.exists(self.data_directory):
            return False
        return True
