"""
modules/demo_data.py — Synthetic forensic datasets for Demo Mode
All data is entirely fictional and for demonstration purposes only.
"""

import random
from datetime import datetime, timedelta


# ── Image analysis demo data ─────────────────────────────────────────────────

IMAGE_DEMO = {
    "threat_level": "HIGH",
    "scene_classification": "Burglary",
    "confidence": 0.91,
    "summary": (
        "Crime scene presents strong indicators of forced residential entry. "
        "Multiple high-confidence detections including a potential edged weapon "
        "and blood spatter patterns consistent with interpersonal violence. "
        "Scene exhibits characteristics of a premeditated act with evidence of "
        "hasty egress by the perpetrator."
    ),
    "detected_objects": [
        {
            "id": "OBJ-001",
            "label": "Person (Suspect)",
            "confidence": 0.94,
            "bbox": [112, 45, 280, 410],
            "notes": "Adult male, dark clothing, facing away from camera",
        },
        {
            "id": "OBJ-002",
            "label": "Edged Weapon (Knife)",
            "confidence": 0.87,
            "bbox": [320, 210, 380, 280],
            "notes": "~20 cm blade, dropped near ingress point",
        },
        {
            "id": "OBJ-003",
            "label": "Blood Spatter",
            "confidence": 0.82,
            "bbox": [190, 300, 460, 390],
            "notes": "Medium-velocity impact pattern, approx 0.8 m²",
        },
        {
            "id": "OBJ-004",
            "label": "Forced Entry Point",
            "confidence": 0.96,
            "bbox": [510, 80, 680, 360],
            "notes": "Door frame splintered, deadbolt defeated",
        },
        {
            "id": "OBJ-005",
            "label": "Firearm (Handgun)",
            "confidence": 0.71,
            "bbox": [445, 198, 510, 240],
            "notes": "Partially obscured, possible semi-automatic pistol",
        },
    ],
    "investigative_leads": [
        {
            "priority": 1,
            "lead": "Secure edged weapon (OBJ-002) for fingerprint and DNA analysis immediately.",
        },
        {
            "priority": 2,
            "lead": "Photograph and sample blood spatter pattern (OBJ-003) for trajectory analysis.",
        },
        {
            "priority": 3,
            "lead": "Collect DNA/touch evidence from forced entry point (OBJ-004) — door frame and lock mechanism.",
        },
        {
            "priority": 4,
            "lead": "Canvas for CCTV coverage of surrounding area within 500m radius.",
        },
        {
            "priority": 5,
            "lead": "Verify firearm detection (OBJ-005) — assess if ballistic evidence present.",
        },
    ],
}


# ── Audio analysis demo data ─────────────────────────────────────────────────

AUDIO_DEMO = {
    "call_type": "Emergency 911 Call",
    "duration_sec": 187,
    "speaker_count": 2,
    "language": "English",
    "summary": (
        "Caller reports a home invasion in progress. Describes a male suspect with a weapon. "
        "Dispatcher attempts to keep caller calm and dispatches units. Caller hears glass breaking "
        "prior to the call. Emotional distress indicators present throughout."
    ),
    "transcript": [
        {"ts": "00:00:03", "speaker": "DISPATCH", "text": "911, what's your emergency?"},
        {
            "ts": "00:00:07",
            "speaker": "CALLER",
            "text": "Please help me — there's someone in my house! I heard the back door —",
        },
        {"ts": "00:00:12", "speaker": "DISPATCH", "text": "Ma'am, stay calm. What is your address?"},
        {
            "ts": "00:00:17",
            "speaker": "CALLER",
            "text": "It's 4172 Elmwood Drive. He has something in his hand, I think it's a knife!",
        },
        {
            "ts": "00:00:28",
            "speaker": "DISPATCH",
            "text": "Units are being dispatched now. Can you lock yourself in a room?",
        },
        {
            "ts": "00:00:35",
            "speaker": "CALLER",
            "text": "I'm in the bedroom — I can hear him going through the living room.",
        },
        {
            "ts": "00:01:02",
            "speaker": "CALLER",
            "text": "He's yelling something. I think he's looking for money or — wait. [glass breaking]",
        },
        {"ts": "00:01:09", "speaker": "DISPATCH", "text": "Are you safe? Stay on the line with me."},
        {
            "ts": "00:01:45",
            "speaker": "CALLER",
            "text": "It went quiet. I think… I think he left through the front. I heard the door slam.",
        },
        {
            "ts": "00:02:14",
            "speaker": "DISPATCH",
            "text": "Officers are 2 minutes out. Do not leave the room until they announce themselves.",
        },
        {"ts": "00:03:07", "speaker": "CALLER", "text": "I hear the sirens. Thank god."},
    ],
    "key_events": [
        {"ts": "00:00:07", "event": "Caller reports active home invasion in progress"},
        {"ts": "00:00:17", "event": "Address confirmed: 4172 Elmwood Drive — suspect has edged weapon"},
        {"ts": "00:01:02", "event": "Audible sound of glass breaking during call — possible secondary entry"},
        {"ts": "00:01:45", "event": "Suspect believed to have fled via front exit — door slam audible"},
        {"ts": "00:03:07", "event": "Police units arrive on scene"},
    ],
    "emotional_markers": ["distress", "fear", "relief"],
    "audio_anomalies": ["glass breaking at T+62s", "door slam at T+105s"],
}


# ── Video analysis demo data ─────────────────────────────────────────────────

VIDEO_DEMO = {
    "duration_sec": 124,
    "fps_analysed": 2,
    "frames_processed": 248,
    "suspects_tracked": 1,
    "vehicles_tracked": 1,
    "summary": (
        "CCTV footage captures a single suspect approaching from the north at T+0s. "
        "Subject uses a tool to defeat the rear entry lock at T+22s. Suspect exits at T+98s "
        "and enters a dark-colored sedan bearing a partial plate (partial: **3K7**) which departs westbound."
    ),
    "event_log": [
        {
            "timestamp": "00:00:00",
            "frame": 1,
            "event": "Scene clear — no subjects detected",
            "category": "Baseline",
            "confidence": 0.99,
        },
        {
            "timestamp": "00:00:08",
            "frame": 16,
            "event": "Suspect S1 enters frame from north perimeter — dark hoodie, gloves",
            "category": "Intrusion / Trespass",
            "confidence": 0.88,
        },
        {
            "timestamp": "00:00:22",
            "frame": 44,
            "event": "S1 attempts forced entry at rear door — tool use detected",
            "category": "Burglary — Breaking & Entering",
            "confidence": 0.91,
        },
        {
            "timestamp": "00:00:34",
            "frame": 68,
            "event": "S1 breaches entry point — enters structure",
            "category": "Burglary — Unlawful Entry",
            "confidence": 0.95,
        },
        {
            "timestamp": "00:01:02",
            "frame": 124,
            "event": "Interior light activation detected through window",
            "category": "Activity — Premises",
            "confidence": 0.78,
        },
        {
            "timestamp": "00:01:38",
            "frame": 196,
            "event": "S1 exits front entry at speed — carrying bag (not present on entry)",
            "category": "Burglary — Theft in Progress",
            "confidence": 0.93,
        },
        {
            "timestamp": "00:01:46",
            "frame": 212,
            "event": "Vehicle V1 detected — dark sedan, partial plate 3K7, westbound",
            "category": "Suspect Vehicle — Escape Route",
            "confidence": 0.84,
        },
        {
            "timestamp": "00:02:04",
            "frame": 248,
            "event": "Scene clear — suspect and vehicle departed",
            "category": "Post-Incident",
            "confidence": 0.99,
        },
    ],
    "trajectories": [
        {"entity": "Suspect S1", "path": "North perimeter → Rear entry → Interior → Front exit"},
        {"entity": "Vehicle V1", "path": "Parked (west side) → Active → Departs westbound"},
    ],
    "vehicle_details": {
        "type": "Sedan",
        "color": "Dark (black/charcoal)",
        "partial_plate": "3K7",
        "direction": "Westbound on Elmwood Drive",
    },
}


# ── Helper ────────────────────────────────────────────────────────────────────

def get_threat_color(level: str) -> str:
    mapping = {
        "CRITICAL": "#f44336",
        "HIGH": "#ffb300",
        "MEDIUM": "#ff9800",
        "LOW": "#00e676",
    }
    return mapping.get(level.upper(), "#7986cb")


def get_confidence_color(score: float) -> str:
    if score >= 0.9:
        return "#00e676"
    if score >= 0.75:
        return "#ffb300"
    if score >= 0.6:
        return "#ff9800"
    return "#f44336"


def confidence_bar_html(score: float, label: str = "") -> str:
    pct = int(score * 100)
    color = get_confidence_color(score)
    return (
        f'<div style="margin:4px 0;">'
        f'<div style="display:flex;justify-content:space-between;font-size:.68rem;">'
        f'<span style="color:#7986cb;">{label}</span>'
        f'<span style="color:{color};font-weight:700;">{pct}%</span></div>'
        f'<div class="conf-bar-wrap">'
        f'<div class="conf-bar" style="width:{pct}%;background:{color};"></div>'
        f'</div></div>'
    )
