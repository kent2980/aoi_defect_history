"""
32bit Windows パフォーマンステスト

このテストファイルは、32bit環境でのパフォーマンスを測定し、
実用的な性能を確保できることを確認します。
"""

import time
import sys
import struct
import platform
import psutil
import pandas as pd
import numpy as np
import tkinter as tk
from PIL import Image, ImageDraw
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
from typing import Dict, List, Tuple
import gc


class Test32BitPerformance:
    """32bit Windows パフォーマンステストクラス"""

    def __init__(self):
        self.results: Dict[str, Dict] = {}
        self.python_bits = struct.calcsize("P") * 8
        self.is_32bit = self.python_bits == 32

    def measure_time(self, func, *args, **kwargs):
        """関数の実行時間を測定"""
        gc.collect()  # ガベージコレクションを実行
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        return result, execution_time

    def test_dataframe_performance(self):
        """DataFrame操作のパフォーマンステスト"""
        print("DataFrame操作パフォーマンステスト...")

        # テストサイズを32bit環境に合わせて調整
        if self.is_32bit:
            small_size = 1000
            medium_size = 5000
            large_size = 10000
        else:
            small_size = 5000
            medium_size = 25000
            large_size = 50000

        tests = {"small": small_size, "medium": medium_size, "large": large_size}

        results = {}

        for test_name, size in tests.items():
            print(f"  {test_name} size ({size} rows)...")

            # DataFrame作成時間
            def create_df():
                return pd.DataFrame(
                    {
                        "id": range(size),
                        "value1": np.random.rand(size),
                        "value2": np.random.rand(size),
                        "category": np.random.choice(["A", "B", "C", "D"], size),
                        "text": [f"item_{i:06d}" for i in range(size)],
                    }
                )

            df, create_time = self.measure_time(create_df)

            # グループ化時間
            def group_operations():
                return df.groupby("category").agg(
                    {
                        "value1": ["mean", "sum", "std"],
                        "value2": ["min", "max", "count"],
                    }
                )

            grouped, group_time = self.measure_time(group_operations)

            # ソート時間
            def sort_operations():
                return df.sort_values(["category", "value1"])

            sorted_df, sort_time = self.measure_time(sort_operations)

            # フィルタリング時間
            def filter_operations():
                return df[df["value1"] > 0.5]

            filtered_df, filter_time = self.measure_time(filter_operations)

            # メモリ使用量
            memory_usage = df.memory_usage(deep=True).sum() / (1024**2)  # MB

            results[test_name] = {
                "size": size,
                "create_time": create_time,
                "group_time": group_time,
                "sort_time": sort_time,
                "filter_time": filter_time,
                "memory_mb": memory_usage,
                "total_time": create_time + group_time + sort_time + filter_time,
            }

            print(f"    作成: {create_time:.3f}s, グループ化: {group_time:.3f}s")
            print(f"    ソート: {sort_time:.3f}s, フィルタ: {filter_time:.3f}s")
            print(f"    メモリ: {memory_usage:.2f}MB")

            # メモリクリーンアップ
            del df, grouped, sorted_df, filtered_df
            gc.collect()

        self.results["dataframe_performance"] = results
        return results

    def test_image_processing_performance(self):
        """画像処理パフォーマンステスト"""
        print("画像処理パフォーマンステスト...")

        # テストサイズを32bit環境に合わせて調整
        if self.is_32bit:
            sizes = [(800, 600), (1024, 768), (1200, 900)]
        else:
            sizes = [(1024, 768), (1920, 1080), (2560, 1440)]

        results = {}

        for width, height in sizes:
            size_name = f"{width}x{height}"
            print(f"  画像サイズ {size_name}...")

            # 画像作成時間
            def create_image():
                return Image.new("RGB", (width, height), color="white")

            img, create_time = self.measure_time(create_image)

            # リサイズ時間
            def resize_image():
                return img.resize((width // 2, height // 2), Image.Resampling.LANCZOS)

            resized_img, resize_time = self.measure_time(resize_image)

            # 描画時間
            def draw_operations():
                draw_img = img.copy()
                draw = ImageDraw.Draw(draw_img)
                # 複数の図形を描画
                for i in range(10):
                    x1, y1 = i * 50, i * 30
                    x2, y2 = x1 + 100, y1 + 60
                    draw.rectangle([x1, y1, x2, y2], fill="red", outline="blue")
                    draw.text((x1 + 10, y1 + 10), f"Test {i}", fill="white")
                return draw_img

            drawn_img, draw_time = self.measure_time(draw_operations)

            # サムネイル作成時間
            def thumbnail_operations():
                thumb_img = img.copy()
                thumb_img.thumbnail((200, 150))
                return thumb_img

            thumb_img, thumb_time = self.measure_time(thumbnail_operations)

            # メモリ使用量推定（RGB: 3 bytes per pixel）
            memory_estimate = width * height * 3 / (1024**2)  # MB

            results[size_name] = {
                "width": width,
                "height": height,
                "create_time": create_time,
                "resize_time": resize_time,
                "draw_time": draw_time,
                "thumbnail_time": thumb_time,
                "memory_estimate_mb": memory_estimate,
                "total_time": create_time + resize_time + draw_time + thumb_time,
            }

            print(f"    作成: {create_time:.3f}s, リサイズ: {resize_time:.3f}s")
            print(f"    描画: {draw_time:.3f}s, サムネイル: {thumb_time:.3f}s")
            print(f"    推定メモリ: {memory_estimate:.2f}MB")

            # メモリクリーンアップ
            del img, resized_img, drawn_img, thumb_img
            gc.collect()

        self.results["image_performance"] = results
        return results

    def test_file_io_performance(self):
        """ファイルI/Oパフォーマンステスト"""
        print("ファイルI/Oパフォーマンステスト...")

        # テストサイズを32bit環境に合わせて調整
        if self.is_32bit:
            sizes = [100, 500, 1000]
        else:
            sizes = [1000, 5000, 10000]

        results = {}

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            for size in sizes:
                size_name = f"{size}_rows"
                print(f"  {size} rows...")

                # テストデータ作成
                test_df = pd.DataFrame(
                    {
                        "id": range(size),
                        "name": [f"item_{i:06d}" for i in range(size)],
                        "value1": np.random.rand(size),
                        "value2": np.random.rand(size),
                        "category": np.random.choice(["A", "B", "C"], size),
                        "timestamp": pd.date_range(
                            "2024-01-01", periods=size, freq="1min"
                        ),
                    }
                )

                csv_file = temp_path / f"test_{size}.csv"

                # CSV書き込み時間
                def write_csv():
                    test_df.to_csv(csv_file, index=False, encoding="utf-8-sig")

                _, write_time = self.measure_time(write_csv)

                # CSV読み込み時間
                def read_csv():
                    return pd.read_csv(csv_file, encoding="utf-8-sig")

                loaded_df, read_time = self.measure_time(read_csv)

                # ファイルサイズ取得
                file_size = csv_file.stat().st_size / 1024  # KB

                results[size_name] = {
                    "rows": size,
                    "write_time": write_time,
                    "read_time": read_time,
                    "file_size_kb": file_size,
                    "total_time": write_time + read_time,
                }

                print(f"    書込: {write_time:.3f}s, 読込: {read_time:.3f}s")
                print(f"    ファイルサイズ: {file_size:.2f}KB")

                # クリーンアップ
                del test_df, loaded_df
                gc.collect()

        self.results["file_io_performance"] = results
        return results

    def test_threading_performance(self):
        """マルチスレッドパフォーマンステスト"""
        print("マルチスレッドパフォーマンステスト...")

        def cpu_intensive_task(n):
            """CPU集約的なタスク"""
            total = 0
            for i in range(n):
                total += i**0.5
            return total

        # テストサイズを32bit環境に合わせて調整
        if self.is_32bit:
            task_size = 50000
            thread_counts = [1, 2, 3]
        else:
            task_size = 100000
            thread_counts = [1, 2, 4, 8]

        results = {}

        for thread_count in thread_counts:
            print(f"  {thread_count} threads...")

            # 単一タスクの時間測定
            def single_task():
                return cpu_intensive_task(task_size)

            _, single_time = self.measure_time(single_task)

            # マルチスレッドタスクの時間測定
            def multi_task():
                with ThreadPoolExecutor(max_workers=thread_count) as executor:
                    futures = [
                        executor.submit(cpu_intensive_task, task_size // thread_count)
                        for _ in range(thread_count)
                    ]
                    results = [future.result() for future in futures]
                return sum(results)

            _, multi_time = self.measure_time(multi_task)

            # 効率性の計算
            efficiency = single_time / multi_time if multi_time > 0 else 0

            results[f"{thread_count}_threads"] = {
                "thread_count": thread_count,
                "single_time": single_time,
                "multi_time": multi_time,
                "efficiency": efficiency,
                "speedup": efficiency,
            }

            print(f"    単一: {single_time:.3f}s, マルチ: {multi_time:.3f}s")
            print(f"    効率: {efficiency:.2f}x")

        self.results["threading_performance"] = results
        return results

    def test_gui_performance(self):
        """GUI描画パフォーマンステスト"""
        print("GUI描画パフォーマンステスト...")

        results = {}

        # Tkinter基本操作テスト
        def gui_operations():
            root = tk.Tk()
            root.withdraw()  # 非表示

            # ウィジェット作成時間
            start_time = time.perf_counter()

            frame = tk.Frame(root)
            canvas = tk.Canvas(frame, width=800, height=600)

            # 大量の図形描画
            for i in range(100):
                x1, y1 = i % 20 * 40, i // 20 * 30
                x2, y2 = x1 + 30, y1 + 20
                canvas.create_rectangle(x1, y1, x2, y2, fill="blue", outline="red")
                canvas.create_text(x1 + 15, y1 + 10, text=str(i))

            frame.pack()
            canvas.pack()

            # 更新処理
            root.update_idletasks()

            end_time = time.perf_counter()

            root.destroy()

            return end_time - start_time

        gui_time = gui_operations()

        results["gui_drawing"] = {
            "drawing_time": gui_time,
            "objects_drawn": 200,  # rectangles + texts
        }

        print(f"    GUI描画時間: {gui_time:.3f}s")

        self.results["gui_performance"] = results
        return results

    def test_memory_usage_pattern(self):
        """メモリ使用パターンテスト"""
        print("メモリ使用パターンテスト...")

        # 初期メモリ使用量
        initial_memory = psutil.Process().memory_info().rss / (1024**2)  # MB

        results = {
            "initial_memory_mb": initial_memory,
            "peak_memory_mb": initial_memory,
            "operations": [],
        }

        # 段階的にメモリを使用するテスト
        operations = [
            ("small_dataframe", lambda: pd.DataFrame(np.random.rand(1000, 10))),
            ("medium_dataframe", lambda: pd.DataFrame(np.random.rand(5000, 20))),
            (
                "large_dataframe",
                lambda: (
                    pd.DataFrame(np.random.rand(10000, 30))
                    if not self.is_32bit
                    else pd.DataFrame(np.random.rand(5000, 20))
                ),
            ),
            ("image_creation", lambda: Image.new("RGB", (1024, 768), "white")),
            (
                "numpy_array",
                lambda: (
                    np.random.rand(1000000)
                    if not self.is_32bit
                    else np.random.rand(500000)
                ),
            ),
        ]

        for op_name, operation in operations:
            print(f"  {op_name}...")

            # メモリ使用量測定
            before_memory = psutil.Process().memory_info().rss / (1024**2)

            # 操作実行
            start_time = time.perf_counter()
            try:
                result = operation()
                end_time = time.perf_counter()
                execution_time = end_time - start_time

                after_memory = psutil.Process().memory_info().rss / (1024**2)
                memory_increase = after_memory - before_memory

                results["operations"].append(
                    {
                        "operation": op_name,
                        "execution_time": execution_time,
                        "memory_before_mb": before_memory,
                        "memory_after_mb": after_memory,
                        "memory_increase_mb": memory_increase,
                    }
                )

                # ピークメモリ更新
                if after_memory > results["peak_memory_mb"]:
                    results["peak_memory_mb"] = after_memory

                print(
                    f"    実行時間: {execution_time:.3f}s, メモリ増加: {memory_increase:.2f}MB"
                )

                # メモリクリーンアップ
                del result
                gc.collect()

            except MemoryError as e:
                print(f"    メモリエラー: {e}")
                results["operations"].append(
                    {
                        "operation": op_name,
                        "error": "MemoryError",
                        "memory_before_mb": before_memory,
                    }
                )

        self.results["memory_usage"] = results
        return results

    def run_all_tests(self):
        """全てのパフォーマンステストを実行"""
        print(f"32bit Windows パフォーマンステスト開始 ({self.python_bits}bit Python)")
        print("=" * 60)

        # システム情報表示
        print(f"Platform: {platform.platform()}")
        print(f"Python: {sys.version}")
        memory = psutil.virtual_memory()
        print(f"Memory: {memory.total / (1024**3):.2f}GB total")
        print()

        # 各テストを実行
        test_methods = [
            self.test_dataframe_performance,
            self.test_image_processing_performance,
            self.test_file_io_performance,
            self.test_threading_performance,
            self.test_gui_performance,
            self.test_memory_usage_pattern,
        ]

        for test_method in test_methods:
            try:
                print()
                test_method()
            except Exception as e:
                print(f"❌ {test_method.__name__} failed: {e}")

        # 結果サマリー
        self.print_summary()

    def print_summary(self):
        """テスト結果のサマリーを表示"""
        print("\n" + "=" * 60)
        print("パフォーマンステスト結果サマリー")
        print("=" * 60)

        # 総合評価
        if self.is_32bit:
            print("🔧 32bit環境でのパフォーマンス評価")
        else:
            print(f"📊 {self.python_bits}bit環境でのパフォーマンス評価")

        # DataFrame性能
        if "dataframe_performance" in self.results:
            df_results = self.results["dataframe_performance"]
            print(f"\n📊 DataFrame処理:")
            for size, data in df_results.items():
                print(
                    f"  {size}: {data['total_time']:.3f}s ({data['memory_mb']:.1f}MB)"
                )

        # 画像処理性能
        if "image_performance" in self.results:
            img_results = self.results["image_performance"]
            print(f"\n🖼️  画像処理:")
            for size, data in img_results.items():
                print(
                    f"  {size}: {data['total_time']:.3f}s ({data['memory_estimate_mb']:.1f}MB)"
                )

        # ファイルI/O性能
        if "file_io_performance" in self.results:
            io_results = self.results["file_io_performance"]
            print(f"\n💾 ファイルI/O:")
            for size, data in io_results.items():
                print(
                    f"  {data['rows']} rows: {data['total_time']:.3f}s ({data['file_size_kb']:.1f}KB)"
                )

        # メモリ使用量
        if "memory_usage" in self.results:
            mem_results = self.results["memory_usage"]
            print(f"\n🧠 メモリ使用量:")
            print(f"  初期: {mem_results['initial_memory_mb']:.1f}MB")
            print(f"  ピーク: {mem_results['peak_memory_mb']:.1f}MB")
            print(
                f"  増加: {mem_results['peak_memory_mb'] - mem_results['initial_memory_mb']:.1f}MB"
            )

        # 32bit推奨事項
        if self.is_32bit:
            print(f"\n💡 32bit環境推奨事項:")
            print(f"  - DataFrameサイズ: 10,000行以下推奨")
            print(f"  - 画像サイズ: 1200x900px以下推奨")
            print(f"  - メモリ使用量: 512MB以下推奨")
            print(f"  - 並列処理: 2-3スレッド程度推奨")


if __name__ == "__main__":
    # パフォーマンステストを実行
    test_runner = Test32BitPerformance()
    test_runner.run_all_tests()
