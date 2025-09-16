import streamlit as st

def use_global_style():
    st.markdown(
        """
        <style>
        /* Global font */
        html, body, [class*="css"]  {
            font-family: 'Comfortaa', sans-serif;
        }

        /* Background & text */
        .stApp {
            background-color: #ffffff;  /* White background */
            color: #000000;             /* Black text */
        }

        /* Navbar style */
        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
            background-color: #000; /* Black navbar */
        }

        .nav .left {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .nav .right a {
            margin-left: 20px;
            text-decoration: none;
            color: white;
            font-weight: 600;
        }

        .nav .right a:hover {
            color: #ff4b4b; /* red accent */
        }

        .btn-primary {
            background: #ff4b4b;
            color: white !important;
            padding: 6px 16px;
            border-radius: 6px;
            font-weight: 600;
            text-decoration: none;
        }

        .btn-primary:hover {
            background: #e04343;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def header():
    st.markdown(
        """
        <div class="nav">
            <div class="left">
                <img src="assets/logo.png" width="40">
                <span style="color:white; font-size:20px; font-weight:700;">TruLine Betting</span>
            </div>
            <div class="right">
                <a href="/EV_Finder">EV Finder</a>
                <a href="/Tools">Tools</a>
                <a href="/Resources">Resources</a>
                <a href="/Subscription">Subscription</a>
                <a class="btn-primary" href="/Login">Free Trial</a>
                <a href="/Login">Login</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
