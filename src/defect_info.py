from dataclasses import dataclass
from uuid import uuid5, NAMESPACE_DNS


@dataclass
class DefectInfo:
    """
    不良情報を保持するデータクラス
    attributes:
        id: str - 不良情報の一意なID（自動生成）
        insert_date: str - 登録日時
        model_code: str - Y番
        model_name: str - 機種名
        lot_number: str - 指図
        current_board_index: int - 現在の基板インデックス
        defect_number: str - 不良番号
        serial: str - 基板シリアル番号
        reference: str - リファレンス番号
        defect_name: str - 不良名称
        x: int - X座標
        y: int - Y座標
        aoi_user: str - AOIユーザー名
    """

    id: str = ""
    model_code: str = ""
    lot_number: str = ""
    current_board_index: int = 0
    defect_number: str = ""
    serial: str = ""
    reference: str = ""
    defect_name: str = ""
    x: int = 0
    y: int = 0
    aoi_user: str = ""
    insert_date: str = ""
    kintone_record_id: str = ""

    def __post_init__(self):
        # idが未設定なら自動生成
        if not self.id:
            values = f"{self.model_code}_{self.lot_number}_{self.current_board_index}_{self.defect_number}"
            self.id = str(uuid5(NAMESPACE_DNS, values))
