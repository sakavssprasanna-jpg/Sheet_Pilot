# Capstone Submission Checklist — SheetPilot AI

This checklist tracks submission requirements for SheetPilot AI.

---

### 📦 1. Pre-Submission Repository Audit
- [x] Application compiles and runs locally (`streamlit run app.py`).
- [x] All **36 unit tests** pass successfully (`python -m unittest discover tests`).
- [x] Git ignores local settings (`.env`, `.streamlit/secrets.toml`, and caches are excluded).
- [x] The demo dataset (`sample_employees.csv`) is tracked in Git.
- [x] No credentials or API keys are hardcoded in the codebase.

### 🚀 2. Deployment Setup
- [x] `requirements.txt` is updated with version limits for all packages.
- [x] The codebase is Linux-compatible and contains no system-level dependencies.
- [x] Streamlit Cloud Secrets are configured for the production deployment.

### 📖 3. Rubric-Aligned Documentation
- [x] `README.md` is updated with terminal logs and architectural flows.
- [x] `docs/system-design.md` covers all 25 system design points.
- [x] `docs/rubric-audit.md` maps code files to each rubric category.
- [x] `docs/defense-questions.md` prepared with answers to potential panel questions.
- [x] `docs/demo-script.md` prepared with a 5-minute presentation walkthrough.

### 🏁 4. Final Submission Links
- **GitHub Repository**: Accessible to evaluators.
- **Live Deployment URL**: `Live Demo: Deployment pending` (Configure Streamlit Community Cloud).
- **Presentation Script**: Ready in `docs/demo-script.md`.
