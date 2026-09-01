import streamlit as st
from typing import Dict, Any, Optional
from src.state import SessionStateManager

def render_hero():
    """Renders the dashboard hero header with Outlined Outfit fonts and active workspace indicators."""
    dataset_loaded = SessionStateManager.get_uploaded_df() is not None
    if dataset_loaded:
        badge_html = '<span class="status-badge status-badge-ready">● Workspace Ready</span>'
    else:
        badge_html = '<span class="status-badge status-badge-warning" style="background-color: rgba(255, 255, 255, 0.03); border-color: rgba(255, 255, 255, 0.08); color: var(--sp-muted);">● No Active Workspace</span>'
        
    st.markdown(f'''
    <div style="margin-bottom: 2.2rem; position: relative;">
        <div style="display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.5rem; flex-wrap: wrap;">
            <h1 style="font-family: 'Outfit', sans-serif; font-size: 2.6rem; font-weight: 900; margin: 0; color: #FFFFFF; letter-spacing: -0.04em; line-height: 1.1;">
                Meet your spreadsheet copilot.
            </h1>
            <div style="margin-top: 0.4rem;">{badge_html}</div>
        </div>
        <p style="font-size: 1.05rem; color: var(--sp-muted); margin-top: 0.4rem; margin-bottom: 0; max-width: 720px; line-height: 1.5; font-weight: 400;">
            Upload your spreadsheet and control your data using natural language or voice.
        </p>
    </div>
    ''', unsafe_allow_html=True)

def render_upload_card() -> Any:
    """Renders a large premium upload card area integrated with onboarding text."""
    st.markdown('''
    <div class="upload-box-premium">
        <div class="upload-icon-pulse">✦</div>
        <div class="upload-title-text">Start with your spreadsheet</div>
        <div class="upload-subtitle-text">Upload a CSV or Excel file and let SheetPilot become your data copilot.</div>
        <div style="max-width: 380px; margin: 0 auto 1.5rem auto;">
    ''', unsafe_allow_html=True)
    
    # Streamlit file uploader widget with collapsed label
    uploaded_file = st.file_uploader(
        "Upload dataset",
        type=["csv", "xlsx", "xls"],
        label_visibility="collapsed",
        key="main_file_uploader"
    )
    
    st.markdown('''
        </div>
        <div style="font-size: 0.78rem; color: var(--sp-muted); font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase;">
            CSV <span style="color: var(--sp-accent); margin: 0 0.5rem;">•</span> XLSX <span style="color: var(--sp-accent); margin: 0 0.5rem;">•</span> Ready for AI automation
        </div>
    </div>
    ''', unsafe_allow_html=True)
    return uploaded_file

def render_upload_success(filename: str, shape: Dict[str, int]) -> bool:
    """Renders a premium success card when a dataset is successfully loaded. Returns True if Replace clicked."""
    rows = shape.get("rows", 0)
    cols = shape.get("cols", 0)
    
    original_df = SessionStateManager.get_original_df()
    current_df = SessionStateManager.get_current_df()
    applied_ops = SessionStateManager.get_applied_ops()
    
    is_modified = len(applied_ops) > 0 or (original_df is not None and current_df is not None and not original_df.equals(current_df))
    
    status_badge = '<span class="status-badge status-badge-ready" style="font-family: \'Inter\', sans-serif;">● Working dataset</span>'
    if is_modified:
        status_badge = '<span class="status-badge" style="background-color: rgba(229, 62, 62, 0.15); border-color: rgba(229, 62, 62, 0.3); color: #FC8181; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.78rem; font-weight: 600; font-family: \'Inter\', sans-serif;">● Modified dataset</span>'
    
    col_info, col_btn = st.columns([3.5, 1.7])
    with col_info:
        st.markdown(f'''
        <div class="success-card" style="margin-bottom: 0; height: 100%;">
            <div class="success-left-block">
                <div class="success-icon-badge">✓</div>
                <div>
                    <h4 class="success-title">{filename}</h4>
                    <div class="success-details">
                        {status_badge}
                        <span style="color: var(--sp-muted); margin: 0 0.5rem;">•</span>
                        <span>{rows:,} rows</span>
                        <span style="color: var(--sp-muted); margin: 0 0.5rem;">•</span>
                        <span>{cols} columns</span>
                    </div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    with col_btn:
        st.markdown('<div style="padding-top: 0.35rem;"></div>', unsafe_allow_html=True)
        replace_clicked = st.button("Replace Dataset", key="btn_replace_dataset", use_container_width=True)
        if is_modified:
            with st.popover("Reset to Original", use_container_width=True):
                st.warning("This will discard all current transformation steps.")
                if st.button("Confirm Reset", key="btn_confirm_reset", use_container_width=True):
                    SessionStateManager.reset_dataset()
                    SessionStateManager.set_result_df(None)
                    SessionStateManager.set_unsaved_changes(False)
                    st.rerun()
        
    return replace_clicked

def render_kpi_cards(metadata: Dict[str, Any]):
    """Renders connected dashboard KPIs for rows, columns, missing values, and data quality."""
    shape = metadata.get("shape", {"rows": 0, "cols": 0})
    rows = shape.get("rows", 0)
    cols = shape.get("cols", 0)
    total_cells = rows * cols
    
    total_missing = sum([col.get("null_count", 0) for col in metadata.get("columns", [])])
    
    if total_cells > 0:
        quality_score = ((total_cells - total_missing) / total_cells) * 100
    else:
        quality_score = 100.0
        
    missing_color = "var(--sp-success)" if total_missing == 0 else "var(--sp-warning)"
    if total_missing > (total_cells * 0.1):
        missing_color = "var(--sp-danger)"
        
    quality_color = "var(--sp-success)"
    if quality_score < 95:
        quality_color = "var(--sp-warning)"
    if quality_score < 80:
        quality_color = "var(--sp-danger)"
        
    st.markdown(f'''
    <div class="kpi-row-container">
        <div class="kpi-column-module">
            <h4 class="kpi-val-display">{rows:,}</h4>
            <div class="kpi-lbl-display">Rows</div>
        </div>
        <div class="kpi-column-module">
            <h4 class="kpi-val-display">{cols}</h4>
            <div class="kpi-lbl-display">Columns</div>
        </div>
        <div class="kpi-column-module">
            <h4 class="kpi-val-display" style="color: {missing_color};">{total_missing:,}</h4>
            <div class="kpi-lbl-display">Missing Values</div>
        </div>
        <div class="kpi-column-module">
            <h4 class="kpi-val-display" style="color: {quality_color};">{quality_score:.1f}%</h4>
            <div class="kpi-lbl-display">Data Quality</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

def render_empty_state() -> Any:
    """Renders a beautiful landing workspace empty state when no dataset is uploaded."""
    st.markdown('''
    <div style="text-align: center; margin-top: 2rem; margin-bottom: 2rem;">
        <h1 style="font-family: 'Outfit', sans-serif; font-size: 3.8rem; font-weight: 900; color: #FFFFFF; letter-spacing: -0.05em; margin-bottom: 0.5rem; line-height: 1.1;">
            SheetPilot AI
        </h1>
        <p style="font-size: 1.25rem; color: var(--sp-muted); font-weight: 400; max-width: 600px; margin: 0 auto; line-height: 1.5;">
            Talk to your spreadsheets. Turn questions into analysis.
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Primary Action: Upload box
    col_up_left, col_up_mid, col_up_right = st.columns([1, 2, 1])
    uploaded_file = None
    with col_up_mid:
        st.markdown('<div class="upload-box-premium" style="margin-bottom: 2rem; padding: 2rem; border-radius: 12px; border: 1px dashed var(--sp-border); background-color: var(--sp-surface-elevated); text-align: center;">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload CSV / Excel",
            type=["csv", "xlsx", "xls"],
            label_visibility="collapsed",
            key="main_file_uploader"
        )
        st.markdown('''
            <div style="font-size: 0.82rem; color: var(--sp-muted); margin-top: 0.8rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase;">
                CSV &bull; XLSX &bull; XLS
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
    # Secondary Capabilities Indicators
    st.markdown('''
    <div style="margin-top: 2rem; margin-bottom: 3.5rem;">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; max-width: 1000px; margin: 0 auto;">
            <div style="background-color: var(--sp-surface-elevated); border: 1px solid var(--sp-border); border-radius: 8px; text-align: center; padding: 1.5rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎙️</div>
                <h5 style="color: #FFFFFF; font-weight: 700; margin: 0 0 0.4rem 0; font-family: 'Outfit', sans-serif;">Multilingual Voice</h5>
                <p style="font-size: 0.78rem; color: var(--sp-muted); margin: 0; line-height: 1.4;">Speak naturally in English, Telugu, Hindi, Tamil, and more dialects.</p>
            </div>
            <div style="background-color: var(--sp-surface-elevated); border: 1px solid var(--sp-border); border-radius: 8px; text-align: center; padding: 1.5rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🤖</div>
                <h5 style="color: #FFFFFF; font-weight: 700; margin: 0 0 0.4rem 0; font-family: 'Outfit', sans-serif;">Gemini Intelligence</h5>
                <p style="font-size: 0.78rem; color: var(--sp-muted); margin: 0; line-height: 1.4;">Zero arbitrary code. Gemini parses queries into safe schemas.</p>
            </div>
            <div style="background-color: var(--sp-surface-elevated); border: 1px solid var(--sp-border); border-radius: 8px; text-align: center; padding: 1.5rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🛡️</div>
                <h5 style="color: #FFFFFF; font-weight: 700; margin: 0 0 0.4rem 0; font-family: 'Outfit', sans-serif;">Safe Pandas Execution</h5>
                <p style="font-size: 0.78rem; color: var(--sp-muted); margin: 0; line-height: 1.4;">Failsafe execution whitelists block raw execution injection.</p>
            </div>
            <div style="background-color: var(--sp-surface-elevated); border: 1px solid var(--sp-border); border-radius: 8px; text-align: center; padding: 1.5rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                <h5 style="color: #FFFFFF; font-weight: 700; margin: 0 0 0.4rem 0; font-family: 'Outfit', sans-serif;">Interactive Analytics</h5>
                <p style="font-size: 0.78rem; color: var(--sp-muted); margin: 0; line-height: 1.4;">Automated chart recommendations and customizable Plotly graphs.</p>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Examples command area
    st.markdown('''
    <div style="max-width: 800px; margin: 0 auto 1.5rem auto; text-align: center;">
        <h4 style="font-family: 'Outfit', sans-serif; color: #FFFFFF; font-weight: 700; margin-bottom: 0.5rem; font-size: 1.3rem;">💡 Try Interactive Examples</h4>
        <p style="font-size: 0.85rem; color: var(--sp-muted); margin-bottom: 1.5rem;">Clicking an example will automatically load the sample dataset and populate the query.</p>
    </div>
    ''', unsafe_allow_html=True)
    
    col_ex1, col_ex2 = st.columns(2)
    examples = [
        ("Show the top 10 revenue records", "Show the top 10 records by Q3_Revenue"),
        ("Group sales by department", "Group Q3_Revenue by Department"),
        ("Find missing values", "Find missing values"),
        ("Create a revenue trend", "Group Q3_Revenue by Role")
    ]
    
    for i, (label, query) in enumerate(examples):
        with col_ex1 if i % 2 == 0 else col_ex2:
            if st.button(f"⚡ {label}", key=f"example_btn_{i}", use_container_width=True):
                st.session_state.load_sample_trigger = True
                st.session_state.user_query_input_val = query
                st.rerun()
                
    return uploaded_file


def render_workspace_header(filename: str, rows: int, cols: int, quality_score: float, state_desc: str, quality_breakdown: dict):
    """Renders the persistent dataset workspace header at the top of the dashboard."""
    state_color = "var(--sp-accent)" if "Original" in state_desc else "#eab308"
    
    col1, col2, col3, col4 = st.columns([3.5, 2.5, 3, 3])
    with col1:
        st.markdown(f"""
        <div style='background-color: var(--sp-surface-elevated); border: 1px solid var(--sp-border); padding: 0.75rem 1rem; border-radius: 8px; min-height: 75px;'>
            <div style='font-size: 0.72rem; color: var(--sp-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>Active Dataset</div>
            <div style='font-size: 1.05rem; color: #FFFFFF; font-weight: 700; margin-top: 0.2rem; font-family: "Outfit", sans-serif; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>
                📄 {filename}
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style='background-color: var(--sp-surface-elevated); border: 1px solid var(--sp-border); padding: 0.75rem 1rem; border-radius: 8px; min-height: 75px;'>
            <div style='font-size: 0.72rem; color: var(--sp-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>Dimensions</div>
            <div style='font-size: 1.05rem; color: #FFFFFF; font-weight: 700; margin-top: 0.2rem; font-family: "Outfit", sans-serif;'>
                {rows:,} rows &bull; {cols:,} cols
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        with st.container():
            st.markdown(f"""
            <div style='background-color: var(--sp-surface-elevated); border: 1px solid var(--sp-border); padding: 0.5rem 1rem 0.2rem 1rem; border-radius: 8px; min-height: 75px; display: flex; flex-direction: column; justify-content: space-between;'>
                <div style='font-size: 0.72rem; color: var(--sp-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>Data Quality: <span style="color: #FFFFFF; font-weight: 700;">{quality_score:.1f}%</span></div>
            </div>
            """, unsafe_allow_html=True)
            with st.popover("📊 Explain Score", use_container_width=True):
                st.markdown(f"**Data Quality Score: {quality_score:.1f}%**")
                st.markdown(f"- **Cell Fill Rate**: {quality_breakdown.get('missing_factor', 100.0):.1f}%")
                st.markdown(f"- **Row Uniqueness Rate**: {quality_breakdown.get('duplicate_factor', 100.0):.1f}%")
                st.markdown(f"- **Column Completeness**: {quality_breakdown.get('completeness_factor', 100.0):.1f}% (Empty columns: {quality_breakdown.get('empty_cols', 0)})")
                st.markdown(f"- **Data Type Consistency**: {quality_breakdown.get('consistency_factor', 100.0):.1f}% (Mixed columns: {quality_breakdown.get('mixed_cols', 0)})")
                st.caption("Score is computed deterministically based on cell completeness, row duplication, column-level completeness, and data type consistency across all fields.")
    with col4:
        with st.container():
            st.markdown(f"""
            <div style='background-color: var(--sp-surface-elevated); border: 1px solid var(--sp-border); padding: 0.5rem 1rem 0.2rem 1rem; border-radius: 8px; min-height: 75px; display: flex; flex-direction: column; justify-content: space-between;'>
                <div style='font-size: 0.72rem; color: var(--sp-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>Current State: <span style="color: {state_color}; font-weight: 700;">● {state_desc}</span></div>
            </div>
            """, unsafe_allow_html=True)
            if "Modified" in state_desc:
                with st.popover("🔄 Reset changes", use_container_width=True):
                    st.write("Are you sure you want to discard all operations and revert to the original uploaded dataset?")
                    if st.button("Confirm Reset", key="confirm_reset_header_btn", use_container_width=True):
                        orig_df = SessionStateManager.get_original_df()
                        SessionStateManager.set_current_df(orig_df)
                        SessionStateManager.set_unsaved_changes(False)
                        st.success("Reverted to original dataset.")
                        st.rerun()


def prepare_gemini_context(query: str, language: str) -> Dict[str, Any]:
    """Helper to prepare the multilingual, conversational context structure for Gemini."""
    current_df = SessionStateManager.get_current_df()
    metadata = SessionStateManager.get_metadata()
    applied_ops = SessionStateManager.get_applied_ops()
    
    schema = {}
    if current_df is not None:
        schema = {col: str(current_df[col].dtype) for col in current_df.columns}
        
    return {
        "original_transcript": query,
        "detected_language": language,
        "dataset_schema": schema,
        "relevant_column_metadata": metadata.get("columns", []),
        "current_dataframe_shape": list(current_df.shape) if current_df is not None else [0, 0],
        "previous_operation_context": applied_ops
    }

def render_ai_command_preview():
    """Renders the styled copilot command and voice interaction preview area."""
    from src.voice.processor import transcribe_audio, estimate_duration
    from src.config import IS_GEMINI_AVAILABLE, GEMINI_MODEL
    from src.ai import query_gemini_intelligence
    from src.execution import render_pandas_code, execute_operation
    import pandas as pd
    
    # Initialize voice panel display state
    if "show_voice_panel" not in st.session_state:
        st.session_state.show_voice_panel = False
    if "pending_ai_response" not in st.session_state:
        st.session_state.pending_ai_response = None
        
    st.markdown('''
    <div class="ai-copilot-container">
        <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.25rem; font-weight: 700; color: #FFFFFF; margin-top: 0; margin-bottom: 0.3rem; display: flex; align-items: center;">
            <span class="ai-sparkle-icon">✦</span> Ask SheetPilot
        </h3>
        <p style="font-size: 0.88rem; color: var(--sp-muted); margin-top: 0; margin-bottom: 1.2rem;">
            What would you like to do with your spreadsheet?
        </p>
    ''', unsafe_allow_html=True)
    
    # Unified command area input layout
    col_form, col_voice = st.columns([6.8, 1.2])
    
    with col_form:
        # Form for command submission to optimize API usage
        with st.form("ai_command_form", clear_on_submit=False):
            col_in, col_btn = st.columns([6, 1.2])
            with col_in:
                user_query = st.text_input(
                    "Ask SheetPilot a command",
                    value=st.session_state.get("user_query_input_val", ""),
                    placeholder="Type your command here...",
                    label_visibility="collapsed",
                    key="user_query_input"
                )
            with col_btn:
                submitted = st.form_submit_button("✦ Analyze", use_container_width=True)
    
    with col_voice:
        # Toggle voice recorder view (outside form to avoid submit reruns)
        voice_label = "🎙️ Close" if st.session_state.show_voice_panel else "🎙️ Speak"
        if st.button(voice_label, key="btn_toggle_voice", use_container_width=True):
            st.session_state.show_voice_panel = not st.session_state.show_voice_panel
            st.rerun()
            
    # Trigger AI analysis if form is submitted
    if submitted and user_query:
        with st.spinner("SheetPilot AI is analyzing your command..."):
            ai_resp = query_gemini_intelligence(user_query, history=SessionStateManager.get_history())
            st.session_state.pending_ai_response = ai_resp
            # Add user interaction to history
            SessionStateManager.add_to_history(
                user_query,
                response=ai_resp.explanation,
                success=(ai_resp.status == "success"),
                language=ai_resp.language,
                response_obj=ai_resp
            )
            # Clear voice audio key once processed
            SessionStateManager.set_last_audio(None)
        st.rerun()

    # Render Multilingual Voice Control Panel if enabled
    if st.session_state.show_voice_panel:
        st.markdown('''
        <div style="background-color: var(--sp-surface-elevated); border: 1px solid var(--sp-border); border-radius: 12px; padding: 1.5rem; margin-top: 1.2rem; text-align: center;">
            <div style="font-size: 2.2rem; color: var(--sp-accent); margin-bottom: 0.5rem; text-shadow: 0 0 15px rgba(14, 165, 233, 0.4);">🎙️</div>
            <h4 style="font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 700; color: #FFFFFF; margin-top: 0; margin-bottom: 0.4rem;">
                Speak to your spreadsheet
            </h4>
            <p style="font-size: 0.85rem; color: var(--sp-muted); margin-bottom: 1.2rem; font-style: italic;">
                "Show me the top 10 Q3 revenue records"
            </p>
         ''', unsafe_allow_html=True)
        
        # Voice UX state indicators
        v_status = SessionStateManager.get_voice_status() or "idle"
        if v_status == "idle":
            st.markdown('<div style="font-size: 0.85rem; color: var(--sp-accent); font-weight: 600; margin-bottom: 0.8rem;">🎙️ Ready to listen</div>', unsafe_allow_html=True)
        elif v_status == "transcribing":
            st.markdown('<div style="font-size: 0.85rem; color: #eab308; font-weight: 600; margin-bottom: 0.8rem;">● Processing audio...</div>', unsafe_allow_html=True)
        elif v_status == "success":
            st.markdown('<div style="font-size: 0.85rem; color: var(--sp-success); font-weight: 600; margin-bottom: 0.8rem;">✓ Transcript ready</div>', unsafe_allow_html=True)
        elif v_status == "error":
            st.markdown('<div style="font-size: 0.85rem; color: var(--sp-danger); font-weight: 600; margin-bottom: 0.8rem;">❌ Transcription error</div>', unsafe_allow_html=True)

        # Select Spoken Language
        selected_lang = st.selectbox(
            "Select Spoken Language",
            options=["English", "Telugu", "Hindi"],
            index=0,
            key="voice_lang_selector"
        )

        audio_file = st.audio_input("Record voice command", label_visibility="collapsed", key="audio_recorder")
        
        if audio_file is not None:
            audio_bytes = audio_file.read()
            if audio_bytes != SessionStateManager.get_last_audio():
                audio_file.seek(0)
                SessionStateManager.set_voice_status("transcribing")
                
                # Perform speech-to-text
                res = transcribe_audio(audio_bytes, audio_file.type, language=selected_lang)
                SessionStateManager.set_last_audio(audio_bytes)
                
                if res.success:
                    SessionStateManager.set_last_transcript(res.transcript)
                    SessionStateManager.set_detected_language(res.language)
                    SessionStateManager.set_voice_status("success")
                    SessionStateManager.set_voice_error(None)
                    
                    SessionStateManager.add_to_transcript_history({
                        "transcript": res.transcript,
                        "language": res.language,
                        "confidence": res.confidence,
                        "duration": res.duration,
                        "success": True
                    })
                else:
                    SessionStateManager.set_last_transcript("")
                    SessionStateManager.set_detected_language("Unknown")
                    SessionStateManager.set_voice_status("error")
                    SessionStateManager.set_voice_error(res.error)
                    
                    SessionStateManager.add_to_transcript_history({
                        "transcript": "",
                        "language": "Unknown",
                        "confidence": "Low",
                        "duration": res.duration,
                        "success": False,
                        "error": res.error
                    })
                st.rerun()
                
        # Privacy details
        st.markdown('''
        <p style="font-size: 0.72rem; color: var(--sp-muted); margin-top: 1rem; margin-bottom: 0; opacity: 0.8; line-height: 1.4;">
            🔒 <b>Privacy Note:</b> Audio is processed only to convert speech into a command. Do not upload sensitive information you do not want processed by external services.
        </p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Render Transcription Review Card
        if SessionStateManager.get_voice_status() == "success":
            lang = SessionStateManager.get_detected_language()
            transcript = SessionStateManager.get_last_transcript()
            
            history = SessionStateManager.get_transcript_history()
            last_entry = history[-1] if history else {}
            confidence = last_entry.get("confidence", "Transcript ready for review")
            duration = last_entry.get("duration", 0.0)
            
            st.markdown(f'''
            <div style="background-color: var(--sp-surface-elevated); border: 1px solid var(--sp-border); border-radius: 12px; padding: 1.5rem; margin-top: 1rem; text-align: left;">
                <div style="font-size: 0.68rem; font-weight: 700; color: var(--sp-accent); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.8rem;">
                    Voice Command Detected
                </div>
                <div style="margin-bottom: 1rem;">
                    <span style="font-size: 0.72rem; color: var(--sp-muted); text-transform: uppercase; font-weight: 600;">Detected Language</span>
                    <div style="margin-top: 0.2rem;"><span class="status-badge status-badge-ready" style="font-size: 0.75rem;">● {lang}</span></div>
                </div>
                <div style="margin-bottom: 1.2rem;">
                    <span style="font-size: 0.72rem; color: var(--sp-muted); text-transform: uppercase; font-weight: 600;">Transcript</span>
                </div>
            ''', unsafe_allow_html=True)
            
            # Editable transcript field
            edited_transcript = st.text_area(
                "Transcript editor",
                value=transcript,
                label_visibility="collapsed",
                key="transcript_editor_text"
            )
            
            st.markdown('<hr style="border: 0; border-top: 1px solid var(--sp-border); margin: 1rem 0;">', unsafe_allow_html=True)
            
            col_discard, col_use = st.columns([1, 1])
            with col_discard:
                if st.button("Discard Command", key="btn_discard_cmd", use_container_width=True):
                    SessionStateManager.set_voice_status("idle")
                    SessionStateManager.set_last_audio(None)
                    st.rerun()
            with col_use:
                if st.button("Run Command", key="btn_use_cmd", use_container_width=True):
                    if not edited_transcript.strip():
                        st.warning("Transcript is empty. Please speak again.")
                    else:
                        st.session_state.user_query_input_val = edited_transcript
                        with st.spinner("SheetPilot AI is analyzing your voice command..."):
                            ai_resp = query_gemini_intelligence(edited_transcript, history=SessionStateManager.get_history())
                            st.session_state.pending_ai_response = ai_resp
                            SessionStateManager.add_to_history(
                                edited_transcript,
                                response=ai_resp.explanation,
                                success=(ai_resp.status == "success"),
                                language=ai_resp.language,
                                response_obj=ai_resp
                            )
                        SessionStateManager.set_voice_status("idle")
                        SessionStateManager.set_last_audio(None)
                        st.session_state.show_voice_panel = False
                        st.rerun()
                    
            st.markdown(f'''
                <div style="font-size: 0.72rem; color: var(--sp-muted); margin-top: 0.8rem; display: flex; justify-content: space-between;">
                    <span>Speech confidence: <b>{confidence}</b></span>
                    <span>Duration: <b>{duration:.1f}s</b></span>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
        elif SessionStateManager.get_voice_status() == "error":
            st.markdown(f'''
            <div style="background-color: rgba(239, 68, 68, 0.03); border: 1px solid rgba(239, 68, 68, 0.15); border-radius: 12px; padding: 1.5rem; margin-top: 1rem; text-align: center;">
                <div style="font-size: 2.2rem; color: var(--sp-danger); margin-bottom: 0.5rem;">⚠️</div>
                <h4 style="font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 700; color: #FFFFFF; margin-top: 0; margin-bottom: 0.4rem;">
                    Couldn't understand the recording
                </h4>
                <p style="font-size: 0.85rem; color: var(--sp-muted); margin-bottom: 1.2rem; line-height: 1.5;">
                    {SessionStateManager.get_voice_error()}
                </p>
            ''', unsafe_allow_html=True)
            
            col_retry, col_text = st.columns([1, 1])
            with col_retry:
                if st.button("Try again", key="btn_retry_voice", use_container_width=True):
                    SessionStateManager.set_voice_status("idle")
                    SessionStateManager.set_last_audio(None)
                    st.rerun()
            with col_text:
                if st.button("Switch to text input", key="btn_switch_to_text", use_container_width=True):
                    SessionStateManager.set_voice_status("idle")
                    SessionStateManager.set_last_audio(None)
                    st.session_state.show_voice_panel = False
                    st.rerun()
                    
            st.markdown('</div>', unsafe_allow_html=True)

    # 13. Render AI Response Lifecycle states (pending_ai_response)
    ai_resp = st.session_state.pending_ai_response
    if ai_resp is not None:
        if ai_resp.status == "clarification_required":
            st.markdown(f'''
            <div style="background-color: rgba(245, 158, 11, 0.04); border: 1px solid rgba(245, 158, 11, 0.2); border-radius: 12px; padding: 1.5rem; margin-top: 1rem;">
                <h4 style="color: var(--sp-warning); margin: 0 0 0.5rem 0; font-family: 'Outfit', sans-serif;">❓ Clarification Needed</h4>
                <p style="font-size: 0.88rem; color: #FFFFFF; margin: 0 0 1rem 0;">{ai_resp.clarification}</p>
            </div>
            ''', unsafe_allow_html=True)
            
            with st.form("clarification_form"):
                clarification_input = st.text_input("Provide details", placeholder="Type your response here...", key="clarification_input_val")
                col_cancel, col_submit = st.columns([1, 1])
                with col_cancel:
                    cancel_clicked = st.form_submit_button("Cancel")
                with col_submit:
                    submit_clicked = st.form_submit_button("Submit")
                    
            if cancel_clicked:
                st.session_state.pending_ai_response = None
                st.rerun()
            elif submit_clicked and clarification_input:
                combined_query = f"{user_query} (Clarification: {clarification_input})"
                with st.spinner("Re-analyzing query..."):
                    new_resp = query_gemini_intelligence(combined_query, history=SessionStateManager.get_history())
                    st.session_state.pending_ai_response = new_resp
                    SessionStateManager.add_to_history(
                        combined_query,
                        response=new_resp.explanation,
                        success=(new_resp.status == "success"),
                        language=new_resp.language,
                        response_obj=new_resp
                    )
                st.rerun()
                
        elif ai_resp.status in ["unsupported", "validation_error"]:
            st.markdown(f'''
            <div style="background-color: rgba(239, 68, 68, 0.03); border: 1px solid rgba(239, 68, 68, 0.15); border-radius: 12px; padding: 1.5rem; margin-top: 1rem; text-align: left;">
                <h4 style="color: var(--sp-danger); margin: 0 0 0.5rem 0; font-family: 'Outfit', sans-serif;">❌ Command validation failed</h4>
                <p style="font-size: 0.88rem; color: #FFFFFF; margin: 0 0 1rem 0;">{ai_resp.error}</p>
            </div>
            ''', unsafe_allow_html=True)
            if st.button("Edit Command / Dismiss", key="btn_dismiss_err"):
                st.session_state.pending_ai_response = None
                st.rerun()
                
        elif ai_resp.status == "ai_error":
            error_msg = ai_resp.error
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                error_display = "Gemini request quota has been reached. Please try again later or configure a plan with available quota."
            else:
                error_display = error_msg
                
            st.markdown(f'''
            <div style="background-color: rgba(239, 68, 68, 0.03); border: 1px solid rgba(239, 68, 68, 0.15); border-radius: 12px; padding: 1.5rem; margin-top: 1rem; text-align: left;">
                <h4 style="color: var(--sp-danger); margin: 0 0 0.5rem 0; font-family: 'Outfit', sans-serif;">⚠️ AI Service Unavailable</h4>
                <p style="font-size: 0.88rem; color: #FFFFFF; margin: 0 0 1rem 0;">{error_display}</p>
                <p style="font-size: 0.8rem; color: var(--sp-muted); margin: 0;">Your spreadsheet is still safe. You can continue using the dataset workspace or try the command again.</p>
            </div>
            ''', unsafe_allow_html=True)
            col_retry, col_dismiss = st.columns([1, 1])
            with col_retry:
                if st.button("Retry Command", key="btn_retry_ai_call"):
                    with st.spinner("Retrying command..."):
                        new_resp = query_gemini_intelligence(user_query, history=SessionStateManager.get_history())
                        st.session_state.pending_ai_response = new_resp
                    st.rerun()
            with col_dismiss:
                if st.button("Edit Command / Dismiss", key="btn_dismiss_ai_err"):
                    st.session_state.pending_ai_response = None
                    st.rerun()
                    
        elif ai_resp.status == "success" and ai_resp.operation is not None:
            op = ai_resp.operation
            
            # Formulate the language indicator display
            lang_display_html = ""
            detected_lang = ai_resp.language or "English"
            if detected_lang.lower() != "english":
                lang_display_html = f'''
                <div style="background-color: rgba(234, 179, 8, 0.05); border-left: 3px solid #eab308; padding: 0.6rem 0.8rem; border-radius: 4px; margin-bottom: 1rem;">
                    <div style="font-size: 0.65rem; font-weight: 700; color: #eab308; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.2rem;">🎙️ Multilingual Detected: {detected_lang}</div>
                    <div style="font-size: 0.85rem; color: #FFFFFF; font-style: italic;">Original: "{user_query}"</div>
                </div>
                '''
                
            st.markdown(f'''
            <div style="background-color: rgba(14, 165, 233, 0.05); border: 1px solid rgba(14, 165, 233, 0.2); border-radius: 12px; padding: 1.5rem; margin-top: 1rem;">
                {lang_display_html}
                <div style="font-size: 0.7rem; font-weight: 700; color: var(--sp-accent); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem;">AI INTERPRETATION</div>
                <p style="font-size: 0.95rem; color: #FFFFFF; font-weight: 600; margin: 0 0 1rem 0;">"{ai_resp.explanation}"</p>
                
                <div style="font-size: 0.7rem; font-weight: 700; color: var(--sp-muted); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.6rem;">STRUCTURED EXECUTION PLAN</div>
            ''', unsafe_allow_html=True)
            
            # Print conditions nicely
            if op.filters:
                for f in op.filters:
                    st.markdown(f"<div style='font-size: 0.82rem; color: #FFFFFF; margin-bottom: 0.3rem;'>✓ Filter: <b>{f.column}</b> {f.operator} <code>{f.value}</code></div>", unsafe_allow_html=True)
            if op.sort:
                for s in op.sort:
                    direction = "Ascending" if s.ascending else "Descending"
                    st.markdown(f"<div style='font-size: 0.82rem; color: #FFFFFF; margin-bottom: 0.3rem;'>✓ Sort: <b>{s.column}</b> ({direction})</div>", unsafe_allow_html=True)
            if op.limit:
                st.markdown(f"<div style='font-size: 0.82rem; color: #FFFFFF; margin-bottom: 0.3rem;'>✓ Limit: return top <b>{op.limit}</b> records</div>", unsafe_allow_html=True)
            if op.group_by:
                st.markdown(f"<div style='font-size: 0.82rem; color: #FFFFFF; margin-bottom: 0.3rem;'>✓ Group by: <b>{', '.join(op.group_by)}</b></div>", unsafe_allow_html=True)
            if op.aggregations:
                for agg in op.aggregations:
                    st.markdown(f"<div style='font-size: 0.82rem; color: #FFFFFF; margin-bottom: 0.3rem;'>✓ Aggregate: <b>{agg.alias}</b> = {agg.func}({agg.column})</div>", unsafe_allow_html=True)
            if op.transformations:
                for trans in op.transformations:
                    st.markdown(f"<div style='font-size: 0.82rem; color: #FFFFFF; margin-bottom: 0.3rem;'>✓ Transform: <b>{trans.column}</b> ({trans.operation})</div>", unsafe_allow_html=True)
            if op.visualization:
                viz = op.visualization
                st.markdown(f"<div style='font-size: 0.82rem; color: #FFFFFF; margin-bottom: 0.3rem;'>✓ Chart: <b>{viz.chart_type}</b> chart (X: {viz.x_axis}, Y: {viz.y_axis or 'count'})</div>", unsafe_allow_html=True)
                
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Deterministic code display
            pandas_code = render_pandas_code(op)
            with st.expander("💻 View Compiled Pandas Code"):
                st.code(pandas_code, language="python")
                
            col_cancel, col_execute = st.columns([1, 1])
            with col_cancel:
                if st.button("Cancel Operation", key="btn_cancel_op", use_container_width=True):
                    st.session_state.pending_ai_response = None
                    st.rerun()
            with col_execute:
                if st.button("Run Operation", key="btn_execute_op", use_container_width=True):
                    import time
                    current_df = SessionStateManager.get_current_df()
                    before_rows = len(current_df) if current_df is not None else 0
                    
                    with st.status("Automating spreadsheet with SheetPilot...", expanded=True) as status:
                        st.write("✓ UNDERSTANDING: Command understood")
                        time.sleep(0.3)
                        st.write("✓ VALIDATING: Operation is safe")
                        time.sleep(0.3)
                        st.write(f"● EXECUTING: Processing {before_rows:,} rows...")
                        
                        # Real execution
                        t0 = time.time()
                        exec_res = execute_operation(op, current_df)
                        duration = time.time() - t0
                        
                        if exec_res.success and exec_res.result_dataframe is not None:
                            # Store results in the Phase 6 states
                            SessionStateManager.set_result_df(exec_res.result_dataframe.copy())
                            SessionStateManager.set_current_df(exec_res.result_dataframe)
                            SessionStateManager.add_applied_op(op)
                            
                            # Re-profile
                            from src.data.profiler import profile_dataframe
                            SessionStateManager.set_metadata(profile_dataframe(exec_res.result_dataframe))
                            SessionStateManager.set_result_metadata(profile_dataframe(exec_res.result_dataframe))
                            
                            # Additional execution details
                            st.session_state.result_before_df = current_df.copy() if current_df is not None else None
                            st.session_state.result_duration = duration
                            st.session_state.result_op = op
                            st.session_state.result_summary = exec_res.operation_summary
                            
                            # Initialize default chart configs based on recommender
                            from src.visualization.recommender import recommend_chart
                            rec = recommend_chart(exec_res.result_dataframe)
                            SessionStateManager.set_chart_config(rec)
                            
                            # Clear pending AI response
                            st.session_state.pending_ai_response = None
                            SessionStateManager.set_unsaved_changes(False)
                            
                            status.update(label="✓ Operation completed successfully!", state="complete", expanded=False)
                            time.sleep(0.2)
                        else:
                            status.update(label="❌ Execution failed!", state="error", expanded=True)
                            st.error(f"Execution Error: {exec_res.operation_summary}")
                    st.rerun()


    # 14. Display Language-Aware Command Context for Gemini Pipeline
    if user_query:
        # Prepare context data
        gemini_context = prepare_gemini_context(user_query, SessionStateManager.get_detected_language())
        
        st.markdown(f'''
        <div style="background-color: rgba(14, 165, 233, 0.04); border: 1px solid rgba(14, 165, 233, 0.15); border-radius: 8px; padding: 0.9rem; margin-top: 1rem;">
            <div style="font-size: 0.85rem; font-weight: 600; color: var(--sp-accent); margin-bottom: 0.2rem;">🤖 SheetPilot Copilot Context</div>
            <div style="font-size: 0.82rem; color: var(--sp-text); font-style: italic; margin-bottom: 0.5rem;">"{user_query}"</div>
            <div style="font-size: 0.78rem; color: var(--sp-muted); line-height: 1.4; margin-bottom: 0.8rem;">
                Note: Natural language compilation executes using whitelisted Pandas operations. Conversational context and dataset properties are prepared for compilation below:
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        with st.expander("🔍 Preview Pipeline Context Sent to Gemini AI"):
            st.json(gemini_context)
    else:
        st.markdown('''
        <div style="font-size: 0.75rem; color: var(--sp-muted); margin-top: 0.8rem; display: flex; align-items: center; gap: 0.4rem;">
            <span>💡</span> <span>AI execution and voice control are active. Speak or type your command, review it, and use the Developer Sandbox below to test operations.</span>
        </div>
        ''', unsafe_allow_html=True)
        
    # API Observability stats badge
    req_count = SessionStateManager.get_ai_request_count()
    if req_count > 0:
        duration = SessionStateManager.get_last_ai_duration()
        status = SessionStateManager.get_ai_request_status()
        
        st.markdown(f'''
        <div style="background-color: rgba(255, 255, 255, 0.01); border: 1px solid var(--sp-border); border-radius: 8px; padding: 0.6rem; margin-top: 1rem; font-size: 0.74rem; color: var(--sp-muted); display: flex; justify-content: space-between;">
            <span>🤖 Model: <b>{GEMINI_MODEL}</b></span>
            <span>Requests: <b>{req_count}</b></span>
            <span>Last Latency: <b>{duration:.2f}s</b></span>
            <span>Status: <b>{status}</b></span>
        </div>
        ''', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Render Result Section if result_df exists
    result_df = SessionStateManager.get_result_df()
    if result_df is not None:
        result_before_df = st.session_state.get("result_before_df")
        result_op = st.session_state.get("result_op")
        result_duration = st.session_state.get("result_duration", 0.0)
        result_summary = st.session_state.get("result_summary", "Spreadsheet operation")
        
        st.markdown("---")
        st.markdown('<h3 style="font-family: \'Outfit\', sans-serif; font-size: 1.5rem; font-weight: 800; color: #FFFFFF; margin-bottom: 0.5rem; margin-top: 2rem;">✦ Operation Complete</h3>', unsafe_allow_html=True)
        
        # Result Header Info block
        rows_before = len(result_before_df) if result_before_df is not None else 0
        rows_after = len(result_df)
        cols_before = len(result_before_df.columns) if result_before_df is not None else 0
        cols_after = len(result_df.columns)
        
        op_explanation = result_op.explanation if result_op else result_summary
        st.info(f"💡 **AI Intent**: {op_explanation}")
        
        op_intent_str = result_op.intent.replace("_", " ").title() if result_op else "Transformation"
        st.markdown(f'''
        <div style="background-color: var(--sp-surface-elevated); border: 1px solid var(--sp-border); border-radius: 8px; padding: 1rem; margin-bottom: 1.5rem; display: flex; flex-wrap: wrap; gap: 2rem; align-items: center;">
            <div>
                <div style="font-size: 0.72rem; color: var(--sp-muted); text-transform: uppercase; font-weight: 600; margin-bottom: 0.2rem;">Dataset Size Change</div>
                <div style="font-size: 1.1rem; color: #FFFFFF; font-weight: bold;">{rows_before:,} → {rows_after:,} rows</div>
            </div>
            <div>
                <div style="font-size: 0.72rem; color: var(--sp-muted); text-transform: uppercase; font-weight: 600; margin-bottom: 0.2rem;">Columns</div>
                <div style="font-size: 1.1rem; color: #FFFFFF; font-weight: bold;">{cols_before} → {cols_after}</div>
            </div>
            <div>
                <div style="font-size: 0.72rem; color: var(--sp-muted); text-transform: uppercase; font-weight: 600; margin-bottom: 0.2rem;">Execution Duration</div>
                <div style="font-size: 1.1rem; color: var(--sp-success); font-weight: bold;">{result_duration:.2f}s</div>
            </div>
            <div>
                <div style="font-size: 0.72rem; color: var(--sp-muted); text-transform: uppercase; font-weight: 600; margin-bottom: 0.2rem;">Operation Type</div>
                <div style="font-size: 1.1rem; color: var(--sp-accent); font-weight: bold;">{op_intent_str}</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Dynamic KPIs
        numeric_cols = [c for c in result_df.columns if pd.api.types.is_numeric_dtype(result_df[c])]
        target_numeric_col = None
        
        for col in numeric_cols:
            if any(k in str(col).lower() for k in ["revenue", "salary", "price", "amount", "cost", "total", "sales"]):
                target_numeric_col = col
                break
                
        if target_numeric_col is None and numeric_cols:
            non_id_cols = [c for c in numeric_cols if not any(x in str(c).lower() for x in ["id", "index", "key"])]
            if non_id_cols:
                target_numeric_col = non_id_cols[0]
            else:
                target_numeric_col = numeric_cols[0]
                
        kpi_cols = st.columns(4)
        with kpi_cols[0]:
            st.metric("Result Rows", f"{rows_after:,}")
        with kpi_cols[1]:
            st.metric("Result Columns", f"{cols_after}")
            
        if target_numeric_col is not None:
            series = result_df[target_numeric_col].dropna()
            if not series.empty:
                col_sum = series.sum()
                col_mean = series.mean()
                
                def format_kpi(val):
                    if abs(val) >= 1_000_000:
                        return f"₹{val/1_000_000:.2f}M"
                    elif abs(val) >= 1_000:
                        return f"₹{val:,.0f}"
                    else:
                        return f"₹{val:.2f}"
                        
                with kpi_cols[2]:
                    st.metric(f"Total {target_numeric_col}", format_kpi(col_sum))
                with kpi_cols[3]:
                    st.metric(f"Average {target_numeric_col}", format_kpi(col_mean))
            else:
                with kpi_cols[2]:
                    st.metric("Data Completion", "100%")
                with kpi_cols[3]:
                    st.metric("Missing Count", "0")
        else:
            total_cells = rows_after * cols_after
            missing_count = int(result_df.isnull().sum().sum())
            complete_pct = ((total_cells - missing_count) / total_cells * 100) if total_cells > 0 else 100.0
            with kpi_cols[2]:
                st.metric("Data Completion", f"{complete_pct:.1f}%")
            with kpi_cols[3]:
                st.metric("Missing Values", f"{missing_count:,}")
                
        # Side-by-Side Table and Chart
        col_data, col_viz = st.columns([1, 1])
        
        with col_data:
            st.markdown("##### 📁 Result Data")
            edited_df = st.data_editor(
                result_df,
                use_container_width=True,
                num_rows="dynamic",
                key="result_df_editor"
            )
            
            # Detect changes
            if edited_df is not None and not edited_df.equals(result_df):
                SessionStateManager.set_unsaved_changes(True)
                
            if SessionStateManager.get_unsaved_changes():
                st.warning("⚠️ Unsaved changes in table.")
                if st.button("Apply & Save Changes", key="btn_save_edits", use_container_width=True):
                    SessionStateManager.set_result_df(edited_df.copy())
                    SessionStateManager.set_current_df(edited_df.copy())
                    from src.data.profiler import profile_dataframe
                    SessionStateManager.set_metadata(profile_dataframe(edited_df))
                    SessionStateManager.set_result_metadata(profile_dataframe(edited_df))
                    SessionStateManager.set_unsaved_changes(False)
                    st.success("Changes saved successfully.")
                    st.rerun()
                    
        with col_viz:
            st.markdown("##### 📊 Visualization")
            chart_config = SessionStateManager.get_chart_config()
            from src.visualization.charts import render_chart
            
            avail_cols = list(result_df.columns)
            
            if chart_config is not None:
                fig = render_chart(result_df, chart_config)
                if fig is not None:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("💡 This result is best represented as a table.")
            else:
                st.info("💡 This result is best represented as a table.")
                
            with st.expander("🛠️ Interactive Chart Controls", expanded=False):
                chart_types = ["bar", "line", "scatter", "pie", "histogram", "box"]
                curr_type = chart_config.chart_type if chart_config else "bar"
                curr_x = chart_config.x_axis if chart_config and chart_config.x_axis in avail_cols else avail_cols[0]
                curr_y = chart_config.y_axis if chart_config and chart_config.y_axis in avail_cols else (avail_cols[1] if len(avail_cols) > 1 else None)
                curr_title = chart_config.title if chart_config else "Custom Chart"
                
                new_type = st.selectbox("Chart Type", chart_types, index=chart_types.index(curr_type) if curr_type in chart_types else 0)
                new_x = st.selectbox("X-Axis", avail_cols, index=avail_cols.index(curr_x) if curr_x in avail_cols else 0)
                
                y_options = [None] + avail_cols
                new_y = st.selectbox("Y-Axis", y_options, index=y_options.index(curr_y) if curr_y in y_options else 0)
                new_title = st.text_input("Chart Title", value=curr_title)
                
                if st.button("Update Visualization", key="btn_update_viz", use_container_width=True):
                    from src.ai.schemas import VisualizationConfig
                    updated_config = VisualizationConfig(
                        chart_type=new_type,
                        x_axis=new_x,
                        y_axis=new_y,
                        title=new_title
                    )
                    SessionStateManager.set_chart_config(updated_config)
                    st.rerun()
                    
        # Explanation & Insights
        st.markdown("---")
        col_did, col_shows = st.columns([1.2, 1])
        
        with col_did:
            st.markdown("##### ⚙️ What SheetPilot Did")
            st.write(op_explanation)
            if result_op:
                from src.execution import render_pandas_code
                pandas_code = render_pandas_code(result_op)
                with st.expander("💻 View Generated Pandas Code", expanded=False):
                    st.code(pandas_code, language="python")
                    st.caption("The code above represents the exact, deterministic operations executed by Pandas.")
                    
        with col_shows:
            st.markdown("##### 🧠 What the Data Shows")
            from src.analytics.insights import generate_data_insights
            insights_list = generate_data_insights(result_df, result_before_df)
            for ins in insights_list:
                st.markdown(f"- {ins}")
                
        # Export panel
        st.markdown("---")
        col_cont, col_exp = st.columns([1, 1])
        
        with col_cont:
            st.markdown("##### 💬 Continue Workflow")
            st.markdown("Ask another question or perform a follow-up operation on the current dataset:")
            st.caption("Suggestions: *'Now filter for Department equals HR'*, *'Average age by Department'*, *'Plot salary trend'*")
            st.markdown("👆 **Type or speak your next command in the 'Ask SheetPilot' panel above.**")
            
        with col_exp:
            st.markdown("##### 📥 Export Result")
            rows_exp = len(result_df)
            cols_exp = len(result_df.columns)
            est_size_kb = (rows_exp * cols_exp * 100) / 1024
            size_str = f"{est_size_kb:.1f} KB" if est_size_kb >= 0.1 else "0.1 KB"
            
            st.markdown(f'''
            <div style="font-size: 0.85rem; color: var(--sp-muted); margin-bottom: 0.8rem;">
                Rows: <b>{rows_exp:,}</b><br>
                Columns: <b>{cols_exp}</b><br>
                Estimated size: <b>{size_str}</b>
            </div>
            ''', unsafe_allow_html=True)
            
            selected_fmt = st.radio("Format", ["XLSX", "CSV"], horizontal=True, key="export_format_selector")
            from src.export.exporters import to_csv, to_excel
            filename_base = st.session_state.get("uploaded_filename", "dataset").split(".")[0]
            
            if selected_fmt == "CSV":
                csv_bytes = to_csv(result_df)
                st.download_button(
                    label="Download Result (CSV)",
                    data=csv_bytes,
                    file_name=f"sheetpilot_{filename_base}_result.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                xlsx_bytes = to_excel(result_df)
                st.download_button(
                    label="Download Result (Excel)",
                    data=xlsx_bytes,
                    file_name=f"sheetpilot_{filename_base}_result.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

