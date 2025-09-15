from __future__ import annotations
import streamlit as st
import os, io, time, json, math, base64
from datetime import datetime, timezone
import pandas as pd
import numpy as np
from dotenv import load_dotenv

from ev_utils import (
    american_to_decimal, implied_prob_from_american, edge_decimal,
    kelly_fraction, estimate_true_prob_from_ref
)

# --- LOGIN SYSTEM ---
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

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    login()
    st.stop()

# --- LOAD ENV ---
load_dotenv()

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="TruLine Betting",  # <- fixed spelling
    layout="wide"
)

# --- EMBED LOGO (Base64) ---
def get_base64_image(image_path: str):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

try:
    logo_base64 = get_base64_image("assets/logo.png")
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;">
            <img src="data:image/png;base64,{logo_base64}" width="80" style="filter: invert(1) brightness(1.6) contrast(1.05);" />
            <h1 style="margin:0;">📈 TruLine Betting</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
except Exception as e:
    st.warning("⚠️ Logo not found — please check assets/logo.png")

# --- CUSTOM CSS ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0f0f0f;  /* matte black background */
        color: #ffffff;
        font-family: 'Helvetica Neue', sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #1a1a1a;
        color: #ffffff;
        border-right: 1px solid #333;
    }
    h1, h2, h3, h4 {
        color: #ffffff;
        font-weight: 600;
    }
    .dataframe th {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        text-align: center;
    }
    .dataframe td {
        color: #d1d1d1 !important;
        background-color: #121212 !important;
    }
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
    .streamlit-expanderHeader {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- SIDEBAR CONFIG ---
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

# Sidebar UI
st.sidebar.header("⚙️ Settings")
min_edge = st.sidebar.slider("Min Edge (EV%)", 0.0, 0.10, min_edge_default, 0.005, format="%.3f")
stake_bankroll = st.sidebar.number_input("Bankroll ($)", min_value=10.0, value=1000.0, step=50.0)
kelly_cap = st.sidebar.slider("Kelly Cap (fraction of full Kelly)", 0.0, 1.0, kelly_cap, 0.05)

st.sidebar.header("📚 Sportsbooks")
selected_books = st.sidebar.multiselect("Books to include", default_books, default=default_books)

with st.sidebar.expander("🔍 Advanced Filters"):
    sports_filter = st.text_input("Sport keys include (comma-separated, blank = all)", value="")
    refresh_seconds = st.number_input("Refresh every (seconds)", min_value=10, value=60)

# Sidebar sportsbook connections
st.sidebar.header("🔗 Sportsbook Connections")
with st.sidebar.expander("⚡ Connect Sportsbooks", expanded=False):
    dk_api = st.text_input("DraftKings API Key", type="password")
    fd_api = st.text_input("FanDuel API Key", type="password")
    # ... (rest of your sportsbook API inputs)

st.sidebar.caption("Tip: Set PROVIDER=csv in .env to use sample data without an API key.")

# --- DATA LOADING ---
def load_data_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

def fetch_odds() -> pd.DataFrame:
    if provider_name.lower() == "csv":
        return load_data_csv("sample_data/sample_odds.csv")
    else:
        return pd.DataFrame()  # simplified fallback for now

df = fetch_odds()

if df.empty:
    st.warning("No data loaded yet. If using API, pick a sport in the sidebar. If using CSV, ensure sample_data/sample_odds.csv exists.")
    st.stop()

# Filter books
if selected_books:
    df = df[df["book"].isin(selected_books)]

# Filter sports
if sports_filter.strip():
    allowed = [s.strip() for s in sports_filter.split(",") if s.strip()]
    df = df[df["sport_key"].isin(allowed)]

# --- EV CALC ---
def compute_table(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for idx, row in df.iterrows():
        price = float(row["price_american"])
        opp_price_val = float(row["opp_price_american"]) if row["opp_price_american"] is not None else None
        ref_price_val = float(row["ref_price_american"]) if row["ref_price_american"] is not None else None

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
            "stake_reco_$": round(rec_stake, 2),
        })
    return pd.DataFrame(out)

table = compute_table(df)
table = table.sort_values(by="edge_pct", ascending=False)
table = table[table["edge_pct"] >= min_edge]

st.subheader("Opportunities")
st.dataframe(table, use_container_width=True, hide_index=True)

# Export
csv = table.to_csv(index=False).encode("utf-8")
st.download_button("Download opportunities (CSV)", data=csv, file_name="positive_ev_opportunities.csv", mime="text/csv")
