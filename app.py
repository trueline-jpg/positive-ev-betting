from __future__ import annotations

# --- stdlib / libs ---
import os
from datetime import datetime, timezone
import pandas as pd
import numpy as np
import streamlit as st
from dotenv import load_dotenv

# --- local ---
from ev_utils import (
    american_to_decimal, implied_prob_from_american, edge_decimal,
    kelly_fraction, estimate_true_prob_from_ref
)

# ------------------------------------------------------
# Page config MUST be the very first Streamlit call
# ------------------------------------------------------
st.set_page_config(page_title="TruLine Betting", layout="wide")

# ------------------------------------------------------
# Login
# ------------------------------------------------------
def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    # Load from Streamlit secrets
    if username in st.secrets.get("users", {}) and st.secrets["users"][username] == password:
        st.session_state["authenticated"] = True
        st.session_state["user"] = username
        st.sidebar.success(f"Welcome, {username}!")
    else:
        if username and password:
            st.sidebar.error("Invalid username or password")

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    login()
    st.stop()

# ------------------------------------------------------
# Env
# ------------------------------------------------------
load_dotenv()

# ------------------------------------------------------
# Global CSS (single, safe block)
# ------------------------------------------------------
st.markdown(
    """
    <style>
      /* ---- Global App Background / Typography ---- */
      .stApp {
        background-color: #0f0f0f;   /* matte black */
        color: #ffffff;              /* white text */
        font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif;
      }

      /* ---- Sidebar ---- */
      section[data-testid="stSidebar"] {
        background-color: #1a1a1a;   /* dark gray */
        color: #ffffff;
        border-right: 1px solid #333;
      }

      /* ---- Titles ---- */
      h1, h2, h3, h4 { color: #ffffff; font-weight: 600; }

      /* ---- Dataframe ---- */
      .dataframe th {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        text-align: center;
      }
      .dataframe td {
        color: #d1d1d1 !important;
        background-color: #121212 !important;
      }

      /* ---- Buttons (primary) ---- */
      button[kind="primary"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: 600;
        border-radius: 6px;
        border: none;
      }
      button[kind="primary"]:hover { background-color: #e6e6e6 !important; }

      /* ---- Slider knob/track ---- */
      .stSlider > div > div > div > div { background: #ffffff; }

      /* ---- Expander ---- */
      .streamlit-expanderHeader {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
      }

      /* ---- Soft brand header layout ---- */
      .brand-row { display: flex; align-items: center; gap: 16px; margin: 8px 0 4px; }
      .brand-right h1 { margin: 0 0 2px 0; }
      .brand-right p  { margin: 0; color: #b3b3b3; }

      /* ---- Logo: make white on black using CSS filter ---- */
      img.app-logo {
        width: 80px;                 /* size of logo */
        filter: invert(1) brightness(1.6) contrast(1.05);  /* turn dark logo to white */
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------
# Brand Header (logo top-left, small; title on right)
# NOTE: using raw <img> so we can attach a CSS class
# ------------------------------------------------------
st.markdown(
    """
    <div class="brand-row">
      <div class="brand-left">
        <img class="app-logo" src="assets/logo.png" alt="TruLine Betting logo" />
      </div>
      <div class="brand-right">
        <h1>📈 Positive EV Betting Finder</h1>
        <p>Built by Armen Chapman | TruLine Betting</p>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------
# Sidebar config
# ------------------------------------------------------
provider_name = os.getenv("PROVIDER", "csv")
regions = os.getenv("REGIONS", "us")
markets_env = os.getenv("MARKETS", "h2h,spreads,totals")
default_books = [b.strip() for b in os.getenv(
    "BOOKS",
    "DraftKings,FanDuel,BetMGM,PointsBet,Caesars,Barstool,BetRivers,Unibet,Bet365,Pinnacle,BetUS,Fanatics,Underdog,Prizepicks,Fliff"
).split(",") if b.strip()]
ref_book = os.getenv("REF_BOOK", "Pinnacle")
fallback_margin = float(os.getenv("REF_FALLBACK_MARGIN", "0.03"))
kelly_cap_env = float(os.getenv("KELLY_FRACTION", "0.25"))
min_edge_default = float(os.getenv("MIN_EDGE", "0.02"))
refresh_seconds_env = int(os.getenv("REFRESH_SECONDS", "60"))

st.sidebar.header("⚙️ Settings")
min_edge = st.sidebar.slider("Min Edge (EV%)", 0.0, 0.10, min_edge_default, 0.005, format="%.3f")
stake_bankroll = st.sidebar.number_input("Bankroll ($)", min_value=10.0, value=1000.0, step=50.0)
kelly_cap = st.sidebar.slider("Kelly Cap (fraction of full Kelly)", 0.0, 1.0, kelly_cap_env, 0.05)

st.sidebar.header("📚 Sportsbooks")
selected_books = st.sidebar.multiselect("Books to include", default_books, default=default_books)

with st.sidebar.expander("🔍 Advanced Filters"):
    sports_filter = st.text_input("Sport keys include (comma-separated, blank = all)", value="")
    refresh_seconds = st.number_input("Refresh every (seconds)", min_value=10, value=refresh_seconds_env)

# 🔑 Sportsbook API Connections (UI only; keys not used in CSV mode)
st.sidebar.header("🔗 Sportsbook Connections")
with st.sidebar.expander("⚡ Connect Sportsbooks", expanded=False):
    st.text_input("DraftKings API Key", type="password")
    st.text_input("FanDuel API Key", type="password")
    st.text_input("BetMGM API Key", type="password")
    st.text_input("PointsBet API Key", type="password")
    st.text_input("Caesars API Key", type="password")
    st.text_input("Barstool API Key", type="password")
    st.text_input("BetRivers API Key", type="password")
    st.text_input("Unibet API Key", type="password")
    st.text_input("Bet365 API Key", type="password")
    st.text_input("Pinnacle API Key", type="password")
    st.text_input("BetUS API Key", type="password")
    st.text_input("Fanatics API Key", type="password")
    st.text_input("Underdog API Key", type="password")
    st.text_input("PrizePicks API Key", type="password")
    st.text_input("Fliff API Key", type="password")
    st.info("Enter your sportsbook API keys above to fetch your personalized odds.")
st.sidebar.caption("Tip: Set PROVIDER=csv in .env to use sample data without an API key.")

# ------------------------------------------------------
# Data provider
# ------------------------------------------------------
def load_data_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

def fetch_odds() -> pd.DataFrame:
    if provider_name.lower() == "csv":
        return load_data_csv("sample_data/sample_odds.csv")
    else:
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
        sport_options = [s.get("key") for s in sports]
        chosen_sport = st.sidebar.selectbox("Sport (live from API)", options=sport_options)
        data = provider.get_odds(chosen_sport)

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
                    for oc in outcomes:
                        side = "home" if oc.get("name") == home else ("away" if oc.get("name") == away else oc.get("name"))
                        price_am = oc.get("price")
                        opp_price = None
                        for oc2 in outcomes:
                            if oc2 is not oc:
                                opp_price = oc2.get("price")
                                break
                        rows.append({
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
                        })
        df = pd.DataFrame(rows)
        return df

# ------------------------------------------------------
# Fetch + validate data
# ------------------------------------------------------
df = fetch_odds()
if df.empty:
    st.warning("No data loaded yet. If using API, pick a sport in the sidebar. If using CSV, ensure sample_data/sample_odds.csv exists.")
    st.stop()

# Filter books
if selected_books:
    df = df[df["book"].isin(selected_books)]

# Filter sports
if "sports_filter" in locals() and sports_filter.strip():
    allowed = [s.strip() for s in sports_filter.split(",") if s.strip()]
    df = df[df["sport_key"].isin(allowed)]

# ------------------------------------------------------
# Compute EV table
# ------------------------------------------------------
def compute_table(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for _, row in df.iterrows():
        # Offer price parsing
        try:
            if isinstance(row["price_american"], str) and row["price_american"].startswith("opp:"):
                price = float(str(row["price_american"]).replace("opp:", "").replace("+", ""))
            else:
                price = float(str(row["price_american"]).replace("+", ""))
        except Exception:
            s = str(row["price_american"]).strip()
            price = float(s.replace("+", "")) if not s.startswith("-") else float(s)

        # Opp price parsing
        opp_price = row.get("opp_price_american", None)
        try:
            if opp_price is not None and isinstance(opp_price, str) and opp_price.startswith("opp:"):
                opp_price_val = float(opp_price.split(":")[1])
            else:
                opp_price_val = float(opp_price) if opp_price is not None else None
        except Exception:
            try:
                opp_str = str(opp_price)
                opp_price_val = float(opp_str.replace("+", "")) if not opp_str.startswith("-") else float(opp_str)
            except Exception:
                opp_price_val = None

        # Reference price parsing (if present)
        ref_price = row.get("ref_price_american", None)
        try:
            if ref_price is not None and isinstance(ref_price, str) and ":" in ref_price:
                ref_price_val = float(ref_price.split(":")[-1])
            elif ref_price is not None:
                ref_price_val = float(ref_price)
            else:
                ref_price_val = None
        except Exception:
            ref_price_val = None

        offer_decimal = american_to_decimal(price)
        side_implied = 1.0 / offer_decimal
        opp_implied = (1.0 / american_to_decimal(opp_price_val)) if opp_price_val else (1.0 - side_implied)

        # True/fair probability using ref/opp with fallback margin
        true_p = estimate_true_prob_from_ref(ref_price_val, fallback_margin, side_implied, opp_implied)

        ev = edge_decimal(offer_decimal, true_p)  # expected value per $1
        full_kelly = kelly_fraction(true_p, offer_decimal)
        rec_stake = max(0.0, min(full_kelly * kelly_cap * stake_bankroll, stake_bankroll))

        out.append({
            "sport_key": row["sport_key"],
            "commence_time": row["commence_time"],
            "home_team": row["home_team"],
            "away_team": row["away_team"],
            "book": row["book"],
            "market": row["market"],
            "side": row["side"],
            "price_american": price,
            "opp_price_american": opp_price_val,
            "ref_price_american": ref_price_val,
            "offer_decimal": round(offer_decimal, 4),
            "true_prob_est": round(true_p, 4),
            "fair_decimal": round(1.0 / true_p, 4) if true_p > 0 else None,
            "edge_pct": round(ev, 4),
            "kelly_full": round(full_kelly, 4),
            "stake_reco_$": round(rec_stake, 2),
        })
    return pd.DataFrame(out)

table = compute_table(df).sort_values(by="edge_pct", ascending=False)
table = table[table["edge_pct"] >= min_edge]

# ------------------------------------------------------
# UI: results
# ------------------------------------------------------
st.subheader("Opportunities")
st.dataframe(table, use_container_width=True, hide_index=True)

csv = table.to_csv(index=False).encode("utf-8")
st.download_button("Download opportunities (CSV)", data=csv, file_name="positive_ev_opportunities.csv", mime="text/csv")

st.caption("""
**Notes**
- `true_prob_est` uses a sharp ref price when provided; otherwise it de-vigs the market pair.
- `edge_pct` is expected return per $1 (e.g., 0.025 = +2.5%).
- `stake_reco_$` uses a capped Kelly (user-controlled cap) against your bankroll input.
- Always verify odds and availability before betting.
""")
st.markdown("---")
st.markdown("⚠️ **Disclaimer**: This tool is for informational purposes only. Always verify odds directly with sportsbooks before betting.")
