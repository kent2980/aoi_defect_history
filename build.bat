@echo off
rem Windows用ビルドスクリプト（自動アーキテクチャ判定）
echo AOI Defect History ビルドスクリプト
echo ================================

rem Pythonのアーキテクチャを確認
python -c "import struct; exit(0 if struct.calcsize('P') == 4 else 1)" >nul 2>&1
if %errorlevel% == 0 (
    set TARGET_ARCH=x86
    set ARCH_NAME=win32
    echo 32bit Python環境を検出しました
) else (
    set TARGET_ARCH=x64
    set ARCH_NAME=win64
    echo 64bit Python環境を検出しました
)

echo ビルドアーキテクチャ: %TARGET_ARCH% (%ARCH_NAME%)
echo.

rem 仮想環境の確認（オプション）
if not exist ".venv" (
    echo 警告: 仮想環境が見つかりません
    echo uv sync を実行することを推奨します
    echo.
)

rem クリーンビルド
echo 以前のビルドファイルを削除中...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

rem 環境変数を設定
set TARGET_ARCH=%TARGET_ARCH%

rem PyInstallerでビルド (specファイル使用)
echo ビルド中...
if exist "uv.exe" (
    uv run pyinstaller --clean --noconfirm pyinstaller.spec
) else (
    pyinstaller --clean --noconfirm pyinstaller.spec
)

rem 結果確認
if exist "dist\aoi-defect-history-%ARCH_NAME%\aoi-defect-history-%ARCH_NAME%.exe" (
    echo.
    echo ✓ ビルド成功！
    echo 実行ファイル: dist\aoi-defect-history-%ARCH_NAME%\aoi-defect-history-%ARCH_NAME%.exe
    dir "dist\aoi-defect-history-%ARCH_NAME%\aoi-defect-history-%ARCH_NAME%.exe"
) else (
    echo.
    echo ✗ ビルド失敗
    echo ログを確認してください: build\pyinstaller\warn-pyinstaller.txt
)

echo.
pause