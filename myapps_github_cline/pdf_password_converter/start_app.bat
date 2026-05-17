@echo off
echo Starting PDF Password Converter...
echo.

REM Try WinPython first (portable, in same folder)
if exist "%~dp0WinPython\python-3.14.5.amd64\python.exe" (
    "%~dp0WinPython\python-3.14.5.amd64\python.exe" "%~dp0main.py"
    goto end
)

REM Try WinPython alternative path
if exist "%~dp0WinPython\python.exe" (
    "%~dp0WinPython\python.exe" "%~dp0main.py"
    goto end
)

REM Fallback to system Python
python "%~dp0main.py"

:end