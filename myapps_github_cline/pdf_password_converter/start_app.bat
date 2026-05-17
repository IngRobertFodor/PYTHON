@echo off
echo Starting PDF Password Converter...
echo.

REM Find python.exe in WinPython folder (any version)
for /f "delims=" %%P in ('dir /s /b "%~dp0WinPython\python.exe" 2^>nul') do (
    set PYTHON=%%P
    goto found
)

REM WinPython not found - try system Python
echo WinPython not found, trying system Python...
set PYTHON=python

:found
"%PYTHON%" "%~dp0main.py"