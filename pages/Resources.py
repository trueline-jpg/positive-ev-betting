import streamlit as st
from ui import use_global_style, header

st.set_page_config(page_title="Resources • TruLine Betting", page_icon="📚", layout="wide")

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
header(active="Resources")

st.markdown("## Resources")
st.markdown("### Guides")
st.markdown(
    "- Positive EV Basics\n"
    "- Bankroll Management\n"
    "- Understanding Vig\n"
    "- Kelly Criterion (capped)"
)
st.markdown("### Help Center")
st.info("Support and docs are coming soon.")
