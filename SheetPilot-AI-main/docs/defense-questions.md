# SheetPilot AI — Capstone Defense & FAQ Guide

This document contains technically correct answers to questions that may be asked by the Capstone evaluation panel.

---

### 1. Why did you use Gemini?
- **Answer**: Gemini models natively support structured JSON schema generation using Pydantic, are cost-efficient, and feature multimodal audio processing (enabling multilingual voice commands directly from WebM bytes without an external speech-to-text pipeline).

### 2. Why not ChatGPT/OpenAI?
- **Answer**: Gemini's Google GenAI SDK allows structured schema compilation and native audio processing. The Google GenAI ecosystem is highly optimized for serverless deployments on platforms like Streamlit Community Cloud.

### 3. Why structured output?
- **Answer**: Standard text generation is unpredictable. By forcing Gemini to respond with a structured JSON schema (conforming to a Pydantic contract), SheetPilot ensures that commands are parsed into exact, predictable data operations.

### 4. Why Pandas?
- **Answer**: Pandas is the standard for in-memory data science in Python. It provides high-performance, vectorized, and deterministic execution for filtering, sorting, aggregation, and styling without needing external database systems.

### 5. Why not let Gemini generate and execute Python code?
- **Answer**: **Safety & Security**. Letting an LLM write Python code and running it via `eval()` or `exec()` exposes the application to code injection, file-system deletion, and unauthorized shell access. SheetPilot eliminates this risk by translating queries into schema parameters and executing them using predefined, audited Pandas methods.

### 6. How do you prevent prompt injection?
- **Answer**: 
  1. **Strict Input Boundaries**: Spreadsheet cell contents are treated strictly as cell values and are never passed as instructions to the LLM.
  2. **Audit Verification**: The translation query only uses the dataframe's metadata (column names and data types), not the actual cell string values.
  3. **No Execution Access**: Even if a cell contains `"Ignore previous instructions"`, the safety validator blocks any unauthorized operations.

### 7. How does session_state work?
- **Answer**: Streamlit's `st.session_state` stores state variables across user interactions. SheetPilot wraps this in a `SessionStateManager` static class to manage variables (like the original dataframe, active dataframe, quality scores, and change histories) without accidental resets.

### 8. Why use st.form?
- **Answer**: In Streamlit, modifying an input field triggers a full page rerun. Wrapping text commands inside `st.form` batches user actions, executing them only when the "Run Command" button is clicked. This prevents redundant Gemini API calls and improves performance.

### 9. How does multilingual voice work?
- **Answer**: The browser's microphone captures audio as WebM bytes. These bytes are sent directly to the Gemini API, which transcribes the audio, detects the spoken language, and translates the intent into a structured operation.

### 10. How do you handle API failure?
- **Answer**: If the API key is missing or the network fails, SheetPilot displays a clean warning box instead of crashing. Users can still view, profile, filter, edit, and export their datasets manually using the dashboard controls.

### 11. How do you select charts?
- **Answer**: The dashboard uses a rule-based visualization recommender (`src/visualization/recommender.py`) that analyzes column data types:
  - Date + Numeric: Line Chart.
  - Category + Numeric: Bar Chart or Pie Chart.
  - Single Numeric: Histogram.
  - Numeric + Numeric: Scatter Plot.

### 12. How do you prevent hallucinated columns?
- **Answer**: SheetPilot extracts the exact column names of the active spreadsheet and includes them in the Gemini prompt. The safety validator then audits the output, rejecting any operations that reference non-existent columns.

### 13. How is the application deployed?
- **Answer**: The application is deployed to Streamlit Community Cloud. Dependencies are managed via `requirements.txt`, and the API key is configured using Streamlit's native Secrets manager (`.streamlit/secrets.toml` or the cloud secrets dashboard).

### 14. How are secrets protected?
- **Answer**: 
  1. **No Hardcoding**: The API key is loaded dynamically from the environment.
  2. **Git Ignored**: Local configuration files (`.env`) are added to `.gitignore`.
  3. **Runtime Fallbacks**: Streamlit Cloud injection handles secrets securely in production.

### 15. What are the limitations?
- **Answer**: 
  1. **File Size**: Streamlit Community Cloud has a 1GB RAM limit. Datasets larger than 200MB may hit memory constraints.
  2. **Multi-Sheet Workbooks**: SheetPilot parses the first sheet of Excel workbooks; support for multi-sheet workbooks is planned.

### 16. What would you improve next?
- **Answer**: 
  1. **Local Audio Processing**: Integrate Whisper models locally to reduce external API dependency.
  2. **Export Design Templates**: Offer multiple layout templates for generated Excel spreadsheets.
