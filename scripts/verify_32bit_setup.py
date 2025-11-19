"""
32bit Windows環境セットアップ検証スクリプト

このスクリプトは、32bit Windows向けビルドに必要な環境が
正しく設定されているかを確認します。
"""

import sys
import platform
import struct
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict
import importlib.util


class Setup32BitVerifier:
    """32bit Windows環境検証クラス"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.python_bits = struct.calcsize("P") * 8
        self.issues: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

    def verify_python_architecture(self) -> bool:
        """Pythonのアーキテクチャを確認"""
        print("=" * 60)
        print("1. Pythonアーキテクチャの確認")
        print("=" * 60)

        python_version = sys.version.split()[0]
        print(f"Python バージョン: {python_version}")
        print(f"Python アーキテクチャ: {self.python_bits}bit")
        print(f"プラットフォーム: {platform.platform()}")
        print(f"マシン: {platform.machine()}")

        if self.python_bits == 32:
            print("✅ 32bit Python環境が検出されました")
            return True
        elif self.python_bits == 64:
            self.issues.append(
                "❌ 64bit Pythonが検出されました。32bit Pythonが必要です。"
            )
            print("❌ 64bit Pythonが検出されました")
            print("   32bit Pythonをインストールしてください")
            return False
        else:
            self.issues.append(f"❌ サポートされていないアーキテクチャ: {self.python_bits}bit")
            return False

    def verify_python_version(self) -> bool:
        """Pythonバージョンを確認"""
        print("\n" + "=" * 60)
        print("2. Pythonバージョンの確認")
        print("=" * 60)

        major, minor = sys.version_info[:2]
        print(f"Python バージョン: {major}.{minor}")

        if major == 3 and minor == 11:
            print("✅ Python 3.11が検出されました（推奨）")
            return True
        elif major == 3 and minor >= 9:
            self.warnings.append(
                f"⚠️  Python {major}.{minor}が検出されました。Python 3.11を推奨します。"
            )
            print(f"⚠️  Python {major}.{minor}が検出されました")
            return True
        else:
            self.issues.append(
                f"❌ Python {major}.{minor}はサポートされていません。Python 3.9-3.11が必要です。"
            )
            return False

    def verify_dependencies(self) -> Dict[str, bool]:
        """依存関係の確認"""
        print("\n" + "=" * 60)
        print("3. 依存関係の確認")
        print("=" * 60)

        required_packages = {
            "numpy": "1.24.3",
            "pandas": "2.0.3",
            "pillow": "10.3.0",
            "requests": None,
            "python-dotenv": None,
        }

        results = {}
        for package, expected_version in required_packages.items():
            try:
                module = __import__(package.replace("-", "_"))
                version = getattr(module, "__version__", "unknown")
                installed = True

                print(f"✅ {package}: {version} (インストール済み)")

                if expected_version and version != expected_version:
                    self.warnings.append(
                        f"⚠️  {package}のバージョンが期待値と異なります: {version} != {expected_version}"
                    )
                    print(f"   ⚠️  期待値: {expected_version}, 実際: {version}")

                results[package] = True
            except ImportError:
                print(f"❌ {package}: インストールされていません")
                self.issues.append(f"❌ {package}がインストールされていません")
                results[package] = False

        return results

    def verify_build_tools(self) -> bool:
        """ビルドツールの確認"""
        print("\n" + "=" * 60)
        print("4. ビルドツールの確認")
        print("=" * 60)

        # PyInstallerの確認
        try:
            import PyInstaller
            version = PyInstaller.__version__
            print(f"✅ PyInstaller: {version} (インストール済み)")
            return True
        except ImportError:
            print("❌ PyInstallerがインストールされていません")
            self.issues.append("❌ PyInstallerがインストールされていません")
            print("   インストール方法: pip install pyinstaller または uv sync")
            return False

    def verify_project_files(self) -> bool:
        """プロジェクトファイルの確認"""
        print("\n" + "=" * 60)
        print("5. プロジェクトファイルの確認")
        print("=" * 60)

        required_files = [
            "main.py",
            "pyinstaller.spec",
            "pyproject.toml",
            "src/aoi_view.py",
            "src/utils.py",
        ]

        all_exist = True
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path} が見つかりません")
                self.issues.append(f"❌ {file_path} が見つかりません")
                all_exist = False

        return all_exist

    def verify_memory(self) -> bool:
        """メモリの確認"""
        print("\n" + "=" * 60)
        print("6. メモリの確認")
        print("=" * 60)

        try:
            import psutil
            memory = psutil.virtual_memory()
            total_gb = memory.total / (1024**3)
            available_gb = memory.available / (1024**3)

            print(f"総メモリ: {total_gb:.2f} GB")
            print(f"利用可能メモリ: {available_gb:.2f} GB")
            print(f"メモリ使用率: {memory.percent:.1f}%")

            if self.python_bits == 32:
                if total_gb > 4:
                    self.warnings.append(
                        "⚠️  32bit環境で4GB超のメモリが検出されました（通常は2-4GB）"
                    )

                if available_gb < 1:
                    self.warnings.append("⚠️  利用可能メモリが1GB未満です")

            if available_gb < 0.5:
                self.issues.append("❌ 利用可能メモリが不足しています（最低0.5GB必要）")
                return False

            print("✅ メモリ容量は十分です")
            return True
        except ImportError:
            self.warnings.append("⚠️  psutilがインストールされていないため、メモリ情報を取得できません")
            print("⚠️  psutilがインストールされていません（オプション）")
            return True

    def verify_uv_installation(self) -> bool:
        """uvのインストール確認"""
        print("\n" + "=" * 60)
        print("7. uvパッケージマネージャーの確認")
        print("=" * 60)

        try:
            result = subprocess.run(
                ["uv", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ uv: {version} (インストール済み)")
                return True
            else:
                print("⚠️  uvがインストールされていない可能性があります")
                self.warnings.append("⚠️  uvがインストールされていない可能性があります")
                return False
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print("⚠️  uvがインストールされていません（オプション）")
            print("   インストール方法: pip install uv")
            self.warnings.append("⚠️  uvがインストールされていません（オプション）")
            return False

    def print_summary(self):
        """検証結果のサマリーを表示"""
        print("\n" + "=" * 60)
        print("検証結果サマリー")
        print("=" * 60)

        if self.info:
            print("\n📋 情報:")
            for info in self.info:
                print(f"  {info}")

        if self.warnings:
            print("\n⚠️  警告:")
            for warning in self.warnings:
                print(f"  {warning}")

        if self.issues:
            print("\n❌ 問題:")
            for issue in self.issues:
                print(f"  {issue}")
            print("\n❌ セットアップに問題があります。上記の問題を解決してください。")
            return False
        elif self.warnings:
            print("\n⚠️  セットアップは完了していますが、警告があります。")
            return True
        else:
            print("\n✅ セットアップは正常です。32bitビルドを実行できます。")
            return True

    def run_all_checks(self) -> bool:
        """全ての検証を実行"""
        print("32bit Windows環境セットアップ検証")
        print("=" * 60)
        print(f"プロジェクトルート: {self.project_root}")
        print()

        # 各検証を実行
        checks = [
            self.verify_python_architecture,
            self.verify_python_version,
            self.verify_dependencies,
            self.verify_build_tools,
            self.verify_project_files,
            self.verify_memory,
            self.verify_uv_installation,
        ]

        for check in checks:
            try:
                check()
            except Exception as e:
                self.issues.append(f"❌ 検証中にエラーが発生: {e}")
                print(f"❌ エラー: {e}")

        return self.print_summary()


def main():
    """メイン関数"""
    verifier = Setup32BitVerifier()
    success = verifier.run_all_checks()

    if not success:
        print("\n" + "=" * 60)
        print("次のステップ:")
        print("=" * 60)
        print("1. 上記の問題を解決してください")
        print("2. 32bit Pythonをインストール（必要に応じて）")
        print("3. 依存関係をインストール: uv sync または pip install -e .")
        print("4. 再度このスクリプトを実行して確認してください")
        sys.exit(1)
    else:
        print("\n" + "=" * 60)
        print("次のステップ:")
        print("=" * 60)
        print("1. ビルドを実行: .\\build_32bit.bat または python build_test.py")
        print("2. 32bit互換性テストを実行: python tests\\run_32bit_tests.py")
        sys.exit(0)


if __name__ == "__main__":
    main()

