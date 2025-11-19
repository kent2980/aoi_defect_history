from pathlib import Path
from aoi_data_manager import (
    FileManager,
    KintoneClient,
    SqlOperations,
)


class AoiRepository:

    settings_path: Path
    sqlite_dir: Path
    sqlite_ops: SqlOperations | None
    kintone_client: KintoneClient | None
    schedule_directory: Path | None
    file_manager: FileManager
    image_root: Path
