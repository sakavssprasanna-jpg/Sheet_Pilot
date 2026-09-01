# Capstone Demo Walkthrough Script — SheetPilot AI

This script guides you through a 3–5 minute live presentation of SheetPilot AI for the Capstone evaluation panel.

---

### ⏱️ 0:00–0:30 | The Problem
> **Presenter Pitch**:
> "Good morning, members of the evaluation panel. Traditional spreadsheet tools require users to manually write complex formulas, pivot tables, or write custom macros. Modern AI assistants try to solve this, but they usually write raw Python code and execute it using risky functions like `eval()` or `exec()`. This introduces security risks. SheetPilot AI solves this by acting as a secure data copilot, translating natural voice and text commands into safe, deterministic data actions."

---

### ⏱️ 0:30–1:00 | Product Overview & Landing State
> **Action**: Point to the dark-themed landing page.
> **Presenter Pitch**:
> "Here is SheetPilot AI's onboarding landing page. Notice the clean dark theme. To help users get started immediately, we have integrated a quick-action command card: `⚡ Show top 10 Q3 revenue records`. Clicking this loads our pre-loaded sample dataset, fills the search field, and runs the operation instantly."
> **Action**: Click the quick-action button.

---

### ⏱️ 1:00–1:30 | Upload and Data Quality Profiling
> **Action**: Point to the header.
> **Presenter Pitch**:
> "The sample dataset is now loaded. In the persistent header, we display the calculated **Data Quality Score** of 87.5%. Hovering over this score shows a breakdown of cell fill rates, row uniqueness, empty columns, and mixed data types, calculated using a weighted 4-factor formula."

---

### ⏱️ 1:30–2:15 | Multilingual Voice Command
> **Action**: Switch to the **Ask SheetPilot** tab. Click the microphone button and speak a command (or type it): *"Filter Salary strictly greater than 80000"*.
> **Presenter Pitch**:
> "SheetPilot AI features a native audio recording pipeline. The browser captures voice input as WebM bytes and sends it directly to Gemini. The model transcribes the speech, detects the spoken language, and updates the UI status cards."

---

### ⏱️ 2:15–2:45 | Gemini Structured Interpretation & Validation
> **Action**: Expand the **AI Interpretation** card.
> **Presenter Pitch**:
> "Notice that SheetPilot did not write raw Python code. Instead, Gemini translated the voice command into a structured JSON operation schema. Before execution, SheetPilot's validator audits the schema, checking it against active column names and whitelisted operators. This ensures that only safe, valid operations are executed."

---

### ⏱️ 2:45–3:15 | Safe execution & Pandas Sandbox
> **Action**: Point to the bottom sandbox section.
> **Presenter Pitch**:
> "Once validated, the operation is executed in-memory using Pandas. The compiled Pandas code is displayed at the bottom of the page, showing users the exact, transparent steps taken by the execution engine."

---

### ⏱️ 3:15–3:45 | KPI, Visualizations & Insights
> **Action**: Scroll down to the result visualization section.
> **Presenter Pitch**:
> "Below the query block, SheetPilot displays dynamic KPI cards summarizing rows, columns, and numeric averages. It also recommends and renders interactive Plotly Express charts (in this case, a Bar Chart matching our category filters) alongside AI-generated insights."

---

### ⏱️ 3:45–4:15 | Data Grid & Undo History
> **Action**: Click on the **Data Grid** tab. Click a cell, change its value, and click **Save Changes**. Then, click the **Operation History** tab.
> **Presenter Pitch**:
> "Users can also manually override cell values in the Data Grid. The editor tracks changes and warns users of unsaved edits. If a user makes a mistake, they can open the Operation History tab and click **Undo** to roll back the changes."

---

### ⏱️ 4:15–4:45 | Styled Excel Export
> **Action**: Click the **Download Styled Excel** button. Open the downloaded file.
> **Presenter Pitch**:
> "Finally, users can export their processed data. SheetPilot does not generate a generic spreadsheet; it formats the Excel sheet with aligned columns, formatted headers, and auto-fitted column widths."

---

### ⏱️ 4:45–5:00 | Conclusion
> **Presenter Pitch**:
> "SheetPilot AI provides a secure, interactive interface for spreadsheet analysis. All unit tests pass, secrets are protected, and the application is ready for deployment. Thank you, and I welcome any questions from the panel."
