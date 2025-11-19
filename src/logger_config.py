"""
ロギング設定モジュール
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

from .utils import get_project_dir


def setup_logger(name: str = "aoi_defect_history", log_level: int = logging.INFO) -> logging.Logger:
    """
    アプリケーション用のロガーを設定する
    
    Args:
        name (str): ロガー名
        log_level (int): ログレベル
    
    Returns:
        logging.Logger: 設定済みロガー
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # 既存のハンドラーをクリア（重複を防ぐ）
    logger.handlers.clear()
    
    # フォーマッターの設定
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # コンソールハンドラー（INFOレベル以上）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # ファイルハンドラー（DEBUGレベル以上、ローテーション付き）
    project_dir = get_project_dir()
    log_file = project_dir / "aoi_defect_history.log"
    
    try:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        # ログファイルの作成に失敗した場合は警告のみ
        logger.warning(f"ログファイルの作成に失敗しました: {e}")
    
    return logger


# アプリケーション全体で使用するロガーインスタンス
app_logger = setup_logger()

