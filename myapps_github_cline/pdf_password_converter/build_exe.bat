@echo off
echo ==========================================
echo  PDF Password Converter v2.0 - Build EXE
echo ==========================================
echo.

REM Instalujem zavislosti
pip install python-docx pypdf reportlab keyring pyinstaller

echo.
echo Vytváram .exe súbor...
pyinstaller --onefile --windowed --name "PDF_Password_Converter_v2.0" --hidden-import keyring.backends.Windows --add-data "converter.py;." main.py

echo.
echo Kopirujem .exe do hlavného priečinka...
copy "dist\PDF_Password_Converter_v2.0.exe" ".\PDF_Password_Converter_v2.0.exe"

echo.
echo ==========================================
echo  BUILD DOKONCENY!
echo ==========================================
echo.
echo  .exe subor: PDF_Password_Converter_v2.0.exe
echo  Ziadny config.json nie je potrebny!
echo  Hesla sa ukladaju do Windows Credential Manager.
echo ==========================================

pause