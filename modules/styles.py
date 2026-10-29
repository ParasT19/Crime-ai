"""
modules/styles.py — Dark forensic CSS theme injection
"""

import streamlit as st


def inject_css():
    """Inject the CrimeVision AI dark-theme forensic CSS."""
    st.markdown(
        """
<style>
/* ── Root palette ──────────────────────────────────────────────────── */
:root {
    --bg-primary:   #0a0e1a;
    --bg-secondary: #0f1629;
    --bg-card:      #131c35;
    --bg-card2:     #1a2540;
    --accent-blue:  #1e88e5;
    --accent-cyan:  #00bcd4;
    --accent-green: #00e676;
    --accent-amber: #ffb300;
    --accent-red:   #f44336;
    --accent-purple:#9c27b0;
    --text-primary: #e8eaf6;
    --text-muted:   #7986cb;
    --border:       rgba(30,136,229,0.25);
    --glow-blue:    0 0 12px rgba(30,136,229,0.4);
    --glow-red:     0 0 12px rgba(244,67,54,0.4);
    --glow-green:   0 0 12px rgba(0,230,118,0.35);
    --glow-amber:   0 0 12px rgba(255,179,0,0.4);
}

/* ── Global ────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: 'JetBrains Mono', 'Courier New', monospace !important;
}

.stApp { background: var(--bg-primary) !important; }

/* ── Sidebar ───────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* ── Tabs ──────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-secondary) !important;
    border-bottom: 2px solid var(--border) !important;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    padding: 10px 18px !important;
    border-radius: 6px 6px 0 0 !important;
    border: 1px solid transparent !important;
    transition: all 0.2s ease !important;
}
.stTabs [aria-selected="true"] {
    background: var(--bg-card) !important;
    color: var(--accent-cyan) !important;
    border-color: var(--border) !important;
    border-bottom-color: var(--bg-card) !important;
    box-shadow: var(--glow-blue) !important;
}

/* ── Cards ─────────────────────────────────────────────────────────── */
.forensic-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px 24px;
    margin: 12px 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
.forensic-card-highlight {
    background: var(--bg-card2);
    border: 1px solid var(--accent-blue);
    border-radius: 10px;
    padding: 20px 24px;
    margin: 12px 0;
    box-shadow: var(--glow-blue);
}

/* ── Header / COC banner ───────────────────────────────────────────── */
.coc-banner {
    background: linear-gradient(135deg, #0a1628 0%, #0f2040 50%, #0a1628 100%);
    border: 1px solid var(--accent-blue);
    border-radius: 12px;
    padding: 16px 24px;
    margin-bottom: 20px;
    box-shadow: var(--glow-blue);
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
}
.coc-title {
    font-size: 1.6rem;
    font-weight: 800;
    background: linear-gradient(90deg, #1e88e5, #00bcd4, #00e676);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 0.04em;
}
.coc-subtitle {
    font-size: 0.72rem;
    color: var(--text-muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
}
.coc-badge {
    background: rgba(30,136,229,0.15);
    border: 1px solid var(--accent-blue);
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--accent-cyan);
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.coc-badge-live {
    background: rgba(0,230,118,0.15);
    border: 1px solid var(--accent-green);
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--accent-green);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    animation: pulse-green 2s infinite;
}
@keyframes pulse-green {
    0%, 100% { box-shadow: 0 0 6px rgba(0,230,118,0.4); }
    50%       { box-shadow: 0 0 18px rgba(0,230,118,0.8); }
}

/* ── Threat level badges ───────────────────────────────────────────── */
.threat-critical { color: var(--accent-red)   !important; font-weight:800; text-transform:uppercase; letter-spacing:.1em; }
.threat-high     { color: var(--accent-amber)  !important; font-weight:800; text-transform:uppercase; letter-spacing:.1em; }
.threat-medium   { color: #ff9800             !important; font-weight:700; text-transform:uppercase; letter-spacing:.1em; }
.threat-low      { color: var(--accent-green)  !important; font-weight:700; text-transform:uppercase; letter-spacing:.1em; }

/* ── Metric boxes ──────────────────────────────────────────────────── */
.metric-box {
    background: var(--bg-card2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px 18px;
    text-align: center;
}
.metric-value {
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--accent-cyan);
}
.metric-label {
    font-size: 0.68rem;
    color: var(--text-muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* ── Confidence bar ────────────────────────────────────────────────── */
.conf-bar-wrap { background: rgba(255,255,255,0.06); border-radius: 4px; height: 8px; margin: 4px 0; }
.conf-bar      { height: 8px; border-radius: 4px; transition: width 0.6s ease; }

/* ── Evidence table ────────────────────────────────────────────────── */
.evidence-table { width: 100%; border-collapse: collapse; font-size: 0.78rem; }
.evidence-table th {
    background: rgba(30,136,229,0.2);
    color: var(--accent-cyan);
    padding: 10px 14px;
    text-align: left;
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    border-bottom: 1px solid var(--border);
}
.evidence-table td {
    padding: 9px 14px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    color: var(--text-primary);
    vertical-align: top;
}
.evidence-table tr:hover td { background: rgba(30,136,229,0.06); }

/* ── Chat bubbles ──────────────────────────────────────────────────── */
.chat-user {
    background: rgba(30,136,229,0.15);
    border: 1px solid rgba(30,136,229,0.4);
    border-radius: 10px 10px 2px 10px;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 0.82rem;
}
.chat-ai {
    background: rgba(0,188,212,0.08);
    border: 1px solid rgba(0,188,212,0.3);
    border-radius: 10px 10px 10px 2px;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 0.82rem;
}
.chat-citation {
    background: rgba(156,39,176,0.12);
    border-left: 3px solid var(--accent-purple);
    border-radius: 4px;
    padding: 6px 12px;
    margin-top: 8px;
    font-size: 0.72rem;
    color: #ce93d8;
}

/* ── Upload area ───────────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    border: 2px dashed var(--border) !important;
    border-radius: 10px !important;
    background: var(--bg-card) !important;
    padding: 12px !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent-cyan) !important;
    box-shadow: var(--glow-blue) !important;
}

/* ── Buttons ───────────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #1565c0, #0d47a1) !important;
    color: white !important;
    border: 1px solid var(--accent-blue) !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    transition: all 0.2s ease !important;
    font-family: 'JetBrains Mono', monospace !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1e88e5, #1565c0) !important;
    box-shadow: var(--glow-blue) !important;
    transform: translateY(-1px) !important;
}

/* ── Selectbox / Text inputs ───────────────────────────────────────── */
.stSelectbox > div > div,
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border-color: var(--border) !important;
}

/* ── Streamlit metric widget ───────────────────────────────────────── */
[data-testid="metric-container"] {
    background: var(--bg-card2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 12px !important;
}

/* ── Scrollbar ─────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--accent-blue); border-radius: 3px; }

/* ── Dividers ──────────────────────────────────────────────────────── */
hr { border-color: var(--border) !important; }

/* ── Expanders ─────────────────────────────────────────────────────── */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    color: var(--accent-cyan) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-size: 0.8rem !important;
}

/* ── Info / Warning / Success boxes ───────────────────────────────── */
.stInfo    { background: rgba(30,136,229,0.1) !important; border-color: var(--accent-blue) !important; }
.stWarning { background: rgba(255,179,0,0.1)  !important; border-color: var(--accent-amber) !important; }
.stSuccess { background: rgba(0,230,118,0.1)  !important; border-color: var(--accent-green) !important; }
.stError   { background: rgba(244,67,54,0.1)  !important; border-color: var(--accent-red)   !important; }

/* ── Code blocks ───────────────────────────────────────────────────── */
code { background: rgba(0,188,212,0.1) !important; color: var(--accent-cyan) !important; }

/* ── Section headers ───────────────────────────────────────────────── */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 24px 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
}
.section-header h3 {
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    color: var(--accent-cyan) !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    margin: 0 !important;
}

/* ── Progress / Spinner ────────────────────────────────────────────── */
.stProgress > div > div { background: var(--accent-blue) !important; }
.stSpinner > div        { border-top-color: var(--accent-cyan) !important; }

/* ── PDF export button ─────────────────────────────────────────────── */
.export-btn > button {
    background: linear-gradient(135deg, #1b5e20, #2e7d32) !important;
    border-color: var(--accent-green) !important;
    font-size: 1rem !important;
    padding: 14px 28px !important;
    width: 100%;
}
.export-btn > button:hover {
    box-shadow: var(--glow-green) !important;
}

/* ── Demo mode indicator ───────────────────────────────────────────── */
.demo-banner {
    background: rgba(255,179,0,0.1);
    border: 1px solid var(--accent-amber);
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 0.75rem;
    color: var(--accent-amber);
    margin-bottom: 12px;
    letter-spacing: 0.05em;
}
</style>
""",
        unsafe_allow_html=True,
    )
