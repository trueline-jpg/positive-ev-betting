from __future__ import annotations
import streamlit as st
import os, io, time, json, math
from datetime import datetime, timezone
import pandas as pd
import numpy as np
from dotenv import load_dotenv

from ev_utils import (
    american_to_decimal, implied_prob_from_american, edge_decimal,
    kelly_fraction, estimate_true_prob_from_ref
)

# ==============================
# LOGIN SYSTEM
# ==============================
def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    # Load from Streamlit secrets
    if username in st.secrets["users"] and st.secrets["users"][username] == password:
        st.session_state["authenticated"] = True
        st.session_state["user"] = username
        st.sidebar.success(f"Welcome, {username}!")
    else:
        if username and password:
            st.sidebar.error("Invalid username or password")

# Run login if not already authenticated
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    login()
    st.stop()

# ==============================
# ENV + CONFIG
# ==============================
load_dotenv()

st.set_page_config(
    page_title="TruLine Betting",
    layout="wide"
)

# ==============================
# CUSTOM CSS
# ==============================
st.markdown(
    """
    <style>
    /* Global App Background */
    .stApp {
        background-color: #0f0f0f;  /* matte black */
        color: #ffffff;  /* white text */
        font-family: 'Helvetica Neue', sans-serif;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #1a1a1a;
        color: #ffffff;
        border-right: 1px solid #333;
    }

    /* Titles */
    h1, h2, h3, h4 {
        color: #ffffff;
        font-weight: 600;
    }

    /* Dataframe/Table Styling */
    .dataframe th {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        text-align: center;
    }
    .dataframe td {
        color: #d1d1d1 !important;
        background-color: #121212 !important;
    }

    /* Buttons */
    button[kind="primary"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: 600;
        border-radius: 6px;
        border: none;
    }
    button[kind="primary"]:hover {
        background-color: #e6e6e6 !important;
    }

    /* Expander Panels */
    .streamlit-expanderHeader {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }

    /* Disclaimer */
    .disclaimer {
        color: #b3b3b3;
        font-size: 13px;
        margin-top: 20px;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================
# HEADER + LOGO
# ==============================
col1, col2 = st.columns([0.15, 0.85])
with col1:
    st.image("assets/logo.png", width=80)
with col2:
    st.markdown(
        """
        <h1 style='margin-bottom:0;'>📈 TruLine Betting</h1>
        <p style='margin-top:0; color: #b3b3b3;'>Positive EV Betting Finder</p>
        """,
        unsafe_allow_html=True
    )

# ==============================
# SIDEBAR CONFIG
# ==============================
provider_name = os.getenv("PROVIDER", "csv")
regions = os.getenv("REGIONS", "us")
markets_env = os.getenv("MARKETS", "h2h,spreads,totals")
default_books = [b.strip() for b in os.getenv(
    "BOOKS",
    "DraftKings,FanDuel,BetMGM,PointsBet,Caesars,Barstool,BetRivers,Unibet,Bet365,Pinnacle,BetUS,Fanatics,Underdog,Prizepicks,Fliff"
).split(",") if b.strip()]
ref_book = os.getenv("REF_BOOK", "Pinnacle")
fallback_margin = float(os.getenv("REF_FALLBACK_MARGIN", "0.03"))
kelly_cap = float(os.getenv("KELLY_FRACTION", "0.25"))
min_edge_default = float(os.getenv("MIN_EDGE", "0.02"))
refresh_seconds = int(os.getenv("REFRESH_SECONDS", "60"))

st.sidebar.header("⚙️ Settings")
min_edge = st.sidebar.slider("Min Edge (EV%)", 0.0, 0.10, min_edge_default, 0.005, format="%.3f")
stake_bankroll = st.sidebar.number_input("Bankroll ($)", min_value=10.0, value=1000.0, step=50.0)
kelly_cap = st.sidebar.slider("Kelly Cap (fraction of full Kelly)", 0.0, 1.0, kelly_cap, 0.05)

st.sidebar.header("📚 Sportsbooks")
selected_books = st.sidebar.multiselect("Books to include", default_books, default=default_books)

with st.sidebar.expander("🔍 Advanced Filters"):
    sports_filter = st.text_input("Sport keys include (comma-separated, blank = all)", value="")
    refresh_seconds = st.number_input("Refresh every (seconds)", min_value=10, value=60)

st.sidebar.header("🔗 Sportsbook Connections")
with st.sidebar.expander("⚡ Connect Sportsbooks", expanded=False):
    st.info("Enter your sportsbook API keys above to fetch personalized odds.")
st.sidebar.caption("Tip: Set PROVIDER=csv in .env to use sample data without an API key.")

# ==============================
# DATA PROVIDER
# ==============================
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
        return pd.DataFrame(rows)

# ==============================
# FETCH DATA
# ==============================
df = fetch_odds()
if df.empty:
    st.warning("No data loaded yet. If using API, pick a sport in the sidebar. If using CSV, ensure sample_data/sample_odds.csv exists.")
    st.stop()

if selected_books:
    df = df[df["book"].isin(selected_books)]

if sports_filter.strip():
    allowed = [s.strip() for s in sports_filter.split(",") if s.strip()]
    df = df[df["sport_key"].isin(allowed)]

# ==============================
# COMPUTE EV TABLE
# ==============================
def compute_table(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for _, row in df.iterrows():
        try:
            price = float(str(row["price_american"]).replace("+","").replace("opp:","")) if isinstance(row["price_american"], str) and row["price_american"].startswith("opp:") else float(row["price_american"])
        except Exception:
            s = str(row["price_american"]).strip()
            price = float(s.replace("+",""))
            if s.startswith("-"):
                price = float(s)

        opp_price = row.get("opp_price_american", None)
        try:
            opp_price_val = float(opp_price) if opp_price not in [None, ""] else None
        except Exception:
            opp_price_val = None

        ref_price = row.get("ref_price_american", None)
        try:
            ref_price_val = float(ref_price) if ref_price not in [None, ""] else None
        except Exception:
            ref_price_val = None

        offer_decimal = american_to_decimal(price)
        side_implied = 1.0 / offer_decimal
        true_p = estimate_true_prob_from_ref(
            ref_price_val, fallback_margin, side_implied,
            (1.0 / american_to_decimal(opp_price_val)) if opp_price_val else 1.0 - side_implied
        )

        ev = edge_decimal(offer_decimal, true_p)
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
            "edge_pct": round(ev, 4),
            "kelly_full": round(full_kelly, 4),
            "stake_reco_$": round(rec_stake, 2),
        })
    return pd.DataFrame(out)

table = compute_table(df)
table = table.sort_values(by="edge_pct", ascending=False)
table = table[table["edge_pct"] >= min_edge]

# ==============================
# DISPLAY
# ==============================
st.subheader("Opportunities")
st.dataframe(table, use_container_width=True, hide_index=True)

csv = table.to_csv(index=False).encode("utf-8")
st.download_button("Download opportunities (CSV)", data=csv, file_name="positive_ev_opportunities.csv", mime="text/csv")

st.markdown("---")
st.caption("""
⚠️ **Disclaimer**: This tool is for informational purposes only. 
Always verify odds directly with sportsbooks before betting.
""")
