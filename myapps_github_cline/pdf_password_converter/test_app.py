"""
Test script pre PDF Password Converter v2.0
Overuje základnú funkcionalitu: zamestanci, názvy súborov, konverzia.
Vyžaduje: Microsoft Word (pre .docx konverziu)
"""

import os
import sys
import io
import tempfile
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Pridáme adresár aplikácie do sys.path
_app_dir = os.path.dirname(os.path.abspath(__file__))
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

from converter import (
    get_employees, add_employee, remove_employee,
    get_employee_password, set_employee_password,
    generate_output_filename, convert_file, docx_to_pdf,
    encrypt_pdf, get_output_folder, get_app_dir, MESIACE, KEYRING_SERVICE
)
import keyring

# Testovacie konštanty
TS, TP = "TS", "test123"


def setup():
    """Príprava pred testami."""
    add_employee(TS, TP)


def cleanup():
    """Upratanie po testoch."""
    remove_employee(TS)


# === TESTY PROSTREDIA ===

def test_env_imports():
    """Všetky importy fungujú."""
    print("\n[TEST 1] Importy")
    import comtypes
    import pypdf
    assert keyring is not None
    assert comtypes is not None
    assert pypdf is not None
    print("  [OK] PASSED")


def test_env_output_folder():
    """Výstupný priečinok sa vytvorí."""
    print("\n[TEST 2] Výstupný priečinok")
    out = get_output_folder()
    assert os.path.exists(out) and os.path.isdir(out)
    print(f"  Priečinok: {out}")
    print("  [OK] PASSED")


def test_env_keyring():
    """Keyring funguje (zápis/čítanie)."""
    print("\n[TEST 3] Keyring R/W")
    keyring.set_password("test_svc_tmp", "test_key_tmp", "test_val_tmp")
    assert keyring.get_password("test_svc_tmp", "test_key_tmp") == "test_val_tmp"
    keyring.delete_password("test_svc_tmp", "test_key_tmp")
    print("  [OK] PASSED")


# === TESTY ZAMESTNANCOV ===

def test_emp_crud():
    """Pridanie, heslo, zmena, overenie."""
    print("\n[TEST 4] Zamestnanec CRUD")
    assert TS in get_employees()
    assert get_employee_password(TS) == TP
    set_employee_password(TS, "new_pass")
    assert get_employee_password(TS) == "new_pass"
    set_employee_password(TS, TP)  # Vrátime späť
    print("  [OK] PASSED")


def test_emp_multiple():
    """Viacero zamestnancov."""
    print("\n[TEST 5] Viacero zamestnancov")
    add_employee("AB", "a1")
    add_employee("CD", "c2")
    emps = get_employees()
    assert "AB" in emps and "CD" in emps
    assert get_employee_password("AB") == "a1"
    remove_employee("AB")
    remove_employee("CD")
    assert "AB" not in get_employees()
    print("  [OK] PASSED")


# === TESTY NÁZVU SÚBORU ===

def test_name_auto():
    """Automatický názov (predchádzajúci mesiac)."""
    print("\n[TEST 6] Názov - auto")
    name = generate_output_filename(TS)
    now = datetime.now()
    assert name.startswith(f"{TS}_") and name.endswith(".pdf")
    if now.month == 1:
        assert "December" in name
    else:
        assert MESIACE[now.month - 2] in name
    print(f"  {name}")
    print("  [OK] PASSED")


def test_name_all_months():
    """Všetkých 12 mesiacov."""
    print("\n[TEST 7] Názov - 12 mesiacov")
    for i, m in enumerate(MESIACE):
        n = generate_output_filename("KM", i, 2025)
        expected = f"KM_Výplatná Páska_{m}_2025.pdf"
        assert n == expected, f"Očakávané '{expected}', dostali '{n}'"
    print("  [OK] PASSED")


# === TESTY KONVERZIE ===

def test_conv_docx():
    """Konverzia .docx -> zaheslované PDF (vyžaduje Microsoft Word)."""
    print("\n[TEST 8] Konverzia .docx -> PDF")
    try:
        import comtypes.client
    except ImportError:
        print("  [SKIP] comtypes nie je nainštalované")
        return

    # Vytvoríme testovací .docx pomocou Word COM
    docx_path = os.path.join(tempfile.gettempdir(), "test_converter.docx")
    result = None

    word = None
    doc = None
    try:
        word = comtypes.client.CreateObject('Word.Application')
        word.Visible = False
        doc = word.Documents.Add()
        doc.Content.Text = "Test výplatná páska\nMzda: 1500 EUR\nDátum: 2026-05-01"
        doc.SaveAs(os.path.abspath(docx_path), FileFormat=16)
        doc.Close(0)
        doc = None
        word.Quit()
        word = None
    except Exception as e:
        if doc:
            doc.Close(0)
        if word:
            word.Quit()
        print(f"  [SKIP] Word nie je dostupný: {e}")
        return

    # Otestujeme konverziu
    try:
        result, error = convert_file(docx_path, tempfile.gettempdir(), TS, 0, 2025)
        assert result is not None, f"Konverzia zlyhala: {error}"
        assert os.path.exists(result)
        size = os.path.getsize(result)
        assert size > 500, f"PDF príliš malé: {size} bytes"

        from pypdf import PdfReader
        reader = PdfReader(result)
        assert reader.is_encrypted
        reader.decrypt(TP)
        text = reader.pages[0].extract_text()
        assert "1500" in text, f"Text '1500' nenájdený v PDF"
        print(f"  PDF veľkosť: {size} bytes")
        print("  [OK] PASSED")
    finally:
        if os.path.exists(docx_path):
            os.remove(docx_path)
        if result and os.path.exists(result):
            os.remove(result)


def test_conv_pdf_encrypt():
    """Zaheslovanie existujúceho .pdf."""
    print("\n[TEST 9] Zaheslovanie .pdf")
    from pypdf import PdfWriter, PdfReader

    src_pdf = os.path.join(tempfile.gettempdir(), "test_source.pdf")
    result = None
    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)
    with open(src_pdf, 'wb') as f:
        writer.write(f)

    try:
        result, error = convert_file(src_pdf, tempfile.gettempdir(), TS, 5, 2026)
        assert result is not None, f"Konverzia zlyhala: {error}"
        assert os.path.exists(result)

        reader = PdfReader(result)
        assert reader.is_encrypted
        print("  [OK] PASSED")
    finally:
        if os.path.exists(src_pdf):
            os.remove(src_pdf)
        if result and os.path.exists(result):
            os.remove(result)


# === TESTY CHÝB ===

def test_err_no_password():
    """Heslo nenájdené."""
    print("\n[TEST 10] Chyba - heslo nenájdené")
    r, e = convert_file("fake.docx", _app_dir, "NOBODY", 0, 2025)
    assert r is None and "nenájdené" in e
    print("  [OK] PASSED")


def test_err_bad_format():
    """Nepodporovaný formát."""
    print("\n[TEST 11] Chyba - zlý formát")
    p = os.path.join(tempfile.gettempdir(), "test_bad.txt")
    with open(p, "w") as f:
        f.write("x")
    try:
        r, e = convert_file(p, tempfile.gettempdir(), TS, 0, 2025)
        assert r is None and "Nepodporovaný" in e
        print("  [OK] PASSED")
    finally:
        os.remove(p)


# === TESTY BEZPEČNOSTI ===

def test_security_gitignore():
    """Gitignore obsahuje výstupný priečinok a citlivé súbory."""
    print("\n[TEST 12] Bezpečnosť - .gitignore")
    gitignore_path = os.path.join(_app_dir, ".gitignore")
    assert os.path.exists(gitignore_path), ".gitignore neexistuje!"
    with open(gitignore_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Výplatné Pásky/" in content, "Výstupný priečinok nie je v .gitignore!"
    assert "WinPython/" in content, "WinPython nie je v .gitignore!"
    assert "*.exe" in content, "*.exe nie je v .gitignore!"
    print("  [OK] PASSED")


# === RUNNER ===

if __name__ == "__main__":
    tests = [
        test_env_imports, test_env_output_folder, test_env_keyring,
        test_emp_crud, test_emp_multiple,
        test_name_auto, test_name_all_months,
        test_conv_docx, test_conv_pdf_encrypt,
        test_err_no_password, test_err_bad_format,
        test_security_gitignore,
    ]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print("=" * 50)
    print(f"  PDF PASSWORD CONVERTER v2.0 - TESTY | {now}")
    print("=" * 50)
    setup()
    passed = failed = skipped = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as ex:
            print(f"  [FAIL] {ex}")
            failed += 1
        except Exception as ex:
            print(f"  [FAIL] {type(ex).__name__}: {ex}")
            failed += 1
    cleanup()
    total = len(tests)
    print("\n" + "=" * 50)
    print(f"  VÝSLEDOK: {passed} PASSED / {failed} FAILED / {total} TOTAL")
    status = "ALL PASSED" if failed == 0 else "SOME FAILED"
    print(f"  {status}")
    print("=" * 50)

    # Zápis do test_results.txt
    results_file = os.path.join(_app_dir, "test_results.txt")
    run_num = 1
    if os.path.exists(results_file):
        with open(results_file, "r", encoding="utf-8") as rf:
            for line in rf:
                if line.startswith("#"):
                    run_num += 1
    with open(results_file, "a", encoding="utf-8") as rf:
        rf.write(f"#{run_num} | {now} | {passed} PASSED / {failed} FAILED / {total} TOTAL | {status}\n")

    sys.exit(0 if failed == 0 else 1)