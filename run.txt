@echo off
chcp 65001 > nul

REM ============================================
REM AppRun.bat
REM 1) 從網路安裝 uv
REM 2) 用 uv 安裝 Python
REM 3) 用 uv 同步依賴
REM 4) 執行 app.py
REM ============================================

echo [1] Installing uv from internet ...
powershell -ExecutionPolicy Bypass -NoProfile -Command "irm https://astral.sh/uv/install.ps1 | iex"
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to install uv. Exiting.
    echo 安裝 uv 失敗，程式結束。
    pause
    exit /b 1
)

REM 切換到當前批次檔所在目錄
cd /d "%~dp0"

echo [2] Installing Python via uv ...

uv python install 3.12
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to install Python via uv. Exiting.
    echo 透過 uv 安裝 Python 失敗，程式結束。
    pause
    exit /b 1
)

echo [3] Syncing dependencies with uv ...
cd python

uv sync
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to sync dependencies. Exiting.
    echo 依賴同步失敗，程式結束。
    pause
    exit /b 1
)

echo [4] Running app.py ...
uv run main.py

pause
