@echo off
echo ==========================================
echo  PDF Password Converter v1.0 - Build EXE
echo ==========================================
echo.

REM Instalujem zavislosti...
pip install python-docx pypdf reportlab pyinstaller

echo.
echo Vytváram .exe súbor...
pyinstaller --onefile --windowed --name "PDF_Password_Converter_v1.0" main.py

echo.
echo Kopirujem subory do myapps_github_cline...
copy "dist\PDF_Password_Converter_v1.0.exe" "..\PDF_Password_Converter_v1.0.exe"
copy "config.json" "..\config.json"

echo.
echo ==========================================
echo  BUILD DOKONCENY!
echo ==========================================
echo.
echo  .exe subor: myapps_github_cline\PDF_Password_Converter_v1.0.exe
echo  config.json: myapps_github_cline\config.json
echo  Poznamky: myapps_github_cline\v1.0_notes.txt
echo ==========================================

pause