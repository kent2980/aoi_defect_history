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

rem PyInstallerでビルド (specファイル使用)
echo ビルド中...
uv run pyinstaller pyinstaller.spec

rem 結果確認
if exist "dist\aoi-defect-history-win64.exe" (
    echo.
    echo ✓ ビルド成功！
    echo 実行ファイル: dist\aoi-defect-history-win64.exe
    dir "dist\aoi-defect-history-win64.exe"
) else (
    echo.
    echo ✗ ビルド失敗
    echo ログを確認してください
)

echo.
pause