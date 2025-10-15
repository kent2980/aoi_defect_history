# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# プロジェクトルートディレクトリ
project_root = Path(__file__).parent

# アーキテクチャの判定
arch = 'win64' if sys.maxsize > 2**32 else 'win32'
output_name = f'aoi-defect-history-{arch}'

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        ('defect_mapping.csv', '.'),
        ('user.csv', '.'),
        ('settings.ini', '.'),
        ('kintone_settings.ini', '.'),
    ],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=output_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUIアプリケーションなのでコンソールを非表示
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # アイコンファイルがあれば指定: 'path/to/icon.ico'
)