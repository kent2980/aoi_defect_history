# AOI Defect History

## 概要

AOI（Automated Optical Inspection）検査機での不良履歴管理アプリケーションです。

## 配布パッケージの構成

### フルパッケージ（推奨）

```text
aoi-defect-history-win64/
├── aoi-defect-history-win64.exe    # メイン実行ファイル
├── defect_mapping.csv              # 不良名マッピングファイル（編集可能）
├── user.csv                        # ユーザー情報ファイル（編集可能）
└── _internal/                      # 実行時ライブラリ（自動生成）
```

### 設定ファイルの編集

- **defect_mapping.csv**: 不良コードと不良名の対応表
- **user.csv**: ユーザーIDと氏名の対応表

これらのCSVファイルは実行ファイルと同じディレクトリに配置してください。
ファイルが見つからない場合、アプリケーションでエラーが発生します。

### インストール手順

1. フルパッケージ（.zip）をダウンロード
2. 任意のフォルダに展開
3. `aoi-defect-history-win64.exe`を実行
4. 必要に応じて`defect_mapping.csv`と`user.csv`を編集

## 開発環境

### 要件

- Python 3.12+
- uv (パッケージマネージャー)

### セットアップ

```bash
# 依存関係のインストール
uv sync

# .envファイルの作成（初回のみ）
# .env.exampleをコピーして.envファイルを作成し、実際の値を設定してください
cp .env.example .env
# または、手動で.envファイルを作成して以下の内容を設定してください

# アプリケーション実行
uv run python main.py
```

### 環境変数の設定

修理機能を使用する場合は、`.env`ファイルにKintone APIの認証情報を設定する必要があります。

プロジェクトルートに`.env`ファイルを作成し、以下の内容を設定してください：

```env
# Kintone API設定（修理用）
REPAIR_KINTONE_SUBDOMAIN=your_subdomain_here
REPAIR_KINTONE_APP_ID=your_app_id_here
REPAIR_KINTONE_API_TOKEN=your_api_token_here
```

**重要**: `.env`ファイルには機密情報が含まれるため、Gitにコミットしないでください。`.gitignore`に`.env`が含まれていることを確認してください。

### ビルド

#### 64bit Windows向けビルド（推奨）

```bash
# 方法1: バッチファイルを使用（推奨）
.\build_64bit.bat

# 方法2: 手動ビルド
$env:TARGET_ARCH = "x64"
uv run pyinstaller --clean --noconfirm pyinstaller.spec
```

#### 32bit Windows向けビルド

32bit Windows向けのビルドには、32bit Python環境が必要です。

**詳細なセットアップ手順**: [32bit Windows向けセットアップ手順](docs/SETUP_32BIT.md)

```bash
# 方法1: バッチファイルを使用（推奨）
.\build_32bit.bat

# 方法2: セットアップ検証後にビルド
python scripts\verify_32bit_setup.py
$env:TARGET_ARCH = "x86"
uv run pyinstaller --clean --noconfirm pyinstaller.spec

# 方法3: 自動判定ビルド
.\build.bat
```

**32bitビルドの前提条件:**
- Python 3.11 (32bit版)
- 32bit対応の依存関係（現在の設定で問題なし）
- メモリ: 2GB以上推奨

**32bit環境の検証:**
```bash
# セットアップ検証
python scripts\verify_32bit_setup.py

# 32bit互換性テスト
python tests\run_32bit_tests.py
```

### アプリケーションアイコン

アプリケーションアイコンは`assets/icon.ico`に配置されています。

#### アイコンのデザイン

- 基板を拡大鏡で検査しているデザイン
- 緑色の基板に金色の配線パターン
- 赤色の不良箇所マーク
- シルバーの拡大鏡

#### アイコンの変更方法

1. `create_icon.py`スクリプトを編集してデザインを変更
2. アイコンを再生成:

   ```bash
   python create_icon.py
   ```

3. PyInstallerでビルド:

   ```bash
   uv run pyinstaller pyinstaller.spec
   ```

または、既存の`.ico`ファイルを`assets/icon.ico`に置き換えてビルドすることもできます。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
