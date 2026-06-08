@echo off
echo ==========================================
echo  Installing dependencies...
echo ==========================================
echo.

REM Find python.exe in WinPython folder
for /f "delims=" %%P in ('dir /s /b "%~dp0WinPython\python.exe" 2^>nul ^| findstr /i /v "Scripts"') do (
    set PYTHON=%%P
    goto found
)

REM Fallback to system Python
set PYTHON=python
goto install

:found
echo Found Python: %PYTHON%
echo.

:install
echo Installing libraries...
"%PYTHON%" -m pip install -r "%~dp0requirements.txt"
echo.
echo ==========================================
echo  DONE! You can now run start_app.bat
echo ==========================================
pause