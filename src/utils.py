"""
ユーティリティ関数モジュール
"""

import os
import sys
from pathlib import Path


def get_project_dir():
    """
    プロジェクトディレクトリを取得する

    実行時環境（開発環境 vs PyInstaller実行ファイル）に応じて
    適切なディレクトリパスを返す

    Returns:
        Path: プロジェクトディレクトリのパス
    """
    if getattr(sys, "frozen", False):
        # PyInstaller実行ファイルの場合
        # 実行ファイルと同じディレクトリを返す
        return Path(sys.executable).parent
    else:
        # 開発環境の場合
        # このファイルの親の親ディレクトリ（プロジェクトルート）を返す
        return Path(__file__).parent.parent


def get_csv_file_path(filename):
    """
    CSVファイルのパスを取得する

    実行時環境に応じて適切なCSVファイルパスを返す
    - 開発環境: プロジェクトルート直下
    - 実行ファイル: 実行ファイルと同じディレクトリ

    Args:
        filename (str): CSVファイル名

    Returns:
        Path: CSVファイルのパス
    """
    project_dir = get_project_dir()
    return project_dir / filename


def get_config_file_path(filename):
    """
    設定ファイルのパスを取得する

    実行時環境に応じて適切な設定ファイルパスを返す

    Args:
        filename (str): 設定ファイル名

    Returns:
        Path: 設定ファイルのパス
    """
    if getattr(sys, "frozen", False):
        # PyInstaller実行ファイルの場合
        # 実行ファイル内に埋め込まれているファイルを参照
        # sys._MEIPASSは一時展開ディレクトリ
        return Path(sys._MEIPASS) / filename
    else:
        # 開発環境の場合
        project_dir = get_project_dir()
        return project_dir / filename


class Utils:
    @staticmethod
    def create_repaird_csv_path(data_directory: str, current_lot_number: str) -> str:
        """指図に対応する修理データCSVファイル名を生成"""
        if not current_lot_number:
            raise ValueError("Current lot number is not set.")
        if not data_directory:
            raise ValueError("Not Setting Data Directory")
        filename = f"{current_lot_number}_repaird_list.csv"
        return os.path.join(data_directory, filename)
