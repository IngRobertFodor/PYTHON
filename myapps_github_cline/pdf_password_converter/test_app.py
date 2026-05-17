"""Testy pre PDF Password Converter v2.0"""
import os, sys, io, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
_dir = os.path.dirname(os.path.abspath(__file__))
if _dir not in sys.path:
    sys.path.insert(0, _dir)

from datetime import datetime
from docx import Document
from pypdf import PdfReader
from converter import (
    get_employees, add_employee, remove_employee,
    get_employee_password, set_employee_password,
    generate_output_filename, convert_file, docx_to_pdf,
    get_output_folder, MESIACE
)

TS, TP = "TS", "test123"

def setup():
    add_employee(TS, TP)
    print(f"  [SETUP] '{TS}' vytvoreny")

def cleanup():
    remove_employee(TS)
    print(f"  [CLEANUP] '{TS}' odstraneny")

def test_1_employee_crud():
    print("\n[TEST 1] Zamestnanec CRUD")
    assert TS in get_employees()
    assert get_employee_password(TS) == TP
    set_employee_password(TS, "new")
    assert get_employee_password(TS) == "new"
    set_employee_password(TS, TP)
    print("  [OK] PASSED")

def test_2_multiple_employees():
    print("\n[TEST 2] Viacero zamestnancov")
    add_employee("AB", "a1")
    add_employee("CD", "c2")
    assert "AB" in get_employees() and "CD" in get_employees()
    assert get_employee_password("AB") == "a1"
    remove_employee("AB")
    remove_employee("CD")
    assert "AB" not in get_employees()
    print("  [OK] PASSED")

def test_3_filename_auto():
    print("\n[TEST 3] Nazov - automaticky")
    name = generate_output_filename(TS)
    now = datetime.now()
    assert name.startswith(f"{TS}_") and name.endswith(".pdf")
    if now.month == 1:
        assert "December" in name and str(now.year-1) in name
    else:
        assert MESIACE[now.month-2] in name
    print(f"  {name}")
    print("  [OK] PASSED")

def test_4_filename_all_months():
    print("\n[TEST 4] Nazov - vsetky mesiace")
    for i, m in enumerate(MESIACE):
        n = generate_output_filename("KM", i, 2025)
        assert n == f"KM_Výplatná Páska_{m}_2025.pdf", f"Zly: {n}"
    print("  [OK] 12/12 mesiacov OK")
    print("  [OK] PASSED")

def test_5_convert_docx():
    print("\n[TEST 5] Konverzia .docx -> zaheslovane PDF")
    p = os.path.join(_dir, "t.docx")
    doc = Document()
    doc.add_heading('Test', level=1)
    doc.add_paragraph('Mzda: 1500 EUR')
    doc.save(p)
    r, e = convert_file(p, _dir, TS, 0, 2025)
    assert r and os.path.exists(r), f"Err: {e}"
    reader = PdfReader(r)
    assert reader.is_encrypted
    reader.decrypt(TP)
    assert "1500" in reader.pages[0].extract_text()
    os.remove(p)
    os.remove(r)
    print("  [OK] PASSED")

def test_6_convert_pdf():
    print("\n[TEST 6] Zaheslovanie .pdf")
    dp = os.path.join(_dir, "t2.docx")
    pp = os.path.join(_dir, "t2.pdf")
    doc = Document()
    doc.add_paragraph("Test PDF obsah")
    doc.save(dp)
    docx_to_pdf(dp, pp)
    os.remove(dp)
    r, e = convert_file(pp, _dir, TS, 5, 2026)
    assert r and os.path.exists(r), f"Err: {e}"
    reader = PdfReader(r)
    assert reader.is_encrypted
    reader.decrypt(TP)
    assert "Test" in reader.pages[0].extract_text()
    os.remove(pp)
    os.remove(r)
    print("  [OK] PASSED")

def test_7_error_no_password():
    print("\n[TEST 7] Chyba - heslo nenajdene")
    r, e = convert_file("fake.docx", _dir, "NEEXISTUJE", 0, 2025)
    assert r is None
    assert "nenájdené" in e
    print("  [OK] PASSED")

def test_8_error_bad_format():
    print("\n[TEST 8] Chyba - nepodporovany format")
    p = os.path.join(_dir, "t.txt")
    with open(p, "w") as f:
        f.write("test")
    r, e = convert_file(p, _dir, TS, 0, 2025)
    assert r is None
    assert "Nepodporovaný" in e
    os.remove(p)
    print("  [OK] PASSED")

def test_9_output_folder_created():
    print("\n[TEST 9] Vystupny priecinok sa vytvori ak neexistuje")
    out = get_output_folder()
    # Zmazeme ak existuje
    if os.path.exists(out):
        shutil.rmtree(out)
    assert not os.path.exists(out)
    # Zavolame znova - musi sa vytvorit
    out2 = get_output_folder()
    assert os.path.exists(out2)
    assert os.path.isdir(out2)
    print(f"  Priecinok: {out2}")
    print("  [OK] PASSED")

if __name__ == "__main__":
    print("=" * 50)
    print("  PDF PASSWORD CONVERTER v2.0 - TESTY")
    print("=" * 50)
    setup()
    tests = [test_1_employee_crud, test_2_multiple_employees,
             test_3_filename_auto, test_4_filename_all_months,
             test_5_convert_docx, test_6_convert_pdf,
             test_7_error_no_password, test_8_error_bad_format,
             test_9_output_folder_created]
    passed = failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as ex:
            print(f"  [FAIL] {ex}")
            failed += 1
    cleanup()
    print("\n" + "=" * 50)
    print(f"  VYSLEDOK: {passed} PASSED / {failed} FAILED / {len(tests)} TOTAL")
    if failed == 0:
        print("  VSETKY TESTY PRESLI USPESNE!")
    else:
        print("  NIEKTORE TESTY ZLYHALI!")
    print("=" * 50)
    sys.exit(0 if failed == 0 else 1)