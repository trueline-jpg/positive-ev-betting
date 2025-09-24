import streamlit as st
from ui import use_global_style, header

st.set_page_config(page_title="Resources • TruLine Betting", page_icon="📚", layout="wide")

# Hide sidebar
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"], section[data-testid="stSidebar"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True,
)

use_global_style()
header(active="Resources")

st.markdown("## Resources")
st.markdown("### Guides")
st.markdown("- Positive EV Basics\n- Bankroll Management\n- Understanding Vig\n- Kelly Criterion")
st.info("Support and docs coming soon.")
