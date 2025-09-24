import streamlit as st
from ui import use_global_style, header, footer

st.set_page_config(page_title="Tools • TruLine Betting", page_icon="🛠️", layout="wide")

use_global_style()
header(active="Tools")

st.markdown("## Tools")

st.markdown(
    """
    <div class="grid">
        <div class="card">
            <h4>EV Finder</h4>
            <a class="btn btn-small" href="/EV_Finder">Open</a>
        </div>
        <div class="card">
            <h4>Arbitrage</h4>
            <button class="btn btn-small" disabled>Coming soon</button>
        </div>
        <div class="card">
            <h4>Parlay Builder</h4>
            <button class="btn btn-small" disabled>Coming soon</button>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

footer()
