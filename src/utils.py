"""
ユーティリティ関数モジュール
"""

import os
import sys
from pathlib import Path, PurePath

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


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


def load_env_file():
    """
    .envファイルを読み込む

    実行時環境に応じて適切な.envファイルパスから環境変数を読み込む
    """
    if load_dotenv is None:
        return

    if getattr(sys, "frozen", False):
        # PyInstaller実行ファイルの場合
        # 実行ファイルと同じディレクトリの.envファイルを読み込む
        env_path = Path(sys.executable).parent / ".env"
    else:
        # 開発環境の場合
        # プロジェクトルートの.envファイルを読み込む
        env_path = get_project_dir() / ".env"

    if env_path.exists():
        load_dotenv(dotenv_path=env_path)


def sanitize_file_path(file_path: str, base_directory: str = None) -> Path:
    """
    ファイルパスをサニタイズして、パストラバーサル攻撃を防止する

    Args:
        file_path (str): 検証するファイルパス
        base_directory (str, optional): ベースディレクトリ。指定された場合、このディレクトリ内のパスのみ許可

    Returns:
        Path: サニタイズされたパス

    Raises:
        ValueError: パストラバーサル攻撃が検出された場合
        PermissionError: ベースディレクトリ外へのアクセスが試みられた場合
    """
    # パスを正規化
    normalized_path = PurePath(file_path)

    # パストラバーサル攻撃のチェック（.. を含むパス）
    if ".." in str(normalized_path):
        raise ValueError(f"パストラバーサル攻撃の可能性があります: {file_path}")

    # ベースディレクトリが指定されている場合、その中に含まれるかチェック
    if base_directory:
        target_path = Path(base_directory) / normalized_path
        base_path = Path(base_directory).resolve()
        try:
            # パスがベースディレクトリ内にあるか確認
            target_path.relative_to(base_path)
        except ValueError:
            raise PermissionError(
                f"ベースディレクトリ外へのアクセスは許可されていません: {file_path}"
            )

        return target_path
    else:
        return Path(normalized_path)


def validate_directory_path(directory_path: str) -> Path:
    """
    ディレクトリパスを検証してサニタイズする

    Args:
        directory_path (str): 検証するディレクトリパス

    Returns:
        Path: サニタイズされたディレクトリパス

    Raises:
        ValueError: 無効なパスの場合
    """
    if not directory_path or not directory_path.strip():
        raise ValueError("ディレクトリパスが空です")

    sanitized = sanitize_file_path(directory_path)

    # ディレクトリが存在するか確認（必須ではないが警告として）
    if not sanitized.exists():
        # 存在しない場合でもエラーにはしない（作成される可能性があるため）
        pass

    return sanitized


class Utils:
    @staticmethod
    def create_repaird_csv_path(data_directory: str, current_lot_number: str) -> str:
        """指図に対応する修理データCSVファイル名を生成"""
        if not current_lot_number:
            raise ValueError("Current lot number is not set.")
        if not data_directory:
            raise ValueError("Not Setting Data Directory")
        filename = f"{current_lot_number}_repaird_list.csv"
        # ファイルパスをサニタイズ
        sanitized_dir = validate_directory_path(data_directory)
        return str(sanitized_dir / filename)
