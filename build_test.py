"""
ローカル環境でのWindows実行ファイルビルドテストスクリプト

このスクリプトは、GitHub Actionsと同様の環境でローカルビルドをテストします。
"""

import os
import sys
import subprocess
import platform
import struct
from pathlib import Path
import shutil
import time


def get_system_info():
    """システム情報を取得"""
    python_bits = struct.calcsize("P") * 8
    return {
        "python_bits": python_bits,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python_version": sys.version,
        "python_executable": sys.executable,
    }


def run_command(command, description, cwd=None):
    """コマンドを実行し、結果を表示"""
    print(f"\n🔄 {description}")
    print(f"実行コマンド: {' '.join(command)}")
    print("-" * 50)

    try:
        start_time = time.time()
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            encoding="utf-8",
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


def test_build_architecture(target_arch, python_bits):
    """指定されたアーキテクチャでビルドテスト"""
    print(f"\n{'='*60}")
    print(f"ビルドテスト: {target_arch} アーキテクチャ")
    print(f"{'='*60}")

    # 環境変数を設定
    env = os.environ.copy()
    env["TARGET_ARCH"] = target_arch

    arch_name = "win32" if target_arch == "x86" else "win64"

    # アーキテクチャとPythonの整合性チェック
    if target_arch == "x86" and python_bits == 64:
        print("⚠️  警告: 64bit Pythonで32bit実行ファイルをビルドしようとしています")
        print("   正常にビルドできない可能性があります")
    elif target_arch == "x64" and python_bits == 32:
        print("⚠️  警告: 32bit Pythonで64bit実行ファイルをビルドしようとしています")
        print("   正常にビルドできない可能性があります")

    # ビルド前のクリーンアップ
    build_dir = Path("build")
    dist_dir = Path("dist")

    if build_dir.exists():
        shutil.rmtree(build_dir)
        print("🧹 build ディレクトリをクリーンアップしました")

    if dist_dir.exists():
        shutil.rmtree(dist_dir)
        print("🧹 dist ディレクトリをクリーンアップしました")

    # PyInstallerでビルド
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        "pyinstaller.spec",
    ]

    success = run_command(command, f"{arch_name}ビルド実行", env=env)

    if success:
        # ビルド結果の確認
        expected_exe = (
            dist_dir
            / f"aoi-defect-history-{arch_name}"
            / f"aoi-defect-history-{arch_name}.exe"
        )

        if expected_exe.exists():
            file_size = expected_exe.stat().st_size / (1024 * 1024)  # MB
            print(f"✅ 実行ファイル作成成功: {expected_exe}")
            print(f"📏 ファイルサイズ: {file_size:.2f} MB")

            # 追加ファイルの確認
            dist_files = list(expected_exe.parent.glob("*"))
            print(f"📁 配布ファイル数: {len(dist_files)}")
            for file in dist_files[:10]:  # 最初の10ファイルを表示
                if file.is_file():
                    size_kb = file.stat().st_size / 1024
                    print(f"   - {file.name} ({size_kb:.1f} KB)")
            if len(dist_files) > 10:
                print(f"   ... および {len(dist_files) - 10} 個の追加ファイル")

            return True
        else:
            print(f"❌ 実行ファイルが見つかりません: {expected_exe}")

            # distディレクトリの内容を確認
            if dist_dir.exists():
                print("\n📁 dist ディレクトリの内容:")
                for item in dist_dir.rglob("*"):
                    print(f"   {item}")

            return False

    return False


def main():
    """メイン実行関数"""
    print("🔨 AOI Defect History - Windows実行ファイルビルドテスト")
    print("=" * 60)

    # システム情報表示
    sys_info = get_system_info()
    print(f"Python: {sys_info['python_bits']}bit")
    print(f"Platform: {sys_info['platform']}")
    print(f"Machine: {sys_info['machine']}")
    print(f"Python Version: {sys_info['python_version'].split()[0]}")
    print(f"作業ディレクトリ: {Path.cwd()}")

    # 必要なファイルの確認
    required_files = ["main.py", "pyinstaller.spec", "src/aoi_view.py"]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"\n❌ 必要なファイルが見つかりません:")
        for file in missing_files:
            print(f"   - {file}")
        return 1

    print("\n✅ 必要なファイルが揃っています")

    # 依存関係の確認
    print("\n🔍 依存関係の確認")
    success = run_command(
        [sys.executable, "-m", "pip", "check"], "依存関係整合性チェック"
    )

    if not success:
        print("⚠️  依存関係に問題がありますが、ビルドを継続します")

    # PyInstallerの確認・インストール
    print("\n🔧 PyInstallerの確認")
    try:
        import PyInstaller

        print(f"✅ PyInstaller {PyInstaller.__version__} が利用可能です")
    except ImportError:
        print("📦 PyInstallerをインストール中...")
        success = run_command(
            [sys.executable, "-m", "pip", "install", "pyinstaller"],
            "PyInstallerインストール",
        )
        if not success:
            print("❌ PyInstallerのインストールに失敗しました")
            return 1

    # アーキテクチャ別ビルドテスト
    test_results = {}
    python_bits = sys_info["python_bits"]

    # 利用可能なアーキテクチャを決定
    if python_bits == 64:
        # 64bit Pythonでは両方試せるが、32bitは警告付き
        test_architectures = ["x64", "x86"]
    else:
        # 32bit Pythonでは32bitのみ
        test_architectures = ["x86"]

    for arch in test_architectures:
        test_results[arch] = test_build_architecture(arch, python_bits)

    # 結果サマリー
    print(f"\n{'='*60}")
    print("ビルドテスト結果サマリー")
    print(f"{'='*60}")

    for arch, success in test_results.items():
        arch_name = "win32" if arch == "x86" else "win64"
        status = "✅ 成功" if success else "❌ 失敗"
        print(f"  {arch_name}: {status}")

    successful_builds = sum(test_results.values())
    total_builds = len(test_results)

    print(f"\n📊 統計:")
    print(f"  成功: {successful_builds}/{total_builds} ビルド")
    print(f"  成功率: {successful_builds/total_builds*100:.1f}%")

    if successful_builds == total_builds:
        print("\n🎉 全ビルド成功！")
        return 0
    elif successful_builds > 0:
        print(f"\n⚠️  一部ビルド成功（{total_builds - successful_builds}件失敗）")
        return 1
    else:
        print("\n❌ 全ビルド失敗")
        return 2


if __name__ == "__main__":
    exit_code = main()
    input("\nEnterキーを押して終了...")
    sys.exit(exit_code)
