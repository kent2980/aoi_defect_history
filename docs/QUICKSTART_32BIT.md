# 32bit Windows クイックスタートガイド

このガイドでは、32bit Windows向けの実行ファイルを最短でビルドする手順を説明します。

## 🚀 5分で始める

### ステップ1: 32bit Pythonのインストール（初回のみ）

1. [Python 3.11 (32bit版)をダウンロード](https://www.python.org/downloads/)
2. インストール時に「Add Python to PATH」にチェック
3. インストールを完了

### ステップ2: 環境の確認

```powershell
# Pythonのアーキテクチャを確認
python -c "import struct; print(f'Python {struct.calcsize(\"P\") * 8}bit')"
```

**期待される出力**: `Python 32bit`

### ステップ3: 依存関係のインストール

```powershell
# プロジェクトディレクトリに移動
cd C:\path\to\aoi_defect_history

# 依存関係をインストール
uv sync
# または
pip install -e .
```

### ステップ4: セットアップ検証（推奨）

```powershell
python scripts\verify_32bit_setup.py
```

### ステップ5: ビルド実行

```powershell
.\build_32bit.bat
```

## ✅ ビルド成功の確認

ビルドが成功すると、以下のファイルが作成されます：

```
dist\aoi-defect-history-win32\aoi-defect-history-win32.exe
```

## 🧪 テスト実行（オプション）

```powershell
# 32bit互換性テスト
python tests\run_32bit_tests.py
```

## ❓ トラブルシューティング

### 問題: 64bit Pythonが検出される

**解決方法:**
1. 32bit Pythonをインストール
2. 環境変数PATHで32bit Pythonを優先
3. 新しいコマンドプロンプトを開く

### 問題: 依存関係のインストールエラー

**解決方法:**
```powershell
# 個別にインストール
pip install "numpy==1.24.3"
pip install "pandas==2.0.3"
pip install "pillow<=10.3.0"
```

### 問題: ビルドエラー

**解決方法:**
1. ログを確認: `build\pyinstaller\warn-pyinstaller.txt`
2. セットアップを再検証: `python scripts\verify_32bit_setup.py`
3. 詳細な手順を確認: [SETUP_32BIT.md](SETUP_32BIT.md)

## 📚 詳細情報

- **詳細なセットアップ手順**: [SETUP_32BIT.md](SETUP_32BIT.md)
- **32bit互換性テスト**: [tests/README_32bit_tests.md](../tests/README_32bit_tests.md)
- **プロジェクトREADME**: [README.md](../README.md)

---

**次のステップ**: ビルドが成功したら、実行ファイルをテストして動作確認してください。

