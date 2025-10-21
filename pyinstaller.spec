# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification file for AOI Defect History
32bit/64bit Windows executable build configuration
"""

import sys
import os
import platform
from pathlib import Path

# プロジェクトルートディレクトリ
# GitHub Actionsでは__file__が定義されないため、os.getcwd()を使用
try:
    project_root = Path(__file__).parent
except NameError:
    project_root = Path(os.getcwd())

# ターゲットアーキテクチャの設定
target_arch = os.environ.get('TARGET_ARCH')
if target_arch == 'x64':
    arch = 'win64'
    is_32bit = False
elif target_arch == 'x86':
    arch = 'win32'
    is_32bit = True
else:
    # ローカルビルド時はシステムから判定
    if sys.maxsize > 2**32:
        arch = 'win64'
        is_32bit = False
    else:
        arch = 'win32'
        is_32bit = True

output_name = f'aoi-defect-history-{arch}'

print(f"Building for: {target_arch or 'auto-detected'} architecture")
print(f"Application name: {output_name}")
print(f"Platform: {platform.platform()}")
print(f"Is 32bit build: {is_32bit}")

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

# 隠しインポートの設定
hiddenimports = [
    # GUI関連
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.simpledialog',
    
    # PIL/Pillow関連
    'PIL',
    'PIL._tkinter_finder',
    'PIL.Image',
    'PIL.ImageTk',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    
    # データ処理関連
    'pandas',
    'numpy',
    'requests',
    
    # プロジェクト固有モジュール
    'aoi_data_manager',
    'aoi_data_manager.file_operations',
    'aoi_data_manager.api_client',
    'aoi_data_manager.models',
    'ktec_smt_schedule',
    'src.aoi_view',
    'src.mode_view',
    'src.repair_view',
    'src.dialog',
    'src.sub_window',
    'src.utils',
]

# 32bit環境での特別な設定
if is_32bit:
    # 32bit環境では一部のライブラリで問題が発生する可能性があるため、
    # より多くの依存関係を明示的に含める
    hiddenimports.extend([
        'psutil',
        'platform',
        'struct',
        'configparser',
        'pathlib',
        'threading',
        'concurrent.futures',
    ])
    print("Added 32bit specific hidden imports")

# 除外するモジュール
excludes = [
    # テスト関連モジュールを除外
    'pytest',
    '_pytest',
    'unittest',
    'test',
    'tests',
    
    # 不要なモジュールを除外
    'setuptools',
    'wheel',
    'pip',
    'distutils',
    
    # 開発ツールを除外
    'black',
    'autopep8',
    'yapf',
    
    # ドキュメント生成ツールを除外
    'pydoc',
    'doctest',
    
    # 不要な大きなライブラリ
    'matplotlib',
    'scipy',
    'sklearn',
    'tensorflow',
    'torch',
    'jupyter',
    'notebook',
    
    # その他不要なパッケージ
    'openpyxl',
    'yaml',
    'jinja2',
    'markupsafe',
    'colorama',
    'pygments',
]

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# 不要なモジュールを手動で除去
excluded_modules = excludes

# pure pythonモジュールから除外
a.pure = [item for item in a.pure if not any(excluded in item[0] for excluded in excluded_modules)]

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# アイコンファイルの設定
icon_file = project_root / 'assets' / 'icon.ico'
icon_path = str(icon_file) if icon_file.exists() else None

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
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=target_arch,  # GitHub Actionsで指定されたアーキテクチャを使用
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
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
dist_dir = project_root / "dist" / output_name
user_editable_files = ['defect_mapping.csv', 'user.csv']

# ディストリビューション後処理
def post_build_copy():
    """ビルド後にユーザー編集可能ファイルをコピー"""
    try:
        for filename in user_editable_files:
            src_file = project_root / filename
            if src_file.exists():
                dst_file = dist_dir / filename
                if not dst_file.exists():
                    with open(str(src_file), 'r', encoding='utf-8-sig') as f_src:
                        content = f_src.read()
                    with open(str(dst_file), 'w', encoding='utf-8-sig') as f_dst:
                        f_dst.write(content)
                    print(f"✓ Copied {filename} to distribution directory")
    except Exception as e:
        print(f"Warning: Could not copy user files: {e}")

# ビルド後処理を実行
post_build_copy()

# ビルド情報の出力
print(f"\nBuild completed:")
print(f"  Target architecture: {target_arch or 'auto-detected'}")
print(f"  Application name: {output_name}")
print(f"  Console mode: False")
print(f"  Icon file: {icon_path if icon_path else 'None'}")
print(f"  Hidden imports: {len(hiddenimports)} modules")
print(f"  Data files: {len(datas)} files")
print(f"  Excluded modules: {len(excludes)} modules")
print(f"  32bit optimizations: {'Enabled' if is_32bit else 'Disabled'}")
print(f"  Distribution directory: {dist_dir}")