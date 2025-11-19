from repository import AoiRepository
from typing import List, Dict
from aoi_data_manager import DefectInfo

from src.context import AoiContext


class AoiService:
    repository: AoiRepository
    defect_list: List[DefectInfo]
    delete_defect_ids: List[str]
    serial_dict: Dict[int, str]
    current_context: AoiContext
