from __future__ import annotations
import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from ui import use_global_style, header
from ev_utils import (
    american_to_decimal, edge_decimal,
    kelly_fraction, estimate_true_prob_from_ref
)

# --- SAFE FLOAT HELPER ---
def safe_float(value):
    try:
        if value is None:
            return None
        s = str(value).strip()
        if s == "" or s.lower() in ("nan", "none"):
            return None
        return float(s.replace("+", "")) if not s.startswith("-") else float(s)
    except Exception:
        return None

# --- PROVIDERS ---
def load_data_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

def fetch_odds(provider_name: str, regions: str) -> pd.DataFrame:
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
        chosen = st.selectbox("Choose a sport (live from API)", options=sport_options)
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
                    for oc in outcomes:
                        name = oc.get("name")
                        side = "home" if name == home else ("away" if name == away else name)
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

# --- MAIN COMPUTE ---
def compute_table(df: pd.DataFrame,
                  kelly_cap: float,
                  stake_bankroll: float,
                  fallback_margin: float,
                  min_edge: float) -> pd.DataFrame:
    out = []
    for _, row in df.iterrows():
        price = safe_float(row["price_american"])
        opp_val = safe_float(row.get("opp_price_american"))
        ref_val = safe_float(row.get("ref_price_american"))

        if price is None:
            continue

        offer_decimal = american_to_decimal(price)
        side_implied = 1.0 / offer_decimal
        opp_implied = (1.0 / american_to_decimal(opp_val)) if opp_val else 1 - side_implied

        true_p = estimate_true_prob_from_ref(ref_val, fallback_margin, side_implied, opp_implied)
        ev = edge_decimal(offer_decimal, true_p)
        full_k = kelly_fraction(true_p, offer_decimal)
        stake_reco = max(0.0, min(full_k * kelly_cap * stake_bankroll, stake_bankroll))

        out.append({
            "sport_key": row["sport_key"],
            "commence_time": row["commence_time"],
            "home_team": row["home_team"],
            "away_team": row["away_team"],
            "book": row["book"],
            "market": row["market"],
            "side": row["side"],
            "price_american": price,
            "opp_price_american": opp_val,
            "ref_price_american": ref_val,
            "offer_decimal": round(offer_decimal, 4),
            "true_prob_est": round(true_p, 4),
            "fair_decimal": round(1.0 / true_p, 4) if true_p > 0 else None,
            "edge_pct": round(ev, 4),
            "kelly_full": round(full_k, 4),
            "stake_reco_$": round(stake_reco, 2),
        })

    out = pd.DataFrame(out)
    if out.empty:
        return out
    out = out.sort_values(by="edge_pct", ascending=False)
    out = out[out["edge_pct"] >= min_edge]
    return out.reset_index(drop=True)

# --- PAGE CONFIG ---
st.set_page_config(page_title="EV Finder • TruLine Betting", page_icon="📈", layout="wide")

# --- HIDE SIDEBAR ---
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        section[data-testid="stSidebar"] {display: none !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- STYLE + HEADER ---
use_global_style()
header(active="EV Finder")

# --- SETTINGS PANEL ---
load_dotenv()
provider_name = os.getenv("PROVIDER", "csv")
regions = os.getenv("REGIONS", "us")

st.markdown("## ⚙️ Settings")

min_edge_default = float(os.getenv("MIN_EDGE", "0.02"))
kelly_cap_default = float(os.getenv("KELLY_FRACTION", "0.25"))
fallback_margin = float(os.getenv("REF_FALLBACK_MARGIN", "0.03"))

col1, col2, col3 = st.columns(3)
with col1:
    min_edge = st.slider("Min Edge (EV%)", 0.0, 0.10, min_edge_default, 0.005, format="%.3f")
with col2:
    bankroll = st.number_input("Bankroll ($)", min_value=10.0, value=1000.0, step=50.0)
with col3:
    kelly_cap = st.slider("Kelly Cap (fraction of full Kelly)", 0.0, 1.0, kelly_cap_default, 0.05)

books_default = [b.strip() for b in os.getenv(
    "BOOKS", "DraftKings,FanDuel,BetMGM,PointsBet,Pinnacle"
).split(",") if b.strip()]
selected_books = st.multiselect("Books to include", books_default, default=books_default)

# --- DATA ---
st.markdown("## 📈 Positive EV Betting Finder")
df = fetch_odds(provider_name, regions)

if df.empty:
    st.warning("No data loaded. If using API, pick a sport. If using CSV, ensure `sample_data/sample_odds.csv` exists.")
    st.stop()

if selected_books:
    df = df[df["book"].isin(selected_books)]

with st.expander("Advanced filters"):
    sports_filter = st.text_input("Sport keys include (comma-separated, blank = all)", value="")
    if sports_filter.strip():
        allowed = [s.strip() for s in sports_filter.split(",") if s.strip()]
        df = df[df["sport_key"].isin(allowed)]

# --- TABLE ---
table = compute_table(df, kelly_cap=kelly_cap, stake_bankroll=bankroll,
                      fallback_margin=fallback_margin, min_edge=min_edge)

if table.empty:
    st.info("No bets passed the filters — try adjusting settings or load different data.")
else:
    st.dataframe(table, use_container_width=True, hide_index=True)
    csv = table.to_csv(index=False).encode("utf-8")
    st.download_button("Download opportunities (CSV)", data=csv,
                       file_name="positive_ev_opportunities.csv", mime="text/csv")
from ui import footer
footer()
