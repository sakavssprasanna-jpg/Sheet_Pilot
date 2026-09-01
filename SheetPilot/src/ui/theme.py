import streamlit as st

# Theme variables configuration map for python usage if needed
THEME = {
    "bg": "#080B10",
    "surface": "#0E131F",
    "surface_elevated": "#161D2F",
    "border": "rgba(255, 255, 255, 0.06)",
    "text": "#F3F4F6",
    "text_muted": "#8E9BAE",
    "accent": "#0EA5E9",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444"
}

def inject_custom_theme():
    """Inject premium CSS variables and Vercel/Linear style Dark UI overrides."""
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800;900&display=swap');

    /* CSS Custom Properties Design Tokens */
    :root {{
        --sp-bg: {THEME["bg"]};
        --sp-surface: {THEME["surface"]};
        --sp-surface-elevated: {THEME["surface_elevated"]};
        --sp-border: {THEME["border"]};
        --sp-text: {THEME["text"]};
        --sp-muted: {THEME["text_muted"]};
        --sp-accent: {THEME["accent"]};
        --sp-success: {THEME["success"]};
        --sp-warning: {THEME["warning"]};
        --sp-danger: {THEME["danger"]};
        --sp-glow: rgba(14, 165, 233, 0.15);
    }}

    /* Global layout & typography reset */
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        color: var(--sp-text);
        background-color: var(--sp-bg) !important;
    }}
    
    .stApp {{
        background-color: var(--sp-bg);
    }}
    
    /* Hide Streamlit default decorations */
    header, footer, #MainMenu {{
        visibility: hidden !important;
        display: none !important;
    }}

    /* Custom Scrollbars */
    ::-webkit-scrollbar {{
        width: 6px;
        height: 6px;
    }}
    ::-webkit-scrollbar-track {{
        background: var(--sp-bg);
    }}
    ::-webkit-scrollbar-thumb {{
        background: var(--sp-surface-elevated);
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--sp-accent);
    }}

    /* Sidebar Navigation Design */
    section[data-testid="stSidebar"] {{
        background-color: #05070B !important;
        border-right: 1px solid var(--sp-border) !important;
        width: 290px !important;
    }}
    
    .sidebar-logo {{
        font-family: 'Outfit', sans-serif;
        font-weight: 900;
        font-size: 1.45rem;
        letter-spacing: -0.04em;
        margin: 0;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }}
    
    .sidebar-tagline {{
        font-size: 0.68rem;
        font-weight: 650;
        color: var(--sp-muted);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin: 0.2rem 0 1.5rem 0;
    }}
    
    .nav-section-title {{
        font-size: 0.68rem;
        font-weight: 700;
        color: var(--sp-muted);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 1.4rem 0.5rem 0.4rem 0.5rem;
        opacity: 0.5;
    }}
    
    .nav-item {{
        display: flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0.55rem 0.75rem;
        margin-bottom: 0.2rem;
        border-radius: 8px;
        color: var(--sp-muted);
        text-decoration: none;
        font-size: 0.88rem;
        font-weight: 500;
        transition: background-color 0.15s, color 0.15s;
    }}
    
    .nav-item:hover {{
        background-color: rgba(255, 255, 255, 0.02);
        color: var(--sp-text);
    }}
    
    .nav-item-active {{
        background-color: rgba(14, 165, 233, 0.06) !important;
        color: var(--sp-accent) !important;
        border-left: 2px solid var(--sp-accent);
        border-top-left-radius: 0;
        border-bottom-left-radius: 0;
        font-weight: 600;
    }}
    
    .nav-item-disabled {{
        opacity: 0.35;
        cursor: not-allowed;
    }}
    
    .nav-item-disabled:hover {{
        background-color: transparent !important;
        color: var(--sp-muted) !important;
    }}
    
    .coming-soon-tag {{
        font-size: 0.62rem;
        font-weight: 700;
        background-color: var(--sp-surface-elevated);
        color: var(--sp-muted);
        padding: 0.1rem 0.35rem;
        border-radius: 4px;
        margin-left: auto;
        border: 1px solid var(--sp-border);
    }}

    /* Custom premium cards */
    .sp-card {{
        background-color: var(--sp-surface);
        border: 1px solid var(--sp-border);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        transition: border-color 0.2s, box-shadow 0.2s;
    }}
    
    .sp-card:hover {{
        border-color: rgba(14, 165, 233, 0.25);
        box-shadow: 0 0 18px rgba(14, 165, 233, 0.04);
    }}

    /* Upload Area redesign */
    .upload-box-premium {{
        background-color: var(--sp-surface);
        border: 1.5px dashed var(--sp-border);
        border-radius: 12px;
        padding: 3.5rem 2rem;
        text-align: center;
        margin-bottom: 1rem;
        transition: all 0.25s ease-in-out;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }}
    
    .upload-box-premium:hover {{
        border-color: var(--sp-accent);
        box-shadow: 0 0 25px rgba(14, 165, 233, 0.08);
        background-color: rgba(14, 165, 233, 0.01);
    }}
    
    .upload-icon-pulse {{
        font-size: 2.8rem;
        color: var(--sp-accent);
        margin-bottom: 1rem;
        opacity: 0.95;
        text-shadow: 0 0 15px rgba(14, 165, 233, 0.3);
    }}
    
    .upload-title-text {{
        font-family: 'Outfit', sans-serif;
        font-size: 1.35rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
        color: var(--sp-text);
        letter-spacing: -0.02em;
    }}
    
    .upload-subtitle-text {{
        font-size: 0.9rem;
        color: var(--sp-muted);
        margin-bottom: 1.5rem;
    }}

    .format-pill {{
        display: inline-block;
        background-color: var(--sp-surface-elevated);
        padding: 0.25rem 0.8rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--sp-accent);
        border: 1px solid var(--sp-border);
    }}

    /* Upload Success Card redesign */
    .success-card {{
        background-color: var(--sp-surface);
        border: 1px solid rgba(16, 185, 129, 0.15);
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }}
    
    .success-left-block {{
        display: flex;
        align-items: center;
        gap: 1rem;
    }}
    
    .success-icon-badge {{
        width: 42px;
        height: 42px;
        background-color: rgba(16, 185, 129, 0.08);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        color: var(--sp-success);
        border: 1px solid rgba(16, 185, 129, 0.15);
    }}
    
    .success-title {{
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 1.1rem;
        color: var(--sp-text);
        margin: 0;
    }}
    
    .success-details {{
        font-size: 0.85rem;
        color: var(--sp-muted);
        margin-top: 0.15rem;
    }}

    /* Connected KPI Card System */
    .kpi-row-container {{
        display: flex;
        background-color: var(--sp-surface);
        border: 1px solid var(--sp-border);
        border-radius: 12px;
        padding: 0.25rem;
        margin-bottom: 1.8rem;
        width: 100%;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }}
    
    .kpi-column-module {{
        flex: 1;
        padding: 1.25rem 1.5rem;
        position: relative;
        text-align: left;
    }}
    
    .kpi-column-module:not(:last-child)::after {{
        content: "";
        position: absolute;
        right: 0;
        top: 20%;
        width: 1px;
        height: 60%;
        background-color: var(--sp-border);
    }}
    
    .kpi-val-display {{
        font-family: 'Outfit', sans-serif;
        font-size: 1.95rem;
        font-weight: 800;
        color: var(--sp-text);
        margin: 0;
        line-height: 1.1;
    }}
    
    .kpi-lbl-display {{
        font-size: 0.72rem;
        font-weight: 700;
        color: var(--sp-muted);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 0.35rem;
        margin-bottom: 0;
    }}

    /* Table visual structure */
    table {{
        background-color: var(--sp-surface) !important;
        border-collapse: collapse !important;
        width: 100% !important;
        border-radius: 8px !important;
        overflow: hidden !important;
        border: 1px solid var(--sp-border) !important;
    }}
    
    th {{
        background-color: var(--sp-surface-elevated) !important;
        color: var(--sp-text) !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        padding: 10px 14px !important;
        text-align: left !important;
        border-bottom: 1px solid var(--sp-border) !important;
        font-size: 0.85rem !important;
    }}
    
    td {{
        padding: 10px 14px !important;
        border-bottom: 1px solid var(--sp-border) !important;
        color: var(--sp-muted) !important;
        font-size: 0.82rem !important;
    }}
    
    tr:last-child td {{
        border-bottom: none !important;
    }}
    
    tr:hover td {{
        color: var(--sp-text) !important;
        background-color: rgba(255, 255, 255, 0.015) !important;
    }}

    /* Status Badges */
    .status-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 0.2rem 0.55rem;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }}
    
    .status-badge-ready {{
        color: var(--sp-success);
        background-color: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.15);
    }}
    
    .status-badge-warning {{
        color: var(--sp-warning);
        background-color: rgba(245, 158, 11, 0.08);
        border: 1px solid rgba(245, 158, 11, 0.15);
    }}

    /* Command Interface Container */
    .ai-copilot-container {{
        background-color: var(--sp-surface);
        border: 1px solid var(--sp-border);
        border-radius: 12px;
        padding: 1.8rem;
        margin-top: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        transition: border-color 0.2s, box-shadow 0.2s;
    }}
    
    .ai-copilot-container:hover {{
        border-color: rgba(99, 102, 241, 0.2);
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.04);
    }}
    
    .ai-sparkle-icon {{
        color: var(--sp-accent);
        font-size: 1.1rem;
        margin-right: 0.4rem;
        text-shadow: 0 0 10px rgba(14, 165, 233, 0.4);
    }}

    /* Streamlit Components Overrides */
    
    /* Buttons */
    .stButton > button {{
        background-color: var(--sp-surface-elevated) !important;
        color: var(--sp-text) !important;
        border: 1px solid var(--sp-border) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s ease-in-out !important;
        width: 100% !important;
    }}
    
    .stButton > button:hover {{
        border-color: var(--sp-accent) !important;
        color: var(--sp-text) !important;
        background-color: rgba(14, 165, 233, 0.05) !important;
        box-shadow: 0 0 12px rgba(14, 165, 233, 0.1) !important;
    }}
    
    .stButton > button:active {{
        transform: scale(0.98) !important;
    }}
    
    /* Inputs */
    div[data-baseweb="input"] {{
        background-color: var(--sp-surface-elevated) !important;
        border: 1px solid var(--sp-border) !important;
        border-radius: 8px !important;
        color: var(--sp-text) !important;
    }}
    
    div[data-baseweb="input"] input {{
        color: var(--sp-text) !important;
        font-size: 0.9rem !important;
        padding: 0.55rem 0.85rem !important;
    }}
    
    /* Select-box */
    div[data-baseweb="select"] > div {{
        background-color: var(--sp-surface-elevated) !important;
        border: 1px solid var(--sp-border) !important;
        border-radius: 8px !important;
        color: var(--sp-text) !important;
        font-size: 0.9rem !important;
    }}
    
    /* Dataframes */
    div[data-testid="stDataFrame"] {{
        border: 1px solid var(--sp-border) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        background-color: var(--sp-surface) !important;
    }}
    
    /* Expanders */
    div[data-testid="stExpander"] {{
        background-color: var(--sp-surface) !important;
        border: 1px solid var(--sp-border) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
        margin-bottom: 1.5rem !important;
        overflow: hidden !important;
    }}
    
    div[data-testid="stExpander"] details summary {{
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        color: var(--sp-text) !important;
        padding: 0.9rem 1.2rem !important;
        background-color: var(--sp-surface) !important;
    }}
    
    div[data-testid="stExpander"] details summary:hover {{
        color: var(--sp-accent) !important;
    }}

    /* Tabs Styling */
    div[data-testid="stTabs"] {{
        background: transparent !important;
    }}
    
    div[data-testid="stTabs"] button[data-baseweb="tab"] {{
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        color: var(--sp-muted) !important;
        background-color: transparent !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.2s ease !important;
    }}
    
    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {{
        color: var(--sp-accent) !important;
        border-bottom: 2px solid var(--sp-accent) !important;
    }}
    
    div[data-testid="stTabs"] button[data-baseweb="tab"]:hover {{
        color: var(--sp-text) !important;
    }}
    
    div[data-testid="stTabs"] > div:first-child {{
        border-bottom: 1px solid var(--sp-border) !important;
    }}
    </style>
    """, unsafe_allow_html=True)
