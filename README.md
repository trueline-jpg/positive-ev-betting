# Positive EV Betting MVP

An end-to-end minimal app that finds **positive expected value (EV)** bets by comparing sportsbook lines to a sharp reference price and removing the vig.

## Features
- Pull odds from an odds aggregator API (supports OddsAPI/TheOddsAPI style responses).
- Remove vig on 2-way and 3-way markets to estimate fair probabilities.
- Compute **edge/EV%** and **recommended stake** using a capped Kelly fraction.
- Line shop across books, filter by **min edge** and **min hold**.
- Streamlit dashboard to sort and export opportunities to CSV.
- Works **offline** with sample CSV data if you don't have an API key yet.

## Quick Start

### 0) Prereqs
- Python 3.10+ recommended

### 1) Clone / unzip and install deps
```bash
pip install -r requirements.txt
```

### 2) Configure environment
Create a `.env` file in the project root (same folder as this README) with:

```env
PROVIDER=oddsapi           # or 'csv' to use sample file
ODDS_API_KEY=YOUR_KEY_HERE # get from the-odds-api.com or oddsapi.io
REGIONS=us,us2             # regions your key supports; see provider docs
MARKETS=h2h,spreads,totals # supported markets (app filters to h2h by default)
BOOKS=DraftKings,FanDuel,BetMGM,PointsBet # optional, comma-separated
REF_BOOK=Pinnacle          # used as the sharp reference when present
REF_FALLBACK_MARGIN=0.03   # assumed market margin if ref book missing
KELLY_FRACTION=0.25        # Kelly cap (0.25 = quarter Kelly)
MIN_EDGE=0.02              # default minimum edge 2%
REFRESH_SECONDS=60         # auto-refresh interval in app
```

> If you don't have an API key yet, set `PROVIDER=csv` to run with the sample file in `sample_data/sample_odds.csv`.

### 3) Run the app
```bash
streamlit run app.py
```

### 4) Usage Tips
- Start with `MIN_EDGE` around 2–3% and increase as needed.
- Keep stakes sensible: even with edge, variance is real. Quarter Kelly is a good starting point.
- Log your bets and outcomes; refine filters (books/markets that overperform).

## Legal/ToS
Scraping individual sportsbooks may violate terms of service. This app uses odds aggregator APIs. Bet responsibly.
