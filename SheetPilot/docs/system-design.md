# System Design — SheetPilot AI

This document details the complete production-grade system design of SheetPilot AI, structured to fulfill the 100-point B.Tech Capstone Project Rubric.

---

## 1. Executive Summary
SheetPilot AI is an AI-driven, secure spreadsheet copilot designed for automated data manipulation, profiling, and analytics. It translates natural speech and text commands into safe, deterministic data actions. By utilizing structured JSON schemas instead of executing LLM-generated Python code, it provides a secure alternative for enterprise data processing.

## 2. Problem Statement
Non-technical users struggle to analyze datasets because querying requires proficiency in Python (Pandas), SQL, or advanced spreadsheet formulas. Conversational AI assistants attempt to resolve this by writing code and executing it via standard `eval()` or `exec()`. This execution pattern is highly vulnerable to remote code execution (RCE) and injection attacks, exposing backend infrastructure.

## 3. Goals
- Provide natural language and voice spreadsheet automation.
- Enforce strict security validation using schema-based translation and whitelisting.
- Deliver interactive data exploration, grid cell editing, and dynamic visualizations.
- Implement session state durability with full undo/redo transaction safety.
- Achieve compatibility for deployment on Streamlit Community Cloud.

## 4. Non-Goals
- **No Arbitrary Python Execution**: The system will not generate or run arbitrary Python scripts on the backend.
- **No Large File Database Storage**: Files are processed in-memory and are not persisted permanently to backend databases.
- **No Multi-User Concurrent File Sharing**: Sessions are strictly isolated to the browser tab session memory.

## 5. Functional Requirements
- **Spreadsheet Uploads**: Ingestion of CSV and Excel files.
- **Natural Language Parsing**: Text or audio-to-text queries.
- **Multilingual Speech Detection**: Support and preservation of regional languages.
- **Data Editing**: In-grid cell edits with save/discard capability.
- **Visualization**: Recommends and renders customizable Plotly figures.
- **Operation History**: Inspect timeline logs and undo modifications.
- **Excel Exports**: Stylized spreadsheet downloads with adjusted spacing.

## 6. Non-Functional Requirements
- **Failsafe Security**: Zero RCE vulnerability; all operations run through validators.
- **Response Time**: AI response translation and local data execution within 1.5–3 seconds.
- **Compatibility**: Runs on Linux and Windows platforms without system-level binary dependencies.
- **State Reliability**: Unchanged inputs are not lost; session states are protected from Streamlit rerun resets.

## 7. Architecture
SheetPilot AI follows a decoupled MVC-like architectural pattern:
- **Model**: Centralized state manager (`src/state.py`) containing data frames, parameters, history list, and quality metrics.
- **View**: Streamlit dashboard app containing visual grids, metrics, tabs, and control panels.
- **Controller/Engine**: Gemini translator client (`src/ai/`), Safety Validator (`src/execution/safety.py`), and Pandas execution engine (`src/execution/operation_engine.py`).

## 8. Data Flow
1. **Ingress**: User uploads a file. `loader.py` compiles the DataFrame.
2. **Quality Audit**: `profiler.py` evaluates data quality metrics.
3. **Query Capture**: User speaks/types a command.
4. **Translation**: `gemini_client.py` uses dynamic context and prompt rules to call `gemini-2.5-flash`, outputting a `StructuredOperation` JSON schema.
5. **Validation**: `safety.py` audits references, whitelisted operators, and arithmetic syntax.
6. **Execution**: `operation_engine.py` applies safe Pandas functions.
7. **Rendering**: Results are visualized in Plotly and rendered in the data grid.

## 9. Session State
All data-associated keys are encapsulated within `SessionStateManager` (`src/state.py`):
- `current_df`: Stores the active dataset state.
- `original_df`: Backed-up original dataset for resets.
- `history`: List containing query strings, timestamps, languages, and operational outputs.
- `undo_stack`: Stack storing previous DataFrame states for rollbacks.
- `unsaved_changes`: Boolean flag tracking edited cells in the interactive grid.

## 10. Data Pipeline
The data ingestion engine (`src/data/loader.py`) parses binary file streams. If the input is a CSV, it reads via `pd.read_csv` with automatic encoding detection. If it is an Excel workbook, it utilizes `openpyxl` as the parser engine to support `.xlsx` formats. The profiling pipeline calculates cell fill-rates, duplicates, missing cells, column lists, and summary statistics.

## 11. Gemini Integration
Using the official `google-genai` SDK and the `gemini-2.5-flash` model, SheetPilot AI integrates AI translation capabilities:
- **Fuzzy Token Matching**: Rather than sending the entire dataset, the client extracts only column profiles and sample rows relevant to the user's query, reducing token usage and latency.
- **SDK Compliance**: The API connection is established safely using environment variables or Streamlit Community Cloud secrets.

## 12. Prompt Engineering
System instructions in `src/ai/prompts.py` define the AI's boundaries:
- Enforce output strictness: The AI is treated solely as a compiler that outputs JSON fitting the Pydantic schema.
- Explicitly block code creation: System prompts forbid generating code, scripts, or executing external terminal commands.

## 13. Structured Output
To prevent AI hallucinations, we configure the Gemini API request with a strict return contract:
- `response_mime_type="application/json"`
- `response_schema=StructuredOperation`

Gemini must return a structured operational payload defining the filters, sorting rules, grouping indices, math transformations, or limits.

## 14. Execution Safety
The `SafetyValidator` (`src/execution/safety.py`) runs a two-step validation:
1. **Structural Audit**: Validates that all requested columns match the dataset's actual column names.
2. **Expression Audit**: Checks that operators are whitelisted (`>`, `<`, `==`, `!=`, `contains`, `in`). For column math transformations, a strict regex checks that only safe math operators (`+`, `-`, `*`, `/`) and numeric constants are used, blocking system keywords (`import`, `eval`, `getattr`, `__`).

## 15. Voice Pipeline
The client-side Voice Engine captures WebM/WAV audio streams. 
- **Audits**: Audio files must be larger than 120 bytes (preventing empty files) and shorter than 60 seconds (preventing timeouts).
- **Gemini Transcription**: The audio bytes are sent to Gemini for native transcription, eliminating the need for a separate speech-to-text API or system-level audio dependencies (e.g. PyAudio, FFmpeg).

## 16. Multilingual Strategy
Multilingual support is built-in:
- **Accents**: Gemini's multimodal capabilities allow high-fidelity recognition of Indian accents and regional languages (Hindi, Telugu, Tamil, Kannada, Bengali).
- **Preservation**: The original transcript language is preserved, allowing the user to review the transcript before submission.
- **Language Detection**: The detected language is returned as part of the structured JSON response.

## 17. Visualization Strategy
The visualization module (`src/visualization/charts.py`) recommends chart types based on the column metrics:
- Recommends **Line/Bar charts** for combinations of categorical and numerical columns.
- Recommends **Scatter plots** for two numerical columns.
- Recommends **Histograms/Box plots** for numerical distribution analysis.
Charts are rendered using Plotly Express with dark-themed layouts.

## 18. Export Strategy
The Excel export engine (`src/export/exporters.py`) creates structured, readable documents:
- **Visual Styles**: Sheet headers are styled with dark fills (`#1E293B`) and white bold text.
- **Usability**: Adjusts column widths based on maximum string lengths and enables default gridlines.

## 19. Error Handling
SheetPilot AI implements strict error boundaries:
- **API Errors**: If the Gemini API key is missing or invalid, the app falls back to manual operations rather than crashing, displaying a message in the UI.
- **Execution Errors**: If a Pandas operation fails, the exception is caught, and the error details are rendered in the dashboard without crashing the main thread.

## 20. Security
Security checks prevent unauthorized access:
- **Sandbox execution**: Strict whitelist enforcement restricts all DataFrame transformations to safe, built-in Pandas methods.
- **No CLI execution**: The app blocks terminal execution commands (`os.system`, `subprocess`).
- **No credential leaks**: API keys are loaded via secure channels and never printed to the logs.

## 21. Performance
Performance is optimized for execution speed:
- In-memory operations minimize disk I/O overhead.
- Fuzzy matching filters metadata sent to Gemini, keeping prompt context lightweight.
- Streamlit forms prevent redundant, state-clearing app reruns.

## 22. Deployment
SheetPilot AI is optimized for **Streamlit Community Cloud**:
- No system-level package dependencies (no FFmpeg, PortAudio, or compile tools required).
- Relies on Standard library python packages and mainstream python libraries (Pandas, Plotly, OpenPyXL).
- Key configuration is managed through Streamlit Secrets.

## 23. Testing
Automated testing is managed by the `unittest` framework:
- Unit tests verify: Data loaders, profiling calculations, safety validations, Pandas operations, visualization recommendations, exporters, and session managers.
- Tests can be run locally using the command: `python -m unittest discover tests`.

## 24. Limitations
- **File Size**: Large datasets may encounter memory limits on Streamlit Cloud's free hosting tier (1GB RAM limit).
- **Workbook Sheets**: Supports only the first sheet of Excel files.
- **Single-Turn Audio**: Captures speech in single inputs rather than streaming continuous audio.

## 25. Future Improvements
- **Chunked File Processing**: Implement chunking logic to support files larger than 500MB on Streamlit Cloud.
- **Multi-Sheet Support**: Add sheet selection controls to the dashboard interface.
- **Direct Database Connectors**: Support connecting directly to cloud databases (PostgreSQL, Snowflake, BigQuery) in addition to flat files.
