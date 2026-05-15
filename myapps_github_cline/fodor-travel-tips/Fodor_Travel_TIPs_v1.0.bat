g@echo off
REM ============================================
REM  Fodor Travel TIPs v1.0 - LAUNCHER
REM  Double-click to start the app!
REM ============================================
echo.
echo  ✈️  FODOR TRAVEL TIPs v1.0
echo  ================================
echo  Starting server...
echo.

cd /d "%~dp0backend"
start "" "http://localhost:5000"
python app.py

pause