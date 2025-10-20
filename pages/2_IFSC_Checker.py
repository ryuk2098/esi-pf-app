# pages/2_IFSC_Checker.py

import streamlit as st
import pandas as pd
from src.features.ifsc_checker import validate_ifsc_format, check_ifsc_exists

# --- Page Configuration ---
st.set_page_config(layout="wide")
st.title(":green[🔍 IFSC Code Checker]")

# --- Input Section ---
st.subheader(":blue[Enter IFSC Code]", divider="grey", width="content")

ifsc_input = st.text_input(
    "Enter 11-character IFSC Code (e.g., HDFC0000123)",
    key="ifsc_code_input",
    label_visibility="visible",
    width=300
).upper().strip()

# The entire logic now runs inside the button click condition
if st.button("Validate and Search IFSC"):
    
    # --- Step 1: Validate Input ---
    if not ifsc_input:
        st.warning("Please enter an IFSC code to search.")
        st.stop()
        
    if not validate_ifsc_format(ifsc_input):
        st.error(
            f"❌ Invalid IFSC Format: '{ifsc_input}'. Must be 4 letters, '0', then 6 alphanumeric characters."
        )
        st.stop()
    
    # --- Step 2: Call API ---
    with st.spinner(f"Searching for {ifsc_input}..."):
        # Use a local variable, not session_state
        result = check_ifsc_exists(ifsc_input)
        
    # --- Step 3: Display Results ---
    st.header(":blue[Verification Result]")
    st.subheader(":grey[Details]", divider="grey", width="content")
    
    if result['status'] == 'success':
        data = result['data']
        st.success(f"✅ IFSC Code Found and Verified!")
        
        col1, col2, col3 = st.columns(3)
        col1.metric(":green[Bank Name]", data.get("BANK"))
        col2.metric(":blue[Branch Name]", data.get("BRANCH"))
        col3.metric(":orange[City / District]", f"{data.get('CITY')} / {data.get('DISTRICT')}")

        st.info(f"**Address:** {data.get('ADDRESS')}")
        
        with st.expander("Show Full Response Data"):
            df = pd.DataFrame(data.items(), columns=['Key', 'Value'])
            df['Value'] = df['Value'].astype(str)
            st.dataframe(df, hide_index=True)

    elif result['status'] == 'error':
        st.error(f"⚠️ Search Failed: {result['message']}")
        
        if result['data']:
            with st.expander("Show Detailed Error Data"):
                st.json(result['data'])
else:
    # This message is shown only when the button has not been clicked in the current run
    st.info("Enter an IFSC code and click search to see the results.")