import streamlit as st
from config.state_manager import initialize_session_state

# Initialize session state once, at the very beginning
initialize_session_state()

st.set_page_config(page_title="Payroll & Banking Tools", layout="wide", initial_sidebar_state="collapsed")

# st.session_state.sidebar_state = 'expanded'
# time.sleep(0.1) 

# Define the pages for your app
pages = [
    st.Page("pages/0_Home.py", title="Home", icon="🏠"),
    st.Page("pages/1_ESI_PF_Calculator.py", title="ESI PF Calculator", icon="📄"),
    st.Page("pages/2_IFSC_Checker.py", title="IFSC Checker", icon="🔍"),
]

# Create the navigation menu
# This is where you can control the sidebar's default state!
pg = st.navigation(pages, position="top")

# Run the selected page
pg.run()