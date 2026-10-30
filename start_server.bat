@echo off
title Autonomous Lead Intelligence Server
echo ========================================================
echo Starting Autonomous Lead Intelligence Server (FastAPI)
echo ========================================================
echo.

cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Python virtual environment not found in venv\
    echo Please install dependencies first.
    pause
    exit /b 1
)

echo [1/2] Activating Python Virtual Environment...
call venv\Scripts\activate.bat

echo [2/2] Starting FastAPI Uvicorn Server on http://127.0.0.1:8000 ...
echo.
echo Dashboard URL: http://127.0.0.1:8000
echo Auto-Pilot Daemon: Running 24/7 in Background
echo (Press CTRL+C anytime to stop the server)
echo.

start "" "http://127.0.0.1:8000"
venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload

pause
