"""
32bit Windows対応テスト

このテストファイルは、アプリケーションが32bit Windowsで正常に動作することを確認します。
"""

import sys
import platform
import struct
import psutil
import pandas as pd
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
import pytest
import warnings
from pathlib import Path
from typing import Dict, List, Tuple, Any
import subprocess
import importlib.util


class Test32BitCompatibility:
    """32bit Windows対応テストクラス"""

    def setup_method(self):
        """テスト前の設定"""
        self.test_results: Dict[str, Any] = {}
        self.warnings_list: List[str] = []

    def test_system_architecture(self):
        """システムアーキテクチャの確認"""
        # Pythonのビット数を確認
        python_bits = struct.calcsize("P") * 8

        # システム情報を取得
        system_info = {
            "python_bits": python_bits,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "architecture": platform.architecture(),
            "processor": platform.processor(),
            "python_version": sys.version,
            "python_executable": sys.executable,
        }

        self.test_results["system_info"] = system_info

        print(f"Python bit: {python_bits}")
        print(f"Platform: {platform.platform()}")
        print(f"Machine: {platform.machine()}")
        print(f"Architecture: {platform.architecture()}")

        # 32bitシステムでの動作確認
        if python_bits == 32:
            print("✓ 32bit Python環境で動作中")
        else:
            print(f"⚠ {python_bits}bit Python環境で動作中")

        assert python_bits in [
            32,
            64,
        ], f"サポートされていないアーキテクチャ: {python_bits}bit"

    def test_memory_constraints(self):
        """メモリ制限の確認"""
        try:
            # 使用可能メモリの確認
            memory = psutil.virtual_memory()
            available_memory_gb = memory.available / (1024**3)
            total_memory_gb = memory.total / (1024**3)

            memory_info = {
                "total_memory_gb": total_memory_gb,
                "available_memory_gb": available_memory_gb,
                "memory_percent": memory.percent,
            }

            self.test_results["memory_info"] = memory_info

            print(f"総メモリ: {total_memory_gb:.2f} GB")
            print(f"利用可能メモリ: {available_memory_gb:.2f} GB")
            print(f"メモリ使用率: {memory.percent:.1f}%")

            # 32bitシステムでは通常4GB未満
            python_bits = struct.calcsize("P") * 8
            if python_bits == 32:
                # 32bit環境では通常2-4GBの制限
                if total_memory_gb > 4:
                    self.warnings_list.append(
                        "32bit環境で4GB超のメモリが検出されました"
                    )

                # 利用可能メモリが少ない場合の警告
                if available_memory_gb < 1:
                    self.warnings_list.append("利用可能メモリが1GB未満です")

            assert (
                available_memory_gb > 0.5
            ), f"利用可能メモリが不足: {available_memory_gb:.2f} GB"

        except Exception as e:
            pytest.fail(f"メモリ情報の取得に失敗: {e}")

    def test_pandas_compatibility(self):
        """Pandasの32bit互換性テスト"""
        try:
            # Pandasのバージョン確認
            pandas_version = pd.__version__
            numpy_version = np.__version__

            print(f"Pandas version: {pandas_version}")
            print(f"NumPy version: {numpy_version}")

            # バージョンチェック（32bit互換性）
            pandas_major_minor = tuple(map(int, pandas_version.split(".")[:2]))
            numpy_major_minor = tuple(map(int, numpy_version.split(".")[:2]))

            # 32bit対応バージョンの確認
            if pandas_major_minor >= (2, 3):
                self.warnings_list.append(
                    f"Pandas {pandas_version}は32bit Windows互換性に問題がある可能性があります"
                )

            if numpy_major_minor >= (1, 25):
                self.warnings_list.append(
                    f"NumPy {numpy_version}は32bit Windows互換性に問題がある可能性があります"
                )

            # 基本的なPandas操作のテスト
            df = pd.DataFrame(
                {
                    "id": range(1000),
                    "value": np.random.rand(1000),
                    "category": ["A", "B", "C"] * 333 + ["A"],
                }
            )

            # メモリ使用量チェック
            memory_usage = df.memory_usage(deep=True).sum()
            print(f"DataFrame memory usage: {memory_usage / 1024:.2f} KB")

            # 基本操作のテスト
            result = df.groupby("category")["value"].mean()
            assert len(result) == 3, "Pandas groupby操作に失敗"

            self.test_results["pandas_test"] = {
                "version": pandas_version,
                "numpy_version": numpy_version,
                "memory_usage_kb": memory_usage / 1024,
                "basic_operations": "OK",
            }

            print("✓ Pandas基本操作テスト成功")

        except Exception as e:
            pytest.fail(f"Pandas互換性テストに失敗: {e}")

    def test_tkinter_compatibility(self):
        """Tkinter GUI の32bit互換性テスト"""
        try:
            # Tkinterの基本テスト（非表示ウィンドウ）
            root = tk.Tk()
            root.withdraw()  # ウィンドウを非表示にする

            # 基本ウィジェットの作成テスト
            frame = tk.Frame(root)
            label = tk.Label(frame, text="Test Label")
            entry = tk.Entry(frame)
            button = tk.Button(frame, text="Test Button")
            canvas = tk.Canvas(frame, width=100, height=100)

            # ウィジェットの配置テスト
            frame.pack()
            label.pack()
            entry.pack()
            button.pack()
            canvas.pack()

            # Canvas描画テスト
            canvas.create_rectangle(10, 10, 50, 50, fill="blue")
            canvas.create_text(25, 75, text="Test")

            # メモリ使用量の確認
            root.update_idletasks()

            # クリーンアップ
            root.destroy()

            self.test_results["tkinter_test"] = {
                "basic_widgets": "OK",
                "canvas_drawing": "OK",
            }

            print("✓ Tkinter基本機能テスト成功")

        except Exception as e:
            pytest.fail(f"Tkinter互換性テストに失敗: {e}")

    def test_pil_compatibility(self):
        """PIL/Pillowの32bit互換性テスト"""
        try:
            from PIL import Image, ImageTk, ImageDraw, ImageFont

            pillow_version = Image.__version__
            print(f"Pillow version: {pillow_version}")

            # バージョンチェック
            pillow_major_minor = tuple(map(int, pillow_version.split(".")[:2]))
            if pillow_major_minor >= (11, 0):
                print(f"✓ Pillow {pillow_version} (最新版)")

            # 基本的な画像操作テスト
            # 小さなテスト画像を作成
            test_image = Image.new("RGB", (100, 100), color="red")

            # 画像変換テスト
            resized = test_image.resize((50, 50))
            thumbnail = test_image.copy()
            thumbnail.thumbnail((25, 25))

            # 描画テスト
            draw = ImageDraw.Draw(test_image)
            draw.rectangle([10, 10, 40, 40], fill="blue")
            draw.text((50, 50), "Test", fill="white")

            # メモリ使用量チェック
            memory_estimate = test_image.size[0] * test_image.size[1] * 3  # RGB
            print(f"Test image memory estimate: {memory_estimate} bytes")

            self.test_results["pil_test"] = {
                "version": pillow_version,
                "basic_operations": "OK",
                "memory_estimate": memory_estimate,
            }

            print("✓ PIL/Pillow基本機能テスト成功")

        except Exception as e:
            pytest.fail(f"PIL/Pillow互換性テストに失敗: {e}")

    def test_file_operations(self):
        """ファイル操作の32bit互換性テスト"""
        try:
            import tempfile
            import os
            import configparser

            # 一時ディレクトリでのテスト
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # CSVファイル書き込みテスト
                csv_file = temp_path / "test.csv"
                test_df = pd.DataFrame(
                    {
                        "id": range(100),
                        "name": [f"item_{i}" for i in range(100)],
                        "value": np.random.rand(100),
                    }
                )

                test_df.to_csv(csv_file, index=False, encoding="utf-8-sig")

                # CSVファイル読み込みテスト
                loaded_df = pd.read_csv(csv_file, encoding="utf-8-sig")
                assert len(loaded_df) == 100, "CSV読み書きテストに失敗"

                # 設定ファイルテスト
                config = configparser.ConfigParser()
                config["DIRECTORIES"] = {
                    "image_directory": "C:/test/images",
                    "data_directory": "C:/test/data",
                }

                config_file = temp_path / "settings.ini"
                with open(config_file, "w", encoding="utf-8") as f:
                    config.write(f)

                # 設定ファイル読み込みテスト
                config_read = configparser.ConfigParser()
                config_read.read(config_file, encoding="utf-8")

                assert (
                    "DIRECTORIES" in config_read.sections()
                ), "設定ファイルテストに失敗"

                # ファイルサイズチェック
                csv_size = csv_file.stat().st_size
                config_size = config_file.stat().st_size

                self.test_results["file_operations"] = {
                    "csv_read_write": "OK",
                    "config_read_write": "OK",
                    "csv_size_bytes": csv_size,
                    "config_size_bytes": config_size,
                }

                print("✓ ファイル操作テスト成功")

        except Exception as e:
            pytest.fail(f"ファイル操作テストに失敗: {e}")

    def test_threading_compatibility(self):
        """マルチスレッドの32bit互換性テスト"""
        try:
            import threading
            import time
            from concurrent.futures import ThreadPoolExecutor

            results = []

            def test_thread_function(thread_id):
                """テスト用のスレッド関数"""
                time.sleep(0.1)  # 短時間の処理をシミュレート
                return f"Thread {thread_id} completed"

            # ThreadPoolExecutorテスト
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = [executor.submit(test_thread_function, i) for i in range(5)]
                for future in futures:
                    result = future.result(timeout=5)
                    results.append(result)

            assert len(results) == 5, "マルチスレッドテストに失敗"

            # 基本的なThreadingテスト
            def simple_thread_test():
                time.sleep(0.1)
                results.append("Simple thread test")

            thread = threading.Thread(target=simple_thread_test)
            thread.start()
            thread.join(timeout=5)

            self.test_results["threading_test"] = {
                "thread_pool_executor": "OK",
                "basic_threading": "OK",
                "results_count": len(results),
            }

            print("✓ マルチスレッドテスト成功")

        except Exception as e:
            pytest.fail(f"マルチスレッドテストに失敗: {e}")

    def test_dependency_versions(self):
        """依存関係のバージョン確認"""
        try:
            dependencies = {
                "pandas": pd.__version__,
                "numpy": np.__version__,
                "PIL": Image.__version__,
                "tkinter": tk.TkVersion,
                "python": sys.version.split()[0],
                "platform": platform.platform(),
            }

            # psutilバージョンの取得
            try:
                dependencies["psutil"] = psutil.__version__
            except AttributeError:
                dependencies["psutil"] = "unknown"

            self.test_results["dependencies"] = dependencies

            print("\n=== 依存関係バージョン ===")
            for name, version in dependencies.items():
                print(f"{name}: {version}")

            # 32bit推奨バージョンのチェック
            python_bits = struct.calcsize("P") * 8
            if python_bits == 32:
                recommendations = []

                # Pandasの推奨バージョン
                pandas_major_minor = tuple(
                    map(int, dependencies["pandas"].split(".")[:2])
                )
                if pandas_major_minor >= (2, 3):
                    recommendations.append("Pandas: < 2.0.0 推奨 (32bit互換性)")

                # NumPyの推奨バージョン
                numpy_major_minor = tuple(
                    map(int, dependencies["numpy"].split(".")[:2])
                )
                if numpy_major_minor >= (1, 25):
                    recommendations.append("NumPy: < 1.25.0 推奨 (32bit互換性)")

                if recommendations:
                    print("\n=== 32bit Windows推奨バージョン ===")
                    for rec in recommendations:
                        print(f"⚠ {rec}")
                        self.warnings_list.append(rec)

        except Exception as e:
            pytest.fail(f"依存関係バージョン確認に失敗: {e}")

    def test_large_data_handling(self):
        """大容量データ処理の32bit対応テスト"""
        try:
            python_bits = struct.calcsize("P") * 8

            # 32bit環境での制限を考慮したテストサイズ
            if python_bits == 32:
                test_size = 10000  # 32bitでは小さめのサイズ
                memory_limit_mb = 512  # 512MB制限
            else:
                test_size = 50000  # 64bitではより大きなサイズ
                memory_limit_mb = 1024  # 1GB制限

            print(
                f"大容量データテスト (サイズ: {test_size}, メモリ制限: {memory_limit_mb}MB)"
            )

            # 大きなDataFrameの作成と処理
            large_df = pd.DataFrame(
                {
                    "id": range(test_size),
                    "value1": np.random.rand(test_size),
                    "value2": np.random.rand(test_size),
                    "category": np.random.choice(["A", "B", "C"], test_size),
                    "text": [f"item_{i:06d}" for i in range(test_size)],
                }
            )

            # メモリ使用量チェック
            memory_usage_mb = large_df.memory_usage(deep=True).sum() / (1024**2)
            print(f"DataFrame memory usage: {memory_usage_mb:.2f} MB")

            # メモリ制限チェック
            if memory_usage_mb > memory_limit_mb:
                self.warnings_list.append(
                    f"大容量データのメモリ使用量が制限を超過: {memory_usage_mb:.2f} MB > {memory_limit_mb} MB"
                )

            # 基本的な集計処理
            grouped = large_df.groupby("category").agg(
                {"value1": ["mean", "sum"], "value2": ["min", "max"]}
            )

            assert len(grouped) == 3, "大容量データ集計処理に失敗"

            self.test_results["large_data_test"] = {
                "test_size": test_size,
                "memory_usage_mb": memory_usage_mb,
                "memory_limit_mb": memory_limit_mb,
                "processing": "OK",
            }

            print("✓ 大容量データ処理テスト成功")

        except MemoryError as e:
            pytest.fail(f"メモリ不足: {e}")
        except Exception as e:
            pytest.fail(f"大容量データ処理テストに失敗: {e}")

    def teardown_method(self):
        """テスト後のクリーンアップ"""
        # テスト結果のサマリー出力
        print("\n" + "=" * 50)
        print("32bit Windows 互換性テスト結果")
        print("=" * 50)

        # システム情報
        if "system_info" in self.test_results:
            sys_info = self.test_results["system_info"]
            print(f"Python: {sys_info['python_bits']}bit")
            print(f"Platform: {sys_info['platform']}")

        # メモリ情報
        if "memory_info" in self.test_results:
            mem_info = self.test_results["memory_info"]
            print(
                f"Memory: {mem_info['total_memory_gb']:.2f}GB total, {mem_info['available_memory_gb']:.2f}GB available"
            )

        # 警告一覧
        if self.warnings_list:
            print("\n⚠ 警告:")
            for warning in self.warnings_list:
                print(f"  - {warning}")
        else:
            print("\n✓ 警告なし")

        # 全体的な互換性判定
        python_bits = struct.calcsize("P") * 8
        if python_bits == 32:
            if len(self.warnings_list) == 0:
                print("\n✅ 32bit Windows 完全対応")
            elif len(self.warnings_list) <= 2:
                print("\n⚠️  32bit Windows 部分対応 (警告あり)")
            else:
                print("\n❌ 32bit Windows 対応に問題あり")
        else:
            print(f"\n📝 {python_bits}bit環境での動作確認済み")


if __name__ == "__main__":
    # スタンドアローン実行用
    test_instance = Test32BitCompatibility()

    try:
        test_instance.setup_method()

        print("32bit Windows 互換性テストを開始します...\n")

        # 各テストを実行
        test_methods = [
            test_instance.test_system_architecture,
            test_instance.test_memory_constraints,
            test_instance.test_pandas_compatibility,
            test_instance.test_tkinter_compatibility,
            test_instance.test_pil_compatibility,
            test_instance.test_file_operations,
            test_instance.test_threading_compatibility,
            test_instance.test_dependency_versions,
            test_instance.test_large_data_handling,
        ]

        for test_method in test_methods:
            try:
                print(f"\n--- {test_method.__name__} ---")
                test_method()
            except Exception as e:
                print(f"❌ {test_method.__name__} failed: {e}")

        test_instance.teardown_method()

    except Exception as e:
        print(f"テスト実行中にエラーが発生しました: {e}")
