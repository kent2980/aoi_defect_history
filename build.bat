@echo off
rem Windows用ビルドスクリプト
echo AOI Defect History ビルドスクリプト
echo ================================

rem 仮想環境の確認
if not exist ".venv" (
    echo エラー: 仮想環境が見つかりません
    echo uv sync を実行してください
    pause
    exit /b 1
)

rem クリーンビルド
echo 以前のビルドファイルを削除中...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del "*.spec"

rem PyInstallerでビルド
echo ビルド中...
uv run pyinstaller --onefile --windowed --name=aoi-defect-history main.py

rem 結果確認
if exist "dist\aoi-defect-history.exe" (
    echo.
    echo ✓ ビルド成功！
    echo 実行ファイル: dist\aoi-defect-history.exe
    dir "dist\aoi-defect-history.exe"
) else (
    echo.
    echo ✗ ビルド失敗
    echo ログを確認してください
)

echo.
pause