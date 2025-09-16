from __future__ import annotations
import streamlit as st
from ui import use_global_style, header
use_global_style()
header()
from pathlib import Path

st.set_page_config(page_title="TruLine Betting", page_icon="📈", layout="wide")

use_global_style()  # font + theme + css
header(active="Home")  # top nav bar

# --- HERO ---------------------------------------------------------------------
col1, col2 = st.columns([7, 5], gap="large")

with col1:
    st.markdown(
        """
        <div class='hero'>
          <div class='eyebrow'>TruLine <span class='thin'>Betting</span><span class='tag'>POSITIVE EV</span></div>
          <h1>We scan the lines.<br/>You place the bets.</h1>
          <p class='lead'>Find rare, high-edge opportunities using fair odds, vig removal, and disciplined bankroll controls.</p>
          <div class='cta-row'>
            <a class='btn btn-primary' href='/Subscription'>Try 7 Days Free</a>
            <a class='btn btn-ghost' href='#how'>How it works</a>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    # Optional: hero watermark logo (kept subtle)
    if Path("assets/logo.png").exists():
        st.image("assets/logo.png", use_column_width=True)

# --- HOW IT WORKS -------------------------------------------------------------
st.markdown("<a id='how'></a>", unsafe_allow_html=True)
st.markdown("## How does Positive EV Betting work?")
st.markdown(
    """
- **Compute fair odds** by removing the bookmaker’s vig using the market pair.  
- **Reference price**: Use a sharp book (e.g., Pinnacle) when available; otherwise de-vig the market.  
- **Find edge**: We surface bets where offered odds **exceed** our fair odds.  
- **Stake sizing**: Capped Kelly with a bankroll cap you control.  
    """.strip()
)

colA, colB, colC = st.columns(3)
with colA:
    st.markdown("### Scan\nMillions of odds across books & markets.\n\n`Live` and pre-match.")
with colB:
    st.markdown("### Detect Edge\nWe compute fair probabilities and show EV in real-time.")
with colC:
    st.markdown("### Bet & Track\nUse capped Kelly, download opportunities, and track results.")

st.divider()

# --- QUICK LINKS / CARDS ------------------------------------------------------
st.markdown("### Explore tools")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("<div class='card'><h4>EV Finder</h4><p>Find high-edge bets across supported books.</p><a class='btn btn-small' href='/EV_Finder'>Open</a></div>", unsafe_allow_html=True)
with c2:
    st.markdown("<div class='card'><h4>Arbitrage</h4><p>Risk-free pairs (coming soon).</p><button class='btn btn-small' disabled>Coming soon</button></div>", unsafe_allow_html=True)
with c3:
    st.markdown("<div class='card'><h4>Parlay Builder</h4><p>Build smarter parlays (coming soon).</p><button class='btn btn-small' disabled>Coming soon</button></div>", unsafe_allow_html=True)

st.divider()
st.markdown(
    """
<div class='center'>
  <a class='btn btn-primary' href='/Subscription'>Start your 7-day free trial</a>
  <span class='muted'>No credit card required for sample data.</span>
</div>
""",
    unsafe_allow_html=True,
)
