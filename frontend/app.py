"""
AI Code Reviewer - Streamlit Frontend
Complete multi-page application
"""

import streamlit as st
import requests
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

import os

# Check environment variable first, then st.secrets, fallback to localhost
API_BASE = os.getenv("API_BASE_URL")
if not API_BASE:
    try:
        API_BASE = st.secrets.get("API_BASE_URL", "http://localhost:8000/api")
    except Exception:
        API_BASE = "http://localhost:8000/api"


st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────

def load_css():
    st.markdown("""
    <style>
    /* ── Global Reset & Base ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── App Background ── */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        color: #0f172a;
    }

    /* ── Hide Streamlit Branding ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {visibility: hidden;}
    header {
        background: transparent !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f1f5f9 100%);
        border-right: 1px solid #e2e8f0;
    }

    /* ── Score Cards ── */
    .score-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 8px 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .score-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
    }
    .score-value {
        font-size: 3rem;
        font-weight: 700;
        line-height: 1;
        margin: 8px 0;
    }
    .score-label {
        font-size: 0.85rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .score-excellent { color: #10b981; }
    .score-good      { color: #3b82f6; }
    .score-fair      { color: #f59e0b; }
    .score-poor      { color: #ef4444; }

    /* ── Issue Cards ── */
    .issue-card {
        border-radius: 10px;
        padding: 16px 20px;
        margin: 10px 0;
        border-left: 4px solid;
        position: relative;
    }
    .issue-high   { border-left-color: #ef4444; background: #fef2f2; color: #b91c1c; }
    .issue-medium { border-left-color: #f59e0b; background: #fffbeb; color: #b45309; }
    .issue-low    { border-left-color: #10b981; background: #f0fdf4; color: #047857; }

    .severity-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-high   { background: #fee2e2; color: #ef4444; border: 1px solid #fca5a5; }
    .badge-medium { background: #fef3c7; color: #d97706; border: 1px solid #fcd34d; }
    .badge-low    { background: #d1fae5; color: #059669; border: 1px solid #6ee7b7; }

    .category-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        background: #f1f5f9;
        color: #2563eb;
        border: 1px solid #e2e8f0;
        margin-left: 8px;
    }

    /* ── Code Block ── */
    .code-container {
        background: #0f172a;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        overflow-x: auto;
        max-height: 400px;
        overflow-y: auto;
    }

    /* ── Section Headers ── */
    .section-header {
        color: #0f172a;
        font-size: 1.2rem;
        font-weight: 600;
        padding: 12px 0 8px 0;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 16px;
    }

    /* ── Metric Cards ── */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }
    .metric-number {
        font-size: 2rem;
        font-weight: 700;
        color: #2563eb;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 4px;
    }

    /* ── Hero Banner ── */
    .hero-banner {
        background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 32px;
        text-align: center;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #2563eb, #10b981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero-subtitle {
        color: #64748b;
        font-size: 1.1rem;
        margin-top: 8px;
    }

    /* ── Buttons ── */
    .stButton > button, .stFormSubmitButton > button {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.2s ease;
        width: 100%;
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover {
        background: linear-gradient(135deg, #059669, #047857);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: #f1f5f9;
        border-radius: 10px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #64748b;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: #ffffff !important;
        color: #0f172a !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: #ffffff;
        border-radius: 8px;
        color: #0f172a;
        border: 1px solid #e2e8f0;
    }

    /* ── Auth Forms ── */
    .auth-container {
        max-width: 400px;
        margin: 0 auto;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 32px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    /* ── Spinner ── */
    .stSpinner > div {
        border-top-color: #2563eb !important;
    }

    /* ── Alert boxes ── */
    .alert-success {
        background: #ecfdf5;
        border: 1px solid #10b981;
        border-radius: 8px;
        padding: 12px 16px;
        color: #065f46;
    }
    .alert-error {
        background: #fef2f2;
        border: 1px solid #ef4444;
        border-radius: 8px;
        padding: 12px 16px;
        color: #991b1b;
    }

    /* ── History Table ── */
    .history-row {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 6px 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }
    </style>
    """, unsafe_allow_html=True)


# ─── API Helpers ───────────────────────────────────────────────────────────────

def api_call(method: str, endpoint: str, data: dict = None, token: str = None) -> tuple:
    """Make API calls and return (data, error)"""
    url = f"{API_BASE}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=120)
        elif method == "POST":
            r = requests.post(url, headers=headers, json=data, timeout=120)
        elif method == "DELETE":
            r = requests.delete(url, headers=headers, timeout=30)

        if r.status_code in [200, 201]:
            return r.json(), None
        else:
            try:
                err = r.json().get("detail", "Unknown error")
            except:
                err = f"HTTP {r.status_code}"
            return None, err
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to backend. Is the API server running?"
    except requests.exceptions.Timeout:
        return None, "Request timed out. The AI is taking too long."
    except Exception as e:
        return None, str(e)


# ─── Score Helpers ─────────────────────────────────────────────────────────────

def score_class(score: float) -> str:
    if score >= 85: return "score-excellent"
    if score >= 70: return "score-good"
    if score >= 50: return "score-fair"
    return "score-poor"


def score_emoji(score: float) -> str:
    return ""


def render_score_card(label: str, score: float, icon: str):
    css_class = score_class(score)
    st.markdown(f"""
    <div class="score-card">
        <div style="font-size:1.8rem;">{icon}</div>
        <div class="score-value {css_class}">{score:.0f}</div>
        <div class="score-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def render_gauge_chart(score: float, title: str):
    color = "#10b981" if score >= 85 else "#3b82f6" if score >= 70 else "#f59e0b" if score >= 50 else "#ef4444"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": title, "font": {"color": "#0f172a", "size": 14}},
        number={"font": {"color": color, "size": 36}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#64748b"},
            "bar": {"color": color},
            "bgcolor": "#f1f5f9",
            "bordercolor": "#e2e8f0",
            "steps": [
                {"range": [0, 50], "color": "#fee2e2"},
                {"range": [50, 70], "color": "#fef3c7"},
                {"range": [70, 85], "color": "#dbeafe"},
                {"range": [85, 100], "color": "#d1fae5"},
            ],
        }
    ))
    fig.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font={"color": "#0f172a"},
        height=200,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


# ─── Session State ──────────────────────────────────────────────────────────────

def init_session():
    defaults = {
        "logged_in": False,
        "token": None,
        "username": None,
        "user_id": None,
        "review_result": None,
        "page": "review"
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ─── Auth Pages ───────────────────────────────────────────────────────────────

def page_login():
    import os
    import base64
    
    # Read logo SVG
    logo_svg = ""
    logo_path = r"c:\AI_Code_Reviewer\frontend\assets\logo.svg"
    if os.path.exists(logo_path):
        try:
            with open(logo_path, "r", encoding="utf-8") as f:
                logo_svg = f.read()
        except Exception:
            pass
            
    # Fallback logo if file read fails
    if not logo_svg:
        logo_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="60" height="60"><rect width="128" height="128" rx="20" fill="#10b981"/></svg>"""

    # Read preview mockup image in base64
    img_base64 = ""
    img_path = r"c:\AI_Code_Reviewer\frontend\assets\ide_preview.png"
    if os.path.exists(img_path):
        try:
            with open(img_path, "rb") as image_file:
                img_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception:
            pass

    # Track auth mode in session state
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    # Define CSS styles for the cover page
    login_css = """
    <style>
    /* ── Hide default Streamlit navigation, footer, header ── */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    header, footer {
        display: none !important;
        visibility: hidden !important;
    }
    .stAppDeployButton {
        display: none !important;
    }
    
    /* ── Main viewport reset ── */
    [data-testid="stAppViewContainer"] {
        background-color: #ffffff !important;
    }
    
    /* Center the main container block and make it wide */
    .main .block-container {
        max-width: 1200px !important;
        padding-top: 3rem !important;
        padding-bottom: 2rem !important;
        margin: 0 auto !important;
    }

    /* ── Top and Right purple border bars ── */
    .top-accent-bar {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 10px;
        background-color: #7c3aed; /* Purple */
        z-index: 999999;
    }
    .right-accent-bar {
        position: fixed;
        top: 0;
        right: 0;
        width: 10px;
        height: 100vh;
        background-color: #7c3aed; /* Purple */
        z-index: 999999;
    }
    
    /* ── Logo & Title alignment ── */
    .logo-cluster-container {
        position: relative;
        width: 160px;
        height: 110px;
        margin: 0 auto;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .main-logo-wrapper {
        z-index: 10;
    }
    .main-logo-wrapper svg {
        width: 60px;
        height: 60px;
    }
    .logo-bubble {
        position: absolute;
        background-color: #ffffff;
        border: 1.5px solid #e2e8f0;
        border-radius: 8px;
        padding: 4px 8px;
        font-size: 0.75rem;
        font-weight: 600;
        color: #64748b;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        font-family: 'JetBrains Mono', monospace;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .bubble-1 { top: 25px; left: 10px; color: #a855f7; background-color: #faf5ff; }
    .bubble-2 { top: 10px; left: 65px; color: #10b981; background-color: #ecfdf5; }
    .bubble-3 { top: 25px; right: 10px; color: #6366f1; background-color: #e0e7ff; }
    .bubble-4 { bottom: 20px; left: 20px; color: #6366f1; background-color: #e0e7ff; }
    .bubble-5 { bottom: 20px; right: 20px; color: #10b981; background-color: #ecfdf5; }

    .landing-title {
        font-size: 2.25rem;
        font-weight: 700;
        color: #0f172a;
        text-align: center;
        margin: 1rem 0 0.25rem 0;
        font-family: 'Inter', sans-serif;
        letter-spacing: -0.5px;
    }
    .landing-subtitle {
        font-size: 1.35rem;
        color: #475569;
        text-align: center;
        margin: 0 0 3rem 0;
        font-family: 'Inter', sans-serif;
        font-weight: 400;
    }

    /* ── Label styling ── */
    .login-field-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
        display: block;
        text-align: left;
        font-family: 'Inter', sans-serif;
    }
    
    /* ── Text Input Styling ── */
    div[data-testid="stTextInput"] {
        margin-bottom: 1.5rem !important;
    }
    div[data-testid="stTextInput"] label {
        display: none !important;
    }
    div[data-testid="stTextInput"] input {
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 6px !important;
        padding: 12px 16px !important;
        font-size: 1rem !important;
        color: #0f172a !important;
        background-color: #ffffff !important;
        height: 48px !important;
        box-shadow: none !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #059669 !important;
        box-shadow: 0 0 0 2px rgba(5, 150, 105, 0.2) !important;
    }
    
    /* ── Pill Demo button ── */
    button[aria-label^="Not a user?"],
    button[aria-label^="Already a user?"] {
        background-color: #047857 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 8px 16px !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        height: auto !important;
        width: auto !important;
        margin-bottom: 1.5rem !important;
        display: inline-flex !important;
        box-shadow: none !important;
    }
    button[aria-label^="Not a user?"]:hover,
    button[aria-label^="Already a user?"]:hover {
        background-color: #065f46 !important;
    }

    /* ── Green Stack Buttons ── */
    button[aria-label="Login →"],
    button[aria-label="Sign up →"],
    button[aria-label="Sign in with Google"] {
        background-color: #059669 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        height: 44px !important;
        width: 220px !important;
        margin-bottom: 0.75rem !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        transition: background-color 0.2s !important;
        box-shadow: none !important;
    }
    button[aria-label="Login →"]:hover,
    button[aria-label="Sign up →"]:hover,
    button[aria-label="Sign in with Google"]:hover {
        background-color: #047857 !important;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.15) !important;
    }
    
    button[aria-label="Sign in with Google"]::before {
        content: "";
        display: inline-block;
        width: 18px;
        height: 18px;
        margin-right: 10px;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="white" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v3.92h6.69c-.29 1.5-1.14 2.77-2.4 3.61v3h3.86c2.26-2.09 3.59-5.17 3.59-8.46z"/><path fill="white" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.86-3c-1.08.72-2.45 1.16-4.07 1.16-3.13 0-5.78-2.11-6.73-4.96H1.29v3.09C3.26 21.3 7.31 24 12 24z"/><path fill="white" d="M5.27 14.29c-.25-.72-.38-1.49-.38-2.29s.14-1.57.38-2.29V6.62H1.29C.47 8.24 0 10.06 0 12s.47 3.76 1.29 5.38l3.98-3.09z"/><path fill="white" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.31 0 3.26 2.7 1.29 6.62l3.98 3.09c.95-2.85 3.6-4.96 6.73-4.96z"/></svg>');
        background-repeat: no-repeat;
        background-size: contain;
    }

    /* ── Insights List styling ── */
    .insights-container {
        margin-top: 2rem;
        text-align: left;
        font-family: 'Inter', sans-serif;
    }
    .insights-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 0.75rem;
    }
    .insights-list {
        list-style-type: disc !important;
        padding-left: 1.25rem !important;
        color: #475569;
        font-size: 0.95rem;
        line-height: 1.7;
    }
    .insights-list li {
        margin-bottom: 0.4rem;
    }

    /* ── Browser Mockup container ── */
    .browser-mockup {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        overflow: hidden;
        background-color: #ffffff;
        transition: transform 0.3s ease;
        margin-top: 1rem;
    }
    .browser-mockup:hover {
        transform: translateY(-2px);
    }
    </style>
    """

    st.markdown(login_css, unsafe_allow_html=True)
    st.markdown('<div class="top-accent-bar"></div>', unsafe_allow_html=True)
    st.markdown('<div class="right-accent-bar"></div>', unsafe_allow_html=True)

    # Render Centered Header with logo cluster
    st.markdown(f"""
    <div class="logo-cluster-container">
        <div class="logo-bubble bubble-1">&#123;&#125;</div>
        <div class="logo-bubble bubble-2">&lt;/&gt;</div>
        <div class="logo-bubble bubble-3">if</div>
        <div class="logo-bubble bubble-4">&#123;&#125;</div>
        <div class="logo-bubble bubble-5">if</div>
        <div class="main-logo-wrapper">{logo_svg}</div>
    </div>
    <h1 class="landing-title">Welcome to CodeRev AI</h1>
    <h2 class="landing-subtitle">The Intelligence behind your Codebase</h2>
    """, unsafe_allow_html=True)

    # Two Column Layout
    col_left, col_right = st.columns([1, 1.25], gap="large")

    with col_left:
        if st.session_state.auth_mode == "login":
            # Pill Demo Button
            if st.button("Not a user? Sign up for a demo →", key="btn_demo"):
                st.session_state.auth_mode = "signup"
                st.rerun()

            # Form fields
            st.markdown('<span class="login-field-label">ENTER WORK EMAIL (for analysis dashboard)</span>', unsafe_allow_html=True)
            email = st.text_input("", placeholder="me@example.com", key="login_email_input")
            
            if st.button("Login →", type="primary", key="btn_submit_login"):
                if email and email.strip():
                    with st.spinner("Authenticating..."):
                        data, err = api_call("POST", "/auth/login-passwordless", {"email": email.strip()})
                    if data:
                        st.session_state.logged_in = True
                        st.session_state.token = data["access_token"]
                        st.session_state.username = data["user"]["username"]
                        st.session_state.user_id = data["user"]["id"]
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(f"❌ {err}")
                else:
                    st.warning("Please enter your email.")
                    
        else:
            # Pill Login Button
            if st.button("Already a user? Log into account →", key="btn_demo"):
                st.session_state.auth_mode = "login"
                st.rerun()

            # Form fields
            st.markdown('<span class="login-field-label">ENTER WORK EMAIL (for analysis dashboard)</span>', unsafe_allow_html=True)
            email = st.text_input("", placeholder="me@example.com", key="signup_email_input")
            
            if st.button("Sign up →", type="primary", key="btn_submit_signup"):
                if email and email.strip():
                    with st.spinner("Creating account..."):
                        data, err = api_call("POST", "/auth/register-passwordless", {"email": email.strip()})
                    if data:
                        st.session_state.logged_in = True
                        st.session_state.token = data["access_token"]
                        st.session_state.username = data["user"]["username"]
                        st.session_state.user_id = data["user"]["id"]
                        st.success("Account created successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ {err}")
                else:
                    st.warning("Please enter your email.")

        # Social login handler
        def handle_social_login(provider: str, mock_email: str):
            with st.spinner(f"Signing in with {provider}..."):
                data, err = api_call("POST", "/auth/register-passwordless", {"email": mock_email})
                if err and "already registered" in err.lower():
                    data, err = api_call("POST", "/auth/login-passwordless", {"email": mock_email})
                
                if data:
                    st.session_state.logged_in = True
                    st.session_state.token = data["access_token"]
                    st.session_state.username = data["user"]["username"]
                    st.session_state.user_id = data["user"]["id"]
                    st.success(f"Successfully logged in via {provider}!")
                    st.rerun()
                else:
                    st.error(f"❌ {provider} Sign-in failed: {err}")

        # Social Google button
        if st.button("Sign in with Google", key="btn_google", type="primary"):
            handle_social_login("Google", "google_user@example.com")

        # Insights list
        st.markdown("""
        <div class="insights-container">
            <h3 class="insights-title">AI-Powered Insights</h3>
            <ul class="insights-list">
                <li>Automated Code Quality Analysis</li>
                <li>Security Vulnerability Detection</li>
                <li>Best Practice & Maintainability Reports</li>
                <li>Seamless Git Integration</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        if img_base64:
            st.markdown(f"""
            <div class="browser-mockup">
                <img src="data:image/png;base64,{img_base64}" style="width:100%; display:block;" alt="IDE Mockup Preview" />
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Visual preview loading...")



# ─── Sidebar ──────────────────────────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; padding: 16px 0;">
            <div style="font-size: 1.1rem; font-weight: 700; color: #e6edf3;">AI Code Reviewer</div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        st.markdown(f"""
        <div style="background:#f1f5f9; border:1px solid #e2e8f0; border-radius:8px; padding:10px 14px; margin-bottom:12px;">
            <div style="font-size:0.8rem; color:#64748b;">Logged in as</div>
            <div style="font-weight:600; color:#2563eb;">{st.session_state.username}</div>
        </div>
        """, unsafe_allow_html=True)

        nav_items = [
            ("Code Review", "review"),
            ("Dashboard", "dashboard"),
            ("History", "history"),
        ]

        for label, page_key in nav_items:
            active = st.session_state.page == page_key
            btn_style = "primary" if active else "secondary"
            if st.button(label, key=f"nav_{page_key}", use_container_width=True,
                         type=btn_style):
                st.session_state.page = page_key
                st.rerun()

        st.divider()

        if st.button("Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()




# ─── Page: Code Review ────────────────────────────────────────────────────────

def page_review():
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">AI Code Review</div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1.2, 0.8])

    with col_left:
        st.markdown('<div class="section-header">Submit Code for Review</div>', unsafe_allow_html=True)

        language = st.selectbox(
            "Programming Language",
            options=["python", "javascript", "java", "cpp", "c"],
            format_func=lambda x: {
                "python": "Python",
                "java": "Java",
                "javascript": "JavaScript",
                "cpp": "C++",
                "c": "C"
            }[x]
        )

        code = st.text_area(
            "Paste your code here",
            height=380,
            placeholder=f"// Paste your {language} code here...\n// The AI will analyze bugs, security issues, performance, and more.",
            help="Maximum 50,000 characters"
        )

        char_count = len(code) if code else 0
        st.caption(f"Characters: {char_count:,} / 50,000")

        if st.button("Analyze Code", use_container_width=True):
            if not code or not code.strip():
                st.error("Please paste some code to analyze.")
            elif len(code) > 50000:
                st.error("Code is too long. Maximum 50,000 characters.")
            else:
                with st.spinner("Gemini AI is analyzing your code... (may take 30-60 seconds)"):
                    result, err = api_call(
                        "POST", "/review/analyze",
                        {"code": code, "language": language},
                        token=st.session_state.token
                    )

                if result:
                    st.session_state.review_result = result
                    st.success(f"Review complete! Found {result.get('total_issues', 0)} issues.")
                    st.rerun()
                else:
                    st.error(f"Analysis failed: {err}")

    with col_right:
        st.markdown('<div class="section-header">What Gets Analyzed</div>', unsafe_allow_html=True)
        categories = [
            ("Bugs", "Logic errors, null pointers, off-by-one"),
            ("Security", "SQL injection, XSS, buffer overflows"),
            ("Performance", "Algorithm efficiency, memory leaks"),
            ("Code Smells", "Dead code, duplication, magic numbers"),
            ("Standards", "Language-specific best practices"),
            ("Maintainability", "Readability, modularity, docs"),
        ]
        for cat, desc in categories:
            st.markdown(f"""
            <div style="background:#161b22; border:1px solid #30363d; border-radius:8px; padding:10px 14px; margin:6px 0;">
                <strong style="color:#e6edf3;">{cat}</strong>
                <div style="font-size:0.8rem; color:#7d8590; margin-top:3px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Results ──
    result = st.session_state.get("review_result")
    if result:
        render_review_results(result)


def render_review_results(result: dict):
    st.markdown("---")
    st.markdown('<div class="section-header">Review Results</div>', unsafe_allow_html=True)

    # Score cards
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_score_card("Overall Score", result["overall_score"], "")
    with c2: render_score_card("Security", result["security_score"], "")
    with c3: render_score_card("Performance", result["performance_score"], "")
    with c4: render_score_card("Maintainability", result["maintainability_score"], "")

    # Gauge charts
    st.markdown("#### Score Breakdown")
    g1, g2, g3, g4 = st.columns(4)
    with g1: st.plotly_chart(render_gauge_chart(result["overall_score"], "Overall"), use_container_width=True)
    with g2: st.plotly_chart(render_gauge_chart(result["security_score"], "Security"), use_container_width=True)
    with g3: st.plotly_chart(render_gauge_chart(result["performance_score"], "Performance"), use_container_width=True)
    with g4: st.plotly_chart(render_gauge_chart(result["maintainability_score"], "Maintainability"), use_container_width=True)

    # Issue summary
    st.markdown("#### Issue Summary")
    i1, i2, i3, i4 = st.columns(4)
    with i1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{result['total_issues']}</div>
            <div class="metric-label">Total Issues</div>
        </div>""", unsafe_allow_html=True)
    with i2:
        st.markdown(f"""
        <div class="metric-card" style="border-color:#f85149;">
            <div class="metric-number" style="color:#f85149;">{result['high_severity_count']}</div>
            <div class="metric-label">High Severity</div>
        </div>""", unsafe_allow_html=True)
    with i3:
        st.markdown(f"""
        <div class="metric-card" style="border-color:#d29922;">
            <div class="metric-number" style="color:#d29922;">{result['medium_severity_count']}</div>
            <div class="metric-label">Medium Severity</div>
        </div>""", unsafe_allow_html=True)
    with i4:
        st.markdown(f"""
        <div class="metric-card" style="border-color:#3fb950;">
            <div class="metric-number" style="color:#3fb950;">{result['low_severity_count']}</div>
            <div class="metric-label">Low Severity</div>
        </div>""", unsafe_allow_html=True)

    # Issues List + Improved Code
    tab1, tab2, tab3 = st.tabs(["Detected Issues", "Improved Code", "Raw JSON"])

    with tab1:
        issues = result.get("issues", [])
        if not issues:
            st.success("No issues detected! Great code!")
        else:
            # Filter controls
            fc1, fc2 = st.columns(2)
            with fc1:
                sev_filter = st.multiselect("Filter by Severity", ["High", "Medium", "Low"],
                                            default=["High", "Medium", "Low"])
            with fc2:
                cats = list(set(i["category"] for i in issues))
                cat_filter = st.multiselect("Filter by Category", cats, default=cats)

            filtered = [i for i in issues
                        if i["severity"] in sev_filter and i["category"] in cat_filter]

            st.caption(f"Showing {len(filtered)} of {len(issues)} issues")

            for i, issue in enumerate(filtered):
                sev = issue["severity"].lower()
                sev_colors = {"high": "issue-high", "medium": "issue-medium", "low": "issue-low"}
                badge_colors = {"high": "badge-high", "medium": "badge-medium", "low": "badge-low"}

                with st.expander(
                    f"[{issue['severity']}] {issue['category']}: "
                    f"{issue['description'][:80]}{'...' if len(issue['description']) > 80 else ''}",
                    expanded=(sev == "high")
                ):
                    st.markdown(f"""
                    <div class="issue-card {sev_colors.get(sev, '')}">
                        <span class="severity-badge {badge_colors.get(sev, '')}">{issue['severity']}</span>
                        <span class="category-badge">{issue['category']}</span>
                        {"<span style='color:#7d8590; font-size:0.8rem; margin-left:8px;'>Line " + str(issue['line_number']) + "</span>" if issue.get('line_number') else ""}
                        <p style="margin-top:12px; color:#e6edf3; line-height:1.6;">{issue['description']}</p>
                        <div style="margin-top:10px; padding:10px; background:#0d1117; border-radius:6px; border:1px solid #30363d;">
                            <div style="font-size:0.8rem; color:#7d8590; margin-bottom:6px;">Suggested Fix:</div>
                            <div style="color:#3fb950; font-family:'JetBrains Mono', monospace; font-size:0.85rem; white-space:pre-wrap;">{issue['fix']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    with tab2:
        improved = result.get("improved_code", "")
        if improved:
            lang = result.get("language", "python")
            st.markdown("**AI-Improved Version of Your Code**")
            st.markdown("> All detected issues have been fixed in this version.")
            st.code(improved, language=lang)
            st.download_button(
                "Download Improved Code",
                improved,
                file_name=f"improved_code.{lang}",
                mime="text/plain"
            )
        else:
            st.info("Improved code not available.")

    with tab3:
        st.json({
            "overall_score": result["overall_score"],
            "security_score": result["security_score"],
            "performance_score": result["performance_score"],
            "maintainability_score": result["maintainability_score"],
            "total_issues": result["total_issues"],
            "issues": result.get("issues", [])
        })


# ─── Page: Dashboard ──────────────────────────────────────────────────────────

def page_dashboard():
    st.markdown('<div class="hero-banner"><div class="hero-title">Dashboard</div></div>', unsafe_allow_html=True)

    data, err = api_call("GET", "/dashboard/stats", token=st.session_state.token)

    if err:
        st.error(f"Failed to load dashboard: {err}")
        return

    if data["total_reviews"] == 0:
        st.info("No reviews yet. Start by submitting code for review!")
        if st.button("Go to Code Review"):
            st.session_state.page = "review"
            st.rerun()
        return

    # ── Top Stats ──
    c1, c2, c3, c4 = st.columns(4)
    metrics = [
        (c1, "Total Reviews", data["total_reviews"], "", "#58a6ff"),
        (c2, "Average Score", f"{data['average_score']:.1f}", "", "#3fb950"),
        (c3, "Total Issues", data["total_issues_found"], "", "#d29922"),
        (c4, "High Severity", data["high_severity_total"], "", "#f85149"),
    ]
    for col, label, value, icon, color in metrics:
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-color:{color};">
                <div class="metric-number" style="color:{color};">{value}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Score Breakdown Chart ──
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Average Scores by Category")
        categories = ["Overall", "Security", "Performance", "Maintainability"]
        scores = [
            data["average_score"],
            data["average_security_score"],
            data["average_performance_score"],
            data["average_maintainability_score"]
        ]
        colors = ["#3b82f6", "#ef4444", "#10b981", "#f59e0b"]

        fig = go.Figure(go.Bar(
            x=categories,
            y=scores,
            marker_color=colors,
            text=[f"{s:.1f}" for s in scores],
            textposition="outside",
            textfont={"color": "#0f172a"}
        ))
        fig.update_layout(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font={"color": "#0f172a"},
            yaxis={"range": [0, 105], "gridcolor": "#f1f5f9"},
            xaxis={"gridcolor": "#f1f5f9"},
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("#### Language Distribution")
        lang_data = data.get("languages_used", {})
        if lang_data:
            labels = [k.upper() for k in lang_data.keys()]
            values = list(lang_data.values())

            fig2 = go.Figure(go.Pie(
                labels=labels,
                values=values,
                hole=0.5,
                marker={"colors": ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"]},
                textfont={"color": "#0f172a"}
            ))
            fig2.update_layout(
                paper_bgcolor="#ffffff",
                font={"color": "#0f172a"},
                showlegend=True,
                legend={"bgcolor": "#f8fafc"},
                margin=dict(l=20, r=20, t=20, b=20),
                height=300
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No language data available yet.")

    # ── Recent Reviews Table ──
    st.markdown("#### Recent Reviews")
    recent = data.get("recent_reviews", [])
    if recent:
        df = pd.DataFrame(recent)
        df["Score"] = df["overall_score"].apply(lambda x: f"{x:.0f}")
        df["Language"] = df["language"].str.upper()
        df["Issues"] = df["total_issues"].astype(str)
        df["High"] = df["high_severity_count"].astype(str)
        df["Date"] = pd.to_datetime(df["created_at"]).dt.strftime("%b %d, %Y %H:%M")

        display_df = df[["id", "Language", "Score", "Issues", "High", "Date"]].rename(columns={"id": "ID"})
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No recent reviews.")


# ─── Page: History ────────────────────────────────────────────────────────────

def page_history():
    st.markdown('<div class="hero-banner"><div class="hero-title">Review History</div></div>', unsafe_allow_html=True)

    # Filter
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        lang_filter = st.selectbox("Filter Language", ["All", "python", "javascript", "java", "cpp", "c"])
    with col_f2:
        page_size = st.selectbox("Per Page", [10, 20, 50], index=0)

    lang_param = "" if lang_filter == "All" else f"&language={lang_filter}"
    data, err = api_call("GET", f"/review/history?limit={page_size}{lang_param}",
                         token=st.session_state.token)

    if err:
        st.error(f"Failed to load history: {err}")
        return

    reviews = data.get("reviews", [])

    if not reviews:
        st.info("No reviews found. Submit your first code review!")
        return

    st.caption(f"Found {len(reviews)} reviews")

    for rev in reviews:
        score = rev["overall_score"]
        dt = datetime.fromisoformat(rev["created_at"]).strftime("%b %d, %Y at %H:%M")

        with st.expander(
            f"{rev['language'].upper()}  |  "
            f"Score: {score:.0f}  |  "
            f"{rev['total_issues']} Issues  |  "
            f"{dt}",
            expanded=False
        ):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Overall", f"{rev['overall_score']:.0f}")
            with c2:
                st.metric("Security", f"{rev['security_score']:.0f}")
            with c3:
                st.metric("Performance", f"{rev['performance_score']:.0f}")
            with c4:
                st.metric("Maintainability", f"{rev['maintainability_score']:.0f}")

            btn_col1, btn_col2 = st.columns([1, 4])
            with btn_col1:
                if st.button("View Full", key=f"view_{rev['id']}"):
                    st.session_state[f"show_review_{rev['id']}"] = True

            # Show full review details
            if st.session_state.get(f"show_review_{rev['id']}"):
                detail, err2 = api_call("GET", f"/review/{rev['id']}", token=st.session_state.token)
                if detail:
                    st.markdown("**Detected Issues:**")
                    for issue in detail.get("issues", []):
                        st.markdown(f"- **[{issue['severity']}] {issue['category']}**: {issue['description']}")
                    if detail.get("original_code"):
                        with st.expander("Original Code"):
                            st.code(detail["original_code"], language=rev["language"])
                    if detail.get("improved_code"):
                        with st.expander("Improved Code"):
                            st.code(detail["improved_code"], language=rev["language"])



# ─── Main App ─────────────────────────────────────────────────────────────────

def main():
    init_session()
    load_css()

    if not st.session_state.logged_in:
        page_login()
        return

    render_sidebar()

    page = st.session_state.get("page", "review")
    if page == "review":
        page_review()
    elif page == "dashboard":
        page_dashboard()
    elif page == "history":
        page_history()


if __name__ == "__main__":
    main()
