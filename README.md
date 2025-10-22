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

# アプリケーション実行
uv run python main.py
```

### ビルド

```bash
# 実行ファイル作成
uv run pyinstaller pyinstaller.spec
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
