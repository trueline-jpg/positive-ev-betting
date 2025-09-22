from __future__ import annotations
import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from ui import use_global_style, header
from ev_utils import (
    american_to_decimal, edge_decimal,
    estimate_true_prob_from_ref
)

# ---------- STYLE ----------
use_global_style()
header(active="EV Finder")

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

# ---------- DATA FETCH ----------
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
            st.error("Missing ODDS_API_KEY in environment. Add it to your .env file.")
            return pd.DataFrame()

        provider = OddsAPIProvider(api_key, regions=regions, markets="h2h", odds_format="american")
        sports = provider.get_sports()
        sport_options = [s.get("key") for s in sports]
        chosen = st.sidebar.selectbox("Choose Sport", options=sport_options)
        data = provider.get_odds(chosen)

        rows = []
        for ev in data:
            home = ev.get("home_team", "")
            away = ev.get("away_team", "")
            matchup = f"{home} vs {away}" if home and away else ev.get("sport_key", "Unknown")
            sport_key = ev.get("sport_key", "Unknown")
            commence = ev.get("commence_time", "")

            for bk in ev.get("bookmakers", []):
                book = bk.get("title", "Unknown Sportsbook")
                for mk in bk.get("markets", []):
                    if mk.get("key") != "h2h":
                        continue
                    outcomes = mk.get("outcomes", [])
                    if len(outcomes) < 2:
                        continue
                    for oc in outcomes:
                        name = oc.get("name", "")
                        price_am = oc.get("price")
                        opp_price = [o.get("price") for o in outcomes if o != oc]
                        opp_price = opp_price[0] if opp_price else None

                        rows.append({
                            "matchup": matchup,
                            "player_team": name,
                            "price_american": price_am,
                            "opp_price_american": opp_price,
                            "book": book,
                            "sport": sport_key,
                            "commence_time": commence,
                        })
        return pd.DataFrame(rows)

# ---------- CALCULATIONS ----------
def compute_table(df: pd.DataFrame,
                  fallback_margin: float,
                  min_edge: float) -> pd.DataFrame:
    out = []
    for _, row in df.iterrows():
        price = safe_float(row.get("price_american"))
        opp_val = safe_float(row.get("opp_price_american"))

        if price is None:
            continue

        offer_decimal = american_to_decimal(price)
        side_implied = 1.0 / offer_decimal
        opp_implied = (1.0 / american_to_decimal(opp_val)) if opp_val else 1 - side_implied

        # Expected (true) probability
        true_p = estimate_true_prob_from_ref(None, fallback_margin, side_implied, opp_implied)
        ev = edge_decimal(offer_decimal, true_p)

        out.append({
            "Matchup": row.get("matchup", "Unknown"),
            "Team / Player": row.get("player_team", "Unknown"),
            "Sportsbook": row.get("book", "Unknown"),
            "Odds (American)": price,
            "Implied Probability": f"{side_implied:.2%}",
            "Expected Probability": f"{true_p:.2%}",
        })

    out = pd.DataFrame(out)
    if out.empty:
        return out
    out = out.sort_values(by="Expected Probability", ascending=False)
    out = out[out["Expected Probability"].notnull()]
    return out.reset_index(drop=True)

# ---------- PAGE ----------
st.set_page_config(page_title="EV Finder • TruLine Betting", page_icon="📈", layout="wide")

load_dotenv()
provider_name = os.getenv("PROVIDER", "csv")
regions = os.getenv("REGIONS", "us")
fallback_margin = float(os.getenv("REF_FALLBACK_MARGIN", "0.03"))
min_edge = float(os.getenv("MIN_EDGE", "0.02"))

st.markdown("## 📈 Positive EV Betting Finder")
st.caption("TruLine Betting")

df = fetch_odds(provider_name, regions)
if df.empty:
    st.warning("No data loaded. Check your API key or sample_data folder.")
    st.stop()

table = compute_table(df, fallback_margin=fallback_margin, min_edge=min_edge)

if table.empty:
    st.info("No bets passed the filters — try adjusting settings or wait for new odds.")
else:
    st.dataframe(table, use_container_width=True, hide_index=True)
