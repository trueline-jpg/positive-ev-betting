# app.py  — TruLine Betting (full site + EV engine)
from __future__ import annotations

import os
import math
import json
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# ---- Your EV math helpers (already in repo) ----
from ev_utils import (
    american_to_decimal,
    implied_prob_from_american,
    edge_decimal,
    kelly_fraction,
    estimate_true_prob_from_ref,
)

load_dotenv()

# =========================
# ---- THEME / SETTINGS ---
# =========================
PAGE_TITLE = "TruLine Betting"
BRAND_NAME = "TruLine Betting"
LOGO_PATH = "assets/logo.png"  # keep your logo here
PRIMARY_CTA = "Try 7 Days Free"
ACCENT = "#14B8A6"  # teal accent
DARK_BG = "#0b1220"  # deep navy/black background

# -- page icon: if you export a small 32x32 png to assets/favicon.png, uncomment:
# PAGE_ICON = "assets/favicon.png"
# st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")

st.set_page_config(page_title=PAGE_TITLE, layout="wide")

# A tiny helper so we can jump around sections like a website
def set_view(view: str):
    st.session_state["view"] = view

if "view" not in st.session_state:
    st.session_state["view"] = "home"

# =======================================================
# ---- GLOBAL CSS (nav, hero, cards, tables, footer) ----
# =======================================================
st.markdown(
    f"""
<style>
/* Reset some defaults */
html, body, .stApp {{ background: {DARK_BG}; color: #e5e7eb; }}
a, a:visited {{ color: {ACCENT}; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}

/* Make Streamlit wider & hide default header/footer gaps */
.block-container {{ padding-top: 0rem; padding-bottom: 3rem; }}

.navbar {{
  position: sticky; top: 0; z-index: 1000;
  display: flex; align-items: center; gap: 16px;
  background: rgba(7,12,25,0.85); backdrop-filter: blur(8px);
  border-bottom: 1px solid rgba(255,255,255,0.06);
  padding: 12px 20px; border-radius: 0 0 10px 10px;
}}
.nav-title {{ display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 18px; }}
.nav-links {{ margin-left: auto; display: flex; align-items: center; gap: 18px; }}
.nav-link {{ opacity: 0.85; cursor: pointer; }}
.nav-btn {{
  background: {ACCENT}; color: #0b1220; font-weight: 700;
  padding: 8px 14px; border-radius: 8px; border: none;
}}
.nav-btn:hover {{ filter: brightness(0.95); }}

.hero {{
  display: grid; grid-template-columns: 1.2fr 1fr; gap: 32px;
  align-items: center; padding: 28px 8px 8px 8px;
}}
.kicker {{ color: #93c5fd; letter-spacing: .15em; text-transform: uppercase; font-weight: 700; font-size: 12px; }}
h1.hero-title {{ font-size: 42px; line-height: 1.1; margin: 6px 0 12px 0; font-weight: 800; }}
.hero-sub {{ color: #a3a3a3; font-size: 16px; }}
.cta-row {{ display:flex; gap: 10px; margin-top: 14px; }}
.cta-primary {{ background: {ACCENT}; color:#0b1220; font-weight:800; padding:10px 14px; border-radius:10px; border:none; }}
.cta-secondary {{ background: transparent; color: #e5e7eb; border:1px solid rgba(255,255,255,.1); padding:10px 14px; border-radius:10px; }}

.section {{ padding: 28px 8px; }}
.section h2 {{ font-size: 28px; margin-bottom: 14px; }}
.card-grid {{ display:grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }}
.card {{
  background: rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06);
  padding: 16px; border-radius: 14px;
}}
.card h4 {{ margin: 0 0 8px 0; }}

.disclaimer {{ color:#9ca3af; font-size: 12px; }}

footer {{
  border-top: 1px solid rgba(255,255,255,.08);
  margin-top: 28px; padding-top: 18px; color: #9ca3af;
}}
/* Dataframe polish */
[data-testid="stTable"], [data-testid="stDataFrame"] {{ border-radius: 10px; overflow:hidden; }}
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# -------- NAVBAR --------
# =========================
def navbar():
    with st.container():
        cols = st.columns([1, 6, 4, 2])
        with cols[0]:
            # Logo + brand
            exists = os.path.exists(LOGO_PATH)
            if exists:
                st.image(LOGO_PATH, width=36)
            st.markdown(f"<div class='nav-title'>{BRAND_NAME}</div>", unsafe_allow_html=True)

        with cols[2]:
            # Links
            c1, c2, c3 = st.columns([1, 1, 1])
            if c1.button("Tools", key="nav_tools", use_container_width=True):
                set_view("tools")
            if c2.button("Pricing", key="nav_pricing", use_container_width=True):
                set_view("pricing")
            if c3.button("Resources", key="nav_resources", use_container_width=True):
                set_view("resources")

        with cols[3]:
            colA, colB = st.columns([1, 1])
            if colA.button("Login", key="nav_login"):
                set_view("login")
            if colB.button(PRIMARY_CTA, key="nav_cta"):
                set_view("login")

navbar()

# ======================================================
# ----------- AUTH (simple, same as before) -----------
# ======================================================
def do_login_sidebar():
    st.sidebar.header("Login")
    u = st.sidebar.text_input("Email or Username")
    p = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Sign in"):
        # simple secrets-based auth
        try:
            if u in st.secrets["users"] and st.secrets["users"][u] == p:
                st.session_state["authenticated"] = True
                st.session_state["user"] = u
                st.sidebar.success(f"Welcome, {u}!")
                set_view("tools")
            else:
                st.sidebar.error("Invalid credentials")
        except Exception:
            st.sidebar.warning("Configure users in `.streamlit/secrets.toml`.")

if st.session_state.get("view") != "login":
    # keep login handy on sidebar even on other pages
    do_login_sidebar()

# ======================================================
# ----------- DATA / PROVIDER CONFIG -------------------
# ======================================================
provider_name = os.getenv("PROVIDER", "csv")
regions = os.getenv("REGIONS", "us")
markets_env = os.getenv("MARKETS", "h2h,spreads,totals")
default_books = [b.strip() for b in os.getenv(
    "BOOKS",
    "DraftKings,FanDuel,BetMGM,PointsBet,Caesars,Barstool,BetRivers,Unibet,Bet365,Pinnacle,BetUS,Fanatics,Underdog,Prizepicks,Fliff"
).split(",") if b.strip()]
ref_book = os.getenv("REF_BOOK", "Pinnacle")
fallback_margin = float(os.getenv("REF_FALLBACK_MARGIN", "0.03"))
initial_kelly_cap = float(os.getenv("KELLY_FRACTION", "0.25"))
min_edge_default = float(os.getenv("MIN_EDGE", "0.02"))
refresh_seconds_default = int(os.getenv("REFRESH_SECONDS", "60"))

def load_data_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

def fetch_odds() -> pd.DataFrame:
    if provider_name.lower() == "csv":
        return load_data_csv("sample_data/sample_odds.csv")
    # Live provider (unchanged structure)
    try:
        from providers.oddsapi_provider import OddsAPIProvider
    except Exception as e:
        st.error(f"Provider import failed: {e}")
        return pd.DataFrame()

    api_key = os.getenv("ODDS_API_KEY", "")
    if not api_key:
        st.error("Missing ODDS_API_KEY in environment. Set PROVIDER=csv to use sample data.")
        return pd.DataFrame()

    provider = OddsAPIProvider(api_key, regions=regions, markets="h2h", odds_format="american")
    sports = provider.get_sports()
    options = [s.get("key") for s in sports]
    chosen = st.sidebar.selectbox("Sport (live from API)", options=options)
    data = provider.get_odds(chosen)

    rows = []
    for ev in data:
        sport_key = ev.get("sport_key")
        commence = ev.get("commence_time")
        home = ev.get("home_team")
        away = ev.get("away_team")
        for bk in ev.get("bookmakers", []):
            book = bk.get("title")
            for mk in bk.get("markets", []):
                if mk.get("key") != "h2h":
                    continue
                outcomes = mk.get("outcomes", [])
                # 2- or 3-way
                for oc in outcomes:
                    name = oc.get("name")
                    side = "home" if name == home else ("away" if name == away else name)
                    price_am = oc.get("price")
                    opp_price = None
                    for oc2 in outcomes:
                        if oc2 is not oc:
                            opp_price = oc2.get("price")
                            break
                    rows.append(
                        {
                            "sport_key": sport_key,
                            "commence_time": commence,
                            "home_team": home,
                            "away_team": away,
                            "book": book,
                            "market": "h2h",
                            "side": side,
                            "price_american": price_am,
                            "opp_price_american": opp_price,
                            "ref_price_american": None,
                        }
                    )
    return pd.DataFrame(rows)

# ----------------- robust number parsing -----------------
def to_american_float(x) -> float | None:
    if x is None:
        return None
    if isinstance(x, (int, float)) and not pd.isna(x):
        return float(x)
    s = str(x).strip()
    if s == "" or s.lower() in {"nan", "none"}:
        return None
    # allow formats like "+110", "-105", "opp:110"
    if ":" in s:
        s = s.split(":")[-1].strip()
    try:
        return float(s.replace("+", ""))
    except Exception:
        try:
            return float(s)
        except Exception:
            return None

# =============== EV TABLE =================
def compute_table(df: pd.DataFrame, kelly_cap: float, bankroll: float) -> pd.DataFrame:
    out = []
    for _, row in df.iterrows():
        price = to_american_float(row.get("price_american"))
        opp_price_val = to_american_float(row.get("opp_price_american"))
        ref_price_val = to_american_float(row.get("ref_price_american"))

        if price is None:
            continue

        offer_decimal = american_to_decimal(price)
        side_implied = 1.0 / offer_decimal

        # If we don't have reference price, infer a fair prob by de-vigging pair;
        # if opp is missing, fall back to complement.
        opp_prob = (1.0 / american_to_decimal(opp_price_val)) if opp_price_val is not None else (1.0 - side_implied)
        true_p = estimate_true_prob_from_ref(ref_price_val, fallback_margin, side_implied, opp_prob)

        ev = edge_decimal(offer_decimal, true_p)
        full_kelly = kelly_fraction(true_p, offer_decimal)
        stake_reco = max(0.0, min(full_kelly * kelly_cap * bankroll, bankroll))

        out.append(
            {
                "sport_key": row.get("sport_key"),
                "commence_time": row.get("commence_time"),
                "home_team": row.get("home_team"),
                "away_team": row.get("away_team"),
                "book": row.get("book"),
                "market": row.get("market"),
                "side": row.get("side"),
                "price_american": price,
                "opp_price_american": opp_price_val,
                "ref_price_american": ref_price_val,
                "offer_decimal": round(offer_decimal, 4),
                "true_prob_est": round(true_p, 4),
                "fair_decimal": round(1.0 / true_p, 4) if true_p > 0 else None,
                "edge_pct": round(ev, 4),
                "kelly_full": round(full_kelly, 4),
                "stake_reco_$": round(stake_reco, 2),
            }
        )
    return pd.DataFrame(out)

# =========================
# --------- PAGES ---------
# =========================
def page_home():
    # HERO
    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.markdown("<div class='kicker'>POSITIVE EV</div>", unsafe_allow_html=True)
        st.markdown("<h1 class='hero-title'>We scan the lines. You place the bets.</h1>", unsafe_allow_html=True)
        st.markdown(
            "<div class='hero-sub'>Find rare, high-edge opportunities using fair odds, "
            "vig removal, and disciplined bankroll controls.</div>",
            unsafe_allow_html=True,
        )
        colA, colB = st.columns([1, 1])
        if colA.button(PRIMARY_CTA, type="primary", use_container_width=True):
            set_view("login")
        if colB.button("How it works", use_container_width=True):
            set_view("resources")

    with c2:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, caption="TruLine logo", use_container_width=True)

    st.markdown("")

    # QUICK EXPLAINER
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.markdown("### How does Positive EV Betting work?")
    st.write(
        "- **Compute fair odds**: Remove the bookmaker's vig using the market pair.\n"
        "- **Estimate edge**: Compare your offer price vs. fair price (expected value per $1).\n"
        "- **Stake sizing**: Use capped Kelly to size your bets within bankroll limits.\n"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # CTAs like OddsJam
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    cfa, cfb, cfc = st.columns(3)
    cfa.markdown("#### 7-Day FREE Trial")
    cfa.write("Explore EV opportunities, filters, and CSV export.")
    if cfa.button("Start my trial"):
        set_view("login")

    cfb.markdown("#### Live Data & Alerts")
    cfb.write("(Optional) Connect sportsbooks and get fresh odds.")
    cfb.button("See Tools", on_click=set_view, args=("tools",))

    cfc.markdown("#### Learn the System")
    cfc.write("Short guide on edge, fair odds, and bankroll management.")
    cfc.button("Read the guide", on_click=set_view, args=("resources",))
    st.markdown("</div>", unsafe_allow_html=True)

    _ev_preview_table()

def page_tools():
    st.markdown("### 📊 Positive EV Finder")

    # ----- Sidebar controls -----
    st.sidebar.header("⚙️ Settings")
    min_edge = st.sidebar.slider("Min Edge (EV%)", 0.0, 0.10, min_edge_default, 0.005, format="%.3f")
    bankroll = st.sidebar.number_input("Bankroll ($)", min_value=10.0, value=1000.0, step=50.0)
    kelly_cap = st.sidebar.slider("Kelly Cap (fraction of full Kelly)", 0.0, 1.0, initial_kelly_cap, 0.05)

    st.sidebar.header("📚 Sportsbooks")
    selected_books = st.sidebar.multiselect("Books to include", default_books, default=default_books)

    with st.sidebar.expander("🔍 Advanced Filters"):
        sports_filter = st.text_input("Sport keys include (comma-separated, blank = all)", value="")
        refresh_seconds = st.number_input("Refresh every (seconds)", min_value=10, value=refresh_seconds_default)

    # ----- Fetch + compute -----
    df = fetch_odds()
    if df.empty:
        st.warning(
            "No data loaded yet. If using API, pick a sport in the sidebar. "
            "If using CSV, make sure `sample_data/sample_odds.csv` exists."
        )
        return

    if selected_books:
        df = df[df["book"].isin(selected_books)]
    if sports_filter.strip():
        allowed = [s.strip() for s in sports_filter.split(",") if s.strip()]
        df = df[df["sport_key"].isin(allowed)]

    table = compute_table(df, kelly_cap=kelly_cap, bankroll=bankroll)
    if table.empty:
        st.info("No rows matched your filters.")
        return

    table = table.sort_values(by="edge_pct", ascending=False)
    table = table[table["edge_pct"] >= min_edge]

    st.dataframe(table, use_container_width=True, hide_index=True)

    csv = table.to_csv(index=False).encode("utf-8")
    st.download_button("Download opportunities (CSV)", data=csv, file_name="positive_ev_opportunities.csv", mime="text/csv")

    st.caption(
        """
**Notes**
- `true_prob_est` uses a sharp ref price when provided; otherwise it de-vigs the market pair.
- `edge_pct` is expected return per $1 (e.g., 0.025 = +2.5%).
- `stake_reco_$` uses a capped Kelly vs. your bankroll.
"""
    )

def _ev_preview_table():
    """Small preview table on home page using CSV if present (no controls)."""
    try:
        df = load_data_csv("sample_data/sample_odds.csv")
        df = df.head(100)
        table = compute_table(df, kelly_cap=initial_kelly_cap, bankroll=1000.0).sort_values("edge_pct", ascending=False).head(8)
        st.markdown("### Opportunities (preview)")
        st.dataframe(table, use_container_width=True, hide_index=True)
        st.caption("Preview uses sample data. Full controls are in Tools →")
    except Exception:
        pass

def page_pricing():
    st.markdown("## Pricing")
    cols = st.columns(2)
    with cols[0]:
        st.markdown("### Gold")
        st.write("- Positive EV Finder\n- CSV Export\n- Basic Filters")
        if st.button("Try 7 days free"):
            set_view("login")
    with cols[1]:
        st.markdown("### Platinum")
        st.write("- Everything in Gold\n- Live data support\n- Priority updates")
        st.button("Apply for trial", on_click=set_view, args=("login",))

def page_resources():
    st.markdown("## Resources")
    st.markdown("### Positive EV Betting 101")
    st.write(
        "- De-vig markets to get **fair odds**.\n"
        "- Compare sportsbook price vs. fair price to get **edge**.\n"
        "- Use **capped Kelly** to size bets within risk limits.\n"
    )
    st.markdown("### Responsible Betting")
    st.write("Always verify prices and availability before placing any bets.")

def page_login():
    st.markdown("## Sign in to your account")
    # central login card
    email = st.text_input("Email or Username")
    password = st.text_input("Password", type="password")
    colL, colR = st.columns([1, 2])
    if colL.button("Sign in"):
        try:
            if email in st.secrets["users"] and st.secrets["users"][email] == password:
                st.session_state["authenticated"] = True
                st.session_state["user"] = email
                st.success(f"Welcome, {email}!")
                set_view("tools")
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")
        except Exception:
            st.warning("Configure users in `.streamlit/secrets.toml`.")

    st.markdown("or continue with")
    c1, c2, c3 = st.columns(3)
    c1.button("Continue with Google", use_container_width=True)
    c2.button("Continue with Apple", use_container_width=True)
    c3.button("Continue with Phone", use_container_width=True)
    st.caption("Don't have an account? Click the trial button anywhere to get started.")

# ======================
# -------- ROUTER ------
# ======================
if st.session_state["view"] == "home":
    page_home()
elif st.session_state["view"] == "tools":
    page_tools()
elif st.session_state["view"] == "pricing":
    page_pricing()
elif st.session_state["view"] == "resources":
    page_resources()
elif st.session_state["view"] == "login":
    page_login()
else:
    page_home()

# ======================
# ------- FOOTER -------
# ======================
st.markdown(
    f"""
<footer>
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <div>© {datetime.now().year} {BRAND_NAME}. All rights reserved.</div>
    <div class="disclaimer">This tool is for informational purposes only. Always verify odds before betting.</div>
  </div>
</footer>
""",
    unsafe_allow_html=True,
)
