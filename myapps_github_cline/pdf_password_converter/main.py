"""
PDF Password Converter
Aplikácia na konverziu .docx a .pdf súborov do zaheslovaného PDF.
Výstupný súbor: KM_Výplatná Páska_[Mesiac]_[Rok].pdf
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# PDF knižnice
from pypdf import PdfReader, PdfWriter
from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# Slovenské názvy mesiacov
MESIACE = [
    "Január", "Február", "Marec", "Apríl", "Máj", "Jún",
    "Júl", "August", "September", "Október", "November", "December"
]


def get_app_dir():
    """Získa priečinok aplikácie - funguje aj v .exe režime."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


def get_config_path():
    """Získa cestu ku config.json - funguje aj v .exe režime."""
    return os.path.join(get_app_dir(), "config.json")


def get_output_folder():
    """Získa cestu k priečinku Výplatné Pásky. Vytvorí ho ak neexistuje."""
    output_dir = os.path.join(get_app_dir(), "Výplatné Pásky")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def load_password():
    """Načíta heslo z konfiguračného súboru."""
    config_path = get_config_path()
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get("password", "")
    except FileNotFoundError:
        messagebox.showerror("Chyba", f"Konfiguračný súbor nenájdený:\n{config_path}")
        return None
    except json.JSONDecodeError:
        messagebox.showerror("Chyba", "Konfiguračný súbor je poškodený.")
        return None


def generate_output_filename():
    """
    Generuje názov výstupného súboru na základe aktuálneho dátumu.
    Mesiac = predchádzajúci mesiac, rok = aktuálny (v januári predchádzajúci).
    """
    now = datetime.now()
    current_month = now.month  # 1-12
    current_year = now.year

    if current_month == 1:
        # V januári: mesiac = December, rok = predchádzajúci
        prev_month = 12
        year = current_year - 1
    else:
        # Ostatné mesiace: mesiac - 1, rok aktuálny
        prev_month = current_month - 1
        year = current_year

    month_name = MESIACE[prev_month - 1]
    filename = f"KM_Výplatná Páska_{month_name}_{year}.pdf"
    return filename


def register_fonts():
    """Registruje fonty s podporou diakritiky."""
    fonts_dir = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')

    # Registrujeme Arial (podporuje slovenskú diakritiku)
    arial_path = os.path.join(fonts_dir, 'arial.ttf')
    arial_bold_path = os.path.join(fonts_dir, 'arialbd.ttf')

    if os.path.exists(arial_path):
        pdfmetrics.registerFont(TTFont('Arial', arial_path))
    if os.path.exists(arial_bold_path):
        pdfmetrics.registerFont(TTFont('Arial-Bold', arial_bold_path))


def docx_to_pdf(docx_path, pdf_path):
    """Konvertuje .docx súbor na PDF pomocou reportlab."""
    doc = Document(docx_path)

    # Registrujeme fonty s diakritikou
    register_fonts()

    # Vytvoríme PDF dokument
    pdf_doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    styles = getSampleStyleSheet()

    # Vytvoríme vlastný štýl pre slovenský text s Arial fontom
    normal_style = ParagraphStyle(
        'Slovak',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=11,
        leading=14,
    )

    heading_style = ParagraphStyle(
        'SlovakHeading',
        parent=styles['Heading1'],
        fontName='Arial-Bold',
        fontSize=14,
        leading=18,
    )

    story = []

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if not text:
            story.append(Spacer(1, 0.3 * cm))
            continue

        # Escapovanie špeciálnych HTML znakov pre reportlab
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')

        # Rozlíšenie nadpisov a bežného textu
        if paragraph.style.name.startswith('Heading'):
            story.append(Paragraph(text, heading_style))
            story.append(Spacer(1, 0.3 * cm))
        else:
            story.append(Paragraph(text, normal_style))

    if not story:
        story.append(Paragraph("(Prázdny dokument)", normal_style))

    pdf_doc.build(story)


def encrypt_pdf(input_pdf_path, output_pdf_path, password):
    """Zahesluje PDF súbor."""
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # Skopírujeme všetky stránky
    for page in reader.pages:
        writer.add_page(page)

    # Nastavíme heslo (owner aj user password rovnaké)
    writer.encrypt(user_password=password, owner_password=password)

    with open(output_pdf_path, 'wb') as f:
        writer.write(f)


def convert_file(input_path, output_dir):
    """
    Hlavná funkcia konverzie.
    Vstup: .docx alebo .pdf
    Výstup: zaheslované PDF s automatickým názvom
    """
    password = load_password()
    if password is None:
        return None

    # Generovanie názvu výstupného súboru
    output_filename = generate_output_filename()
    output_path = os.path.join(output_dir, output_filename)

    file_ext = Path(input_path).suffix.lower()

    try:
        if file_ext == '.docx':
            # Najprv konvertujeme docx na PDF (dočasný)
            temp_pdf = output_path + ".tmp"
            docx_to_pdf(input_path, temp_pdf)
            # Potom zaheslujeme
            encrypt_pdf(temp_pdf, output_path, password)
            # Zmažeme dočasný súbor
            os.remove(temp_pdf)

        elif file_ext == '.pdf':
            # PDF už je, len zaheslujeme
            encrypt_pdf(input_path, output_path, password)

        else:
            messagebox.showerror("Chyba", f"Nepodporovaný formát: {file_ext}\nPoužite .docx alebo .pdf")
            return None

        return output_path

    except Exception as e:
        # Vyčistíme dočasné súbory
        temp_pdf = output_path + ".tmp"
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)
        messagebox.showerror("Chyba pri konverzii", str(e))
        return None


class PDFConverterApp:
    """Hlavná GUI trieda aplikácie."""

    def __init__(self, root):
        self.root = root
        self.root.title("PDF Password Converter")
        self.root.geometry("550x350")
        self.root.resizable(False, False)

        # Premenné
        self.input_file = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.status_text = tk.StringVar(value="Čakám na výber súboru...")

        # Predvolený výstupný priečinok = Výplatné Pásky (vedľa aplikácie)
        default_output = get_output_folder()
        self.output_dir.set(default_output)

        self._create_widgets()

    def _create_widgets(self):
        """Vytvorí všetky GUI widgety."""
        # Hlavný frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Nadpis
        title_label = ttk.Label(
            main_frame,
            text="📄 PDF Password Converter 🔒",
            font=("Segoe UI", 16, "bold")
        )
        title_label.pack(pady=(0, 20))

        # --- Vstupný súbor ---
        input_frame = ttk.LabelFrame(main_frame, text="Vstupný súbor", padding=10)
        input_frame.pack(fill=tk.X, pady=5)

        input_entry = ttk.Entry(input_frame, textvariable=self.input_file, width=50)
        input_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)

        input_btn = ttk.Button(input_frame, text="Vybrať", command=self._select_input_file)
        input_btn.pack(side=tk.RIGHT)

        # --- Výstupný priečinok ---
        output_frame = ttk.LabelFrame(main_frame, text="Výstupný priečinok", padding=10)
        output_frame.pack(fill=tk.X, pady=5)

        output_entry = ttk.Entry(output_frame, textvariable=self.output_dir, width=50)
        output_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)

        output_btn = ttk.Button(output_frame, text="Vybrať", command=self._select_output_dir)
        output_btn.pack(side=tk.RIGHT)

        # --- Info o výstupnom názve ---
        output_name = generate_output_filename()
        name_label = ttk.Label(
            main_frame,
            text=f"Výstupný súbor: {output_name}",
            font=("Segoe UI", 9, "italic"),
            foreground="gray"
        )
        name_label.pack(pady=5)

        # --- Tlačidlo konverzie ---
        convert_btn = ttk.Button(
            main_frame,
            text="🔒 Konvertovať do zaheslovaného PDF",
            command=self._convert
        )
        convert_btn.pack(pady=15)

        # --- Stavová lišta ---
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X)

        status_label = ttk.Label(
            status_frame,
            textvariable=self.status_text,
            font=("Segoe UI", 9),
            foreground="blue"
        )
        status_label.pack()

    def _select_input_file(self):
        """Dialóg na výber vstupného súboru."""
        filetypes = [
            ("Podporované súbory", "*.docx *.pdf"),
            ("Word dokumenty", "*.docx"),
            ("PDF súbory", "*.pdf"),
            ("Všetky súbory", "*.*")
        ]
        filepath = filedialog.askopenfilename(
            title="Vybrať vstupný súbor",
            filetypes=filetypes
        )
        if filepath:
            self.input_file.set(filepath)
            self.status_text.set(f"Vybraný súbor: {os.path.basename(filepath)}")

    def _select_output_dir(self):
        """Dialóg na výber výstupného priečinka."""
        dirpath = filedialog.askdirectory(title="Vybrať výstupný priečinok")
        if dirpath:
            self.output_dir.set(dirpath)

    def _convert(self):
        """Spustí konverziu."""
        input_path = self.input_file.get().strip()
        output_dir = self.output_dir.get().strip()

        # Validácia
        if not input_path:
            messagebox.showwarning("Upozornenie", "Prosím, vyberte vstupný súbor.")
            return

        if not os.path.isfile(input_path):
            messagebox.showerror("Chyba", "Vybraný súbor neexistuje.")
            return

        if not output_dir or not os.path.isdir(output_dir):
            messagebox.showerror("Chyba", "Výstupný priečinok neexistuje.")
            return

        # Kontrola rozšírenia
        ext = Path(input_path).suffix.lower()
        if ext not in ['.docx', '.pdf']:
            messagebox.showerror("Chyba", "Podporované formáty: .docx, .pdf")
            return

        self.status_text.set("⏳ Konvertujem...")
        self.root.update()

        # Konverzia
        result = convert_file(input_path, output_dir)

        if result:
            self.status_text.set(f"✅ Hotovo! Uložené: {os.path.basename(result)}")
            messagebox.showinfo(
                "Úspech",
                f"Súbor bol úspešne konvertovaný a zaheslovaný!\n\n"
                f"Uložený ako:\n{result}"
            )
        else:
            self.status_text.set("❌ Konverzia zlyhala.")


def main():
    """Hlavná funkcia - spustenie aplikácie."""
    root = tk.Tk()
    app = PDFConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()