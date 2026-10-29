# 🔍 CrimeVision AI
## Intelligent Multimodal Forensic Analysis Platform
### Skill Wallet Capstone Project 2

> **FOR LAW ENFORCEMENT USE ONLY** — All AI analysis requires human expert verification before court submission.

---

## 🚀 Quick Start

```bash
# 1. Clone / navigate to the project
cd "crime ai"

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
streamlit run app.py
```

The app opens at **http://localhost:8501**

---

## 🔑 API Configuration

1. Get a **Gemini API key** from [Google AI Studio](https://aistudio.google.com)
2. Open the app → **Sidebar** → Enter your API key → Click **Connect API**
3. Alternatively, use **Demo Mode** (no key required) — all tabs work with rich synthetic forensic data

---

## 📁 Project Structure

```
crime ai/
├── app.py                      ← Main Streamlit entry point
├── requirements.txt            ← Dependencies
├── .streamlit/
│   ├── config.toml             ← Dark theme & server config
│   └── secrets.toml.example   ← Secrets template (never commit)
└── modules/
    ├── __init__.py
    ├── styles.py               ← Dark forensic CSS theme
    ├── config.py               ← API client, sidebar, chain-of-custody
    ├── custody.py              ← COC banner & tracking utilities
    ├── demo_data.py            ← Synthetic forensic datasets
    ├── tab_image.py            ← Epic 2: Visual Evidence Tagger
    ├── tab_audio.py            ← Epic 3: Audio Transcription & Timeline
    ├── tab_video.py            ← Epic 4: CCTV Video Analysis
    ├── tab_fusion.py           ← Epic 5: Multimodal Fusion & RAG Chat
    └── tab_export.py           ← Epic 6: Automated PDF Export
```

---

## 🧩 Features by Tab

| Tab | Epic | Capability |
|-----|------|-----------|
| 🖼️ Visual Evidence | Epic 2 | RT-DETR-simulated object detection — persons, firearms, weapons, blood spatter, forced entry. Threat level, scene classification, detection table with spatial coordinates, investigative leads. |
| 🎙️ Witness Audio | Epic 3 | Audio transcription with speaker diarisation, timestamped chronological event timeline, emotional marker detection, audio anomaly identification. |
| 📹 CCTV Video | Epic 4 | Frame-sampled video analysis, suspect trajectory tracking, vehicle movement detection, legal crime category classification, confidence timeline chart. |
| 🧩 Fusion & Chat | Epic 5 | Master forensic event ledger merging all three modalities. RAG conversational interface grounded strictly in evidence IDs — zero hallucination mode. |
| 📄 PDF Export | Epic 6 | One-click court-admissible PDF with chain-of-custody, all evidence sections, master ledger, legal disclaimer, and signature block. |

---

## 🔒 Chain-of-Custody

Every analysis session generates a unique **Evidence ID** (e.g., `EV-A3F9C12B`). The investigator must:
1. Enter their **Name** and **Badge/Employee ID** in the sidebar
2. Click **Sign Off** to attach their identity to the evidence
3. The timestamp, Evidence ID, and investigator signature appear on all reports

---

## ☁️ Streamlit Community Cloud Deployment

1. Push this repository to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Deploy from your repo — set main file to `app.py`
4. Add your `GEMINI_API_KEY` via **App Settings → Secrets** (not in code)

> No external database required — all state is managed in-memory via `st.session_state`.

---

## 🛡️ Legal Notice

This platform is an **AI-assisted forensic analysis tool**. All outputs:
- Must be verified by qualified human forensic experts
- Cannot be used as sole evidence in legal proceedings
- Confidence scores ≠ legal standard of proof
- All demo data is entirely fictional

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web application framework |
| `google-genai` | Gemini multimodal AI API |
| `reportlab` | PDF generation |
| `Pillow` | Image processing |
| `pandas` | Data handling |
| `plotly` | Interactive charts |

---

*CrimeVision AI v2.0 · © 2026 Forensic AI Systems*
