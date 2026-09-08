@echo off
SETLOCAL

echo ============================================================
echo  Land Research Invest - Spustenie
echo ============================================================

:: Kontrola Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [CHYBA] Python nie je nainstalovany alebo nie je v PATH.
    echo Stiahnite z: https://www.python.org/downloads/
    echo Pri instalacii zaskrtnite: Add Python to PATH
    pause
    exit /b 1
)

:: Nacitaj .env ak existuje
if exist .env (
    for /f "tokens=1,2 delims==" %%a in (.env) do (
        if not "%%a"=="" if not "%%b"=="" set %%a=%%b
    )
)

:: Instalacia zavislosti (iba ak chybaju)
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalujem zavislosti...
    pip install -r backend/requirements.txt
    if errorlevel 1 (
        echo [CHYBA] Instalacia zlyhala.
        pause
        exit /b 1
    )
    echo [INFO] Stiahnutie Playwright Chromium...
    python -m playwright install chromium
)

:: Kontrola API kluca
if "%GOOGLE_API_KEY%"=="" (
    echo.
    echo [UPOZORNENIE] GOOGLE_API_KEY nie je nastaveny.
    echo Skopirujte .env.example na .env a doplnte kluc.
    echo Aplikacia stale bezi ale LLM funkcie budu nedostupne.
    echo.
)

:: Spustenie Flask servera
echo [OK] Spustam server na http://localhost:5001 ...
echo Zastavenie: stlacte Ctrl+C
echo.
cd backend
python app.py

pause
