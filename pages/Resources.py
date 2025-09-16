import streamlit as st
from ui import use_global_style, header

# Set global styles + header once
use_global_style()
header(active="Resources")

# Page config
st.set_page_config(
    page_title="Resources • TruLine Betting",
    page_icon="📚",
    layout="wide"
)

# Page content
st.markdown("## Resources")
st.markdown("### Guides")
st.markdown(
    "- Positive EV Basics\n"
    "- Bankroll Management\n"
    "- Understanding Vig\n"
    "- Kelly Criterion (capped)"
)
st.markdown("### Help Center")
st.info("Support and docs are coming soon. For now, you can reach us via the contact link in the footer.")
