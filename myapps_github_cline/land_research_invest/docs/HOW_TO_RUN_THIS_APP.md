# HOW TO RUN THIS APP

## First Time Setup (do this only once)

### Step 1: Make sure Python is installed
- Download Python from https://www.python.org/downloads/
- During installation, **CHECK** the box `"Add Python to PATH"`
- Restart your computer after installation

### Step 2: Get a Google Gemini API key (free tier)
1. Go to https://aistudio.google.com/app/apikey
2. Click **"Create API key"** (free, no credit card needed)
3. Copy the file `.env.example` to `.env`
4. Open `.env` and paste your key:
   ```
   GOOGLE_API_KEY=your_key_here
   ```
5. Optionally add Anthropic key as fallback:
   ```
   ANTHROPIC_API_KEY=your_key_here
   ```
   *(leave empty or omit if not needed)*

### Step 3: Install required libraries
- Double-click **`start_app.bat`**
- It will automatically install all dependencies:
  Flask, LangChain, Gemini, GIS libraries, Playwright...
- It will also run: `playwright install chromium`
  *(downloads Chromium browser for scraping — ~130 MB, one-time only)*
- This step may take a few minutes on first run

---

## Running the App (every time)

1. Double-click **`start_app.bat`**
2. Wait a few seconds
3. Your web browser will open automatically at **http://localhost:5001**
4. Done!

---

## Using the App

### 1. Set your search criteria
| Field | Description |
|-------|-------------|
| Max price (EUR) | Upper price limit |
| Max distance (km) | Max distance from Bratislava (max 70) |
| Min / max area (m²) | Parcel size range |
| Min parcel width (m) | Minimum width (recommended: 15 m) |

### 2. Click "Start scan"
- The AI agent begins searching real estate portals
- Progress and reasoning are shown in the live log panel

### 3. Agent validates each parcel automatically
- 📐 Geometry (width, shape, area) via **ZBGIS WFS**
- 🌊 Flood zone Q100 via **SHMÚ WMS**
- 🌱 Soil quality BPEJ via **geodata.gov.sk WMS**
- 🚗 Road access, electricity, water via **OpenStreetMap Overpass**
- 📏 Distance and drive time from Bratislava

### 4. Results appear on the map + as scored cards (0–100)
| Color | Score | Meaning |
|-------|-------|---------|
| 🟢 Green | ≥ 85 | Strong Buy |
| 🟡 Yellow | ≥ 70 | Investigate |
| 🟠 Orange | ≥ 50 | Consider |
| 🔴 Red | < 50 | Skip |

### 5. Download cadastral checklist
For top candidates (score ≥ 70), download the **Cadastral Checklist**
and use it to manually verify List vlastníctva at:
> https://kataster.skgeodesy.sk

---

## ⚠️ Important — Manual Steps Required

Some checks **cannot be automated** and require your manual action:

| Step | Why manual? | What agent provides |
|------|-------------|---------------------|
| ❌ List vlastníctva (B/C/D) | CAPTCHA on katasterportal.sk | Pre-filled checklist |
| ❌ ÚPI / zoning (IBV zone) | Must request from municipality | Draft request letter |
| ⚠️ Transformer capacity | Only proximity is auto-checked | Note to confirm with ZSDIS |
| ❌ Archaeological zone | No open API | Note to check with KPÚ |

---

## Stopping the App

1. Go to the CMD window (black window with text)
2. Press **Ctrl+C**
3. The server will stop

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `"Python nie je nainstalovany"` | Install Python from python.org (check "Add to PATH") |
| `"GOOGLE_API_KEY not set"` | Make sure `.env` exists and contains `GOOGLE_API_KEY=...` |
| Scraping returns no results | Portals use anti-bot protection — retry in 10–15 min or update selectors in `realestate_scraper_service.py` |
| GIS service timeout (ZBGIS/SHMÚ/BPEJ) | Slovak state endpoints can be temporarily down — retry later |
| Port 5001 already in use | Change `PORT` in `backend/app.py` or in `.env` |
| `playwright install` fails | Run CMD as administrator: `cd backend && python -m playwright install chromium` |

---

## Running Tests

```bash
python -m pytest tests/ --rootdir=. -v
```

---

## Author

Robert Fodor | 2026
