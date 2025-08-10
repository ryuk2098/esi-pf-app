import pandas as pd
import numpy as np # Required for data types
from tabulate import tabulate

def verify_pf(payroll_df: pd.DataFrame, active_pf: pd.DataFrame) -> pd.DataFrame:
    """
    Validates and merges a payroll dataframe with an active PF members dataframe.

    Args:
        payroll_df (pd.DataFrame): DataFrame with payroll data, including "UAN", "MEMBER_NAME", and "father".
        active_pf (pd.DataFrame): DataFrame with active PF members, including "UAN". "Name", and "Father's/Husband's Name".

    Returns:
        pd.DataFrame: DataFrame containing UAN, names from payroll, and names from active PF list.

    Raises:
        ValueError: If validation checks for UAN mismatches fail.
    """
    # --- 1. Check for UANs in payroll_df that are NOT in active_pf ---
    # Using .isin() is efficient for this check
    required_payroll_cols = {"UAN", "MEMBER_NAME", "father"}
    required_active_cols = {"UAN", "Name", "Father's/Husband's Name"}
    if not required_payroll_cols.issubset(payroll_df.columns):
        raise ValueError(f"Payroll DataFrame missing required columns: {required_payroll_cols - set(payroll_df.columns)}")
    if not required_active_cols.issubset(active_pf.columns):
        raise ValueError(f"Active PF DataFrame missing required columns: {required_active_cols - set(active_pf.columns)}")

    # --- 1. Check for UANs in payroll_df not in active_pf ---
    missing_from_active = payroll_df[~payroll_df["UAN"].isin(active_pf["UAN"])]
    missing_from_active.index = missing_from_active.index + 2
    if not missing_from_active.empty:
        display_cols = ["UAN", "MEMBER_NAME"]
        table = tabulate(
            missing_from_active[display_cols], 
            headers=display_cols, 
            tablefmt='rounded_grid', 
        )
        raise ValueError(f"Error: The following UANs from WAGES sheet were not found in active PF list:\n{table}")

    # --- 2. Merge to compare names ---
    merged_df = payroll_df.merge(
        active_pf[["UAN", "Name", "Father's/Husband's Name"]],
        on="UAN",
        how="left"  # keep only payroll_df rows
    )

    # --- 3. Prepare verification DataFrame ---
    verify_df = merged_df.rename(columns={
        "MEMBER_NAME": "Name in Payment Sheet",
        "Name": "Name in Active List",
        "father": "Father's Name in Payment Sheet",
        "Father's/Husband's Name": "Father's Name in Active List"
    })[[
        "UAN", "Name in Payment Sheet", "Name in Active List",
        "Father's Name in Payment Sheet", "Father's Name in Active List"
    ]]

    verify_df.index = range(2, len(verify_df) + 2)

    return verify_df



def verify_esi(payroll_df: pd.DataFrame, active_esi: pd.DataFrame) -> None:
    """
    Validates and merges a payroll dataframe with an active PF members dataframe.

    Args:
        payroll_df (pd.DataFrame): DataFrame with calculated payroll data.
        active_esi (pd.DataFrame): DataFrame with active ESI members, including "empe_ip_number" and "empe_name".

    Returns:
        pd.DataFrame: DataFrame containing IP Number, IP Name from payroll, and empe_name from active ESI list.

    Raises:
        ValueError: If validation checks for esi_no mismatches fail.
    """
    # --- 1. Check for UANs in payroll_df that are NOT in active_pf ---
    # Using .isin() is efficient for this check

    required_active_cols = {"empe_ip_number", "empe_name"}
    if not required_active_cols.issubset(active_esi.columns):
        raise ValueError(f"Active PF DataFrame missing required columns: {required_active_cols - set(active_esi.columns)}")

    # --- 1. Check for UANs in payroll_df not in active_pf ---
    missing_from_active = payroll_df[~payroll_df["IP Number"].isin(active_esi["empe_ip_number"])]
    missing_from_active.index = missing_from_active.index + 2
    if not missing_from_active.empty:
        display_cols = ["IP Number", "IP Name"]
        table = tabulate(
            missing_from_active[display_cols], 
            headers=display_cols, 
            tablefmt='rounded_grid', 
        )
        raise ValueError(f"Error: The following ESI number from WAGES sheet were not found in ESI List of employees:\n{table}")
    
    # --- 2. Merge payroll with active ESI to get names side by side ---
    merged_df = payroll_df.merge(
        active_esi,
        how="left",
        left_on="IP Number",
        right_on="empe_ip_number"
    )

    # --- 3. Select and rename columns for clarity ---
    verify_df = merged_df[["IP Number", "IP Name", "empe_name"]].rename(
        columns={
            "IP Name": "Name in Payment Sheet",
            "empe_name": "Name in ESI Active List"
        }
    )
    verify_df.index = range(2, len(verify_df) + 2)
    return verify_df