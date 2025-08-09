import pandas as pd
import numpy as np
import io
from io import BytesIO
from streamlit.runtime.uploaded_file_manager import UploadedFile

# Read input data
# wages_sheet = pd.read_excel("resources/PAYMENT SHEET SCL JUNE 2025.xlsx", sheet_name="WAGES", parse_dates=["birth_date"])
# ncp_days = pd.read_excel("resources/PAYMENT SHEET SCL JUNE 2025.xlsx", sheet_name="PAYMENT", header=1, usecols=["NCP DAYS","uan_no"])

# ===== Save function =====
def save_with_custom_sep(df, sep="#~#", header=False):
    buf = io.StringIO()
    if header:
        buf.write(sep.join(df.columns) + "\n")
    rows = [sep.join(map(str, row)) for row in df.itertuples(index=False, name=None)]
    buf.write("\n".join(rows))
    return buf.getvalue()


def calculate_pf(excel_file: UploadedFile) -> pd.DataFrame:
    wages_sheet = pd.read_excel(excel_file, sheet_name="WAGES", parse_dates=["birth_date"])
    payments_sheet = pd.read_excel(excel_file, sheet_name="PAYMENT", header=1, usecols=["NCP DAYS","uan_no"])

    # clean up input data
    wages_sheet.dropna(inplace=True, subset=["uan_no"])
    payments_sheet.dropna(inplace=True, subset=["uan_no"])

    # Check if counts match
    if len(wages_sheet) != len(payments_sheet):
        raise ValueError(f"Row count mismatch: WAGES has {len(wages_sheet)}, PAYMENT has {len(payments_sheet)}")

    # constants
    EPF_RATE = 0.12
    EPS_RATE = 0.0833
    EPF_WAGE_CAP = 15000
    RETIREMENT_AGE = 58

    # age calculation
    today = pd.Timestamp.today() - pd.DateOffset(months=1)
    ages = (
        today.year - wages_sheet["birth_date"].dt.year
        - ((today.month < wages_sheet["birth_date"].dt.month) |
        ((today.month == wages_sheet["birth_date"].dt.month) &
            (today.day < wages_sheet["birth_date"].dt.day)))
    )

    # Wage calculations
    gross_wages = wages_sheet["basic_sal"] + wages_sheet["earn_pf"]
    epf_wages = gross_wages.clip(upper=EPF_WAGE_CAP)
    eps_wages = epf_wages.where(ages < RETIREMENT_AGE, 0)
    epf_contri_remitted = round(epf_wages * EPF_RATE)
    eps_contri_remitted = round(eps_wages * EPS_RATE)
    epf_epf_diff_remitted = epf_contri_remitted - eps_contri_remitted

    # Output DataFrame
    out_df = pd.DataFrame({
        "UAN": wages_sheet["uan_no"],
        "MEMBER_NAME": wages_sheet["naam"],
        "GROSS_WAGES": gross_wages,
        "EPF_WAGES": epf_wages,
        "EPS_WAGES": eps_wages,
        "EDLI_WAGES": epf_wages,
        "EPF_CONTRI_REMITTED": epf_contri_remitted,
        "EPS_CONTRI_REMITTED": eps_contri_remitted,
        "EPF_EPS_DIFF_REMITTED": epf_epf_diff_remitted,
        "NCP_DAYS": payments_sheet["NCP DAYS"],
        "REFUND_OF_ADVANCES": 0
    })
    for col in out_df.columns:
        if col in ["UAN", "MEMBER_NAME"]:
            out_df[col] = out_df[col].astype(str)
        else:
            out_df[col] = out_df[col].astype(int)
    return out_df



def save_esi_excel(df: pd.DataFrame) -> BytesIO:
    instructions_df = pd.read_excel("resources/MC_Template_scl_june_2025.xlsx", sheet_name="Instructions & Reason Codes")

    # Write to in-memory Excel file with two sheets
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='ESI Report')
        instructions_df.to_excel(writer, index=False, sheet_name='Instructions & Reason Codes')
    output.seek(0)
    return output

def calculate_esi(excel_file: UploadedFile) -> BytesIO:
    wages_sheet = pd.read_excel(excel_file, sheet_name="WAGES")

    # clean up input data
    wages_sheet.dropna(inplace=True, subset=["esi_no"])
    days = wages_sheet["days"].copy()
    
    # Find fractional day rows
    fractional_rows = days[days % 1 != 0]
    if not fractional_rows.empty:
        # Sort by index to keep deterministic behavior
        frac_indices = fractional_rows.index.to_numpy()
        half = len(frac_indices) // 2

        # Apply ceil to first half, floor to second half
        days.loc[frac_indices[:half]] = np.ceil(days.loc[frac_indices[:half]])
        days.loc[frac_indices[half:]] = np.floor(days.loc[frac_indices[half:]])
    
    total_wages = wages_sheet["tot_earn"] + wages_sheet["ot_amtord"] + wages_sheet["earn_npf"]

    # Output DataFrame
    out_df = pd.DataFrame({
        "IP Number": wages_sheet["esi_no"],
        "IP Name": wages_sheet["naam"],
        "No of Days for which wages paid/payable during the month": days.astype(int),
        "Total Monthly Wages": total_wages,
        " Reason Code for Zero workings days(numeric only; provide 0 for all other reasons- Click on the link for reference)": "",
        " Last Working Day": ""
    })
    out_df = out_df.astype(str).astype(str)

    output_excel = save_esi_excel(out_df)

    return output_excel