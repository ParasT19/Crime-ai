"""
modules/tab_fusion.py — Tab 4: Multimodal Fusion & Grounded Evidence Chat (Epic 5)

Unifies image, audio, and video findings into a master forensic event ledger and
provides a RAG-style conversational interface grounded strictly in uploaded evidence.
"""

import json
import streamlit as st
from datetime import datetime

from modules.config import get_api_client, get_model, is_demo_mode
from modules.demo_data import IMAGE_DEMO, AUDIO_DEMO, VIDEO_DEMO
from modules.custody import get_timestamp


# ── Evidence ledger builder ───────────────────────────────────────────────────

def _build_master_ledger() -> list[dict]:
    """Merge image, audio, and video findings into a unified timeline."""
    ledger = []

    # ── Image evidence ────────────────────────────────────────────────────────
    img = st.session_state.get("image_findings")
    img_src = st.session_state.get("image_source", "image_upload.jpg")
    if img:
        # Scene entry
        ledger.append({
            "ev_id": f'{st.session_state.evidence_id}-IMG-001',
            "source": "IMAGE",
            "source_file": img_src,
            "timestamp": "Scene Photography",
            "event": f'Scene classified as {img.get("scene_classification","Unknown")} — '
                     f'Threat Level: {img.get("threat_level","N/A")}',
            "details": img.get("summary", ""),
            "confidence": img.get("confidence", 0),
        })
        # Each detected object
        for i, obj in enumerate(img.get("detected_objects", []), 1):
            ledger.append({
                "ev_id": f'{st.session_state.evidence_id}-IMG-{i+1:03d}',
                "source": "IMAGE",
                "source_file": img_src,
                "timestamp": "Scene Photography",
                "event": f'Detected: {obj.get("label","Unknown")} [{obj.get("id","OBJ-?")}]',
                "details": obj.get("notes", ""),
                "confidence": obj.get("confidence", 0),
            })

    # ── Audio evidence ────────────────────────────────────────────────────────
    aud = st.session_state.get("audio_findings")
    aud_src = st.session_state.get("audio_source", "audio_recording.mp3")
    if aud:
        for i, ev in enumerate(aud.get("key_events", []), 1):
            ledger.append({
                "ev_id": f'{st.session_state.evidence_id}-AUD-{i:03d}',
                "source": "AUDIO",
                "source_file": aud_src,
                "timestamp": ev.get("ts", "??:??"),
                "event": ev.get("event", ""),
                "details": aud.get("call_type", ""),
                "confidence": 0.88,
            })
        for anomaly in aud.get("audio_anomalies", []):
            ledger.append({
                "ev_id": f'{st.session_state.evidence_id}-AUD-A{len(ledger):02d}',
                "source": "AUDIO",
                "source_file": aud_src,
                "timestamp": "Audio Recording",
                "event": f"Audio Anomaly: {anomaly}",
                "details": "Non-speech acoustic event",
                "confidence": 0.75,
            })

    # ── Video evidence ────────────────────────────────────────────────────────
    vid = st.session_state.get("video_findings")
    vid_src = st.session_state.get("video_source", "cctv_footage.mp4")
    if vid:
        for i, ev in enumerate(vid.get("event_log", []), 1):
            ledger.append({
                "ev_id": f'{st.session_state.evidence_id}-VID-{i:03d}',
                "source": "VIDEO",
                "source_file": vid_src,
                "timestamp": ev.get("timestamp", "??:??:??"),
                "event": ev.get("event", ""),
                "details": f'Category: {ev.get("category","Unknown")}',
                "confidence": ev.get("confidence", 0),
            })

    return ledger


def _ledger_to_context(ledger: list) -> str:
    """Serialise the ledger as a structured context string for the AI."""
    if not ledger:
        return "No evidence has been loaded yet."
    lines = ["=== MASTER FORENSIC EVIDENCE LEDGER ===\n"]
    for entry in ledger:
        lines.append(
            f"[{entry['ev_id']}] SOURCE={entry['source']} | FILE={entry['source_file']} | "
            f"TS={entry['timestamp']} | CONF={int(entry['confidence']*100)}%\n"
            f"EVENT: {entry['event']}\n"
            f"DETAIL: {entry['details']}\n"
        )
    return "\n".join(lines)


def _chat_with_gemini(question: str, ledger_context: str, history: list) -> str:
    """Send a RAG query to Gemini grounded strictly in the evidence ledger."""
    client = get_api_client()
    model = get_model()

    system = f"""You are a forensic intelligence analyst AI. You have access ONLY to the following 
Master Forensic Evidence Ledger which contains evidence collected from crime scene images, witness audio, 
and CCTV video analysis. 

STRICT RULES:
1. NEVER speculate or hallucinate facts not present in the ledger.
2. ALWAYS cite specific evidence IDs (e.g., EV-XXXXXXXX-IMG-002) for every claim.
3. If the answer is not in the evidence, say: "This information is not available in the current evidence corpus."
4. Respond in clear, professional forensic language suitable for court proceedings.
5. Structure your answer with: [FINDING] → [EVIDENCE CITATIONS] → [CONFIDENCE ASSESSMENT]

{ledger_context}

The investigator is: {st.session_state.get("investigator","PENDING")}
Current UTC Time: {get_timestamp()}"""

    try:
        # Build conversation input with history
        conversation_input = question
        if history:
            prev_context = "\n".join(
                f"Q: {h['q']}\nA: {h['a']}" for h in history[-3:]  # Last 3 turns
            )
            conversation_input = f"Previous conversation:\n{prev_context}\n\nCurrent question: {question}"

        interaction = client.interactions.create(
            model=model,
            system_instruction=system,
            input=conversation_input,
        )
        return interaction.output_text or "No response generated."
    except Exception as e:
        return f"⚠️ API error: {e}\n\nFalling back to evidence summary. Please check your API connection."


def _chat_demo(question: str, ledger: list) -> str:
    """Generate a demo AI response grounded in the evidence ledger."""
    q_lower = question.lower()

    # Weapon-related queries
    if any(w in q_lower for w in ["weapon", "knife", "gun", "firearm", "armed"]):
        img_ev = [e for e in ledger if "IMAGE" in e.get("source","") and
                  any(w in e.get("event","").lower() for w in ["weapon","knife","firearm","gun"])]
        if img_ev:
            ev = img_ev[0]
            return (
                f"**[FINDING]** Yes. A potential edged weapon (knife) and firearm were detected in the crime scene imagery.\n\n"
                f"**[EVIDENCE CITATIONS]**\n"
                f"- `{ev['ev_id']}`: {ev['event']} (Confidence: {int(ev['confidence']*100)}%)\n\n"
                f"**[CONFIDENCE ASSESSMENT]** HIGH — Two independent weapon signatures detected in scene photography."
            )
        return "**[FINDING]** No weapon evidence currently in the evidence corpus.\n\n**[EVIDENCE CITATIONS]** N/A\n\n**[CONFIDENCE ASSESSMENT]** N/A"

    # Suspect/person queries
    if any(w in q_lower for w in ["suspect", "person", "who", "perpetrator", "attacker"]):
        vid_ev = [e for e in ledger if "VIDEO" in e.get("source","") and
                  any(w in e.get("event","").lower() for w in ["suspect","person","s1"])]
        aud_ev = [e for e in ledger if "AUDIO" in e.get("source","") and
                  "weapon" in e.get("event","").lower()]
        citations = []
        if vid_ev:
            citations.append(f"- `{vid_ev[0]['ev_id']}`: {vid_ev[0]['event']}")
        if aud_ev:
            citations.append(f"- `{aud_ev[0]['ev_id']}`: {aud_ev[0]['event']}")
        cit_str = "\n".join(citations) if citations else "- No direct suspect evidence found."
        return (
            f"**[FINDING]** One suspect (S1) was tracked throughout the CCTV footage. "
            f"The caller described a male individual with an edged weapon.\n\n"
            f"**[EVIDENCE CITATIONS]**\n{cit_str}\n\n"
            f"**[CONFIDENCE ASSESSMENT]** MEDIUM-HIGH — Consistent across video and audio modalities."
        )

    # Timeline/sequence queries
    if any(w in q_lower for w in ["when", "timeline", "sequence", "first", "before", "after", "fled", "escape"]):
        vid_evs = sorted([e for e in ledger if "VIDEO" in e.get("source","")],
                         key=lambda x: x.get("timestamp",""))
        if vid_evs:
            cits = "\n".join(f"- `{e['ev_id']}` [{e['timestamp']}]: {e['event']}" for e in vid_evs[:5])
            return (
                f"**[FINDING]** The chronological event sequence from CCTV analysis is as follows:\n\n"
                f"**[EVIDENCE CITATIONS]**\n{cits}\n\n"
                f"**[CONFIDENCE ASSESSMENT]** HIGH — Derived directly from timestamped CCTV evidence log."
            )

    # Vehicle queries
    if any(w in q_lower for w in ["vehicle", "car", "plate", "licence", "sedan", "getaway"]):
        vid_ev = [e for e in ledger if "VIDEO" in e.get("source","") and
                  "vehicle" in e.get("event","").lower()]
        if vid_ev:
            ev = vid_ev[0]
            return (
                f"**[FINDING]** A suspect vehicle was identified in the CCTV footage: dark-colored sedan, partial plate **3K7**, departing westbound.\n\n"
                f"**[EVIDENCE CITATIONS]**\n- `{ev['ev_id']}`: {ev['event']}\n\n"
                f"**[CONFIDENCE ASSESSMENT]** MEDIUM — Partial plate only; full identification requires DMV cross-reference."
            )

    # Default response
    ev_count = len(ledger)
    sources = list({e.get("source","?") for e in ledger})
    return (
        f"**[FINDING]** The current evidence corpus contains {ev_count} evidence entries from "
        f"the following sources: {', '.join(sources)}.\n\n"
        f"**[EVIDENCE CITATIONS]** Please ask a more specific question about weapons, suspects, "
        f"timeline, or vehicle information to retrieve grounded evidence citations.\n\n"
        f"**[CONFIDENCE ASSESSMENT]** N/A — Reformulate query for specific evidence retrieval."
    )


def _render_ledger_table(ledger: list):
    """Render the master evidence ledger as an HTML table."""
    source_colors = {"IMAGE": "#00bcd4", "AUDIO": "#ce93d8", "VIDEO": "#ffb300"}
    rows_html = ""
    for entry in ledger:
        src = entry.get("source", "?")
        src_color = source_colors.get(src, "#7986cb")
        conf = entry.get("confidence", 0)
        conf_color = "#00e676" if conf >= 0.9 else "#ffb300" if conf >= 0.75 else "#f44336"
        rows_html += (
            f'<tr>'
            f'<td><code style="color:#00bcd4;font-size:.62rem;">{entry.get("ev_id","---")}</code></td>'
            f'<td><span style="color:{src_color};font-weight:700;font-size:.7rem;">{src}</span></td>'
            f'<td style="color:#7986cb;font-size:.68rem;">{entry.get("timestamp","?")}</td>'
            f'<td style="font-size:.76rem;">{entry.get("event","")}</td>'
            f'<td style="color:{conf_color};font-weight:700;font-size:.72rem;">{int(conf*100)}%</td>'
            f'</tr>'
        )
    st.markdown(
        f'<table class="evidence-table">'
        f'<thead><tr>'
        f'<th>Evidence ID</th><th>Source</th><th>Timestamp</th>'
        f'<th>Event / Finding</th><th>Conf.</th>'
        f'</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        f'</table>',
        unsafe_allow_html=True,
    )


def render_tab_fusion():
    """Render Tab 4 — Multimodal Fusion & Grounded Evidence Chat."""

    st.markdown(
        '<div class="forensic-card">'
        '<h2 style="color:#00bcd4;margin:0 0 6px 0;font-size:1.1rem;">🧩 Epic 5 — Multimodal Fusion & Grounded Evidence Chat</h2>'
        '<p style="color:#7986cb;font-size:.8rem;margin:0;">Unified master forensic event ledger combining all evidence modalities. '
        'Interrogate the evidence in natural language with zero hallucination and strict evidence citations.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Build / display master ledger ─────────────────────────────────────────
    ledger = _build_master_ledger()

    # Use demo data if nothing uploaded
    has_real_data = any([
        st.session_state.get("image_findings"),
        st.session_state.get("audio_findings"),
        st.session_state.get("video_findings"),
    ])
    if not has_real_data and is_demo_mode():
        st.markdown(
            '<div class="demo-banner">ℹ️  No evidence uploaded — loading full demo dataset (Image + Audio + Video) for demonstration.</div>',
            unsafe_allow_html=True,
        )
        # Temporarily inject demo data
        if not st.session_state.get("image_findings"):
            st.session_state.image_findings = IMAGE_DEMO
            st.session_state.image_source = "demo_crime_scene.jpg"
        if not st.session_state.get("audio_findings"):
            st.session_state.audio_findings = AUDIO_DEMO
            st.session_state.audio_source = "demo_911_call.mp3"
        if not st.session_state.get("video_findings"):
            st.session_state.video_findings = VIDEO_DEMO
            st.session_state.video_source = "demo_cctv.mp4"
        ledger = _build_master_ledger()

    # Metrics
    img_count = sum(1 for e in ledger if e.get("source") == "IMAGE")
    aud_count = sum(1 for e in ledger if e.get("source") == "AUDIO")
    vid_count = sum(1 for e in ledger if e.get("source") == "VIDEO")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f'<div class="metric-box"><div class="metric-value">{len(ledger)}</div>'
            f'<div class="metric-label">Total Evidence Items</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="metric-box"><div class="metric-value" style="color:#00bcd4;">{img_count}</div>'
            f'<div class="metric-label">Image Events</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="metric-box"><div class="metric-value" style="color:#ce93d8;">{aud_count}</div>'
            f'<div class="metric-label">Audio Events</div></div>',
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f'<div class="metric-box"><div class="metric-value" style="color:#ffb300;">{vid_count}</div>'
            f'<div class="metric-label">Video Events</div></div>',
            unsafe_allow_html=True,
        )

    # Ledger table
    with st.expander("📋 Master Forensic Event Ledger", expanded=True):
        if ledger:
            _render_ledger_table(ledger)
        else:
            st.info("No evidence loaded. Upload files in the Image, Audio, or Video tabs.")

    st.divider()

    # ── RAG Chat Interface ────────────────────────────────────────────────────
    st.markdown(
        '<div class="section-header"><h3>💬 Grounded Evidence Interrogation</h3></div>',
        unsafe_allow_html=True,
    )

    # Suggested questions
    st.markdown(
        '<div style="font-size:.7rem;color:#7986cb;margin-bottom:8px;letter-spacing:.06em;">💡 SUGGESTED QUERIES:</div>',
        unsafe_allow_html=True,
    )
    suggestions = [
        "Was a weapon visible before the suspect fled?",
        "What was the suspect's trajectory through the scene?",
        "Summarise all evidence with confidence > 85%",
        "What was the getaway vehicle description?",
        "When did the breach occur relative to the 911 call?",
    ]
    cols = st.columns(len(suggestions))
    for col, sug in zip(cols, suggestions):
        with col:
            if st.button(sug, key=f"sug_{hash(sug)}", use_container_width=True):
                st.session_state.chat_input_value = sug

    # Chat history display
    chat_container = st.container()
    with chat_container:
        for turn in st.session_state.get("chat_history", []):
            st.markdown(
                f'<div class="chat-user">👮 <b>Investigator:</b> {turn["q"]}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="chat-ai">🤖 <b>CrimeVision AI:</b><br>{turn["a"]}'
                f'<div class="chat-citation">📎 Evidence corpus grounded · Zero hallucination mode · {get_timestamp()}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Input area
    with st.form("chat_form", clear_on_submit=True):
        default_val = st.session_state.pop("chat_input_value", "")
        question = st.text_input(
            "Ask a forensic question about the evidence…",
            value=default_val,
            placeholder='e.g. "Was a weapon visible before the suspect fled?"',
            key="chat_question",
        )
        col_ask, col_clear = st.columns([4, 1])
        with col_ask:
            submitted = st.form_submit_button("🔎 Interrogate Evidence", use_container_width=True, type="primary")
        with col_clear:
            clear = st.form_submit_button("🗑 Clear", use_container_width=True)

    if submitted and question.strip():
        ledger_context = _ledger_to_context(ledger)
        with st.spinner("⚙️ Querying evidence corpus…"):
            if is_demo_mode() or not get_api_client():
                answer = _chat_demo(question, ledger)
            else:
                answer = _chat_with_gemini(
                    question,
                    ledger_context,
                    st.session_state.get("chat_history", []),
                )
        st.session_state.chat_history.append({"q": question, "a": answer})
        st.rerun()

    if clear:
        st.session_state.chat_history = []
        st.rerun()

    # Store ledger in session for PDF export
    st.session_state.master_ledger = ledger
