import streamlit as st
import textwrap

def use_global_style():
    st.markdown(
        """
<style>
:root { --primary:#e63946; }

body { font-family:'Comfortaa', sans-serif; background:#fff; color:#000; }

/* Navbar */
.navbar{
  position: sticky; top:0; z-index:999;
  display:flex; justify-content:space-between; align-items:center;
  padding:1rem 2rem; border-bottom:1px solid #ddd; background:#fff;
}

/* Left: logo + name */
.navbar-left{ display:flex; align-items:center; gap:.5rem; font-weight:700; font-size:1.1rem; }
.navbar-left img{ width:40px; height:40px; }

/* Center: links */
.navbar-center a{ margin:0 1rem; text-decoration:none; font-weight:600; color:#000; }
.navbar-center a.active{ color:var(--primary); }

/* Right: buttons */
.navbar-right{ display:flex; align-items:center; gap:1rem; }
.btn-login{ font-weight:600; color:#000; text-decoration:none; }
.btn-primary{
  background:var(--primary); color:#fff !important; padding:.6rem 1.2rem;
  border-radius:8px; font-weight:600; text-decoration:none;
}
.btn-primary:hover{ filter:brightness(.9); }

/* Footer */
.footer{
  margin-top:3rem; padding:2rem; background:#111; color:#f5f5f5;
  text-align:center; border-top:1px solid #333;
}
.footer a{ margin:0 1rem; color:var(--primary); text-decoration:none; font-weight:600; }
.footer a:hover{ text-decoration:underline; }
</style>

<link href="https://fonts.googleapis.com/css2?family=Comfortaa:wght@400;600;700&display=swap" rel="stylesheet">
        """,
        unsafe_allow_html=True,
    )

def header(active="Home"):
    nav_html = textwrap.dedent(f"""\
    <div class="navbar">
      <div class="navbar-left">
        <img src="https://raw.githubusercontent.com/trueline-jpg/positive-ev-betting/main/assets/logo.png" alt="TruLine logo"/>
        TruLine Betting
      </div>

      <div class="navbar-center">
        <a href="/" class="{ 'active' if active=='Home' else ''}">Home</a>
        <a href="/EV_Finder" class="{ 'active' if active=='EV Finder' else ''}">EV Finder</a>
        <a href="/Tools" class="{ 'active' if active=='Tools' else ''}">Tools</a>
        <a href="/Resources" class="{ 'active' if active=='Resources' else ''}">Resources</a>
        <a href="/Subscription" class="{ 'active' if active=='Subscription' else ''}">Subscription</a>
      </div>

      <div class="navbar-right">
        <a href="/Subscription" class="btn-login">Login</a>
        <a href="/Subscription" class="btn-primary">Try for Free</a>
      </div>
    </div>
    """)
    st.markdown(nav_html, unsafe_allow_html=True)

def footer():
    st.markdown(
        textwrap.dedent("""\
        <div class="footer">
          <p>© 2025 TruLine Betting</p>
          <p>
            <a href="mailto:contact@trulinebetting.com">Contact</a> |
            <a href="https://discord.com" target="_blank">Discord</a> |
            <a href="https://youtube.com" target="_blank">YouTube</a> |
            <a href="https://tiktok.com" target="_blank">TikTok</a>
          </p>
        </div>
        """),
        unsafe_allow_html=True,
    )
