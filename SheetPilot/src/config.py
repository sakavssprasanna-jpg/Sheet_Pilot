import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()

# Configuration variables
GEMINI_API_KEY = None
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
IS_GEMINI_AVAILABLE = False

# 1. Try to load from Streamlit Secrets (recommended for production)
try:
    if "GEMINI_API_KEY" in st.secrets:
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    # st.secrets raises an exception if not running in Streamlit environment
    pass

# 2. Fall back to Environment Variables (recommended for local development)
if not GEMINI_API_KEY:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY and GEMINI_API_KEY.strip() and GEMINI_API_KEY != "your_gemini_api_key_here":
    IS_GEMINI_AVAILABLE = True

def get_gemini_api_key() -> str:
    """Retrieve the Gemini API key safely, returning an empty string if not set."""
    return GEMINI_API_KEY if GEMINI_API_KEY else ""

def get_app_env() -> str:
    """Retrieve current app environment, defaults to 'development'."""
    return os.getenv("APP_ENV", "development")

def get_log_level() -> str:
    """Retrieve log level, defaults to 'INFO'."""
    return os.getenv("LOG_LEVEL", "INFO")
