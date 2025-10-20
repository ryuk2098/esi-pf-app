# pages/1_ESI_PF_Calculator.py

import traceback
import streamlit as st
import pandas as pd

# Import initialization and processing logic
from config.state_manager import initialize_session_state
from src.features.esi_pf_challan import somany_pf, somany_esi, hng_pf, hng_esi, save_esi_excel, save_pf_custom_sep

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# --- CORE RESET FUNCTION ---
def reset_all_states():
    """Resets all data-related session states and clears file uploader keys."""
    
    # 1. Clear Processing/Results Data
    st.session_state.approved = False
    st.session_state.pf_df = None
    st.session_state.esi_df = None
    st.session_state.verify_pf = None
    st.session_state.verify_esi = None
    
    # 2. Clear our DERIVED state keys (safe to clear)
    st.session_state.payroll_file = None
    st.session_state.pf_payroll_file = None
    st.session_state.esi_payroll_file = None
    st.session_state.pf_members_file = None
    st.session_state.esi_members_file = None

    # 3. Clear the actual file uploader widget keys (CRITICAL FIX)
    file_keys_to_clear = [
        'somany_payroll_file', 'pf_payroll', 'esi_payroll', 'pf_members', 'esi_members'
    ]
    
    for key in file_keys_to_clear:
        # Use del to completely remove the file object and allow the new widget to initialize cleanly
        if key in st.session_state:
            del st.session_state[key]


# 1. Guaranteed Initialization
initialize_session_state()

st.title(":green[📄 PF/ESI Processing App]")


# ===== Step 1: Select Company =====
st.header(":blue[Step 1: Company Selection]")

def handle_company_change():
    """Triggered when the company selection changes."""
    if st.session_state.current_company != st.session_state.company_select:
        reset_all_states()
        st.session_state.current_company = st.session_state.company_select
        
company = st.selectbox(
    "Select the company", 
    ["Somany", "HNG"],
    key="company_select",
    on_change=handle_company_change
)

if st.session_state.current_company is None:
    st.session_state.current_company = company


# ===== Step 2: Upload Required Files =====
st.header(":blue[Step 2: Upload Required Files]")

# --- Helper function to handle file upload state ---
# This helper now only maps the file object and handles downstream state reset.
def handle_file_upload_state(file_object, state_key):
    """Assigns file object to the consistent state key and resets processing flags if the file changed."""
    
    # Check if the file object is new or different from what's currently stored under the state_key
    is_new = file_object is not None and (st.session_state.get(state_key) is None or file_object.name != st.session_state.get(state_key).name)
    is_cleared = file_object is None and st.session_state.get(state_key) is not None

    if is_new or is_cleared:
        st.session_state.approved = False
        st.session_state.pf_df = None
        st.session_state.esi_df = None
        st.session_state.verify_pf = None
        st.session_state.verify_esi = None
    
    # Always update the consistent state key
    st.session_state[state_key] = file_object
    
    return file_object is not None


if company == "Somany":
    st.subheader(":grey[Payment Sheet]", divider="grey", width="content")
    payroll_file = st.file_uploader(
        "1. Upload your main payroll Excel file (.xlsx)",
        type=["xlsx"],
        key="somany_payroll_file",
        help="Ensure your file contains the required sheets: 'WAGES' and 'PAYMENT'."
    )
    if handle_file_upload_state(payroll_file, 'payroll_file'):
        st.success(f"✅ Payroll file uploaded: `{payroll_file.name}`")
    
elif company == "HNG":
    upload_cols = st.columns(2)
    with upload_cols[0]:
        st.subheader(":grey[PF Payroll Sheet]", divider="grey", width="content")
        pf_payroll_file = st.file_uploader(
            "1. Upload PF Payroll Excel file (.xlsx)",
            type=["xlsx"],
            key="pf_payroll" 
        )
        if handle_file_upload_state(pf_payroll_file, 'pf_payroll_file'):
            st.success(f"✅ PF Payroll file uploaded: `{pf_payroll_file.name}`")
            
    with upload_cols[1]:
        st.subheader(":grey[ESI Payroll Sheet]", divider="grey", width="content")
        esi_payroll_file = st.file_uploader(
            "2. Upload ESI Payroll Excel file (.xlsx)",
            type=["xlsx"],
            key="esi_payroll" 
        )
        if handle_file_upload_state(esi_payroll_file, 'esi_payroll_file'):
            st.success(f"✅ ESI Payroll file uploaded: `{esi_payroll_file.name}`")

    
# Safely retrieve file states using the consistent naming convention
payroll_file_state = st.session_state.get('payroll_file')
pf_payroll_file_state = st.session_state.get('pf_payroll_file')
esi_payroll_file_state = st.session_state.get('esi_payroll_file')


# Determine if we should show the member file uploaders
if (company == "Somany" and payroll_file_state) or \
   (company == "HNG" and pf_payroll_file_state and esi_payroll_file_state):
    
    upload_cols = st.columns(2)

    with upload_cols[0]:
        st.subheader(":grey[PF Active Member List]", divider="grey", width="content")
        pf_members_file = st.file_uploader(
            "2. Upload PF Active Members List (.csv)",
            type=["csv"],
            key="pf_members", 
            help="Upload the CSV file containing the list of active PF members."
        )
        if handle_file_upload_state(pf_members_file, 'pf_members_file'):
            st.success(f"✅ PF members file uploaded: `{pf_members_file.name}`")

    with upload_cols[1]:
        st.subheader(":grey[ESI Active List of Employees]", divider="grey", width="content")
        esi_members_file = st.file_uploader(
            "3. Upload ESI List Of Employees (.xls or .xlsx)",
            type=["xls", "xlsx"],
            key="esi_members", 
            help="Upload the Excel file containing the list of active ESI members."
        )
        if handle_file_upload_state(esi_members_file, 'esi_members_file'):
            st.success(f"✅ ESI members file uploaded: `{esi_members_file.name}`")

# Safely retrieve member file states
pf_members_file_state = st.session_state.get('pf_members_file')
esi_members_file_state = st.session_state.get('esi_members_file')


# ===== Step 3: Processing and Approval =====

if company == "Somany":
    ready = payroll_file_state and pf_members_file_state and esi_members_file_state
else:  # HNG
    ready = pf_payroll_file_state and esi_payroll_file_state and pf_members_file_state and esi_members_file_state

if ready:
    st.header(":blue[Step 3: Processing and Approval]")
    
    # --- Processing Logic (Unchanged from previous successful revision) ---
    try:
        # Run calculation only if data is missing or not yet approved
        if st.session_state.pf_df is None or st.session_state.approved == False:
            
            with st.spinner(f"Processing calculations for {company}..."):
                if company == "Somany":
                    verify_pf, pf_df = somany_pf(st.session_state.payroll_file, st.session_state.pf_members_file)
                    verify_esi, esi_df = somany_esi(st.session_state.payroll_file, st.session_state.esi_members_file)
                else: # HNG company logic
                    verify_pf, pf_df = hng_pf(st.session_state.pf_payroll_file, st.session_state.pf_members_file)
                    verify_esi, esi_df = hng_esi(st.session_state.esi_payroll_file, st.session_state.esi_members_file)

            # Store results in session state 
            st.session_state.pf_df = pf_df.copy()
            st.session_state.verify_pf = verify_pf.copy()
            st.session_state.esi_df = esi_df.copy()
            st.session_state.verify_esi = verify_esi.copy()
            
            st.success("Processing complete. Review data below.")

        # If results are already stored, load them for display
        pf_df = st.session_state.pf_df
        esi_df = st.session_state.esi_df
        verify_pf = st.session_state.verify_pf
        verify_esi = st.session_state.verify_esi

        # --- Display Section (Omitted for brevity, assumed to be unchanged) ---
        st.subheader(":grey[Review the data]", divider="grey", width="content")
        
        # [Preview Expander blocks go here]
        with st.expander("📊 Preview PF"):
            with st.expander("📊 Preview Processed PF Data", expanded=False):
                pf_df_display = pf_df.copy()
                pf_df_display.index = range(2, len(pf_df_display) + 2)
                st.dataframe(pf_df_display, width='stretch')
            with st.expander("📊 Preview Names of Labours", expanded=False):
                verify_pf.index = range(2, len(verify_pf) + 2)
                st.dataframe(verify_pf, width='stretch')
                
        with st.expander("📊 Preview ESI"):
            with st.expander("📊 Preview Processed ESI Data", expanded=False):
                esi_df_display = esi_df.copy()
                esi_df_display.index = range(2, len(esi_df_display) + 2)
                st.dataframe(esi_df_display, width='stretch')
            with st.expander("📊 Preview Names of Labours", expanded=False):
                    verify_esi.index = range(2, len(verify_esi) + 2)
                    st.dataframe(verify_esi, width='stretch')


        # [Totals Summary blocks go here]
        if pf_df is not None and not pf_df.empty:
            numeric_cols = pf_df.select_dtypes(include=["number"]).columns
            if not numeric_cols.empty:
                st.subheader(f":grey[Totals Summary]", divider="grey", width="content")
                
                sum_cols = st.columns(4)
                
                esi_days = esi_df.get("No of Days for which wages paid/payable during the month")
                esi_wages = esi_df.get("Total Monthly Wages")
                
                with sum_cols[0]:
                    st.metric(":blue[Total Number of Employees]", pf_df.shape[0], border=True)
                with sum_cols[1]:
                    st.metric(":green[PF Gross Wages]", pf_df["GROSS_WAGES"].sum(), border=True)
                with sum_cols[2]:
                    esi_days_sum = esi_days.astype(int).sum() if esi_days is not None else 0
                    st.metric(":red[ESI Total Days]", esi_days_sum, border=True)
                    
                with sum_cols[3]:
                    esi_wages_sum = esi_wages.astype(int).sum() if esi_wages is not None else 0
                    st.metric(":orange[ESI Gross Wages]", esi_wages_sum, border=True)
                
                totals_df = pd.DataFrame(pf_df[numeric_cols].sum()).T
                st.dataframe(totals_df, width='stretch', hide_index=True)

            if "EPS_WAGES" in pf_df.columns and (pf_df["EPS_WAGES"] == 0).any():
                st.subheader(f":grey[Employees with Age >= 60]", divider="grey", width="content")
                age_df = pf_df[pf_df["EPS_WAGES"] == 0].copy()
                age_df.index = age_df.index + 2
                st.dataframe(age_df, width='stretch')


        # [Approval and Download blocks go here]
        if not st.session_state.approved:
            if st.button("✅ Approve and Generate Files"):
                st.session_state.approved = True
                st.rerun()

        if st.session_state.approved:
            st.success("🎉 Approved! You can now download the generated files.")
            
            cols = st.columns(8)
            
            with cols[0]:
                if st.session_state.pf_df is not None:
                    file_content = save_pf_custom_sep(st.session_state.pf_df, sep="#~#", header=False)
                    st.download_button(
                        label="📥 Download PF File",
                        data=file_content,
                        file_name="PF_CHALLAN.txt",
                        mime="text/plain"
                    )
            
            with cols[1]:
                if st.session_state.esi_df is not None:
                    st.download_button(
                        label="📥 Download ESI File",
                        data=save_esi_excel(st.session_state.esi_df),
                        file_name="ESI_CHALLAN.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
    
    except ValueError as e:
        st.error(f"Processing Error (Validation):\n```\n{e}\n```")
        traceback.print_exc()
        st.session_state.pf_df = None
        st.session_state.esi_df = None
        st.session_state.approved = False
        
    except Exception as e:
        st.error(f"An unexpected error occurred during processing: {e}")
        st.exception(e)
        traceback.print_exc()

else:
    st.info("Please upload the required payroll files and member lists to proceed.")