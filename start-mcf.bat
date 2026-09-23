@echo off
title MCF - Multimodal Content Factory

echo.
echo ==========================================
echo     MCF - Multimodal Content Factory
echo ==========================================
echo.

echo [1/3] Starting PostgreSQL...
docker start mcf_postgres >nul 2>&1

if errorlevel 1 (
    echo PostgreSQL container not found/running.
    echo Please make sure Docker Desktop is running.
    pause
    exit /b 1
)

echo PostgreSQL started.
echo.

echo [2/3] Starting Backend...
start "MCF Backend" cmd /k "cd /d %~dp0backend && venv\Scripts\activate && python -m uvicorn app.main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo [3/3] Starting Frontend...
start "MCF Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ==========================================
echo     MCF is starting...
echo ==========================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Keep the two terminal windows open.
echo.

timeout /t 5
start http://localhost:3000

exit