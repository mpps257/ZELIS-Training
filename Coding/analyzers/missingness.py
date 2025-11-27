import pandas as pd
import numpy as np
from analyzers.numeric import analyze_numeric
 
def analyze_missingness(df: pd.DataFrame):
    results = []
    # Get numeric column skew/normality
    numeric_eda = analyze_numeric(df)
    skew_map = {row['column']: row['skewness'] for _, row in numeric_eda.iterrows()}
    for col in df.columns:
        s = df[col]
        missing = s.isnull().sum()
        pct = float(missing) / len(df) * 100 if len(df) > 0 else 0
        # Heuristic suggestions
        if pct > 30:
            suggestion = 'Drop column (>30% missing).'
        elif 5 < pct <= 30:
            # Numeric/categorical differentiation
            if pd.api.types.is_numeric_dtype(s):
                skew = skew_map.get(col, 0)
                shapiro_p = shap_map.get(col, None)
                if abs(skew) < 0.5 or (shapiro_p is not None and shapiro_p > 0.05):
                    suggestion = 'Impute missing values with mean or median (data is not strongly skewed).'
                else:
                    suggestion = 'Impute missing values with median (data is skewed).'
            else:
                suggestion = 'Impute missing values with mode (categorical).'
        elif 0 < pct <= 5:
            suggestion = 'Add missing value indicator flag.'
        else:
            suggestion = 'No missing data.'
        results.append({
            'column': col,
            'missing': int(missing),
            'missing_pct': pct,
            'suggestions': [suggestion]
        })
    # Dataset-level
    total_missing = df.isnull().values.sum()
    overall = {
        'total_missing': int(total_missing),
        'total_missing_pct': float(total_missing) / df.size * 100 if df.size > 0 else 0,
        'suggestions': []
    }
    if overall['total_missing_pct'] > 20:
        overall['suggestions'].append('Dataset has high overall missingness (>20%); review input sources or drop variables.')
    return pd.DataFrame(results), overall