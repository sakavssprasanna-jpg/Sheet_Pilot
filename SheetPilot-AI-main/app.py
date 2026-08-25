import streamlit as st
import pandas as pd
from src.state import SessionStateManager
from src.data.loader import load_file
from src.data.validator import validate_dataframe
from src.data.profiler import profile_dataframe
from src.ui import (
    inject_custom_theme,
    render_sidebar,
    render_hero,
    render_upload_card,
    render_upload_success,
    render_kpi_cards,
    render_empty_state,
    render_ai_command_preview,
    render_workspace_header
)

# Set page config for a premium wide dashboard appearance
st.set_page_config(
    page_title="SheetPilot AI — Spreadsheet Automation Copilot",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 1. Initialize custom design theme and load fonts
inject_custom_theme()

# 2. Initialize Centralized Session State
SessionStateManager.init_state()

# 3. Render Navigation Sidebar Layout
render_sidebar()

# Load sample dataset if requested by landing page actions
uploaded_file = None
if st.session_state.get("load_sample_trigger", False):
    import os
    from io import BytesIO
    if os.path.exists("sample_employees.csv"):
        with open("sample_employees.csv", "rb") as f:
            uploaded_file = BytesIO(f.read())
            uploaded_file.name = "sample_employees.csv"
        st.session_state.load_sample_trigger = False

# Get data elements from state
current_df = SessionStateManager.get_current_df()
metadata = SessionStateManager.get_metadata()

# 5. File Upload Handler
# If no dataset is active, show the onboarding/uploader card
if current_df is None and uploaded_file is None:
    uploaded_file = st.session_state.get("main_file_uploader")
elif current_df is not None:
    # 4. Render Main Dashboard Header
    render_hero()
    
    # Back to Home navigation button
    col_back, _ = st.columns([2.5, 9.5])
    with col_back:
        if st.button("← Back to Home", key="btn_back_to_home", use_container_width=True):
            # Clean dataset and app state
            SessionStateManager.reset_data_state()
            
            # Safely clear streamlit's internal widget key cache/values to prevent reloading
            keys_to_clear = [
                "main_file_uploader",
                "uploaded_filename",
                "autoload_done",
                "user_query_input_val",
                "show_voice_panel",
                "user_query_input",
                "playground_select",
                "voice_lang_selector",
                "audio_recorder",
                "transcript_editor_text",
                "clarification_input_val",
                "data_tab_search_input",
                "analytics_tab_chart_type",
                "analytics_tab_x",
                "analytics_tab_y",
                "analytics_tab_color",
                "col_tab_select",
                "history_tab_select"
            ]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            
            st.rerun()



# Handle file validation and loading when a file is selected
if uploaded_file is not None:
    current_name = uploaded_file.name
    # Check if this is a newly uploaded file
    if "uploaded_filename" not in st.session_state or st.session_state.uploaded_filename != current_name:
        SessionStateManager.reset_data_state()
        st.session_state.uploaded_filename = current_name
        
        # Load the file bytes
        df, load_err = load_file(uploaded_file, current_name)
        if load_err:
            SessionStateManager.add_error(load_err)
            st.error(load_err)
        else:
            # Validate structural integrity
            is_valid, errors, warnings = validate_dataframe(df)
            if not is_valid:
                for err in errors:
                    SessionStateManager.add_error(err)
                st.error("Dataset contains critical structure errors and cannot be loaded:\n" + "\n".join(errors))
            else:
                # Save data objects to centralized state
                SessionStateManager.set_uploaded_df(df)
                SessionStateManager.set_original_df(df)
                SessionStateManager.set_current_df(df)
                
                # Profile dataset statistics
                profile = profile_dataframe(df)
                SessionStateManager.set_metadata(profile)
                
                # Store warnings
                for warn in warnings:
                    SessionStateManager.add_error(f"Warning: {warn}")
                
                # Mark autoload done so replacing doesn't trigger it again
                st.session_state.autoload_done = True
                
                # Trigger a quick rerun to immediately update layout elements
                st.rerun()

if current_df is not None and metadata:
    # Render persistent dataset header
    orig_df = SessionStateManager.get_original_df()
    is_modified = not current_df.equals(orig_df)
    state_desc = "Modified Dataset" if is_modified else "Original Dataset"
    
    render_workspace_header(
        filename=st.session_state.get("uploaded_filename", "dataset.csv"),
        rows=current_df.shape[0],
        cols=current_df.shape[1],
        quality_score=metadata.get("data_quality_score", 100.0),
        state_desc=state_desc,
        quality_breakdown=metadata.get("data_quality_breakdown", {})
    )
    
    st.markdown("---")
    
    # 6. Applied Modifications Toolbar
    applied_ops = SessionStateManager.get_applied_ops()
    if applied_ops:
        col_op1, col_op2, col_op3 = st.columns([4, 1.2, 1])
        with col_op1:
            st.markdown(f"""
            <div style="font-size: 0.95rem; color: var(--sp-accent); padding-top: 0.4rem; font-weight: 600;">
                ⚡ Applied transformations: {len(applied_ops)}
            </div>
            """, unsafe_allow_html=True)
        with col_op2:
            if st.button("Undo Last Operation", key="undo_op_btn", use_container_width=True):
                SessionStateManager.undo_last_operation()
                st.rerun()
        with col_op3:
            if st.button("Reset Dataset", key="reset_op_btn", use_container_width=True):
                SessionStateManager.reset_dataset()
                st.rerun()
                
    # 7. Navigation Tabs
    tab_ask, tab_data, tab_column, tab_analytics, tab_history = st.tabs([
        "💬 Ask SheetPilot",
        "🗂️ Data Grid",
        "🔎 Column Explorer",
        "📊 Analytics Dashboard",
        "⏳ Operation History"
    ])
    
    with tab_ask:
        # Render Copilot (Text, Voice, Exec, Results, Export)
        render_ai_command_preview()
        
        # Developer Playground Expandable inside Ask tab
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🛠️ Developer Intelligence Engine Tester"):
            st.markdown("<p style='font-size: 0.85rem; color: var(--sp-muted); margin-bottom: 1rem;'>Execute the backend test cases covering filters, sort, limit, group aggregates, math transformations, type safety, invalid parameters, and undo states.</p>", unsafe_allow_html=True)
            
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.markdown("##### 🧪 Operations Sandbox")
                st.markdown("<p style='font-size: 0.82rem; color: var(--sp-muted); margin-bottom: 0.8rem;'>Select a structured operation schema to execute on the active dataset:</p>", unsafe_allow_html=True)
                
                ops_options = [
                    "Select operation...",
                    "Filter: Salary > 80000",
                    "Sort: Salary descending",
                    "Limit: Top 3 rows",
                    "Group By: Department -> Mean Salary",
                    "Math: Increment Salary by 10%"
                ]
                
                # Map values to columns in actual dataset if they don't match standard Employees CSV headers
                has_sales_cols = "Salary" in current_df.columns and "Department" in current_df.columns
                if not has_sales_cols:
                    st.warning("⚠️ Operations Playground options require columns 'Salary' and 'Department' to execute correctly.")
                    
                selected_playground_op = st.selectbox("Predefined Operations:", ops_options, key="playground_select", disabled=not has_sales_cols)
                
                if selected_playground_op != "Select operation..." and has_sales_cols:
                    from src.ai.schemas import FilterCondition, SortCondition, AggregateOperation, ColumnTransformation, StructuredOperation
                    
                    op_obj = None
                    if selected_playground_op == "Filter: Salary > 80000":
                        op_obj = StructuredOperation(
                            intent="filter_sort",
                            filters=[FilterCondition(column="Salary", operator=">", value=80000)],
                            explanation="Filter dataset to keep only rows where Salary is greater than 80000"
                        )
                    elif selected_playground_op == "Sort: Salary descending":
                        op_obj = StructuredOperation(
                            intent="filter_sort",
                            sort=[SortCondition(column="Salary", ascending=False)],
                            explanation="Sort dataset rows by Salary in descending order"
                        )
                    elif selected_playground_op == "Limit: Top 3 rows":
                        op_obj = StructuredOperation(
                            intent="filter_sort",
                            limit=3,
                            explanation="Keep only the top 3 rows of the dataset"
                        )
                    elif selected_playground_op == "Group By: Department -> Mean Salary":
                        op_obj = StructuredOperation(
                            intent="aggregate",
                            group_by=["Department"],
                            aggregations=[AggregateOperation(column="Salary", func="mean", alias="Average_Salary")],
                            explanation="Group rows by Department and calculate the average Salary per department"
                        )
                    elif selected_playground_op == "Math: Increment Salary by 10%":
                        op_obj = StructuredOperation(
                            intent="transformation",
                            transformations=[ColumnTransformation(
                                column="Salary",
                                new_column="New_Salary",
                                operation="math",
                                args={"operator": "*", "operand": 1.1}
                            )],
                            explanation="Multiply Salary column by 1.1 to calculate New_Salary"
                        )
                        
                    if op_obj:
                        st.markdown("<p style='font-size: 0.8rem; font-weight: 600; color: #FFFFFF;'>Operation JSON Payload:</p>", unsafe_allow_html=True)
                        st.json(op_obj.dict())
                        if st.button("Apply Operation", key="apply_playground_op", use_container_width=True):
                            from src.execution.operation_engine import execute_operation
                            res = execute_operation(op_obj, current_df)
                            if res.success and res.result_dataframe is not None:
                                SessionStateManager.set_current_df(res.result_dataframe)
                                SessionStateManager.add_applied_op(op_obj)
                                from src.data.profiler import profile_dataframe
                                SessionStateManager.set_metadata(profile_dataframe(res.result_dataframe))
                                st.success("✓ Operation executed successfully!")
                                st.rerun()
                            else:
                                st.error(f"Execution failed: {res.operation_summary}")
                                
            with col_t2:
                st.markdown("##### ⚙️ Automated Test Runner")
                st.markdown("<p style='font-size: 0.82rem; color: var(--sp-muted); margin-bottom: 0.8rem;'>Run the unittest suite verifying edge cases, syntax error guards, and undo limits.</p>", unsafe_allow_html=True)
                
                if st.button("Run Engine Unit Tests", key="run_engine_tests_btn", use_container_width=True):
                    import unittest
                    from tests.test_engine import TestDataIntelligenceEngine
                    import io
                    
                    suite = unittest.TestLoader().loadTestsFromTestCase(TestDataIntelligenceEngine)
                    stream = io.StringIO()
                    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
                    result = runner.run(suite)
                    
                    output_log = stream.getvalue()
                    st.code(output_log, language="text")
                    
                    if result.wasSuccessful():
                        st.success(f"✓ All {result.testsRun} test cases compiled and passed successfully!")
                    else:
                        st.error(f"❌ Failed: {len(result.failures)} failures, {len(result.errors)} errors")
                
                st.markdown("---")
                st.markdown("##### 🎙️ Voice Mock Tester")
                st.markdown("<p style='font-size: 0.82rem; color: var(--sp-muted); margin-bottom: 0.8rem;'>Mock speech-to-text inputs to verify multilingual voice workflow:</p>", unsafe_allow_html=True)
                
                col_vm1, col_vm2, col_vm3 = st.columns(3)
                with col_vm1:
                    if st.button("English Voice", key="mock_voice_en", use_container_width=True):
                        SessionStateManager.set_voice_status("success")
                        SessionStateManager.set_last_transcript("Show the top 10 records by revenue.")
                        SessionStateManager.set_detected_language("English")
                        st.session_state.show_voice_panel = True
                        st.rerun()
                with col_vm2:
                    if st.button("Telugu Voice", key="mock_voice_te", use_container_width=True):
                        SessionStateManager.set_voice_status("success")
                        SessionStateManager.set_last_transcript("South region lo highest profit vachina top 5 records chupinchu.")
                        SessionStateManager.set_detected_language("Telugu")
                        st.session_state.show_voice_panel = True
                        st.rerun()
                with col_vm3:
                    if st.button("Hindi Voice", key="mock_voice_hi", use_container_width=True):
                        SessionStateManager.set_voice_status("success")
                        SessionStateManager.set_last_transcript("राजस्व के आधार पर शीर्ष 10 रिकॉर्ड दिखाओ।")
                        SessionStateManager.set_detected_language("Hindi")
                        st.session_state.show_voice_panel = True
                        st.rerun()
                        
    with tab_data:
        st.subheader("🗂️ Interactive Data Grid")
        st.markdown("Directly edit cell values in the table below. Use search to filter rows.")
        
        # Display dirty warning
        is_dirty = st.session_state.get("unsaved_changes", False)
        if is_dirty:
            st.warning("⚠️ Warning: You have unapplied cell edits. Click 'Save Cell Edits' below to persist changes to the active session dataframe.")
            
        col_ed_btn1, col_ed_btn2 = st.columns([1.5, 6.5])
        with col_ed_btn1:
            save_clicked = st.button("💾 Save Cell Edits", key="data_tab_save_btn", type="primary", use_container_width=True)
        with col_ed_btn2:
            reset_clicked = st.button("Discard Edits", key="data_tab_discard_btn", use_container_width=True)
            
        col_search, col_info = st.columns([4, 2])
        with col_search:
            search_query = st.text_input(
                "Search grid values...",
                placeholder="Type search terms here (e.g. Sales, Alice)...",
                key="data_tab_search_input"
            )
        with col_info:
            st.markdown(f"""
            <div style="text-align: right; padding-top: 2rem; font-size: 0.85rem; color: var(--sp-muted); font-weight: 500;">
                Showing first 50 rows &bull; {current_df.shape[0]:,} total rows
            </div>
            """, unsafe_allow_html=True)
            
        # Apply simple local search filtering if terms typed
        display_df = current_df
        if search_query:
            mask = display_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
            display_df = display_df[mask]
            
        edited_df = st.data_editor(
            display_df.head(50),
            key="data_tab_editor",
            use_container_width=True,
            num_rows="dynamic"
        )
        
        # Check if edits occurred in the editor
        if edited_df is not None and not edited_df.equals(display_df.head(50)):
            if not is_dirty:
                st.session_state.unsaved_changes = True
                st.rerun()
                
        if save_clicked and edited_df is not None:
            # Merge edited rows back into current_df
            merged_df = current_df.copy()
            if not search_query:
                merged_df.iloc[:len(edited_df)] = edited_df
            else:
                for idx in edited_df.index:
                    if idx in merged_df.index:
                        merged_df.loc[idx] = edited_df.loc[idx]
                        
            SessionStateManager.set_current_df(merged_df)
            SessionStateManager.set_unsaved_changes(False)
            
            # Re-profile
            from src.data.profiler import profile_dataframe
            SessionStateManager.set_metadata(profile_dataframe(merged_df))
            st.success("Cell edits successfully applied and saved!")
            st.rerun()
            
        if reset_clicked:
            st.session_state.unsaved_changes = False
            st.rerun()

        # Export Active Dataset Section
        st.markdown("---")
        col_grid_exp_lbl, col_grid_exp_select, col_grid_exp_btn = st.columns([4.2, 1.8, 2])
        with col_grid_exp_lbl:
            st.markdown("##### 📥 Export Active Dataset")
            st.markdown("<p style='font-size: 0.82rem; color: var(--sp-muted); margin: 0;'>Download the current state of the active dataset with all applied modifications and cell edits.</p>", unsafe_allow_html=True)
        with col_grid_exp_select:
            selected_fmt = st.radio("Export Format:", ["XLSX", "CSV"], horizontal=True, key="grid_export_fmt_selector")
        with col_grid_exp_btn:
            from src.export.exporters import to_csv, to_excel
            filename_base = st.session_state.get("uploaded_filename", "dataset").split(".")[0]
            st.markdown("<div style='padding-top: 0.6rem;'>", unsafe_allow_html=True)
            if selected_fmt == "CSV":
                csv_bytes = to_csv(current_df)
                st.download_button(
                    label="Download CSV",
                    data=csv_bytes,
                    file_name=f"sheetpilot_{filename_base}_export.csv",
                    mime="text/csv",
                    key="grid_export_download_csv_btn",
                    use_container_width=True
                )
            else:
                xlsx_bytes = to_excel(current_df)
                st.download_button(
                    label="Download Excel",
                    data=xlsx_bytes,
                    file_name=f"sheetpilot_{filename_base}_export.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="grid_export_download_xlsx_btn",
                    use_container_width=True
                )
            st.markdown("</div>", unsafe_allow_html=True)
            
    with tab_column:
        st.subheader("🔎 Column Explorer")
        selected_col = st.selectbox("Select a column to inspect metrics:", list(current_df.columns), key="col_tab_select")
        
        # Find column metadata
        col_meta = None
        for col in metadata.get("columns", []):
            if col["name"] == selected_col:
                col_meta = col
                break
                
        if col_meta:
            col_info_1, col_info_2 = st.columns(2)
            with col_info_1:
                st.markdown(f"**Column Name**: `{selected_col}`")
                st.markdown(f"**Pandas Dtype**: `{col_meta['dtype']}`")
                st.markdown(f"**Semantic Type**: `{col_meta['semantic_type'].upper()}`")
            with col_info_2:
                st.markdown(f"**Unique Values**: {col_meta['unique_count']}")
                st.markdown(f"**Missing Values**: {col_meta['null_count']} ({col_meta['null_pct']}%)")
                
            # Render sample values
            st.markdown("**Sample Values**:")
            st.write(", ".join([f"`{val}`" for val in col_meta["samples"]]))
            
            # Numeric stats
            stats_map = metadata.get("stats", {})
            col_stats = stats_map.get(selected_col, {})
            if col_stats:
                st.markdown("---")
                if "mean" in col_stats:
                    st.markdown("**Numerical Summary Statistics**:")
                    s_col1, s_col2, s_col3, s_col4 = st.columns(4)
                    s_col1.metric("Min", f"{col_stats.get('min')}")
                    s_col2.metric("Mean", f"{col_stats.get('mean')}")
                    s_col3.metric("Median", f"{col_stats.get('median')}")
                    s_col4.metric("Max", f"{col_stats.get('max')}")
                else:
                    st.markdown("**Categorical Summary Statistics**:")
                    st.markdown(f"- **Most Frequent Value**: `{col_stats.get('top')}`")
                    st.markdown(f"- **Frequency**: {col_stats.get('freq')} ({col_stats.get('freq_pct')}% of rows)")
        else:
            st.info("No detailed profiling metadata available for this column.")
            
    with tab_analytics:
        st.subheader("📊 Analytics Dashboard")
        st.markdown("Visualize data distributions, trends, and relationships using custom Plotly charts.")
        
        col_viz1, col_viz2 = st.columns([1, 3])
        with col_viz1:
            chart_type = st.selectbox(
                "Chart Type", 
                ["Bar", "Line", "Scatter", "Pie", "Histogram", "Box"],
                key="analytics_tab_chart_type"
            )
            x_col = st.selectbox("X-Axis Column", current_df.columns, key="analytics_tab_x")
            
            y_cols = ["None"] + list(current_df.columns)
            y_col = st.selectbox(
                "Y-Axis Column (Optional)", 
                y_cols, 
                key="analytics_tab_y"
            )
            
            color_col_options = ["None"] + list(current_df.columns)
            color_col = st.selectbox(
                "Color Group (Optional)", 
                color_col_options, 
                key="analytics_tab_color"
            )
            
        with col_viz2:
            # Render Plotly chart based on selected configs
            import plotly.express as px
            y_val = None if y_col == "None" else y_col
            color_val = None if color_col == "None" else color_col
            
            try:
                fig = None
                if chart_type == "Bar":
                    fig = px.bar(current_df, x=x_col, y=y_val, color=color_val, template="plotly_dark")
                elif chart_type == "Line":
                    fig = px.line(current_df, x=x_col, y=y_val, color=color_val, template="plotly_dark")
                elif chart_type == "Scatter":
                    fig = px.scatter(current_df, x=x_col, y=y_val, color=color_val, template="plotly_dark")
                elif chart_type == "Pie":
                    fig = px.pie(current_df, names=x_col, values=y_val, template="plotly_dark")
                elif chart_type == "Histogram":
                    fig = px.histogram(current_df, x=x_col, y=y_val, color=color_val, template="plotly_dark")
                elif chart_type == "Box":
                    fig = px.box(current_df, x=x_col, y=y_val, color=color_val, template="plotly_dark")
                    
                if fig:
                    fig.update_layout(
                        margin=dict(l=20, r=20, t=30, b=20),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color="#FFFFFF")
                    )
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Could not render chart: {e}")
                
    with tab_history:
        st.subheader("⏳ Operation History Timeline")
        history = SessionStateManager.get_history()
        
        if not history:
            st.info("No operations have been run in this session yet.")
        else:
            history_options = []
            for i, item in enumerate(history):
                ts = item.get("timestamp", "")
                if ts:
                    ts = ts[:19].replace("T", " ")
                q = item.get("query", "")
                history_options.append(f"{i+1}. [{ts}] {q[:40]}...")
                
            selected_idx = st.selectbox("Select history item to inspect:", range(len(history)), format_func=lambda i: history_options[i], key="history_tab_select")
            selected_item = history[selected_idx]
            
            st.markdown("---")
            st.markdown(f"##### Query: \"{selected_item.get('query')}\"")
            
            lang = selected_item.get("language", "English")
            st.markdown(f"**Detected Language**: `{lang}`")
            
            success = selected_item.get("success", True)
            if success:
                st.success("✓ Completed successfully")
            else:
                st.error("❌ Execution failed")
                
            resp = selected_item.get("response_obj")
            if resp:
                st.markdown(f"**Explanation**: {resp.explanation}")
                if resp.operation:
                    st.markdown("**Structured Operation Plan:**")
                    st.json(resp.operation.dict())
                    
                    from src.execution import render_pandas_code
                    st.markdown("**Generated Pandas Code:**")
                    st.code(render_pandas_code(resp.operation), language="python")
                    
else:
    # Onboarding Empty State layout
    render_empty_state()
