from __future__ import annotations
import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from ui import use_global_style, header, footer
from ev_utils import (
    american_to_decimal, implied_prob_from_american, edge_decimal,
    kelly_fraction, estimate_true_prob_from_ref
)

# ---------- SAFE FLOAT ----------
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

# ---------- PROVIDERS ----------
def load_data_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

def fetch_odds(provider_name: str, regions: str) -> pd.DataFrame:
    if provider_name.lower() == "csv":
        return load_data_csv("sample_data/sample_odds.csv")
    else:
        from providers.oddsapi_provider import OddsAPIProvider
        api_key = os.getenv("ODDS_API_KEY", "")
        if not api_key:
            return pd.DataFrame()

        provider = OddsAPIProvider(api_key, regions=regions, markets="h2h", odds_format="american")
        sports = provider.get_sports()
        sport_options = [s.get("key") for s in sports]
        chosen = st.sidebar.selectbox("Sport (live from API)", options=sport_options)
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
                            "side": side,
                            "price_american": price_am,
                            "opp_price_american": opp_price,
                            "ref_price_american": None,
                        })
        return pd.DataFrame(rows)

# ---------- MAIN COMPUTE ----------
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

        matchup = f"{row['home_team']} vs {row['away_team']}"

        sport_map = {
            "americanfootball_nfl": "NFL",
            "basketball_nba": "NBA",
            "soccer_epl": "EPL",
            "soccer_laliga": "La Liga",
            "baseball_mlb": "MLB",
            "basketball_wnba": "WNBA",
        }
        sport_label = sport_map.get(row["sport_key"], row["sport_key"])

        out.append({
            "Matchup": matchup,
            "Date/Time": row["commence_time"],
            "Sport": sport_label,
            "Book": row["book"],
            "Side": row["side"],
            "Odds (American)": price,
            "Implied Probability": f"{round(side_implied * 100, 1)}%",
            "Expected Probability": f"{round(true_p * 100, 1)}%",
            "Edge %": f"{round(ev * 100, 1)}%",
            "Stake ($)": f"${round(stake_reco, 2)}",
        })

    out = pd.DataFrame(out)
    if out.empty:
        return out
    out = out.sort_values(by="Date/Time", ascending=True)
    out = out.reset_index(drop=True)
    return out

# ---------- PAGE ----------
st.set_page_config(page_title="EV Finder • TruLine Betting", page_icon="📈", layout="wide")

use_global_style()
header(active="EV Finder")

load_dotenv()
provider_name = os.getenv("PROVIDER", "csv")
regions = os.getenv("REGIONS", "us")

# Sidebar controls
st.sidebar.header("⚙️ Settings")
min_edge_default = float(os.getenv("MIN_EDGE", "0.02"))
kelly_cap_default = float(os.getenv("KELLY_FRACTION", "0.25"))
fallback_margin = float(os.getenv("REF_FALLBACK_MARGIN", "0.03"))

min_edge = st.sidebar.slider("Min Edge (EV%)", 0.0, 0.10, min_edge_default, 0.005, format="%.3f")
bankroll = st.sidebar.number_input("Bankroll ($)", min_value=10.0, value=1000.0, step=50.0)
kelly_cap = st.sidebar.slider("Kelly Cap (fraction of full Kelly)", 0.0, 1.0, kelly_cap_default, 0.05)

books_default = [b.strip() for b in os.getenv(
    "BOOKS",
    "DraftKings,FanDuel,BetMGM,PointsBet,Pinnacle"
).split(",") if b.strip()]
selected_books = st.sidebar.multiselect("Books to include", books_default, default=books_default)

# Sports filter
sports_options = ["NFL", "NBA", "WNBA", "MLB", "EPL", "La Liga"]
selected_sports = st.sidebar.multiselect("Sports", sports_options, default=sports_options)

st.markdown("## 📈 Positive EV Betting Finder")
st.caption("TruLine Betting")

df = fetch_odds(provider_name, regions)
if df.empty:
    st.warning("No data loaded. Try API or check sample_data.")
    st.stop()

if selected_books:
    df = df[df["book"].isin(selected_books)]

table = compute_table(
    df=df,
    kelly_cap=kelly_cap,
    stake_bankroll=bankroll,
    fallback_margin=fallback_margin,
    min_edge=min_edge,
)

if table.empty:
    st.info("No bets passed the filters — try adjusting settings.")
else:
    if selected_sports:
        table = table[table["Sport"].isin(selected_sports)]
    st.dataframe(table, use_container_width=True, hide_index=True)

    csv = table.to_csv(index=False).encode("utf-8")
    st.download_button("Download opportunities (CSV)", data=csv,
                       file_name="positive_ev_opportunities.csv", mime="text/csv")

# --- FOOTER ---
footer()
