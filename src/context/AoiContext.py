from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from aoi_data_manager import DefectInfo


@dataclass
class AoiContext:
    """AOI画面の業務状態をまとめて扱うためのコンテキスト"""

    lot_number: Optional[str] = None
    item_code: Optional[str] = None
    line_name: Optional[str] = None
    board_index: int = 1
    total_boards: int = 1
    user_name: Optional[str] = None
    defect_list: List[DefectInfo] = field(default_factory=list)
    delete_defect_ids: List[str] = field(default_factory=list)
    serial_dict: Dict[int, str] = field(default_factory=dict)
    last_updated_at: Optional[datetime] = None

    def mark_updated(self) -> None:
        """状態更新タイムスタンプを記録"""
        self.last_updated_at = datetime.utcnow()
