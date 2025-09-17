import streamlit as st
import textwrap

def _html(s: str):
    """Render raw HTML/CSS with indentation removed so Markdown doesn't make code blocks."""
    st.markdown(textwrap.dedent(s), unsafe_allow_html=True)

def use_global_style():
    _html("""
    <style>
      :root { --primary:#e63946; }

      /* Hide Streamlit chrome + sidebar globally */
      header[data-testid="stHeader"] { display:none; }
      section[data-testid="stSidebar"] { display:none !important; }
      [data-testid="stSidebarNav"] { display:none !important; }
      div.block-container { padding-top: 1rem; }

      /* Base font/colors */
      body {
        font-family: 'Comfortaa', sans-serif;
        background:#fff; color:#000;
      }

      /* Navbar */
      .navbar {
        display:flex; justify-content:space-between; align-items:center;
        padding:1rem 2rem; border-bottom:1px solid #ddd;
      }
      .navbar-left {
        display:flex; align-items:center; gap:.5rem;
        font-weight:700; font-size:1.1rem;
      }
      .navbar-left img { width:40px; height:40px; }

      .navbar-center a {
        margin:0 1rem; text-decoration:none; font-weight:600; color:#000;
      }
      .navbar-center a.active { color:var(--primary); }

      .navbar-right { display:flex; align-items:center; gap:1rem; }
      .btn-login { font-weight:600; color:#000; text-decoration:none; }

      .btn-primary {
        background:var(--primary); color:#fff !important;
        padding:.6rem 1.2rem; border-radius:8px; font-weight:600; text-decoration:none;
      }
      .btn-primary:hover { background:#c92c3c; }

      /* Cards / grid (used in Tools/Subscription) */
      .grid {
        display:grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap:18px;
      }
      .card {
        background:#fff; border:1px solid #e6e6e6; border-radius:14px; padding:18px;
      }

      /* Footer */
      .footer {
        margin-top:3rem; padding:2rem; background:#111; color:#f5f5f5;
        text-align:center; border-top:1px solid #333;
      }
      .footer a { margin:0 1rem; color:var(--primary); text-decoration:none; font-weight:600; }
      .footer a:hover { text-decoration:underline; }
    </style>

    <link href="https://fonts.googleapis.com/css2?family=Comfortaa:wght@400;600;700&display=swap" rel="stylesheet">
    """)

def header(active: str = "Home"):
    _html(f"""
    <div class="navbar">
      <!-- Left -->
      <div class="navbar-left">
        <img src="https://raw.githubusercontent.com/trueline-jpg/positive-ev-betting/main/assets/logo.png" alt="TruLine"/>
        TruLine Betting
      </div>

      <!-- Center -->
      <div class="navbar-center">
        <a href="/" class="{'active' if active=='Home' else ''}">Home</a>
        <a href="/EV_Finder" class="{'active' if active=='EV Finder' else ''}">EV Finder</a>
        <a href="/Tools" class="{'active' if active=='Tools' else ''}">Tools</a>
        <a href="/Resources" class="{'active' if active=='Resources' else ''}">Resources</a>
        <a href="/Subscription" class="{'active' if active=='Subscription' else ''}">Subscription</a>
      </div>

      <!-- Right -->
      <div class="navbar-right">
        <a href="/Subscription" class="btn-login">Login</a>
        <a href="/Subscription" class="btn-primary">Try for Free</a>
      </div>
    </div>
    """)

def footer():
    _html("""
    <div class="footer">
      <p>© 2025 TruLine Betting</p>
      <p>
        <a href="mailto:contact@trulinebetting.com">Contact</a> |
        <a href="https://discord.com" target="_blank">Discord</a> |
        <a href="https://youtube.com" target="_blank">YouTube</a> |
        <a href="https://tiktok.com" target="_blank">TikTok</a>
      </p>
    </div>
    """)
