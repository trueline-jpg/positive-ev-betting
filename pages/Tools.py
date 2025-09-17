import streamlit as st
from ui import use_global_style, header

# --- PAGE CONFIG ---
st.set_page_config(page_title="Tools • TruLine Betting", page_icon="🛠️", layout="wide")

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
header(active="Tools")

# --- PAGE CONTENT ---
st.markdown("## 🛠️ Tools")

# Tools grid layout
st.markdown(
    """
    <div class="grid">
        <div class="card">
            <h4>📈 EV Finder</h4>
            <p>Find positive-edge bets across your books.</p>
            <a class="btn btn-small btn-primary" href="/EV_Finder">Open</a>
        </div>
        
        <div class="card">
            <h4>🔄 Arbitrage</h4>
            <p>Risk-free pairs (coming soon).</p>
            <button class="btn btn-small" disabled>Coming soon</button>
        </div>
        
        <div class="card">
            <h4>🎯 Parlay Builder</h4>
            <p>Build smarter parlays (coming soon).</p>
            <button class="btn btn-small" disabled>Coming soon</button>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
