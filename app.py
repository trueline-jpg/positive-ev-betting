from __future__ import annotations

# --- stdlib / libs ---
import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# --- local ---
from ev_utils import (
    american_to_decimal, edge_decimal,
    kelly_fraction, estimate_true_prob_from_ref
)

# ------------------------------------------------------
# Page config
# ------------------------------------------------------
st.set_page_config(page_title="TruLine Betting", page_icon="assets/logo.png", layout="wide")

# ------------------------------------------------------
# Login
# ------------------------------------------------------
def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

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
# Global CSS
# ------------------------------------------------------
st.markdown(
    """
    <style>
      .stApp {
        background-color: #0f0f0f;
        color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif;
      }

      section[data-testid="stSidebar"] {
        background-color: #1a1a1a;
        color: #ffffff;
        border-right: 1px solid #333;
      }

      h1, h2, h3, h4 { color: #ffffff; font-weight: 600; }

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
      button[kind="primary"]:hover { background-color: #e6e6e6 !important; }

      .stSlider > div > div > div > div { background: #ffffff; }

      .streamlit-expanderHeader {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
      }

      .brand-row { display: flex; align-items: center; gap: 16px; margin: 8px 0 4px; }
      .brand-right h1 { margin: 0 0 2px 0; }
      .brand-right p  { margin: 0; color: #b3b3b3; }

      img.app-logo {
        width: 80px;
        filter: invert(1) brightness(1.6) contrast(1.05);
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------
# Brand Header
# ------------------------------------------------------
st.markdown(
    """
    <div class="brand-row">
      <div class="brand-left">
        <img class="app-logo" src="assets/logo.png" alt="TruLine logo" />
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

st.sidebar.header("🔗 Sportsbook Connections")
with st.sidebar.expander("⚡ Connect Sportsbooks", expanded=False):
    st.info("Enter your sportsbook API keys above to fetch your personalized odds.")
st.sidebar.caption("Tip: Set PROVIDER=csv in .env to use sample data without an API key.")

# ------------------------------------------------------
# Data provider (simplified for CSV)
# ------------------------------------------------------
def load_data_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

def fetch_odds() -> pd.DataFrame:
    if provider_name.lower() == "csv":
        return load_data_csv("sample_data/sample_odds.csv")
    return pd.DataFrame()

df = fetch_odds()
if df.empty:
    st.warning("No data loaded yet. If using API, pick a sport in the sidebar. If using CSV, ensure sample_data/sample_odds.csv exists.")
    st.stop()

# Filter
if selected_books:
    df = df[df["book"].isin(selected_books)]
if "sports_filter" in locals() and sports_filter.strip():
    allowed = [s.strip() for s in sports_filter.split(",") if s.strip()]
    df = df[df["sport_key"].isin(allowed)]

# ------------------------------------------------------
# Compute EV table
# ------------------------------------------------------
def compute_table(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for _, row in df.iterrows():
        price = float(str(row["price_american"]).replace("+", ""))
        opp_price_val = float(row.get("opp_price_american", 0)) if row.get("opp_price_american") else None
        ref_price_val = float(row.get("ref_price_american", 0)) if row.get("ref_price_american") else None

        offer_decimal = american_to_decimal(price)
        side_implied = 1.0 / offer_decimal
        opp_implied = (1.0 / american_to_decimal(opp_price_val)) if opp_price_val else (1.0 - side_implied)

        true_p = estimate_true_prob_from_ref(ref_price_val, fallback_margin, side_implied, opp_implied)
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

table = compute_table(df).sort_values(by="edge_pct", ascending=False)
table = table[table["edge_pct"] >= min_edge]

# ------------------------------------------------------
# UI
# ------------------------------------------------------
st.subheader("Opportunities")
st.dataframe(table, use_container_width=True, hide_index=True)

csv = table.to_csv(index=False).encode("utf-8")
st.download_button("Download opportunities (CSV)", data=csv, file_name="positive_ev_opportunities.csv", mime="text/csv")

st.caption("""
**Notes**
- `true_prob_est` uses a sharp ref price when provided; otherwise it de-vigs the market pair.
- `edge_pct` is expected return per $1 (e.g., 0.025 = +2.5%).
- `stake_reco_$` uses a capped Kelly against your bankroll input.
""")
st.markdown("---")
st.markdown("⚠️ **Disclaimer**: This tool is for informational purposes only. Always verify odds directly with sportsbooks before betting.")
