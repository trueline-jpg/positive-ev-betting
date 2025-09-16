import streamlit as st
from pathlib import Path

def use_global_style():
    # Inject Google Comfortaa + global CSS (light theme, red accents)
    st.markdown(
        """
<link href="https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
:root{
  --bg: #ffffff;
  --text:#0c0c0c;
  --muted:#6b7280;
  --primary:#ef4444; /* red */
  --surface:#f7f7f8;
  --border:#e5e7eb;
}
html, body, [data-testid="stAppViewContainer"], .stApp {
  background: var(--bg);
  color: var(--text);
  font-family: 'Comfortaa', system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
}
a { color: var(--text); text-decoration: none; }
a:hover { opacity:.85; }

header.nav {
  position: sticky; top:0; z-index:100;
  background: var(--bg); border-bottom:1px solid var(--border);
  padding: 14px 8px; margin-bottom: 8px;
}
.nav .row { display:flex; gap:16px; align-items:center; justify-content:space-between; }
.nav .left, .nav .right { display:flex; gap:22px; align-items:center; }
.logo-wrap { display:flex; gap:10px; align-items:center; font-weight:700; }
.logo-wrap img { height:26px; width:auto; }

.nav a.item { opacity:.9; }
.nav a.item.active { color: var(--primary); font-weight:700; }

.btn { display:inline-block; border:1px solid var(--border); padding:10px 14px; border-radius:8px; font-weight:600; }
.btn.btn-primary { background: var(--primary); color:#fff; border-color: var(--primary); }
.btn.btn-ghost { background: transparent; }
.btn.btn-small { padding:8px 12px; font-size: 0.9rem; }

.hero .eyebrow { color: var(--muted); font-weight:600; letter-spacing:.02em; }
.hero .thin{font-weight:300;}
.hero .tag{ margin-left:10px; font-size:.78rem; color:#fff; background:#111; padding:2px 8px; border-radius:999px;}
.hero h1{ font-size: 3rem; line-height:1.1; margin:.5rem 0 1rem; }
.hero .lead{ color: var(--muted); max-width: 720px; }
.cta-row { display:flex; gap:12px; margin-top:18px; }

.card{ background: var(--surface); border:1px solid var(--border); border-radius:14px; padding:18px; }
.grid{ display:grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap:18px; }
.center{ text-align:center; }
.muted{ color: var(--muted); margin-left:10px; }

.plan .price{ font-size:2rem; font-weight:700; }
.plan .price span{ font-size:1rem; font-weight:400; color:var(--muted); margin-left:6px; }
</style>
""",
        unsafe_allow_html=True,
    )

def header(active: str = "Home"):
    # Left side: Logo + nav
    left = """
    <div class='left'>
      <a class='logo-wrap' href="/"><img src="/app/static/logo" onerror="this.style.display='none'"/><span>TruLine Betting</span></a>
      <a class='item {h}' href="/">Home</a>
      <a class='item {t}' href="/Tools">Tools</a>
      <a class='item {r}' href="/Resources">Resources</a>
      <a class='item {s}' href="/Subscription">Subscription</a>
    </div>
    """.format(
        h="active" if active=="Home" else "",
        t="active" if active=="Tools" else "",
        r="active" if active=="Resources" else "",
        s="active" if active=="Subscription" else "",
    )

    # Right side: CTAs
    right = """
    <div class='right'>
      <a class='item' href="/Subscription">Free Trial</a>
      <a class='btn btn-primary' href="#login">Login</a>
    </div>
    """

    st.markdown(f"<header class='nav'><div class='row'>{left}{right}</div></header>", unsafe_allow_html=True)

    # Lightweight inline “Login” (email/password + social icons – visuals only)
    with st.container():
        if st.query_params.get("login") == "1":
            st.subheader("Login")
            with st.form("login_form"):
                c1, c2 = st.columns(2)
                email = c1.text_input("Email or Username")
                pwd = c2.text_input("Password", type="password")
                st.markdown("Or continue with:")
                c3, c4, c5 = st.columns(3)
                c3.button("Sign in with Google", use_container_width=True)
                c4.button("Sign in with Apple", use_container_width=True)
                c5.button("Sign in with Phone", use_container_width=True)
                submitted = st.form_submit_button("Sign in")
                if submitted:
                    st.success("Sign-in simulated. Connect your auth later.")
