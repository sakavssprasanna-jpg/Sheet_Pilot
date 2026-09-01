import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional

class SessionStateManager:
    # State key names
    UPLOADED_DF = "uploaded_df"
    ORIGINAL_DF = "original_df"
    CURRENT_DF = "current_df"
    METADATA = "metadata"
    CURRENT_LANGUAGE = "current_language"
    HISTORY = "history"
    OPERATIONS = "operations"
    RESULTS = "results"
    SELECTED_VIZ = "selected_viz"
    PREFERENCES = "preferences"
    ERRORS = "errors"
    APPLIED_OPS = "applied_ops"
    
    # Phase 6 execution & visualization keys
    RESULT_DF = "result_df"
    RESULT_METADATA = "result_metadata"
    CHART_CONFIG = "chart_config"
    CHART_HISTORY = "chart_history"
    EXPORT_FORMAT = "export_format"
    UNSAVED_CHANGES = "unsaved_changes"
    CURRENT_OPERATION = "current_operation"
    EXECUTION_STATUS = "execution_status"
    
    # Voice state keys
    LAST_AUDIO = "last_audio"
    LAST_TRANSCRIPT = "last_transcript"
    DETECTED_LANGUAGE = "detected_language"
    VOICE_STATUS = "voice_status"
    VOICE_ERROR = "voice_error"
    TRANSCRIPT_HISTORY = "transcript_history"
    
    # AI request tracking keys
    AI_REQUEST_COUNT = "ai_request_count"
    LAST_AI_REQUEST_TIMESTAMP = "last_ai_request_timestamp"
    LAST_AI_REQUEST_DURATION = "last_ai_request_duration"
    AI_REQUEST_STATUS = "ai_request_status"

    @classmethod
    def init_state(cls):
        """Initialize all session state keys with default values if they do not exist."""
        defaults = {
            cls.UPLOADED_DF: None,
            cls.ORIGINAL_DF: None,
            cls.CURRENT_DF: None,
            cls.METADATA: {},
            cls.CURRENT_LANGUAGE: "en",
            cls.HISTORY: [],
            cls.OPERATIONS: [],
            cls.RESULTS: None,
            cls.SELECTED_VIZ: None,
            cls.PREFERENCES: {
                "theme": "dark",
                "max_rows_display": 100,
                "precision": 2
            },
            cls.ERRORS: [],
            cls.APPLIED_OPS: [],
            cls.LAST_AUDIO: None,
            cls.LAST_TRANSCRIPT: "",
            cls.DETECTED_LANGUAGE: "Unknown",
            cls.VOICE_STATUS: "idle",
            cls.VOICE_ERROR: None,
            cls.TRANSCRIPT_HISTORY: [],
            
            # AI tracking defaults
            cls.AI_REQUEST_COUNT: 0,
            cls.LAST_AI_REQUEST_TIMESTAMP: None,
            cls.LAST_AI_REQUEST_DURATION: 0.0,
            cls.AI_REQUEST_STATUS: "Idle",
            
            # Phase 6 defaults
            cls.RESULT_DF: None,
            cls.RESULT_METADATA: {},
            cls.CHART_CONFIG: None,
            cls.CHART_HISTORY: [],
            cls.EXPORT_FORMAT: "XLSX",
            cls.UNSAVED_CHANGES: False,
            cls.CURRENT_OPERATION: None,
            cls.EXECUTION_STATUS: "idle"
        }
        for key, default in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default

    @classmethod
    def reset_data_state(cls):
        """Reset only data-related session state keys (e.g. when uploading a new file)."""
        st.session_state[cls.UPLOADED_DF] = None
        st.session_state[cls.ORIGINAL_DF] = None
        st.session_state[cls.CURRENT_DF] = None
        st.session_state[cls.METADATA] = {}
        st.session_state[cls.OPERATIONS] = []
        st.session_state[cls.RESULTS] = None
        st.session_state[cls.SELECTED_VIZ] = None
        st.session_state[cls.ERRORS] = []
        st.session_state[cls.APPLIED_OPS] = []
        st.session_state[cls.HISTORY] = []
        
        # Reset voice state
        st.session_state[cls.LAST_AUDIO] = None
        st.session_state[cls.LAST_TRANSCRIPT] = ""
        st.session_state[cls.DETECTED_LANGUAGE] = "Unknown"
        st.session_state[cls.VOICE_STATUS] = "idle"
        st.session_state[cls.VOICE_ERROR] = None
        st.session_state[cls.TRANSCRIPT_HISTORY] = []
        
        # Reset pending AI response
        if "pending_ai_response" in st.session_state:
            st.session_state["pending_ai_response"] = None
            
        # Reset Phase 6 state keys
        st.session_state[cls.RESULT_DF] = None
        st.session_state[cls.RESULT_METADATA] = {}
        st.session_state[cls.CHART_CONFIG] = None
        st.session_state[cls.CHART_HISTORY] = []
        st.session_state[cls.EXPORT_FORMAT] = "XLSX"
        st.session_state[cls.UNSAVED_CHANGES] = False
        st.session_state[cls.CURRENT_OPERATION] = None
        st.session_state[cls.EXECUTION_STATUS] = "idle"

    # Voice Getters and Setters
    @classmethod
    def get_last_audio(cls) -> Optional[bytes]:
        return st.session_state.get(cls.LAST_AUDIO)

    @classmethod
    def set_last_audio(cls, audio_bytes: Optional[bytes]):
        st.session_state[cls.LAST_AUDIO] = audio_bytes

    @classmethod
    def get_last_transcript(cls) -> str:
        return st.session_state.get(cls.LAST_TRANSCRIPT, "")

    @classmethod
    def set_last_transcript(cls, transcript: str):
        st.session_state[cls.LAST_TRANSCRIPT] = transcript

    @classmethod
    def get_detected_language(cls) -> str:
        return st.session_state.get(cls.DETECTED_LANGUAGE, "Unknown")

    @classmethod
    def set_detected_language(cls, language: str):
        st.session_state[cls.DETECTED_LANGUAGE] = language

    @classmethod
    def get_voice_status(cls) -> str:
        return st.session_state.get(cls.VOICE_STATUS, "idle")

    @classmethod
    def set_voice_status(cls, status: str):
        st.session_state[cls.VOICE_STATUS] = status

    @classmethod
    def get_voice_error(cls) -> Optional[str]:
        return st.session_state.get(cls.VOICE_ERROR)

    @classmethod
    def set_voice_error(cls, error_msg: Optional[str]):
        st.session_state[cls.VOICE_ERROR] = error_msg

    @classmethod
    def get_transcript_history(cls) -> List[Dict[str, Any]]:
        return st.session_state.get(cls.TRANSCRIPT_HISTORY, [])

    @classmethod
    def add_to_transcript_history(cls, entry: Dict[str, Any]):
        st.session_state[cls.TRANSCRIPT_HISTORY].append(entry)
        # Prevent unbounded memory growth by limiting history length
        if len(st.session_state[cls.TRANSCRIPT_HISTORY]) > 100:
            st.session_state[cls.TRANSCRIPT_HISTORY].pop(0)

    @classmethod
    def get_ai_request_count(cls) -> int:
        return st.session_state.get(cls.AI_REQUEST_COUNT, 0)

    @classmethod
    def increment_ai_requests(cls):
        st.session_state[cls.AI_REQUEST_COUNT] = st.session_state.get(cls.AI_REQUEST_COUNT, 0) + 1

    @classmethod
    def get_last_ai_timestamp(cls) -> Optional[str]:
        return st.session_state.get(cls.LAST_AI_REQUEST_TIMESTAMP)

    @classmethod
    def set_last_ai_timestamp(cls, ts: str):
        st.session_state[cls.LAST_AI_REQUEST_TIMESTAMP] = ts

    @classmethod
    def get_last_ai_duration(cls) -> float:
        return st.session_state.get(cls.LAST_AI_REQUEST_DURATION, 0.0)

    @classmethod
    def set_last_ai_duration(cls, duration: float):
        st.session_state[cls.LAST_AI_REQUEST_DURATION] = duration

    @classmethod
    def get_ai_request_status(cls) -> str:
        return st.session_state.get(cls.AI_REQUEST_STATUS, "Idle")

    @classmethod
    def set_ai_request_status(cls, status: str):
        st.session_state[cls.AI_REQUEST_STATUS] = status

    # Getters and setters
    @classmethod
    def get_uploaded_df(cls) -> Optional[pd.DataFrame]:
        return st.session_state.get(cls.UPLOADED_DF)

    @classmethod
    def set_uploaded_df(cls, df: Optional[pd.DataFrame]):
        st.session_state[cls.UPLOADED_DF] = df

    @classmethod
    def get_original_df(cls) -> Optional[pd.DataFrame]:
        return st.session_state.get(cls.ORIGINAL_DF)

    @classmethod
    def set_original_df(cls, df: Optional[pd.DataFrame]):
        st.session_state[cls.ORIGINAL_DF] = df

    @classmethod
    def get_current_df(cls) -> Optional[pd.DataFrame]:
        return st.session_state.get(cls.CURRENT_DF)

    @classmethod
    def set_current_df(cls, df: Optional[pd.DataFrame]):
        st.session_state[cls.CURRENT_DF] = df

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        return st.session_state.get(cls.METADATA, {})

    @classmethod
    def set_metadata(cls, metadata: Dict[str, Any]):
        st.session_state[cls.METADATA] = metadata

    @classmethod
    def get_current_language(cls) -> str:
        return st.session_state.get(cls.CURRENT_LANGUAGE, "en")

    @classmethod
    def set_current_language(cls, lang: str):
        st.session_state[cls.CURRENT_LANGUAGE] = lang

    @classmethod
    def get_history(cls) -> List[Dict[str, Any]]:
        return st.session_state.get(cls.HISTORY, [])

    @classmethod
    def add_to_history(cls, query: str, response: Optional[str] = None, success: bool = True, language: str = "English", response_obj: Optional[Any] = None):
        st.session_state[cls.HISTORY].append({
            "timestamp": pd.Timestamp.now().isoformat(),
            "query": query,
            "response": response,
            "success": success,
            "language": language,
            "response_obj": response_obj
        })

    @classmethod
    def get_operations(cls) -> List[Dict[str, Any]]:
        return st.session_state.get(cls.OPERATIONS, [])

    @classmethod
    def add_operation(cls, operation: Dict[str, Any]):
        st.session_state[cls.OPERATIONS].append(operation)

    @classmethod
    def get_results(cls) -> Any:
        return st.session_state.get(cls.RESULTS)

    @classmethod
    def set_results(cls, results: Any):
        st.session_state[cls.RESULTS] = results

    @classmethod
    def get_selected_viz(cls) -> Optional[Dict[str, Any]]:
        return st.session_state.get(cls.SELECTED_VIZ)

    @classmethod
    def set_selected_viz(cls, viz: Optional[Dict[str, Any]]):
        st.session_state[cls.SELECTED_VIZ] = viz

    @classmethod
    def get_preferences(cls) -> Dict[str, Any]:
        return st.session_state.get(cls.PREFERENCES, {})

    @classmethod
    def update_preferences(cls, updates: Dict[str, Any]):
        st.session_state[cls.PREFERENCES].update(updates)

    @classmethod
    def get_errors(cls) -> List[str]:
        return st.session_state.get(cls.ERRORS, [])

    @classmethod
    def add_error(cls, error_msg: str):
        st.session_state[cls.ERRORS].append(error_msg)

    @classmethod
    def clear_errors(cls):
        st.session_state[cls.ERRORS] = []

    @classmethod
    def get_applied_ops(cls) -> List[Any]:
        return st.session_state.get(cls.APPLIED_OPS, [])

    @classmethod
    def add_applied_op(cls, op: Any):
        st.session_state[cls.APPLIED_OPS].append(op)

    @classmethod
    def reset_dataset(cls):
        """Restore dataset to its original unmodified form and clear history list."""
        orig = cls.get_original_df()
        if orig is not None:
            cls.set_current_df(orig.copy())
            st.session_state[cls.APPLIED_OPS] = []
            
            # Re-profile original
            from src.data.profiler import profile_dataframe
            cls.set_metadata(profile_dataframe(orig))

    @classmethod
    def undo_last_operation(cls):
        """Pop the last structured operation and replay the remaining ones to conserve memory."""
        ops = st.session_state.get(cls.APPLIED_OPS, [])
        orig = cls.get_original_df()
        
        if not ops or orig is None:
            return
            
        # Pop the last operation
        ops.pop()
        
        # Replay operations on a fresh copy of original dataset
        temp_df = orig.copy()
        from src.execution.operation_engine import execute_operation
        
        for op in ops:
            res = execute_operation(op, temp_df)
            if res.success and res.result_dataframe is not None:
                temp_df = res.result_dataframe
                
        cls.set_current_df(temp_df)
        
        # Update profile metadata
        from src.data.profiler import profile_dataframe
        cls.set_metadata(profile_dataframe(temp_df))

    # Phase 6 getters/setters
    @classmethod
    def get_result_df(cls) -> Optional[pd.DataFrame]:
        return st.session_state.get(cls.RESULT_DF)

    @classmethod
    def set_result_df(cls, df: Optional[pd.DataFrame]):
        st.session_state[cls.RESULT_DF] = df

    @classmethod
    def get_result_metadata(cls) -> Dict[str, Any]:
        return st.session_state.get(cls.RESULT_METADATA, {})

    @classmethod
    def set_result_metadata(cls, meta: Dict[str, Any]):
        st.session_state[cls.RESULT_METADATA] = meta

    @classmethod
    def get_chart_config(cls) -> Optional[Any]:
        return st.session_state.get(cls.CHART_CONFIG)

    @classmethod
    def set_chart_config(cls, config: Optional[Any]):
        st.session_state[cls.CHART_CONFIG] = config

    @classmethod
    def get_chart_history(cls) -> List[Any]:
        return st.session_state.get(cls.CHART_HISTORY, [])

    @classmethod
    def add_chart_to_history(cls, config: Any):
        if cls.CHART_HISTORY not in st.session_state:
            st.session_state[cls.CHART_HISTORY] = []
        st.session_state[cls.CHART_HISTORY].append(config)

    @classmethod
    def get_export_format(cls) -> str:
        return st.session_state.get(cls.EXPORT_FORMAT, "XLSX")

    @classmethod
    def set_export_format(cls, fmt: str):
        st.session_state[cls.EXPORT_FORMAT] = fmt

    @classmethod
    def get_unsaved_changes(cls) -> bool:
        return st.session_state.get(cls.UNSAVED_CHANGES, False)

    @classmethod
    def set_unsaved_changes(cls, val: bool):
        st.session_state[cls.UNSAVED_CHANGES] = val

    @classmethod
    def get_current_operation(cls) -> Optional[Any]:
        return st.session_state.get(cls.CURRENT_OPERATION)

    @classmethod
    def set_current_operation(cls, op: Optional[Any]):
        st.session_state[cls.CURRENT_OPERATION] = op

    @classmethod
    def get_execution_status(cls) -> str:
        return st.session_state.get(cls.EXECUTION_STATUS, "idle")

    @classmethod
    def set_execution_status(cls, status: str):
        st.session_state[cls.EXECUTION_STATUS] = status
