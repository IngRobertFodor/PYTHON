"""
PDF Password Converter v2.0 - Konverzná logika
Obsahuje: správu zamestnancov, generovanie názvov, PDF konverziu.
Heslá bezpečne v Windows Credential Manager (keyring).
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from pypdf import PdfReader, PdfWriter
import keyring

# Konštanty
KEYRING_SERVICE = "pdf_password_converter"
KEYRING_EMPLOYEES_KEY = "employees_list"
MESIACE = ["Január", "Február", "Marec", "Apríl", "Máj", "Jún",
           "Júl", "August", "September", "Október", "November", "December"]


# === POMOCNÉ FUNKCIE ===

def get_app_dir():
    """Priečinok aplikácie (funguje aj ako .exe)."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_output_folder():
    """Výstupný priečinok - vytvorí ak neexistuje."""
    d = os.path.join(get_app_dir(), "Výplatné Pásky")
    os.makedirs(d, exist_ok=True)
    return d


# === SPRÁVA ZAMESTNANCOV ===

def get_employees():
    """Zoznam iniciálov zamestnancov z keyring."""
    data = keyring.get_password(KEYRING_SERVICE, KEYRING_EMPLOYEES_KEY)
    return [e.strip() for e in data.split(",") if e.strip()] if data else []


def save_employees(emp_list):
    """Uloží zoznam zamestnancov."""
    keyring.set_password(KEYRING_SERVICE, KEYRING_EMPLOYEES_KEY, ",".join(emp_list))


def add_employee(initials, password):
    """Pridá zamestnanca + heslo."""
    emps = get_employees()
    if initials not in emps:
        emps.append(initials)
        save_employees(emps)
    keyring.set_password(KEYRING_SERVICE, f"password_{initials}", password)


def remove_employee(initials):
    """Odstráni zamestnanca + heslo."""
    emps = get_employees()
    if initials in emps:
        emps.remove(initials)
        save_employees(emps)
    try:
        keyring.delete_password(KEYRING_SERVICE, f"password_{initials}")
    except keyring.errors.PasswordDeleteError:
        pass


def get_employee_password(initials):
    """Heslo zamestnanca z keyring."""
    return keyring.get_password(KEYRING_SERVICE, f"password_{initials}")


def set_employee_password(initials, password):
    """Zmení heslo zamestnanca."""
    keyring.set_password(KEYRING_SERVICE, f"password_{initials}", password)


# === GENEROVANIE NÁZVU ===

def generate_output_filename(initials, month_idx=None, year=None):
    """Názov súboru. month_idx: 0-11, None=predchádzajúci mesiac."""
    if month_idx is None or year is None:
        now = datetime.now()
        if now.month == 1:
            month_idx, year = 11, now.year - 1
        else:
            month_idx, year = now.month - 2, now.year
    return f"{initials}_Výplatná Páska_{MESIACE[month_idx]}_{year}.pdf"


# === PDF KONVERZIA ===

def docx_to_pdf(docx_path, pdf_path):
    """
    Konvertuje .docx na PDF pomocou Microsoft Word (COM automation).
    Funguje rovnako ako Súbor -> Uložiť ako -> PDF vo Worde.
    Zachová celý vzhľad dokumentu vrátane tabuliek, obrázkov, formátovania.
    """
    import comtypes.client

    # Absolutné cesty sú povinné pre Word COM
    docx_path = os.path.abspath(docx_path)
    pdf_path = os.path.abspath(pdf_path)

    word = None
    doc = None
    try:
        # Spustíme Word (alebo sa pripojíme k existujúcemu)
        word = comtypes.client.CreateObject('Word.Application')
        word.Visible = False

        # Otvoríme dokument
        doc = word.Documents.Open(docx_path)

        # Uložíme ako PDF (wdFormatPDF = 17)
        doc.SaveAs(pdf_path, FileFormat=17)

    finally:
        # Zatvoríme dokument a Word
        if doc is not None:
            doc.Close(0)  # 0 = wdDoNotSaveChanges
        if word is not None:
            word.Quit()

    # Overíme, že PDF bolo vytvorené a nie je prázdne
    if not os.path.exists(pdf_path):
        raise RuntimeError("Word nevytvoril PDF súbor!")
    if os.path.getsize(pdf_path) < 500:
        raise RuntimeError(
            "Word vytvoril prázdne PDF!\n"
            "Skúste otvoriť .docx manuálne a uložiť ako PDF."
        )


def encrypt_pdf(input_path, output_path, password):
    """Zahesluje PDF."""
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(user_password=password, owner_password=password)
    with open(output_path, 'wb') as f:
        writer.write(f)


def convert_file(input_path, output_dir, initials, month_idx=None, year=None):
    """
    Hlavná konverzia .docx/.pdf -> zaheslované PDF.
    Vracia (output_path, None) pri úspechu alebo (None, error_msg) pri chybe.
    """
    password = get_employee_password(initials)
    if not password:
        return None, f"Heslo pre '{initials}' nenájdené!"

    filename = generate_output_filename(initials, month_idx, year)
    output_path = os.path.join(output_dir, filename)
    ext = Path(input_path).suffix.lower()

    try:
        if ext == '.docx':
            tmp = output_path + ".tmp"
            docx_to_pdf(input_path, tmp)
            encrypt_pdf(tmp, output_path, password)
            os.remove(tmp)
        elif ext == '.pdf':
            encrypt_pdf(input_path, output_path, password)
        else:
            return None, f"Nepodporovaný formát: {ext}"
        return output_path, None
    except Exception as e:
        tmp = output_path + ".tmp"
        if os.path.exists(tmp):
            os.remove(tmp)
        return None, str(e)