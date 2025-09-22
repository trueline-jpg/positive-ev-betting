import requests
import os

class OddsAPIProvider:
    def __init__(self, api_key: str, regions="us", markets="h2h", odds_format="american"):
        self.api_key = api_key
        self.base_url = "https://api.the-odds-api.com/v4"
        self.regions = regions
        self.markets = markets
        self.odds_format = odds_format

    def get_sports(self):
        url = f"{self.base_url}/sports/?apiKey={self.api_key}"
        resp = requests.get(url)
        return resp.json() if resp.status_code == 200 else []

    def get_odds(self, sport_key: str):
        url = (f"{self.base_url}/sports/{sport_key}/odds/"
               f"?apiKey={self.api_key}&regions={self.regions}"
               f"&markets={self.markets}&oddsFormat={self.odds_format}")
        resp = requests.get(url)
        return resp.json() if resp.status_code == 200 else []
