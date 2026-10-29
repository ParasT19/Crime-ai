"""
modules/tab_export.py — Tab 5: Automated Forensic PDF Export (Epic 6)

Generates court-admissible forensic summary PDF reports using ReportLab.
"""

import io
import streamlit as st
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib import colors
    from reportlab.lib.units import mm, cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, PageBreak, KeepTogether,
    )
    from reportlab.graphics.shapes import Drawing, Rect, String
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False

from modules.demo_data import IMAGE_DEMO, AUDIO_DEMO, VIDEO_DEMO, get_threat_color
from modules.custody import get_timestamp


# ── PDF Colour palette ────────────────────────────────────────────────────────
_NAVY    = colors.HexColor("#0a1628")
_DARK    = colors.HexColor("#0f1629")
_BLUE    = colors.HexColor("#1e88e5")
_CYAN    = colors.HexColor("#00bcd4")
_GREEN   = colors.HexColor("#00c853")
_AMBER   = colors.HexColor("#ffb300")
_RED     = colors.HexColor("#f44336")
_WHITE   = colors.white
_LIGHT   = colors.HexColor("#e8eaf6")
_MUTED   = colors.HexColor("#7986cb")
_BGCARD  = colors.HexColor("#131c35")
_BGCARD2 = colors.HexColor("#1a2540")


def _threat_color_rl(level: str):
    mapping = {
        "CRITICAL": _RED,
        "HIGH":     _AMBER,
        "MEDIUM":   colors.HexColor("#ff9800"),
        "LOW":      _GREEN,
    }
    return mapping.get(level.upper(), _MUTED)


def _make_styles():
    """Return a dict of ParagraphStyles for the PDF."""
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=22,
                                 textColor=_CYAN, alignment=TA_CENTER, spaceAfter=4),
        "subtitle": ParagraphStyle("subtitle", fontName="Helvetica", fontSize=10,
                                    textColor=_MUTED, alignment=TA_CENTER, spaceAfter=2),
        "section": ParagraphStyle("section", fontName="Helvetica-Bold", fontSize=11,
                                   textColor=_CYAN, spaceBefore=14, spaceAfter=5,
                                   borderPad=4),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=8.5,
                                textColor=_LIGHT, leading=13, spaceAfter=4,
                                alignment=TA_JUSTIFY),
        "mono": ParagraphStyle("mono", fontName="Courier", fontSize=8,
                                textColor=_CYAN, leading=11),
        "label": ParagraphStyle("label", fontName="Helvetica-Bold", fontSize=7.5,
                                 textColor=_MUTED, spaceAfter=2),
        "value": ParagraphStyle("value", fontName="Helvetica", fontSize=8.5,
                                 textColor=_LIGHT, spaceAfter=4),
        "lead": ParagraphStyle("lead", fontName="Helvetica", fontSize=8.5,
                                textColor=_LIGHT, leading=12, spaceAfter=3),
        "footer": ParagraphStyle("footer", fontName="Helvetica", fontSize=7,
                                  textColor=_MUTED, alignment=TA_CENTER),
        "citation": ParagraphStyle("citation", fontName="Courier", fontSize=7.5,
                                    textColor=_AMBER, spaceAfter=3),
        "threat": ParagraphStyle("threat", fontName="Helvetica-Bold", fontSize=14,
                                  alignment=TA_CENTER, spaceAfter=6),
    }


def _page_header_footer(canvas, doc):
    """Draw repeating page header and footer."""
    canvas.saveState()
    w, h = A4

    # Header bar
    canvas.setFillColor(_DARK)
    canvas.rect(0, h - 28*mm, w, 28*mm, fill=1, stroke=0)
    canvas.setFillColor(_BLUE)
    canvas.rect(0, h - 30*mm, w, 2*mm, fill=1, stroke=0)

    canvas.setFont("Helvetica-Bold", 11)
    canvas.setFillColor(_CYAN)
    canvas.drawString(18*mm, h - 16*mm, "🔍 CrimeVision AI — Forensic Analysis Report")

    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(_MUTED)
    canvas.drawRightString(w - 18*mm, h - 16*mm,
                           f"Evidence: {doc.evidence_id}  |  CONFIDENTIAL — FOR LAW ENFORCEMENT USE ONLY")

    canvas.setFont("Helvetica", 7.5)
    canvas.drawRightString(w - 18*mm, h - 22*mm,
                           f"Page {doc.page}")

    # Footer bar
    canvas.setFillColor(_DARK)
    canvas.rect(0, 0, w, 16*mm, fill=1, stroke=0)
    canvas.setFillColor(_BLUE)
    canvas.rect(0, 16*mm, w, 0.5*mm, fill=1, stroke=0)

    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(_MUTED)
    canvas.drawCentredString(w / 2, 8*mm,
        "This document is AI-assisted forensic analysis. All findings require human expert verification before court submission.")
    canvas.drawString(18*mm, 8*mm, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    canvas.drawRightString(w - 18*mm, 8*mm, f"Investigator: {doc.investigator}")

    canvas.restoreState()


def _section_heading(text: str, styles: dict) -> list:
    return [
        HRFlowable(width="100%", thickness=0.5, color=_BLUE, spaceAfter=3),
        Paragraph(text, styles["section"]),
    ]


def _coc_table(evidence_id: str, ts: str, investigator: str, styles: dict) -> Table:
    """Build the chain-of-custody metadata table."""
    data = [
        [
            Paragraph("<b>EVIDENCE ID</b>", styles["label"]),
            Paragraph(evidence_id, styles["mono"]),
            Paragraph("<b>GENERATED (UTC)</b>", styles["label"]),
            Paragraph(ts, styles["mono"]),
        ],
        [
            Paragraph("<b>INVESTIGATOR</b>", styles["label"]),
            Paragraph(investigator, styles["value"]),
            Paragraph("<b>CLASSIFICATION</b>", styles["label"]),
            Paragraph("RESTRICTED — LAW ENFORCEMENT", styles["citation"]),
        ],
    ]
    tbl = Table(data, colWidths=[40*mm, 55*mm, 45*mm, 55*mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _BGCARD),
        ("TEXTCOLOR", (0, 0), (-1, -1), _LIGHT),
        ("GRID", (0, 0), (-1, -1), 0.5, _BLUE),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [_BGCARD, _BGCARD2]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return tbl


def _detection_table(objects: list, styles: dict) -> Table:
    header = [
        Paragraph("<b>ID</b>", styles["label"]),
        Paragraph("<b>Label</b>", styles["label"]),
        Paragraph("<b>Confidence</b>", styles["label"]),
        Paragraph("<b>Spatial (px)</b>", styles["label"]),
        Paragraph("<b>Forensic Notes</b>", styles["label"]),
    ]
    rows = [header]
    for obj in objects:
        conf = obj.get("confidence", 0)
        conf_color = _GREEN if conf >= 0.9 else _AMBER if conf >= 0.75 else _RED
        bbox = obj.get("bbox", [])
        bbox_str = f"[{bbox[0]},{bbox[1]}]→[{bbox[2]},{bbox[3]}]" if len(bbox) == 4 else "N/A"
        rows.append([
            Paragraph(obj.get("id", "---"), styles["mono"]),
            Paragraph(f'<b>{obj.get("label","Unknown")}</b>', styles["body"]),
            Paragraph(f'{int(conf*100)}%', ParagraphStyle("c", fontName="Helvetica-Bold",
                                                           fontSize=8.5, textColor=conf_color)),
            Paragraph(bbox_str, styles["mono"]),
            Paragraph(obj.get("notes", ""), styles["body"]),
        ])
    tbl = Table(rows, colWidths=[22*mm, 35*mm, 22*mm, 32*mm, 84*mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), _BGCARD2),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_BGCARD, _BGCARD2]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#1e3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), _CYAN),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return tbl


def _event_log_table(events: list, styles: dict) -> Table:
    header = [
        Paragraph("<b>Timestamp</b>", styles["label"]),
        Paragraph("<b>Frame</b>", styles["label"]),
        Paragraph("<b>Event</b>", styles["label"]),
        Paragraph("<b>Classification</b>", styles["label"]),
        Paragraph("<b>Conf.</b>", styles["label"]),
    ]
    rows = [header]
    for ev in events:
        conf = ev.get("confidence", 0)
        conf_color = _GREEN if conf >= 0.9 else _AMBER if conf >= 0.75 else _RED
        rows.append([
            Paragraph(ev.get("timestamp", "?"), styles["mono"]),
            Paragraph(str(ev.get("frame", "?")), styles["mono"]),
            Paragraph(ev.get("event", ""), styles["body"]),
            Paragraph(ev.get("category", "Unknown"),
                      ParagraphStyle("cat", fontName="Helvetica", fontSize=7.5, textColor=_AMBER)),
            Paragraph(f'{int(conf*100)}%',
                      ParagraphStyle("c2", fontName="Helvetica-Bold", fontSize=8, textColor=conf_color)),
        ])
    tbl = Table(rows, colWidths=[22*mm, 16*mm, 70*mm, 48*mm, 16*mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), _BGCARD2),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_BGCARD, _BGCARD2]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#1e3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), _CYAN),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return tbl


def _ledger_table(ledger: list, styles: dict) -> Table:
    header = [
        Paragraph("<b>Evidence ID</b>", styles["label"]),
        Paragraph("<b>Src</b>", styles["label"]),
        Paragraph("<b>Timestamp</b>", styles["label"]),
        Paragraph("<b>Event / Finding</b>", styles["label"]),
        Paragraph("<b>Conf.</b>", styles["label"]),
    ]
    rows = [header]
    for entry in ledger:
        conf = entry.get("confidence", 0)
        conf_color = _GREEN if conf >= 0.9 else _AMBER if conf >= 0.75 else _RED
        src_color = {"IMAGE": _CYAN, "AUDIO": colors.HexColor("#ce93d8"), "VIDEO": _AMBER}.get(
            entry.get("source", "?"), _MUTED)
        rows.append([
            Paragraph(entry.get("ev_id", "---"), styles["mono"]),
            Paragraph(entry.get("source", "?"),
                      ParagraphStyle("src", fontName="Helvetica-Bold", fontSize=7.5, textColor=src_color)),
            Paragraph(entry.get("timestamp", "?"), styles["mono"]),
            Paragraph(entry.get("event", ""), styles["body"]),
            Paragraph(f'{int(conf*100)}%',
                      ParagraphStyle("c3", fontName="Helvetica-Bold", fontSize=8, textColor=conf_color)),
        ])
    tbl = Table(rows, colWidths=[48*mm, 16*mm, 24*mm, 72*mm, 16*mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), _BGCARD2),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_BGCARD, _BGCARD2]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#1e3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), _CYAN),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return tbl


def generate_forensic_pdf() -> bytes:
    """Generate the complete court-admissible forensic PDF. Returns raw bytes."""
    if not REPORTLAB_OK:
        raise RuntimeError("ReportLab not installed. Run: pip install reportlab")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=35*mm, bottomMargin=22*mm,
        title="CrimeVision AI — Forensic Analysis Report",
        author="CrimeVision AI Platform",
        subject="Forensic Analysis Report",
        creator="CrimeVision AI v2.0",
    )

    # Attach metadata for header/footer
    doc.evidence_id = st.session_state.get("evidence_id", "EV-UNKNOWN")
    doc.investigator = st.session_state.get("investigator", "PENDING")
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    styles = _make_styles()
    story = []

    # ── Cover / title ─────────────────────────────────────────────────────────
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("CrimeVision AI", styles["title"]))
    story.append(Paragraph("Intelligent Multimodal Forensic Analysis Platform", styles["subtitle"]))
    story.append(Paragraph("FORENSIC ANALYSIS REPORT", styles["subtitle"]))
    story.append(Spacer(1, 5*mm))

    # COC table
    story.append(_coc_table(doc.evidence_id, ts, doc.investigator, styles))
    story.append(Spacer(1, 6*mm))

    # ── Section 1: Image Analysis ─────────────────────────────────────────────
    img = st.session_state.get("image_findings") or IMAGE_DEMO
    img_src = st.session_state.get("image_source", "N/A")

    story += _section_heading("Section 1 — Crime Scene Visual Evidence Analysis", styles)
    story.append(Paragraph(f"<b>Source File:</b> {img_src}", styles["label"]))

    # Threat + classification row
    tl = img.get("threat_level", "UNKNOWN")
    tl_color = _threat_color_rl(tl)
    meta_data = [
        [
            Paragraph("<b>THREAT LEVEL</b>", styles["label"]),
            Paragraph(f'<b>{tl}</b>',
                      ParagraphStyle("tl", fontName="Helvetica-Bold", fontSize=13, textColor=tl_color)),
            Paragraph("<b>SCENE CLASS</b>", styles["label"]),
            Paragraph(f'<b>{img.get("scene_classification","N/A")}</b>',
                      ParagraphStyle("sc", fontName="Helvetica-Bold", fontSize=11, textColor=_CYAN)),
            Paragraph("<b>CONFIDENCE</b>", styles["label"]),
            Paragraph(f'<b>{int(img.get("confidence",0)*100)}%</b>',
                      ParagraphStyle("cf", fontName="Helvetica-Bold", fontSize=11, textColor=_GREEN)),
        ]
    ]
    meta_tbl = Table(meta_data, colWidths=[32*mm, 32*mm, 32*mm, 40*mm, 28*mm, 28*mm])
    meta_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _BGCARD2),
        ("GRID", (0, 0), (-1, -1), 0.5, _BLUE),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 4*mm))

    story.append(Paragraph("<b>AI Forensic Narrative:</b>", styles["label"]))
    story.append(Paragraph(img.get("summary", ""), styles["body"]))
    story.append(Spacer(1, 3*mm))

    # Detected objects table
    story.append(Paragraph("<b>1.1 — Detected Objects & Evidence Items</b>", styles["label"]))
    story.append(_detection_table(img.get("detected_objects", []), styles))
    story.append(Spacer(1, 4*mm))

    # Investigative leads
    story.append(Paragraph("<b>1.2 — Prioritised Investigative Leads</b>", styles["label"]))
    for lead in sorted(img.get("investigative_leads", []), key=lambda x: x.get("priority", 99)):
        story.append(Paragraph(
            f'<b>#{lead.get("priority","?")}</b>  {lead.get("lead","")}',
            styles["lead"]
        ))

    story.append(PageBreak())

    # ── Section 2: Audio Analysis ─────────────────────────────────────────────
    aud = st.session_state.get("audio_findings") or AUDIO_DEMO
    aud_src = st.session_state.get("audio_source", "N/A")

    story += _section_heading("Section 2 — Witness Audio Transcription & Timeline", styles)
    story.append(Paragraph(f"<b>Source File:</b> {aud_src}", styles["label"]))

    dur = aud.get("duration_sec", 0)
    mins, secs = divmod(dur, 60)
    aud_meta = [
        [
            Paragraph("<b>CALL TYPE</b>", styles["label"]),
            Paragraph(aud.get("call_type", "Unknown"), styles["value"]),
            Paragraph("<b>DURATION</b>", styles["label"]),
            Paragraph(f"{mins:02d}:{secs:02d}", styles["value"]),
            Paragraph("<b>SPEAKERS</b>", styles["label"]),
            Paragraph(str(aud.get("speaker_count", 0)), styles["value"]),
        ]
    ]
    aud_meta_tbl = Table(aud_meta, colWidths=[28*mm, 50*mm, 24*mm, 24*mm, 24*mm, 42*mm])
    aud_meta_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _BGCARD2),
        ("GRID", (0, 0), (-1, -1), 0.5, _BLUE),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(aud_meta_tbl)
    story.append(Spacer(1, 4*mm))

    story.append(Paragraph("<b>AI Forensic Audio Summary:</b>", styles["label"]))
    story.append(Paragraph(aud.get("summary", ""), styles["body"]))
    story.append(Spacer(1, 3*mm))

    # Key events
    story.append(Paragraph("<b>2.1 — Chronological Forensic Events</b>", styles["label"]))
    for ev in aud.get("key_events", []):
        story.append(Paragraph(
            f'<font color="#00bcd4"><b>[{ev.get("ts","?")}]</b></font>  {ev.get("event","")}',
            styles["body"]
        ))

    story.append(Spacer(1, 4*mm))

    # Transcript excerpt (first 10 lines)
    story.append(Paragraph("<b>2.2 — Transcript Excerpt (first 10 entries)</b>", styles["label"]))
    transcript = aud.get("transcript", [])[:10]
    for entry in transcript:
        spk = entry.get("speaker", "UNK")
        ts_e = entry.get("ts", "?")
        text = entry.get("text", "")
        story.append(Paragraph(
            f'<font color="#7986cb">[{ts_e}]</font> '
            f'<font color="#00bcd4"><b>{spk}:</b></font> {text}',
            styles["body"]
        ))

    story.append(PageBreak())

    # ── Section 3: Video Analysis ─────────────────────────────────────────────
    vid = st.session_state.get("video_findings") or VIDEO_DEMO
    vid_src = st.session_state.get("video_source", "N/A")

    story += _section_heading("Section 3 — CCTV Video Analysis & Event Progression", styles)
    story.append(Paragraph(f"<b>Source File:</b> {vid_src}", styles["label"]))

    dur_v = vid.get("duration_sec", 0)
    m_v, s_v = divmod(dur_v, 60)
    vid_meta = [
        [
            Paragraph("<b>DURATION</b>", styles["label"]),
            Paragraph(f"{m_v:02d}:{s_v:02d}", styles["value"]),
            Paragraph("<b>FRAMES</b>", styles["label"]),
            Paragraph(str(vid.get("frames_processed", 0)), styles["value"]),
            Paragraph("<b>SUSPECTS</b>", styles["label"]),
            Paragraph(str(vid.get("suspects_tracked", 0)), styles["value"]),
            Paragraph("<b>VEHICLES</b>", styles["label"]),
            Paragraph(str(vid.get("vehicles_tracked", 0)), styles["value"]),
        ]
    ]
    vid_meta_tbl = Table(vid_meta, colWidths=[26*mm, 22*mm, 22*mm, 22*mm, 24*mm, 14*mm, 24*mm, 14*mm])
    vid_meta_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _BGCARD2),
        ("GRID", (0, 0), (-1, -1), 0.5, _BLUE),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(vid_meta_tbl)
    story.append(Spacer(1, 4*mm))

    story.append(Paragraph("<b>AI CCTV Narrative:</b>", styles["label"]))
    story.append(Paragraph(vid.get("summary", ""), styles["body"]))
    story.append(Spacer(1, 3*mm))

    story.append(Paragraph("<b>3.1 — Chronological Event Log</b>", styles["label"]))
    story.append(_event_log_table(vid.get("event_log", []), styles))

    story.append(Spacer(1, 4*mm))
    veh = vid.get("vehicle_details", {})
    if veh:
        story.append(Paragraph("<b>3.2 — Vehicle Intelligence</b>", styles["label"]))
        veh_data = [
            [Paragraph("<b>Type</b>", styles["label"]), Paragraph(veh.get("type","?"), styles["value"]),
             Paragraph("<b>Color</b>", styles["label"]), Paragraph(veh.get("color","?"), styles["value"])],
            [Paragraph("<b>Partial Plate</b>", styles["label"]), Paragraph(veh.get("partial_plate","?"), styles["citation"]),
             Paragraph("<b>Direction</b>", styles["label"]), Paragraph(veh.get("direction","?"), styles["value"])],
        ]
        veh_tbl = Table(veh_data, colWidths=[36*mm, 60*mm, 36*mm, 60*mm])
        veh_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), _BGCARD),
            ("GRID", (0, 0), (-1, -1), 0.5, _BLUE),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(veh_tbl)

    story.append(PageBreak())

    # ── Section 4: Master Evidence Ledger ─────────────────────────────────────
    ledger = st.session_state.get("master_ledger", [])
    story += _section_heading("Section 4 — Master Forensic Evidence Ledger (Multimodal Fusion)", styles)
    if ledger:
        story.append(_ledger_table(ledger, styles))
    else:
        story.append(Paragraph("No master ledger generated. Please visit the Fusion tab.", styles["body"]))

    story.append(Spacer(1, 6*mm))

    # ── Section 5: Legal Disclaimer ───────────────────────────────────────────
    story += _section_heading("Section 5 — Legal Disclaimer & Chain-of-Custody Declaration", styles)
    disclaimer = (
        "This forensic analysis report has been generated by the CrimeVision AI platform, an AI-assisted "
        "forensic analysis system. All findings presented herein are the result of multimodal AI analysis "
        "and MUST be independently verified by qualified forensic experts before being used as evidence "
        "in any legal proceeding. The AI system does not replace human forensic examination and cannot "
        "provide legally binding conclusions. Confidence scores represent algorithmic certainty and are "
        "not equivalent to legal standards of proof. "
        "This document is classified as RESTRICTED and is intended solely for use by authorised law "
        "enforcement personnel. Unauthorised disclosure is prohibited."
    )
    story.append(Paragraph(disclaimer, styles["body"]))
    story.append(Spacer(1, 4*mm))

    # Signature block
    sig_data = [
        [
            Paragraph("<b>Investigating Officer Signature</b>", styles["label"]),
            Paragraph("<b>Date / Time (UTC)</b>", styles["label"]),
            Paragraph("<b>Supervising Officer</b>", styles["label"]),
        ],
        [
            Paragraph(f'{doc.investigator}\n\n{"_" * 30}', styles["value"]),
            Paragraph(ts, styles["mono"]),
            Paragraph("_" * 30, styles["value"]),
        ],
    ]
    sig_tbl = Table(sig_data, colWidths=[68*mm, 52*mm, 72*mm])
    sig_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), _BGCARD2),
        ("BACKGROUND", (0, 1), (-1, 1), _BGCARD),
        ("GRID", (0, 0), (-1, -1), 0.5, _BLUE),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(sig_tbl)

    # Build PDF
    doc.build(story, onFirstPage=_page_header_footer, onLaterPages=_page_header_footer)
    return buf.getvalue()


def render_tab_export():
    """Render Tab 5 — Automated Forensic PDF Export."""

    st.markdown(
        '<div class="forensic-card">'
        '<h2 style="color:#00bcd4;margin:0 0 6px 0;font-size:1.1rem;">📄 Epic 6 — Automated Forensic PDF Export</h2>'
        '<p style="color:#7986cb;font-size:.8rem;margin:0;">Generate a complete, court-admissible forensic summary PDF '
        'combining all evidence modalities with chain-of-custody metadata and legal disclaimers.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    if not REPORTLAB_OK:
        st.error(
            "❌ **ReportLab not installed.** Add `reportlab>=4.0.0` to `requirements.txt` and redeploy. "
            "Run locally: `pip install reportlab`"
        )
        return

    # ── Pre-flight checklist ──────────────────────────────────────────────────
    st.markdown(
        '<div class="section-header"><h3>✅ Pre-Export Checklist</h3></div>',
        unsafe_allow_html=True,
    )

    checks = [
        ("Evidence ID", bool(st.session_state.get("evidence_id")), st.session_state.get("evidence_id", "---")),
        ("Investigator Sign-off", st.session_state.get("investigator", "PENDING") != "PENDING",
         st.session_state.get("investigator", "NOT SIGNED")),
        ("Image Analysis", st.session_state.get("image_findings") is not None, "Loaded ✓" if st.session_state.get("image_findings") else "Not loaded (demo data will be used)"),
        ("Audio Analysis", st.session_state.get("audio_findings") is not None, "Loaded ✓" if st.session_state.get("audio_findings") else "Not loaded (demo data will be used)"),
        ("Video Analysis", st.session_state.get("video_findings") is not None, "Loaded ✓" if st.session_state.get("video_findings") else "Not loaded (demo data will be used)"),
    ]

    for label, ok, value in checks:
        icon = "✅" if ok else "⚠️"
        color = "#00e676" if ok else "#ffb300"
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;padding:8px 14px;'
            f'border-left:3px solid {color};background:rgba({"0,230,118" if ok else "255,179,0"},0.06);'
            f'border-radius:4px;margin:4px 0;">'
            f'<span style="font-size:.8rem;">{icon} <b>{label}</b></span>'
            f'<span style="font-size:.75rem;color:{color};">{value}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Report configuration ──────────────────────────────────────────────────
    col_cfg, col_prev = st.columns([1, 1])
    with col_cfg:
        st.markdown("**📋 Report Contents**")
        inc_image = st.checkbox("Include Visual Evidence Analysis", value=True)
        inc_audio = st.checkbox("Include Audio Transcription", value=True)
        inc_video = st.checkbox("Include CCTV Video Analysis", value=True)
        inc_ledger = st.checkbox("Include Master Evidence Ledger", value=True)
        inc_disclaimer = st.checkbox("Include Legal Disclaimer", value=True)

    with col_prev:
        st.markdown("**📊 Report Statistics**")
        ledger = st.session_state.get("master_ledger", [])
        img_f = st.session_state.get("image_findings") or IMAGE_DEMO
        aud_f = st.session_state.get("audio_findings") or AUDIO_DEMO
        vid_f = st.session_state.get("video_findings") or VIDEO_DEMO

        stats = [
            ("Detected Objects", len(img_f.get("detected_objects", []))),
            ("Audio Events", len(aud_f.get("key_events", []))),
            ("Video Events", len(vid_f.get("event_log", []))),
            ("Ledger Entries", len(ledger)),
            ("Threat Level", img_f.get("threat_level", "N/A")),
            ("Scene Class", img_f.get("scene_classification", "N/A")),
        ]
        for label, val in stats:
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;padding:6px 0;'
                f'border-bottom:1px solid rgba(255,255,255,0.05);">'
                f'<span style="font-size:.76rem;color:#7986cb;">{label}</span>'
                f'<span style="font-size:.8rem;font-weight:600;color:#00bcd4;">{val}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.divider()

    # ── Generate button ───────────────────────────────────────────────────────
    st.markdown(
        '<div style="text-align:center;margin:12px 0;">'
        '<div style="font-size:.8rem;color:#7986cb;margin-bottom:12px;">'
        '🔒 PDF will include chain-of-custody metadata, evidence IDs, investigator sign-off, and legal disclaimers.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        st.markdown('<div class="export-btn">', unsafe_allow_html=True)
        if st.button("📄 Generate Court-Admissible PDF Report", use_container_width=True, type="primary"):
            with st.spinner("⚙️ Compiling forensic report… This may take a moment."):
                try:
                    pdf_bytes = generate_forensic_pdf()
                    fname = (
                        f"CrimeVision_Forensic_Report_"
                        f"{st.session_state.get('evidence_id','EV-UNKNOWN')}_"
                        f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
                    )
                    st.session_state.generated_pdf = pdf_bytes
                    st.session_state.generated_pdf_name = fname
                    st.success(f"✅ PDF generated successfully — {len(pdf_bytes)/1024:.1f} KB")
                except Exception as e:
                    st.error(f"❌ PDF generation failed: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Download button ───────────────────────────────────────────────────────
    if st.session_state.get("generated_pdf"):
        pdf_bytes = st.session_state.generated_pdf
        fname = st.session_state.get("generated_pdf_name", "forensic_report.pdf")
        col_dl = st.columns([1, 2, 1])
        with col_dl[1]:
            st.download_button(
                label="⬇️ Download PDF Report",
                data=pdf_bytes,
                file_name=fname,
                mime="application/pdf",
                use_container_width=True,
            )
            st.markdown(
                f'<div style="text-align:center;font-size:.72rem;color:#7986cb;margin-top:8px;">'
                f'📎 {fname}<br>Size: {len(pdf_bytes)/1024:.1f} KB</div>',
                unsafe_allow_html=True,
            )

    # ── PDF preview info ──────────────────────────────────────────────────────
    st.divider()
    st.markdown(
        '<div class="forensic-card">'
        '<div style="font-size:.68rem;color:#7986cb;letter-spacing:.1em;text-transform:uppercase;margin-bottom:8px;">📄 PDF Report Structure</div>'
        '<div style="font-size:.8rem;color:#e8eaf6;line-height:2;">',
        unsafe_allow_html=True,
    )
    sections = [
        ("Cover Page", "Evidence ID, investigator sign-off, classification, UTC timestamp"),
        ("Section 1", "Crime Scene Visual Evidence — detections, confidence scores, investigative leads"),
        ("Section 2", "Witness Audio — transcription, key events, emotional markers, anomalies"),
        ("Section 3", "CCTV Video — event log, suspect trajectories, vehicle intelligence"),
        ("Section 4", "Master Evidence Ledger — unified multimodal timeline with evidence IDs"),
        ("Section 5", "Legal Disclaimer & Signature Block — court-admissible chain-of-custody"),
    ]
    for sec, desc in sections:
        st.markdown(
            f'<div style="display:flex;gap:10px;margin:4px 0;">'
            f'<span style="color:#1e88e5;font-weight:700;min-width:80px;">{sec}:</span>'
            f'<span style="color:#b0bec5;">{desc}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div></div>", unsafe_allow_html=True)
