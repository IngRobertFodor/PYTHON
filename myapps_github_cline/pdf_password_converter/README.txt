PDF Password Converter v2.0
============================
Offline Windows app - konverzia .docx/.pdf do zaheslovaneho PDF.
Hesla bezpecne v Windows Credential Manager (keyring).

Poziadavky:
  - Windows 10+
  - Microsoft Word (pre konverziu .docx -> PDF)

Pouzitie:
  1. Dvojklik na start_app.bat
  2. Pridaj zamestnanca (inicialy + heslo)
  3. Vyber vstupny subor (.docx / .pdf)
  4. Klikni "Konvertovat"
  5. Vysledok v priecinku "Výplatné Pásky"

Ako to funguje:
  - .docx subory: Otvori sa vo Worde (skryte) a ulozi sa ako PDF
    (rovnako ako Subor -> Ulozit ako -> PDF). Nasledne sa zasifruje.
  - .pdf subory: Priamo sa zasifruju heslom zamestnanca.
  - Hesla su ulozene v Windows Credential Manager (nie v suboroch).

Bezpecnost:
  - Ziadne hesla nie su ulozene v suboroch
  - Ziadne vyplatne pasky nie su ulozene v git repozitari
  - .gitignore vylucuje vystupny priecinok aj docasne subory

Struktura:
  main.py              - GUI (tkinter)
  converter.py         - logika (Word COM konverzia, sifrovanie, keyring)
  start_app.bat        - spustenie appky
  install_dependencies.bat - instalacia kniznic
  requirements.txt     - Python zavislosti
  test_app.py          - testy
  test_results.txt     - vysledky testov
  README.txt           - tento subor
  HOW_TO_RUN_THIS_APP.txt - navod pre pouzivatelov
  WinPython/           - portable Python (neinstalovany = .exe instalator)
  .gitignore           - vylucene subory z git

Technologie:
  Python 3, tkinter, comtypes (Word COM), pypdf, keyring

Spustenie testov:
  python test_app.py