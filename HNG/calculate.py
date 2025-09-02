import pandas as pd
import numpy as np
from pathlib import Path
from io import BytesIO
from typing import List
from streamlit.runtime.uploaded_file_manager import UploadedFile
from tabulate import tabulate

from utils.save_output import save_esi_excel
from .verification import verify_pf, verify_esi

def calculate_pf(payroll_file: UploadedFile, active_pf_file: UploadedFile) -> List[pd.DataFrame]:
    wages_sheet = pd.read_excel(payroll_file, header=4, usecols=[ "Paycode", "UAN", "Name Of the Employee" , "PF GROSS", "NCP DAYS", "Father Name", "EDLI WAGES"],dtype={"UAN": str})
    wages_sheet.drop(wages_sheet.index[-1], inplace=True)
    active_pf = pd.read_csv(active_pf_file, usecols=["UAN", "Name", "Father's/Husband's Name", "DoB"],dtype={"UAN": str})


    wages_sheet = wages_sheet.merge(
        active_pf[["UAN", "DoB"]],
        on="UAN",
        how="left"
    )

    wages_sheet["DoB"] = pd.to_datetime(wages_sheet["DoB"], format="%d-%b-%Y")
    active_pf = active_pf.astype(str)

    # clean up input data
    missing_uan_wages = wages_sheet[wages_sheet["UAN"].isna()]
    missing_uan_wages.index = missing_uan_wages.index + 2
    if not missing_uan_wages.empty:
        display_cols = ["Paycode", "Name Of the Employee"]
        table = tabulate(
            missing_uan_wages[display_cols], 
            headers=display_cols, 
            tablefmt='rounded_grid',
        )
        raise ValueError(f"Missing UAN in WAGES sheet for the following rows:\n{table}")
    
    # constants
    EPF_RATE = 0.12
    EPS_RATE = 0.0833
    RETIREMENT_AGE = 58

    # age calculation
    processing_month = pd.Timestamp.today() - pd.DateOffset(months=1)  # July
    cutoff_date = processing_month.replace(day=1) - pd.DateOffset(days=1)  # Last day of June

    ages = (
        cutoff_date.year - wages_sheet["DoB"].dt.year
        - (
            (cutoff_date.month < wages_sheet["DoB"].dt.month) |
            ((cutoff_date.month == wages_sheet["DoB"].dt.month) &
            (cutoff_date.day < wages_sheet["DoB"].dt.day))
        )
    )

    # Wage calculations
    epf_wages = wages_sheet["PF GROSS"]
    eps_wages = epf_wages.where(ages < RETIREMENT_AGE, 0)
    epf_contri_remitted = round(epf_wages * EPF_RATE)
    eps_contri_remitted = round(eps_wages * EPS_RATE)
    epf_eps_diff_remitted = epf_contri_remitted - eps_contri_remitted

    # Output DataFrame
    out_df = pd.DataFrame({
        "UAN": wages_sheet["UAN"],
        "MEMBER_NAME": wages_sheet["Name Of the Employee"],
        "GROSS_WAGES": wages_sheet["PF GROSS"],
        "EPF_WAGES": epf_wages,
        "EPS_WAGES": eps_wages,
        "EDLI_WAGES": wages_sheet['EDLI WAGES'],
        "EPF_CONTRI_REMITTED": epf_contri_remitted,
        "EPS_CONTRI_REMITTED": eps_contri_remitted,
        "EPF_EPS_DIFF_REMITTED": epf_eps_diff_remitted,
        "NCP_DAYS": wages_sheet["NCP DAYS"],
        "REFUND_OF_ADVANCES": 0
    })

    for col in out_df.columns:
        if col in ["UAN", "MEMBER_NAME"]:
            out_df[col] = out_df[col].astype(str)
        else:
            out_df[col] = out_df[col].astype("Int64")
    
    payroll_df = out_df[["UAN", "MEMBER_NAME"]].copy()
    payroll_df["father"] = wages_sheet["Father Name"]
    verify_df = verify_pf(payroll_df, active_pf)
    return [verify_df, out_df]

def calculate_esi(payroll_file: UploadedFile, active_esi_file: UploadedFile) -> List[pd.DataFrame]:
    wages_sheet = pd.read_excel(payroll_file,header=4, usecols=['Paycode', 'Name Of the Employee', 'ESI No', 'Day ', 'Earning On Which ESI Deducted.'])
    wages_sheet.drop(wages_sheet.index[-1], inplace=True)
    wages_sheet["Day "] = wages_sheet["Day "].astype("Float64")
    wages_sheet["Earning On Which ESI Deducted."] = pd.to_numeric(wages_sheet["Earning On Which ESI Deducted."], errors="coerce").astype("Int64")
    wages_sheet["ESI No"] = wages_sheet["ESI No"].astype("Int64").astype(str)

    if Path(active_esi_file.name).suffix == ".xls":
        active_esi_df = pd.read_html(active_esi_file)
        if isinstance(active_esi_df, list):
            active_esi_df = active_esi_df[0]
    else:
        active_esi_df = pd.read_excel(active_esi_file)

    active_esi_df = active_esi_df.astype(str)


    # clean up input data
    missing_esi_wages = wages_sheet[wages_sheet["ESI No"].isna()]
    missing_esi_wages.index = missing_esi_wages.index + 2
    if not missing_esi_wages.empty:
        display_cols = ["Paycode", "Name Of the Employee"]
        table = tabulate(
            missing_esi_wages[display_cols], 
            headers=display_cols, 
            tablefmt='rounded_grid',
        )
        raise ValueError(f"Missing ESI number in WAGES sheet for the following rows:\n{table}")
    
    days = wages_sheet["Day "].copy()
        
    # Find fractional day rows
    fractional_rows = days[days % 1 != 0]
    if not fractional_rows.empty:
        # Sort by index to keep deterministic behavior
        frac_indices = fractional_rows.index.to_numpy()
        half = len(frac_indices) // 2

        # Apply ceil to first half, floor to second half
        days.loc[frac_indices[:half]] = np.ceil(days.loc[frac_indices[:half]])
        days.loc[frac_indices[half:]] = np.floor(days.loc[frac_indices[half:]])


    # Output DataFrame
    out_df = pd.DataFrame({
        "IP Number": wages_sheet["ESI No"],
        "IP Name": wages_sheet["Name Of the Employee"],
        "No of Days for which wages paid/payable during the month": days.astype(int),
        "Total Monthly Wages": wages_sheet["Earning On Which ESI Deducted."],
        " Reason Code for Zero workings days(numeric only; provide 0 for all other reasons- Click on the link for reference)": "",
        " Last Working Day": ""
    })
    out_df = out_df.astype(str).astype(str)


    verify_esi_df = verify_esi(out_df, active_esi_df)

    return [verify_esi_df, out_df]