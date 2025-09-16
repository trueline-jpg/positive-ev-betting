import streamlit as st

def use_global_style():
    st.markdown(
        """
        <style>
        body {
            font-family: 'Comfortaa', sans-serif;
            background-color: white;
            color: black;
        }
        .stButton>button {
            background-color: #e63946;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
        }
        .stButton>button:hover {
            background-color: #c92c3c;
        }
        .navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
            border-bottom: 1px solid #ddd;
        }
        .nav-links a {
            margin: 0 1rem;
            text-decoration: none;
            font-weight: 600;
            color: black;
        }
        .nav-links a.active {
            color: #e63946;
        }
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Comfortaa:wght@400;600;700&display=swap" rel="stylesheet">
        """,
        unsafe_allow_html=True,
    )

def header(active="Home"):
    st.markdown(
        f"""
        <div class="navbar">
            <div>
                <img src="https://raw.githubusercontent.com/trueline-jpg/positive-ev-betting/main/assets/logo.png" width="40"/>
                <strong> TruLine Betting </strong>
            </div>
            <div class="nav-links">
                <a href="/" class="{'active' if active=='Home' else ''}">Home</a>
                <a href="/EV_Finder" class="{'active' if active=='EV Finder' else ''}">EV Finder</a>
                <a href="/Tools" class="{'active' if active=='Tools' else ''}">Tools</a>
                <a href="/Resources" class="{'active' if active=='Resources' else ''}">Resources</a>
                <a href="/Subscription" class="{'active' if active=='Subscription' else ''}">Subscription</a>
                <a href="/Subscription" class="btn btn-primary">Free Trial</a>
                <a href="/Subscription">Login</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
