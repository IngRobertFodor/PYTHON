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
python -m pip show flask >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalujem zavislosti...
    python -m pip install -r backend/requirements.txt
    if errorlevel 1 (
        echo [CHYBA] Instalacia zlyhala.
        pause
        exit /b 1
    )
)


:: Otvor prehliadac (server startujem ihned po tom)
start "" http://localhost:5001

:: Spustenie Flask servera
echo [OK] Spustam server na http://localhost:5001 ...
echo Zastavenie: stlacte Ctrl+C
echo.
cd backend
python app.py

pause
