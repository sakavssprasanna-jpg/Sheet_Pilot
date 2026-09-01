import logging
import time
import pandas as pd
from typing import Optional, List, Dict, Any
from src.config import get_gemini_api_key, IS_GEMINI_AVAILABLE, GEMINI_MODEL
from src.ai.schemas import AIResponse, StructuredOperation

# Try importing google.genai safely
try:
    from google import genai
    from google.genai import types
    GENAI_INSTALLED = True
except ImportError:
    GENAI_INSTALLED = False

logger = logging.getLogger(__name__)

def get_gemini_client() -> Optional[object]:
    """
    Initialize and return the official Gemini API Client from google-genai.
    Returns None if the SDK is not installed or the API key is not available.
    """
    if not GENAI_INSTALLED:
        logger.warning("google-genai is not installed. Gemini Client is unavailable.")
        return None
        
    api_key = get_gemini_api_key()
    if not api_key:
        logger.warning("Gemini API key is missing. Gemini Client is unavailable.")
        return None
        
    try:
        # Initialize the official SDK Client
        return genai.Client(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to initialize Gemini Client: {e}")
        return None

def verify_connection(client: Optional[object]) -> bool:
    """
    Verify that the Gemini API client is authenticated and responsive.
    Attempts a minimal test call (generating content) to check availability.
    """
    if client is None or not GENAI_INSTALLED:
        return False
        
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents='Ping. Reply with Pong.',
        )
        return "pong" in response.text.lower()
    except Exception as e:
        logger.error(f"Gemini API connection verification failed: {e}")
        return False

def build_relevance_context(df: pd.DataFrame, query: str) -> Dict[str, Any]:
    """
    Builds a dynamic, relevance-aware context description of the dataset.
    Prioritizes columns referenced in the query, including stats and sample values,
    and returns a clean, structured representation.
    """
    if df is None:
        return {
            "total_rows": 0,
            "total_cols": 0,
            "column_details_str": "No active dataset.",
            "sample_rows_str": "No active dataset.",
            "numeric_columns": [],
            "categorical_columns": []
        }

    total_rows, total_cols = df.shape
    columns = list(df.columns)
    query_lower = query.lower() if query else ""

    # Relevance filtering: find columns explicitly or implicitly mentioned in the query
    relevant_cols = []
    for col in columns:
        col_str = str(col)
        # Check if column name or parts of it are in the query
        if col_str.lower() in query_lower or any(word in query_lower for word in col_str.lower().split()):
            relevant_cols.append(col)

    # Fallback to all columns if none detected or query is empty
    if not relevant_cols:
        relevant_cols = columns

    # Build column details
    col_details = []
    numeric_cols = []
    categorical_cols = []

    for col in columns:
        dtype = str(df[col].dtype)
        is_num = pd.api.types.is_numeric_dtype(df[col]) and not "bool" in dtype
        if is_num:
            numeric_cols.append(col)
        else:
            categorical_cols.append(col)

        # Only build deep details for relevant columns to optimize context size
        if col in relevant_cols:
            missing = int(df[col].isnull().sum())
            nunique = int(df[col].nunique())
            if is_num:
                min_val = df[col].min()
                max_val = df[col].max()
                mean_val = df[col].mean()
                mean_str = f"{mean_val:.2f}" if pd.notnull(mean_val) else "N/A"
                detail = f"- {col} ({dtype}): {nunique} distinct values, {missing} missing. Range: [{min_val}, {max_val}], Mean: {mean_str} (RELEVANT)"
            else:
                sample_vals = list(df[col].dropna().unique()[:3])
                detail = f"- {col} ({dtype}): {nunique} distinct values, {missing} missing. Sample: {sample_vals} (RELEVANT)"
        else:
            detail = f"- {col} ({dtype}) (Available)"
        col_details.append(detail)

    column_details_str = "\n".join(col_details)

    # Sample rows (only keep relevant columns if too large, or select columns)
    sample_df = df[relevant_cols].head(5)
    sample_rows_str = sample_df.to_string(index=False)

    return {
        "total_rows": total_rows,
        "total_cols": total_cols,
        "column_details_str": column_details_str,
        "sample_rows_str": sample_rows_str,
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols
    }

def sanitize_gemini_schema(schema_input: Any) -> Dict[str, Any]:
    """
    Recursively sanitize a schema dictionary or Pydantic model to remove
    unsupported Gemini Developer API properties like 'additionalProperties'
    and 'additional_properties'.
    """
    import copy
    from pydantic import BaseModel
    
    # 1. Extract raw dictionary if it is a Pydantic model class
    if isinstance(schema_input, type) and issubclass(schema_input, BaseModel):
        schema_dict = schema_input.model_json_schema()
    elif hasattr(schema_input, "model_json_schema"):
        schema_dict = schema_input.model_json_schema()
    elif isinstance(schema_input, dict):
        schema_dict = schema_input
    else:
        # Fallback for unexpected types
        return schema_input

    # 2. Recursively clean the schema copy
    cleaned = copy.deepcopy(schema_dict)

    def _clean(node: Any) -> Any:
        if isinstance(node, dict):
            # Strip invalid keys
            node.pop("additionalProperties", None)
            node.pop("additional_properties", None)
            # Recurse
            for k, v in list(node.items()):
                node[k] = _clean(v)
        elif isinstance(node, list):
            node = [_clean(item) for item in node]
        return node

    return _clean(cleaned)

def query_gemini_intelligence(query: str, history: List[Dict[str, Any]] = None) -> AIResponse:
    """
    Query the Gemini API to translate a user's voice/text command into a structured operation plan.
    Incorporates dynamic relevance-aware context, conversational history, and error fallbacks.
    Updates the session state metrics for observability.
    """
    from src.state import SessionStateManager
    
    start_time = time.time()
    SessionStateManager.set_ai_request_status("Preparing context")
    SessionStateManager.increment_ai_requests()
    SessionStateManager.set_last_ai_timestamp(pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    client = get_gemini_client()
    if client is None:
        duration = time.time() - start_time
        SessionStateManager.set_last_ai_duration(duration)
        SessionStateManager.set_ai_request_status("Failed (No Client)")
        return AIResponse(
            status="ai_error",
            error="Gemini Client is unavailable. Please configure GEMINI_API_KEY in secrets or environment.",
            explanation="AI engine is not connected.",
            language="English"
        )
        
    df = SessionStateManager.get_current_df()
    if df is None:
        duration = time.time() - start_time
        SessionStateManager.set_last_ai_duration(duration)
        SessionStateManager.set_ai_request_status("Failed (No Dataset)")
        return AIResponse(
            status="validation_error",
            error="No active dataset loaded in workspace.",
            explanation="Dataset missing.",
            language="English"
        )

    # 1. Build Relevance-Aware Context
    ctx = build_relevance_context(df, query)
    
    # 2. Format Bounded Conversational History
    history_lines = []
    if history:
        # Bounded history to last 5 entries to prevent token bloat
        for h in history[-5:]:
            history_lines.append(f"Command: {h.get('query', '')} -> Status: {'Success' if h.get('success') else 'Failed'}")
    history_str = "\n".join(history_lines) if history_lines else "No previous commands in session."

    # 3. Assemble Prompt
    from src.ai.prompts import SYSTEM_INSTRUCTION, INTENT_EXTRACTION_PROMPT_TEMPLATE
    
    # Check if voice language is detected in state
    voice_lang = SessionStateManager.get_detected_language()
    
    prompt = INTENT_EXTRACTION_PROMPT_TEMPLATE.format(
        total_rows=ctx["total_rows"],
        total_cols=ctx["total_cols"],
        column_details_str=ctx["column_details_str"],
        sample_rows_str=ctx["sample_rows_str"],
        history_str=history_str,
        user_query=query,
        voice_language=voice_lang
    )

    SessionStateManager.set_ai_request_status("Sending request")
    
    sanitized_schema = sanitize_gemini_schema(AIResponse)
    
    # Safe debug logging for verification (only metadata, no API keys or sensitive data)
    logger.debug(f"Gemini Request Config - Model: {GEMINI_MODEL}")
    logger.debug(f"Gemini Request Config - MIME Type: application/json")
    logger.debug(f"Gemini Request Config - Schema Type: {type(sanitized_schema)}")
    if isinstance(sanitized_schema, dict):
        logger.debug(f"Gemini Request Config - Schema Keys: {list(sanitized_schema.keys())}")
        has_add_prop = "additionalProperties" in str(sanitized_schema) or "additional_properties" in str(sanitized_schema)
        logger.debug(f"Gemini Request Config - Contains additionalProperties: {has_add_prop}")

    try:
        # Query with schema enforcement
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=sanitized_schema
            )
        )
        
        # Parse the typed response
        import json
        resp_dict = json.loads(response.text)
        ai_resp = AIResponse.model_validate(resp_dict)
        
        duration = time.time() - start_time
        SessionStateManager.set_last_ai_duration(duration)
        SessionStateManager.set_ai_request_status("Success")
        return ai_resp
        
    except Exception as e:
        logger.exception("Gemini execution failed")
        duration = time.time() - start_time
        SessionStateManager.set_last_ai_duration(duration)
        SessionStateManager.set_ai_request_status(f"Failed ({type(e).__name__})")
        return AIResponse(
            status="ai_error",
            error=f"Gemini API request failed: {str(e)}",
            explanation="AI analysis failed due to system exception.",
            language="English"
        )

