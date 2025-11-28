@echo off
chcp 65001 > nul

REM ============================================
REM AppUninstaller.bat
REM 使用 uv + PowerShell 清理 uv 環境與 uv 本身
REM ============================================

echo Running: uv cache clean
powershell -Command "uv cache clean"

echo Running: remove Python directory from uv
powershell -Command "rm -r \"$(uv python dir)\""

echo Running: remove uv tool directory
powershell -Command "rm -r \"$(uv tool dir)\""

echo Running: remove uv.exe
powershell -Command "rm $HOME\.local\bin\uv.exe"

echo Running: remove uvx.exe
powershell -Command "rm $HOME\.local\bin\uvx.exe"

echo.
echo Uninstall finished. Press Enter to exit.
echo 卸載完成，按 Enter 離開。
pause
