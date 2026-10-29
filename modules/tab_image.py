"""
modules/tab_image.py — Tab 1: Crime Scene Visual Evidence Tagger (Epic 2)

Multimodal object detection simulating RT-DETR with Gemini Vision analysis.
"""

import io
import json
import base64
import streamlit as st
from PIL import Image

from modules.config import get_api_client, get_model, is_demo_mode
from modules.demo_data import (
    IMAGE_DEMO,
    get_threat_color,
    get_confidence_color,
    confidence_bar_html,
)
from modules.custody import custody_log_entry, get_timestamp


# ── Gemini system prompt ──────────────────────────────────────────────────────
_SYSTEM_PROMPT = """You are a senior forensic image analyst AI integrated into the CrimeVision AI platform.
Analyze the uploaded crime scene photograph with the precision of an RT-DETR-based multimodal detector.

You MUST return ONLY valid JSON matching this exact schema (no markdown fences, no prose):
{
  "threat_level": "<LOW|MEDIUM|HIGH|CRITICAL>",
  "scene_classification": "<Burglary|Homicide|Vandalism|Assault|Robbery|Unknown>",
  "confidence": <0.0-1.0>,
  "summary": "<2-3 sentence forensic narrative>",
  "detected_objects": [
    {
      "id": "OBJ-NNN",
      "label": "<Person|Firearm|Edged Weapon|Blood Spatter|Forced Entry|Vehicle|Drug Paraphernalia|Other>",
      "confidence": <0.0-1.0>,
      "bbox": [x1, y1, x2, y2],
      "notes": "<specific forensic observation>"
    }
  ],
  "investigative_leads": [
    {
      "priority": <1-10>,
      "lead": "<actionable investigative step>"
    }
  ]
}

Rules:
- Detect ALL forensically significant items with high specificity.
- Assign realistic confidence scores (not uniformly high).
- BBox coordinates should be approximate pixel values if discernible, otherwise estimate.
- Leads must be actionable, specific, and prioritised by urgency.
- Never hallucinate items not visible in the image.
- Classify threat level based on weapon presence, injury indicators, and scene severity."""


def _analyze_with_gemini(image_bytes: bytes, mime_type: str) -> dict:
    """Send image to Gemini Vision API and parse JSON response."""
    client = get_api_client()
    model = get_model()

    try:
        img_b64 = base64.b64encode(image_bytes).decode()
        interaction = client.interactions.create(
            model=model,
            system_instruction=_SYSTEM_PROMPT,
            input=[
                {
                    "type": "image",
                    "data": img_b64,
                    "mime_type": mime_type,
                },
                {
                    "type": "text",
                    "text": "Perform full forensic RT-DETR object detection analysis on this crime scene image.",
                },
            ],
        )
        raw = interaction.output_text or ""
        # Strip possible markdown code fences
        raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        return json.loads(raw)
    except json.JSONDecodeError:
        st.warning("⚠️ API response parse error — falling back to demo data.")
        return IMAGE_DEMO
    except Exception as e:
        st.error(f"API error: {e}")
        return IMAGE_DEMO


def _render_threat_badge(level: str):
    color = get_threat_color(level)
    icons = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}
    icon = icons.get(level.upper(), "⚪")
    st.markdown(
        f'<div style="display:inline-block;background:rgba({_hex_to_rgb(color)},0.15);'
        f'border:2px solid {color};border-radius:8px;padding:10px 24px;margin:8px 0;">'
        f'<span style="font-size:1.8rem;">{icon}</span>'
        f'<span style="font-size:1.2rem;font-weight:800;color:{color};'
        f'letter-spacing:.1em;margin-left:10px;text-transform:uppercase;">THREAT: {level}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _hex_to_rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"{r},{g},{b}"


def _render_detections(objects: list):
    """Render detection results as an interactive evidence table."""
    st.markdown(
        '<div class="section-header"><h3>🎯 Detected Objects & Evidence Items</h3></div>',
        unsafe_allow_html=True,
    )

    rows_html = ""
    for obj in objects:
        conf = obj.get("confidence", 0)
        color = get_confidence_color(conf)
        pct = int(conf * 100)
        bar = (
            f'<div class="conf-bar-wrap" style="width:80px;display:inline-block;">'
            f'<div class="conf-bar" style="width:{pct}%;background:{color};"></div></div>'
            f'<span style="color:{color};font-size:.72rem;margin-left:6px;">{pct}%</span>'
        )
        bbox = obj.get("bbox", [])
        bbox_str = f"[{bbox[0]},{bbox[1]}]→[{bbox[2]},{bbox[3]}]" if len(bbox) == 4 else "N/A"

        rows_html += (
            f'<tr>'
            f'<td><code style="color:#00bcd4;">{obj.get("id","---")}</code></td>'
            f'<td style="font-weight:600;">{obj.get("label","Unknown")}</td>'
            f'<td>{bar}</td>'
            f'<td><code style="font-size:.68rem;">{bbox_str}</code></td>'
            f'<td style="color:#b0bec5;font-size:.78rem;">{obj.get("notes","")}</td>'
            f'</tr>'
        )

    st.markdown(
        f'<table class="evidence-table">'
        f'<thead><tr>'
        f'<th>ID</th><th>Label</th><th>Confidence</th><th>Spatial (px)</th><th>Forensic Notes</th>'
        f'</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        f'</table>',
        unsafe_allow_html=True,
    )


def _render_leads(leads: list):
    st.markdown(
        '<div class="section-header"><h3>🔎 Prioritised Investigative Leads</h3></div>',
        unsafe_allow_html=True,
    )
    sorted_leads = sorted(leads, key=lambda x: x.get("priority", 99))
    for lead in sorted_leads:
        pri = lead.get("priority", "?")
        color = "#f44336" if pri <= 2 else "#ffb300" if pri <= 4 else "#00bcd4"
        st.markdown(
            f'<div style="display:flex;gap:12px;align-items:flex-start;margin:6px 0;'
            f'background:rgba(255,255,255,0.03);border-radius:6px;padding:10px 14px;'
            f'border-left:3px solid {color};">'
            f'<span style="color:{color};font-weight:800;font-size:1.1rem;min-width:24px;">#{pri}</span>'
            f'<span style="font-size:.82rem;color:#e8eaf6;">{lead.get("lead","")}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


def render_tab_image():
    """Render Tab 1 — Crime Scene Visual Evidence Tagger."""

    st.markdown(
        '<div class="forensic-card">'
        '<h2 style="color:#00bcd4;margin:0 0 6px 0;font-size:1.1rem;">🖼️ Epic 2 — Crime Scene Visual Evidence Tagger</h2>'
        '<p style="color:#7986cb;font-size:.8rem;margin:0;">Upload a crime scene photograph for AI-powered multimodal object detection. '
        'Simulates RT-DETR detection of persons, firearms, edged weapons, blood spatter, and forced entry points.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    col_upload, col_preview = st.columns([1, 1])

    with col_upload:
        uploaded_file = st.file_uploader(
            "Upload Crime Scene Image",
            type=["jpg", "jpeg", "png", "bmp", "tiff", "webp"],
            key="image_uploader",
            help="Supported: JPG, PNG, BMP, TIFF, WebP — max 200 MB",
        )

        if uploaded_file:
            st.markdown(
                f'<div class="forensic-card" style="padding:12px;">'
                f'<div style="font-size:.68rem;color:#7986cb;margin-bottom:6px;">FILE METADATA</div>'
                f'<div style="font-size:.78rem;color:#e8eaf6;"><b>Name:</b> {uploaded_file.name}</div>'
                f'<div style="font-size:.78rem;color:#e8eaf6;"><b>Size:</b> {uploaded_file.size/1024:.1f} KB</div>'
                f'<div style="font-size:.78rem;color:#e8eaf6;"><b>Type:</b> {uploaded_file.type}</div>'
                f'<div style="font-size:.78rem;color:#e8eaf6;"><b>Ingested:</b> {get_timestamp()}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            analyze_btn = st.button(
                "🔍 Analyse Crime Scene",
                use_container_width=True,
                key="btn_analyze_image",
                type="primary",
            )

            if analyze_btn:
                img_bytes = uploaded_file.read()
                mime = uploaded_file.type or "image/jpeg"
                with st.spinner("⚙️ Running forensic RT-DETR analysis…"):
                    if is_demo_mode():
                        findings = IMAGE_DEMO
                    else:
                        findings = _analyze_with_gemini(img_bytes, mime)

                st.session_state.image_findings = findings
                # Store source reference for chain-of-custody
                st.session_state.image_source = uploaded_file.name
                st.success("✅ Analysis complete — results below")

    with col_preview:
        if uploaded_file:
            try:
                uploaded_file.seek(0)
                img = Image.open(uploaded_file)
                st.image(img, caption=f"📷 {uploaded_file.name}", use_container_width=True)
            except Exception:
                st.warning("Preview unavailable")

    # ── Results ────────────────────────────────────────────────────────────
    findings = st.session_state.get("image_findings")
    if findings:
        st.divider()
        st.markdown(
            '<div class="section-header"><h3>📊 Forensic Analysis Report</h3></div>',
            unsafe_allow_html=True,
        )

        # Metrics row
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            _render_threat_badge(findings.get("threat_level", "UNKNOWN"))
        with c2:
            st.markdown(
                f'<div class="metric-box">'
                f'<div class="metric-value">{findings.get("scene_classification","N/A")}</div>'
                f'<div class="metric-label">Scene Classification</div></div>',
                unsafe_allow_html=True,
            )
        with c3:
            obj_count = len(findings.get("detected_objects", []))
            st.markdown(
                f'<div class="metric-box">'
                f'<div class="metric-value">{obj_count}</div>'
                f'<div class="metric-label">Items Detected</div></div>',
                unsafe_allow_html=True,
            )
        with c4:
            conf_pct = int(findings.get("confidence", 0) * 100)
            st.markdown(
                f'<div class="metric-box">'
                f'<div class="metric-value">{conf_pct}%</div>'
                f'<div class="metric-label">Scene Confidence</div></div>',
                unsafe_allow_html=True,
            )

        # Summary
        st.markdown(
            f'<div class="forensic-card-highlight">'
            f'<div style="font-size:.68rem;color:#7986cb;letter-spacing:.1em;text-transform:uppercase;margin-bottom:6px;">'
            f'🧠 AI Forensic Narrative</div>'
            f'<p style="font-size:.85rem;color:#e8eaf6;margin:0;line-height:1.7;">{findings.get("summary","")}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Detections table
        _render_detections(findings.get("detected_objects", []))

        # Investigative leads
        _render_leads(findings.get("investigative_leads", []))

        # Confidence overview chart
        with st.expander("📈 Confidence Score Breakdown", expanded=False):
            objects = findings.get("detected_objects", [])
            if objects:
                import plotly.graph_objects as go
                labels = [o.get("label", "?") for o in objects]
                confs = [o.get("confidence", 0) for o in objects]
                colors = [get_confidence_color(c) for c in confs]
                fig = go.Figure(
                    go.Bar(
                        x=labels,
                        y=[c * 100 for c in confs],
                        marker_color=colors,
                        text=[f"{c*100:.0f}%" for c in confs],
                        textposition="outside",
                    )
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(15,22,41,1)",
                    font_color="#e8eaf6",
                    font_size=11,
                    yaxis=dict(range=[0, 110], gridcolor="rgba(30,136,229,0.15)"),
                    xaxis=dict(tickfont=dict(size=10)),
                    title=dict(text="Detection Confidence by Object", font=dict(color="#00bcd4")),
                    margin=dict(t=50, b=10, l=10, r=10),
                    height=300,
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown(
            '<div style="text-align:center;padding:48px;color:#7986cb;">'
            '<div style="font-size:3rem;">🖼️</div>'
            '<div style="font-size:.9rem;margin-top:8px;">Upload a crime scene image and click Analyse to begin.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
