@echo off
title My Travel Tips - Starting...
echo.
echo ============================================
echo   MY TRAVEL TIPS - Starting Application
echo ============================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python nie je nainstalovany alebo nie je v PATH.
    echo         Nainštalujte Python z https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: Navigate to backend directory
cd /d "%~dp0backend"

:: Install dependencies if needed (quick check)
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalujem zavislosti...
    pip install -r requirements.txt
    echo.
)

echo [INFO] Spustam server...
echo [INFO] Aplikacia bude dostupna na: http://localhost:5000
echo [INFO] Pre zatvorenie stlacte Ctrl+C
echo.

:: Open browser after short delay
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:5000"

:: Start Flask server
python app.py