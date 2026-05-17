@echo off
echo ==========================================
echo  Installing dependencies...
echo ==========================================
echo.

REM Find python.exe in WinPython folder
for /f "delims=" %%P in ('dir /s /b "%~dp0WinPython\python.exe" 2^>nul') do (
    set PYTHON=%%P
    goto found
)

echo ERROR: WinPython not found!
echo Please extract WinPython first (see HOW_TO_RUN_THIS_APP.txt)
pause
exit /b 1

:found
echo Found Python: %PYTHON%
echo.
echo Installing libraries...
"%PYTHON%" -m pip install -r "%~dp0requirements.txt"
echo.
echo ==========================================
echo  DONE! You can now run start_app.bat
echo ==========================================
pause