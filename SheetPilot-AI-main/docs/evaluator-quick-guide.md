# Evaluator Quick Presentation Guide — SheetPilot AI

This guide helps presenters explain SheetPilot AI's system architecture, technical differentiators, and features in a 2-3 minute presentation.

---

## ⚡ 30-Second Pitch
SheetPilot AI is an AI-driven, secure spreadsheet copilot designed for automated data manipulation, profiling, and analytics. It translates natural speech and text commands into safe, deterministic data actions. By utilizing structured JSON schemas instead of executing LLM-generated Python code, it provides a secure alternative for enterprise data processing.

---

## 🎨 System Architecture Pipeline

The system processes commands through a decoupled execution chain:

```text
User Input (Voice/Text)
  ↓
Multimodal Speech-to-Text (Transcribed by Gemini)
  ↓
Context Builder (Selected column metadata + sample rows)
  ↓
Gemini AI Engine (Translates query to JSON parameters)
  ↓
Safety Validator (Checks column names & whitelists)
  ↓
Pandas Engine (Executes safe Pandas operations in-memory)
  ↓
Plotly Analytics & Styled openpyxl Export
```

---

## 🛡️ Core Differentiators

### 1. Technical Differentiator
*Traditional assistants write Python code and execute it using `eval()` or `exec()`, exposing servers to code injection.*
- **SheetPilot AI's Approach**: Gemini compiles user intent into a **Structured Operation Schema** (specifying column names, whitelisted operators, and parameters). The system executes these parameters using built-in, deterministic Pandas code.

### 2. AI Differentiator
- **Dynamic Context Selection**: Rather than sending entire datasets to the API, the context builder matches keywords to select only relevant column statistics and sample rows.
- **Multilingual Support**: Supports native accent audio capture (Hindi, Telugu, Tamil, Kannada) and preserves original language scripts in the UI.

### 3. UX Differentiator
- **Workspace Navigation Tabs**: Interactive workspace separated into a copilot command interface, editable data editor grid with dirty-state checks, column deep-dive metrics, custom Plotly charting playboards, and history undo timelines.

### 4. Security Differentiator
- **Regex & Operator Whitelists**: The validator rejects operations referencing non-existent columns, non-numeric arguments for numeric columns, and math expressions containing Python keywords (e.g., `import`, `globals`).

---

## 🚀 Recommended Capstone Demo Flow (2 Minutes)

1. **Onboarding**: Start the app. Point out the empty-state cards. Click the quick-action command `⚡ Show top 10 Q3 revenue records`. The sample dataset loads, and Gemini executes the command instantly.
2. **Tab 1 — Ask SheetPilot**:
   - Highlight the **Data Quality Score** (e.g. 87.5%) and its breakdown popover in the persistent header.
   - Demonstrate a multilingual input. Click the microphone button and say *"salary strictly greater than 80000"* or type *"Department represents Sales"*. Show the detected language box and original voice transcription.
   - Point out the **Pandas Compilation Sandbox** at the bottom, proving that SheetPilot translates commands into structured steps and compiles clean, viewable Pandas code.
3. **Tab 2 — Data Grid**: Switch tabs. Double-click a cell to edit its value. Note the banner warning of unsaved cell edits. Click **Save Changes**.
4. **Tab 3 — Column Explorer**: Show how each column type is automatically categorized (identifier, categorical, currency-like) with missing percentage summaries.
5. **Tab 4 — Analytics Dashboard**: Plot a custom chart on the fly by selecting X-axis, Y-axis, and group colors.
6. **Tab 5 — Operation History**: Show the timeline of executed commands and click **Undo** to roll back the last action.
7. **Export**: Click **Download Styled Excel** in the copilot tab to download a professionally formatted spreadsheet.
