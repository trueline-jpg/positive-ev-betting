from __future__ import annotations
import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime

from ui import use_global_style, header
from ev_utils import (
    american_to_decimal, edge_decimal,
    kelly_fraction, estimate_true_prob_from_ref
)

# ---------- SPORT MAPPING ----------
SPORT_MAP = {
    "americanfootball_nfl": "NFL",
    "basketball_nba": "NBA",
    "baseball_mlb": "MLB",
    "soccer_epl": "EPL",
    "soccer_spain_la_liga": "La Liga",
    "soccer_uefa_champs_league": "UCL",
    "soccer_fifa_world_cup": "World Cup",
    "tennis_atp": "ATP Tennis",
    "mma_mixed_martial_arts": "MMA",
}

def clean_sport(sport_key: str) -> str:
    return SPORT_MAP.get(sport_key, sport_key.replace("_", " ").title())

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
        chosen = st.sidebar.selectbox("Select Sport (API)", options=sport_options)
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

        game_time = row.get("commence_time")
        if pd.notna(game_time):
            try:
                dt = datetime.fromisoformat(game_time.replace("Z", "+00:00"))
                game_time_str = dt.strftime("%b %d, %Y %I:%M %p")
            except Exception:
                game_time_str = "Unknown"
        else:
            game_time_str = "Unknown"

        matchup = f"{row['home_team']} vs {row['away_team']}" if row.get("home_team") and row.get("away_team") else "Unknown Matchup"

        out.append({
            "Matchup": matchup,
            "Date/Time": game_time_str,
            "Sport": clean_sport(row["sport_key"]),
            "Book": row["book"],
            "Side": row["side"],
            "Odds (American)": price,
            "Implied Probability": f"{side_implied * 100:.1f}%",
            "Expected Probability": f"{true_p * 100:.1f}%",
            "Edge %": f"{ev * 100:.1f}%",
            "Stake ($)": f"${stake_reco:.2f}"
        })

    out = pd.DataFrame(out)
    if out.empty:
        return out
    out["SortTime"] = pd.to_datetime(out["Date/Time"], errors="coerce")
    out = out.sort_values(by=["SortTime", "Edge %"], ascending=[True, False])
    out = out.drop(columns=["SortTime"])
    return out.reset_index(drop=True)

# ---------- PAGE ----------
st.set_page_config(page_title="EV Finder • TruLine Betting", page_icon="📈", layout="wide")
use_global_style()
header(active="EV Finder")

load_dotenv()
provider_name = os.getenv("PROVIDER", "csv")
regions = os.getenv("REGIONS", "us")

st.sidebar.header("⚙️ Filters & Settings")

# EV threshold filter
min_edge_default = float(os.getenv("MIN_EDGE", "0.02"))
min_edge = st.sidebar.slider("Minimum EV %", 0.0, 0.30, min_edge_default, 0.01)

# Bankroll & Kelly settings
bankroll = st.sidebar.number_input("Bankroll ($)", min_value=10.0, value=1000.0, step=50.0)
kelly_cap_default = float(os.getenv("KELLY_FRACTION", "0.25"))
kelly_cap = st.sidebar.slider("Kelly Cap (fraction of full Kelly)", 0.0, 1.0, kelly_cap_default, 0.05)

# Books filter
books_default = [b.strip() for b in os.getenv(
    "BOOKS",
    "DraftKings,FanDuel,BetMGM,PointsBet,Pinnacle,Caesars,BetRivers,Barstool,Unibet,Bet365"
).split(",") if b.strip()]
selected_books = st.sidebar.multiselect("Sportsbooks", books_default, default=books_default)

# Sports filter dropdown
sports_available = list(SPORT_MAP.values())
selected_sports = st.sidebar.multiselect("Sports", sports_available, default=sports_available)

st.markdown("## 📈 Positive EV Betting Finder")
st.caption("TruLine Betting")

df = fetch_odds(provider_name, regions)
if df.empty:
    st.warning("No data loaded. If using API, pick a sport in the sidebar. If using CSV, ensure `sample_data/sample_odds.csv` exists.")
    st.stop()

# Apply filters
if selected_books:
    df = df[df["book"].isin(selected_books)]

if selected_sports:
    allowed_keys = [k for k, v in SPORT_MAP.items() if v in selected_sports]
    df = df[df["sport_key"].isin(allowed_keys)]

table = compute_table(
    df=df,
    kelly_cap=kelly_cap,
    stake_bankroll=bankroll,
    fallback_margin=float(os.getenv("REF_FALLBACK_MARGIN", "0.03")),
    min_edge=min_edge,
)

if table.empty:
    st.info("No bets passed the filters — try adjusting settings or load different data.")
else:
    st.dataframe(table, use_container_width=True, hide_index=True)

    csv = table.to_csv(index=False).encode("utf-8")
    st.download_button("Download opportunities (CSV)", data=csv,
                       file_name="positive_ev_opportunities.csv", mime="text/csv")
