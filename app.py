import traceback
import streamlit as st
import pandas as pd
from somany.calculate import calculate_pf as spf, calculate_esi as sesi
from utils.save_output import save_pf_custom_sep, save_esi_excel

# ===== Dummy HNG processor (updated to accept new files) =====
# NOTE: Update your actual functions to accept these new arguments.
def process_hng(payroll_file, pf_members_file, esi_members_file):
    # You can now use the respective member files in your logic.
    # For this example, it still returns dummy data.
    return pd.DataFrame({
        "UAN": [54321, 98760],
        "NAME": ["Charlie", "David"],
        "GROSS_WAGES": [10000, 9000]
    })

# ===== Initialize session state =====
if 'approved' not in st.session_state:
    st.session_state.approved = False
if 'pf_df' not in st.session_state:
    st.session_state.pf_df = None
if 'esi_excel' not in st.session_state:
    st.session_state.esi_excel = None
# Add new state variables for the three files
if 'payroll_file' not in st.session_state:
    st.session_state.payroll_file = None
if 'pf_members_file' not in st.session_state:
    st.session_state.pf_members_file = None
if 'esi_members_file' not in st.session_state:
    st.session_state.esi_members_file = None

# ===== Streamlit Page Config =====
st.set_page_config(page_title="PF/ESI Processing", layout="wide")
st.title(":green[📄 PF/ESI Processing App]")

# ===== Step 1: Select Company =====
st.header(":blue[Step 1: Company Selection]")
company = st.selectbox("Select the company", ["Somany", "HNG"])

# ===== Step 2: Upload Files =====
st.header(":blue[Step 2: Upload Required Files]")
payroll_file = st.file_uploader(
    "1. Upload your main payroll Excel file (.xlsx)",
    type=["xlsx"],
    help="Ensure your file contains the required sheets: 'WAGES' and 'PAYMENT'."
)

# Show member file uploaders only after the main payroll file is uploaded
if payroll_file:
    # When a new payroll file is uploaded, reset everything that follows
    if st.session_state.payroll_file is None or payroll_file.name != st.session_state.payroll_file.name:
        st.session_state.approved = False
        st.session_state.pf_members_file = None
        st.session_state.esi_members_file = None
        st.session_state.pf_df = None
        st.session_state.esi_excel = None

    st.session_state.payroll_file = payroll_file
    st.success(f"✅ Payroll file uploaded: `{payroll_file.name}`")

    # Uploader for PF Active Members (CSV)
    pf_members_file = st.file_uploader(
        "2. Upload PF Active Members List (.csv)",
        type=["csv"],
        help="Upload the CSV file containing the list of active PF members."
    )
    if pf_members_file:
        st.session_state.pf_members_file = pf_members_file
        st.success(f"✅ PF members file uploaded: `{pf_members_file.name}`")

    # Uploader for ESI Active Members (Excel)
    esi_members_file = st.file_uploader(
        "3. Upload ESI List Of Employees (.xls or .xlsx)",
        type=["xls", "xlsx"],
        help="Upload the Excel file containing the list of active ESI members."
    )
    if esi_members_file:
        st.session_state.esi_members_file = esi_members_file
        st.success(f"✅ ESI members file uploaded: `{esi_members_file.name}`")

# ===== Step 3: Processing and Approval =====
# This block runs only when all three files are present in the session state
if st.session_state.payroll_file and st.session_state.pf_members_file and st.session_state.esi_members_file:
    st.header(":blue[Step 3: Processing and Approval]")

    try:
        # Pass the correct files to the correct functions
        if company == "Somany":
            verify_pf, pf_df = spf(st.session_state.payroll_file, st.session_state.pf_members_file)
            verify_esi, esi_df = sesi(st.session_state.payroll_file, st.session_state.esi_members_file)
        else: # HNG company logic
            pf_df = process_hng(st.session_state.payroll_file, st.session_state.pf_members_file, st.session_state.esi_members_file)
            esi_df = None # HNG does not produce an ESI file in this example

        # Store results in session state to prevent reprocessing
        st.session_state.pf_df = pf_df.copy()
        st.session_state.verify_pf = verify_pf.copy()
        st.session_state.esi_df = esi_df.copy()
        st.session_state.verify_esi = verify_esi.copy()

        # Approval & Download Section
        st.subheader(":grey[Review the data]", divider="grey", width="content")
        # Show data preview
        with st.expander("📊 Preview PF"):
            with st.expander("📊 Preview Processed PF Data", expanded=False):
                st.session_state.pf_df.index = range(2, len(st.session_state.pf_df) + 2)
                st.dataframe(st.session_state.pf_df, use_container_width=True)
            with st.expander("📊 Preview Names of Labours", expanded=False):
                st.dataframe(st.session_state.verify_pf, use_container_width=True)
        with st.expander("📊 Preview ESI"):
            with st.expander("📊 Preview Processed ESI Data", expanded=False):
                st.session_state.esi_df.index = range(2, len(st.session_state.esi_df) + 2)
                st.dataframe(st.session_state.esi_df, use_container_width=True)
            with st.expander("📊 Preview Names of Labours", expanded=False):
                    st.dataframe(st.session_state.verify_esi, use_container_width=True)

        # Show key metrics from the PF dataframe
        numeric_cols = pf_df.select_dtypes(include=["number"]).columns
        if not numeric_cols.empty:
            st.subheader(f":grey[Totals Summary:]", divider="grey", width="content")
            # st.markdown(f"##### :red[PF Gross Wages: {pf_df["GROSS_WAGES"].sum()}]")
            # st.markdown(f"##### :orange[ESI Gross Wages: {esi_df["Total Monthly Wages"].astype("Int64").sum()}]")
            # st.markdown(f"##### Total Number of Employees: {pf_df.shape[0]}")
            pf_gross, esi_gross, total_emp = st.columns(3)
            pf_gross.metric(":red[PF Gross Wages]", pf_df["GROSS_WAGES"].sum(), border=True)
            esi_gross.metric(":orange[ESI Gross Wages]", esi_df["Total Monthly Wages"].astype("Int64").sum(), border=True)
            total_emp.metric(":green[Total Number of Employees]", pf_df.shape[0], border=True)

            totals_df = pd.DataFrame(pf_df[numeric_cols].sum()).T
            st.dataframe(totals_df, use_container_width=True, hide_index=True)

        if (pf_df["EPS_WAGES"] == 0).any():
            st.subheader(f":grey[Employees with Age >= 58:]", divider="grey", width="content")
            age_df = pf_df[pf_df["EPS_WAGES"] == 0].copy()
            age_df.index = age_df.index + 2
            st.dataframe(age_df, use_container_width=True)

        # Approval button
        if not st.session_state.approved:
            if st.button("✅ Approve and Generate Files"):
                st.session_state.approved = True
                st.rerun()

        # Show download buttons only if approved
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
        st.error(f"```\n{e}\n```")  # show the exact error message from verify_pf
        traceback.print_exc()
    except Exception as e:
        st.error(f"An error occurred during processing: {e}")
        st.exception(e)
        traceback.print_exc()

else:
    # This message shows if not all files have been uploaded yet.
    st.info("Please upload the payroll file, PF members list, and ESI members list to proceed.")