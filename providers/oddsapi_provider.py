from __future__ import annotations
import os, time, requests
from typing import Dict, List, Any

class OddsAPIProvider:
    """Thin wrapper for TheOddsAPI / oddsapi-style endpoints.
    Docs examples:
      - https://the-odds-api.com/liveapi/guides/v4/
    """
    BASE_URL = "https://api.the-odds-api.com/v4"
    def __init__(self, api_key: str, regions: str = "us", markets: str = "h2h", odds_format: str = "american", date_format: str = "iso"):
        self.api_key = api_key
        self.regions = regions
        self.markets = markets
        self.odds_format = odds_format
        self.date_format = date_format

    def get_sports(self) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/sports?apiKey={self.api_key}"
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        return r.json()

    def get_odds(self, sport_key: str) -> List[Dict[str, Any]]:
        params = {
            "apiKey": self.api_key,
            "regions": self.regions,
            "markets": self.markets,
            "oddsFormat": self.odds_format,
            "dateFormat": self.date_format,
        }
        url = f"{self.BASE_URL}/sports/{sport_key}/odds"
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data
