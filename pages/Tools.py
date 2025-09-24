import streamlit as st
from ui import use_global_style, header

st.set_page_config(page_title="Tools • TruLine Betting", page_icon="🛠️", layout="wide")

st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        section[data-testid="stSidebar"] {display: none !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

use_global_style()
header(active="Tools")

st.markdown("## Tools")

st.markdown(
    """
    <div class="grid">
        <div class="card">
            <h4>EV Finder</h4>
            <p>Find positive-edge bets across your books.</p>
            <a class="btn btn-small" href="/EV_Finder" target="_self">Open</a>
        </div>
        
        <div class="card">
            <h4>Arbitrage</h4>
            <p>Risk-free pairs (coming soon).</p>
            <button class="btn btn-small" disabled>Coming soon</button>
        </div>
        
        <div class="card">
            <h4>Parlay Builder</h4>
            <p>Build smarter parlays (coming soon).</p>
            <button class="btn btn-small" disabled>Coming soon</button>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
