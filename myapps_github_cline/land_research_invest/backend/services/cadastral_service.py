"""
Sluzba katastra - List vlastnictva
===================================
Spracovanie dat z LV a generovanie checklistu.

Rezim CHECKLIST: bez dat -> manualny checklist (skore 50).
Rezim EVALUATE:  s datami -> vyhodnoti sekcie B/C/D podla configu.
Automatizacia: SEMI (Playwright + CAPTCHA klik od pouzivatela).
"""

from models.result import ServiceResult
from config_loader import get_criteria_section

SERVICE_NAME = "cadastral_service"


def check(lv_data=None, parcel_number="", location=""):
    """
    Hlavna funkcia.
    - Bez lv_data -> vracia checklist (skore 50, caka na overenie)
    - S lv_data   -> vyhodnocuje podla kriterii (skore 0-100)
    """
    if lv_data is None:
        return ServiceResult(
            ok=True, score=50.0,
            data={
                "mode": "checklist",
                "checklist": generate_checklist(parcel_number, location),
                "parcel_number": parcel_number,
                "location": location,
                "awaiting_manual_verification": True,
            },
            source=SERVICE_NAME,
        )
    return evaluate_lv_data(lv_data, parcel_number)


def evaluate_lv_data(lv_data, parcel_number=""):
    """
    Vyhodnoti data z LV podla kriterii z criteria.yaml (sekcia cadastral).

    Ocakavany format lv_data:
        plombs: list            # aktivne plomby, napr. ["V"]
        liens: bool             # zalozne pravo
        preemption: bool        # predkupne pravo statu/obce
        usufruct: bool          # pravo dozitia
        unknown_easement: bool  # nezname vecne bremeno
        co_owners: int          # pocet spoluvlastnikov
        has_register_e: bool    # register E (rozdrobene podiely)
        min_fraction_denominator: int  # napr. 32 pre podiel 1/32
        spf_owner: bool         # SPF je vlastnik
        unknown_owners: bool    # nezisti vlastnici
        road_has_easement: bool # cesta ma vecne bremeno
    """
    cfg = get_criteria_section("cadastral")
    issues, warnings = [], []

    # --- Plomby (sekcia D) ---
    allowed = cfg.get("no_active_plombs", {}).get("plomb_types", ["V", "Z"])
    active = [p for p in lv_data.get("plombs", []) if p in allowed]
    if active:
        issues.append(f"Aktivne plomby: {", ".join(active)}")

    # --- Tarchy (sekcia C) ---
    enc = cfg.get("encumbrances", {})
    if enc.get("no_lien") and lv_data.get("liens"):
        issues.append("Zalozne pravo")
    if enc.get("no_preemption") and lv_data.get("preemption"):
        issues.append("Predkupne pravo statu/obce")
    if enc.get("no_usufruct") and lv_data.get("usufruct"):
        issues.append("Pravo dozitia")
    if enc.get("no_unknown_easement") and lv_data.get("unknown_easement"):
        warnings.append("Nezname vecne bremeno - overit obsah")

    # --- Vlastnici (sekcia B) ---
    own = cfg.get("ownership", {})
    max_co = own.get("max_co_owners", 2)
    co = lv_data.get("co_owners", 1)
    if co > max_co:
        issues.append(f"Prilis vela spoluvlastnikov: {co} (max {max_co})")

    if own.get("no_register_e_fractions") and lv_data.get("has_register_e"):
        max_d = own.get("max_fraction_denominator", 8)
        act_d = lv_data.get("min_fraction_denominator", 1)
        if act_d > max_d:
            issues.append(f"Register E - podiel 1/{act_d} (max 1/{max_d})")

    if own.get("no_spf_ownership") and lv_data.get("spf_owner"):
        issues.append("SPF (Slovensky pozemkovy fond) je vlastnik")
    if own.get("no_unknown_owners") and lv_data.get("unknown_owners"):
        issues.append("Nezisti vlastnici")

    # --- Pristupova cesta ---
    road = cfg.get("road_access_legal", {})
    if road.get("verified") and not lv_data.get("road_has_easement", True):
        warnings.append("Cesta nema vecne bremeno prechodu/prejazdu")

    score = _calculate_score(issues, warnings)
    return ServiceResult(
        ok=True, score=score,
        data={
            "mode": "evaluated",
            "parcel_number": parcel_number,
            "issues": issues,
            "warnings": warnings,
            "issues_count": len(issues),
            "warnings_count": len(warnings),
            "clean": len(issues) == 0,
        },
        source=SERVICE_NAME,
    )


def generate_checklist(parcel_number="", location=""):
    """Vygeneruje strukturovany manualny checklist pre kontrolu LV."""
    h = f"""
==============================================================
KATASTER - MANUALNY CHECKLIST
==============================================================
Parcela:  {parcel_number or "(doplnit)"}
Lokalita: {location or "(doplnit)"}

URL: https://kataster.skgeodesy.sk/Portal/
POSTUP: Zadat cislo parcely -> kliknut "List vlastnictva"
==============================================================

SEKCIA B - VLASTNICI
--------------------
[ ] Pocet spoluvlastnikov: ___  (max 2)
[ ] Register E (rozdrobene podiely): ANO / NIE
    - Ak ANO: najmensi podiel 1/___ (max 1/8)
[ ] SPF je vlastnik: ANO / NIE
[ ] Nezisti vlastnici: ANO / NIE

SEKCIA C - TARCHY
-----------------
[ ] Zalozne pravo: ANO / NIE
[ ] Predkupne pravo statu/obce: ANO / NIE
[ ] Pravo dozitia: ANO / NIE
[ ] Ine vecne bremena: ___________________________

SEKCIA D - INE ZAPISY
---------------------
[ ] Aktivne plomby (V, Z): ANO / NIE
[ ] Prebiehajuce konanie: ANO / NIE

PRISTUPOVA CESTA
----------------
[ ] Cislo parcely cesty: ___________________
[ ] Vlastnik (obec / sukromny): _____________
[ ] Vecne bremeno prechodu/prejazdu: ANO / NIE
[ ] SPF vlastni cestu: ANO / NIE

VYSLEDOK:
[ ] CLEAN  - ziadne problemy, mozno pokracovat
[ ] ISSUES - su problemy, riesit pred koupou
[ ] SKIP   - kriticke problemy, nepokracovat
==============================================================
"""
    return h


def _calculate_score(issues, warnings):
    """
    Skore 0-100 podla poctu problemov a varovani.
    Kazdy problem (issue)  -> -30 bodov.
    Kazde varovanie        -> -10 bodov.
    Minimum: 0.
    """
    score = 100.0 - len(issues) * 30.0 - len(warnings) * 10.0
    return round(max(0.0, min(100.0, score)), 2)
