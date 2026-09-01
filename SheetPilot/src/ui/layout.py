import streamlit as st
from src.config import IS_GEMINI_AVAILABLE
from src.state import SessionStateManager

def render_sidebar():
    """Render the premium sidebar navigation layout with status indicators and category structures."""
    with st.sidebar:
        # Title wordmark & tagline
        st.markdown('''
        <div style="margin-top: 1.2rem; margin-bottom: 1.8rem; padding-left: 0.5rem;">
            <h2 style="font-family: 'Outfit', sans-serif; font-weight: 900; font-size: 1.6rem; letter-spacing: -0.04em; margin: 0; color: #FFFFFF; line-height: 1.1;">
                SHEETPILOT<br><span style="background: linear-gradient(135deg, #0EA5E9 0%, #6366F1 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">AI</span>
            </h2>
            <p class="sidebar-tagline">Spreadsheet Automation Copilot</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # System Ready connection status badge
        if IS_GEMINI_AVAILABLE:
            st.markdown('<div class="status-badge status-badge-ready" style="margin-left: 0.5rem; margin-bottom: 2rem;">● System Ready</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-badge status-badge-warning" style="margin-left: 0.5rem; margin-bottom: 2rem;">● Config Required</div>', unsafe_allow_html=True)
            
        # Active Workspace Status
        st.markdown('<div class="nav-section-title">Active Workspace</div>', unsafe_allow_html=True)
        st.markdown('<a href="#" class="nav-item nav-item-active">📊 Dashboard Tabbed Suite</a>', unsafe_allow_html=True)
        
        # Voice history display in the sidebar
        history = SessionStateManager.get_transcript_history()
        if history:
            st.markdown('<div class="nav-section-title" style="margin-left: 0.5rem; margin-top: 1.5rem; margin-bottom: 0.5rem;">Voice History</div>', unsafe_allow_html=True)
            for entry in list(reversed(history))[:5]:
                lang = entry.get("language", "Unknown")
                text = entry.get("transcript", "")
                success = entry.get("success", True)
                
                if success:
                    st.markdown(f'''
                    <div style="background-color: rgba(255, 255, 255, 0.01); border: 1px solid var(--sp-border); border-radius: 6px; padding: 0.5rem 0.6rem; margin-bottom: 0.4rem; margin-left: 0.5rem; margin-right: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.68rem; font-weight: 700; color: var(--sp-accent); margin-bottom: 0.2rem;">
                            <span>🎙️ {lang}</span>
                            <span style="color: var(--sp-success); font-weight: 600;">✓ Transcribed</span>
                        </div>
                        <p style="font-size: 0.76rem; color: var(--sp-text); margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-style: italic;">"{text}"</p>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    err = entry.get("error", "Error")
                    st.markdown(f'''
                    <div style="background-color: rgba(239, 68, 68, 0.02); border: 1px solid rgba(239, 68, 68, 0.1); border-radius: 6px; padding: 0.5rem 0.6rem; margin-bottom: 0.4rem; margin-left: 0.5rem; margin-right: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.68rem; font-weight: 700; color: var(--sp-danger); margin-bottom: 0.2rem;">
                            <span>🎙️ {lang}</span>
                            <span style="font-weight: 600;">✗ Failed</span>
                        </div>
                        <p style="font-size: 0.72rem; color: var(--sp-muted); margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{err}</p>
                    </div>
                    ''', unsafe_allow_html=True)

        st.markdown('<hr style="border: 0; border-top: 1px solid var(--sp-border); margin: 2rem 0 1rem 0;">', unsafe_allow_html=True)
        
        # Active dataset info overview block
        uploaded_df = SessionStateManager.get_uploaded_df()
        if uploaded_df is not None:
            filename = st.session_state.get("uploaded_filename", "spreadsheet")
            st.markdown(f'''
            <div style="background-color: rgba(14, 165, 233, 0.03); border: 1px solid rgba(14, 165, 233, 0.1); border-radius: 8px; padding: 0.85rem; margin-bottom: 1rem; margin-left: 0.5rem; margin-right: 0.5rem;">
                <p style="font-size: 0.72rem; font-weight: 700; color: var(--sp-accent); margin: 0; text-transform: uppercase; letter-spacing: 0.05em;">Active Dataset</p>
                <p style="font-size: 0.85rem; font-weight: 600; color: #FFFFFF; margin: 0.3rem 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">📄 {filename}</p>
                <p style="font-size: 0.72rem; color: var(--sp-muted); margin: 0;">{uploaded_df.shape[0]:,} rows • {uploaded_df.shape[1]} cols</p>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div style="background-color: rgba(255, 255, 255, 0.01); border: 1px dashed var(--sp-border); border-radius: 8px; padding: 0.85rem; margin-bottom: 1rem; margin-left: 0.5rem; margin-right: 0.5rem; text-align: center;">
                <p style="font-size: 0.75rem; color: var(--sp-muted); margin: 0;">No active dataset</p>
            </div>
            ''', unsafe_allow_html=True)
            
        # Footer build tag
        st.markdown('''
        <div style="text-align: center; margin-top: auto; padding-bottom: 1.2rem; padding-left: 0.5rem;">
            <span style="font-size: 0.68rem; color: #475569; font-weight: 600; letter-spacing: 0.05em;">SheetPilot AI • v1.0.0 • Capstone Build</span>
        </div>
        ''', unsafe_allow_html=True)

