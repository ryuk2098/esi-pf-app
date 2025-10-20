import streamlit as st
from config.state_manager import initialize_session_state

# ===== Streamlit Page Config =====
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")


# ===== Initialize session state (for the first load) =====
initialize_session_state()

# --- Applied Color Theme ---
st.title(":green[Welcome to the Payroll & Banking Suite]")
st.markdown("Welcome! Use the navigation sidebar on the left or the launch buttons below to access different tools.")

st.header(":blue[Available Tools]", divider="grey")

# --- Tool 1: PF/ESI Calculator ---
col1, col2 = st.columns([4, 1])

with col1:
    # Applied Color Theme
    st.subheader(":grey[📄 PF/ESI Calculator]")
    st.write("Process payroll files, check active member lists, and generate official challan files.")

with col2:
    # Corrected width parameter to use_container_width
    if st.button("Launch Tool", key="launch_pf_esi", use_container_width=True):
        st.switch_page("pages/1_ESI_PF_Calculator.py")

st.divider()

# --- Tool 2: IFSC Checker ---
col3, col4 = st.columns([4, 1])

with col3:
    # Applied Color Theme
    st.subheader(":grey[🔍 IFSC Code Checker]")
    st.write("Search and validate the format and check the existence of an 11-character Indian Financial System Code (IFSC).")

with col4:
    # Corrected width parameter to use_container_width
    if st.button("Launch Tool", key="launch_ifsc", use_container_width=True):
        st.switch_page("pages/2_IFSC_Checker.py")

st.divider()