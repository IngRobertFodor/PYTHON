with open('C://__TESTAUTOMATION//SCRIPTS//PYTHON//myapps_github_cline//www_centrumzdravenia_sk_chatbot//chatbot.html', 'r', encoding='utf-8') as f:
    content = f.read()

original_len = len(content)

# ── 1. Komentar v hlavicke ──────────────────────────────────────────────────
content = content.replace(
    '  3. Odporucana velkost embed boxu: min. 360 x 540 px (idealne 400 x 600 px)',
    '  3. Odporucana velkost embed boxu: 500 x 760 px (pre PC; mobil/tablet automaticky responzivne)'
)

# ── 2. Hlavicka loga +20 %: 84px → 101px ────────────────────────────────────
content = content.replace(
    '  display: block; width: 100%; height: 84px;',
    '  display: block; width: 100%; height: 101px;'
)

# ── 3. Responzivne velkosti okna ─────────────────────────────────────────────
# Nahradim stary #cz-window (fixne na cely box) novym s media queries

old_window = """/* === WINDOW === */
#cz-window {
  position: absolute; bottom: 78px; right: 12px; left: 12px; top: 12px;
  background: var(--c-cream);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-lg);
  box-shadow: 0 8px 36px var(--c-shadow);
  display: none; flex-direction: column; overflow: hidden; z-index: 90;
  opacity: 0; transform: translateY(10px);
  transition: opacity .24s ease, transform .24s ease;
}
#cz-window.is-open { opacity: 1; transform: translateY(0); }"""

new_window = """/* === WINDOW === */
/* Mobil – takmer cela plocha */
#cz-window {
  position: absolute;
  left: 8px; right: 8px; top: 8px; bottom: 76px;
  background: var(--c-cream);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-lg);
  box-shadow: 0 8px 36px var(--c-shadow);
  display: none; flex-direction: column; overflow: hidden; z-index: 90;
  opacity: 0; transform: translateY(10px);
  transition: opacity .24s ease, transform .24s ease;
}
#cz-window.is-open { opacity: 1; transform: translateY(0); }
/* Tablet (640 px a viac) */
@media (min-width: 640px) {
  #cz-window {
    left: auto; top: auto;
    width: 420px; height: 620px;
    right: 12px; bottom: 78px;
    max-width: calc(100vw - 24px);
    max-height: calc(100vh - 90px);
  }
}
/* Desktop (1024 px a viac) */
@media (min-width: 1024px) {
  #cz-window {
    width: 460px; height: 680px;
    right: 12px; bottom: 78px;
    max-width: calc(100vw - 24px);
    max-height: calc(100vh - 90px);
  }
}"""

if old_window in content:
    content = content.replace(old_window, new_window)
    print('OK: #cz-window nahradeny')
else:
    print('CHYBA: #cz-window nenajdeny – kontrolujem fragment...')
    # Skus najst aspon cast
    frag = '  position: absolute; bottom: 78px; right: 12px; left: 12px; top: 12px;'
    if frag in content:
        print('  Fragment najdeny v obsahu')
    else:
        print('  Fragment NENAJDENY')

with open('C://__TESTAUTOMATION//SCRIPTS//PYTHON//myapps_github_cline//www_centrumzdravenia_sk_chatbot//chatbot.html', 'w', encoding='utf-8') as f:
    f.write(content)

new_len = len(content)
print(f'Hotovo. Velkost: {original_len} → {new_len} znakov')
print('Zmeny:')
print('  1. Komentar embed boxu:', '500 x 760' in content)
print('  2. Hlavicka 101px:', 'height: 101px' in content)
print('  3. Media queries:', '@media (min-width: 640px)' in content)
