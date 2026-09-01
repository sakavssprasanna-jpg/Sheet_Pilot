# Evaluation Rubric Matrix — SheetPilot AI

This document maps SheetPilot AI's codebase modules and functions directly to the 100-Point B.Tech Capstone Evaluation Rubric.

---

## 📈 Summary Matrix

| Rubric Category | Points | Core Implementation Evidence | Verification File & Line Reference |
| :--- | :---: | :--- | :--- |
| **Technical Implementation** | 25 | - Whitelist-based Pandas execution engine<br>- Central state encapsulation<br>- Unsaved cell grid changes tracker<br>- Strict safety validators for code injection | - [operation_engine.py](file:///c:/Users/VAJAYA/Desktop/SheetPilot/src/execution/operation_engine.py)<br>- [state.py](file:///c:/Users/VAJAYA/Desktop/SheetPilot/src/state.py)<br>- [safety.py](file:///c:/Users/VAJAYA/Desktop/SheetPilot/src/execution/safety.py) |
| **AI Integration** | 20 | - Official `google-genai` SDK implementation<br>- Native multimodal Gemini STT transcription<br>- Pydantic schema return enforcement<br>- Fuzzy sample context builder | - [gemini_client.py](file:///c:/Users/VAJAYA/Desktop/SheetPilot/src/ai/gemini_client.py)<br>- [schemas.py](file:///c:/Users/VAJAYA/Desktop/SheetPilot/src/ai/schemas.py)<br>- [prompts.py](file:///c:/Users/VAJAYA/Desktop/SheetPilot/src/ai/prompts.py) |
| **UI/UX & Visualization** | 20 | - Vercel-inspired dark theme CSS styles<br>- Tabbed workspace navigation panels<br>- Plotly Custom Express playboard<br>- Type-aware visual recommenders | - [app.py](file:///c:/Users/VAJAYA/Desktop/SheetPilot/app.py)<br>- [components.py](file:///c:/Users/VAJAYA/Desktop/SheetPilot/src/ui/components.py)<br>- [charts.py](file:///c:/Users/VAJAYA/Desktop/SheetPilot/src/visualization/charts.py) |
| **Deployment & Cloud** | 15 | - Linux-compatible package dependencies<br>- Priority secrets keys loader logic<br>- Community cloud deployment recipe | - [requirements.txt](file:///c:/Users/VAJAYA/Desktop/SheetPilot/requirements.txt)<br>- [config.py](file:///c:/Users/VAJAYA/Desktop/SheetPilot/src/config.py)<br>- [deployment.md](file:///c:/Users/VAJAYA/Desktop/SheetPilot/docs/deployment.md) |
| **GitHub Cleanliness** | 10 | - Preserved demo spreadsheet tracking<br>- Comprehensive `.gitignore` patterns<br>- Step-by-step setup walkthroughs | - [.gitignore](file:///c:/Users/VAJAYA/Desktop/SheetPilot/.gitignore)<br>- [README.md](file:///c:/Users/VAJAYA/Desktop/SheetPilot/README.md) |
| **System Design** | 10 | - 25-section system design spec<br>- High-fidelity Mermaid component maps<br>- Decoupled MVC data flow diagram | - [system-design.md](file:///c:/Users/VAJAYA/Desktop/SheetPilot/docs/system-design.md)<br>- [architecture.md](file:///c:/Users/VAJAYA/Desktop/SheetPilot/docs/architecture.md) |

---

## 🔍 Detailed Evidence Breakdowns

### 1. Technical Implementation & Architecture (25 Points)
- **Centralized State**: All Streamlit states are centralized in `src/state.py` under the static class `SessionStateManager`. This keeps state isolated and consistent across UI reruns.
- **Sandboxed Operations**: In `src/execution/operation_engine.py`, transformations like sorting (`df.sort_values`), filtering (`df.query` on whitelisted subsets), and grouping are processed programmatically. No raw string execution (`eval` or `exec`) is allowed.
- **Safety Validators**: `src/execution/safety.py` audits Pydantic schema intents. Operators not matching the whitelisted operators list are rejected. Column transformations are restricted to valid numeric calculations with regex safety checks blocking system calls.

### 2. AI Integration & Prompt Engineering (20 Points)
- **Official SDK**: Built using the modern, official `google-genai` SDK in `src/ai/gemini_client.py`.
- **Structured Outputs**: Gemini model requests use `response_mime_type="application/json"` and `response_schema=StructuredOperation` to ensure structured JSON output.
- **Multimodal STT**: Captures WebM audio via the browser microphone, validates format/length, and runs native speech-to-text transcription with regional language support using `gemini-2.5-flash`.

### 3. UI/UX & Data Visualization (20 Points)
- **Workspace Navigation Tabs**: Integrated five top-level workspace tabs to coordinate user interaction:
  - `Ask SheetPilot`: Main LLM prompt card with recording indicators and results.
  - `Data Grid`: Native `st.data_editor` cell-modification layout with save/discard control flags.
  - `Column Explorer`: Metadata inspection card.
  - `Analytics Dashboard`: Dynamic Plotly chart selectors.
  - `Operation History`: Chronological operations log.
- **Visual Recommender**: `src/visualization/charts.py` inspects output data column types to recommend line, bar, scatter, pie, or distribution charts.

### 4. Deployment & Cloud Engineering (15 Points)
- **Community Cloud Ready**: SheetPilot AI does not require system packages like FFmpeg, ensuring compatibility with Streamlit's Linux instances.
- **Secrets Management**: `src/config.py` searches Streamlit production secrets (`st.secrets["GEMINI_API_KEY"]`) before falling back to local environmental `.env` files.

### 5. Open-Source Branding & GitHub (10 Points)
- **Standard Layout**: Features a professional open-source README with usage examples, terminal logs, step-by-step setup guides, and environment configurations.
- **Excluded Keys**: `.gitignore` prevents environmental credential files from being tracked.

### 6. System Design & Documentation (10 Points)
- **Deep Design Specs**: Detailed Mermaid flowcharts and component mapping in `docs/architecture.md` and `docs/system-design.md`.
