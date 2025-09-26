import os
import pandas as pd
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

from ui import use_global_style, header
from ev_utils import american_to_decimal, implied_prob_from_american

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Picks • TruLine Betting", page_icon="🤖", layout="wide")
use_global_style()
header(active="AI Picks")

# Load environment variables
load_dotenv()
provider_name = os.getenv("PROVIDER", "csv")
regions = os.getenv("REGIONS", "us")

# --- Placeholder Data Fetch ---
# (For now, we just use sample CSV or API odds. Later we swap for real AI.)
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
        chosen_sport = st.sidebar.selectbox("Choose Sport", [s["key"] for s in sports])
        return provider.get_odds(chosen_sport)

df = fetch_odds(provider_name, regions)

if df.empty:
    st.warning("No data loaded. Add API key in .env or use sample_data.")
    st.stop()

# --- AI MODEL PLACEHOLDER ---
# Replace this later with real trained model
def fake_ai_predict(row):
    # Pretend AI predicts 55% for home team if odds are close
    return 0.55 if row.get("home_team") else 0.45

# Build AI Picks Table
rows = []
for _, row in df.iterrows():
    try:
        price = float(row["price_american"])
    except Exception:
        continue

    offer_decimal = american_to_decimal(price)
    ip = implied_prob_from_american(price)

    ai_prob = fake_ai_predict(row)  # <-- placeholder
    edge = ai_prob - ip

    rows.append({
        "Date/Time": row.get("commence_time", "Unknown"),
        "Sport": row.get("sport_key", "Unknown").upper(),
        "Matchup": f"{row.get('home_team', 'Unknown')} vs {row.get('away_team', 'Unknown')}",
        "Sportsbook": row.get("book", "Unknown"),
        "Odds": price,
        "IP%": f"{ip*100:.1f}%",
        "AI%": f"{ai_prob*100:.1f}%",
        "Edge%": f"{edge*100:.1f}%",
        "Pick": "Home" if ai_prob > 0.5 else "Away"
    })

table = pd.DataFrame(rows)

st.markdown("## 🤖 AI Betting Picks")
st.caption("Experimental machine learning picks — placeholder model for now.")

if table.empty:
    st.info("No AI picks yet.")
else:
    st.dataframe(table, use_container_width=True, hide_index=True)

    # Download option
    csv = table.to_csv(index=False).encode("utf-8")
    st.download_button("Download AI Picks (CSV)", data=csv, file_name="ai_picks.csv", mime="text/csv")
