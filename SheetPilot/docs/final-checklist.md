# Capstone Evaluation Checklist — SheetPilot AI

This checklist serves as the final evaluator sheet to verify all components are fully operational and rubric-aligned.

---

## 🛠️ Technical Implementation Checklist

- [ ] **Central Session State Manager**: All states accessed via static getters/setters (`src/state.py`). No direct modification of `st.session_state` outside manager boundary.
- [ ] **Streamlit Form Bounds**: Intent query text submissions occur within `st.form` fields to prevent redundant executions.
- [ ] **Sandboxed Pandas Engine**: Standard pandas methods used. No `eval()` or `exec()` used on LLM outputs.
- [ ] **Failsafe Operations Validator**: Rejects requests references non-existent columns, non-whitelisted math symbols, or non-whitelisted comparison operators.
- [ ] **Undo Stack Management**: Transformed DataFrames are pushed onto history stack buffer; full rollbacks supported.
- [ ] **Clean Ingestion Pipeline**: Ingestion modules validate empty structures and parse CSV/Excel seamlessly.
- [ ] **Data Quality Breakdown**: Multi-factor scoring calculated deterministically using fill rate, completeness, mixed columns, and duplicate row calculations.
- [ ] **Unit Tests**: Full test suite verifying loader, profiling, safety, execution, state, and exporters.

---

## 🧠 AI Integration Checklist

- [ ] **Official google-genai SDK**: Gemini 2.5 Flash initialized using official Google genai standard.
- [ ] **Structured Returns**: Gemini API configured with `response_mime_type="application/json"` and `response_schema=StructuredOperation`.
- [ ] **Fuzzy Metadata Context Builder**: Resolves query keywords to select matching columns and examples, keeping tokens compact.
- [ ] **Robust System Prompts**: Prompts define clear operational roles and enforce strict compliance rules.
- [ ] **Multimodal Voice STT**: WebM audio captured in browser, validated, and transcribed directly by Gemini.
- [ ] **Multilingual & ACC Preservation**: Indian accents and regional language script (Hindi, Telugu, etc.) preserved in transcript cards.

---

## 🎨 UI/UX Checklist

- [ ] **Vercel-inspired dark theme CSS**: Sleek surface colors, custom card shadows, and Inter typography defaults.
- [ ] **Persistent Metric Header**: Displays current row count, column count, dataset status, and quality score.
- [ ] **Tabbed Navigation Workspace**: Segmented into Ask SheetPilot, Data Grid, Column Explorer, Analytics, and History.
- [ ] **Dirty Grid Warning**: Warns user when local cell changes are pending, providing Save/Discard controls.
- [ ] **Custom Plotly Playboard**: Interactive axis and color mapping configurations rendered in real-time.
- [ ] **OpenPyXL Excel Exports**: Styles headers, widths, and grid lines.

---

## ☁️ Deployment & Cloud Checklist

- [ ] **Linux-Compatible packages**: No binary requirements like FFmpeg or PyAudio.
- [ ] **Credential Fallback**: Automatically reads Streamlit secrets (`st.secrets`) before checking env files.
- [ ] **app.py Entrypoint**: Can be run locally and in the cloud with `streamlit run app.py`.

---

## 📂 GitHub & Documentation Checklist

- [ ] **Clean Gitignore**: Credentials, logs, cache, and dynamic datasets excluded.
- [ ] **README.md Overhaul**: Badges, mermaid design, setup guidelines, terminal concept, security definitions, and future works.
- [ ] **docs/architecture.md**: Clear Mermaid flowcharts mapping STT and Pandas safety validator pipelines.
- [ ] **docs/system-design.md**: technically accurate descriptions across 25 specific rubric-aligned sections.
- [ ] **docs/evaluation-matrix.md**: Maps implementation code references to capstone rubric parameters.
