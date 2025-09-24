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

        /* Navbar */
        .navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
            border-bottom: 1px solid #ddd;
        }

        /* Left logo */
        .navbar-left img {
            width: 70px;  /* bigger logo */
            height: auto;
        }

        /* Center nav */
        .navbar-center a {
            margin: 0 1rem;
            text-decoration: none;
            font-weight: 600;
            color: black;
        }

        .navbar-center a.active {
            color: #e63946;
        }

        /* Right side */
        .navbar-right {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .btn-login {
            font-weight: 600;
            color: black;
            text-decoration: none;
        }

        .btn-primary {
            background-color: #e63946;
            color: white !important;
            padding: 0.6rem 1.2rem;
            border-radius: 8px;
            font-weight: 600;
            text-decoration: none;
        }

        .btn-primary:hover {
            background-color: #c92c3c;
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
            <!-- Left -->
            <div class="navbar-left">
                <img src="https://raw.githubusercontent.com/trueline-jpg/positive-ev-betting/main/assets/logo.png"/>
            </div>

            <!-- Center -->
            <div class="navbar-center">
                <a href="/" target="_self" class="{'active' if active=='Home' else ''}">Home</a>
                <a href="/EV_Finder" target="_self" class="{'active' if active=='EV Finder' else ''}">EV Finder</a>
                <a href="/Tools" target="_self" class="{'active' if active=='Tools' else ''}">Tools</a>
                <a href="/Resources" target="_self" class="{'active' if active=='Resources' else ''}">Resources</a>
                <a href="/Subscription" target="_self" class="{'active' if active=='Subscription' else ''}">Subscription</a>
            </div>

            <!-- Right -->
            <div class="navbar-right">
                <a href="/Subscription" target="_self" class="btn-login">Login</a>
                <a href="/Subscription" target="_self" class="btn-primary">Try for Free</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
