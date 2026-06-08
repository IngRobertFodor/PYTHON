PDF Password Converter v2.0
============================
Offline Windows app - converts .docx/.pdf to password-protected PDF.
Passwords stored securely in Windows Credential Manager (keyring).

Requirements:
  - Windows 10+
  - Microsoft Word (required for .docx to PDF conversion)

Usage:
  1. Double-click start_app.bat
  2. Add an employee (initials + password)
  3. Select input file (.docx / .pdf)
  4. Click "Convert"
  5. Result saved in "Výplatné Pásky" folder

How it works:
  - .docx files: Opened in Word (hidden) and saved as PDF
    (identical to File -> Save As -> PDF). Then encrypted with password.
  - .pdf files: Directly encrypted with employee's password.
  - Passwords are stored in Windows Credential Manager (not in files).

Security:
  - No passwords are stored in files
  - No pay slips are stored in the git repository
  - .gitignore excludes output folder and temporary files

Structure:
  main.py              - GUI (tkinter)
  converter.py         - logic (Word COM conversion, encryption, keyring)
  start_app.bat        - launch the app
  install_dependencies.bat - install libraries
  requirements.txt     - Python dependencies
  test_app.py          - tests
  test_results.txt     - test results
  README.txt           - this file
  HOW_TO_RUN_THIS_APP.txt - user guide
  WinPython/           - portable Python (not installed = .exe installer)
  .gitignore           - excluded files from git

Technologies:
  Python 3, tkinter, comtypes (Word COM), pypdf, keyring

Running tests:
  python test_app.py