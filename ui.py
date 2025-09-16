import streamlit as st

def use_global_style():
    st.markdown(
        """
        <style>
        /* Global font and background */
        html, body, [class*="css"]  {
            font-family: 'Comfortaa', sans-serif;
            background-color: #ffffff; /* white background */
            color: #000000; /* black text */
        }

        /* Navigation bar */
        .top-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 24px;
            background-color: #ffffff;
            border-bottom: 1px solid #eee;
        }
        .top-nav .left {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .top-nav .left img {
            height: 32px;
        }
        .top-nav .links a {
            margin: 0 10px;
            text-decoration: none;
            font-weight: 600;
            color: #333;
            opacity: 0.8;
        }
        .top-nav .links a.active {
            color: #e63946; /* red accent */
            opacity: 1;
        }
        .top-nav .right a {
            margin-left: 15px;
            text-decoration: none;
            font-weight: 600;
        }
        .btn-primary {
            padding: 6px 14px;
            border-radius: 6px;
            background-color: #e63946;
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def header(active="Home"):
    """Renders the top navigation bar with active page highlighting"""
    st.markdown(
        f"""
        <div class="top-nav">
            <div class="left">
                <img src="https://raw.githubusercontent.com/trueline-jpg/positive-ev-betting/main/assets/logo.png">
                <span><b>TruLine Betting</b></span>
            </div>
            <div class="links">
                <a href="/" class="{'active' if active=='Home' else ''}">Home</a>
                <a href="/EV_Finder" class="{'active' if active=='EV Finder' else ''}">EV Finder</a>
                <a href="/Tools" class="{'active' if active=='Tools' else ''}">Tools</a>
                <a href="/Resources" class="{'active' if active=='Resources' else ''}">Resources</a>
                <a href="/Subscription" class="{'active' if active=='Subscription' else ''}">Subscription</a>
            </div>
            <div class="right">
                <a class="btn-primary" href="/Subscription">Free Trial</a>
                <a href="#">Login</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
