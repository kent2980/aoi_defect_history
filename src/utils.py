import os

class Utils:
    @staticmethod
    def create_repaird_csv_path(data_directory: str, current_lot_number: str) -> str:
        """ 指図に対応する修理データCSVファイル名を生成"""
        if not current_lot_number:
            raise ValueError("Current lot number is not set.")
        if not data_directory:
            raise ValueError("Not Setting Data Directory")
        filename = f"{current_lot_number}_repaird_list.csv"
        return os.path.join(data_directory, filename)