# 32bit Windows対応テスト

このディレクトリには、アプリケーションが32bit Windowsで正常に動作することを確認するためのテストファイルが含まれています。

## 📁 ファイル構成

### 🧪 テストファイル

- **`test_32bit_compatibility.py`** - 32bit Windows互換性テスト
  - システムアーキテクチャの確認
  - メモリ制限の検証
  - ライブラリ互換性（Pandas, PIL, Tkinter等）
  - ファイル操作・マルチスレッド処理の確認

- **`test_32bit_performance.py`** - 32bit環境パフォーマンステスト
  - DataFrame処理性能
  - 画像処理性能
  - ファイルI/O性能
  - メモリ使用パターン

- **`validate_32bit_config.py`** - 設定検証スクリプト
  - pyproject.tomlの32bit対応設定確認
  - 依存関係のバージョン検証
  - システム互換性確認

- **`run_32bit_tests.py`** - テスト実行統合スクリプト
  - 全テストの一括実行
  - 結果サマリーの表示

## 🚀 実行方法

### 1. 全テスト一括実行（推奨）

```bash
# 全ての32bit対応テストを一括実行
python tests/run_32bit_tests.py
```

### 2. 個別テスト実行

```bash
# 設定検証のみ
python tests/validate_32bit_config.py

# 互換性テストのみ（pytest使用）
python -m pytest tests/test_32bit_compatibility.py -v

# 互換性テストのみ（直接実行）
python tests/test_32bit_compatibility.py

# パフォーマンステストのみ
python tests/test_32bit_performance.py
```

## 📊 テスト内容詳細

### 🔍 互換性テスト (`test_32bit_compatibility.py`)

#### システムアーキテクチャ確認

- Pythonのビット数（32bit/64bit）検出
- プラットフォーム情報の取得
- アーキテクチャ情報の確認

#### メモリ制限確認

- 利用可能メモリの確認
- 32bit環境での適切なメモリ容量チェック
- メモリ不足時の警告

#### ライブラリ互換性

- **Pandas**: バージョン2.3+の32bit互換性問題を検出
- **NumPy**: バージョン1.25+の32bit互換性問題を検出
- **PIL/Pillow**: 画像処理機能の動作確認
- **Tkinter**: GUI機能の基本動作確認

#### ファイル・マルチスレッド処理

- CSV読み書き処理の確認
- 設定ファイル処理の確認
- ThreadPoolExecutorの動作確認
- 基本的なマルチスレッド処理の確認

### ⚡ パフォーマンステスト (`test_32bit_performance.py`)

#### DataFrame処理性能

- 1,000〜10,000行のDataFrame操作
- グループ化、ソート、フィルタリング性能
- メモリ使用量の測定

#### 画像処理性能

- 800x600〜1200x900の画像処理
- リサイズ、描画、サムネイル作成
- メモリ使用量の推定

#### ファイルI/O性能

- CSV読み書き性能
- ファイルサイズと処理時間の関係
- エンコーディング処理の確認

#### メモリ使用パターン

- 段階的なメモリ使用量測定
- ピークメモリ使用量の確認
- ガベージコレクション効果の確認

### ⚙️ 設定検証 (`validate_32bit_config.py`)

#### pyproject.toml検証

- 依存関係の32bit対応バージョン確認
- Python要件の検証
- プロジェクト分類子の確認

#### システム設定検証

- インストール済みパッケージの確認
- ファイルパスの互換性確認
- 推奨設定の生成

## 🎯 32bit Windows対応基準

### ✅ 成功基準

1. **全テストが成功** - 32bit Windows完全対応
2. **軽微な警告のみ** - 32bit Windows部分対応（実用可能）

### ⚠️ 注意すべき警告

- Pandas 2.3+ バージョンの使用
- NumPy 1.25+ バージョンの使用
- Python 3.12+ での一部ライブラリ互換性
- 4GB超メモリ環境での動作

### ❌ 対応が必要な問題

- 基本ライブラリのインポートエラー
- メモリ不足エラー
- 重要なファイル操作の失敗
- GUI機能の動作不良

## 📋 推奨環境設定

### 32bit Windows推奨構成

```toml
# pyproject.toml
[project]
requires-python = ">=3.9,<3.12"
dependencies = [
    "pandas<2.0.0",
    "numpy<1.25.0", 
    "pillow>=10.0.0,<12.0.0",
    "psutil>=5.8.0",
    "openpyxl>=3.0.0"
]

classifiers = [
    "Operating System :: Microsoft :: Windows",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10", 
    "Programming Language :: Python :: 3.11"
]
```

### システム要件

- **OS**: Windows 7 SP1 以降（32bit版）
- **Python**: 3.9 - 3.11（32bit版）
- **メモリ**: 2GB以上推奨（最低1GB）
- **ディスク**: 500MB以上の空き容量

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### 1. Pandas/NumPy互換性エラー

```bash
# 古いバージョンに変更
pip install "pandas<2.0.0" "numpy<1.25.0"
```

#### 2. メモリ不足エラー

- 大きなデータセットの処理を避ける
- チャンク処理の実装
- ガベージコレクションの明示的実行

#### 3. GUI表示エラー

- ディスプレイDPI設定の確認
- Tkinterのバージョン確認
- フォント設定の調整

#### 4. ファイルアクセスエラー

- 管理者権限での実行
- パス長制限の確認（260文字以下）
- 日本語文字を含まないパスの使用

## 📈 継続的な32bit対応

### 開発時の注意点

1. **依存関係の更新時** - 32bit互換性の確認
2. **新機能追加時** - メモリ使用量の測定
3. **リリース前** - 全テストの実行
4. **定期的** - パフォーマンステストの実行

### CI/CD統合

```yaml
# GitHub Actions example
- name: Run 32bit compatibility tests
  run: python tests/run_32bit_tests.py
```

---

💡 **ヒント**: 32bit環境でのテストは、仮想マシンや専用の32bit Windowsマシンで実行することを推奨します。
