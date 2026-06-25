import pandas as pd
from io import BytesIO
def to_excel_bytes(df: pd.DataFrame) -> bytes:
    buffer=BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer: df.to_excel(writer,index=False,sheet_name="dados")
    buffer.seek(0); return buffer.getvalue()
