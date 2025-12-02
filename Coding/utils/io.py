import os
import tempfile
import requests
 
import pandas as pd

def load_table(source: str) -> pd.DataFrame:
    """
    Load a table from a local file or URL. Supports CSV, Excel, Parquet, and public Google Sheets URLs.
    """
    # Google Sheets detection
    if source.startswith('https://docs.google.com/spreadsheets'):
        csv_url = source.split('/edit')[0] + '/export?format=csv'
        return pd.read_csv(csv_url)
 
    # URL: download to temp file and infer type
    if source.startswith('http://') or source.startswith('https://'):
        file_ext = os.path.splitext(source.split('?')[0])[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            response = requests.get(source)
            tmp.write(response.content)
            tmp.flush()
            tmp_name = tmp.name
        if file_ext == '.csv':
            return pd.read_csv(tmp_name)
        elif file_ext in ('.xls', '.xlsx'):
            return pd.read_excel(tmp_name)
        elif file_ext == '.parquet':
            return pd.read_parquet(tmp_name)
        else:
            raise ValueError(f"Unsupported remote file format: {file_ext}")
 
    # Local file
    file_ext = os.path.splitext(source)[-1].lower()
    if file_ext == '.csv':
        return pd.read_csv(source)
    elif file_ext in ('.xls', '.xlsx'):
        return pd.read_excel(source)
    elif file_ext == '.parquet':
        return pd.read_parquet(source)
    else:
        raise ValueError(f"Unsupported local file format: {file_ext}")
