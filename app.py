"""
Wise spending — Streamlit onboarding: financial baseline capture + JSONL persistence.
"""

from __future__ import annotations

import csv
import io
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

import i18n as _i18n
import snapshot_export as _wiz_snap

# ACS: B25064 median gross rent & B25105 median owner monthly housing cost (ZCTA ≈ ZIP).
ACS_YEAR = 2023

# --- Constants ----------------------------------------------------------------

APP_TITLE = "Wise spending"
CONFIG_PATH = Path(__file__).resolve().parent / "user_config.jsonl"

# Baseline monthly “typical” living cost at U.S. average (no location adjustment).
BASE_LIVING_COST_BY_FAMILY: dict[str, float] = {
    "Single": 2_800.0,
    "Couple": 4_200.0,
    "Parents (1 kid)": 5_800.0,
    "Parents (2+ kids)": 7_200.0,
}

FAMILY_OPTIONS = list(BASE_LIVING_COST_BY_FAMILY.keys())
VIBE_OPTIONS = ["Minimalist", "Balanced", "Spender"]


def _wfl_short_label(idx: int) -> str:
    return _i18n.t(f"wfl_short_{idx}")


def _translate_family_option(value: str) -> str:
    m = {
        "Single": "opt_fam_single",
        "Couple": "opt_fam_couple",
        "Parents (1 kid)": "opt_fam_p1",
        "Parents (2+ kids)": "opt_fam_p2",
    }
    return _i18n.t(m.get(value, "opt_fam_single"))


def _translate_vibe_option(value: str) -> str:
    m = {
        "Minimalist": "opt_vibe_min",
        "Balanced": "opt_vibe_bal",
        "Spender": "opt_vibe_spend",
    }
    return _i18n.t(m.get(value, "opt_vibe_bal"))


def _translate_alloc_row_display_index(i: int) -> str:
    return _i18n.t(f"alloc_long_{i}")


def _fmt_car_household_band(v: str) -> str:
    return _i18n.t("car_hh_1") if v == "1" else _i18n.t("car_hh_2plus")


def _fmt_car_status(s: str) -> str:
    m = {
        "No car": "car_st_none",
        "Lease": "car_st_lease",
        "Finance": "car_st_finance",
        "Own outright": "car_st_own",
    }
    return _i18n.t(m.get(s, "car_st_none"))


def _fmt_own_median_choice(v: str) -> str:
    if v == _wiz_snap.OWN_MEDIAN_CONFIRM_YES:
        return _i18n.t("own_median_yes_disp")
    if v == _wiz_snap.OWN_MEDIAN_CONFIRM_UNSURE:
        return _i18n.t("own_median_unsure_disp")
    return str(v)


def _fmt_housing_ws_side(s: str) -> str:
    return _i18n.t("house_ws_side_rent") if s == "rent" else _i18n.t("house_ws_side_own")


def _fmt_housing_ui_tab(s: str) -> str:
    return _i18n.t("house_tab_rent_lbl") if s == "rent" else _i18n.t("house_tab_own_lbl")


def _fmt_401k_choice(v: str) -> str:
    m = {
        "Not sure — need to check": "inv_401k_opt_ns",
        "No / probably under the match": "inv_401k_opt_under",
        "Yes — I’m at or above full match": "inv_401k_opt_full",
        "No employer plan / N/A": "inv_401k_opt_na",
    }
    return _i18n.t(m.get(v, "inv_401k_opt_ns"))


# Own · Step 2 — simplified monthly property tax estimate by property style (not assessor data).
DASH_OWN_PROPERTY_TAX_APARTMENT_MO = 500.0
DASH_OWN_PROPERTY_TAX_HOUSE_MO = 1_000.0


def _fmt_own_property_kind(k: str) -> str:
    if k == "apartment":
        return _i18n.t("house_prop_apt", mo=int(DASH_OWN_PROPERTY_TAX_APARTMENT_MO))
    return _i18n.t("house_prop_house", mo=int(DASH_OWN_PROPERTY_TAX_HOUSE_MO))

# Rule-of-thumb ceilings as a fraction of monthly take-home (after tax).
HOUSING_SPEND_CEILING_FRAC = 0.30
CAR_SPEND_CEILING_FRAC = 0.15

# Illustrative resale retention for new-car depreciation demo (mid-range consumer-guide style; not a quote).
CAR_DEP_ILLUSTRATIVE_RETENTION_3YR = 0.47
CAR_DEP_ILLUSTRATIVE_RETENTION_5YR = 0.37

# Illustrative “food at home” monthly ranges (USDA official food plan order-of-magnitude; national, rounded — not live CPI).
GROCERY_USDA_BALLPARK_MONTHLY: dict[str, tuple[int, int]] = {
    "Single": (290, 430),
    "Couple": (520, 760),
    "Parents (1 kid)": (700, 960),
    "Parents (2+ kids)": (880, 1_220),
}

TOTAL_ONBOARD_STEPS = 3


def _render_language_selector() -> None:
    """Top-right language: English (default), Spanish, Chinese."""
    opts = [("en", "English"), ("es", "Español"), ("zh", "中文")]
    cur = str(st.session_state.get("ui_lang", "en") or "en")
    if cur not in ("en", "es", "zh"):
        cur = "en"
    labels = [o[1] for o in opts]
    idx = next(i for i, o in enumerate(opts) if o[0] == cur)
    sel = st.selectbox(
        _i18n.t("lang_selector_label"),
        labels,
        index=idx,
        key="_ui_lang_selectbox",
    )
    chosen = opts[labels.index(sel)][0]
    if chosen != st.session_state.get("ui_lang"):
        st.session_state.ui_lang = chosen
        st.rerun()


def _parse_zip5(raw: str | None) -> str | None:
    if not raw:
        return None
    digits = "".join(c for c in str(raw).strip() if c.isdigit())
    return digits[:5] if len(digits) >= 5 else None


def _family_suggested_bedrooms(family: str) -> str:
    """Human-readable bedroom / home-size hint for Own flow."""
    if family == "Single":
        return _i18n.t("bed_single")
    if family == "Couple":
        return _i18n.t("bed_couple")
    if family == "Parents (1 kid)":
        return _i18n.t("bed_p1")
    if family == "Parents (2+ kids)":
        return _i18n.t("bed_p2")
    return _i18n.t("bed_default")


def _family_housing_benchmark_profile(family: str) -> tuple[str, str, float]:
    """
    Map questionnaire household to expected rental size band.
    Returns (short_label, detail, multiplier on ZCTA-level ACS median).
    """
    if family == "Single":
        return (
            _i18n.t("prof_single_short"),
            _i18n.t("prof_single_detail"),
            0.94,
        )
    if family == "Couple":
        return (
            _i18n.t("prof_couple_short"),
            _i18n.t("prof_couple_detail"),
            1.02,
        )
    if family == "Parents (1 kid)":
        return (
            _i18n.t("prof_p1_short"),
            _i18n.t("prof_p1_detail"),
            1.14,
        )
    if family == "Parents (2+ kids)":
        return (
            _i18n.t("prof_p2_short"),
            _i18n.t("prof_p2_detail"),
            1.32,
        )
    return (_i18n.t("prof_default_short"), _i18n.t("prof_default_detail"), 1.0)


@st.cache_data(ttl=86_400, show_spinner=False)
def _acs_median_gross_rent_zcta(zip5: str, year: int = ACS_YEAR) -> int | None:
    """B25064: median gross rent (rent + utilities tenants pay)."""
    url = (
        f"https://api.census.gov/data/{year}/acs/acs5"
        f"?get=B25064_001E&for=zip%20code%20tabulation%20area:{urllib.parse.quote(zip5)}"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "WiseSpending/1.0"})
        with urllib.request.urlopen(req, timeout=25) as resp:
            rows = json.loads(resp.read().decode("utf-8"))
        if len(rows) < 2:
            return None
        v = rows[1][0]
        if v is None:
            return None
        n = int(v)
        return n if n > 0 else None
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, json.JSONDecodeError, IndexError, TypeError):
        return None


@st.cache_data(ttl=86_400, show_spinner=False)
def _acs_zcta_owner_snapshot(
    zip5: str, year: int = ACS_YEAR
) -> tuple[str | None, int | None, int | None]:
    """NAME, B25105 owner monthly cost, B25077 median home value (ZCTA)."""
    url = (
        f"https://api.census.gov/data/{year}/acs/acs5"
        f"?get=NAME,B25105_001E,B25077_001E"
        f"&for=zip%20code%20tabulation%20area:{urllib.parse.quote(zip5)}"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "WiseSpending/1.0"})
        with urllib.request.urlopen(req, timeout=25) as resp:
            rows = json.loads(resp.read().decode("utf-8"))
        if len(rows) < 2:
            return None, None, None
        name = str(rows[1][0]) if rows[1][0] else None
        oc_raw, hv_raw = rows[1][1], rows[1][2]

        def _pos_int(x: object) -> int | None:
            if x is None or x == "":
                return None
            try:
                n = int(float(x))
            except (TypeError, ValueError):
                return None
            return n if n > 0 else None

        oc = _pos_int(oc_raw)
        hv = _pos_int(hv_raw)
        return name, oc, hv
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, json.JSONDecodeError, IndexError, TypeError):
        return None, None, None


@st.cache_data(ttl=43_200, show_spinner=False)
def _fred_latest_mortgage30_annual_pct() -> float | None:
    """FRED MORTGAGE30US — weekly average 30-year fixed rate in percent."""
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
    transient = (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError)
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "WiseSpending/1.0"})
            with urllib.request.urlopen(req, timeout=25) as resp:
                text = resp.read().decode("utf-8", errors="replace")
            r = list(csv.reader(io.StringIO(text)))
            if len(r) < 2:
                return None
            val = float(r[-1][1])
            if not (0 < val < 30):
                return None
            return val
        except transient:
            if attempt == 0:
                continue
            return None
        except (ValueError, IndexError, TypeError):
            return None
    return None


def _monthly_principal_interest(principal: float, annual_rate_decimal: float, years: int = 30) -> float:
    if principal <= 0:
        return 0.0
    r = annual_rate_decimal / 12.0
    n = years * 12
    if n <= 0:
        return 0.0
    if r <= 0:
        return principal / float(n)
    return float(principal * (r * (1.0 + r) ** n) / ((1.0 + r) ** n - 1.0))


def _compare_user_to_own_model(user_amt: int, model_total: int | None) -> None:
    if model_total is None or model_total <= 0 or user_amt <= 0:
        return
    pct = (user_amt / float(model_total) - 1.0) * 100.0
    if pct > 5:
        st.warning(_i18n.t("own_model_high", pct=pct, model=model_total))
        st.markdown(_i18n.t("own_model_ideas_high"))
    elif pct < -5:
        st.success(_i18n.t("own_model_low", pct=abs(pct), model=model_total))
        st.markdown(_i18n.t("own_model_ideas_low"))
    else:
        st.info(_i18n.t("own_model_near", model=model_total))


# Post-onboarding wizard modules: slug, title key, description key, short nav key (i18n)
WIZARD_MODULES: list[tuple[str, str, str, str]] = [
    ("housing", "wiz_title_housing", "wiz_desc_housing", "wiz_nav_housing"),
    ("car", "wiz_title_car", "wiz_desc_car", "wiz_nav_car"),
    ("child", "wiz_title_child", "wiz_desc_child", "wiz_nav_child"),
    ("grocery", "wiz_title_grocery", "wiz_desc_grocery", "wiz_nav_grocery"),
    ("entertainment", "wiz_title_entertainment", "wiz_desc_entertainment", "wiz_nav_entertainment"),
    ("invest", "wiz_title_invest", "wiz_desc_invest", "wiz_nav_invest"),
    ("chat", "wiz_title_chat", "wiz_desc_chat", "wiz_nav_chat"),
]

N_WIZARD_STEPS = len(WIZARD_MODULES)


def _inject_soft_survey_backdrop_css() -> None:
    """Warm off-white page + carbon chrome (matches main emerald theme)."""
    st.markdown(
        """
        <style>
          .stApp {
            background-color: #f9f9f7 !important;
            background-image: none !important;
          }
          [data-testid="stHeader"] {
            background: #f9f9f7 !important;
            border-bottom: 1px solid #d1d5db !important;
          }
          [data-testid="stHeader"] [data-testid="stToolbar"] {
            background: transparent !important;
          }
          [data-testid="stHeader"] button,
          [data-testid="stHeader"] [data-testid="stToolbar"] {
            color: #1a1a1a !important;
          }
          [data-testid="stHeader"] svg {
            fill: #1a1a1a !important;
          }
          [data-testid="stHeader"] a {
            color: #059669 !important;
          }
          [data-testid="stHeader"] a:hover,
          [data-testid="stHeader"] a:focus-visible {
            color: #047857 !important;
            text-decoration: underline !important;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _inject_intro_fullbleed_css() -> None:
    _inject_soft_survey_backdrop_css()
    st.markdown(
        """
        <style>
          @keyframes fv-hero-line-in {
            0% { opacity: 0; transform: translateY(10px); }
            100% { opacity: 1; transform: translateY(0); }
          }
          @keyframes fv-hero-fade-up {
            0% { opacity: 0; transform: translateY(10px); }
            100% { opacity: 1; transform: translateY(0); }
          }
          .block-container {
            padding-top: 2.25rem !important;
            padding-bottom: 3.5rem !important;
            max-width: min(100%, 920px) !important;
            margin-left: auto !important;
            margin-right: auto !important;
          }
          .fv-hero-shell {
            margin: 0 auto 2rem;
            max-width: min(96vw, 1100px);
            border-radius: 0.5rem;
            overflow: hidden;
            background: #ffffff;
            border: none;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.06);
          }
          .fv-hero-brand {
            background: #f3f3f0;
            padding: clamp(2.5rem, 5vw, 4rem) clamp(1.25rem, 4vw, 2.75rem) clamp(2rem, 4vw, 3rem);
            text-align: center;
            border-bottom: 1px solid #d1d5db;
          }
          .fv-hero-logo {
            display: inline-flex;
            width: 3.25rem;
            height: 3.25rem;
            border-radius: 0.375rem;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1.25rem;
            background: #ffffff;
            border: none;
            box-shadow: 0 2px 4px -1px rgb(0 0 0 / 0.1);
            opacity: 0;
            animation: fv-hero-fade-up 0.85s ease 0.05s forwards;
          }
          .fv-hero-icon {
            font-size: 1.55rem;
            color: #1a1a1a;
            line-height: 1;
          }
          .fv-hero-sub {
            font-family: "JetBrains Mono", ui-monospace, monospace;
            font-size: 0.8125rem;
            font-weight: 500;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: #4b5563;
            margin: 0 0 0.75rem 0;
            opacity: 0;
            animation: fv-hero-fade-up 0.95s ease 0.1s forwards;
          }
          .fv-hero-title {
            font-family: "Playfair Display", Georgia, "Times New Roman", serif;
            margin: 0;
            font-size: clamp(2.6rem, 5.5vw, 4.5rem);
            font-weight: 600;
            line-height: 1.05;
            letter-spacing: -0.04em;
            color: #1a1a1a;
            opacity: 0;
            animation: fv-hero-fade-up 1.05s ease 0.18s forwards;
          }
          .fv-hero-body {
            background: #ffffff;
            padding: clamp(1.75rem, 4vw, 2.75rem) clamp(1.25rem, 4vw, 2.5rem);
            text-align: center;
          }
          .fv-hero-line {
            font-family: "Source Serif 4", Georgia, "Times New Roman", serif;
            margin: 0;
            font-size: clamp(1.25rem, 2.2vw, 1.45rem);
            font-weight: 400;
            line-height: 1.8;
            color: #1a1a1a;
            max-width: 48ch;
            margin-left: auto;
            margin-right: auto;
            opacity: 0;
            animation: fv-hero-line-in 1s ease 0.3s forwards;
          }
          .fv-hero-line strong {
            font-weight: 600;
            color: #1a1a1a;
          }
          section.main [data-testid="stMarkdownContainer"] p.fv-intro-cta-line {
            font-family: "Source Serif 4", Georgia, serif !important;
            font-size: clamp(1.25rem, 2.6vw, 1.4rem) !important;
            font-weight: 500 !important;
            line-height: 1.5 !important;
            color: #4b5563 !important;
            text-align: center !important;
            margin: 0.35rem auto 0 !important;
            max-width: 38rem;
            letter-spacing: -0.015em !important;
          }
          .fv-intro-cta-gap {
            height: 1.15rem;
          }
          section.main .block-container .stButton > button[kind="primary"] {
            min-height: 4.1rem !important;
            padding: 1.05rem 2.35rem !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.08em !important;
            text-transform: uppercase !important;
            border-radius: 0.375rem !important;
            background: #1a1a1a !important;
            border: 2px solid #1a1a1a !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            font-family: "JetBrains Mono", ui-monospace, monospace !important;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1) !important;
            transition: background-color 0.15s ease, color 0.15s ease, transform 0.08s ease,
              box-shadow 0.08s ease !important;
          }
          section.main .block-container .stButton > button[kind="primary"]:active:not(:disabled) {
            transform: scale(0.98) !important;
            background: #333333 !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            box-shadow: 0 2px 4px -1px rgb(0 0 0 / 0.1) !important;
          }
          section.main .block-container .stButton > button[kind="primary"]:hover {
            background: #333333 !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
          }
          section.main .block-container .stButton > button[kind="primary"]:focus-visible {
            outline: 3px solid #1a1a1a !important;
            outline-offset: 2px !important;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _inject_emerald_theme() -> None:
    """Magazine-grade readability: warm off-white page, carbon text, soft-depth cards & buttons (Streamlit overrides)."""
    try:
        _ui_lang = str(st.session_state.get("ui_lang", "en") or "en").strip().lower()
    except Exception:
        _ui_lang = "en"
    _zh_serif_block = ""
    if _ui_lang == "zh":
        _zh_serif_block = """
          /* Chinese UI: stable CJK serif stack (Noto Serif SC loads above) */
          .stApp,
          section.main {
            font-family: "Noto Serif SC", "Source Han Serif SC", "Source Serif 4", Georgia, serif !important;
          }
          section.main [data-testid="stMarkdownContainer"] p,
          section.main [data-testid="stMarkdownContainer"] li {
            font-family: "Noto Serif SC", "Source Han Serif SC", "Source Serif 4", Georgia, serif !important;
          }
          section.main h1,
          section.main h2,
          section.main h3 {
            font-family: "Noto Serif SC", "Source Han Serif SC", "Playfair Display", Georgia, serif !important;
          }
          section.main [data-testid="stWidgetLabel"] p,
          section.main label[data-testid="stWidgetLabel"] p {
            font-family: "Noto Serif SC", "Source Han Serif SC", "Source Serif 4", Georgia, serif !important;
          }
          section.main button[kind="segmented_control"],
          section.main button[kind="segmented_controlActive"],
          section.main button[data-testid^="stBaseButton-segmented_control"] {
            font-family: "Noto Serif SC", "Source Han Serif SC", "Source Serif 4", Georgia, serif !important;
          }
        """
    _theme_html = """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Noto+Serif+SC:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,500;0,8..60,600;0,8..60,700;1,8..60,400&display=swap" rel="stylesheet">
        <style>
          :root {
            --fv-page: #f9f9f7;
            --fv-card: #ffffff;
            --fv-muted-bg: #f3f3f0;
            --fv-border: #d1d5db;
            --fv-border-strong: #9ca3af;
            --fv-text: #1a1a1a;
            --fv-heading: #1a1a1a;
            --fv-muted: #4b5563;
            --fv-accent: #059669;
            --fv-accent-hover: #047857;
            --fv-accent-pressed: #065f46;
            --fv-emerald: #059669;
            --fv-emerald-soft: #ecfdf5;
            --fv-slider-fill: #059669;
            --fv-callout-bg: #ffffff;
            --fv-callout-border: #e5e7eb;
            --fv-warn: #991b1b;
            --fv-card-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            --fv-btn-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            --fv-btn-shadow-active: 0 2px 4px -1px rgb(0 0 0 / 0.1);
          }
          html {
            font-size: 144%;
          }
          html, body, .stApp {
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
          }
          .stApp {
            font-family: "Source Serif 4", Georgia, "Times New Roman", serif !important;
            color: var(--fv-text) !important;
            background-color: #f9f9f7 !important;
            background-image: none !important;
          }
          section.main h1 {
            font-family: "Playfair Display", Georgia, serif !important;
            font-size: clamp(2.5rem, 4.5vw, 3.75rem) !important;
            font-weight: 600 !important;
            letter-spacing: -0.03em !important;
            line-height: 1.08 !important;
          }
          section.main h2 {
            font-family: "Playfair Display", Georgia, serif !important;
            font-size: clamp(1.85rem, 3.2vw, 2.65rem) !important;
            font-weight: 600 !important;
            letter-spacing: -0.03em !important;
          }
          section.main h3 {
            font-family: "Playfair Display", Georgia, serif !important;
            font-size: clamp(1.5rem, 2.6vw, 2.15rem) !important;
            font-weight: 600 !important;
            letter-spacing: -0.025em !important;
          }
          section.main [data-testid="stCaptionContainer"] {
            font-family: "JetBrains Mono", ui-monospace, monospace !important;
            font-size: 0.9375rem !important;
            letter-spacing: 0.05em !important;
            text-transform: uppercase !important;
          }
          section.main [data-testid="stMarkdownContainer"] p {
            font-size: 1.5rem !important;
            line-height: 1.8 !important;
          }
          .stButton > button {
            font-size: 1rem !important;
            border-radius: 0.375rem !important;
          }
          [data-testid="stMetricLabel"] {
            font-size: 1.05rem !important;
            letter-spacing: 0.02em !important;
          }
          /* Metric title row: test id is on the <label>, not a wrapping div — force dark text. */
          [data-testid="stMetricLabel"],
          [data-testid="stMetricLabel"] * {
            color: var(--fv-heading) !important;
          }
          div[data-testid="stMetricValue"] {
            font-size: 1.65rem !important;
            font-family: "JetBrains Mono", ui-monospace, monospace !important;
            font-weight: 600 !important;
            letter-spacing: -0.02em !important;
            color: var(--fv-accent) !important;
          }
          [data-testid="stWidgetLabel"] p,
          label[data-testid="stWidgetLabel"] p {
            font-size: 1.4rem !important;
            line-height: 1.5 !important;
          }
          [data-testid="stWidgetLabel"],
          [data-testid="stWidgetLabel"] * {
            color: var(--fv-heading) !important;
          }
          /* Radio / checkbox / multi-select — option labels (incl. horizontal legend) must stay dark. */
          section.main [data-testid="stRadio"],
          section.main [data-testid="stRadio"] *,
          section.main [data-testid="stRadioGroup"],
          section.main [data-testid="stRadioGroup"] *,
          section.main [data-testid="stCheckbox"],
          section.main [data-testid="stCheckbox"] *,
          section.main [data-testid="stMultiSelect"],
          section.main [data-testid="stMultiSelect"] * {
            color: var(--fv-heading) !important;
          }
          section.main [data-baseweb="radio"],
          section.main [data-baseweb="radio"] * {
            color: var(--fv-heading) !important;
          }
          section.main [data-baseweb="checkbox"],
          section.main [data-baseweb="checkbox"] * {
            color: var(--fv-heading) !important;
          }
          [data-testid="stDataFrame"] {
            font-size: 1.15rem !important;
          }
          section.main .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2.5rem !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
          }
          section.main hr {
            margin: 2.25rem 0 !important;
            border: none !important;
            border-top: 1px solid var(--fv-border) !important;
          }
          div[data-testid="element-container"] {
            margin-bottom: 0.35rem;
          }
          div[data-testid="stProgress"] > div > div > div > div {
            background: #059669 !important;
            box-shadow: 0 0 8px #10b981 !important;
          }
          div[data-testid="stProgress"] > div {
            background: var(--fv-border) !important;
            border-radius: 0 !important;
          }
          .stButton > button {
            font-family: "JetBrains Mono", ui-monospace, monospace !important;
            transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease,
              transform 0.08s ease, box-shadow 0.08s ease !important;
            background: #1a1a1a !important;
            border: 2px solid #1a1a1a !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            font-weight: 600 !important;
            border-radius: 0.375rem !important;
            padding: 0.9rem 1.85rem !important;
            font-size: 1rem !important;
            letter-spacing: 0.08em !important;
            text-transform: uppercase !important;
            box-shadow: var(--fv-btn-shadow) !important;
          }
          .stButton > button:hover {
            background: #333333 !important;
            border-color: #1a1a1a !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
          }
          .stButton > button:active:not(:disabled) {
            transform: scale(0.98) !important;
            background: #333333 !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            box-shadow: var(--fv-btn-shadow-active) !important;
          }
          .stButton > button[kind="primary"] {
            /* Inherits same black / white treatment as base `.stButton > button` */
          }
          .stButton > button:focus-visible {
            outline: 3px solid #1a1a1a !important;
            outline-offset: 2px !important;
          }
          h1, h2, h3 {
            color: var(--fv-heading) !important;
          }
          div[data-testid="stChatMessage"] {
            border-radius: 0.375rem !important;
            border: none !important;
            background: #ffffff !important;
            color: var(--fv-text) !important;
            -webkit-text-fill-color: var(--fv-text) !important;
            box-shadow: var(--fv-card-shadow) !important;
          }
          /* Slider (Base Web): gray rail + green fill to thumb; value text green (not theme primary/red) */
          .stSlider [data-baseweb="slider"] > div > div > div {
            background: var(--fv-border) !important;
            background-color: var(--fv-border) !important;
          }
          .stSlider [data-baseweb="slider"] > div > div > div > div {
            background: var(--fv-slider-fill) !important;
            background-color: var(--fv-slider-fill) !important;
          }
          /* Extra nesting in some Streamlit / Base Web builds (fill bar inside rail) */
          .stSlider [data-baseweb="slider"] > div > div > div > div > div:not([role="slider"]) {
            background: var(--fv-slider-fill) !important;
            background-color: var(--fv-slider-fill) !important;
          }
          .stSlider [data-baseweb="slider"] div:has(> div[role="slider"]),
          [data-testid="stSlider"] [data-baseweb="slider"] div:has(> div[role="slider"]) {
            background: transparent !important;
            background-color: transparent !important;
          }
          [data-testid="stSlider"] [data-baseweb="slider"] > div > div > div {
            background: var(--fv-border) !important;
            background-color: var(--fv-border) !important;
          }
          [data-testid="stSlider"] [data-baseweb="slider"] > div > div > div > div {
            background: var(--fv-slider-fill) !important;
            background-color: var(--fv-slider-fill) !important;
          }
          [data-testid="stSlider"] [data-baseweb="slider"] > div > div > div > div > div:not([role="slider"]) {
            background: var(--fv-slider-fill) !important;
            background-color: var(--fv-slider-fill) !important;
          }
          .stSlider [data-baseweb="slider"] div[role="slider"],
          [data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
            background: #ffffff !important;
            background-color: #ffffff !important;
            border: 2px solid var(--fv-accent) !important;
            box-shadow: var(--fv-card-shadow) !important;
          }
          .stSlider [data-baseweb="slider"] div[role="slider"]:focus-visible,
          [data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"]:focus-visible {
            box-shadow: 0 0 0 2px #ffffff, 0 0 0 4px var(--fv-slider-fill) !important;
          }
          /* Value label above thumb */
          .stSlider [data-baseweb="slider"] div:has(> div[role="slider"]) > div:not([role="slider"]),
          [data-testid="stSlider"] [data-baseweb="slider"] div:has(> div[role="slider"]) > div:not([role="slider"]) {
            font-size: clamp(1.125rem, 2.8vw, 1.375rem) !important;
            font-weight: 600 !important;
            color: var(--fv-slider-fill) !important;
            -webkit-text-fill-color: var(--fv-slider-fill) !important;
            line-height: 1.2 !important;
            background: transparent !important;
            background-color: transparent !important;
          }
          .stCaption, [data-testid="stCaptionContainer"] {
            color: var(--fv-muted) !important;
          }
          /* --- Unified modules: alerts (strip Streamlit tint + inner panels) --- */
          [data-testid="stAlert"],
          div.stAlert {
            background: var(--fv-callout-bg) !important;
            background-color: var(--fv-callout-bg) !important;
            border: none !important;
            border-left: 4px solid var(--fv-accent) !important;
            border-radius: 0.375rem !important;
            box-shadow: var(--fv-card-shadow) !important;
            color: var(--fv-text) !important;
          }
          [data-testid="stAlert"] div[role="alert"],
          div.stAlert div[role="alert"],
          [data-testid="stAlert"] > div,
          div.stAlert > div {
            background: transparent !important;
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            color: var(--fv-text) !important;
          }
          [data-testid="stAlert"] p,
          [data-testid="stAlert"] li,
          [data-testid="stAlert"] span,
          [data-testid="stAlert"] [data-testid="stMarkdownContainer"] {
            color: var(--fv-text) !important;
          }
          [data-testid="stAlert"] strong {
            color: var(--fv-heading) !important;
          }
          [data-testid="stAlert"] a {
            color: var(--fv-accent) !important;
            text-decoration: underline !important;
          }
          [data-testid="stAlert"] svg {
            fill: var(--fv-muted) !important;
          }
          /* st.json uses react-json-view monokai on light theme — force light panel */
          [data-testid="stJson"],
          [data-testid="stJsonColumnViewer"],
          .stJson {
            background: var(--fv-card) !important;
            border: none !important;
            border-radius: 0.375rem !important;
            box-shadow: var(--fv-card-shadow) !important;
          }
          [data-testid="stJson"] .react-json-view,
          [data-testid="stJsonColumnViewer"] .react-json-view,
          .stJson .react-json-view {
            background-color: var(--fv-emerald-soft) !important;
          }
          /* Exception / stack trace blocks */
          [data-testid="stException"],
          .stException {
            background: var(--fv-callout-bg) !important;
            border: none !important;
            border-left: 4px solid var(--fv-warn) !important;
            border-radius: 0.375rem !important;
            box-shadow: var(--fv-card-shadow) !important;
            color: var(--fv-text) !important;
          }
          [data-testid="stException"] a {
            color: var(--fv-accent-hover) !important;
          }
          [data-testid="stErrorElementStack"] pre,
          [data-testid="stErrorElementStack"] code,
          [data-testid="stException"] pre,
          [data-testid="stException"] code {
            background: var(--fv-emerald-soft) !important;
            color: var(--fv-heading) !important;
            border: 1px solid var(--fv-border) !important;
            border-radius: 0.25rem !important;
          }
          /* Markdown fenced code — default Streamlit can look like a dark “box” */
          [data-testid="stMarkdownContainer"] pre {
            background: var(--fv-emerald-soft) !important;
            color: var(--fv-heading) !important;
            border: 1px solid var(--fv-border) !important;
            border-radius: 0.25rem !important;
          }
          [data-testid="stMarkdownContainer"] pre code {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            color: inherit !important;
          }
          [data-testid="stMarkdownContainer"] :not(pre) > code {
            background: var(--fv-emerald-soft) !important;
            color: var(--fv-heading) !important;
            border: 1px solid var(--fv-border) !important;
            border-radius: 0.25rem !important;
            padding: 0.1em 0.35em !important;
            font-family: "JetBrains Mono", ui-monospace, monospace !important;
            font-size: 0.9em !important;
          }
          /* Bordered blocks (e.g. st.container(border=True), chat shell) */
          section.main [data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--fv-card) !important;
            border: none !important;
            border-radius: 0.375rem !important;
            box-shadow: var(--fv-card-shadow) !important;
          }
          /* Chat bubbles: white card + black type (Streamlit can force light text on some builds). */
          section.main [data-testid="stChatMessage"],
          section.main [data-testid="stChatMessage"] > div {
            background: #ffffff !important;
            background-color: #ffffff !important;
            border: none !important;
            color: var(--fv-text) !important;
            -webkit-text-fill-color: var(--fv-text) !important;
            box-shadow: var(--fv-card-shadow) !important;
            border-radius: 0.375rem !important;
          }
          section.main [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
          section.main [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
          section.main [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li,
          section.main [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] span,
          section.main [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] strong,
          section.main [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] em,
          section.main [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h1,
          section.main [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h2,
          section.main [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h3 {
            color: var(--fv-text) !important;
            -webkit-text-fill-color: var(--fv-text) !important;
            font-size: 1.2rem !important;
            line-height: 1.65 !important;
          }
          section.main [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] a {
            color: var(--fv-accent) !important;
            -webkit-text-fill-color: var(--fv-accent) !important;
            text-decoration: underline !important;
          }
          /* Expanders */
          section.main [data-testid="stExpander"] {
            background: var(--fv-card) !important;
            border: none !important;
            border-radius: 0.375rem !important;
            box-shadow: var(--fv-card-shadow) !important;
          }
          section.main [data-testid="stExpander"] summary,
          section.main [data-testid="stExpander"] summary span {
            color: var(--fv-heading) !important;
          }
          /* Tabs & Segmented Control */
          section.main [data-baseweb="tab-list"] {
            border-bottom: 1px solid var(--fv-border) !important;
            gap: 0.25rem !important;
          }
          section.main button[role="tab"] {
            color: var(--fv-heading) !important;
            background: #ffffff !important;
            border-radius: 0 !important;
          }
          section.main button[role="tab"][aria-selected="true"] {
            color: #ffffff !important;
            background: #1a1a1a !important;
            font-weight: bold !important;
            border-bottom: none !important;
          }
          section.main [data-testid="stSegmentedControl"] {
            background: #ffffff !important;
            border-radius: 0.375rem !important;
            padding: 0.25rem !important;
            border: 2px solid #1a1a1a !important;
            box-shadow: var(--fv-card-shadow) !important;
          }
          section.main [data-testid="stSegmentedControl"] > div {
            background: transparent !important;
            border: none !important;
          }
          section.main [data-testid="stSegmentedControl"] button,
          section.main [data-testid="stSegmentedControl"] label,
          section.main button[kind="segmented_control"] {
            background: #ffffff !important;
            background-color: #ffffff !important;
            border: 2px solid #1a1a1a !important;
            box-shadow: none !important;
            min-height: 5rem !important;
          }
          section.main [data-testid="stSegmentedControl"] p,
          section.main [data-testid="stSegmentedControl"] span,
          section.main [data-testid="stSegmentedControl"] strong,
          section.main button[kind="segmented_control"] p,
          section.main button[kind="segmented_control"] span,
          section.main button[kind="segmented_control"] strong,
          section.main button[kind="segmented_control"] {
            color: #404040 !important;
            -webkit-text-fill-color: #404040 !important;
            font-size: 1.25rem !important;
            font-weight: 700 !important;
          }
          section.main [data-testid="stSegmentedControl"] button[aria-selected="true"],
          section.main [data-testid="stSegmentedControl"] button[aria-checked="true"],
          section.main [data-testid="stSegmentedControl"] label[data-selected="true"],
          section.main [data-testid="stSegmentedControl"] div[data-selected="true"],
          section.main [data-testid="stSegmentedControl"] div[data-baseweb="radio"][aria-checked="true"],
          section.main [data-testid="stSegmentedControl"] button[data-baseweb="radio"][aria-checked="true"],
          section.main button[kind="segmented_controlActive"] {
            background: #1a1a1a !important;
            background-color: #1a1a1a !important;
            border: 2px solid #1a1a1a !important;
            border-radius: 0.25rem !important;
            min-height: 5rem !important;
            box-shadow: none !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
          }
          section.main [data-testid="stSegmentedControl"] button[aria-selected="true"] p,
          section.main [data-testid="stSegmentedControl"] button[aria-selected="true"] span,
          section.main [data-testid="stSegmentedControl"] button[aria-checked="true"] p,
          section.main [data-testid="stSegmentedControl"] button[aria-checked="true"] span,
          section.main [data-testid="stSegmentedControl"] label[data-selected="true"] p,
          section.main [data-testid="stSegmentedControl"] label[data-selected="true"] span,
          section.main [data-testid="stSegmentedControl"] div[data-selected="true"] p,
          section.main [data-testid="stSegmentedControl"] div[data-selected="true"] span,
          section.main [data-testid="stSegmentedControl"] div[data-baseweb="radio"][aria-checked="true"] p,
          section.main [data-testid="stSegmentedControl"] div[data-baseweb="radio"][aria-checked="true"] span,
          section.main [data-testid="stSegmentedControl"] button[data-baseweb="radio"][aria-checked="true"] p,
          section.main [data-testid="stSegmentedControl"] button[data-baseweb="radio"][aria-checked="true"] span,
          section.main [data-testid="stSegmentedControl"] button[aria-checked="true"] strong,
          section.main [data-testid="stSegmentedControl"] button[aria-selected="true"] strong,
          section.main button[kind="segmented_controlActive"] p,
          section.main button[kind="segmented_controlActive"] span,
          section.main button[kind="segmented_controlActive"] strong,
          section.main button[kind="segmented_controlActive"] {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            font-size: 1.25rem !important;
            font-weight: 700 !important;
          }
          /* Inputs (legacy widgets without Base Web wrapper) */
          section.main .stTextInput input,
          section.main .stNumberInput input,
          section.main textarea {
            background: var(--fv-card) !important;
            color: var(--fv-heading) !important;
            border: 2px solid var(--fv-border) !important;
            border-radius: 0.375rem !important;
            box-shadow: var(--fv-card-shadow) !important;
            font-family: "Source Serif 4", Georgia, serif !important;
          }
          section.main .stTextInput input:focus,
          section.main .stNumberInput input:focus,
          section.main textarea:focus {
            border-color: var(--fv-accent) !important;
            background-color: #ecfdf5 !important;
            box-shadow: var(--fv-card-shadow), 0 0 0 3px rgba(5, 150, 105, 0.25) !important;
            outline: none !important;
          }
          /* Base Web input shell (Streamlit 1.3x+) — soft card, emerald focus */
          section.main [data-baseweb="base-input"] {
            background-color: #ffffff !important;
            border: 2px solid var(--fv-border) !important;
            border-radius: 0.375rem !important;
            box-shadow: var(--fv-card-shadow) !important;
            transition: background-color 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease !important;
          }
          section.main [data-baseweb="base-input"]:focus-within {
            background-color: #ecfdf5 !important;
            border-color: var(--fv-accent) !important;
            box-shadow: var(--fv-card-shadow), 0 0 0 3px rgba(5, 150, 105, 0.25) !important;
          }
          section.main [data-baseweb="base-input"] > div {
            background-color: #ffffff !important;
            color: var(--fv-heading) !important;
            transition: background-color 0.15s ease !important;
          }
          section.main [data-baseweb="base-input"]:focus-within > div {
            background-color: #ffffff !important;
          }
          section.main [data-baseweb="base-input"] input {
            background-color: transparent !important;
            color: var(--fv-heading) !important;
            -webkit-text-fill-color: var(--fv-heading) !important;
            caret-color: var(--fv-heading) !important;
            border: none !important;
            border-radius: 0 !important;
          }
          section.main [data-baseweb="base-input"] input::placeholder {
            color: var(--fv-muted) !important;
            -webkit-text-fill-color: var(--fv-muted) !important;
            opacity: 1 !important;
            font-style: italic !important;
          }
          section.main [data-baseweb="base-input"] svg {
            fill: var(--fv-heading) !important;
            color: var(--fv-heading) !important;
          }
          section.main [data-baseweb="base-input"] button {
            background: transparent !important;
            color: var(--fv-heading) !important;
          }
          /* Segmented control — elderly-friendly: inactive white/#404040, active #1A1A1A/#FFF, 2px border */
          section.main button[kind="segmented_control"],
          section.main button[kind="segmented_controlActive"],
          section.main button[data-testid^="stBaseButton-segmented_control"] {
            border-radius: 0.375rem !important;
            box-shadow: none !important;
            font-family: inherit !important;
            min-height: 5rem !important;
            padding: 0.55rem 0.9rem !important;
            font-size: 1.25rem !important;
            line-height: 1.35 !important;
            font-weight: 700 !important;
            white-space: normal !important;
            text-align: center !important;
            border: 2px solid #1a1a1a !important;
            outline: none !important;
          }
          section.main button[kind="segmented_control"],
          section.main button[data-testid^="stBaseButton-segmented_control"]:not([data-testid*="Active"]) {
            background-color: #ffffff !important;
            background: #ffffff !important;
            color: #404040 !important;
            -webkit-text-fill-color: #404040 !important;
            transition: background-color 0.15s ease, color 0.15s ease, transform 0.08s ease !important;
          }
          section.main button[kind="segmented_control"]:hover:not(:disabled),
          section.main button[kind="segmented_control"]:focus-visible:not(:disabled),
          section.main
            button[data-testid^="stBaseButton-segmented_control"]:not([data-testid*="Active"]):hover:not(:disabled),
          section.main
            button[data-testid^="stBaseButton-segmented_control"]:not([data-testid*="Active"]):focus-visible:not(
              :disabled
            ) {
            background-color: #f3f3f0 !important;
            color: #404040 !important;
            -webkit-text-fill-color: #404040 !important;
          }
          section.main button[kind="segmented_controlActive"],
          section.main button[data-testid*="segmented_controlActive"] {
            background-color: #1a1a1a !important;
            background: #1a1a1a !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
          }
          section.main button[kind="segmented_controlActive"] *,
          section.main button[data-testid*="segmented_controlActive"] *,
          section.main button[kind="segmented_controlActive"] p,
          section.main button[kind="segmented_controlActive"] span,
          section.main button[kind="segmented_controlActive"] strong,
          section.main button[data-testid*="segmented_controlActive"] p,
          section.main button[data-testid*="segmented_controlActive"] span,
          section.main button[data-testid*="segmented_controlActive"] strong {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
          }
          section.main button[kind="segmented_control"] *,
          section.main button[data-testid^="stBaseButton-segmented_control"]:not([data-testid*="Active"]) *,
          section.main button[kind="segmented_control"] p,
          section.main button[kind="segmented_control"] span,
          section.main button[kind="segmented_control"] strong,
          section.main
            button[data-testid^="stBaseButton-segmented_control"]:not([data-testid*="Active"]) p,
          section.main
            button[data-testid^="stBaseButton-segmented_control"]:not([data-testid*="Active"]) span,
          section.main
            button[data-testid^="stBaseButton-segmented_control"]:not([data-testid*="Active"]) strong {
            color: #404040 !important;
            -webkit-text-fill-color: #404040 !important;
          }
          section.main button[kind="segmented_control"] a,
          section.main button[kind="segmented_controlActive"] a,
          section.main button[data-testid^="stBaseButton-segmented_control"] a {
            color: inherit !important;
            -webkit-text-fill-color: inherit !important;
            text-decoration: none !important;
          }
          section.main button[kind="segmented_control"] .stMarkdownColoredText,
          section.main
            button[data-testid^="stBaseButton-segmented_control"]:not([data-testid*="Active"])
            .stMarkdownColoredText {
            color: #404040 !important;
            -webkit-text-fill-color: #404040 !important;
          }
          section.main button[kind="segmented_controlActive"] .stMarkdownColoredText,
          section.main button[data-testid*="segmented_controlActive"] .stMarkdownColoredText {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
          }
          section.main button[kind="segmented_controlActive"]:hover:not(:disabled),
          section.main button[kind="segmented_controlActive"]:focus-visible:not(:disabled),
          section.main button[data-testid*="segmented_controlActive"]:hover:not(:disabled),
          section.main button[data-testid*="segmented_controlActive"]:focus-visible:not(:disabled) {
            background-color: #333333 !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            border-color: #1a1a1a !important;
          }
          section.main button[kind="segmented_control"]:focus-visible,
          section.main button[kind="segmented_controlActive"]:focus-visible,
          section.main button[data-testid^="stBaseButton-segmented_control"]:focus-visible {
            outline: 3px solid #1a1a1a !important;
            outline-offset: 2px !important;
          }
          section.main [data-baseweb="select"] > div {
            background: var(--fv-card) !important;
            border: 1px solid var(--fv-border) !important;
            border-radius: 0.375rem !important;
            box-shadow: var(--fv-card-shadow) !important;
            color: var(--fv-heading) !important;
            font-size: 1.08rem !important;
          }
          /* Secondary buttons — same high-contrast treatment as primary */
          .stButton > button[kind="secondary"] {
            background: #1a1a1a !important;
            border: 2px solid #1a1a1a !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            letter-spacing: 0.08em !important;
            text-transform: uppercase !important;
            font-weight: 600 !important;
            box-shadow: var(--fv-btn-shadow) !important;
            transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease,
              transform 0.08s ease, box-shadow 0.08s ease !important;
          }
          .stButton > button[kind="secondary"]:hover {
            background: #333333 !important;
            border-color: #1a1a1a !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
          }
          .stButton > button[kind="secondary"]:focus-visible {
            outline: 3px solid #1a1a1a !important;
            outline-offset: 2px !important;
          }
          /* --- Readable surfaces everywhere: links + markdown (no theme red/pink) --- */
          section.main [data-testid="stMarkdownContainer"] a,
          section.main [data-testid="stMarkdownContainer"] a:visited {
            color: var(--fv-accent) !important;
            text-decoration: underline !important;
            text-underline-offset: 0.2em !important;
          }
          section.main [data-testid="stMarkdownContainer"] a:hover,
          section.main [data-testid="stMarkdownContainer"] a:focus-visible {
            color: var(--fv-accent-hover) !important;
            background-color: var(--fv-emerald-soft) !important;
          }
          section.main [data-testid="stMarkdownContainer"] .stMarkdownColoredText {
            color: var(--fv-text) !important;
            -webkit-text-fill-color: var(--fv-text) !important;
          }
          section.main [data-testid="stMarkdownContainer"] strong {
            color: var(--fv-heading) !important;
            -webkit-text-fill-color: var(--fv-heading) !important;
          }
          /* Pills — soft cards + emerald active */
          section.main button[kind="pills"],
          section.main button[kind="pillsActive"],
          section.main button[data-testid^="stBaseButton-pills"] {
            border-radius: 0.375rem !important;
            box-shadow: var(--fv-card-shadow) !important;
            font-family: "Source Serif 4", Georgia, serif !important;
            min-height: 2.85rem !important;
            padding: 0.45rem 0.85rem !important;
            font-size: 1.02rem !important;
            line-height: 1.35 !important;
            border: none !important;
          }
          section.main button[kind="pills"],
          section.main button[data-testid^="stBaseButton-pills"]:not([data-testid*="Active"]) {
            background-color: #ffffff !important;
            background: #ffffff !important;
            color: var(--fv-text) !important;
            -webkit-text-fill-color: var(--fv-text) !important;
            transition: background-color 0.15s ease, color 0.15s ease, box-shadow 0.15s ease,
              transform 0.08s ease !important;
          }
          section.main button[kind="pills"]:hover:not(:disabled),
          section.main button[kind="pills"]:focus-visible:not(:disabled),
          section.main
            button[data-testid^="stBaseButton-pills"]:not([data-testid*="Active"]):hover:not(:disabled),
          section.main
            button[data-testid^="stBaseButton-pills"]:not([data-testid*="Active"]):focus-visible:not(
              :disabled
            ) {
            background-color: var(--fv-muted-bg) !important;
            color: var(--fv-text) !important;
            -webkit-text-fill-color: var(--fv-text) !important;
            box-shadow: 0 6px 8px -2px rgb(0 0 0 / 0.12), 0 2px 4px -2px rgb(0 0 0 / 0.06) !important;
          }
          section.main button[kind="pillsActive"],
          section.main button[data-testid*="pillsActive"] {
            background-color: var(--fv-accent) !important;
            background: var(--fv-accent) !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            box-shadow: var(--fv-btn-shadow) !important;
          }
          section.main button[kind="pillsActive"] *,
          section.main button[data-testid*="pillsActive"] *,
          section.main button[kind="pillsActive"] p,
          section.main button[kind="pillsActive"] span,
          section.main button[kind="pillsActive"] strong,
          section.main button[data-testid*="pillsActive"] p,
          section.main button[data-testid*="pillsActive"] span,
          section.main button[data-testid*="pillsActive"] strong {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
          }
          section.main button[kind="pills"] *,
          section.main button[data-testid^="stBaseButton-pills"]:not([data-testid*="Active"]) *,
          section.main button[kind="pills"] .stMarkdownColoredText,
          section.main
            button[data-testid^="stBaseButton-pills"]:not([data-testid*="Active"]) .stMarkdownColoredText {
            color: var(--fv-text) !important;
            -webkit-text-fill-color: var(--fv-text) !important;
          }
          section.main button[kind="pillsActive"] .stMarkdownColoredText,
          section.main button[data-testid*="pillsActive"] .stMarkdownColoredText {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
          }
          section.main button[kind="pillsActive"]:hover:not(:disabled),
          section.main button[kind="pillsActive"]:focus-visible:not(:disabled),
          section.main button[data-testid*="pillsActive"]:hover:not(:disabled),
          section.main button[data-testid*="pillsActive"]:focus-visible:not(:disabled) {
            background-color: var(--fv-accent-hover) !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
          }
          /* Radio / checkbox: light panels only, legible labels */
          section.main [data-testid="stRadio"],
          section.main [data-testid="stRadio"] > div,
          section.main [data-testid="stRadio"] [role="radiogroup"] {
            background-color: transparent !important;
            background: transparent !important;
          }
          section.main [data-testid="stRadio"] label,
          section.main [data-testid="stRadio"] label *,
          section.main [data-testid="stRadio"] p,
          section.main [data-testid="stRadio"] span {
            color: var(--fv-heading) !important;
            -webkit-text-fill-color: var(--fv-heading) !important;
          }
          section.main [data-baseweb="radio"] {
            background: transparent !important;
          }
          section.main [data-testid="stCheckbox"] label,
          section.main [data-testid="stCheckbox"] label *,
          section.main [data-testid="stCheckbox"] p,
          section.main [data-testid="stCheckbox"] span {
            color: var(--fv-heading) !important;
            -webkit-text-fill-color: var(--fv-heading) !important;
          }
          section.main [data-testid="stCheckbox"] svg,
          section.main [data-baseweb="checkbox"] svg {
            fill: var(--fv-heading) !important;
            color: var(--fv-heading) !important;
          }
          /* Selectbox trigger + chevron */
          section.main [data-baseweb="select"] svg {
            fill: var(--fv-heading) !important;
            color: var(--fv-heading) !important;
          }
          /* Portals (dropdowns render outside section.main) — white menu, gray hover, never red */
          body [data-baseweb="popover"],
          body [data-baseweb="popover"] > div {
            background-color: #ffffff !important;
            color: var(--fv-text) !important;
            border-radius: 0.375rem !important;
            box-shadow: var(--fv-card-shadow) !important;
            border: 1px solid var(--fv-border) !important;
          }
          body [data-baseweb="menu"],
          body [role="listbox"],
          body [data-baseweb="menu"] ul {
            background-color: #ffffff !important;
            color: var(--fv-text) !important;
            border-radius: 0.375rem !important;
          }
          body [data-baseweb="menu"] li,
          body [role="option"],
          body [data-baseweb="menu"] [role="option"] {
            background-color: #ffffff !important;
            color: var(--fv-text) !important;
          }
          body [data-baseweb="menu"] li:hover,
          body [data-baseweb="menu"] li:focus,
          body [data-baseweb="menu"] li[aria-selected="true"],
          body [role="option"]:hover,
          body [role="option"][aria-selected="true"] {
            background-color: var(--fv-muted-bg) !important;
            color: var(--fv-text) !important;
          }
          body [data-baseweb="menu"] li span,
          body [data-baseweb="menu"] li div {
            color: var(--fv-text) !important;
          }
          /* Multiselect chips + chat/composer surfaces */
          section.main [data-baseweb="tag"] {
            background-color: #ffffff !important;
            color: var(--fv-text) !important;
            border: 1px solid var(--fv-border) !important;
            border-radius: 0.375rem !important;
            box-shadow: var(--fv-card-shadow) !important;
          }
          section.main [data-baseweb="tag"] svg {
            fill: var(--fv-heading) !important;
          }
          section.main [data-testid="stChatInput"] [data-baseweb="base-input"],
          section.main [data-testid="stChatInput"] textarea {
            background-color: #ffffff !important;
            color: var(--fv-heading) !important;
            -webkit-text-fill-color: var(--fv-heading) !important;
            caret-color: var(--fv-heading) !important;
            border: 1px solid var(--fv-border) !important;
            border-radius: 0.375rem !important;
            box-shadow: var(--fv-card-shadow) !important;
          }
          section.main [data-testid="stChatInput"] textarea::placeholder {
            color: var(--fv-muted) !important;
            -webkit-text-fill-color: var(--fv-muted) !important;
            opacity: 1 !important;
          }
          /* Sidebar (if expanded) */
          [data-testid="stSidebar"] {
            background: var(--fv-page) !important;
            border-right: 1px solid var(--fv-border) !important;
          }
          [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
          [data-testid="stSidebar"] label {
            color: var(--fv-text) !important;
          }
          .stButton > button[kind="secondary"]:active:not(:disabled) {
            transform: translateY(1px) !important;
            box-shadow: 0 2px 4px -1px rgb(0 0 0 / 0.12) !important;
            background: #333333 !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
          }
          @media (max-width: 768px) {
            section.main [data-testid="stHorizontalBlock"] {
              flex-direction: column !important;
              align-items: stretch !important;
              gap: 1rem !important;
            }
            section.main [data-testid="stHorizontalBlock"] > div[data-testid="column"] {
              width: 100% !important;
              min-width: 0 !important;
              flex: 1 1 auto !important;
            }
          }
        </style>
        """
    st.markdown(
        _theme_html.replace("        </style>", _zh_serif_block + "\n        </style>", 1),
        unsafe_allow_html=True,
    )


def _inject_onboarding_stage_css() -> None:
    _inject_soft_survey_backdrop_css()
    st.markdown(
        """
        <style>
          section.main .block-container {
            max-width: 720px !important;
            margin-left: auto !important;
            margin-right: auto !important;
            margin-top: 0.5rem !important;
            padding-top: 2.75rem !important;
            padding-bottom: 3.25rem !important;
            padding-left: clamp(1.35rem, 4vw, 2.75rem) !important;
            padding-right: clamp(1.35rem, 4vw, 2.75rem) !important;
            background: #ffffff !important;
            border-radius: 0.5rem !important;
            border: none !important;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1) !important;
            font-size: 1.5rem;
            line-height: 1.8;
            font-family: "Source Serif 4", Georgia, serif !important;
            color: #1a1a1a !important;
            -webkit-font-smoothing: antialiased;
          }
          section.main .block-container h1 {
            font-family: "Playfair Display", Georgia, serif !important;
            font-size: clamp(2.5rem, 4vw, 3.5rem) !important;
            font-weight: 600 !important;
            color: #1a1a1a !important;
            letter-spacing: -0.04em !important;
            line-height: 1.1 !important;
            margin-bottom: 0.5rem !important;
          }
          section.main .block-container [data-testid="stMarkdownContainer"] p.onboard-baseline-lead {
            font-family: "Source Serif 4", Georgia, serif !important;
            font-size: clamp(1.15rem, 2.9vw, 1.45rem) !important;
            font-weight: 500 !important;
            line-height: 1.45 !important;
            color: #4b5563 !important;
            margin: 0.2rem 0 1.15rem 0 !important;
            letter-spacing: -0.01em !important;
          }
          section.main .block-container [data-testid="stCaptionContainer"] {
            font-family: "JetBrains Mono", ui-monospace, monospace !important;
            font-size: 0.9375rem !important;
            color: #4b5563 !important;
            margin-top: 0.5rem !important;
            margin-bottom: 1.5rem !important;
            letter-spacing: 0.08em !important;
            text-transform: uppercase !important;
          }
          section.main .block-container [data-testid="stMarkdownContainer"] h3 {
            font-family: "Playfair Display", Georgia, serif !important;
            font-size: clamp(1.35rem, 2.8vw, 1.85rem) !important;
            font-weight: 600 !important;
            color: #1a1a1a !important;
            margin: 1.75rem 0 0.85rem 0 !important;
            line-height: 1.25 !important;
            letter-spacing: -0.03em !important;
          }
          section.main .block-container [data-testid="stMarkdownContainer"] p {
            font-size: 1.5rem !important;
            line-height: 1.8 !important;
            color: #1a1a1a !important;
            margin-bottom: 1rem !important;
          }
          section.main .block-container [data-testid="stWidgetLabel"] p,
          section.main .block-container label[data-testid="stWidgetLabel"] p,
          section.main .block-container .stSlider label p {
            font-size: 1.3rem !important;
            line-height: 1.45 !important;
            color: #1a1a1a !important;
          }
          section.main .block-container .stSlider [data-baseweb="slider"] > div > div > div,
          section.main .block-container [data-testid="stSlider"] [data-baseweb="slider"] > div > div > div {
            background: #e5e5e5 !important;
            background-color: #e5e5e5 !important;
          }
          section.main .block-container .stSlider [data-baseweb="slider"] > div > div > div > div,
          section.main
            .block-container
            [data-testid="stSlider"]
            [data-baseweb="slider"]
            > div
            > div
            > div
            > div {
            background: var(--fv-slider-fill) !important;
            background-color: var(--fv-slider-fill) !important;
          }
          section.main .block-container .stSlider [data-baseweb="slider"] > div > div > div > div > div:not([role="slider"]),
          section.main
            .block-container
            [data-testid="stSlider"]
            [data-baseweb="slider"]
            > div
            > div
            > div
            > div
            > div:not([role="slider"]) {
            background: var(--fv-slider-fill) !important;
            background-color: var(--fv-slider-fill) !important;
          }
          section.main .block-container .stSlider [data-baseweb="slider"] div:has(> div[role="slider"]),
          section.main .block-container [data-testid="stSlider"] [data-baseweb="slider"] div:has(> div[role="slider"]) {
            background: transparent !important;
            background-color: transparent !important;
          }
          section.main .block-container .stSlider [data-baseweb="slider"] div[role="slider"],
          section.main .block-container [data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
            background: #ffffff !important;
            background-color: #ffffff !important;
            border: 2px solid #059669 !important;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.06) !important;
          }
          section.main .block-container .stSlider [data-baseweb="slider"] div[role="slider"]:focus-visible,
          section.main
            .block-container
            [data-testid="stSlider"]
            [data-baseweb="slider"]
            div[role="slider"]:focus-visible {
            box-shadow: 0 0 0 2px #ffffff, 0 0 0 4px var(--fv-slider-fill) !important;
          }
          section.main .block-container
            .stSlider
            [data-baseweb="slider"]
            div:has(> div[role="slider"])
            > div:not([role="slider"]),
          section.main
            .block-container
            [data-testid="stSlider"]
            [data-baseweb="slider"]
            div:has(> div[role="slider"])
            > div:not([role="slider"]) {
            font-size: clamp(1.125rem, 2.8vw, 1.375rem) !important;
            font-weight: 600 !important;
            color: var(--fv-slider-fill) !important;
            -webkit-text-fill-color: var(--fv-slider-fill) !important;
            line-height: 1.2 !important;
            background: transparent !important;
            background-color: transparent !important;
          }
          section.main .block-container div[data-baseweb="select"] > div {
            font-size: 1.08rem !important;
            min-height: 48px !important;
            border-radius: 0.375rem !important;
            border: 1px solid #d1d5db !important;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.06) !important;
          }
          section.main .block-container .stButton > button[kind="primary"] {
            min-height: 3.2rem !important;
            padding: 0.82rem 1.9rem !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
            border-radius: 0.375rem !important;
            background: #1a1a1a !important;
            border: 2px solid #1a1a1a !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1) !important;
            letter-spacing: 0.08em !important;
            text-transform: uppercase !important;
            font-family: "JetBrains Mono", ui-monospace, monospace !important;
            transition: background-color 0.15s ease, color 0.15s ease, transform 0.08s ease,
              box-shadow 0.08s ease !important;
          }
          section.main .block-container .stButton > button[kind="primary"]:active:not(:disabled) {
            transform: scale(0.98) !important;
            background: #333333 !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            box-shadow: 0 2px 4px -1px rgb(0 0 0 / 0.1) !important;
          }
          section.main .block-container .stButton > button[kind="primary"]:hover {
            background: #333333 !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
          }
          section.main .block-container .stButton > button[kind="primary"]:focus-visible {
            outline: 3px solid #1a1a1a !important;
            outline-offset: 2px !important;
          }
          div[data-testid="stProgress"] > div {
            height: 6px !important;
            border-radius: 0 !important;
            overflow: hidden !important;
          }
          div[data-testid="stProgress"] > div > div > div > div {
            background: #059669 !important;
            box-shadow: 0 0 8px #10b981 !important;
          }
          .questionnaire-privacy-shell {
            background: #ffffff;
            border: none;
            border-left: 4px solid #059669;
            border-radius: 0.375rem;
            padding: 1.5rem 1.5rem 1.6rem 1.35rem;
            margin: 0 0 2rem 0;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.06);
          }
          .questionnaire-privacy-shell h3 {
            font-family: "Playfair Display", Georgia, serif;
            margin: 0 0 0.65rem 0;
            font-size: clamp(1.35rem, 3vw, 1.75rem);
            font-weight: 600;
            color: #1a1a1a;
            letter-spacing: -0.03em;
            line-height: 1.25;
          }
          .questionnaire-privacy-shell p {
            font-family: "Source Serif 4", Georgia, serif;
            margin: 0;
            font-size: clamp(1.2rem, 2vw, 1.3rem);
            line-height: 1.7;
            color: #1a1a1a;
          }
          .questionnaire-privacy-shell strong {
            color: #1a1a1a;
            font-weight: 600;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_questionnaire_privacy_banner() -> None:
    """Large, friendly copy on the 3-step questionnaire — local cache only, no profiling."""
    st.markdown(_i18n.t("privacy_banner_html"), unsafe_allow_html=True)


def _render_intro_text_hero() -> None:
    """Full-width hero: wordmark + disclaimer line; primary CTA only."""
    _c1, _c2 = st.columns([1, 0.22])
    with _c2:
        _render_language_selector()
    st.markdown(_i18n.t("intro_hero_html"), unsafe_allow_html=True)
    st.markdown(
        f'<p class="fv-intro-cta-line">{_i18n.t("intro_cta_line")}</p>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="fv-intro-cta-gap" aria-hidden="true"></div>', unsafe_allow_html=True)
    if st.button(
        _i18n.t("intro_start_questionnaire"),
        type="primary",
        use_container_width=True,
        key="btn_intro_continue",
    ):
        st.session_state.onboarding_step = 1
        st.rerun()


def _bump_mortgage_edit_flag() -> None:
    """Set when the user changes the Own-tab all-in ``number_input`` (used to allow cache → 0 on real clears)."""
    st.session_state["_dash_mortgage_user_edit"] = True


def _sync_dash_mortgage_cache(*, allow_zero: bool = False) -> None:
    """
    Mirror ``dash_mortgage`` into ``dash_mortgage_cached`` for math when the widget is not mounted.

    **Do not** copy a spurious ``0`` from session (Streamlit may register the key before the user edits Own),
    or we wipe a good cache and the waterfall collapses (housing → $0, no step-to-step decrease).

    When the user clears the Own-tab all-in field, ``on_change`` sets ``_dash_mortgage_user_edit``; we then
    sync ``0`` into the cache so the pie matches. ``allow_zero`` is a second path for the same intent.
    """
    if "dash_mortgage" not in st.session_state:
        return
    edited = bool(st.session_state.get("_dash_mortgage_user_edit"))
    if edited:
        st.session_state.pop("_dash_mortgage_user_edit", None)
    live = float(st.session_state.get("dash_mortgage") or 0)
    if live > 0:
        st.session_state.dash_mortgage_cached = live
        return
    if allow_zero or edited:
        st.session_state.dash_mortgage_cached = live
        return


def _init_session_state() -> None:
    defaults = {
        "onboarding_step": 0,
        "onboarding_complete": False,
        "monthly_take_home": 5_000.0,
        "family": FAMILY_OPTIONS[0],
        "spending_vibe": VIBE_OPTIONS[1],
        # Default UI language: English. Not written to `wizard_user_inputs.json` — each new browser session starts in English; in-session changes persist until the tab closes.
        "ui_lang": "en",
        "last_saved_record": None,
        "advisor_messages": [],
        "llm_model": "gpt-4o-mini",
        "llm_base_url": "",
        "llm_openai_api_key": "",
        "dashboard_step": 0,
        "dash_own_mortgage_step": False,
        "dash_own_down_pct": 20,
        "dash_own_term": 30,
        "dash_own_came_from_unsure": False,
        "dash_own_property_kind": "house",
        "dash_housing_zip": "",
        "dash_housing_benchmark_rent_mo": 0.0,
        "dash_housing_benchmark_owner_mo": 0.0,
        "dash_housing_model_own_monthly": 0.0,
        "dash_housing_ui_subtab": "rent",
        "dash_housing_committed_subtab": "rent",
        "dash_own_median_confirm": _wiz_snap.OWN_MEDIAN_CONFIRM_YES,
        "dash_own_home_price": 450_000,
        "dash_own_rate_pct": 6.5,
        "dash_mortgage_cached": 0.0,
        "dash_car_status": "No car",
        "dash_car_dep_example_price": 38_000,
        "dash_car_household_cars": "1",
        "dash_transit_monthly": 0,
        "dash_car_payment_monthly": 0,
        "dash_car_depreciation_monthly": 0,
        "dash_car_insurance_monthly": 0,
        "dash_car_fuel_monthly": 0,
        "dash_car_maintenance_monthly": 0,
        "dash_car_monthly": 0,
        "dash_child_tuition_monthly": 0,
        "dash_child_childcare_monthly": 0,
        "dash_child_insurance_monthly": 0,
        "dash_child_activities_monthly": 0,
        "dash_child_entertainment_monthly": 0,
        "dash_child_clothing_monthly": 0,
        "dash_child_other_monthly": 0,
        "dash_child_monthly": 0,
        "dash_grocery": 0,
        "dash_ent_out_monthly": 0,
        "dash_ent_media_monthly": 0,
        "dash_ent_trips_monthly": 0,
        "dash_ent_play_monthly": 0,
        "dash_ent_social_monthly": 0,
        "dash_ent_other_monthly": 0,
        "dash_ent": 0,
        "dash_invest_pct": 10,
        "dash_ef_target_months": 6,
        "dash_ef_current_balance": 0.0,
        "dash_ef_monthly_save": 0.0,
        "dash_401k_match_status": "Not sure — need to check",
        "dash_pie_prefer_ledger_file": _pie_prefer_ledger_file_default(),
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # Only once per browser session: re-applying JSON on every rerun would overwrite
    # widget-driven session_state before `_refresh_wizard_snapshot` runs.
    if not st.session_state.get("_user_inputs_disk_hydrated"):
        _apply_disk_user_input_cache()
        st.session_state["_user_inputs_disk_hydrated"] = True

    if st.session_state.get("dash_housing_worksheet_side") not in ("rent", "own"):
        st.session_state.dash_housing_worksheet_side = (
            "own" if st.session_state.get("dash_own_mortgage_step") else "rent"
        )

    for _hk in ("dash_housing_ui_subtab", "dash_housing_committed_subtab"):
        if st.session_state.get(_hk) not in ("rent", "own"):
            st.session_state[_hk] = str(st.session_state.get("dash_housing_worksheet_side", "rent") or "rent").lower()

    mc = st.session_state.get("dash_own_median_confirm")
    if isinstance(mc, str) and mc.strip().startswith("Close enough"):
        st.session_state.dash_own_median_confirm = _wiz_snap.OWN_MEDIAN_CONFIRM_YES
    elif mc not in (_wiz_snap.OWN_MEDIAN_CONFIRM_YES, _wiz_snap.OWN_MEDIAN_CONFIRM_UNSURE):
        st.session_state.dash_own_median_confirm = _wiz_snap.OWN_MEDIAN_CONFIRM_YES

    _ul = str(st.session_state.get("ui_lang", "en") or "en").strip().lower()
    st.session_state.ui_lang = _ul if _ul in ("en", "es", "zh") else "en"


def _apply_disk_user_input_cache() -> None:
    """Restore wizard + onboarding answers from `data/wizard_user_inputs.json` if present."""
    blob = _wiz_snap.load_user_inputs_from_disk()
    if not blob:
        return
    for k, v in blob.items():
        if k not in _wiz_snap.WIZARD_USER_INPUT_KEYS:
            continue
        if k == "family" and v not in FAMILY_OPTIONS:
            continue
        if k == "spending_vibe" and v not in VIBE_OPTIONS:
            continue
        if k in ("dashboard_step", "onboarding_step", "dash_own_term", "dash_invest_pct", "dash_ef_target_months"):
            try:
                v = int(v)
            except (TypeError, ValueError):
                continue
        if k == "onboarding_complete":
            v = bool(v)
        if k == "dash_pie_prefer_ledger_file":
            v = bool(v)
        if k == "monthly_take_home":
            try:
                v = float(v)
            except (TypeError, ValueError):
                continue
        if k in ("dash_ef_current_balance", "dash_ef_monthly_save"):
            try:
                v = float(v)
            except (TypeError, ValueError):
                continue
        if k in ("dash_housing_benchmark_rent_mo", "dash_housing_benchmark_owner_mo", "dash_housing_model_own_monthly"):
            try:
                v = float(v)
            except (TypeError, ValueError):
                continue
        if k == "dash_housing_worksheet_side" and v not in ("rent", "own"):
            continue
        if k in ("dash_housing_ui_subtab", "dash_housing_committed_subtab"):
            vs = str(v).strip().lower()
            if vs not in ("rent", "own"):
                continue
            v = vs
        if k == "dash_own_median_confirm":
            if isinstance(v, str) and v.strip().startswith("Close enough"):
                v = _wiz_snap.OWN_MEDIAN_CONFIRM_YES
            elif v not in (_wiz_snap.OWN_MEDIAN_CONFIRM_YES, _wiz_snap.OWN_MEDIAN_CONFIRM_UNSURE):
                continue
        if k in ("llm_model", "llm_base_url"):
            v = str(v) if v is not None else ""
        if k in (
            "_wf_car_pool_meta",
            "_wf_pool_after_child_meta",
            "_wf_grocery_pool_meta",
            "_wf_entertainment_pool_meta",
        ):
            if isinstance(v, (list, tuple)):
                try:
                    v = tuple(float(x) for x in v)
                except (TypeError, ValueError):
                    continue
        if k in (
            "_wf_car_pool_usd",
            "_wf_pool_after_child_usd",
            "_wf_grocery_pool_usd",
            "_wf_entertainment_pool_usd",
            "_wf_grocery_tracker_spend_usd",
            "_wf_entertainment_tracker_spend_usd",
            "_wf_next_pie_income_snapshot",
            "_wf_next_pie_housing_usd",
            "_wf_next_pie_car_usd",
            "_wf_next_pie_child_usd",
            "_wf_next_pie_grocery_usd",
            "_wf_next_pie_fun_usd",
        ):
            try:
                v = float(v)
            except (TypeError, ValueError):
                continue
        st.session_state[k] = v
    _sync_dash_mortgage_cache()


def _append_jsonl(record: dict) -> None:
    line = json.dumps(record, ensure_ascii=False)
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def _progress_bar() -> None:
    step = int(st.session_state.onboarding_step)
    pct = min(max(step / float(TOTAL_ONBOARD_STEPS), 0.0), 1.0)
    st.progress(pct, text=None)


def _inject_wizard_css() -> None:
    """Post-onboarding wizard: magazine readability + soft-depth surfaces (matches main theme)."""
    st.markdown(
        """
        <style>
          .stApp {
            background-color: #f9f9f7 !important;
            background-image: none !important;
          }
          [data-testid="stHeader"] {
            background: #f9f9f7 !important;
            border-bottom: 1px solid #d1d5db !important;
          }
          [data-testid="stHeader"] button,
          [data-testid="stHeader"] [data-testid="stToolbar"] {
            color: #1a1a1a !important;
          }
          [data-testid="stHeader"] svg {
            fill: #1a1a1a !important;
          }
          section.main .block-container {
            font-family: "Source Serif 4", Georgia, "Times New Roman", serif;
            -webkit-font-smoothing: antialiased;
            color: #1a1a1a !important;
            font-size: 1.25rem !important;
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
          }
          .wiz-summary-strip {
            background: #ffffff;
            border: none;
            border-radius: 0.375rem;
            padding: 1.1rem 1.35rem;
            margin-bottom: 1.75rem;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.06);
          }
          .wiz-step-meta {
            font-family: "JetBrains Mono", ui-monospace, monospace;
            font-size: 0.8125rem;
            font-weight: 500;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #4b5563;
            margin: 0 0 0.5rem 0;
          }
          .wiz-title {
            font-family: "Playfair Display", Georgia, serif;
            font-size: clamp(2.5rem, 2.8vw, 3rem);
            font-weight: 600;
            color: #1a1a1a;
            margin: 0 0 1rem 0;
            line-height: 1.12;
            letter-spacing: -0.04em;
          }
          .wiz-instructions {
            color: #4b5563;
            font-size: 1.25rem;
            line-height: 1.75;
            margin: 0 0 1.75rem 0;
          }
          .wiz-nav-label {
            font-family: "JetBrains Mono", ui-monospace, monospace;
            font-size: 0.8125rem;
            font-weight: 500;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: #4b5563;
            margin: 0 0 0.75rem 0.15rem;
          }
          section.main div[data-testid="stVerticalBlock"]:has(p.wiz-nav-label),
          section.main div[data-testid="column"]:has(p.wiz-nav-label) {
            background: #f3f3f0 !important;
            border-radius: 0.375rem !important;
            padding: 0.65rem 0.5rem 0.85rem 0.65rem !important;
            border: none !important;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.06) !important;
          }
          section.main div[data-testid="stVerticalBlock"]:has(p.wiz-nav-label) .stButton > button,
          section.main div[data-testid="column"]:has(p.wiz-nav-label) .stButton > button {
            min-height: 3.05rem !important;
            padding: 0.75rem 1.05rem !important;
            border-radius: 0 !important;
            font-size: 1.05rem !important;
            justify-content: flex-start !important;
            text-align: left !important;
            font-family: "Source Serif 4", Georgia, serif !important;
          }
          section.main div[data-testid="stVerticalBlock"]:has(p.wiz-nav-label) .stButton > button[kind="secondary"],
          section.main div[data-testid="column"]:has(p.wiz-nav-label) .stButton > button[kind="secondary"] {
            background: #1a1a1a !important;
            border: 2px solid #1a1a1a !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            font-weight: 600 !important;
            box-shadow: var(--fv-btn-shadow) !important;
            border-radius: 0.375rem !important;
          }
          section.main div[data-testid="stVerticalBlock"]:has(p.wiz-nav-label) .stButton > button[kind="secondary"]:hover,
          section.main div[data-testid="column"]:has(p.wiz-nav-label) .stButton > button[kind="secondary"]:hover {
            background: #333333 !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
          }
          section.main div[data-testid="stVerticalBlock"]:has(p.wiz-nav-label) .stButton > button[kind="primary"],
          section.main div[data-testid="column"]:has(p.wiz-nav-label) .stButton > button[kind="primary"] {
            background: #1a1a1a !important;
            border: 2px solid #1a1a1a !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            font-weight: 600 !important;
            box-shadow: var(--fv-btn-shadow) !important;
            border-radius: 0.375rem !important;
          }
          section.main div[data-testid="stVerticalBlock"]:has(p.wiz-nav-label) .stButton > button[kind="primary"]:hover,
          section.main div[data-testid="column"]:has(p.wiz-nav-label) .stButton > button[kind="primary"]:hover {
            background: #333333 !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
          }
          section.main div[data-testid="stVerticalBlock"]:has(p.wiz-nav-label) .stButton > button[kind="primary"]:active:not(:disabled),
          section.main div[data-testid="column"]:has(p.wiz-nav-label) .stButton > button[kind="primary"]:active:not(:disabled) {
            background: #333333 !important;
            transform: translateY(1px) !important;
            box-shadow: 0 2px 4px -1px rgb(0 0 0 / 0.12) !important;
          }
          div[data-testid="stVerticalBlock"] > div.wiz-footer-bar {
            margin-top: 2.25rem;
            padding-top: 1.5rem;
            border-top: 1px solid #d1d5db;
          }
          section.main .block-container .stButton > button[kind="primary"] {
            background: #1a1a1a !important;
            border: 2px solid #1a1a1a !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            border-radius: 0.375rem !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            letter-spacing: 0.08em !important;
            text-transform: uppercase !important;
            font-family: "JetBrains Mono", ui-monospace, monospace !important;
            box-shadow: var(--fv-btn-shadow) !important;
            transition: background-color 0.15s ease, color 0.15s ease, transform 0.08s ease,
              box-shadow 0.08s ease !important;
          }
          section.main .block-container .stButton > button[kind="primary"]:active:not(:disabled) {
            transform: translateY(1px) !important;
            background: #333333 !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            box-shadow: 0 2px 4px -1px rgb(0 0 0 / 0.12) !important;
          }
          section.main .block-container .stButton > button[kind="primary"]:hover {
            background: #333333 !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
          }
          div[data-testid="stVerticalBlockBorderWrapper"] {
            background: #ffffff !important;
            border-radius: 0.375rem !important;
            border: none !important;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.06) !important;
            padding: 0.55rem 0.75rem !important;
          }
          section.main [data-testid="stMetricLabel"] {
            font-size: 1.05rem !important;
            letter-spacing: 0.02em !important;
          }
          section.main [data-testid="stMetricLabel"],
          section.main [data-testid="stMetricLabel"] * {
            color: #1a1a1a !important;
          }
          section.main div[data-testid="stMetricValue"] {
            font-size: 1.65rem !important;
            font-family: "JetBrains Mono", ui-monospace, monospace !important;
            font-weight: 600 !important;
            color: #059669 !important;
          }
          section.main [data-testid="stRadio"],
          section.main [data-testid="stRadio"] *,
          section.main [data-testid="stRadioGroup"],
          section.main [data-testid="stRadioGroup"] *,
          section.main [data-testid="stCheckbox"],
          section.main [data-testid="stCheckbox"] *,
          section.main [data-testid="stMultiSelect"],
          section.main [data-testid="stMultiSelect"] * {
            color: #1a1a1a !important;
          }
          section.main [data-baseweb="radio"],
          section.main [data-baseweb="radio"] * {
            color: #1a1a1a !important;
          }
          section.main [data-baseweb="checkbox"],
          section.main [data-baseweb="checkbox"] * {
            color: #1a1a1a !important;
          }
          section.main [data-baseweb="button-group"] {
            background: #ffffff !important;
            border-radius: 0.375rem !important;
            padding: 4px !important;
            gap: 4px !important;
            border: 2px solid #1a1a1a !important;
            box-shadow: none !important;
          }
          section.main [data-baseweb="button-group"] button {
            color: #404040 !important;
            -webkit-text-fill-color: #404040 !important;
            background: #ffffff !important;
            border-radius: 0.25rem !important;
            font-weight: 700 !important;
            font-size: 1.25rem !important;
            line-height: 1.35 !important;
            min-height: 5rem !important;
            padding: 0.5rem 0.75rem !important;
            border: 2px solid #1a1a1a !important;
          }
          section.main [data-baseweb="button-group"] button * {
            color: inherit !important;
            -webkit-text-fill-color: inherit !important;
          }
          section.main [data-baseweb="button-group"] button:hover {
            background: #f3f3f0 !important;
            color: #404040 !important;
            -webkit-text-fill-color: #404040 !important;
          }
          section.main [data-baseweb="button-group"] button[kind="segmented_control_active"],
          section.main [data-baseweb="button-group"] button[aria-checked="true"] {
            background: #1a1a1a !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            border: 2px solid #1a1a1a !important;
            font-weight: 700 !important;
            box-shadow: none !important;
          }
          /* Repeat Base Web + segmented overrides after wizard rules (loaded later than global theme). */
          section.main [data-baseweb="base-input"] {
            background-color: #ffffff !important;
            border: 1px solid #d1d5db !important;
            border-radius: 0.375rem !important;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.06) !important;
            transition: background-color 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease !important;
          }
          section.main [data-baseweb="base-input"]:focus-within {
            background-color: #ffffff !important;
            border-color: #059669 !important;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.06),
              0 0 0 3px rgba(5, 150, 105, 0.25) !important;
          }
          section.main [data-baseweb="base-input"] > div {
            background-color: #ffffff !important;
            color: #1a1a1a !important;
            transition: background-color 0.15s ease !important;
          }
          section.main [data-baseweb="base-input"]:focus-within > div {
            background-color: #ffffff !important;
          }
          section.main [data-baseweb="base-input"] input {
            background-color: transparent !important;
            color: #1a1a1a !important;
            -webkit-text-fill-color: #1a1a1a !important;
            border: none !important;
          }
          section.main [data-baseweb="base-input"] input::placeholder {
            color: #4b5563 !important;
            -webkit-text-fill-color: #4b5563 !important;
            opacity: 1 !important;
          }
          section.main [data-baseweb="base-input"] svg {
            fill: #1a1a1a !important;
            color: #1a1a1a !important;
          }
          /* Segmented control — same high-contrast rules as global theme (wizard loads later) */
          section.main button[kind="segmented_control"],
          section.main button[kind="segmented_controlActive"],
          section.main button[data-testid^="stBaseButton-segmented_control"] {
            border-radius: 0.375rem !important;
            box-shadow: none !important;
            font-family: inherit !important;
            min-height: 5rem !important;
            padding: 0.55rem 0.9rem !important;
            font-size: 1.25rem !important;
            line-height: 1.35 !important;
            font-weight: 700 !important;
            white-space: normal !important;
            text-align: center !important;
            border: 2px solid #1a1a1a !important;
            outline: none !important;
          }
          section.main button[kind="segmented_control"],
          section.main button[data-testid^="stBaseButton-segmented_control"]:not([data-testid*="Active"]) {
            background-color: #ffffff !important;
            background: #ffffff !important;
            color: #404040 !important;
            -webkit-text-fill-color: #404040 !important;
            transition: background-color 0.15s ease, color 0.15s ease, transform 0.08s ease !important;
          }
          section.main button[kind="segmented_control"]:hover:not(:disabled),
          section.main button[kind="segmented_control"]:focus-visible:not(:disabled),
          section.main
            button[data-testid^="stBaseButton-segmented_control"]:not([data-testid*="Active"]):hover:not(:disabled),
          section.main
            button[data-testid^="stBaseButton-segmented_control"]:not([data-testid*="Active"]):focus-visible:not(
              :disabled
            ) {
            background-color: #f3f3f0 !important;
            color: #404040 !important;
            -webkit-text-fill-color: #404040 !important;
          }
          section.main button[kind="segmented_controlActive"],
          section.main button[data-testid*="segmented_controlActive"] {
            background-color: #1a1a1a !important;
            background: #1a1a1a !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
          }
          section.main button[kind="segmented_controlActive"] *,
          section.main button[data-testid*="segmented_controlActive"] *,
          section.main button[kind="segmented_controlActive"] p,
          section.main button[kind="segmented_controlActive"] span,
          section.main button[kind="segmented_controlActive"] strong,
          section.main button[data-testid*="segmented_controlActive"] p,
          section.main button[data-testid*="segmented_controlActive"] span,
          section.main button[data-testid*="segmented_controlActive"] strong {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
          }
          section.main button[kind="segmented_control"] *,
          section.main button[data-testid^="stBaseButton-segmented_control"]:not([data-testid*="Active"]) *,
          section.main button[kind="segmented_control"] p,
          section.main button[kind="segmented_control"] span,
          section.main button[kind="segmented_control"] strong,
          section.main
            button[data-testid^="stBaseButton-segmented_control"]:not([data-testid*="Active"]) p,
          section.main
            button[data-testid^="stBaseButton-segmented_control"]:not([data-testid*="Active"]) span,
          section.main
            button[data-testid^="stBaseButton-segmented_control"]:not([data-testid*="Active"]) strong {
            color: #404040 !important;
            -webkit-text-fill-color: #404040 !important;
          }
          section.main button[kind="segmented_control"] a,
          section.main button[kind="segmented_controlActive"] a,
          section.main button[data-testid^="stBaseButton-segmented_control"] a {
            color: inherit !important;
            -webkit-text-fill-color: inherit !important;
            text-decoration: none !important;
          }
          section.main button[kind="segmented_control"] .stMarkdownColoredText,
          section.main
            button[data-testid^="stBaseButton-segmented_control"]:not([data-testid*="Active"])
            .stMarkdownColoredText {
            color: #404040 !important;
            -webkit-text-fill-color: #404040 !important;
          }
          section.main button[kind="segmented_controlActive"] .stMarkdownColoredText,
          section.main button[data-testid*="segmented_controlActive"] .stMarkdownColoredText {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
          }
          section.main button[kind="segmented_controlActive"]:hover:not(:disabled),
          section.main button[kind="segmented_controlActive"]:focus-visible:not(:disabled),
          section.main button[data-testid*="segmented_controlActive"]:hover:not(:disabled),
          section.main button[data-testid*="segmented_controlActive"]:focus-visible:not(:disabled) {
            background-color: #333333 !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            border-color: #1a1a1a !important;
          }
          section.main button[kind="segmented_control"]:focus-visible,
          section.main button[kind="segmented_controlActive"]:focus-visible,
          section.main button[data-testid^="stBaseButton-segmented_control"]:focus-visible {
            outline: 3px solid #1a1a1a !important;
            outline-offset: 2px !important;
          }
          @media (max-width: 768px) {
            section.main [data-testid="stHorizontalBlock"] {
              flex-direction: column !important;
              align-items: stretch !important;
              gap: 1rem !important;
            }
            section.main [data-testid="stHorizontalBlock"] > div[data-testid="column"] {
              width: 100% !important;
              min-width: 0 !important;
              flex: 1 1 auto !important;
            }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _compare_to_benchmark(user_amt: int, baseline: int | None) -> None:
    if baseline is None or user_amt <= 0:
        return
    ratio = user_amt / float(baseline)
    pct = (ratio - 1.0) * 100.0
    if pct > 5:
        st.warning(_i18n.t("cmp_bench_high", pct=pct, baseline=baseline))
    elif pct < -5:
        st.success(_i18n.t("cmp_bench_low", pct=abs(pct), baseline=baseline))
    else:
        st.info(_i18n.t("cmp_bench_near", baseline=baseline))


def _compare_car_to_ceiling(user_amt: int, ceiling: int) -> None:
    """Rough guideline: all-in monthly car costs vs ~15% take-home ceiling."""
    if ceiling <= 0 or user_amt <= 0:
        return
    pct = (user_amt / float(ceiling) - 1.0) * 100.0
    if pct > 5:
        st.warning(_i18n.t("cmp_car_high", pct=pct, ceiling=ceiling))
    elif pct < -5:
        st.success(_i18n.t("cmp_car_low", pct=abs(pct), ceiling=ceiling))
    else:
        st.info(_i18n.t("cmp_car_near", ceiling=ceiling))


def _render_wizard_car_panel(income: float, car_spend_ceiling: float) -> None:
    """Car costs, spend ceiling, depreciation education, lease/finance context."""
    st.metric(
        _i18n.t("car_metric_ceiling"),
        f"${car_spend_ceiling:,.0f}",
        help=_i18n.t("car_metric_ceiling_help"),
    )
    st.caption(_i18n.t("car_ceiling_caption"))

    st.info(_i18n.t("car_edu_block"))

    cars_band = st.radio(
        _i18n.t("car_hh_radio"),
        ["1", "2 or more"],
        horizontal=True,
        key="dash_car_household_cars",
        format_func=_fmt_car_household_band,
    )
    ceil_1 = int(round(car_spend_ceiling))
    if cars_band == "2 or more":
        ceil_2 = int(round(car_spend_ceiling * 2))
        st.warning(_i18n.t("car_warn_two", ceil2=ceil_2, ceil1=ceil_1, inc=income))

    st.markdown(_i18n.t("car_pay_heading"))
    status = st.radio(
        _i18n.t("car_status_radio"),
        ["No car", "Lease", "Finance", "Own outright"],
        horizontal=True,
        key="dash_car_status",
        label_visibility="collapsed",
        format_func=_fmt_car_status,
    )
    if status == "Lease":
        st.markdown(_i18n.t("car_md_lease"))
    elif status == "Finance":
        st.markdown(_i18n.t("car_md_finance"))
    elif status == "Own outright":
        st.markdown(_i18n.t("car_md_own"))
    else:
        st.markdown(_i18n.t("car_md_transit"))

    with st.expander(_i18n.t("car_dep_expander")):
        st.caption(
            _i18n.t(
                "car_dep_caption",
                r3=CAR_DEP_ILLUSTRATIVE_RETENTION_3YR,
                r5=CAR_DEP_ILLUSTRATIVE_RETENTION_5YR,
            )
        )
        ex_price = st.number_input(
            _i18n.t("car_dep_example_price"),
            min_value=5_000,
            max_value=250_000,
            value=38_000,
            step=1_000,
            key="dash_car_dep_example_price",
        )
        v3 = int(round(ex_price * CAR_DEP_ILLUSTRATIVE_RETENTION_3YR))
        v5 = int(round(ex_price * CAR_DEP_ILLUSTRATIVE_RETENTION_5YR))
        dep3 = ex_price - v3
        dep5 = ex_price - v5
        avg_mo_dep3 = dep3 / 36.0
        avg_mo_dep5 = dep5 / 60.0
        st.markdown(
            _i18n.t(
                "car_dep_lines",
                v3=v3,
                v5=v5,
                d3=int(dep3),
                d5=int(dep5),
                a3=avg_mo_dep3,
                a5=avg_mo_dep5,
            )
        )
        st.caption(_i18n.t("car_dep_add_ons"))

    if status == "No car":
        st.markdown("##### " + _i18n.t("car_mob_budget_title"))
        st.caption(_i18n.t("car_mob_budget_cap"))
        t1, t2, t3 = st.columns(3)
        with t1:
            if st.button(_i18n.t("car_chip_transit_75"), key="chip_transit_75"):
                st.session_state.dash_transit_monthly = 75
                st.rerun()
        with t2:
            if st.button(_i18n.t("car_chip_transit_150"), key="chip_transit_150"):
                st.session_state.dash_transit_monthly = 150
                st.rerun()
        with t3:
            if st.button(_i18n.t("car_chip_transit_300"), key="chip_transit_300"):
                st.session_state.dash_transit_monthly = 300
                st.rerun()
        st.number_input(
            _i18n.t("car_transit_inp"),
            min_value=0,
            step=5,
            key="dash_transit_monthly",
            help=_i18n.t("car_transit_help"),
        )
        st.session_state.dash_car_monthly = 0
        transit_m = int(float(st.session_state.get("dash_transit_monthly", 0) or 0))
        if transit_m > 0:
            st.info(_i18n.t("car_transit_info", m=transit_m))
    else:
        st.markdown("##### " + _i18n.t("car_monthly_costs_title"))
        st.caption(_i18n.t("car_monthly_costs_cap"))

        if status == "Lease":
            st.number_input(
                _i18n.t("car_inp_lease"),
                min_value=0,
                step=25,
                key="dash_car_payment_monthly",
            )
        elif status == "Finance":
            st.number_input(
                _i18n.t("car_inp_finance"),
                min_value=0,
                step=25,
                key="dash_car_payment_monthly",
            )
        elif status == "Own outright":
            st.number_input(
                _i18n.t("car_inp_dep"),
                min_value=0,
                step=25,
                key="dash_car_depreciation_monthly",
                help=_i18n.t("car_inp_dep_help"),
            )

        c_ins, c_fuel = st.columns(2)
        with c_ins:
            st.number_input(
                _i18n.t("car_inp_ins"),
                min_value=0,
                step=10,
                key="dash_car_insurance_monthly",
            )
        with c_fuel:
            st.number_input(
                _i18n.t("car_inp_fuel"),
                min_value=0,
                step=25,
                key="dash_car_fuel_monthly",
                help=_i18n.t("car_inp_fuel_help"),
            )
        st.number_input(
            _i18n.t("car_inp_maint"),
            min_value=0,
            step=25,
            key="dash_car_maintenance_monthly",
            help=_i18n.t("car_inp_maint_help"),
        )

        pay = (
            float(st.session_state.get("dash_car_payment_monthly", 0) or 0)
            if status in ("Lease", "Finance")
            else 0.0
        )
        dep = (
            float(st.session_state.get("dash_car_depreciation_monthly", 0) or 0)
            if status == "Own outright"
            else 0.0
        )
        ins_m = float(st.session_state.get("dash_car_insurance_monthly", 0) or 0)
        fuel_m = float(st.session_state.get("dash_car_fuel_monthly", 0) or 0)
        maint_m = float(st.session_state.get("dash_car_maintenance_monthly", 0) or 0)
        total_car = int(round(pay + dep + ins_m + fuel_m + maint_m))
        st.session_state.dash_car_monthly = total_car

        parts: list[str] = []
        if status in ("Lease", "Finance"):
            parts.append(_i18n.t("car_part_payment", v=pay))
        if status == "Own outright":
            parts.append(_i18n.t("car_part_dep", v=dep))
        parts.extend(
            [
                _i18n.t("car_part_ins", v=ins_m),
                _i18n.t("car_part_fuel", v=fuel_m),
                _i18n.t("car_part_maint", v=maint_m),
            ]
        )
        st.caption(" + ".join(parts) + f" → **${total_car:,}/mo**")

        st.metric(_i18n.t("car_total_metric"), f"${total_car:,}")

        with st.expander(_i18n.t("car_bundle_exp")):
            st.caption(_i18n.t("car_bundle_cap"))
            q1, q2, q3 = st.columns(3)
            with q1:
                if st.button(_i18n.t("car_bundle_low"), key="car_bundle_low"):
                    if status == "Own outright":
                        st.session_state.dash_car_depreciation_monthly = 180
                    else:
                        st.session_state.dash_car_payment_monthly = 260
                    st.session_state.dash_car_insurance_monthly = 100
                    st.session_state.dash_car_fuel_monthly = 90
                    st.session_state.dash_car_maintenance_monthly = 55
                    st.rerun()
            with q2:
                if st.button(_i18n.t("car_bundle_mid"), key="car_bundle_mid"):
                    if status == "Own outright":
                        st.session_state.dash_car_depreciation_monthly = 320
                    else:
                        st.session_state.dash_car_payment_monthly = 420
                    st.session_state.dash_car_insurance_monthly = 140
                    st.session_state.dash_car_fuel_monthly = 160
                    st.session_state.dash_car_maintenance_monthly = 85
                    st.rerun()
            with q3:
                if st.button(_i18n.t("car_bundle_high"), key="car_bundle_high"):
                    if status == "Own outright":
                        st.session_state.dash_car_depreciation_monthly = 520
                    else:
                        st.session_state.dash_car_payment_monthly = 680
                    st.session_state.dash_car_insurance_monthly = 190
                    st.session_state.dash_car_fuel_monthly = 220
                    st.session_state.dash_car_maintenance_monthly = 120
                    st.rerun()

        compare_ceil = ceil_1 * (2 if cars_band == "2 or more" else 1)
        if total_car > 0:
            _compare_car_to_ceiling(total_car, compare_ceil)

    _wiz_snap.refresh_session_derived_totals(st.session_state)
    eff_tr = _wiz_snap.effective_transport_monthly(st.session_state)
    st.divider()
    st.metric(
        _i18n.t("car_mobility_pie_metric"),
        f"${eff_tr:,.0f}",
        help=_i18n.t("car_mobility_pie_help"),
    )
    _render_wizard_step_tracker("car")


def _render_wizard_child_panel(family: str) -> None:
    """Common child expense lines — user-filled; no spending ceiling."""
    if "kid" in family.lower() or "parents" in family.lower():
        st.success(_i18n.t("child_has_kids"))
    else:
        st.info(_i18n.t("child_no_kids"))

    st.caption(_i18n.t("child_cap"))

    st.markdown("##### " + _i18n.t("child_title"))
    a, b = st.columns(2)
    with a:
        tui = float(
            st.number_input(
                _i18n.t("child_inp_tuition"),
                min_value=0,
                step=25,
                key="dash_child_tuition_monthly",
                help=_i18n.t("child_inp_tuition_h"),
            )
            or 0
        )
        care = float(
            st.number_input(
                _i18n.t("child_inp_care"),
                min_value=0,
                step=25,
                key="dash_child_childcare_monthly",
                help=_i18n.t("child_inp_care_h"),
            )
            or 0
        )
        ins = float(
            st.number_input(
                _i18n.t("child_inp_ins"),
                min_value=0,
                step=10,
                key="dash_child_insurance_monthly",
                help=_i18n.t("child_inp_ins_h"),
            )
            or 0
        )
    with b:
        act = float(
            st.number_input(
                _i18n.t("child_inp_act"),
                min_value=0,
                step=25,
                key="dash_child_activities_monthly",
                help=_i18n.t("child_inp_act_h"),
            )
            or 0
        )
        ent = float(
            st.number_input(
                _i18n.t("child_inp_ent"),
                min_value=0,
                step=25,
                key="dash_child_entertainment_monthly",
                help=_i18n.t("child_inp_ent_h"),
            )
            or 0
        )
        clo = float(
            st.number_input(
                _i18n.t("child_inp_clo"),
                min_value=0,
                step=25,
                key="dash_child_clothing_monthly",
                help=_i18n.t("child_inp_clo_h"),
            )
            or 0
        )
    oth = float(
        st.number_input(
            _i18n.t("child_inp_other"),
            min_value=0,
            step=25,
            key="dash_child_other_monthly",
            help=_i18n.t("child_inp_other_h"),
        )
        or 0
    )
    tot = int(round(tui + care + ins + act + ent + clo + oth))
    st.session_state.dash_child_monthly = tot

    st.caption(
        _i18n.t(
            "child_sum_cap",
            tui=tui,
            care=care,
            ins=ins,
            act=act,
            ent=ent,
            clo=clo,
            oth=oth,
            tot=tot,
        )
    )
    st.metric(_i18n.t("child_total_metric"), f"${tot:,}")
    _wiz_snap.refresh_session_derived_totals(st.session_state)
    _render_wizard_step_tracker("child")


def _render_wizard_grocery_panel(income: float, family: str) -> None:
    """Groceries at home — US benchmark ideas; user keeps full freedom on the total."""
    # If Child step was never opened (or pins were cleared on Housing), seed the same carry Child would write.
    if st.session_state.get("_wf_pool_after_child_usd") is None:
        lf0 = _wiz_snap.living_five_amounts_usd_monthly(st.session_state)
        inc0 = _wiz_snap.session_take_home_usd_monthly(st.session_state)
        st.session_state["_wf_pool_after_child_meta"] = (
            float(inc0),
            float(lf0[0]),
            float(lf0[1]),
            float(lf0[2]),
        )
        st.session_state["_wf_pool_after_child_usd"] = float(inc0) - float(lf0[0]) - float(lf0[1]) - float(lf0[2])
    fam_disp = _translate_family_option(family)
    ball = GROCERY_USDA_BALLPARK_MONTHLY.get(family, (520, 800))
    lo, hi = ball

    st.info(_i18n.t("groc_info_block", fam=fam_disp, lo=lo, hi=hi))

    with st.expander(_i18n.t("groc_why_spread")):
        st.markdown(_i18n.t("groc_why_body"))

    g10 = int(round(income * 0.10 / 50.0)) * 50
    g12 = int(round(income * 0.12 / 50.0)) * 50
    g15 = int(round(income * 0.15 / 50.0)) * 50
    st.caption(_i18n.t("groc_shortcut_cap"))
    g1, g2, g3 = st.columns(3)
    with g1:
        if st.button(f"${g10:,} · ~10%", key="chip_g_10"):
            st.session_state.dash_grocery = max(0, g10)
            st.rerun()
    with g2:
        if st.button(f"${g12:,} · ~12%", key="chip_g_12"):
            st.session_state.dash_grocery = max(0, g12)
            st.rerun()
    with g3:
        if st.button(f"${g15:,} · ~15%", key="chip_g_15"):
            st.session_state.dash_grocery = max(0, g15)
            st.rerun()
    g_mo = float(
        st.number_input(
            _i18n.t("groc_monthly_inp"),
            min_value=0,
            step=50,
            key="dash_grocery",
            help=_i18n.t("groc_monthly_help"),
        )
        or 0
    )
    st.session_state["_wf_grocery_tracker_spend_usd"] = float(g_mo)
    _wiz_snap.refresh_session_derived_totals(st.session_state)
    _render_wizard_step_tracker("grocery")


def _render_wizard_entertainment_panel(income: float, vibe: str, family: str) -> None:
    """Discretionary fun — merged buckets; no ceiling; many households exceed ~$200/mo."""
    # If Grocery step was never opened (or pins were cleared on Housing), seed the carry Grocery would write.
    if st.session_state.get("_wf_grocery_pool_usd") is None:
        lf0 = _wiz_snap.living_five_amounts_usd_monthly(st.session_state)
        inc0 = _wiz_snap.session_take_home_usd_monthly(st.session_state)
        g0 = float(lf0[3])
        st.session_state["_wf_grocery_pool_meta"] = (
            float(inc0),
            float(lf0[0]),
            float(lf0[1]),
            float(lf0[2]),
            float(g0),
        )
        st.session_state["_wf_grocery_pool_usd"] = (
            float(inc0) - float(lf0[0]) - float(lf0[1]) - float(lf0[2]) - float(g0)
        )
    st.info(_i18n.t("ent_info_block"))
    st.caption(
        _i18n.t(
            "ent_vibe_cap",
            vibe=_translate_vibe_option(vibe),
            family=_translate_family_option(family),
            inc=income,
        )
    )

    st.markdown("##### " + _i18n.t("ent_title"))
    c1, c2 = st.columns(2)
    with c1:
        st.number_input(
            _i18n.t("ent_inp_out"),
            min_value=0,
            step=25,
            key="dash_ent_out_monthly",
            help=_i18n.t("ent_inp_out_h"),
        )
        st.number_input(
            _i18n.t("ent_inp_media"),
            min_value=0,
            step=10,
            key="dash_ent_media_monthly",
            help=_i18n.t("ent_inp_media_h"),
        )
        st.number_input(
            _i18n.t("ent_inp_trips"),
            min_value=0,
            step=50,
            key="dash_ent_trips_monthly",
            help=_i18n.t("ent_inp_trips_h"),
        )
    with c2:
        st.number_input(
            _i18n.t("ent_inp_play"),
            min_value=0,
            step=25,
            key="dash_ent_play_monthly",
            help=_i18n.t("ent_inp_play_h"),
        )
        st.number_input(
            _i18n.t("ent_inp_social"),
            min_value=0,
            step=25,
            key="dash_ent_social_monthly",
            help=_i18n.t("ent_inp_social_h"),
        )
    st.number_input(
        _i18n.t("ent_inp_other"),
        min_value=0,
        step=25,
        key="dash_ent_other_monthly",
        help=_i18n.t("ent_inp_other_h"),
    )

    out = float(st.session_state.get("dash_ent_out_monthly", 0) or 0)
    med = float(st.session_state.get("dash_ent_media_monthly", 0) or 0)
    trp = float(st.session_state.get("dash_ent_trips_monthly", 0) or 0)
    ply = float(st.session_state.get("dash_ent_play_monthly", 0) or 0)
    soc = float(st.session_state.get("dash_ent_social_monthly", 0) or 0)
    ot = float(st.session_state.get("dash_ent_other_monthly", 0) or 0)
    tot = int(round(out + med + trp + ply + soc + ot))
    st.session_state.dash_ent = tot

    st.caption(
        _i18n.t(
            "ent_sum_cap",
            out=out,
            med=med,
            trp=trp,
            ply=ply,
            soc=soc,
            ot=ot,
            tot=tot,
        )
    )
    st.metric(_i18n.t("ent_total_metric"), f"${tot:,}")
    st.session_state["_wf_entertainment_tracker_spend_usd"] = float(tot)
    _wiz_snap.refresh_session_derived_totals(st.session_state)
    _render_wizard_step_tracker("entertainment")


def _render_wizard_housing_panel(family: str) -> None:
    """Two sub-pages: Rent (ZIP + family band vs ACS gross rent) and Own (ZIP vs owner cost)."""
    st.session_state.pop("_wf_car_pool_usd", None)
    st.session_state.pop("_wf_car_pool_meta", None)
    st.session_state.pop("_wf_pool_after_child_usd", None)
    st.session_state.pop("_wf_pool_after_child_meta", None)
    st.session_state.pop("_wf_grocery_pool_meta", None)
    st.session_state.pop("_wf_grocery_pool_usd", None)
    st.session_state.pop("_wf_grocery_tracker_spend_usd", None)
    st.session_state.pop("_wf_entertainment_tracker_spend_usd", None)
    st.session_state.pop("_wf_entertainment_pool_meta", None)
    st.session_state.pop("_wf_entertainment_pool_usd", None)
    for _nk in (
        "_wf_next_pie_income_snapshot",
        "_wf_next_pie_housing_usd",
        "_wf_next_pie_car_usd",
        "_wf_next_pie_child_usd",
        "_wf_next_pie_grocery_usd",
        "_wf_next_pie_fun_usd",
    ):
        st.session_state.pop(_nk, None)
    _sync_dash_mortgage_cache()
    prof_short, prof_detail, mult = _family_housing_benchmark_profile(family)

    st.markdown(
        _i18n.t(
            "house_from_q",
            family=_translate_family_option(family),
            short=prof_short,
            detail=prof_detail,
        )
    )
    zip_combined = st.text_input(
        _i18n.t("house_zip_label"),
        placeholder=_i18n.t("house_zip_ph"),
        max_chars=10,
        key="dash_housing_zip",
    )
    z5 = _parse_zip5(zip_combined)

    median_r = _acs_median_gross_rent_zcta(z5) if z5 else None
    bench_r = int(round(median_r * mult)) if median_r else None
    name_z, oc_med, hv_med = _acs_zcta_owner_snapshot(z5) if z5 else (None, None, None)
    bench_o = int(round(oc_med * mult)) if oc_med else None
    bench_home = int(round(hv_med * mult)) if hv_med else None
    if z5:
        st.session_state.dash_housing_benchmark_rent_mo = float(bench_r or 0)
        st.session_state.dash_housing_benchmark_owner_mo = float(bench_o or 0)
    else:
        st.session_state.dash_housing_benchmark_rent_mo = 0.0
        st.session_state.dash_housing_benchmark_owner_mo = 0.0

    # Implementer notes (not shown in UI): ZIP is shared by Rent/Own. When rent and owned
    # all-in are both still $0, worksheet & pie take housing from the first control’s side.
    # The second control is which worksheet is binding (Rent vs Own); it’s persisted on Next
    # and drives tracker, pie, and exports.
    st.segmented_control(
        _i18n.t("house_ws_side_lbl"),
        options=["rent", "own"],
        format_func=_fmt_housing_ws_side,
        key="dash_housing_worksheet_side",
        help=_i18n.t("house_ws_side_help"),
        label_visibility="visible",
        width="stretch",
    )

    st.segmented_control(
        _i18n.t("house_binding_lbl"),
        options=["rent", "own"],
        format_func=_fmt_housing_ui_tab,
        key="dash_housing_ui_subtab",
        label_visibility="visible",
        width="stretch",
    )

    if str(st.session_state.get("dash_housing_ui_subtab", "rent") or "rent").lower() == "rent":
        st.markdown("##### " + _i18n.t("house_renting_title"))
        st.caption(_i18n.t("house_renting_caption"))

        if z5:
            if median_r:
                st.metric(
                    _i18n.t("house_bench_rent"),
                    f"${bench_r:,}/mo",
                    help=_i18n.t(
                        "house_bench_rent_help",
                        yr=ACS_YEAR,
                        med=int(median_r),
                        mult=mult,
                    ),
                )
            else:
                st.warning(_i18n.t("house_warn_no_rent"))
        else:
            st.info(_i18n.t("house_info_zip"))

        st.number_input(
            _i18n.t("house_your_rent"),
            min_value=0,
            step=50,
            key="dash_rent",
            help=_i18n.t("house_your_rent_help"),
        )
        user_r = int(float(st.session_state.get("dash_rent", 0) or 0))
        _compare_to_benchmark(user_r, bench_r)

        _wiz_snap.refresh_session_derived_totals(st.session_state)
        eff_rent_tab = _wiz_snap.housing_worksheet_rent_subview_monthly(st.session_state)
        st.divider()
        st.metric(
            _i18n.t("house_metric_rent_tab"),
            f"${eff_rent_tab:,.0f}",
            help=_i18n.t("house_metric_rent_tab_help"),
        )

    else:
        st.markdown("##### " + _i18n.t("house_owning_title"))
        beds = _family_suggested_bedrooms(family)
        st.caption(_i18n.t("house_own_beds_caption", beds=beds))

        if not st.session_state.dash_own_mortgage_step:
            st.markdown("###### " + _i18n.t("house_own_step1"))
            if not z5:
                st.info(_i18n.t("house_own_zip_info"))
            else:
                if name_z:
                    st.markdown(_i18n.t("house_census_lbl", name=name_z))
                st.markdown(
                    _i18n.t("house_band_mult", short=prof_short, mult=mult),
                )
                if bench_o and oc_med:
                    st.metric(
                        _i18n.t("house_own_cost_metric"),
                        f"${bench_o:,}/mo",
                        help=_i18n.t(
                            "house_own_cost_help",
                            yr=ACS_YEAR,
                            med=int(oc_med),
                            mult=mult,
                        ),
                    )
                else:
                    st.warning(_i18n.t("house_warn_no_b25105"))
                if bench_home and hv_med:
                    st.metric(
                        _i18n.t("house_home_val_metric"),
                        f"${bench_home:,}",
                        help=_i18n.t(
                            "house_home_val_help",
                            yr=ACS_YEAR,
                            med=int(hv_med),
                            mult=mult,
                        ),
                    )
                else:
                    st.info(_i18n.t("house_info_no_b25077"))

            st.radio(
                _i18n.t("house_median_confirm_lbl"),
                [
                    _wiz_snap.OWN_MEDIAN_CONFIRM_YES,
                    _wiz_snap.OWN_MEDIAN_CONFIRM_UNSURE,
                ],
                key="dash_own_median_confirm",
                format_func=_fmt_own_median_choice,
            )
            if st.session_state.get("dash_own_median_confirm") == _wiz_snap.OWN_MEDIAN_CONFIRM_UNSURE:
                with st.container(border=True):
                    st.markdown(_i18n.t("house_unsure_title"))
                    st.markdown(_i18n.t("house_unsure_body"))
            if st.button(_i18n.t("house_btn_verify"), type="primary", key="dash_own_verify"):
                st.session_state.dash_own_mortgage_step = True
                st.session_state.dash_housing_worksheet_side = "own"
                st.session_state.dash_housing_ui_subtab = "own"
                st.session_state.dash_housing_committed_subtab = "own"
                if st.session_state.get("dash_own_median_confirm") == _wiz_snap.OWN_MEDIAN_CONFIRM_UNSURE:
                    st.session_state.dash_own_came_from_unsure = True
                else:
                    st.session_state.dash_own_came_from_unsure = False
                if bench_home:
                    st.session_state.dash_own_home_price = bench_home
                elif "dash_own_home_price" not in st.session_state:
                    st.session_state.dash_own_home_price = 450_000
                dr = _fred_latest_mortgage30_annual_pct()
                if dr is not None:
                    st.session_state.dash_own_rate_pct = round(float(dr), 3)
                st.rerun()

        else:
            st.markdown("###### " + _i18n.t("house_own_step2"))
            if st.session_state.get("dash_own_came_from_unsure"):
                st.info(_i18n.t("house_from_unsure_info"))
            fred_r = _fred_latest_mortgage30_annual_pct()
            default_rate = round(float(fred_r), 3) if fred_r is not None else 6.5
            if "dash_own_rate_pct" not in st.session_state:
                st.session_state.dash_own_rate_pct = default_rate
            if "dash_own_home_price" not in st.session_state:
                st.session_state.dash_own_home_price = int(bench_home or 450_000)
            if "dash_own_down_pct" not in st.session_state:
                st.session_state.dash_own_down_pct = 20
            if "dash_own_term" not in st.session_state:
                st.session_state.dash_own_term = 30

            if fred_r is not None:
                st.caption(_i18n.t("house_fred_ok", rate=default_rate))
            else:
                st.caption(_i18n.t("house_fred_fail", rate=default_rate))
            if st.button(_i18n.t("house_back_median"), key="dash_own_back_phase"):
                st.session_state.dash_own_mortgage_step = False
                st.session_state.dash_housing_model_own_monthly = 0.0
                st.rerun()

            st.number_input(
                _i18n.t("house_inp_home_price"),
                min_value=50_000,
                max_value=6_000_000,
                step=5_000,
                key="dash_own_home_price",
            )
            st.slider(_i18n.t("house_slider_down"), 3, 50, key="dash_own_down_pct")
            st.number_input(
                _i18n.t("house_inp_rate"),
                min_value=0.25,
                max_value=20.0,
                step=0.125,
                format="%.3f",
                key="dash_own_rate_pct",
            )
            st.selectbox(_i18n.t("house_sel_term"), [30, 25, 20, 15], key="dash_own_term")
            st.selectbox(
                _i18n.t("house_prop_tax_lbl"),
                options=["apartment", "house"],
                format_func=_fmt_own_property_kind,
                key="dash_own_property_kind",
            )

            hp = float(st.session_state.dash_own_home_price)
            down_pct = float(st.session_state.dash_own_down_pct)
            rate_pct = float(st.session_state.dash_own_rate_pct)
            term_years = int(st.session_state.dash_own_term)
            loan = hp * (1.0 - down_pct / 100.0)
            pi = _monthly_principal_interest(loan, rate_pct / 100.0, term_years)
            util_m = pi * 0.10
            ins_m = pi * 0.05
            kind = str(st.session_state.get("dash_own_property_kind", "house"))
            tax_m = (
                DASH_OWN_PROPERTY_TAX_APARTMENT_MO
                if kind == "apartment"
                else DASH_OWN_PROPERTY_TAX_HOUSE_MO
            )
            model_total = int(round(pi + util_m + ins_m + tax_m))
            st.session_state.dash_housing_model_own_monthly = float(model_total)

            st.markdown(
                _i18n.t(
                    "house_modeled_breakdown",
                    apt=int(DASH_OWN_PROPERTY_TAX_APARTMENT_MO),
                    house=int(DASH_OWN_PROPERTY_TAX_HOUSE_MO),
                )
            )
            b1, b2, b3, b4 = st.columns(4)
            with b1:
                st.metric(_i18n.t("house_m_pi"), f"${pi:,.0f}")
            with b2:
                st.metric(_i18n.t("house_m_util"), f"${util_m:,.0f}")
            with b3:
                st.metric(_i18n.t("house_m_ins"), f"${ins_m:,.0f}")
            with b4:
                st.metric(
                    _i18n.t("house_m_tax"),
                    f"${tax_m:,.0f}",
                    help=_i18n.t("house_m_tax_help"),
                )
            st.metric(_i18n.t("house_m_total_model"), f"${model_total:,}")
            st.caption(_i18n.t("house_model_disclaimer"))

            if "dash_mortgage" not in st.session_state:
                cm = float(st.session_state.get("dash_mortgage_cached", 0) or 0)
                if cm > 0:
                    st.session_state.dash_mortgage = float(cm)
            st.number_input(
                _i18n.t("house_actual_allin"),
                min_value=0,
                step=50,
                key="dash_mortgage",
                on_change=_bump_mortgage_edit_flag,
            )
            _sync_dash_mortgage_cache()
            if st.session_state.get("dash_own_came_from_unsure"):
                st.caption(_i18n.t("house_unsure_worksheet_cap"))
            user_o = int(float(st.session_state.get("dash_mortgage", 0) or 0))
            _compare_user_to_own_model(user_o, model_total)

        _wiz_snap.refresh_session_derived_totals(st.session_state)
        eff_own_tab = _wiz_snap.housing_worksheet_own_subview_monthly(st.session_state)
        st.divider()
        st.metric(
            _i18n.t("house_metric_own_tab"),
            f"${eff_own_tab:,.0f}",
            help=_i18n.t("house_metric_own_tab_help"),
        )

    _wiz_snap.refresh_session_derived_totals(st.session_state)
    ui_tab = str(st.session_state.get("dash_housing_ui_subtab", "rent") or "rent").lower()
    st.session_state.dash_housing_committed_subtab = ui_tab if ui_tab in ("rent", "own") else "rent"
    _sync_dash_mortgage_cache()
    _render_wizard_step_tracker("housing")


def _wizard_module_cashflow_surplus() -> tuple[float, float, float, dict[str, float]]:
    """
    Returns (final_savings, take_home_income, total_allocated_ex_final, full_allocation_breakdown).
    ``total_allocated_ex_final`` = take-home minus final savings (all other mapped lines).
    """
    return _wiz_snap.compute_wizard_surplus(st.session_state)


def _render_wizard_step_tracker(slug: str) -> None:
    """Take-home pool through the waterfall: left before each row → that row’s $ → left after (same math as pie)."""
    row_idxs = _wiz_snap.WIZARD_SLUG_TO_WATERFALL_TRACKER_ROWS.get(slug)
    if not row_idxs:
        return
    keys = list(_wiz_snap.TAKEHOME_ALLOCATION_PIE_KEYS)
    labels = tuple(_wfl_short_label(i) for i in range(8))
    living5 = _wiz_snap.living_five_amounts_usd_monthly(st.session_state)
    inc = _wiz_snap.session_take_home_usd_monthly(st.session_state)
    alloc = _wiz_snap.compute_takehome_allocation(st.session_state, _living_five=living5)

    def _triple_for_row(row_i: int) -> tuple[float, float, float]:
        if row_i < 5:
            spent_prior = sum(living5[j] for j in range(row_i))
            step_spend = float(living5[row_i])
            left_before = inc - spent_prior
            left_after = left_before - step_spend
            return left_before, step_spend, left_after
        spent_prior = sum(living5) + sum(float(alloc[keys[j]]) for j in range(5, row_i))
        left_before = inc - spent_prior
        step_spend = float(alloc[keys[row_i]])
        left_after = left_before - step_spend
        return left_before, step_spend, left_after

    with st.container(border=True):
        st.markdown("##### " + _i18n.t("trk_title"))
        # Order: housing → car → child → groceries → fun → savings; each row carries balance from prior.
        for k, row_i in enumerate(row_idxs):
            title = labels[row_i]
            left_before, step_spend, left_after = _triple_for_row(row_i)
            # Child: carry from Car pin (same pattern as Car row saving its pin below).
            # Grocery: carry from Child pin ``_wf_pool_after_child_*`` — match **inc + housing** only so a flaky
            # second ``living_five`` read does not drop car/child from the pool; car+child are in the pinned USD value.
            if slug == "child" and row_i == 2:
                inc_i, h_i, c_i = st.session_state.get("_wf_car_pool_meta", (None, None, None))
                if (
                    inc_i is not None
                    and h_i is not None
                    and c_i is not None
                    and _wiz_snap._income_pin_matches_saved(float(inc_i), float(inc))
                    and _wiz_snap._housing_pin_matches_saved(float(h_i), float(living5[0]))
                ):
                    left_before = float(inc_i) - float(h_i) - float(c_i)
                else:
                    left_before = float(inc) - float(living5[0]) - float(living5[1])
                step_spend = float(living5[2])
                left_after = left_before - step_spend
                # Anchor pool after Child for the Grocery step (take-home − Housing − Car − Child).
                st.session_state["_wf_pool_after_child_meta"] = (
                    float(inc),
                    float(living5[0]),
                    float(living5[1]),
                    float(living5[2]),
                )
                st.session_state["_wf_pool_after_child_usd"] = float(left_after)
            if slug == "grocery" and row_i == 3:
                # Take-home left (after Child) = carry from Child step (``_wf_pool_after_child_usd``).
                # Spending this step = same $ as the grocery ``number_input`` on this page (not a second read).
                # Left after = left_before − spending (strict waterfall).
                #
                # Only require **income + housing** to match the pin — do **not** gate on ``living5[2]`` (or car).
                # A second ``living_five`` pass in this run can mis-read car/child after the grocery widget updates;
                # that used to invalidate the pin and fall back to a pre–car/child-looking pool.
                meta_ch = st.session_state.get("_wf_pool_after_child_meta")
                pool_after_child = st.session_state.get("_wf_pool_after_child_usd")
                if meta_ch is not None and pool_after_child is not None:
                    inc_i, h_i, _c_i, _ch_i = meta_ch
                    if _wiz_snap._income_pin_matches_saved(float(inc_i), float(inc)) and _wiz_snap._housing_pin_matches_saved(
                        float(h_i), float(living5[0])
                    ):
                        left_before = float(pool_after_child)
                    else:
                        left_before = float(inc) - float(living5[0]) - float(living5[1]) - float(living5[2])
                else:
                    left_before = float(inc) - float(living5[0]) - float(living5[1]) - float(living5[2])
                step_spend = float(
                    st.session_state.get("_wf_grocery_tracker_spend_usd", st.session_state.get("dash_grocery", 0) or 0)
                )
                left_after = left_before - step_spend
                st.session_state["_wf_grocery_pool_meta"] = (
                    float(inc),
                    float(living5[0]),
                    float(living5[1]),
                    float(living5[2]),
                    float(step_spend),
                )
                st.session_state["_wf_grocery_pool_usd"] = float(left_after)
            if slug == "entertainment" and row_i == 4:
                # Take-home left (after Groceries) = carry from Grocery step (``_wf_grocery_pool_usd``).
                # Spending this step = same $ as **Total estimated monthly entertainment & discretionary fun** (``tot``).
                # Only require **income + housing** to match the pin — same flaky-``living_five`` issue as on Grocery.
                meta_g = st.session_state.get("_wf_grocery_pool_meta")
                pool_after_grocery = st.session_state.get("_wf_grocery_pool_usd")
                if meta_g is not None and pool_after_grocery is not None:
                    inc_i, h_i = float(meta_g[0]), float(meta_g[1])
                    if _wiz_snap._income_pin_matches_saved(inc_i, float(inc)) and _wiz_snap._housing_pin_matches_saved(
                        h_i, float(living5[0])
                    ):
                        left_before = float(pool_after_grocery)
                    else:
                        left_before = float(inc) - float(sum(living5))
                else:
                    left_before = float(inc) - float(sum(living5))
                step_spend = float(
                    st.session_state.get("_wf_entertainment_tracker_spend_usd", st.session_state.get("dash_ent", 0) or 0)
                )
                left_after = left_before - step_spend
                st.session_state["_wf_entertainment_pool_meta"] = (
                    float(inc),
                    float(living5[0]),
                    float(living5[1]),
                    float(living5[2]),
                    float(living5[3]),
                    float(step_spend),
                )
                st.session_state["_wf_entertainment_pool_usd"] = float(left_after)
            if slug == "car" and row_i == 1:
                st.session_state["_wf_car_pool_meta"] = (float(inc), float(living5[0]), float(living5[1]))
                st.session_state["_wf_car_pool_usd"] = float(left_after)
            spend_help = _i18n.t("trk_spend_help_default")
            if slug == "grocery" and row_i == 3:
                spend_help = _i18n.t("trk_spend_help_grocery")
            if slug == "entertainment" and row_i == 4:
                spend_help = _i18n.t("trk_spend_help_ent")
            if slug == "housing" and row_i == 0:
                spend_help = _i18n.t("trk_spend_help_housing")
            st.markdown(_i18n.t("trk_step_header", title=title))
            c1, c2, c3 = st.columns(3)
            with c1:
                if row_i == 0:
                    m1_label = _i18n.t("trk_m1_before", title=title)
                    m1_help = _i18n.t("trk_m1_help_first")
                else:
                    prev_t = labels[row_i - 1]
                    m1_label = _i18n.t("trk_m1_after", prev=prev_t)
                    m1_help = _i18n.t("trk_m1_help_carry", prev=prev_t)
                st.metric(
                    m1_label,
                    f"${left_before:,.0f}",
                    help=m1_help,
                )
            with c2:
                st.metric(
                    _i18n.t("trk_m2_spend", title=title),
                    f"${step_spend:,.0f}",
                    help=spend_help,
                )
            with c3:
                st.metric(
                    _i18n.t("trk_m3_left", title=title),
                    f"${left_after:,.0f}",
                    help=_i18n.t("trk_m3_help", title=title),
                )
            if k < len(row_idxs) - 1:
                st.divider()

        keys_all = keys
        row_sum = sum(float(alloc[kk]) for kk in keys_all)
        final_cushion = float(alloc[keys_all[-1]])
        if slug == "chat":
            st.caption(
                _i18n.t(
                    "trk_footer_chat",
                    cushion=final_cushion,
                    rowsum=row_sum,
                    inc=inc,
                )
            )


def _pie_prefer_ledger_file_default() -> bool:
    """Env: ``WISE_SPENDING_PIE_FROM_LEDGER_FILE=1|true|yes|on`` → default the dashboard checkbox to on."""
    return os.environ.get("WISE_SPENDING_PIE_FROM_LEDGER_FILE", "").strip().lower() in ("1", "true", "yes", "on")


def _render_wizard_spending_pie() -> None:
    """Pie + table: driven by ``build_waterfall_for_pie`` (same order as wizard: Housing → … → Invest rows)."""
    if "dash_pie_prefer_ledger_file" not in st.session_state:
        st.session_state.dash_pie_prefer_ledger_file = _pie_prefer_ledger_file_default()
    prefer_file = st.checkbox(
        _i18n.t("pie_checkbox_ledger"),
        key="dash_pie_prefer_ledger_file",
        help=_i18n.t("pie_checkbox_ledger_help"),
    )
    _wiz_snap.refresh_session_derived_totals(st.session_state)
    wf = _wiz_snap.build_waterfall_for_pie(st.session_state, prefer_ledger_file=prefer_file)
    if prefer_file and wf.get("pie_data_source") != "ledger_file":
        st.warning(_i18n.t("pie_warn_ledger_invalid"))
    elif prefer_file and wf.get("pie_data_source") == "ledger_file":
        p = _wiz_snap.waterfall_pie_ledger_path()
        ts = wf.get("ledger_updated_at_utc") or "—"
        st.info(_i18n.t("pie_info_ledger_ok", path=p, ts=ts))
    st.session_state["waterfall_for_pie"] = wf
    inc_tr = float(wf["monthly_take_home_usd"])
    lines = wf["lines"]
    true_vals = [float(L["usd_monthly"]) for L in lines]
    drift0 = inc_tr - sum(true_vals)
    if abs(drift0) > 1e-6 and inc_tr > 0:
        true_vals[-1] += drift0
        lines[-1]["usd_monthly"] = round(true_vals[-1], 2)

    ledger_disk = _wiz_snap.load_waterfall_pie_ledger_from_disk() if _wiz_snap.disk_cache_enabled() else None
    if ledger_disk is not None:
        lj_inc, lj_vals = _wiz_snap.takehome_amounts_from_ledger_dict(ledger_disk)
        if abs(lj_inc - inc_tr) <= max(2.0, 0.001 * max(abs(lj_inc), abs(inc_tr), 1.0)) and len(lj_vals) == len(
            true_vals
        ):
            true_vals = lj_vals
            inc_tr = float(lj_inc)
            for i, tv in enumerate(true_vals):
                lines[i]["usd_monthly"] = round(float(tv), 2)
    zh_inc, zh_vals = inc_tr, [*true_vals]
    _lp = str(_wiz_snap.waterfall_pie_ledger_path())
    pie_json_note = (
        _i18n.t("pie_ledger_note_disk_on", path=_lp)
        if _wiz_snap.disk_cache_enabled()
        else _i18n.t("pie_ledger_note_disk_off")
    )

    ssum = sum(true_vals)
    final_s = true_vals[-1]
    pct_take_home = [(float(tv) / inc_tr * 100.0) if inc_tr > 1e-6 else 0.0 for tv in true_vals]
    _ck = _i18n.t("pie_col_category")
    _pk = _i18n.t("pie_col_pct_th")
    _uk = _i18n.t("pie_col_usd_mo")
    rows = [
        {
            _ck: _wfl_short_label(i),
            _pk: round(pct_take_home[i], 1),
            _uk: true_vals[i],
        }
        for i in range(len(lines))
    ]

    st.markdown("##### " + _i18n.t("pie_title_split"))
    if inc_tr < 1:
        st.info(_i18n.t("pie_set_takehome"))
        return

    pie_lines_md = _i18n.t("pie_breakdown_title") + "\n\n" + "\n".join(
        _i18n.t(
            "pie_breakdown_line",
            n=i + 1,
            label=_i18n.t(f"pie_row_{i}"),
            usd=float(zh_vals[i]),
            pct=float(pct_take_home[i]),
        )
        for i in range(8)
    )
    st.markdown(pie_lines_md)
    st.caption(pie_json_note)

    st.caption(_i18n.t("pie_caption_sum_line", ssum=ssum, inc=inc_tr))

    if final_s < -1e-2:
        st.warning(_i18n.t("pie_warn_over_budget", gap=-final_s))
        st.dataframe(rows, use_container_width=True, hide_index=True)
        return

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.patches as mpatches
        import matplotlib.pyplot as plt
    except ImportError:
        st.warning(_i18n.t("pie_warn_matplotlib"))
        st.dataframe(rows, use_container_width=True, hide_index=True)
        return

    _n_slices = len(lines)
    _emerald_mono = ["#064e3b", "#065f46", "#047857", "#059669", "#10b981", "#34d399", "#6ee7b7", "#a7f3d0"]
    colors = [_emerald_mono[min(i, len(_emerald_mono) - 1)] for i in range(_n_slices)]
    legend_handles = [
        mpatches.Patch(
            facecolor=colors[i],
            edgecolor="#1a1a1a",
            linewidth=0.5,
            label=f"{_wfl_short_label(i)}: {pct_take_home[i]:.1f}% · ${true_vals[i]:,.0f}/mo",
        )
        for i in range(len(lines))
    ]
    idx = {"i": 0}
    min_show_pct = 2.0

    def _autopct(_pct_mpl: float) -> str:
        i = idx["i"]
        idx["i"] += 1
        tv = true_vals[i]
        if tv <= 1e-9:
            return ""
        pct_inc = (tv / inc_tr * 100.0) if inc_tr > 1e-6 else 0.0
        if pct_inc < min_show_pct:
            return ""
        return f"{pct_inc:.0f}%\n${tv:,.0f}"

    _chart_bg = "#ffffff"
    fig, ax = plt.subplots(figsize=(4.15, 4.15), dpi=132)
    fig.patch.set_facecolor(_chart_bg)
    ax.set_facecolor(_chart_bg)
    wedges, _texts, autotexts = ax.pie(
        true_vals,
        labels=None,
        autopct=_autopct,
        startangle=112,
        colors=colors,
        wedgeprops={
            "width": 0.48,
            "edgecolor": "#1a1a1a",
            "linewidth": 0.65,
            "antialiased": True,
        },
        textprops={"fontsize": 11.5, "fontfamily": "serif"},
        radius=1.0,
        pctdistance=0.79,
    )
    ax.axis("equal")
    for w, at in zip(wedges, autotexts):
        if not at.get_text().strip():
            continue
        rgba = w.get_facecolor()
        lum = 0.299 * float(rgba[0]) + 0.587 * float(rgba[1]) + 0.114 * float(rgba[2])
        at.set_color("#ffffff" if lum < 0.45 else "#000000")
        at.set_fontweight("semibold")
        at.set_fontsize(7.35)
    leg = ax.legend(
        handles=legend_handles,
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        fontsize=7.35,
        frameon=True,
        fancybox=False,
        framealpha=1.0,
        edgecolor="#1a1a1a",
        facecolor="#ffffff",
        title=_i18n.t("pie_legend_title"),
        title_fontsize=7.5,
        labelspacing=0.55,
        borderaxespad=0.65,
    )
    leg.get_title().set_color("#000000")
    leg.get_title().set_fontweight("600")
    ax.set_title(
        _i18n.t("pie_chart_title", inc=inc_tr),
        fontsize=10.75,
        pad=10,
        color="#000000",
        fontweight="600",
    )
    fig.subplots_adjust(left=0.02, right=0.72, top=0.9, bottom=0.04)
    st.pyplot(fig, clear_figure=True, use_container_width=False)
    st.dataframe(rows, use_container_width=True, hide_index=True)


def _seed_wizard_entertainment_pool_after_fun_if_missing(ss) -> None:
    """If user skipped **Fun**, seed the same pin the entertainment tracker would write (left after Fun)."""
    if ss.get("_wf_entertainment_pool_usd") is not None:
        return
    lf0 = _wiz_snap.living_five_amounts_usd_monthly(ss)
    inc0 = _wiz_snap.session_take_home_usd_monthly(ss)
    e0 = float(lf0[4])
    ss["_wf_entertainment_pool_meta"] = (
        float(inc0),
        float(lf0[0]),
        float(lf0[1]),
        float(lf0[2]),
        float(lf0[3]),
        float(e0),
    )
    ss["_wf_entertainment_pool_usd"] = (
        float(inc0) - float(lf0[0]) - float(lf0[1]) - float(lf0[2]) - float(lf0[3]) - float(e0)
    )


def _render_wizard_invest_panel() -> None:
    """Cashflow recap, emergency-fund prompts, 401(k) match education, hypothetical invest %."""
    _seed_wizard_entertainment_pool_after_fun_if_missing(st.session_state)
    surplus_pie, inc_tr, _out_tr_legacy, bd = _wizard_module_cashflow_surplus()
    s_after_fun = float(_wiz_snap.savings_before_investment_usd_monthly(st.session_state))
    allocated_show = float(inc_tr) - s_after_fun

    st.markdown("##### " + _i18n.t("inv_section_snapshot"))
    st.caption(_i18n.t("inv_snapshot_caption"))
    ff, ff_warnings = _wiz_snap.build_funnel_finance_state_from_wizard_session(st.session_state)
    for msg in ff_warnings:
        st.warning(msg)
    with st.expander(_i18n.t("inv_expander_funnel")):
        st.caption(_i18n.t("inv_funnel_caption"))
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(_i18n.t("inv_metric_sbi"), f"${ff.saving_before_investing:,.0f}/mo")
        with c2:
            st.metric(_i18n.t("inv_metric_inv_applied"), f"${ff.investing_applied():,.0f}/mo")
        with c3:
            st.metric(_i18n.t("inv_metric_sai"), f"${ff.saving_after_investing:,.0f}/mo")
        st.caption(_i18n.t("inv_funnel_slider_caption", inv=ff.investing))
    if float(st.session_state.get("dash_rent", 0) or 0) > 0 and _wiz_snap.owner_all_in_monthly_typed(
        st.session_state
    ) > 0:
        st.caption(_i18n.t("inv_caption_rent_mortgage"))
    keys_wf = list(_wiz_snap.TAKEHOME_ALLOCATION_PIE_KEYS)
    with st.expander(_i18n.t("inv_expander_math")):
        for i, k in enumerate(keys_wf):
            st.markdown(
                _i18n.t(
                    "inv_line_item",
                    label=_translate_alloc_row_display_index(i),
                    amt=float(bd[k]),
                )
            )
        st.markdown(
            _i18n.t("inv_sum_lines", s=sum(float(v) for v in bd.values())),
        )
        st.markdown(_i18n.t("inv_takehome_match", inc=inc_tr))

    if inc_tr > 0 and allocated_show < 1e-6:
        st.info(_i18n.t("inv_info_mostly_zero"))
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric(_i18n.t("inv_metric_takehome_q"), f"${inc_tr:,.0f}/mo")
    with col_b:
        st.metric(
            _i18n.t("inv_metric_allocated"),
            f"${allocated_show:,.0f}/mo",
            help=_i18n.t("inv_metric_allocated_help"),
        )
    st.metric(
        _i18n.t("inv_metric_final"),
        f"${s_after_fun:,.0f}/mo",
        help=_i18n.t("inv_metric_final_help"),
    )

    if allocated_show > 1e-6 and s_after_fun < -1e-6:
        st.warning(_i18n.t("inv_warn_deficit_living"))
    elif allocated_show > 1e-6 and surplus_pie < -1e-6 and s_after_fun >= -1e-6:
        st.warning(_i18n.t("inv_warn_deficit_invest"))
    elif s_after_fun > 1e-6:
        st.success(_i18n.t("invest_congrats", s=s_after_fun))

    st.markdown("##### " + _i18n.t("inv_emergency_title"))
    st.caption(_i18n.t("inv_emergency_caption"))
    mo = st.slider(
        _i18n.t("inv_ef_months"),
        min_value=3,
        max_value=6,
        key="dash_ef_target_months",
        help=_i18n.t("inv_ef_months_help"),
    )
    ef_goal = float(mo) * inc_tr
    st.number_input(
        _i18n.t("inv_ef_current"),
        min_value=0.0,
        step=500.0,
        key="dash_ef_current_balance",
        help=_i18n.t("inv_ef_current_help"),
    )
    cur_ef = float(st.session_state.get("dash_ef_current_balance", 0) or 0)
    gap = max(0.0, ef_goal - cur_ef)
    st.metric(
        _i18n.t("inv_ef_target_metric", mo=mo),
        f"${ef_goal:,.0f}",
    )
    st.metric(_i18n.t("inv_ef_gap"), f"${gap:,.0f}")
    st.number_input(
        _i18n.t("inv_ef_monthly_save"),
        min_value=0.0,
        step=50.0,
        key="dash_ef_monthly_save",
    )
    mo_save = float(st.session_state.get("dash_ef_monthly_save", 0) or 0)
    if gap > 0 and mo_save > 0:
        approx_mo = int(round(gap / mo_save)) if mo_save > 0 else 0
        st.caption(
            _i18n.t(
                "inv_ef_ballpark",
                mo_save=mo_save,
                gap=gap,
                approx=approx_mo,
            )
        )

    st.markdown("##### " + _i18n.t("inv_401k_title"))
    st.info(_i18n.t("inv_401k_info"))
    opts_401k = [
        "Not sure — need to check",
        "No / probably under the match",
        "Yes — I’m at or above full match",
        "No employer plan / N/A",
    ]
    st.radio(
        _i18n.t("inv_401k_radio_lbl"),
        opts_401k,
        key="dash_401k_match_status",
        format_func=_fmt_401k_choice,
    )
    st.caption(_i18n.t("inv_401k_caption_hr"))

    st.warning(_i18n.t("inv_not_advice"))
    st.slider(
        _i18n.t("inv_slider_pct"),
        0,
        40,
        key="dash_invest_pct",
        help=_i18n.t("inv_slider_help"),
    )
    s_bi = float(ff.saving_before_investing)
    post_em_bd = s_bi - float(bd[keys_wf[5]])
    inv_pct_i = int(st.session_state.get("dash_invest_pct", 0) or 0)
    inv_pct_i = max(0, min(40, inv_pct_i))
    invest_base = max(0.0, post_em_bd)
    hyp_bd = invest_base * inv_pct_i / 100.0
    final_bd = float(bd[keys_wf[7]])
    st.caption(
        _i18n.t(
            "inv_waterfall_check",
            sbi=s_bi,
            post_em=post_em_bd,
            pct=inv_pct_i,
            hyp=hyp_bd,
            final=final_bd,
        )
    )


def _refresh_wizard_snapshot() -> dict:
    """Merge all wizard `dash_*` inputs into session + disk + RAG plaintext (refreshed each dashboard load)."""
    snap = _wiz_snap.collect_wizard_snapshot(st.session_state)
    st.session_state["wizard_snapshot"] = snap
    comp = snap.get("computed")
    if isinstance(comp, dict) and isinstance(comp.get("waterfall_for_pie"), dict):
        st.session_state["waterfall_for_pie"] = comp["waterfall_for_pie"]
    wf_ledger = _wiz_snap.build_waterfall_pie_ledger(st.session_state)
    st.session_state["wizard_rag_plaintext"] = _wiz_snap.snapshot_to_rag_plaintext(
        snap,
        waterfall_ledger=wf_ledger,
    )
    try:
        _wiz_snap.persist_snapshot(snap)
    except OSError:
        pass
    _wiz_snap.persist_user_inputs_to_disk(st.session_state)
    _wiz_snap.persist_llm_advisor_context(st.session_state)
    return snap


_LLM_API_CONTEXT_CHAR_CAP = 56_000
_LLM_CHAT_HISTORY_CAP = 28  # user + assistant pairs max (messages sliced)


def _compact_llm_context_for_api(payload: dict) -> str:
    # Order: small + authoritative waterfall first; large wizard_snapshot last so truncation keeps ledger.
    body = {
        "llm_quick_reference": payload.get("llm_quick_reference"),
        "waterfall_pie_ledger": payload.get("waterfall_pie_ledger"),
        "cashflow_breakdown_usd_monthly": payload.get("cashflow_breakdown_usd_monthly"),
        "wizard_snapshot": payload.get("wizard_snapshot"),
    }
    s = json.dumps(body, ensure_ascii=False, separators=(",", ":"))
    if len(s) > _LLM_API_CONTEXT_CHAR_CAP:
        return s[:_LLM_API_CONTEXT_CHAR_CAP] + "\n...(truncated for API size)"
    return s


def _openai_compatible_chat(
    *,
    api_key: str,
    model: str,
    base_url: str,
    system_content: str,
    messages: list[dict],
) -> str:
    """POST to `/v1/chat/completions` (OpenAI or compatible gateway)."""
    root = (base_url or "").strip().rstrip("/")
    if not root:
        root = "https://api.openai.com"
    url = f"{root}/v1/chat/completions"
    tail = messages[-_LLM_CHAT_HISTORY_CAP:]
    conv: list[dict[str, str]] = []
    for m in tail:
        role = m.get("role")
        if role not in ("user", "assistant"):
            continue
        content = (m.get("content") or "").strip()
        if not content:
            continue
        conv.append({"role": role, "content": content})
    outbound: list[dict[str, str]] = [{"role": "system", "content": system_content}]
    outbound.extend(conv)
    body = json.dumps(
        {"model": model.strip(), "messages": outbound, "temperature": 0.42},
        ensure_ascii=False,
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key.strip()}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw_txt = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {err_body[:2500]}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(getattr(e, "reason", str(e)) or str(e)) from e
    raw = json.loads(raw_txt)
    err = raw.get("error")
    if err:
        raise RuntimeError(str(err))
    choices = raw.get("choices") or []
    if not choices:
        raise RuntimeError(_i18n.t("api_empty_choices"))
    msg = choices[0].get("message") or {}
    return (msg.get("content") or "").strip()


def _render_wizard_chat_panel(income: float, family: str, vibe: str) -> None:
    _render_wizard_spending_pie()
    _wiz_snap.refresh_session_derived_totals(st.session_state)
    _render_wizard_step_tracker("chat")
    st.markdown("---")
    st.markdown(_i18n.t("chat_title"))
    if _wiz_snap.disk_cache_enabled():
        st.caption(_i18n.t("chat_caption_disk_on"))
    else:
        st.caption(_i18n.t("chat_caption_disk_off"))

    col_llm, col_tip = st.columns([0.36, 0.64], gap="medium")
    with col_llm:
        st.text_input(
            _i18n.t("chat_api_key_label"),
            type="password",
            key="llm_openai_api_key",
            help=_i18n.t("chat_api_key_help"),
        )
        st.text_input(_i18n.t("chat_model_label"), key="llm_model")
        if not (str(st.session_state.get("llm_openai_api_key") or "").strip()):
            st.warning(_i18n.t("chat_missing_openai_key"))
        if st.button(_i18n.t("chat_clear_button"), key="btn_clear_advisor_chat", type="secondary"):
            st.session_state.advisor_messages = []
            st.rerun()

    with col_tip:
        st.info(_i18n.t("chat_info_box"))

    try:
        chat_wrap = st.container(height=520, border=True)
    except TypeError:
        chat_wrap = st.container(border=True)
    with chat_wrap:
        st.caption(_i18n.t("chat_area_caption"))
        for msg in st.session_state.advisor_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if prompt := st.chat_input(_i18n.t("chat_input_placeholder")):
        st.session_state.advisor_messages.append({"role": "user", "content": prompt})
        api_key = (st.session_state.get("llm_openai_api_key") or "").strip()
        model = (st.session_state.get("llm_model") or "gpt-4o-mini").strip() or "gpt-4o-mini"
        base_url = (st.session_state.get("llm_base_url") or "").strip()
        payload = _wiz_snap.build_llm_advisor_context_payload(st.session_state)
        st.session_state["wizard_rag_plaintext"] = _wiz_snap.snapshot_to_rag_plaintext(
            payload["wizard_snapshot"],
            waterfall_ledger=payload["waterfall_pie_ledger"],
        )
        rag_ctx = (st.session_state.get("wizard_rag_plaintext") or "").strip()
        ctx_compact = _compact_llm_context_for_api(payload)
        system_message = (
            f"{payload['system_instruction']}\n\n"
            f"USER_FINANCIAL_CONTEXT (JSON):\n{ctx_compact}"
        )
        if api_key:
            with st.spinner(_i18n.t("chat_spinner")):
                try:
                    reply = _openai_compatible_chat(
                        api_key=api_key,
                        model=model,
                        base_url=base_url,
                        system_content=system_message,
                        messages=st.session_state.advisor_messages,
                    )
                except RuntimeError as e:
                    reply = _i18n.t("chat_error_reply", err=str(e))
        else:
            demo = _demo_advisor_reply(
                prompt,
                income,
                family,
                vibe,
                wizard_context=rag_ctx or None,
            )
            reply = _i18n.t("chat_demo_no_key") + demo
        st.session_state.advisor_messages.append({"role": "assistant", "content": reply})
        _wiz_snap.persist_user_inputs_to_disk(st.session_state)
        st.rerun()


def _demo_advisor_reply(
    user_text: str,
    income: float,
    family: str,
    vibe: str,
    wizard_context: str | None = None,
) -> str:
    low = user_text.lower()
    extra = ""
    if "invest" in low or "stock" in low or "401" in low:
        extra = _i18n.t("chat_demo_extra_invest")
    if "debt" in low or "loan" in low:
        extra += _i18n.t("chat_demo_extra_debt")
    fam_d = _translate_family_option(family)
    vibe_d = _translate_vibe_option(vibe)
    ctx = ""
    if wizard_context and wizard_context.strip():
        cap = 12_000
        body = wizard_context.strip()[:cap]
        if len(wizard_context.strip()) > cap:
            body += _i18n.t("chat_demo_trunc")
        ctx = _i18n.t("chat_demo_ctx_open") + body + _i18n.t("chat_demo_ctx_close")
    return (
        _i18n.t("chat_demo_header")
        + "\n\n"
        + _i18n.t("chat_demo_baseline", income=income, family=fam_d, vibe=vibe_d)
        + "\n\n"
        + _i18n.t("chat_demo_modules")
        + extra
        + ctx
    )


def _render_post_onboarding_dashboard() -> None:
    income = float(st.session_state.monthly_take_home)
    family = st.session_state.family
    vibe = st.session_state.spending_vibe
    base = BASE_LIVING_COST_BY_FAMILY[family]
    estimated_living = round(base * 1.0, 2)
    housing_spend_ceiling = round(income * HOUSING_SPEND_CEILING_FRAC, 2)
    car_spend_ceiling = round(income * CAR_SPEND_CEILING_FRAC, 2)
    ds = int(st.session_state.dashboard_step)
    ds = max(0, min(ds, N_WIZARD_STEPS - 1))
    st.session_state.dashboard_step = ds

    _refresh_wizard_snapshot()

    _inject_wizard_css()
    h1, h2 = st.columns([1, 0.22])
    with h1:
        st.title(_i18n.t("onboard_main_title"))
    with h2:
        _render_language_selector()
    st.caption(_i18n.t("dash_subtitle"))
    if not _wiz_snap.disk_cache_enabled():
        st.caption(_i18n.t("dash_disk_cache_off"))

    st.markdown("##### " + _i18n.t("dash_baseline_header"))
    m1, m2, m3, m4, m5 = st.columns([1.1, 1.1, 1.1, 1.1, 0.75])
    with m1:
        st.metric(_i18n.t("dash_metric_takehome_mo"), f"${income:,.0f}")
    with m2:
        st.metric(
            _i18n.t("dash_metric_housing_ceiling"),
            f"${housing_spend_ceiling:,.0f}",
            help=_i18n.t("dash_metric_housing_ceiling_help"),
        )
    with m3:
        st.metric(_i18n.t("dash_metric_est_living"), f"${estimated_living:,.0f}")
    with m4:
        st.metric(_i18n.t("dash_metric_household_lbl"), _translate_family_option(family))
    with m5:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(_i18n.t("dash_start_over"), type="secondary", key="dash_start_over"):
            _wiz_snap.clear_wizard_disk_caches()
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            _init_session_state()
            st.rerun()
    cap_ts = "—"
    if st.session_state.last_saved_record:
        cap_ts = str(st.session_state.last_saved_record.get("captured_at_utc", "—"))
    st.caption(
        _i18n.t("dash_style_saved", vibe=_translate_vibe_option(vibe), ts=cap_ts),
    )
    if st.session_state.last_saved_record:
        with st.expander(_i18n.t("dash_expander_raw_json")):
            st.json(st.session_state.last_saved_record)

    snap = st.session_state.get("wizard_snapshot") or {}
    with st.expander(_i18n.t("dash_expander_export"), expanded=False):
        if _wiz_snap.disk_cache_enabled():
            st.caption(_i18n.t("dash_export_caption_disk_on"))
        else:
            st.caption(_i18n.t("dash_export_caption_disk_off"))
        st.caption(_i18n.t("dash_rag_size_caption", ts=snap.get("updated_at_utc", "—")))
        j_bytes = json.dumps(snap, indent=2, ensure_ascii=False).encode("utf-8")
        d1, d2, d3 = st.columns(3)
        with d1:
            st.download_button(
                _i18n.t("dash_dl_json"),
                data=j_bytes,
                file_name="wise_spending_wizard_snapshot.json",
                mime="application/json",
                key="dl_wiz_json",
                use_container_width=True,
            )
        with d2:
            docx_b: bytes | None
            try:
                docx_b = _wiz_snap.build_docx_bytes(snap)
            except Exception as ex:  # noqa: BLE001 — missing dep or build error
                docx_b = None
                st.caption(_i18n.t("dash_dl_docx_err", ex=ex))
            if docx_b is not None:
                st.download_button(
                    _i18n.t("dash_dl_docx"),
                    data=docx_b,
                    file_name="wise_spending_wizard_snapshot.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key="dl_wiz_docx",
                    use_container_width=True,
                )
        with d3:
            pdf_b: bytes | None
            try:
                pdf_b = _wiz_snap.build_pdf_bytes(snap)
            except Exception as ex:  # noqa: BLE001
                pdf_b = None
                st.caption(_i18n.t("dash_dl_pdf_err", ex=ex))
            if pdf_b is not None:
                st.download_button(
                    _i18n.t("dash_dl_pdf"),
                    data=pdf_b,
                    file_name="wise_spending_wizard_snapshot.pdf",
                    mime="application/pdf",
                    key="dl_wiz_pdf",
                    use_container_width=True,
                )

    st.markdown("---")
    nav_col, main_col = st.columns([0.28, 0.72], gap="large")

    with nav_col:
        st.markdown(
            f'<p class="wiz-nav-label">{_i18n.t("wiz_build_analyze")}</p>',
            unsafe_allow_html=True,
        )
        for i, (_slug, _tk, _dk, nk) in enumerate(WIZARD_MODULES):
            short = _i18n.t(nk)
            label = f"{i + 1}. {short}"
            if st.button(
                label,
                key=f"wiz_nav_{i}",
                type="primary" if i == ds else "secondary",
                use_container_width=True,
            ):
                st.session_state.dashboard_step = i
                st.rerun()

    _slug, title_key, instr_key, _nk = WIZARD_MODULES[ds]
    card_title = _i18n.t(title_key)
    card_instr = _i18n.t(instr_key)
    with main_col:
        with st.container(border=True):
            st.markdown(
                f'<p class="wiz-step-meta">{_i18n.t("wiz_step_counter", cur=ds + 1, total=N_WIZARD_STEPS)}</p>',
                unsafe_allow_html=True,
            )
            st.markdown(f'<h2 class="wiz-title">{card_title}</h2>', unsafe_allow_html=True)
            st.markdown(f'<p class="wiz-instructions">{card_instr}</p>', unsafe_allow_html=True)

            if _slug == "housing":
                _render_wizard_housing_panel(family)

            elif _slug == "car":
                _render_wizard_car_panel(income, car_spend_ceiling)

            elif _slug == "child":
                _render_wizard_child_panel(family)

            elif _slug == "grocery":
                _render_wizard_grocery_panel(income, family)

            elif _slug == "entertainment":
                _render_wizard_entertainment_panel(income, vibe, family)

            elif _slug == "invest":
                _render_wizard_invest_panel()

            elif _slug == "chat":
                _render_wizard_chat_panel(income, family, vibe)

        fb1, fb2, fb3 = st.columns([1, 2, 1])
        with fb1:
            if st.button(_i18n.t("wiz_back"), key="wiz_back", disabled=ds == 0):
                st.session_state.dashboard_step = ds - 1
                st.rerun()
        with fb2:
            if ds >= N_WIZARD_STEPS - 1:
                st.caption(_i18n.t("wiz_last_caption"))
        with fb3:
            last = ds >= N_WIZARD_STEPS - 1
            if st.button(
                _i18n.t("wiz_next_last") if last else _i18n.t("wiz_next"),
                type="primary",
                key="wiz_next",
                disabled=last,
            ):
                _wiz_snap.capture_wizard_step_spending_at_next(st.session_state, _slug)
                st.session_state.dashboard_step = ds + 1
                st.rerun()

    # Save again after widgets render so closing the tab / idle drop still captures the latest numbers.
    if _wiz_snap.disk_cache_enabled():
        try:
            _wiz_snap.refresh_session_derived_totals(st.session_state)
            _wiz_snap.persist_user_inputs_to_disk(st.session_state)
            _wiz_snap.persist_llm_advisor_context(st.session_state)
        except OSError:
            pass


def main() -> None:
    st.set_page_config(
        page_title=f"{APP_TITLE} · Onboarding",
        page_icon="◆",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    _init_session_state()
    _inject_emerald_theme()

    if st.session_state.onboarding_complete:
        _render_post_onboarding_dashboard()
        return

    step = int(st.session_state.onboarding_step)

    if step == 0:
        _inject_intro_fullbleed_css()
        _render_intro_text_hero()
        return

    oh1, oh2 = st.columns([1, 0.22])
    with oh1:
        st.title(_i18n.t("onboard_main_title"))
    with oh2:
        _render_language_selector()
    _inject_onboarding_stage_css()
    st.markdown(
        f'<p class="onboard-baseline-lead">{_i18n.t("onboard_main_caption")}</p>',
        unsafe_allow_html=True,
    )
    _progress_bar()
    st.divider()
    _render_questionnaire_privacy_banner()

    if step == 1:
        st.markdown(_i18n.t("onboard_step1_title"))
        income = st.slider(
            _i18n.t("onboard_slider_income"),
            min_value=1_000,
            max_value=50_000,
            value=int(st.session_state.monthly_take_home),
            step=1_000,
            format="$%d",
            help=_i18n.t("onboard_slider_income_help"),
            label_visibility="collapsed",
        )
        if st.button(_i18n.t("onboard_step1_btn"), type="primary", key="btn_step1"):
            st.session_state.monthly_take_home = float(income)
            st.session_state.onboarding_step = 2
            _wiz_snap.persist_user_inputs_to_disk(st.session_state)
            st.rerun()

    elif step == 2:
        st.markdown(_i18n.t("onboard_step2_title"))
        fam_idx = FAMILY_OPTIONS.index(st.session_state.family) if st.session_state.family in FAMILY_OPTIONS else 0
        family = st.selectbox(
            _i18n.t("lbl_household"),
            FAMILY_OPTIONS,
            index=fam_idx,
            key="sel_family",
            format_func=_translate_family_option,
        )

        if st.button(_i18n.t("onboard_step2_btn"), type="primary", key="btn_step2"):
            st.session_state.family = family
            st.session_state.onboarding_step = 3
            _wiz_snap.persist_user_inputs_to_disk(st.session_state)
            st.rerun()

    elif step == 3:
        st.markdown(_i18n.t("onboard_step3_title"))
        vibe_idx = VIBE_OPTIONS.index(st.session_state.spending_vibe) if st.session_state.spending_vibe in VIBE_OPTIONS else 1
        vibe = st.selectbox(
            _i18n.t("lbl_spending_style"),
            VIBE_OPTIONS,
            index=vibe_idx,
            key="sel_vibe",
            format_func=_translate_vibe_option,
        )

        if st.button(_i18n.t("onboard_step3_btn"), type="primary", key="btn_step3"):
            st.session_state.spending_vibe = vibe

            income = float(st.session_state.monthly_take_home)
            family = st.session_state.family
            base = BASE_LIVING_COST_BY_FAMILY[family]
            estimated_living = round(base * 1.0, 2)
            housing_spend_ceiling = round(income * HOUSING_SPEND_CEILING_FRAC, 2)
            car_spend_ceiling = round(income * CAR_SPEND_CEILING_FRAC, 2)

            record = {
                "schema": "futurevalue.onboarding.v1",
                "captured_at_utc": datetime.now(timezone.utc).isoformat(),
                "monthly_household_take_home": income,
                "family": family,
                "spending_vibe": vibe,
                "derived": {
                    "housing_spend_ceiling_30pct_take_home": housing_spend_ceiling,
                    "safe_spending_limit_30pct": housing_spend_ceiling,  # legacy alias
                    "car_spend_ceiling_15pct_take_home": car_spend_ceiling,
                    "estimated_base_living_cost_us_average": estimated_living,
                },
            }

            _append_jsonl(record)
            st.session_state.last_saved_record = record
            st.session_state.dashboard_step = 0
            st.session_state.onboarding_complete = True
            _wiz_snap.persist_user_inputs_to_disk(st.session_state)
            st.rerun()


if __name__ == "__main__":
    main()
