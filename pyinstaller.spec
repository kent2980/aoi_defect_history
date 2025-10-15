# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# プロジェクトルートディレクトリ
# GitHub Actionsでは__file__が定義されないため、os.getcwd()を使用
try:
    project_root = Path(__file__).parent
except NameError:
    project_root = Path(os.getcwd())

# アーキテクチャの判定
# GitHub Actionsから環境変数を取得、なければシステムから判定
target_arch = os.environ.get('TARGET_ARCH')
if target_arch == 'x64':
    arch = 'win64'
elif target_arch == 'x86':
    arch = 'win32'
else:
    # ローカルビルド時はシステムから判定
    arch = 'win64' if sys.maxsize > 2**32 else 'win32'
output_name = f'aoi-defect-history-{arch}'

# データファイルの設定（実行ファイルに埋め込むもの）
datas = []
embedded_files = [
    'settings.ini',
    'kintone_settings.ini'
]

for data_file in embedded_files:
    data_path = project_root / data_file
    if data_path.exists():
        datas.append((str(data_path), '.'))

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'pandas',
        'requests',
        'aoi_data_manager',
        'aoi_data_manager.file_operations',
        'aoi_data_manager.api_client',
        'aoi_data_manager.models',
        'ktec_smt_schedule',
        'json',
        'datetime',
        'uuid',
        'configparser',
        'threading',
        'pathlib',
        'os',
        're',
        'dataclasses',
        'typing',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=output_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUIアプリケーションなのでコンソールを非表示
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # アイコンファイルがあれば指定: 'path/to/icon.ico'
)

# COLLECTを使用してディレクトリ形式でパッケージ作成
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=output_name,
)

# ユーザー編集可能ファイルを外部に配置
import shutil
import codecs
dist_dir = project_root / "dist" / output_name
user_editable_files = ['defect_mapping.csv', 'user.csv']

for filename in user_editable_files:
    src_file = project_root / filename
    if src_file.exists():
        dst_file = dist_dir / filename
        if not dst_file.exists():
            # UTF-8エンコーディングでファイルを読み込んで書き込み
            try:
                with open(str(src_file), 'r', encoding='utf-8') as f_src:
                    content = f_src.read()
                with open(str(dst_file), 'w', encoding='utf-8', newline='') as f_dst:
                    f_dst.write(content)
                print(f"Copied {filename} with UTF-8 encoding")
            except UnicodeDecodeError:
                # UTF-8で読み込めない場合はShift_JISで試行
                try:
                    with open(str(src_file), 'r', encoding='shift_jis') as f_src:
                        content = f_src.read()
                    with open(str(dst_file), 'w', encoding='utf-8', newline='') as f_dst:
                        f_dst.write(content)
                    print(f"Copied {filename} with Shift_JIS to UTF-8 encoding")
                except Exception as e:
                    print(f"Error copying {filename}: {e}")
                    # フォールバック: バイナリコピー
                    shutil.copy2(str(src_file), str(dst_file))