"""
modules/custody.py — Chain-of-custody banner and tracking utilities
"""

import streamlit as st
from datetime import datetime


def init_custody():
    """No-op — state is initialised in app.py."""
    pass


def render_custody_banner():
    """Render the top-of-page chain-of-custody header."""
    demo = st.session_state.get("demo_mode", True)
    inv = st.session_state.get("investigator", "PENDING")
    eid = st.session_state.get("evidence_id", "---")
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    mode_badge = (
        '<span class="coc-badge" style="color:#ffb300;border-color:#ffb300;'
        'background:rgba(255,179,0,0.1);">⚠ DEMO MODE</span>'
        if demo
        else '<span class="coc-badge-live">● LIVE</span>'
    )

    inv_badge = (
        f'<span class="coc-badge">✍ {inv}</span>'
        if inv != "PENDING"
        else '<span class="coc-badge" style="color:#f44336;border-color:#f44336;'
        'background:rgba(244,67,54,0.1);">⚠ NOT SIGNED</span>'
    )

    st.markdown(
        f"""
<div class="coc-banner">
    <div>
        <div class="coc-title">🔍 CrimeVision AI</div>
        <div class="coc-subtitle">Intelligent Multimodal Forensic Analysis Platform · Capstone Project 2</div>
    </div>
    <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;">
        <span class="coc-badge">📁 {eid}</span>
        <span class="coc-badge">🕐 {ts}</span>
        {inv_badge}
        {mode_badge}
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    if demo:
        st.markdown(
            '<div class="demo-banner">⚠️  DEMO MODE ACTIVE — All analysis uses synthetic forensic data. '
            "Connect a Gemini API key in the sidebar for real AI-powered analysis.</div>",
            unsafe_allow_html=True,
        )


def get_timestamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def custody_log_entry(action: str, detail: str) -> dict:
    """Create a chain-of-custody log entry."""
    return {
        "timestamp": get_timestamp(),
        "evidence_id": st.session_state.get("evidence_id", "---"),
        "investigator": st.session_state.get("investigator", "PENDING"),
        "action": action,
        "detail": detail,
    }
