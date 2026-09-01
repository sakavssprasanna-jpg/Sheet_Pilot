# SheetPilot AI — Current Application State

This document maps SheetPilot AI's features, stability flags, file locations, and release state.

---

## 🚀 Feature Status Summary

| Feature Area | Status | Core Modules | Known Issue | Action Required |
| :--- | :---: | :--- | :--- | :--- |
| **Clean Ingestion** | **STABLE** | `loader.py`, `validator.py` | None. Reads CSV/XLSX. | Maintain file checks. |
| **4-Factor Quality Profiler** | **STABLE** | `profiler.py` | None. Deterministic calculations. | None. |
| **Browser Audio Record** | **STABLE** | `app.py`, `processor.py` | Client microphone permission must be granted. | None. |
| **Gemini Multimodal STT** | **STABLE** | `gemini_client.py` | Requires `GEMINI_API_KEY`. | Handle key missing fallback. |
| **Dynamic Schema Translation** | **STABLE** | `prompts.py`, `gemini_client.py` | AI could try to output invalid column names. | Managed via safety validator check. |
| **Safety Validators** | **STABLE** | `safety.py` | None. Blocks non-whitelisted columns. | None. |
| **Pandas Operations Engine** | **STABLE** | `operation_engine.py` | None. Deterministic methods. | None. |
| **Plotly Analytics Playground** | **STABLE** | `charts.py` | None. Custom dark layouts. | None. |
| **Editable Data Grid** | **STABLE** | `app.py` | Unsaved change markers must not reset. | Managed via session state flag. |
| **Operation Undo Buffer** | **STABLE** | `state.py` | None. Stack rollback logic. | None. |
| **openpyxl Styled Exports** | **STABLE** | `exporters.py` | None. Styled header outputs. | None. |

---

## 🛠️ Deployment Readiness
- **Linux Dependency Audit**: Clear. No system packages required (no FFmpeg, no PortAudio).
- **Python Compatibility**: Python 3.10 and 3.11 fully supported.
- **Entrypoint**: `app.py` is the main target (`streamlit run app.py`).
- **Secrets Management**: Verified priority loader handles Streamlit Secrets correctly. No committed credentials.
