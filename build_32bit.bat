@echo off
rem 32bit Windows用ビルドスクリプト
echo AOI Defect History 32bit ビルドスクリプト
echo ================================

rem Pythonのアーキテクチャを確認
python -c "import struct; exit(0 if struct.calcsize('P') == 4 else 1)" >nul 2>&1
if %errorlevel% == 1 (
    echo.
    echo ❌ エラー: 32bit Python環境が必要です
    echo 現在のPython環境を確認してください:
    python -c "import struct; print(f'Python {struct.calcsize(\"P\") * 8}bit')"
    echo.
    echo 32bit Pythonをインストールするか、環境を切り替えてください
    pause
    exit /b 1
)

echo ✅ 32bit Python環境を確認しました
echo.

rem セットアップ検証（オプション）
if exist "scripts\verify_32bit_setup.py" (
    echo セットアップを検証中...
    python scripts\verify_32bit_setup.py
    if %errorlevel% == 1 (
        echo.
        echo ⚠️  警告: セットアップに問題がある可能性があります
        echo ビルドを続行しますか？ (Y/N)
        set /p continue=
        if /i not "%continue%"=="Y" exit /b 1
    )
    echo.
)

rem クリーンビルド
echo 以前のビルドファイルを削除中...
if exist "build" rmdir /s /q "build"
if exist "dist\aoi-defect-history-win32" rmdir /s /q "dist\aoi-defect-history-win32"

rem 環境変数を設定
set TARGET_ARCH=x86

rem PyInstallerでビルド
echo 32bit実行ファイルをビルド中...
if exist "uv.exe" (
    uv run pyinstaller --clean --noconfirm pyinstaller.spec
) else (
    pyinstaller --clean --noconfirm pyinstaller.spec
)

rem 結果確認
if exist "dist\aoi-defect-history-win32\aoi-defect-history-win32.exe" (
    echo.
    echo ✅ ビルド成功！
    echo.
    echo 実行ファイル: dist\aoi-defect-history-win32\aoi-defect-history-win32.exe
    echo.
    dir "dist\aoi-defect-history-win32\aoi-defect-history-win32.exe"
    echo.
    echo 次のステップ:
    echo 1. 32bit互換性テストを実行: python tests\run_32bit_tests.py
    echo 2. 実行ファイルをテスト: dist\aoi-defect-history-win32\aoi-defect-history-win32.exe
) else (
    echo.
    echo ❌ ビルド失敗
    echo.
    echo トラブルシューティング:
    echo 1. ログを確認: build\pyinstaller\warn-pyinstaller.txt
    echo 2. セットアップを検証: python scripts\verify_32bit_setup.py
    echo 3. エラーログを確認: error.log
)

echo.
pause

