# 32bit Windows向けセットアップ手順

このドキュメントでは、32bit Windows向けの実行ファイルをビルドするためのセットアップ手順を説明します。

## 📋 前提条件

### 必要な環境

- **OS**: Windows 7 SP1以降（32bit版）
- **メモリ**: 2GB以上推奨（最低1GB）
- **ディスク**: 1GB以上の空き容量
- **Python**: 3.11（32bit版）

### 必要なソフトウェア

1. **Python 3.11 (32bit版)**
   - 公式サイト: https://www.python.org/downloads/
   - バージョン: 3.11.x（32bit版を選択）
   - インストール時に「Add Python to PATH」にチェックを入れる

2. **uv (パッケージマネージャー)**
   - インストール方法: `pip install uv`

## 🔧 セットアップ手順

### ステップ1: Python 32bit版のインストール確認

```powershell
# Pythonのバージョンとアーキテクチャを確認
python --version
python -c "import struct; print(f'Python {struct.calcsize(\"P\") * 8}bit')"
```

**期待される出力:**
```
Python 3.11.x
Python 32bit
```

⚠️ **重要**: 64bit Pythonが表示される場合は、32bit Pythonをインストールする必要があります。

### ステップ2: プロジェクトのクローン/ダウンロード

```powershell
# プロジェクトディレクトリに移動
cd C:\path\to\aoi_defect_history
```

### ステップ3: 依存関係のインストール

```powershell
# uvを使用して依存関係をインストール
uv sync

# または、pipを使用する場合
pip install -e .
```

### ステップ4: 32bit環境の検証

```powershell
# 32bit環境検証スクリプトを実行
python scripts/verify_32bit_setup.py
```

このスクリプトは以下を確認します：
- Pythonのアーキテクチャ（32bit/64bit）
- 依存関係の32bit対応バージョン
- 必要なライブラリのインストール状況
- メモリ制約の確認

### ステップ5: 環境変数の設定（オプション）

```powershell
# 32bitビルドを明示的に指定
$env:TARGET_ARCH = "x86"
```

## 🏗️ ビルド手順

### 方法1: バッチファイルを使用（推奨）

```powershell
# 32bitビルド
.\build_32bit.bat

# または、64bitビルド
.\build_64bit.bat

# または、自動判定
.\build.bat
```

### 方法2: 手動ビルド

```powershell
# 環境変数を設定
$env:TARGET_ARCH = "x86"

# PyInstallerでビルド
uv run pyinstaller --clean --noconfirm pyinstaller.spec
```

### 方法3: Pythonスクリプトを使用

```powershell
# 32bitビルドテスト
python build_test.py
```

## ✅ ビルド結果の確認

ビルドが成功すると、以下のディレクトリに実行ファイルが作成されます：

```
dist/
└── aoi-defect-history-win32/
    ├── aoi-defect-history-win32.exe
    ├── defect_mapping.csv
    ├── user.csv
    └── _internal/
        └── (実行時ライブラリ)
```

### 実行ファイルの確認

```powershell
# ファイルサイズの確認
Get-Item dist\aoi-defect-history-win32\aoi-defect-history-win32.exe | Select-Object Name, Length

# 実行テスト（オプション）
.\dist\aoi-defect-history-win32\aoi-defect-history-win32.exe
```

## 🧪 テスト実行

### 32bit互換性テスト

```powershell
# 全テストを実行
python tests/run_32bit_tests.py

# 個別テスト
python tests/test_32bit_compatibility.py
python tests/test_32bit_performance.py
python tests/validate_32bit_config.py
```

## ⚠️ よくある問題と解決方法

### 問題1: 64bit Pythonが検出される

**症状:**
```
Python 64bit
```

**解決方法:**
1. 32bit Pythonをインストール
2. 環境変数PATHで32bit Pythonを優先
3. 仮想環境を再作成

```powershell
# 32bit Pythonのパスを確認
where python

# 仮想環境を再作成
Remove-Item -Recurse -Force .venv
uv sync
```

### 問題2: 依存関係のインストールエラー

**症状:**
```
ERROR: Could not find a version that satisfies the requirement numpy==1.24.3
```

**解決方法:**
1. 32bit対応バージョンを確認
2. 依存関係を個別にインストール

```powershell
# 32bit対応バージョンを確認
pip index versions numpy
pip index versions pandas

# 個別インストール
pip install "numpy==1.24.3"
pip install "pandas==2.0.3"
```

### 問題3: メモリ不足エラー

**症状:**
```
MemoryError: Unable to allocate array
```

**解決方法:**
1. 他のアプリケーションを閉じる
2. 仮想メモリを増やす
3. データサイズを削減

### 問題4: PyInstallerビルドエラー

**症状:**
```
ModuleNotFoundError: No module named 'xxx'
```

**解決方法:**
1. `pyinstaller.spec`の`hiddenimports`を確認
2. 不足しているモジュールを追加

```python
# pyinstaller.spec
hiddenimports = [
    # ... 既存のインポート
    '不足しているモジュール名',
]
```

## 📊 パフォーマンス最適化

### 32bit環境での推奨設定

1. **メモリ使用量の削減**
   - 大きなデータセットを分割処理
   - 不要なデータを早期に削除

2. **依存関係の最適化**
   - 必要最小限のライブラリのみインストール
   - 大きなライブラリの代替を検討

3. **ビルドサイズの削減**
   - UPX圧縮を有効化（`pyinstaller.spec`で設定済み）
   - 不要なモジュールを除外

## 🔍 トラブルシューティング

### ログの確認

```powershell
# ビルドログを確認
Get-Content build\pyinstaller\warn-pyinstaller.txt

# エラーログを確認
Get-Content error.log
```

### デバッグビルド

```powershell
# デバッグモードでビルド
$env:TARGET_ARCH = "x86"
uv run pyinstaller --clean --noconfirm --debug=all pyinstaller.spec
```

### システム情報の収集

```powershell
# システム情報を出力
python -c "import sys, platform, struct; print(f'Python: {sys.version}'); print(f'Platform: {platform.platform()}'); print(f'Architecture: {struct.calcsize(\"P\") * 8}bit')"
```

## 📚 参考資料

- [Python 32bit版ダウンロード](https://www.python.org/downloads/)
- [PyInstaller ドキュメント](https://pyinstaller.org/)
- [32bit Windows対応テスト](./tests/README_32bit_tests.md)

## 💡 ヒント

1. **仮想環境の使用**: プロジェクトごとに独立した環境を作成
2. **定期的なテスト**: ビルド前に32bit互換性テストを実行
3. **バージョン管理**: 依存関係のバージョンを固定（`uv.lock`を使用）

---

**最終更新**: 2025年1月

