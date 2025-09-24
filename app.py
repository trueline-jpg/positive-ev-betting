from __future__ import annotations
import streamlit as st
from ui import use_global_style, header, footer

# --- PAGE CONFIG ---
st.set_page_config(page_title="TruLine Betting", page_icon="📈", layout="wide")

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

# --- GLOBAL STYLE + HEADER ---
use_global_style()
header(active="Home")

# --- HERO SECTION ---
col1, col2 = st.columns([7, 5], gap="large")

with col1:
    st.markdown(
        """
        <div class="hero">
            <h1>We scan the lines.<br>You place the bets.</h1>
            <p class="lead">Find high-edge opportunities using fair odds, vig removal, and bankroll controls.</p>
            <div class="cta-row">
                <a class="btn btn-primary" href="/Subscription">Try 7 Days Free</a>
                <a class="btn btn-ghost" href="#how">How it works</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.image("assets/logo.png", use_container_width=True)

# --- HOW IT WORKS ---
st.markdown("---")
st.markdown("## How does Positive EV Betting work?")
st.markdown(
    """
    - **Compute fair odds** by removing the bookmaker’s vig.  
    - **Reference price**: Use a sharp book (like Pinnacle) when available.  
    - **Find edge**: Bets where offered odds exceed fair odds.  
    - **Stake sizing**: Uses capped Kelly.  
    """
)

# --- EXPLORE TOOLS ---
st.markdown("---")
st.markdown("## Explore Tools")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### EV Finder")
    st.page_link("pages/EV_Finder.py", label="Open")

with col2:
    st.markdown("### Arbitrage (coming soon)")
    st.button("Coming soon", disabled=True)

with col3:
    st.markdown("### Parlay Builder (coming soon)")
    st.button("Coming soon", disabled=True)

# --- FOOTER ---
footer()
