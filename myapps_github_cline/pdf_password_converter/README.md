# 📄 PDF Password Converter 🔒

Jednoduchá offline Windows aplikácia, ktorá vezme dokument (.docx alebo .pdf) a vytvorí z neho zaheslované PDF.

## ✨ Funkcie

- **Vstupné formáty:** `.docx` (Word), `.pdf` (bez hesla)
- **Výstup:** Zaheslované PDF
- **Automatický názov:** `KM_Výplatná Páska_[Mesiac]_[Rok].pdf`
  - Mesiac = predchádzajúci mesiac oproti aktuálnemu
  - V januári sa použije December predchádzajúceho roka
- **Heslo:** Načítané z `config.json`
- **GUI:** Jednoduché grafické rozhranie (tkinter)
- **Offline:** Žiadne pripojenie na internet nie je potrebné

## 📦 Inštalácia a spustenie

### Spustenie ako Python skript
```bash
# Nainštalujte závislosti
pip install -r requirements.txt

# Spustite aplikáciu
python main.py
```

### Vytvorenie .exe súboru
```bash
# Spustite build skript
build_exe.bat
```
Po builde nájdete `.exe` v priečinku `dist/`. Nezabudnite, že `config.json` musí byť v rovnakom priečinku ako `.exe` súbor.

## ⚙️ Konfigurácia

Heslo je uložené v `config.json`:
```json
{
    "password": "vaše_heslo"
}
```

## 📁 Štruktúra projektu
```
pdf_password_converter/
├── main.py              # Hlavná aplikácia (GUI + logika)
├── config.json          # Konfigurácia s heslom
├── requirements.txt     # Python závislosti
├── build_exe.bat        # Skript na vytvorenie .exe
└── README.md            # Tento súbor
```

## 🖥️ Použitie

1. Spustite aplikáciu (`main.py` alebo `.exe`)
2. Kliknite **"Vybrať"** a zvoľte vstupný súbor (.docx alebo .pdf)
3. Voliteľne zmeňte výstupný priečinok
4. Kliknite **"🔒 Konvertovať do zaheslovaného PDF"**
5. Hotovo! Zaheslované PDF sa uloží s automatickým názvom

## 📅 Príklady názvov výstupných súborov

| Dátum spustenia | Názov súboru |
|---|---|
| Máj 2026 | `KM_Výplatná Páska_Apríl_2026.pdf` |
| Január 2026 | `KM_Výplatná Páska_December_2025.pdf` |
| Február 2026 | `KM_Výplatná Páska_Január_2026.pdf` |

## 🛠️ Technológie

- Python 3
- tkinter (GUI)
- python-docx (čítanie .docx)
- reportlab (generovanie PDF)
- pypdf (zaheslovanie PDF)
- PyInstaller (vytvorenie .exe)