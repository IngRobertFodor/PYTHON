"""
PDF Password Converter v2.0 - GUI
Spúšťací súbor aplikácie. Importuje logiku z converter.py.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import os
import sys
from datetime import datetime

# Pridáme adresár aplikácie do sys.path (pre import converter.py)
if getattr(sys, 'frozen', False):
    _app_dir = os.path.dirname(sys.executable)
else:
    _app_dir = os.path.dirname(os.path.abspath(__file__))
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

from converter import (
    MESIACE, get_output_folder, get_employees, add_employee,
    remove_employee, get_employee_password, set_employee_password,
    generate_output_filename, convert_file
)


class PDFConverterApp:
    """Hlavná GUI trieda."""

    def __init__(self, root):
        self.root = root
        self.root.title("PDF Password Converter v2.0")
        self.root.geometry("600x530")
        self.root.resizable(False, False)
        self.input_file = tk.StringVar()
        self.output_dir = tk.StringVar(value=get_output_folder())
        self.status_text = tk.StringVar(value="Pripravený.")
        self.use_prev_month = tk.BooleanVar(value=True)
        self._build_gui()
        self._check_first_run()

    def _check_first_run(self):
        """Pri prvom spustení vyzve na pridanie zamestnanca."""
        if not get_employees():
            self.root.after(500, self._first_run_dialog)

    def _first_run_dialog(self):
        messagebox.showinfo("Vitajte!", "PDF Password Converter v2.0\n\nPridajte prvého zamestnanca.")
        self._add_employee()

    def _build_gui(self):
        """Zostaví celé GUI."""
        f = ttk.Frame(self.root, padding=20)
        f.pack(fill=tk.BOTH, expand=True)

        # Nadpis
        ttk.Label(f, text="PDF Password Converter v2.0",
                  font=("Segoe UI", 16, "bold")).pack(pady=(0, 15))

        # --- Zamestnanec ---
        ef = ttk.LabelFrame(f, text="Zamestnanec", padding=10)
        ef.pack(fill=tk.X, pady=5)
        self.emp_cb = ttk.Combobox(ef, width=10, state="readonly")
        self.emp_cb.pack(side=tk.LEFT, padx=(0, 10))
        self.emp_cb.bind("<<ComboboxSelected>>", self._on_emp_change)
        ttk.Button(ef, text="+ Pridať", command=self._add_employee).pack(side=tk.LEFT, padx=5)
        ttk.Button(ef, text="Odstrániť", command=self._remove_employee).pack(side=tk.LEFT, padx=5)
        ttk.Button(ef, text="Zmeniť heslo", command=self._change_password).pack(side=tk.RIGHT, padx=5)
        self._refresh_employees()

        # --- Vstupný súbor ---
        inf = ttk.LabelFrame(f, text="Vstupný súbor (.docx / .pdf)", padding=10)
        inf.pack(fill=tk.X, pady=5)
        ttk.Entry(inf, textvariable=self.input_file, width=50).pack(
            side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        ttk.Button(inf, text="Vybrať", command=self._pick_input).pack(side=tk.RIGHT)

        # --- Výstupný priečinok ---
        of = ttk.LabelFrame(f, text="Výstupný priečinok", padding=10)
        of.pack(fill=tk.X, pady=5)
        ttk.Entry(of, textvariable=self.output_dir, width=50).pack(
            side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        ttk.Button(of, text="Vybrať", command=self._pick_output).pack(side=tk.RIGHT)

        # --- Dátum ---
        df = ttk.LabelFrame(f, text="Dátum výplatnej pásky", padding=10)
        df.pack(fill=tk.X, pady=5)
        ttk.Checkbutton(df, text="Predchádzajúci mesiac (automaticky)",
                        variable=self.use_prev_month,
                        command=self._toggle_date).pack(anchor=tk.W)

        # Manuálny výber dátumu
        self.date_frame = ttk.Frame(df)
        self.date_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(self.date_frame, text="Mesiac:").pack(side=tk.LEFT, padx=(10, 5))
        self.month_cb = ttk.Combobox(self.date_frame, values=MESIACE,
                                     width=12, state="readonly")
        self.month_cb.pack(side=tk.LEFT, padx=(0, 15))
        self.month_cb.bind("<<ComboboxSelected>>", self._update_name)
        now = datetime.now()
        self.month_cb.current(11 if now.month == 1 else now.month - 2)
        ttk.Label(self.date_frame, text="Rok:").pack(side=tk.LEFT, padx=(0, 5))
        self.year_var = tk.IntVar(value=now.year if now.month > 1 else now.year - 1)
        self.year_sb = ttk.Spinbox(self.date_frame, from_=2020, to=2035,
                                   textvariable=self.year_var, width=7,
                                   command=self._update_name)
        self.year_sb.pack(side=tk.LEFT)

        # --- Názov výstupného súboru ---
        self.name_label = ttk.Label(f, text="", font=("Segoe UI", 9, "italic"),
                                    foreground="gray")
        self.name_label.pack(pady=5)

        # Inicializácia dátumu (musí byť AŽ po vytvorení name_label)
        self._toggle_date()

        # --- Tlačidlo konverzie ---
        ttk.Button(f, text="Konvertovať do zaheslovaného PDF",
                   command=self._convert).pack(pady=10)

        # --- Status ---
        ttk.Label(f, textvariable=self.status_text,
                  font=("Segoe UI", 9), foreground="blue").pack()

    # === ZAMESTNANEC ===

    def _refresh_employees(self):
        """Aktualizuje combobox zamestnancov."""
        emps = get_employees()
        self.emp_cb['values'] = emps
        if emps:
            self.emp_cb.current(0)

    def _on_emp_change(self, event=None):
        """Po zmene zamestnanca aktualizuj názov."""
        self._update_name()

    def _add_employee(self):
        """Dialóg na pridanie nového zamestnanca."""
        initials = simpledialog.askstring(
            "Nový zamestnanec", "Iniciály (napr. KM):", parent=self.root)
        if not initials:
            return
        initials = initials.strip().upper()
        if len(initials) < 2:
            messagebox.showwarning("Chyba", "Minimálne 2 znaky.")
            return
        if initials in get_employees():
            messagebox.showwarning("Existuje", f"'{initials}' už existuje.")
            return
        password = simpledialog.askstring(
            "Heslo", f"Heslo pre {initials}:", show='*', parent=self.root)
        if not password:
            return
        add_employee(initials, password)
        self._refresh_employees()
        emps = get_employees()
        if initials in emps:
            self.emp_cb.current(emps.index(initials))
        self._update_name()
        self.status_text.set(f"Zamestnanec '{initials}' pridaný.")

    def _remove_employee(self):
        """Odstráni vybraného zamestnanca."""
        sel = self.emp_cb.get()
        if not sel:
            messagebox.showwarning("Chyba", "Vyberte zamestnanca.")
            return
        if not messagebox.askyesno("Potvrdiť", f"Odstrániť '{sel}' a jeho heslo?"):
            return
        remove_employee(sel)
        self._refresh_employees()
        self._update_name()
        self.status_text.set(f"Zamestnanec '{sel}' odstránený.")

    def _change_password(self):
        """Zmení heslo vybraného zamestnanca."""
        sel = self.emp_cb.get()
        if not sel:
            messagebox.showwarning("Chyba", "Vyberte zamestnanca.")
            return
        password = simpledialog.askstring(
            "Nové heslo", f"Nové heslo pre {sel}:", show='*', parent=self.root)
        if not password:
            return
        set_employee_password(sel, password)
        self.status_text.set(f"Heslo pre '{sel}' zmenené.")

    # === DÁTUM ===

    def _toggle_date(self):
        """Skryje/zobrazí manuálny výber dátumu."""
        if self.use_prev_month.get():
            for child in self.date_frame.winfo_children():
                child.configure(state="disabled") if hasattr(child, 'configure') else None
            self.month_cb.configure(state="disabled")
            self.year_sb.configure(state="disabled")
        else:
            self.month_cb.configure(state="readonly")
            self.year_sb.configure(state="normal")
        self._update_name()

    def _update_name(self, event=None):
        """Aktualizuje zobrazený názov výstupného súboru."""
        sel = self.emp_cb.get() if self.emp_cb.get() else "XX"
        if self.use_prev_month.get():
            name = generate_output_filename(sel)
        else:
            mi = self.month_cb.current()
            yr = self.year_var.get()
            name = generate_output_filename(sel, mi, yr)
        self.name_label.config(text=f"Výstup: {name}")

    # === SÚBORY ===

    def _pick_input(self):
        """Výber vstupného súboru."""
        path = filedialog.askopenfilename(
            title="Vybrať súbor",
            filetypes=[("Podporované", "*.docx *.pdf"),
                       ("Word", "*.docx"), ("PDF", "*.pdf")])
        if path:
            self.input_file.set(path)
            self.status_text.set(f"Vybraný: {os.path.basename(path)}")

    def _pick_output(self):
        """Výber výstupného priečinka."""
        path = filedialog.askdirectory(title="Výstupný priečinok")
        if path:
            self.output_dir.set(path)

    # === KONVERZIA ===

    def _convert(self):
        """Spustí konverziu."""
        inp = self.input_file.get().strip()
        out = self.output_dir.get().strip()
        sel = self.emp_cb.get()

        # Validácia
        if not sel:
            messagebox.showwarning("Chyba", "Vyberte zamestnanca.")
            return
        if not inp:
            messagebox.showwarning("Chyba", "Vyberte vstupný súbor.")
            return
        if not os.path.isfile(inp):
            messagebox.showerror("Chyba", "Súbor neexistuje.")
            return
        if not out or not os.path.isdir(out):
            messagebox.showerror("Chyba", "Výstupný priečinok neexistuje.")
            return

        # Dátum
        if self.use_prev_month.get():
            mi, yr = None, None
        else:
            mi = self.month_cb.current()
            yr = self.year_var.get()

        self.status_text.set("Konvertujem...")
        self.root.update()

        # Konverzia
        result, error = convert_file(inp, out, sel, mi, yr)
        if result:
            self.status_text.set(f"Hotovo: {os.path.basename(result)}")
            messagebox.showinfo("Úspech",
                                f"Súbor uložený:\n{result}")
        else:
            self.status_text.set("Konverzia zlyhala.")
            messagebox.showerror("Chyba", error)


def main():
    """Spustenie aplikácie."""
    root = tk.Tk()
    PDFConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
