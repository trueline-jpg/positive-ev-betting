import streamlit as st
from ui import use_global_style, header

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Resources • TruLine Betting",
    page_icon="📚",
    layout="wide"
)

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
header(active="Resources")

# --- PAGE CONTENT ---
st.markdown("## 📚 Resources")
st.markdown("### 📖 Guides")
st.markdown(
    """
    - Positive EV Basics  
    - Bankroll Management  
    - Understanding Vig  
    - Kelly Criterion (capped)  
    """
)

st.markdown("### ❓ Help Center")
st.info("Support and docs are coming soon. For now, you can reach us via the contact link in the footer.")
