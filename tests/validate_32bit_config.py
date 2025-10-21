"""
32bit Windows 対応設定検証スクリプト

このスクリプトは、pyproject.tomlの設定が32bit Windowsに対応しているかを検証します。
"""

import sys
import struct
import subprocess
import platform
from pathlib import Path
import configparser
import toml
from typing import Dict, List, Tuple, Optional


class Config32BitValidator:
    """32bit Windows対応設定検証クラス"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.python_bits = struct.calcsize("P") * 8
        self.is_32bit = self.python_bits == 32
        self.issues: List[str] = []
        self.warnings: List[str] = []
        self.recommendations: List[str] = []

    def validate_pyproject_toml(self) -> Dict:
        """pyproject.tomlの32bit対応を検証"""
        pyproject_path = self.project_root / "pyproject.toml"

        if not pyproject_path.exists():
            self.issues.append("pyproject.toml が見つかりません")
            return {}

        try:
            with open(pyproject_path, "r", encoding="utf-8") as f:
                config = toml.load(f)
        except Exception as e:
            self.issues.append(f"pyproject.toml の読み込みに失敗: {e}")
            return {}

        print("📋 pyproject.toml 32bit対応検証")
        print("-" * 40)

        # 依存関係の検証
        dependencies = config.get("dependencies", [])
        self._validate_dependencies(dependencies)

        # Python要件の検証
        if "requires-python" in config:
            self._validate_python_version(config["requires-python"])

        # プロジェクト設定の検証
        project_config = config.get("project", {})
        self._validate_project_config(project_config)

        # ツール設定の検証
        tool_config = config.get("tool", {})
        self._validate_tool_config(tool_config)

        return config

    def _validate_dependencies(self, dependencies: List[str]):
        """依存関係の32bit対応を検証"""
        print("🔍 依存関係の32bit対応チェック:")

        problematic_deps = {
            "pandas": {
                "version_limit": "2.0.0",
                "reason": "32bit Windows互換性の問題",
                "recommendation": "pandas<2.0.0",
            },
            "numpy": {
                "version_limit": "1.25.0",
                "reason": "32bit Windows互換性の問題",
                "recommendation": "numpy<1.25.0",
            },
            "scipy": {
                "version_limit": "1.11.0",
                "reason": "32bit Windows互換性の問題",
                "recommendation": "scipy<1.11.0",
            },
        }

        for dep in dependencies:
            dep_name = (
                dep.split(">=")[0].split("==")[0].split("<")[0].split(">")[0].strip()
            )

            if dep_name in problematic_deps:
                prob_info = problematic_deps[dep_name]

                # バージョン制約をチェック
                if ">=" in dep or "==" in dep:
                    version_part = (
                        dep.split(">=")[-1] if ">=" in dep else dep.split("==")[-1]
                    )
                    version_part = version_part.split("<")[0].strip()

                    try:
                        version_tuple = tuple(map(int, version_part.split(".")[:2]))
                        limit_tuple = tuple(
                            map(int, prob_info["version_limit"].split(".")[:2])
                        )

                        if version_tuple >= limit_tuple:
                            self.issues.append(f"{dep}: {prob_info['reason']}")
                            self.recommendations.append(
                                f"{dep_name}: {prob_info['recommendation']} を推奨"
                            )
                            print(f"  ❌ {dep}: 32bit互換性の問題")
                        else:
                            print(f"  ✅ {dep}: 32bit対応OK")
                    except ValueError:
                        print(f"  ⚠️  {dep}: バージョン形式を解析できません")

                elif "<" not in dep:
                    # バージョン制約がない場合
                    self.warnings.append(
                        f"{dep_name}: 32bit対応のためバージョン制約を推奨"
                    )
                    self.recommendations.append(
                        f"{dep_name}: {prob_info['recommendation']} を推奨"
                    )
                    print(f"  ⚠️  {dep}: バージョン制約なし（32bit問題の可能性）")
                else:
                    print(f"  ✅ {dep}: バージョン制約あり")
            else:
                print(f"  ℹ️  {dep}: 32bit対応チェック対象外")

    def _validate_python_version(self, python_requirement: str):
        """Python バージョン要件の検証"""
        print(f"\n🐍 Python要件: {python_requirement}")

        # 32bit Pythonで推奨されるバージョン
        recommended_versions = ["3.9", "3.10", "3.11"]

        if "3.12" in python_requirement or "3.13" in python_requirement:
            self.warnings.append(
                "Python 3.12+ は32bit Windows での一部ライブラリで互換性問題があります"
            )
            self.recommendations.append("32bit Windows では Python 3.11 以下を推奨")
            print("  ⚠️  Python 3.12+ は32bit互換性に注意が必要")
        else:
            print("  ✅ Python バージョン要件は32bit対応")

    def _validate_project_config(self, project_config: Dict):
        """プロジェクト設定の検証"""
        print(f"\n📦 プロジェクト設定:")

        # クラシファイア（分類子）の確認
        classifiers = project_config.get("classifiers", [])

        has_windows = any("Windows" in c for c in classifiers)
        has_32bit = any("32bit" in c or "win32" in c for c in classifiers)

        if has_windows:
            print("  ✅ Windows対応を明示")
        else:
            self.recommendations.append(
                "classifiers に 'Operating System :: Microsoft :: Windows' を追加推奨"
            )
            print("  ⚠️  Windows対応の明示なし")

        if has_32bit:
            print("  ✅ 32bit対応を明示")
        else:
            self.recommendations.append(
                "classifiers に Windows 32bit対応を明示することを推奨"
            )
            print("  ℹ️  32bit対応の明示なし")

    def _validate_tool_config(self, tool_config: Dict):
        """ツール設定の検証"""
        print(f"\n🔧 ツール設定:")

        # PyInstaller設定の確認
        if "pyinstaller" in tool_config:
            pyinstaller_config = tool_config["pyinstaller"]
            print("  ✅ PyInstaller設定あり")

            # 32bit用の設定確認
            if "options" in pyinstaller_config:
                options = pyinstaller_config["options"]
                if "--target-architecture" in str(options):
                    print("  ✅ ターゲットアーキテクチャ設定あり")
                else:
                    self.recommendations.append(
                        "PyInstaller に --target-architecture x86 オプションを追加推奨"
                    )
                    print("  ⚠️  ターゲットアーキテクチャ未設定")
        else:
            print("  ℹ️  PyInstaller設定なし")

        # pytest設定の確認
        if "pytest" in tool_config:
            print("  ✅ pytest設定あり")
        else:
            print("  ℹ️  pytest設定なし")

    def validate_installed_packages(self):
        """インストール済みパッケージの32bit対応を検証"""
        print(f"\n📦 インストール済みパッケージの32bit対応検証")
        print("-" * 40)

        try:
            # uv pip list の実行
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list"],
                capture_output=True,
                text=True,
                check=True,
            )

            installed_packages = {}
            for line in result.stdout.split("\n")[2:]:  # ヘッダーをスキップ
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        name, version = parts[0], parts[1]
                        installed_packages[name.lower()] = version

            # 32bit問題のあるパッケージをチェック
            problematic_packages = {
                "pandas": ("2.0.0", "32bit Windows互換性"),
                "numpy": ("1.25.0", "32bit Windows互換性"),
                "scipy": ("1.11.0", "32bit Windows互換性"),
                "tensorflow": ("2.11.0", "32bit未対応"),
                "pytorch": ("1.13.0", "32bit未対応"),
            }

            for pkg_name, (limit_version, reason) in problematic_packages.items():
                if pkg_name in installed_packages:
                    installed_version = installed_packages[pkg_name]
                    print(f"  📦 {pkg_name}: {installed_version}")

                    try:
                        installed_tuple = tuple(
                            map(int, installed_version.split(".")[:2])
                        )
                        limit_tuple = tuple(map(int, limit_version.split(".")[:2]))

                        if installed_tuple >= limit_tuple:
                            self.issues.append(
                                f"{pkg_name} {installed_version}: {reason}"
                            )
                            print(f"    ❌ {reason}")
                        else:
                            print(f"    ✅ 32bit対応OK")
                    except ValueError:
                        print(f"    ⚠️  バージョン形式を解析できません")
                else:
                    print(f"  ℹ️  {pkg_name}: 未インストール")

        except subprocess.CalledProcessError as e:
            self.issues.append(f"パッケージリストの取得に失敗: {e}")
        except Exception as e:
            self.issues.append(f"パッケージ検証中にエラー: {e}")

    def validate_system_compatibility(self):
        """システム互換性の検証"""
        print(f"\n🖥️  システム互換性検証")
        print("-" * 40)

        # アーキテクチャ情報
        print(f"  Python: {self.python_bits}bit")
        print(f"  Platform: {platform.platform()}")
        print(f"  Machine: {platform.machine()}")
        print(f"  Processor: {platform.processor()}")

        # 32bit環境特有のチェック
        if self.is_32bit:
            print("  ✅ 32bit Python環境を検出")

            # メモリ制限の確認
            try:
                import psutil

                memory = psutil.virtual_memory()
                total_gb = memory.total / (1024**3)

                print(f"  💾 総メモリ: {total_gb:.2f}GB")

                if total_gb > 4:
                    self.warnings.append(
                        "32bit環境で4GB超のメモリが検出されました（PAE環境の可能性）"
                    )
                    print("    ⚠️  4GB超メモリ検出（PAE環境？）")
                else:
                    print("    ✅ 32bit環境に適したメモリ容量")

            except ImportError:
                print("    ℹ️  psutil未インストール（メモリ情報取得不可）")
        else:
            print(f"  ℹ️  {self.python_bits}bit Python環境（32bit対応テスト）")

    def check_file_compatibility(self):
        """ファイル・パスの互換性確認"""
        print(f"\n📁 ファイル・パス互換性確認")
        print("-" * 40)

        # 長いパス名の確認
        project_path_str = str(self.project_root.absolute())
        print(f"  プロジェクトパス: {project_path_str}")
        print(f"  パス長: {len(project_path_str)} 文字")

        if len(project_path_str) > 240:
            self.warnings.append(
                "プロジェクトパスが長すぎます（Windows旧バージョンで問題の可能性）"
            )
            print("    ⚠️  パスが長すぎる（240文字超）")
        else:
            print("    ✅ パス長は適切")

        # 日本語文字の確認
        if any(ord(c) > 127 for c in project_path_str):
            self.warnings.append("プロジェクトパスに非ASCII文字が含まれています")
            print("    ⚠️  非ASCII文字を含むパス")
        else:
            print("    ✅ ASCII文字のみのパス")

    def generate_32bit_recommendations(self):
        """32bit対応の推奨設定を生成"""
        print(f"\n💡 32bit Windows対応推奨設定")
        print("-" * 40)

        # pyproject.toml の推奨設定
        recommended_config = {
            "dependencies": [
                "pandas<2.0.0",
                "numpy<1.25.0",
                "pillow>=10.0.0,<12.0.0",
                "psutil>=5.8.0",
                "openpyxl>=3.0.0",
            ],
            "requires-python": ">=3.9,<3.12",
            "classifiers": [
                "Development Status :: 4 - Beta",
                "Intended Audience :: End Users/Desktop",
                "License :: OSI Approved :: MIT License",
                "Operating System :: Microsoft :: Windows",
                "Operating System :: Microsoft :: Windows :: Windows 10",
                "Programming Language :: Python :: 3",
                "Programming Language :: Python :: 3.9",
                "Programming Language :: Python :: 3.10",
                "Programming Language :: Python :: 3.11",
                "Topic :: Desktop Environment",
            ],
        }

        print("  推奨 pyproject.toml 設定:")
        for key, value in recommended_config.items():
            if isinstance(value, list):
                print(f"    {key}:")
                for item in value[:3]:  # 最初の3つを表示
                    print(f"      - {item}")
                if len(value) > 3:
                    print(f"      ... ({len(value) - 3} more)")
            else:
                print(f"    {key}: {value}")

    def run_validation(self):
        """全ての検証を実行"""
        print("🔍 32bit Windows対応設定検証")
        print("=" * 60)
        print(f"プロジェクト: {self.project_root}")
        print(f"実行環境: {self.python_bits}bit Python")
        print()

        # 各検証を実行
        self.validate_pyproject_toml()
        self.validate_installed_packages()
        self.validate_system_compatibility()
        self.check_file_compatibility()
        self.generate_32bit_recommendations()

        # 結果サマリー
        self.print_summary()

    def print_summary(self):
        """検証結果のサマリーを表示"""
        print("\n" + "=" * 60)
        print("検証結果サマリー")
        print("=" * 60)

        # 問題の表示
        if self.issues:
            print("❌ 問題:")
            for issue in self.issues:
                print(f"  - {issue}")

        # 警告の表示
        if self.warnings:
            print("\n⚠️  警告:")
            for warning in self.warnings:
                print(f"  - {warning}")

        # 推奨事項の表示
        if self.recommendations:
            print("\n💡 推奨事項:")
            for rec in self.recommendations:
                print(f"  - {rec}")

        # 総合判定
        print(f"\n📊 総合判定:")
        if len(self.issues) == 0:
            if len(self.warnings) == 0:
                print("  ✅ 32bit Windows完全対応")
            elif len(self.warnings) <= 2:
                print("  ⚠️  32bit Windows部分対応（軽微な警告あり）")
            else:
                print("  ⚠️  32bit Windows対応（複数の警告あり）")
        else:
            if len(self.issues) <= 2:
                print("  ❌ 32bit Windows対応に軽微な問題あり")
            else:
                print("  ❌ 32bit Windows対応に重大な問題あり")

        print(f"\n📈 統計:")
        print(f"  問題: {len(self.issues)} 件")
        print(f"  警告: {len(self.warnings)} 件")
        print(f"  推奨: {len(self.recommendations)} 件")


if __name__ == "__main__":
    # 検証を実行
    validator = Config32BitValidator()
    validator.run_validation()
