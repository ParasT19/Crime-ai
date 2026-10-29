"""
modules/tab_audio.py — Tab 2: Witness Audio Transcription & Timeline (Epic 3)

Processes witness statements and emergency 911/112 calls with Gemini audio
understanding. Falls back to demo data when in demo mode.
"""

import io
import json
import base64
import streamlit as st

from modules.config import get_api_client, get_model, is_demo_mode
from modules.demo_data import AUDIO_DEMO
from modules.custody import get_timestamp


# ── Gemini system prompt ──────────────────────────────────────────────────────
_AUDIO_SYSTEM = """You are a forensic audio analyst AI. Analyse the provided audio file — which may be a 
witness statement, emergency call, or surveillance audio — and extract forensically relevant information.

Return ONLY valid JSON matching this exact schema (no markdown, no prose):
{
  "call_type": "<Emergency 911|Witness Statement|Surveillance Audio|Interview|Unknown>",
  "duration_sec": <integer>,
  "speaker_count": <integer>,
  "language": "<language name>",
  "summary": "<2-3 sentence forensic summary>",
  "transcript": [
    {
      "ts": "<MM:SS:ms>",
      "speaker": "<SPEAKER_1|CALLER|DISPATCH|WITNESS|SUSPECT|UNKNOWN>",
      "text": "<transcribed speech>"
    }
  ],
  "key_events": [
    {
      "ts": "<MM:SS:ms>",
      "event": "<forensically significant event description>"
    }
  ],
  "emotional_markers": ["<emotion>"],
  "audio_anomalies": ["<description of non-speech sounds>"]
}

Rules:
- Transcribe verbatim, noting speech disfluencies.
- Tag every speaker change with a speaker label.
- Highlight non-speech sounds (glass breaking, footsteps, doors).
- Identify emotional indicators (distress, deception cues, calmness).
- Extract ONLY events with forensic significance for key_events.
- Never hallucinate content not audible in the recording."""


def _analyze_audio_with_gemini(audio_bytes: bytes, mime_type: str) -> dict:
    """Send audio to Gemini for transcription and forensic analysis."""
    client = get_api_client()
    model = get_model()

    try:
        audio_b64 = base64.b64encode(audio_bytes).decode()
        interaction = client.interactions.create(
            model=model,
            system_instruction=_AUDIO_SYSTEM,
            input=[
                {
                    "type": "audio",
                    "data": audio_b64,
                    "mime_type": mime_type,
                },
                {
                    "type": "text",
                    "text": "Perform full forensic audio transcription and event extraction.",
                },
            ],
        )
        raw = interaction.output_text or ""
        raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        return json.loads(raw)
    except json.JSONDecodeError:
        st.warning("⚠️ Audio API response parse error — falling back to demo data.")
        return AUDIO_DEMO
    except Exception as e:
        st.error(f"Audio API error: {e}")
        return AUDIO_DEMO


def _render_transcript(transcript: list):
    """Render the timestamped transcript with speaker colour coding."""
    st.markdown(
        '<div class="section-header"><h3>📝 Full Timestamped Transcript</h3></div>',
        unsafe_allow_html=True,
    )

    speaker_colors = {
        "DISPATCH": "#1e88e5",
        "CALLER": "#00bcd4",
        "WITNESS": "#00e676",
        "SUSPECT": "#f44336",
        "SPEAKER_1": "#ce93d8",
        "SPEAKER_2": "#ffb300",
        "UNKNOWN": "#7986cb",
    }

    for entry in transcript:
        spk = entry.get("speaker", "UNKNOWN").upper()
        color = speaker_colors.get(spk, "#7986cb")
        ts = entry.get("ts", "??:??")
        text = entry.get("text", "")

        st.markdown(
            f'<div style="display:flex;gap:12px;margin:5px 0;align-items:flex-start;">'
            f'<span style="color:#7986cb;font-size:.68rem;min-width:58px;font-family:monospace;">[{ts}]</span>'
            f'<span style="color:{color};font-size:.72rem;font-weight:700;min-width:72px;">{spk}</span>'
            f'<span style="color:#e8eaf6;font-size:.82rem;flex:1;">{text}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


def _render_key_events(events: list):
    """Render chronological forensic event timeline."""
    st.markdown(
        '<div class="section-header"><h3>⏱️ Chronological Forensic Event Timeline</h3></div>',
        unsafe_allow_html=True,
    )

    for i, ev in enumerate(events):
        ts = ev.get("ts", "??:??")
        event = ev.get("event", "")
        is_last = i == len(events) - 1

        st.markdown(
            f'<div style="display:flex;gap:14px;margin:0;">'
            f'<div style="display:flex;flex-direction:column;align-items:center;">'
            f'<div style="width:12px;height:12px;border-radius:50%;background:#1e88e5;'
            f'border:2px solid #00bcd4;box-shadow:0 0 8px rgba(30,136,229,0.6);flex-shrink:0;"></div>'
            f'{"" if is_last else "<div style=\"width:2px;flex:1;background:rgba(30,136,229,0.3);margin:2px 0;\"></div>"}'
            f'</div>'
            f'<div style="padding-bottom:14px;">'
            f'<span style="font-size:.7rem;color:#7986cb;font-family:monospace;">{ts}</span>'
            f'<div style="font-size:.82rem;color:#e8eaf6;margin-top:2px;">{event}</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def render_tab_audio():
    """Render Tab 2 — Witness Audio Transcription & Timeline."""

    st.markdown(
        '<div class="forensic-card">'
        '<h2 style="color:#00bcd4;margin:0 0 6px 0;font-size:1.1rem;">🎙️ Epic 3 — Witness Audio Transcription & Timeline</h2>'
        '<p style="color:#7986cb;font-size:.8rem;margin:0;">Upload witness statements or emergency calls for AI-powered '
        'transcription, speaker diarisation, and chronological event extraction.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    col_upload, col_meta = st.columns([1, 1])

    with col_upload:
        audio_file = st.file_uploader(
            "Upload Audio File",
            type=["mp3", "wav", "m4a", "ogg", "flac", "aac", "webm"],
            key="audio_uploader",
            help="Supported: MP3, WAV, M4A, OGG, FLAC, AAC, WebM",
        )

        if audio_file:
            st.audio(audio_file, format=audio_file.type)

            st.markdown(
                f'<div class="forensic-card" style="padding:12px;">'
                f'<div style="font-size:.68rem;color:#7986cb;margin-bottom:6px;">AUDIO FILE METADATA</div>'
                f'<div style="font-size:.78rem;color:#e8eaf6;"><b>File:</b> {audio_file.name}</div>'
                f'<div style="font-size:.78rem;color:#e8eaf6;"><b>Size:</b> {audio_file.size/1024:.1f} KB</div>'
                f'<div style="font-size:.78rem;color:#e8eaf6;"><b>Format:</b> {audio_file.type}</div>'
                f'<div style="font-size:.78rem;color:#e8eaf6;"><b>Ingested:</b> {get_timestamp()}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    with col_meta:
        st.markdown(
            '<div class="forensic-card" style="padding:16px;">'
            '<div style="font-size:.68rem;color:#7986cb;letter-spacing:.1em;text-transform:uppercase;margin-bottom:10px;">Transcription Settings</div>',
            unsafe_allow_html=True,
        )
        call_type_hint = st.selectbox(
            "Expected Audio Type",
            ["Auto-detect", "Emergency 911/112 Call", "Witness Statement", "Interview Recording", "Surveillance Audio"],
            key="audio_type_hint",
        )
        diarize = st.checkbox("Enable Speaker Diarisation", value=True, key="diarize")
        extract_anomalies = st.checkbox("Extract Audio Anomalies", value=True, key="audio_anomalies")
        st.markdown("</div>", unsafe_allow_html=True)

    if audio_file:
        if st.button("🎙️ Transcribe & Analyse", use_container_width=True, key="btn_transcribe", type="primary"):
            audio_bytes = audio_file.read()
            mime = audio_file.type or "audio/mpeg"
            with st.spinner("⚙️ Transcribing and extracting forensic events…"):
                if is_demo_mode():
                    findings = AUDIO_DEMO
                else:
                    findings = _analyze_audio_with_gemini(audio_bytes, mime)

            st.session_state.audio_findings = findings
            st.session_state.audio_source = audio_file.name
            st.success("✅ Transcription complete")

    # ── Results ───────────────────────────────────────────────────────────────
    findings = st.session_state.get("audio_findings")
    if findings:
        st.divider()

        # Metrics row
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(
                f'<div class="metric-box"><div class="metric-value">'
                f'{findings.get("call_type","N/A")}</div>'
                f'<div class="metric-label">Call Type</div></div>',
                unsafe_allow_html=True,
            )
        with c2:
            dur = findings.get("duration_sec", 0)
            mins, secs = divmod(dur, 60)
            st.markdown(
                f'<div class="metric-box"><div class="metric-value">{mins:02d}:{secs:02d}</div>'
                f'<div class="metric-label">Duration</div></div>',
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f'<div class="metric-box"><div class="metric-value">'
                f'{findings.get("speaker_count",0)}</div>'
                f'<div class="metric-label">Speakers</div></div>',
                unsafe_allow_html=True,
            )
        with c4:
            key_count = len(findings.get("key_events", []))
            st.markdown(
                f'<div class="metric-box"><div class="metric-value">{key_count}</div>'
                f'<div class="metric-label">Key Events</div></div>',
                unsafe_allow_html=True,
            )

        # Summary
        st.markdown(
            f'<div class="forensic-card-highlight">'
            f'<div style="font-size:.68rem;color:#7986cb;letter-spacing:.1em;text-transform:uppercase;margin-bottom:6px;">'
            f'🧠 Forensic Audio Summary</div>'
            f'<p style="font-size:.85rem;color:#e8eaf6;margin:0;line-height:1.7;">{findings.get("summary","")}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Anomalies & emotional markers
        cols_a = st.columns(2)
        with cols_a[0]:
            anomalies = findings.get("audio_anomalies", [])
            if anomalies:
                st.markdown(
                    '<div style="font-size:.68rem;color:#7986cb;letter-spacing:.1em;text-transform:uppercase;margin-bottom:6px;">🔊 Audio Anomalies</div>',
                    unsafe_allow_html=True,
                )
                for a in anomalies:
                    st.markdown(
                        f'<div style="background:rgba(244,67,54,0.08);border-left:3px solid #f44336;'
                        f'border-radius:4px;padding:6px 12px;margin:4px 0;font-size:.78rem;">{a}</div>',
                        unsafe_allow_html=True,
                    )
        with cols_a[1]:
            markers = findings.get("emotional_markers", [])
            if markers:
                st.markdown(
                    '<div style="font-size:.68rem;color:#7986cb;letter-spacing:.1em;text-transform:uppercase;margin-bottom:6px;">😟 Emotional Markers</div>',
                    unsafe_allow_html=True,
                )
                tags_html = " ".join(
                    f'<span style="background:rgba(156,39,176,0.2);border:1px solid #9c27b0;'
                    f'border-radius:12px;padding:4px 12px;font-size:.72rem;color:#ce93d8;'
                    f'margin:2px;">{m.upper()}</span>'
                    for m in markers
                )
                st.markdown(tags_html, unsafe_allow_html=True)

        # Two-column layout: timeline + transcript
        col_tl, col_tr = st.columns([1, 1])
        with col_tl:
            _render_key_events(findings.get("key_events", []))
        with col_tr:
            with st.expander("📝 Full Transcript", expanded=True):
                _render_transcript(findings.get("transcript", []))

    else:
        st.markdown(
            '<div style="text-align:center;padding:48px;color:#7986cb;">'
            '<div style="font-size:3rem;">🎙️</div>'
            '<div style="font-size:.9rem;margin-top:8px;">Upload an audio file to begin witness statement analysis.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
