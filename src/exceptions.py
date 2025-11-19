"""
カスタム例外クラス定義モジュール
"""


class AOIApplicationError(Exception):
    """アプリケーション基底例外クラス"""
    pass


class ConfigurationError(AOIApplicationError):
    """設定関連のエラー"""
    pass


class DatabaseError(AOIApplicationError):
    """データベース関連のエラー"""
    pass


class KintoneAPIError(AOIApplicationError):
    """Kintone API関連のエラー"""
    pass


class FileOperationError(AOIApplicationError):
    """ファイル操作関連のエラー"""
    pass


class ValidationError(AOIApplicationError):
    """入力検証関連のエラー"""
    pass

