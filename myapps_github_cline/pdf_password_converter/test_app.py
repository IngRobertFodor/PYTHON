"""
Test skript pre PDF Password Converter.
Otestuje konverziu .docx a .pdf do zaheslovaného PDF.
"""

import os
import sys
import io

# Nastavenie UTF-8 pre stdout (riesi problem s emoji pri presmerovani do suboru)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Pridame cestu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from docx import Document
from pypdf import PdfReader
from main import convert_file, generate_output_filename


def create_test_docx(filepath):
    """Vytvori testovaci .docx subor."""
    doc = Document()
    doc.add_heading('Vyplatna Paska - Maj 2026', level=1)
    doc.add_paragraph('Meno: Jan Novak')
    doc.add_paragraph('Pozicia: Senior Developer')
    doc.add_paragraph('Hruba mzda: 2 500,00 EUR')
    doc.add_paragraph('Odvody zamestnanec: 335,00 EUR')
    doc.add_paragraph('Dan z prijmu: 320,50 EUR')
    doc.add_paragraph('Cista mzda: 1 844,50 EUR')
    doc.add_paragraph('')
    doc.add_paragraph('Datum vyplaty: 15.05.2026')
    doc.save(filepath)
    print(f"  [OK] Testovaci .docx vytvoreny: {filepath}")


def test_filename_generation():
    """Test generovania nazvu suboru."""
    print("\n[TEST 1] Generovanie nazvu suboru")
    filename = generate_output_filename()
    print(f"  Vygenerovany nazov: {filename}")
    assert "KM_Výplatná Páska_" in filename, "Nazov neobsahuje prefix!"
    assert ".pdf" in filename, "Nazov neobsahuje .pdf!"
    print("  [OK] Test PRESIEL!")


def test_docx_conversion():
    """Test konverzie .docx na zaheslovane PDF."""
    print("\n[TEST 2] Konverzia .docx -> zaheslovane PDF")
    
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_docx = os.path.join(test_dir, "test_vyplatna_paska.docx")
    
    # Vytvorime testovaci docx
    create_test_docx(test_docx)
    
    # Konvertujeme
    result = convert_file(test_docx, test_dir)
    print(f"  Vystupny subor: {result}")
    
    assert result is not None, "Konverzia zlyhala!"
    assert os.path.exists(result), "Vystupny subor neexistuje!"
    
    # Overime, ze PDF je zaheslovane
    reader = PdfReader(result)
    assert reader.is_encrypted, "PDF NIE JE zaheslovane!"
    print("  [OK] PDF je zaheslovane!")
    
    # Overime, ze heslo funguje
    reader.decrypt("21011988")
    text = reader.pages[0].extract_text()
    print(f"  Obsah (prvych 100 znakov): {text[:100]}")
    
    assert "Novak" in text or "Novák" in text, "Text neobsahuje meno!"
    print("  [OK] Obsah PDF je spravny!")
    
    # Vycistime
    os.remove(test_docx)
    os.remove(result)
    print("  [OK] Testovacie subory vycistene")
    print("  [OK] Test PRESIEL!")


def test_pdf_encryption():
    """Test zaheslovania existujuceho PDF."""
    print("\n[TEST 3] Zaheslovanie existujuceho .pdf")
    
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_docx = os.path.join(test_dir, "test_temp.docx")
    test_pdf = os.path.join(test_dir, "test_input.pdf")
    
    # Najprv vytvorime nezaheslovane PDF (cez docx)
    from main import docx_to_pdf
    doc = Document()
    doc.add_paragraph("Toto je testovaci PDF subor bez hesla.")
    doc.add_paragraph("Specialne znaky: sctzyadie")
    doc.save(test_docx)
    docx_to_pdf(test_docx, test_pdf)
    os.remove(test_docx)
    print(f"  [OK] Testovaci PDF vytvoreny: {test_pdf}")
    
    # Konvertujeme (zaheslujeme)
    result = convert_file(test_pdf, test_dir)
    print(f"  Vystupny subor: {result}")
    
    assert result is not None, "Konverzia zlyhala!"
    assert os.path.exists(result), "Vystupny subor neexistuje!"
    
    # Overime
    reader = PdfReader(result)
    assert reader.is_encrypted, "PDF NIE JE zaheslovane!"
    reader.decrypt("21011988")
    text = reader.pages[0].extract_text()
    print(f"  Obsah: {text[:100]}")
    assert "testovaci" in text or "testovac" in text, "Text neobsahuje ocakavany obsah!"
    print("  [OK] Test PRESIEL!")
    
    # Vycistime
    os.remove(test_pdf)
    os.remove(result)
    print("  [OK] Testovacie subory vycistene")


if __name__ == "__main__":
    print("=" * 50)
    print("  PDF PASSWORD CONVERTER - TESTY")
    print("=" * 50)
    
    test_filename_generation()
    test_docx_conversion()
    test_pdf_encryption()
    
    print("\n" + "=" * 50)
    print("  VSETKY TESTY PRESLI USPESNE!")
    print("=" * 50)