@echo off
rem 64bit Windows用ビルドスクリプト
echo AOI Defect History 64bit ビルドスクリプト
echo ================================

rem Pythonのアーキテクチャを確認
python -c "import struct; exit(0 if struct.calcsize('P') == 8 else 1)" >nul 2>&1
if %errorlevel% == 1 (
    echo.
    echo ❌ エラー: 64bit Python環境が必要です
    echo 現在のPython環境を確認してください:
    python -c "import struct; print(f'Python {struct.calcsize(\"P\") * 8}bit')"
    echo.
    pause
    exit /b 1
)

echo ✅ 64bit Python環境を確認しました
echo.

rem クリーンビルド
echo 以前のビルドファイルを削除中...
if exist "build" rmdir /s /q "build"
if exist "dist\aoi-defect-history-win64" rmdir /s /q "dist\aoi-defect-history-win64"

rem 環境変数を設定
set TARGET_ARCH=x64

rem PyInstallerでビルド
echo 64bit実行ファイルをビルド中...
if exist "uv.exe" (
    uv run pyinstaller --clean --noconfirm pyinstaller.spec
) else (
    pyinstaller --clean --noconfirm pyinstaller.spec
)

rem 結果確認
if exist "dist\aoi-defect-history-win64\aoi-defect-history-win64.exe" (
    echo.
    echo ✅ ビルド成功！
    echo.
    echo 実行ファイル: dist\aoi-defect-history-win64\aoi-defect-history-win64.exe
    echo.
    dir "dist\aoi-defect-history-win64\aoi-defect-history-win64.exe"
) else (
    echo.
    echo ❌ ビルド失敗
    echo.
    echo トラブルシューティング:
    echo 1. ログを確認: build\pyinstaller\warn-pyinstaller.txt
    echo 2. エラーログを確認: error.log
)

echo.
pause

