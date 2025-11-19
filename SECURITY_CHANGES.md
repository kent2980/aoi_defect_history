# セキュリティ対策実施内容

## 実施日
2024年12月

## 実施内容

### 1. .gitignoreの更新

機密情報を含む可能性のある設定ファイルをGit管理から除外するように`.gitignore`を更新しました。

**追加された項目:**
- `kintone_settings.ini` - Kintone API設定ファイル
- `settings.ini` - アプリケーション設定ファイル

### 2. 環境変数を使用した統一的な設定管理

**変更前:**
- `aoi_view.py`: 設定ファイル（`kintone_settings.ini`）から読み込み
- `repair_view.py`: 環境変数から読み込み（`.env`ファイル）

**変更後:**
- `aoi_view.py`: 環境変数を優先的に使用し、フォールバックとして設定ファイルを使用
- `repair_view.py`: 環境変数を使用（変更なし）
- `kintone_settings.py`: 環境変数を使用するように変更

**メリット:**
- 機密情報が設定ファイルに平文で保存されることを防止
- 環境変数による統一的な管理

**環境変数名:**
- `KINTONE_SUBDOMAIN`: Kintoneサブドメイン
- `KINTONE_APP_ID`: KintoneアプリID
- `KINTONE_API_TOKEN`: Kintone APIトークン

**使用方法:**

`.env`ファイルを作成し、以下のように設定してください：

```env
# Kintone API設定（AOI検査用）
KINTONE_SUBDOMAIN=your_subdomain_here
KINTONE_APP_ID=your_app_id_here
KINTONE_API_TOKEN=your_api_token_here

# Kintone API設定（修理用）
REPAIR_KINTONE_SUBDOMAIN=your_subdomain_here
REPAIR_KINTONE_APP_ID=your_app_id_here
REPAIR_KINTONE_API_TOKEN=your_api_token_here
```

### 3. ファイルパスのサニタイズ機能の追加

**新規追加関数:**

1. `sanitize_file_path(file_path: str, base_directory: str = None) -> Path`
   - パストラバーサル攻撃を防止するファイルパスのサニタイズ関数
   - `..`を含むパスを検出して例外を発生
   - ベースディレクトリが指定された場合、そのディレクトリ内のパスのみ許可

2. `validate_directory_path(directory_path: str) -> Path`
   - ディレクトリパスを検証してサニタイズする関数
   - 空のパスを検出して例外を発生

**適用箇所:**
- `__create_sqlite_db()`: 共有ディレクトリのパス検証
- `save_defect_info()`: データディレクトリのパス検証
- `delete_defect_info()`: データディレクトリのパス検証
- `change_lot()`: 画像ディレクトリのパス検証

### 4. パストラバーサル攻撃対策の実装

以下の箇所でファイルパスのサニタイズを適用：

1. **データベースファイルパス**
   - 共有ディレクトリのパス検証
   - データベースファイル名の検証

2. **画像ファイルパス**
   - 画像ディレクトリのパス検証
   - 画像ファイル名の検証（ベースディレクトリ内のパスのみ許可）

3. **データディレクトリパス**
   - 出力ディレクトリのパス検証
   - ロット番号ディレクトリのパス検証

## 注意事項

### 後方互換性

- 既存の`kintone_settings.ini`ファイルがある場合、環境変数が設定されていない場合はフォールバックとして使用されます
- ただし、セキュリティのため、できるだけ早く環境変数への移行を推奨します

### 移行手順

1. `.env`ファイルを作成し、必要な環境変数を設定
2. `kintone_settings.ini`ファイルを削除（または`.gitignore`に含まれていることを確認）
3. アプリケーションを再起動

### SQLiteクエリのパラメータ化について

現在、SQLiteクエリは`aoi_data_manager`パッケージ内で実行されています。
このパッケージがパラメータ化されたクエリを使用していることを確認してください。
もし使用していない場合は、パッケージ側での修正が必要です。

## 今後の改善提案

1. **設定の暗号化**
   - 環境変数も平文で保存されているため、将来的には暗号化を検討

2. **設定管理の一元化**
   - 設定クラスの導入による一元管理

3. **SQLiteクエリの検証**
   - `aoi_data_manager`パッケージでのパラメータ化されたクエリの使用確認

