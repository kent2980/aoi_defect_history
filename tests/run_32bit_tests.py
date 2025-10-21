"""
32bit Windows対応テスト実行スクリプト

このスクリプトは、32bit Windows対応のためのテストを一括実行します。
"""

import sys
import subprocess
import platform
import struct
from pathlib import Path
import time


def run_command(command, description):
    """コマンドを実行し、結果を表示"""
    print(f"\n🔄 {description}")
    print(f"実行コマンド: {' '.join(command)}")
    print("-" * 50)

    try:
        start_time = time.time()
        result = subprocess.run(
            command, check=True, capture_output=True, text=True, encoding="utf-8"
        )
        end_time = time.time()

        print("✅ 成功")
        print(f"実行時間: {end_time - start_time:.2f}秒")

        if result.stdout:
            print("\n📤 出力:")
            print(result.stdout)

        if result.stderr:
            print("\n⚠️  警告:")
            print(result.stderr)

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ 失敗 (終了コード: {e.returncode})")

        if e.stdout:
            print("\n📤 出力:")
            print(e.stdout)

        if e.stderr:
            print("\n❌ エラー:")
            print(e.stderr)

        return False

    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False


def main():
    """メイン実行関数"""
    print("🔍 32bit Windows対応テスト実行")
    print("=" * 60)

    # システム情報表示
    python_bits = struct.calcsize("P") * 8
    print(f"実行環境: {python_bits}bit Python")
    print(f"Platform: {platform.platform()}")
    print(f"Python: {sys.version}")
    print(f"作業ディレクトリ: {Path.cwd()}")

    # テスト結果
    test_results = {}

    # 1. 設定検証テスト
    success = run_command(
        [sys.executable, "tests/validate_32bit_config.py"], "設定検証テスト"
    )
    test_results["config_validation"] = success

    # 2. 32bit互換性テスト（pytest使用）
    success = run_command(
        [sys.executable, "-m", "pytest", "tests/test_32bit_compatibility.py", "-v"],
        "32bit互換性テスト (pytest)",
    )
    test_results["compatibility_test"] = success

    # 3. 32bit互換性テスト（直接実行）
    success = run_command(
        [sys.executable, "tests/test_32bit_compatibility.py"],
        "32bit互換性テスト (直接実行)",
    )
    test_results["compatibility_direct"] = success

    # 4. パフォーマンステスト
    success = run_command(
        [sys.executable, "tests/test_32bit_performance.py"], "32bitパフォーマンステスト"
    )
    test_results["performance_test"] = success

    # 5. 基本アプリケーションテスト（import確認）
    success = run_command(
        [
            sys.executable,
            "-c",
            "import src.aoi_view; print('✅ AOIViewのインポート成功')",
        ],
        "基本アプリケーションテスト (import)",
    )
    test_results["basic_import"] = success

    # 6. 依存関係チェック
    success = run_command(
        [sys.executable, "-m", "pip", "check"], "依存関係整合性チェック"
    )
    test_results["dependency_check"] = success

    # 7. パッケージリスト表示
    success = run_command(
        [sys.executable, "-m", "pip", "list"], "インストール済みパッケージ一覧"
    )
    test_results["package_list"] = success

    # テスト結果サマリー
    print("\n" + "=" * 60)
    print("テスト結果サマリー")
    print("=" * 60)

    passed_tests = 0
    total_tests = len(test_results)

    for test_name, success in test_results.items():
        status = "✅ 成功" if success else "❌ 失敗"
        print(f"  {test_name}: {status}")
        if success:
            passed_tests += 1

    print(f"\n📊 統計:")
    print(f"  成功: {passed_tests}/{total_tests} テスト")
    print(f"  成功率: {passed_tests/total_tests*100:.1f}%")

    # 総合判定
    if passed_tests == total_tests:
        print("\n🎉 全テスト成功！32bit Windows対応OK")
        return 0
    elif passed_tests >= total_tests * 0.8:
        print(f"\n⚠️  一部テスト失敗（{total_tests - passed_tests}件）")
        print("   32bit Windows対応に軽微な問題があります")
        return 1
    else:
        print(f"\n❌ 多数のテスト失敗（{total_tests - passed_tests}件）")
        print("   32bit Windows対応に重大な問題があります")
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
