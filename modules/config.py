"""
modules/config.py — API configuration, sidebar UI, client management
"""

import streamlit as st
from datetime import datetime

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


def render_sidebar():
    """Render the sidebar configuration panel."""
    with st.sidebar:
        st.markdown(
            '<div style="text-align:center;padding:16px 0 8px 0;">'
            '<span style="font-size:2rem;">🔍</span><br>'
            '<span style="font-size:0.95rem;font-weight:800;color:#00bcd4;letter-spacing:.08em;">'
            'CRIMEVISION AI</span><br>'
            '<span style="font-size:0.62rem;color:#7986cb;letter-spacing:.12em;">FORENSIC ANALYSIS PLATFORM</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.divider()

        # ── API Configuration ─────────────────────────────────────────
        st.markdown("### ⚙️ API Configuration")

        api_provider = st.selectbox(
            "AI Provider",
            ["Gemini (Google)", "Demo Mode (No API)"],
            key="api_provider",
        )

        if api_provider == "Gemini (Google)":
            api_key = st.text_input(
                "Gemini API Key",
                type="password",
                placeholder="AIza...",
                help="Get your key at https://aistudio.google.com",
                key="gemini_api_key",
            )
            model_choice = st.selectbox(
                "Model",
                [
                    "gemini-3.8-flash",
                    "gemini-3.1-pro-preview",
                    "gemini-3.5-flash-lite",
                ],
                key="model_choice",
            )
            if st.button("🔑 Connect API", use_container_width=True):
                client = _try_connect(api_key, model_choice)
                if client:
                    st.session_state.api_client = client
                    st.session_state.demo_mode = False
                    st.session_state.current_model = model_choice
                    st.success("✅ API Connected")
                else:
                    st.error("❌ Connection failed — enabling Demo Mode")
                    st.session_state.demo_mode = True
                    st.session_state.api_client = None
        else:
            st.session_state.demo_mode = True
            st.session_state.api_client = None
            st.session_state.current_model = "demo"
            st.info("🟡 Demo Mode — synthetic forensic data will be generated locally.")

        st.divider()

        # ── Chain-of-Custody ─────────────────────────────────────────
        st.markdown("### 🔗 Chain of Custody")

        st.markdown(
            f'<div class="forensic-card" style="padding:12px 16px;">'
            f'<div style="font-size:.68rem;color:#7986cb;letter-spacing:.1em;text-transform:uppercase;">Evidence ID</div>'
            f'<div style="font-size:.9rem;font-weight:700;color:#00bcd4;">{st.session_state.evidence_id}</div>'
            f'<div style="margin-top:8px;font-size:.68rem;color:#7986cb;letter-spacing:.1em;text-transform:uppercase;">Session Start (UTC)</div>'
            f'<div style="font-size:.75rem;color:#e8eaf6;">{st.session_state.session_start.strftime("%Y-%m-%d %H:%M:%S")}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        investigator_name = st.text_input(
            "Investigator Name",
            placeholder="Det. J. Smith",
            key="investigator_input",
        )
        badge_id = st.text_input(
            "Badge / Employee ID",
            placeholder="BADGE-4872",
            key="badge_id",
        )

        if st.button("✍️ Sign Off", use_container_width=True):
            if investigator_name and badge_id:
                st.session_state.investigator = f"{investigator_name} ({badge_id})"
                st.session_state.signoff_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                st.success(f"Signed off: {investigator_name}")
            else:
                st.warning("Enter both name and badge ID.")

        if st.session_state.investigator != "PENDING":
            st.markdown(
                f'<div style="background:rgba(0,230,118,0.1);border:1px solid #00e676;'
                f'border-radius:6px;padding:8px 12px;font-size:.72rem;color:#00e676;">'
                f'✅ Signed: {st.session_state.investigator}</div>',
                unsafe_allow_html=True,
            )

        st.divider()

        # ── Evidence Management ───────────────────────────────────────
        st.markdown("### 📂 Evidence Status")
        cols = st.columns(3)
        with cols[0]:
            has_img = st.session_state.image_findings is not None
            st.markdown(
                f'<div style="text-align:center;font-size:.65rem;color:{"#00e676" if has_img else "#7986cb"};">'
                f'{"✅" if has_img else "○"}<br>IMAGE</div>',
                unsafe_allow_html=True,
            )
        with cols[1]:
            has_aud = st.session_state.audio_findings is not None
            st.markdown(
                f'<div style="text-align:center;font-size:.65rem;color:{"#00e676" if has_aud else "#7986cb"};">'
                f'{"✅" if has_aud else "○"}<br>AUDIO</div>',
                unsafe_allow_html=True,
            )
        with cols[2]:
            has_vid = st.session_state.video_findings is not None
            st.markdown(
                f'<div style="text-align:center;font-size:.65rem;color:{"#00e676" if has_vid else "#7986cb"};">'
                f'{"✅" if has_vid else "○"}<br>VIDEO</div>',
                unsafe_allow_html=True,
            )

        st.divider()
        st.markdown(
            '<div style="font-size:.6rem;color:#455a64;text-align:center;line-height:1.6;">'
            'CrimeVision AI v2.0<br>© 2026 Forensic AI Systems<br>'
            'FOR LAW ENFORCEMENT USE ONLY<br>All analysis is AI-assisted</div>',
            unsafe_allow_html=True,
        )


def _try_connect(api_key: str, model: str):
    """Attempt to create a Gemini API client. Returns client or None."""
    if not GENAI_AVAILABLE:
        return None
    if not api_key or not api_key.strip():
        return None
    try:
        client = genai.Client(api_key=api_key.strip())
        # Lightweight connectivity test
        client.interactions.create(
            model=model,
            input="ping",
        )
        return client
    except Exception:
        return None


def get_api_client():
    """Return the active API client or None if in demo mode."""
    return st.session_state.get("api_client", None)


def get_model() -> str:
    """Return the active model name."""
    return st.session_state.get("current_model", "gemini-3.8-flash")


def is_demo_mode() -> bool:
    return st.session_state.get("demo_mode", True)
