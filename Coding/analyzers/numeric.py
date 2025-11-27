import pandas as pd
import numpy as np
from scipy.stats import skew, kurtosis
 
def analyze_numeric(df: pd.DataFrame):
    results = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        s = df[col].dropna()
        if s.empty:
            continue
        stats = {
            'column': col,
            'count': s.count(),
            'mean': s.mean(),
            'median': s.median(),
            'variance': s.var(),
            'std': s.std(),
            'min': s.min(),
            'max': s.max(),
            'skewness': skew(s),
            'kurtosis': kurtosis(s),
            'outliers': int(((s < (s.quantile(0.25) - 1.5 * s.std())) | (s > (s.quantile(0.75) + 1.5 * s.std()))).sum()),
            'missing': int(df[col].isna().sum()),
            'missing_pct': float(df[col].isna().mean() * 100),
        }
       
        # Suggestions (transforms)
        suggestions = []
        if stats['skewness'] > 1:
            suggestions.append('Apply log or Box-Cox transform to reduce right skew.')
        elif stats['skewness'] < -1:
            suggestions.append('Apply square/cube transform to reduce left skew.')
        if stats['variance'] > 5 * abs(stats['mean']):
            suggestions.append('Standardize or normalize (variance much larger than mean).')
        if stats['outliers'] > 0.05 * stats['count']:
            suggestions.append('Winsorize or remove outliers (>5%).')
        
        stats['suggestions'] = suggestions
        results.append(stats)
    return pd.DataFrame(results)