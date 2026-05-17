PDF Password Converter
======================
Offline Windows app - konverzia .docx/.pdf do zaheslovaneho PDF.
Hesla bezpecne v Windows Credential Manager (keyring).

Pouzitie:
  1. Dvojklik na start_app.bat
  2. Pridaj zamestnanca (inicialy + heslo)
  3. Vyber vstupny subor (.docx / .pdf)
  4. Klikni "Konvertovat"
  5. Vysledok v priecinku "Vyplatne Pasky"

Struktura:
  main.py              - GUI
  converter.py         - logika (konverzia, keyring)
  start_app.bat        - spustenie appky
  requirements.txt     - Python zavislosti
  test_app.py          - testy
  test_results.txt     - vysledky testov
  README.txt           - tento subor
  HOW_TO_RUN_THIS_APP.txt - navod pre pouzivatelov
  WinPython/           - portable Python (neinstalovany = .exe instalator)
  .gitignore

Technologie:
  Python 3, tkinter, pypdf, python-docx, reportlab, keyring

Spustenie testov:
  python test_app.py