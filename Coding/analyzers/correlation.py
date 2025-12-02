import pandas as pd
import numpy as np
from scipy.stats import spearmanr, pearsonr
from scipy.stats import chi2_contingency 
def numeric_correlation(df: pd.DataFrame):
    num_cols = df.select_dtypes(include=[np.number]).columns
    pearson = df[num_cols].corr(method='pearson')
    spearman = df[num_cols].corr(method='spearman')
    suggestions = []
    threshold = 0.9
    for c1 in pearson.columns:
        for c2 in pearson.index:
            if c1 < c2:
                val = pearson.loc[c1, c2]
                if abs(val) > threshold:
                    suggestions.append(f'Drop one of {{ {c1}, {c2} }} (Pearson > 0.9) to reduce multicollinearity.')
    return pearson, spearman, suggestions
 
def _prepare_categorical(series, max_categories=50):
    """Normalize categorical series and cap cardinality for stability."""
    ser = pd.Series(series).astype('object').fillna('Missing')
    if ser.nunique(dropna=False) > max_categories:
        top = ser.value_counts().index[:max_categories - 1]
        ser = ser.where(ser.isin(top), 'Other')
    return ser.astype('category')
 
 
def cramers_v(x, y, max_categories=50):
    cat_x = _prepare_categorical(x, max_categories)
    cat_y = _prepare_categorical(y, max_categories)
    r = len(cat_x.cat.categories)
    k = len(cat_y.cat.categories)
    if r < 2 or k < 2:
        return np.nan 
 
    codes_x = cat_x.cat.codes.to_numpy()
    codes_y = cat_y.cat.codes.to_numpy()
    mask = (codes_x != -1) & (codes_y != -1)
    codes_x = codes_x[mask]
    codes_y = codes_y[mask]
    n = len(codes_x)
    if n == 0:
        return np.nan
 
    combined = codes_x * k + codes_y
    counts = np.bincount(combined, minlength=r * k).reshape(r, k).astype(np.float64)
    row_sums = counts.sum(axis=1, keepdims=True)
    col_sums = counts.sum(axis=0, keepdims=True)
    expected = row_sums @ col_sums / n
 
    with np.errstate(divide='ignore', invalid='ignore'):
        chi2 = np.nansum(((counts - expected) ** 2) / expected, where=expected > 0)
 
    phi2 = chi2 / n if n else 0
    denom = min(k - 1, r - 1)
    if denom <= 0:
        return np.nan
    return np.sqrt(phi2 / denom) if np.isfinite(phi2) else np.nan
    


def categorical_correlation(df: pd.DataFrame, max_categories=50):
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    res = pd.DataFrame(index=cat_cols, columns=cat_cols, dtype=float)
    suggestions = []
    for i, c1 in enumerate(cat_cols):
        for c2 in cat_cols[i + 1:]:
            v = cramers_v(df[c1], df[c2], max_categories=max_categories)
            res.loc[c1, c2] = v
            res.loc[c2, c1] = v
            if v is not None and v > 0.5:
                suggestions.append(f'Consider combining or dropping strongly associated categories: {c1}, {c2} (Cramér’s V > 0.5)')
    return res, suggestions
 
def analyze_correlation(df: pd.DataFrame):
    pearson, spearman, num_sugg = numeric_correlation(df)
    categorical, cat_sugg = categorical_correlation(df)
    suggestions = num_sugg + cat_sugg
    return {
        'pearson': pearson,
        'spearman': spearman,
        'categorical': categorical,
        'suggestions': suggestions,
    }
 