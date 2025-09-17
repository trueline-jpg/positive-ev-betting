from __future__ import annotations
import streamlit as st
from ui import use_global_style, header, footer

# Import page modules
import pages.EV_Finder as ev_finder
import pages.Resources as resources
import pages.Subscription as subscription
import pages.Tools as tools

# --- PAGE CONFIG ---
st.set_page_config(page_title="TruLine Betting", page_icon="📈", layout="wide")

# --- GLOBAL STYLE + NAV ---
use_global_style()
active_page = st.session_state.get("page", "Home")
header(active=active_page)

# --- ROUTER ---
if active_page == "Home":
    st.markdown("## 🏠 Home Page")
    st.write("Hero section, explainer, CTA buttons, etc. (your existing code here).")

elif active_page == "EV Finder":
    ev_finder.run()

elif active_page == "Resources":
    resources.run()

elif active_page == "Subscription":
    subscription.run()

elif active_page == "Tools":
    tools.run()

# --- FOOTER ---
footer()
