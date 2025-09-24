import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from ui import use_global_style, header, footer
from ev_utils import (
    american_to_decimal, implied_prob_from_american, edge_decimal,
    kelly_fraction, estimate_true_prob_from_ref
)

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

# --- GLOBAL STYLE + NAV HEADER ---
use_global_style()
header(active="EV Finder")

# Load environment variables
load_dotenv()
provider_name = os.getenv("PROVIDER", "csv")
regions = os.getenv("REGIONS", "us")

# (keep your compute_table + fetch_odds + UI logic here…)

# --- FOOTER ---
footer()
