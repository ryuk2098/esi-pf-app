import traceback
import streamlit as st
import pandas as pd
from somany.calculate import calculate_pf, calculate_esi, save_with_custom_sep

# ===== Dummy HNG processor =====
def process_hng(file):
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

# ===== Streamlit Page Config =====
st.set_page_config(page_title="PF/ESI Processing", layout="wide")
st.title("📄 PF/ESI Processing App")
st.markdown("Effortlessly process and prepare PF/ESI challan files.")

# ===== Step 1: Select Company =====
st.header("Step 1: Company Selection")
company = st.selectbox("Select the company", ["Somany", "HNG"])

# ===== Step 2: Upload File =====
st.header("Step 2: Upload Payroll File")
uploaded_file = st.file_uploader(
    "Upload your payroll Excel file (.xlsx)",
    type=["xlsx"],
    help="Ensure your file contains the required sheets: 'WAGES' and 'PAYMENT'."
)

# ===== Step 3: Processing =====
if uploaded_file is not None:
    st.success(f"✅ File uploaded: `{uploaded_file.name}`")
    
    # Reset approval state when new file is uploaded
    if 'current_file' not in st.session_state or st.session_state.current_file != uploaded_file.name:
        st.session_state.approved = False
        st.session_state.current_file = uploaded_file.name
    
    try:
        if company == "Somany":
            pf_df = calculate_pf(uploaded_file)
            esi_excel = calculate_esi(uploaded_file)
        else:
            pf_df = process_hng(uploaded_file)
            esi_excel = None

        # Store data in session state
        st.session_state.pf_df = pf_df
        st.session_state.esi_excel = esi_excel

        # Show data preview
        with st.expander("📊 Preview Processed Data", expanded=False):
            st.dataframe(pf_df, use_container_width=True)

        # Step 4: Approval & Download
        st.header("Step 3: Approval & File Generation")
        st.markdown("Review the data above. If everything looks good, approve to generate the challan file.")

        # Show key metrics
        numeric_cols = pf_df.select_dtypes(include=["number"]).columns
        if not numeric_cols.empty:
            st.subheader(f"📊 Totals Summary: {pf_df['GROSS_WAGES'].sum()}")
            totals_df = pd.DataFrame(pf_df[numeric_cols].sum()).T
            st.dataframe(totals_df, use_container_width=True, hide_index=True)
        
        if (pf_df["EPS_WAGES"] == 0).any():
            st.subheader(f"Age more than or equal to 58")
            age_df = pf_df[pf_df["EPS_WAGES"] == 0].copy()
            age_df.index = age_df.index + 2  
            st.dataframe(age_df, use_container_width=True)

        # Approval button
        if not st.session_state.approved:
            if st.button("✅ Approve and Generate File"):
                st.session_state.approved = True
                st.rerun()

        # Show download buttons if approved
        if st.session_state.approved:
            st.success("🎉 File approved! You can now download the files:")
            
            cols = st.columns(8)
            
            with cols[0]:
                if st.session_state.pf_df is not None:
                    file_content = save_with_custom_sep(st.session_state.pf_df, sep="#~#", header=False)
                    st.download_button(
                        label="📥 Download PF File",
                        data=file_content,
                        file_name="PF CHALAN PREPARATION.txt",
                        mime="text/plain"
                    )
            
            with cols[1]:
                if st.session_state.esi_excel is not None:
                    st.download_button(
                        label="📥 Download ESI File",
                        data=st.session_state.esi_excel,
                        file_name="ESI CHALAN PREPARATION.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

    except Exception as e:
        st.exception(e)
        traceback.print_exc()

else:
    st.info("Please upload the payroll file to proceed.")
    # Reset session state when no file is uploaded
    st.session_state.approved = False