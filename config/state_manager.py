# config/state_manager.py

import streamlit as st

def initialize_session_state():
    """Initializes all necessary keys in st.session_state."""
    
    # Core Processing Flags
    if 'approved' not in st.session_state:
        st.session_state.approved = False
        
    # Result DataFrames
    if 'pf_df' not in st.session_state:
        st.session_state.pf_df = None
    if 'esi_excel' not in st.session_state:
        st.session_state.esi_excel = None
    if 'verify_pf' not in st.session_state:
        st.session_state.verify_pf = None
    if 'verify_esi' not in st.session_state:
        st.session_state.verify_esi = None
    if 'esi_df' not in st.session_state:  # Added for consistency
        st.session_state.esi_df = None
        
    # Uploaded Files (used by ESI/PF Page)
    if 'payroll_file' not in st.session_state:
        st.session_state.payroll_file = None
    if 'pf_members_file' not in st.session_state:
        st.session_state.pf_members_file = None
    if 'esi_members_file' not in st.session_state:
        st.session_state.esi_members_file = None
    if 'pf_payroll_file' not in st.session_state:
        st.session_state.pf_payroll_file = None
    if 'esi_payroll_file' not in st.session_state:
        st.session_state.esi_payroll_file = None
        
    # Company state tracker
    if 'current_company' not in st.session_state:
        st.session_state.current_company = None