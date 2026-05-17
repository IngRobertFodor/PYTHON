@echo off

REM Find python.exe in WinPython folder (skip Scripts folder)
for /f "delims=" %%P in ('dir /s /b "%~dp0WinPython\python.exe" 2^>nul ^| findstr /i /v "Scripts"') do (
    set PYTHON=%%P
    goto run
)

REM Fallback to system Python
set PYTHON=python

:run
"%PYTHON%" "%~dp0main.py"
if errorlevel 1 (
    echo.
    echo ===================================
    echo  ERROR - App could not start.
    echo  Check error message above.
    echo ===================================
    pause
)