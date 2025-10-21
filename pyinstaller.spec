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

# バイナリファイルの設定（pythonXX.dllを含める）
binaries = []

# Python DLLを明示的に含める
python_version = f"python{sys.version_info.major}{sys.version_info.minor}"
python_dll_name = f"{python_version}.dll"

# Python DLLの場所を探す（GitHub Actions対応）
import sysconfig
python_dll_paths = [
    Path(sys.executable).parent / python_dll_name,  # 標準的な場所
    Path(sysconfig.get_path('stdlib')).parent / python_dll_name,  # stdlib の親ディレクトリ
    Path(sys.prefix) / python_dll_name,  # sys.prefix
    Path(sys.base_prefix) / python_dll_name,  # sys.base_prefix (仮想環境対応)
    Path(sys.executable).parent.parent / python_dll_name,  # 仮想環境の親
    Path(os.environ.get('WINDIR', 'C:/Windows')) / 'System32' / python_dll_name,  # システムディレクトリ
]

# GitHub Actions環境での追加検索パス
if 'GITHUB_ACTIONS' in os.environ:
    # GitHub Actionsの特別なパス
    hostedtoolcache_python = os.environ.get('pythonLocation')
    if hostedtoolcache_python:
        python_dll_paths.insert(0, Path(hostedtoolcache_python) / python_dll_name)
        python_dll_paths.insert(1, Path(hostedtoolcache_python) / 'DLLs' / python_dll_name)
    
    print(f"GitHub Actions detected. Python location: {hostedtoolcache_python}")

python_dll_path = None
for dll_path in python_dll_paths:
    if dll_path.exists():
        python_dll_path = dll_path
        break

if python_dll_path:
    binaries.append((str(python_dll_path), '.'))
    print(f"Found Python DLL: {python_dll_path}")
else:
    print(f"Warning: {python_dll_name} not found in standard locations")
    print("Searched in:")
    for path in python_dll_paths:
        print(f"  - {path} ({'Found' if path.exists() else 'Not found'})")
    
    # 追加の検索ロジック（PATHとPYTHONPATH）
    for env_var in ['PATH', 'PYTHONPATH']:
        env_paths = os.environ.get(env_var, '').split(os.pathsep)
        for path in env_paths:
            if path:
                dll_candidate = Path(path) / python_dll_name
                if dll_candidate.exists():
                    binaries.append((str(dll_candidate), '.'))
                    python_dll_path = dll_candidate
                    print(f"Found Python DLL in {env_var}: {dll_candidate}")
                    break
        if python_dll_path:
            break

# 強制的にPython DLLを検索（最後の手段）
if not python_dll_path and sys.platform == 'win32':
    try:
        import ctypes
        import ctypes.util
        dll_handle = ctypes.util.find_library(python_version)
        if dll_handle:
            dll_path = Path(dll_handle)
            if dll_path.exists():
                binaries.append((str(dll_path), '.'))
                python_dll_path = dll_path
                print(f"Found Python DLL via ctypes: {dll_path}")
    except Exception as e:
        print(f"ctypes search failed: {e}")

if not python_dll_path:
    print(f"ERROR: Could not locate {python_dll_name}. Build may fail at runtime.")

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
    
    # データ処理関連 - Numpy/Pandas 依存関係を詳細に指定
    'pandas',
    'numpy',
    'numpy.core',
    'numpy.core._methods',
    'numpy.lib',
    'numpy.lib.format',
    'numpy.linalg',
    'numpy.random',
    'numpy._pytesttester',  # Pandasが必要とするnumpyテストモジュール
    'pandas.core',
    'pandas.core.api',
    'pandas.core.arrays',
    'pandas.io',
    'pandas.io.formats',
    'pandas.io.formats.format',
    'pandas.io.common',
    'pandas.plotting',
    'pandas._libs',
    'pandas._libs.tslibs',
    'pandas.compat',
    
    # HTTP関連
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
        # 32bit環境でのnumpy追加依存関係
        'numpy.distutils',
        'numpy.f2py',
        'numpy.testing',
        'numpy.testing._private',
        # 32bit環境でのpandas追加依存関係
        'pandas.util',
        'pandas.errors',
        'pandas.core.dtypes',
        'pandas.core.ops',
    ])
    print("Added 32bit specific hidden imports")

# 除外するモジュール
excludes = [
    # テスト関連モジュールを除外（但しnumpy._pytesttesterは除く）
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
    binaries=binaries,
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

# pure pythonモジュールから除外（但し必要なnumpyモジュールは保持）
def should_exclude(module_name):
    """モジュールを除外すべきかどうかを判定"""
    # numpy._pytesttesterは除外しない
    if 'numpy._pytesttester' in module_name:
        return False
    # pandas関連も除外しない
    if any(pandas_mod in module_name for pandas_mod in ['pandas.', 'numpy.core', 'numpy.lib', 'numpy.linalg']):
        return False
    # 除外リストに含まれているかチェック
    return any(excluded in module_name for excluded in excluded_modules)

a.pure = [item for item in a.pure if not should_exclude(item[0])]

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
print(f"  Python DLL: {python_dll_path if python_dll_path else 'Not found'}")
print(f"  Hidden imports: {len(hiddenimports)} modules")
print(f"  Data files: {len(datas)} files")
print(f"  Binary files: {len(binaries)} files")
print(f"  Excluded modules: {len(excludes)} modules")
print(f"  32bit optimizations: {'Enabled' if is_32bit else 'Disabled'}")
print(f"  Distribution directory: {dist_dir}")