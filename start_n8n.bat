@echo off
title n8n Workflow Automation Engine
echo ========================================================
echo Starting n8n Workflow Automation for Lead Intelligence
echo ========================================================
echo.

docker ps >nul 2>&1
if %ERRORLEVEL% EQU 0 goto DOCKER_READY

echo [INFO] Docker Desktop is not active. Launching Docker Desktop...
if exist "%LOCALAPPDATA%\Programs\DockerDesktop\Docker Desktop.exe" (
    start "" "%LOCALAPPDATA%\Programs\DockerDesktop\Docker Desktop.exe"
) else if exist "C:\Program Files\Docker\Docker\Docker Desktop.exe" (
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
)
echo Waiting for Docker engine to initialize...
set attempts=0

:WAIT_DOCKER
timeout /t 3 /nobreak >nul
docker ps >nul 2>&1
if %ERRORLEVEL% EQU 0 goto DOCKER_READY
set /a attempts+=1
echo [WAITING] Initializing Docker daemon - attempt %attempts% of 10
if %attempts% LSS 10 goto WAIT_DOCKER

echo [WARNING] Docker engine took too long. Falling back to Node.js / npx...
goto NODE_FALLBACK

:DOCKER_READY
echo [INFO] Docker engine active. Starting n8n container...
docker compose up -d n8n
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo [SUCCESS] n8n Workflow Engine is running!
    echo Webhook URL: http://localhost:5678/webhook/lead-alert
    echo Dashboard:   http://localhost:5678
    echo ========================================================
    start http://localhost:5678
    exit /b 0
)

:NODE_FALLBACK
echo.
echo [INFO] Starting n8n directly via Node.js / npx...
echo Dashboard will be available at: http://localhost:5678
echo.
npx -y n8n
pause
