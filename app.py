import streamlit as st
from ui import use_global_style, header

# --- PAGE CONFIG ---
st.set_page_config(page_title="TruLine Betting", page_icon="📈", layout="wide")

# --- GLOBAL STYLE + NAV HEADER ---
use_global_style()
header(active="Home")

# --- HERO SECTION ---
col1, col2 = st.columns([7, 5], gap="large")

with col1:
    st.markdown(
        """
        <div class="hero">
            <h1>We scan the lines.<br>You place the bets.</h1>
            <p class="lead">Find rare, high-edge opportunities using fair odds, vig removal, and disciplined bankroll controls.</p>
            <div class="cta-row">
                <a class="btn btn-primary" href="/Subscription" target="_self">Try 7 Days Free</a>
                <a class="btn btn-ghost" href="#how" target="_self">How it works</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.image("assets/logo.png", use_container_width=True)

# --- HOW IT WORKS SECTION ---
st.markdown("---")
st.markdown("## How does Positive EV Betting work?")

st.markdown(
    """
    - **Compute fair odds** by removing the bookmaker’s vig using the market pair.  
    - **Reference price**: Use a sharp book (e.g., Pinnacle) when available; otherwise de-vig the market.  
    - **Find edge**: We surface bets where offered odds exceed our fair odds.  
    - **Stake sizing**: Capped Kelly with a bankroll cap you control.  
    """
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Scan")
    st.write("Millions of odds across books & markets. **Live** and pre-match.")

with col2:
    st.markdown("### Detect Edge")
    st.write("We compute fair probabilities and show EV in real-time.")

with col3:
    st.markdown("### Bet & Track")
    st.write("Use capped Kelly, download opportunities, and track results.")

# --- EXPLORE TOOLS ---
st.markdown("---")
st.markdown("## Explore tools")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### EV Finder")
    st.write("Find high-edge bets across supported books.")
    st.page_link("pages/EV_Finder.py", label="Open")

with col2:
    st.markdown("### Arbitrage")
    st.write("Risk-free pairs (coming soon).")
    st.button("Coming soon", disabled=True, key="coming_soon_arb")

with col3:
    st.markdown("### Parlay Builder")
    st.write("Build smarter parlays (coming soon).")
    st.button("Coming soon", disabled=True, key="coming_soon_parlay")

# --- FOOTER ---
st.markdown("---")
st.markdown("Start your [7-day free trial](/Subscription) — no credit card required for sample data.")
