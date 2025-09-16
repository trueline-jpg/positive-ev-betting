import streamlit as st

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="TruLine Betting",
    layout="wide"
)

# --- CUSTOM STYLING ---
st.markdown(
    """
    <style>
    /* Import Google Font Comfortaa */
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Comfortaa', sans-serif;
    }

    /* Background */
    .stApp {
        background-color: #ffffff; /* White background */
        color: #000000;            /* Black text */
    }

    /* Header */
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background-color: #000000; /* Black header */
        color: #ffffff;
    }
    .header .left {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.3rem;
        font-weight: 700;
    }
    .header img {
        height: 32px;
    }
    .header .right a {
        margin-left: 20px;
        text-decoration: none;
        color: #ffffff;
        font-weight: 600;
    }
    .header .btn {
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 600;
    }
    .header .btn-primary {
        background-color: #ff4b4b; /* Red button */
        color: #ffffff;
    }
    .header .btn-primary:hover {
        background-color: #e04343;
    }

    /* Hero Section */
    .hero {
        text-align: center;
        padding: 3rem 1rem;
    }
    .hero h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .hero p {
        font-size: 1.1rem;
        color: #333333;
    }
    .hero .cta-row {
        margin-top: 1.5rem;
    }
    .hero .btn {
        margin: 0 8px;
        padding: 10px 18px;
        border-radius: 6px;
        font-weight: 600;
    }
    .hero .btn-primary {
        background-color: #ff4b4b;
        color: #fff;
    }
    .hero .btn-secondary {
        background-color: #000;
        color: #fff;
    }
    .hero .btn-secondary:hover {
        background-color: #333;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- HEADER ---
st.markdown(
    """
    <div class="header">
        <div class="left">
            <img src="assets/logo.png" alt="TruLine Logo">
            TruLine Betting
        </div>
        <div class="right">
            <a href="#">Tools</a>
            <a href="#">Resources</a>
            <a href="#">Subscription</a>
            <a class="btn btn-primary" href="#">Free Trial</a>
            <a class="btn btn-secondary" href="#">Login</a>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# --- HERO SECTION ---
st.markdown(
    """
    <div class="hero">
        <h1>We scan the lines. You place the bets.</h1>
        <p>Find rare, high-edge opportunities using fair odds, vig removal, and disciplined bankroll controls.</p>
        <div class="cta-row">
            <a class="btn btn-primary" href="#">Try 7 Days Free</a>
            <a class="btn btn-secondary" href="#">How it works</a>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# --- EXPLANATION SECTION ---
st.markdown(
    """
    <h2>How does Positive EV Betting work?</h2>
    <ul>
        <li><b>Compute fair odds</b> by removing the bookmaker’s vig using the market pair.</li>
        <li><b>Reference price</b>: Use a sharp book (e.g., Pinnacle) when available; otherwise de-vig the market.</li>
        <li><b>Find edge</b>: We surface bets where offered odds exceed our fair odds.</li>
        <li><b>Stake sizing</b>: Capped Kelly with a bankroll cap you control.</li>
    </ul>
    """,
    unsafe_allow_html=True
)
