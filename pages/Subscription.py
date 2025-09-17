import streamlit as st
from ui import use_global_style, header, footer

st.set_page_config(page_title="Subscription • TruLine Betting", page_icon="💳", layout="wide")

use_global_style()
header(active="Subscription")

st.markdown("## Plans & Free Trial")

c1, c2 = st.columns(2)

with c1:
    st.markdown(
        """
        <div class="plan card">
            <h3>Gold</h3>
            <div class="price">$6.60<span>/day</span></div>
            <ul>
                <li>EV Finder</li>
                <li>Real-time scanning</li>
                <li>Download CSV</li>
            </ul>
            <a class="btn btn-primary" href="#">Try 7 days free</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        """
        <div class="plan card">
            <h3>Platinum</h3>
            <div class="price">Apply</div>
            <ul>
                <li>Everything in Gold</li>
                <li>Priority support</li>
                <li>Multi-market live scanning</li>
            </ul>
            <button class="btn btn-ghost" disabled>Join waitlist</button>
        </div>
        """,
        unsafe_allow_html=True,
    )

footer()
