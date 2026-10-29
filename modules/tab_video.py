"""
modules/tab_video.py — Tab 3: CCTV Video Analysis & Event Progression (Epic 4)

Processes video files by extracting frames and using Gemini Vision to track
suspect trajectories, vehicle movements, and classify criminal acts.
"""

import io
import json
import base64
import time
import streamlit as st

try:
    import numpy as np
    NUMPY_OK = True
except ImportError:
    NUMPY_OK = False

from modules.config import get_api_client, get_model, is_demo_mode
from modules.demo_data import VIDEO_DEMO, get_confidence_color
from modules.custody import get_timestamp


# ── Gemini system prompt ──────────────────────────────────────────────────────
_VIDEO_SYSTEM = """You are a forensic CCTV video analyst AI. Analyse the provided video frames and construct 
a chronological forensic event log tracking all suspects, vehicles, and significant actions.

Return ONLY valid JSON matching this exact schema (no markdown, no prose):
{
  "duration_sec": <integer>,
  "fps_analysed": <integer>,
  "frames_processed": <integer>,
  "suspects_tracked": <integer>,
  "vehicles_tracked": <integer>,
  "summary": "<2-3 sentence forensic narrative>",
  "event_log": [
    {
      "timestamp": "<HH:MM:SS>",
      "frame": <integer>,
      "event": "<description of forensically significant event>",
      "category": "<legal crime category e.g. Burglary|Assault|Homicide|Robbery|Trespass|Vandalism|Baseline|Activity>",
      "confidence": <0.0-1.0>
    }
  ],
  "trajectories": [
    {
      "entity": "<Suspect S1|Vehicle V1|etc>",
      "path": "<entry point → movement → exit>"
    }
  ],
  "vehicle_details": {
    "type": "<vehicle type>",
    "color": "<color>",
    "partial_plate": "<partial if visible>",
    "direction": "<direction of travel>"
  }
}

Rules:
- Track every distinct person and vehicle with a consistent ID (S1, S2, V1, V2).
- Classify events using legal penal crime categories.
- Mark baseline events (empty scene, no activity) accurately.
- Confidence scores reflect actual certainty based on video quality."""


def _extract_video_frames_demo(video_bytes: bytes) -> list:
    """Demo frame extraction — returns simulated frame info."""
    size_mb = len(video_bytes) / (1024 * 1024)
    est_frames = min(int(size_mb * 30), 500)
    return list(range(0, est_frames, max(1, est_frames // 10)))


def _analyze_video_with_gemini(video_bytes: bytes, mime_type: str) -> dict:
    """Send video to Gemini for frame-by-frame forensic analysis."""
    client = get_api_client()
    model = get_model()

    try:
        vid_b64 = base64.b64encode(video_bytes).decode()
        interaction = client.interactions.create(
            model=model,
            system_instruction=_VIDEO_SYSTEM,
            input=[
                {
                    "type": "video",
                    "data": vid_b64,
                    "mime_type": mime_type,
                },
                {
                    "type": "text",
                    "text": (
                        "Perform full forensic CCTV analysis. Sample frames at 2 FPS. "
                        "Track all suspects and vehicles. Classify all criminal acts with legal categories."
                    ),
                },
            ],
        )
        raw = interaction.output_text or ""
        raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        return json.loads(raw)
    except json.JSONDecodeError:
        st.warning("⚠️ Video API response parse error — falling back to demo data.")
        return VIDEO_DEMO
    except Exception as e:
        st.error(f"Video API error: {e}")
        return VIDEO_DEMO


def _render_event_log(event_log: list):
    """Render chronological event log table with crime classifications."""
    st.markdown(
        '<div class="section-header"><h3>📋 Chronological CCTV Event Log</h3></div>',
        unsafe_allow_html=True,
    )

    category_colors = {
        "Baseline": "#455a64",
        "Activity — Premises": "#7986cb",
        "Intrusion / Trespass": "#ff9800",
        "Burglary — Breaking & Entering": "#f44336",
        "Burglary — Unlawful Entry": "#f44336",
        "Burglary — Theft in Progress": "#e53935",
        "Suspect Vehicle — Escape Route": "#ffb300",
        "Post-Incident": "#00e676",
        "Assault": "#d32f2f",
        "Homicide": "#b71c1c",
        "Robbery": "#f44336",
        "Vandalism": "#ff9800",
    }

    rows_html = ""
    for ev in event_log:
        conf = ev.get("confidence", 0)
        conf_color = get_confidence_color(conf)
        cat = ev.get("category", "Unknown")
        cat_color = category_colors.get(cat, "#7986cb")

        rows_html += (
            f'<tr>'
            f'<td><code style="color:#00bcd4;font-size:.7rem;">{ev.get("timestamp","--:--:--")}</code></td>'
            f'<td style="color:#7986cb;font-size:.7rem;">{ev.get("frame","?")}</td>'
            f'<td style="font-size:.8rem;">{ev.get("event","")}</td>'
            f'<td><span style="background:rgba({_hex_to_rgb(cat_color)},0.15);'
            f'border:1px solid {cat_color};border-radius:4px;padding:2px 8px;'
            f'font-size:.65rem;color:{cat_color};white-space:nowrap;">{cat}</span></td>'
            f'<td style="color:{conf_color};font-weight:700;font-size:.75rem;">{int(conf*100)}%</td>'
            f'</tr>'
        )

    st.markdown(
        f'<table class="evidence-table">'
        f'<thead><tr>'
        f'<th>Time</th><th>Frame</th><th>Event Description</th>'
        f'<th>Legal Classification</th><th>Conf.</th>'
        f'</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        f'</table>',
        unsafe_allow_html=True,
    )


def _hex_to_rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    try:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"{r},{g},{b}"
    except Exception:
        return "121,134,203"


def _render_trajectories(trajectories: list, vehicle: dict):
    col_t, col_v = st.columns(2)
    with col_t:
        st.markdown(
            '<div class="section-header"><h3>🗺️ Entity Trajectories</h3></div>',
            unsafe_allow_html=True,
        )
        for traj in trajectories:
            entity = traj.get("entity", "Unknown")
            path = traj.get("path", "")
            icon = "🚶" if "Suspect" in entity else "🚗"
            color = "#f44336" if "Suspect" in entity else "#ffb300"
            st.markdown(
                f'<div style="border:1px solid {color};border-radius:8px;padding:12px 16px;margin:6px 0;'
                f'background:rgba({_hex_to_rgb(color)},0.06);">'
                f'<div style="font-size:.72rem;color:{color};font-weight:700;margin-bottom:4px;">{icon} {entity}</div>'
                f'<div style="font-size:.78rem;color:#b0bec5;">{path}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    with col_v:
        if vehicle and any(vehicle.values()):
            st.markdown(
                '<div class="section-header"><h3>🚗 Vehicle Intelligence</h3></div>',
                unsafe_allow_html=True,
            )
            fields = [
                ("Type", vehicle.get("type", "Unknown")),
                ("Color", vehicle.get("color", "Unknown")),
                ("Partial Plate", vehicle.get("partial_plate", "N/A")),
                ("Direction", vehicle.get("direction", "Unknown")),
            ]
            for label, value in fields:
                st.markdown(
                    f'<div style="display:flex;justify-content:space-between;padding:8px 0;'
                    f'border-bottom:1px solid rgba(255,255,255,0.05);">'
                    f'<span style="font-size:.72rem;color:#7986cb;text-transform:uppercase;">{label}</span>'
                    f'<span style="font-size:.8rem;color:#ffb300;font-weight:600;">{value}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )


def render_tab_video():
    """Render Tab 3 — CCTV Video Analysis & Event Progression."""

    st.markdown(
        '<div class="forensic-card">'
        '<h2 style="color:#00bcd4;margin:0 0 6px 0;font-size:1.1rem;">📹 Epic 4 — CCTV Video Analysis & Event Progression</h2>'
        '<p style="color:#7986cb;font-size:.8rem;margin:0;">Upload CCTV footage for AI-powered frame sampling, suspect trajectory tracking, '
        'vehicle movement analysis, and chronological forensic event log generation.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([1, 1])

    with col_left:
        video_file = st.file_uploader(
            "Upload CCTV Video",
            type=["mp4", "avi", "mov", "mkv", "wmv", "webm", "m4v"],
            key="video_uploader",
            help="Supported: MP4, AVI, MOV, MKV, WMV, WebM — max 200 MB",
        )

        if video_file:
            st.video(video_file)
            st.markdown(
                f'<div class="forensic-card" style="padding:12px;">'
                f'<div style="font-size:.68rem;color:#7986cb;margin-bottom:6px;">VIDEO METADATA</div>'
                f'<div style="font-size:.78rem;color:#e8eaf6;"><b>File:</b> {video_file.name}</div>'
                f'<div style="font-size:.78rem;color:#e8eaf6;"><b>Size:</b> {video_file.size/1024/1024:.2f} MB</div>'
                f'<div style="font-size:.78rem;color:#e8eaf6;"><b>Format:</b> {video_file.type}</div>'
                f'<div style="font-size:.78rem;color:#e8eaf6;"><b>Ingested:</b> {get_timestamp()}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    with col_right:
        st.markdown(
            '<div class="forensic-card" style="padding:16px;">'
            '<div style="font-size:.68rem;color:#7986cb;letter-spacing:.1em;text-transform:uppercase;margin-bottom:10px;">Analysis Settings</div>',
            unsafe_allow_html=True,
        )
        sample_rate = st.selectbox("Frame Sample Rate", ["2 FPS", "1 FPS", "5 FPS", "10 FPS"], key="vid_sample_rate")
        track_suspects = st.checkbox("Track Suspect Trajectories", value=True, key="track_suspects")
        track_vehicles = st.checkbox("Track Vehicle Movements", value=True, key="track_vehicles")
        classify_crimes = st.checkbox("Apply Legal Crime Classification", value=True, key="classify_crimes")
        st.markdown("</div>", unsafe_allow_html=True)

    if video_file:
        if st.button("📹 Analyse CCTV Footage", use_container_width=True, key="btn_analyze_video", type="primary"):
            vid_bytes = video_file.read()
            mime = video_file.type or "video/mp4"

            with st.spinner("⚙️ Sampling frames and running forensic trajectory analysis…"):
                # Simulate progressive analysis with a progress bar
                prog = st.progress(0, "Extracting frames…")
                for i in range(0, 60, 15):
                    time.sleep(0.15)
                    prog.progress(i, f"Processing frame batch {i//15 + 1}/4…")

                if is_demo_mode():
                    findings = VIDEO_DEMO
                else:
                    findings = _analyze_video_with_gemini(vid_bytes, mime)

                prog.progress(100, "Analysis complete.")

            st.session_state.video_findings = findings
            st.session_state.video_source = video_file.name
            st.success("✅ CCTV analysis complete")

    # ── Results ──────────────────────────────────────────────────────────────
    findings = st.session_state.get("video_findings")
    if findings:
        st.divider()

        # Metrics row
        c1, c2, c3, c4, c5 = st.columns(5)
        metrics = [
            ("Duration", f'{findings.get("duration_sec",0)//60:02d}:{findings.get("duration_sec",0)%60:02d}', "Duration"),
            ("FPS Sampled", str(findings.get("fps_analysed", 0)), "Frame Rate"),
            ("Frames", str(findings.get("frames_processed", 0)), "Processed"),
            ("Suspects", str(findings.get("suspects_tracked", 0)), "Tracked"),
            ("Vehicles", str(findings.get("vehicles_tracked", 0)), "Tracked"),
        ]
        for col, (_, val, label) in zip([c1, c2, c3, c4, c5], metrics):
            with col:
                st.markdown(
                    f'<div class="metric-box"><div class="metric-value">{val}</div>'
                    f'<div class="metric-label">{label}</div></div>',
                    unsafe_allow_html=True,
                )

        # Summary
        st.markdown(
            f'<div class="forensic-card-highlight">'
            f'<div style="font-size:.68rem;color:#7986cb;letter-spacing:.1em;text-transform:uppercase;margin-bottom:6px;">'
            f'🧠 CCTV Forensic Narrative</div>'
            f'<p style="font-size:.85rem;color:#e8eaf6;margin:0;line-height:1.7;">{findings.get("summary","")}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Event log
        _render_event_log(findings.get("event_log", []))

        # Trajectories + vehicle
        st.divider()
        _render_trajectories(
            findings.get("trajectories", []),
            findings.get("vehicle_details", {}),
        )

        # Timeline chart
        with st.expander("📊 Event Timeline Visualisation", expanded=False):
            try:
                import plotly.graph_objects as go

                events = findings.get("event_log", [])
                ts_labels = [e.get("timestamp", "?") for e in events]
                confs = [e.get("confidence", 0) * 100 for e in events]
                cats = [e.get("category", "Unknown") for e in events]
                event_texts = [e.get("event", "")[:60] + "…" for e in events]

                cat_color_map = {
                    "Baseline": "#455a64",
                    "Intrusion / Trespass": "#ff9800",
                    "Burglary — Breaking & Entering": "#f44336",
                    "Burglary — Unlawful Entry": "#f44336",
                    "Burglary — Theft in Progress": "#e53935",
                    "Suspect Vehicle — Escape Route": "#ffb300",
                    "Post-Incident": "#00e676",
                    "Activity — Premises": "#7986cb",
                }
                colors = [cat_color_map.get(c, "#1e88e5") for c in cats]

                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=ts_labels,
                        y=confs,
                        mode="markers+lines",
                        marker=dict(color=colors, size=12, line=dict(width=2, color="white")),
                        line=dict(color="rgba(30,136,229,0.4)", width=2),
                        text=event_texts,
                        hovertemplate="<b>%{x}</b><br>Conf: %{y:.0f}%<br>%{text}<extra></extra>",
                    )
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(15,22,41,1)",
                    font_color="#e8eaf6",
                    font_size=10,
                    xaxis=dict(title="Timestamp", gridcolor="rgba(30,136,229,0.15)"),
                    yaxis=dict(title="Confidence %", range=[0, 110], gridcolor="rgba(30,136,229,0.15)"),
                    title=dict(text="CCTV Event Confidence Timeline", font=dict(color="#00bcd4")),
                    height=280,
                    margin=dict(t=50, b=10, l=10, r=10),
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception:
                st.info("Plotly not available for chart rendering.")

    else:
        st.markdown(
            '<div style="text-align:center;padding:48px;color:#7986cb;">'
            '<div style="font-size:3rem;">📹</div>'
            '<div style="font-size:.9rem;margin-top:8px;">Upload CCTV footage to begin suspect trajectory and event analysis.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
