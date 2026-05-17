PDF Password Converter v2.0
============================
Offline Windows aplikacia na konverziu .docx/.pdf do zaheslovaneho PDF.
Hesla bezpecne ulozene v Windows Credential Manager (keyring).
Staci len .exe subor - ziadne konfiguracne subory.

Pouzitie:
  1. Spustit PDF_Password_Converter_v2.0.exe
  2. Prve spustenie: pridat zamestnanca (inicialy + heslo)
  3. Vybrat vstupny subor (.docx / .pdf)
  4. Volitelne zmenit mesiac/rok (odskrtnut checkbox)
  5. Kliknut "Konvertovat do zaheslovaneho PDF"
  6. Vysledok v priecinku "Vyplatne Pasky"

Prenos na iny PC:
  Skopirovat len PDF_Password_Converter_v2.0.exe
  Prve spustenie vyzve na zadanie hesla

Stromova struktura:
  pdf_password_converter/
    PDF_Password_Converter_v2.0.exe  - spustitelna aplikacia
    main.py                          - GUI (tkinter)
    converter.py                     - logika (konverzia, keyring)
    test_app.py                      - testy (9 testov)
    test_results.txt                 - vysledky posledneho testu
    README.txt                       - tento subor
    requirements.txt                 - Python zavislosti
    build_exe.bat                    - build skript
    .gitignore                       - ignorovane subory

Build .exe:
  cd pdf_password_converter
  pip install -r requirements.txt
  build_exe.bat

Spustenie testov:
  python test_app.py

Technologie:
  Python 3.12, tkinter, pypdf, python-docx, reportlab, keyring, PyInstaller

==============================
HISTORIA VERZII
==============================

V1.0 (15.05.2026)
  - Konverzia .docx/.pdf na zaheslovane PDF
  - Heslo v config.json (plain text, nebezpecne)
  - Pevny prefix KM (jeden zamestnanec)
  - Automaticky nazov: KM_Vyplatna Paska_[Mesiac]_[Rok].pdf
  - GUI (tkinter), offline

V2.0 (17.05.2026)
  - HESLA: presunute do Windows Credential Manager (keyring)
    - config.json ZRUSENY
    - Bezpecne, sifrovane
  - ZAMESTNANCI: sprava cez GUI
    - Pridanie/odobratie, kazdy ma vlastne heslo
    - Prefix nazvu suboru podla vybraneho zamestnanca
  - DATUM: volitelny vyber
    - Checkbox "Predchadzajuci mesiac" (predvolene)
    - Moznost vlastneho vyberu mesiaca a roku
  - KOD: rozdeleny na main.py (GUI) + converter.py (logika)
  - DISTRIBUCIA: staci len .exe, ziadne externé subory
  - TESTY: 9 testov pokryvajucich vsetku funkcionalitu