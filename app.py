"""
CrimeVision AI - Intelligent Multimodal Forensic Analysis Platform
Skill Wallet Capstone Project 2

Senior Forensic Systems Architect · Production-Ready Streamlit Application
"""

import streamlit as st
import uuid
from datetime import datetime

# ── Page configuration (must be first Streamlit call) ──────────────────────
st.set_page_config(
    page_title="CrimeVision AI | Forensic Analysis Platform",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "CrimeVision AI — Intelligent Multimodal Forensic Analysis Platform v2.0",
    },
)

# ── Internal modules ────────────────────────────────────────────────────────
from modules.styles import inject_css
from modules.config import render_sidebar, get_api_client
from modules.tab_image import render_tab_image
from modules.tab_audio import render_tab_audio
from modules.tab_video import render_tab_video
from modules.tab_fusion import render_tab_fusion
from modules.tab_export import render_tab_export
from modules.custody import init_custody, render_custody_banner

# ── Global CSS ──────────────────────────────────────────────────────────────
inject_css()

# ── Session State Initialisation ────────────────────────────────────────────
def _init_session():
    if "evidence_id" not in st.session_state:
        st.session_state.evidence_id = f"EV-{uuid.uuid4().hex[:8].upper()}"
    if "session_start" not in st.session_state:
        st.session_state.session_start = datetime.utcnow()
    if "investigator" not in st.session_state:
        st.session_state.investigator = "PENDING"
    if "image_findings" not in st.session_state:
        st.session_state.image_findings = None
    if "audio_findings" not in st.session_state:
        st.session_state.audio_findings = None
    if "video_findings" not in st.session_state:
        st.session_state.video_findings = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "api_client" not in st.session_state:
        st.session_state.api_client = None
    if "demo_mode" not in st.session_state:
        st.session_state.demo_mode = False

_init_session()

# ── Sidebar (config, API key, investigator sign-off) ───────────────────────
render_sidebar()

# ── Header / Chain-of-Custody banner ───────────────────────────────────────
render_custody_banner()

# ── Main Navigation Tabs ────────────────────────────────────────────────────
tab_labels = [
    "🖼️ Visual Evidence",
    "🎙️ Witness Audio",
    "📹 CCTV Video",
    "🧩 Fusion & Chat",
    "📄 PDF Export",
]

tabs = st.tabs(tab_labels)

with tabs[0]:
    render_tab_image()

with tabs[1]:
    render_tab_audio()

with tabs[2]:
    render_tab_video()

with tabs[3]:
    render_tab_fusion()

with tabs[4]:
    render_tab_export()
