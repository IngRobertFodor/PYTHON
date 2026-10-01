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

:: Kontrola portu 5001 - ak uz bezi, len otvor prehliadac
netstat -ano | findstr ":5001 " | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [INFO] Server uz bezi na porte 5001.
    echo [INFO] Otvoram prehliadac...
    start "" http://localhost:5001
    exit /b 0
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

:: Vytvor priecinok pre databazu ak neexistuje
if not exist data mkdir data

:: Otvor prehliadac po 3s (server potrebuje chvilu na start)
start "" /wait cmd /c "timeout /t 3 /nobreak >nul && start "" http://localhost:5001"

:: Spustenie Flask servera
echo [OK] Spustam server na http://localhost:5001 ...
echo Zastavenie: stlacte Ctrl+C alebo zavrite toto okno
echo.
cd backend
python app.py

pause
