import pandas as pd
import numpy as np
 
def analyze_categorical(df: pd.DataFrame, max_unique: int = 20):
    results = []
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    for col in cat_cols:
        s = df[col].astype(str)
        if s.empty:
            continue
        vc = s.value_counts(dropna=False)
        freq_top = vc.iloc[0] if len(vc) > 0 else np.nan
        mode = vc.index[0] if len(vc) > 0 else None
        cardinality = vc.shape[0]
        missing = (df[col].isnull() | (s == 'nan') | (s == '')).sum()
        unique = list(vc.index[:max_unique])
        label_inconsistency = any(u.lower() != u for u in vc.index if isinstance(u, str))
        imbalance = (vc.iloc[0] / float(vc.sum())) if vc.sum() else np.nan
        
        # Check for mixed types
        numeric_count = pd.to_numeric(df[col], errors='coerce').notna().sum()
        total_non_missing = len(df[col]) - missing
        has_mixed_types = False
        if total_non_missing > 0:
            numeric_ratio = numeric_count / total_non_missing
            if numeric_ratio > 0.1 and numeric_ratio < 0.9:  # Mixed numeric and non-numeric
                has_mixed_types = True
        
        suggestions = []
        # Mixed types - highest priority
        if has_mixed_types:
            suggestions.append('Column has mixed data types (numeric and non-numeric); normalize to consistent format or split into separate columns.')
        # Rare category suggestion
        rare_thresh = 0.01 * len(s)
        rare_cats = [cat for cat, count in vc.items() if count < rare_thresh]
        if len(rare_cats) > 0:
            suggestions.append('Group rare categories (<1%) into "Other".')
        # Encoding
        if cardinality <= 20:
            suggestions.append('One-hot encoding is suitable.')
        elif cardinality > 20:
            suggestions.append('Label encoding or target encoding is recommended (high cardinality).')
        # Label normalization
        if label_inconsistency:
            suggestions.append('Normalize label spelling and case.')
        # Imbalance
        if imbalance is not None and imbalance > 0.7:
            suggestions.append('Highly imbalanced (>70% one class); consider resampling or weighting.')
        results.append({
            'column': col,
            'count': s.count(),
            'cardinality': cardinality,
            'unique_sample': unique,
            'top_freq': freq_top,
            'mode': mode,
            'missing': missing,
            'missing_pct': 100 * missing / len(df),
            'label_inconsistency': label_inconsistency,
            'max_imbalance': imbalance,
            'has_mixed_types': has_mixed_types,
            'suggestions': suggestions,
        })
    return pd.DataFrame(results)