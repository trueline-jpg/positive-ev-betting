import streamlit as st
from ui import use_global_style, header

st.set_page_config(page_title="Tools • TruLine Betting", page_icon="🛠️", layout="wide")

st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"], section[data-testid="stSidebar"] {display: none;}
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
        <div class="card"><h4>EV Finder</h4><p>Find positive-edge bets.</p></div>
        <div class="card"><h4>Arbitrage</h4><p>Coming soon.</p></div>
        <div class="card"><h4>Parlay Builder</h4><p>Coming soon.</p></div>
    </div>
    """,
    unsafe_allow_html=True,
)
