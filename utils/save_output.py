import io
from io import BytesIO
import pandas as pd

# ===== Save function =====
def save_pf_custom_sep(df: pd.DataFrame, sep="#~#", header=False) -> str:
    buf = io.StringIO()
    if header:
        buf.write(sep.join(df.columns) + "\n")
    rows = [sep.join(map(str, row)) for row in df.itertuples(index=False, name=None)]
    buf.write("\n".join(rows))
    return buf.getvalue()

def save_esi_excel(df: pd.DataFrame) -> BytesIO:
    instructions_df = pd.read_excel("resources/MC_Template_scl_june_2025.xlsx", sheet_name="Instructions & Reason Codes")

    # Write to in-memory Excel file with two sheets
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='ESI Report')
        instructions_df.to_excel(writer, index=False, sheet_name='Instructions & Reason Codes')
    output.seek(0)
    return output