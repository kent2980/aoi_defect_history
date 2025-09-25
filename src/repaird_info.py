from dataclasses import dataclass

@dataclass
class RepairdInfo:
    """
    修理済み情報を保持するデータクラス
    attributes:
        id: str - 不良情報の一意なID
        is_repaird: bool - 修理済みフラグ（デフォルトはFalse）
        parts_type: str - 部品分類（チップ/異形）
    """
    id: str 
    is_repaird: str = "未修理"
    parts_type: str = ""
    insert_date: str = ""