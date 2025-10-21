"""
GitHub Actions ワークフロー設定確認スクリプト

このスクリプトは、GitHub Actionsのワークフローファイルが正しく設定されているかを確認します。
"""

import yaml
import sys
from pathlib import Path


def check_workflow_file():
    """GitHub Actionsワークフローファイルの確認"""
    workflow_file = Path(".github/workflows/build-windows.yml")

    print("🔍 GitHub Actions ワークフロー設定確認")
    print("=" * 50)

    if not workflow_file.exists():
        print(f"❌ ワークフローファイルが見つかりません: {workflow_file}")
        return False

    print(f"✅ ワークフローファイル: {workflow_file}")

    try:
        with open(workflow_file, "r", encoding="utf-8") as f:
            workflow = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ YAML解析エラー: {e}")
        return False

    print("✅ YAML構文: 正常")

    # YAMLの仕様により、'on'はTrueに変換される可能性があるため、両方チェック
    # GitHub ActionsのYAMLでは'on'キーワードを使用
    on_key = "on" if "on" in workflow else True if True in workflow else None

    # 基本構造の確認
    required_keys = ["name", "jobs"]
    for key in required_keys:
        if key not in workflow:
            print(f"❌ 必須キー不足: {key}")
            return False

    # 'on'キーの確認（TrueまたはONとして解釈される可能性）
    if on_key is None:
        print(f"❌ 必須キー不足: on (トリガー設定)")
        return False

    print("✅ 基本構造: 正常")

    # ジョブの確認
    jobs = workflow.get("jobs", {})
    expected_jobs = ["test", "build", "release", "cleanup"]

    print(f"\n📋 ジョブ確認:")
    for job_name in expected_jobs:
        if job_name in jobs:
            print(f"  ✅ {job_name}")
        else:
            print(f"  ⚠️  {job_name} (オプション)")

    # ビルドジョブの詳細確認
    if "build" in jobs:
        build_job = jobs["build"]

        print(f"\n🔧 ビルドジョブ詳細:")

        # マトリックス戦略の確認
        if "strategy" in build_job and "matrix" in build_job["strategy"]:
            matrix = build_job["strategy"]["matrix"]
            if "include" in matrix:
                architectures = [item.get("architecture") for item in matrix["include"]]
                print(f"  アーキテクチャ: {architectures}")

                if "x86" in architectures and "x64" in architectures:
                    print("  ✅ 32bit/64bit両対応")
                elif "x64" in architectures:
                    print("  ⚠️  64bitのみ")
                elif "x86" in architectures:
                    print("  ⚠️  32bitのみ")
                else:
                    print("  ❌ アーキテクチャ未設定")

        # ステップの確認
        steps = build_job.get("steps", [])
        step_names = [step.get("name", "unnamed") for step in steps]

        important_steps = [
            "Checkout code",
            "Set up Python",
            "Install uv",
            "Install dependencies",
            "Build with PyInstaller",
            "Verify executable",
            "Create distribution package",
            "Upload artifacts",
        ]

        print(f"\n📝 ビルドステップ確認:")
        for step in important_steps:
            if any(step in step_name for step_name in step_names):
                print(f"  ✅ {step}")
            else:
                print(f"  ❌ {step}")

    # 環境変数の確認
    if "env" in workflow:
        env_vars = workflow["env"]
        print(f"\n🌍 環境変数:")
        for key, value in env_vars.items():
            print(f"  {key}: {value}")

    # トリガー条件の確認
    on_conditions = workflow.get(on_key, {})
    print(f"\n🚀 トリガー条件:")

    if isinstance(on_conditions, dict):
        for trigger, config in on_conditions.items():
            if trigger == "push":
                branches = (
                    config.get("branches", []) if isinstance(config, dict) else []
                )
                tags = config.get("tags", []) if isinstance(config, dict) else []
                print(f"  プッシュ: ブランチ{branches}, タグ{tags}")
            elif trigger == "pull_request":
                branches = (
                    config.get("branches", []) if isinstance(config, dict) else []
                )
                print(f"  プルリクエスト: ブランチ{branches}")
            elif trigger == "workflow_dispatch":
                print(f"  手動実行: 有効")
            else:
                print(f"  {trigger}: {config}")
    elif isinstance(on_conditions, list):
        for trigger in on_conditions:
            print(f"  {trigger}")

    print(f"\n✅ ワークフロー設定確認完了")
    return True


def check_required_files():
    """必要なファイルの存在確認"""
    print(f"\n📁 必要ファイル確認:")

    required_files = [
        "main.py",
        "pyinstaller.spec",
        "version_info.txt",
        "src/aoi_view.py",
        "defect_mapping.csv",
        "user.csv",
    ]

    optional_files = ["assets/icon.ico", "LICENSE", "README.md", "CHANGELOG.md"]

    all_good = True

    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (必須)")
            all_good = False

    for file_path in optional_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path} (オプション)")
        else:
            print(f"  ⚠️  {file_path} (オプション)")

    return all_good


def check_pyproject_toml():
    """pyproject.tomlの確認"""
    print(f"\n⚙️  pyproject.toml確認:")

    pyproject_file = Path("pyproject.toml")
    if not pyproject_file.exists():
        print(f"  ❌ pyproject.toml が見つかりません")
        return False

    try:
        import toml

        with open(pyproject_file, "r", encoding="utf-8") as f:
            config = toml.load(f)
    except ImportError:
        print(f"  ⚠️  tomlモジュールが必要です (pip install toml)")
        return True
    except Exception as e:
        print(f"  ❌ 読み込みエラー: {e}")
        return False

    # 依存関係の確認
    dependencies = config.get("dependencies", [])

    required_deps = ["pandas", "pillow", "requests"]
    optional_deps = ["psutil", "openpyxl"]

    print(f"  依存関係:")
    for dep in required_deps:
        if any(dep in d.lower() for d in dependencies):
            print(f"    ✅ {dep}")
        else:
            print(f"    ❌ {dep} (必須)")

    for dep in optional_deps:
        if any(dep in d.lower() for d in dependencies):
            print(f"    ✅ {dep} (オプション)")
        else:
            print(f"    ⚠️  {dep} (オプション)")

    # 開発依存関係の確認
    dev_deps = config.get("dev-dependencies", [])
    if "pyinstaller" in str(dev_deps).lower():
        print(f"    ✅ pyinstaller (開発用)")
    else:
        print(f"    ⚠️  pyinstaller (開発用)")

    return True


def main():
    """メイン実行関数"""
    print("🔍 GitHub Actions ビルド設定確認")
    print("=" * 60)

    results = {
        "workflow": check_workflow_file(),
        "files": check_required_files(),
        "pyproject": check_pyproject_toml(),
    }

    print(f"\n{'='*60}")
    print("確認結果サマリー")
    print(f"{'='*60}")

    for check_name, result in results.items():
        status = "✅ OK" if result else "❌ NG"
        print(f"  {check_name}: {status}")

    all_good = all(results.values())

    if all_good:
        print(f"\n🎉 すべての確認項目がOKです！")
        print(f"GitHub Actionsでのビルドが正常に実行される可能性が高いです。")
        return 0
    else:
        print(f"\n⚠️  一部の確認項目で問題が見つかりました。")
        print(f"GitHub Actionsでのビルドが失敗する可能性があります。")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
