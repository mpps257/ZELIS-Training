def numeric_narrative(stats: dict) -> list:
    col = stats['column']
    out = []
    sk = stats.get('skewness', 0)
    var = stats.get('variance', 0)
    mean = stats.get('mean', 1)
    outliers = stats.get('outliers', 0)
    count = stats.get('count', 1)
    shapiro_p = stats.get('shapiro_p', None)
    # Skewness
    if sk > 1:
        out.append(f"{col} is strongly right-skewed; consider log transform.")
    elif sk < -1:
        out.append(f"{col} is strongly left-skewed; consider square or cube transform.")
    # Dispersion
    if var > 5 * abs(mean):
        out.append(f"{col} shows high dispersion; standardization recommended.")
    # Outliers
    if outliers > 0.05 * count:
        out.append(f"{col} contains many extreme values; winsorization or removal suggested.")
    # Normality
    if shapiro_p is not None and shapiro_p < 0.05:
        out.append(f"{col} data is not normally distributed (Shapiro p<{shapiro_p:.1g}); consider transformation.")
    if not out:
        out.append(f"{col} appears typical; no strong transformation needed.")
    return out
 
def categorical_narrative(stats: dict) -> list:
    col = stats['column']
    out = []
    cardinality = stats.get('cardinality', 0)
    max_imbalance = stats.get('max_imbalance', None)
    sample = stats.get('unique_sample', [])
    has_mixed_types = stats.get('has_mixed_types', False)
    
    # Mixed types - highest priority issue
    if has_mixed_types:
        out.append(f"{col} has mixed data types (numeric and non-numeric); normalize to consistent format or split into separate columns.")
    
    if cardinality <= 20:
        out.append(f"{col} has manageable cardinality ({cardinality}); one-hot encoding is suitable.")
    elif cardinality > 20:
        out.append(f"{col} has high cardinality ({cardinality}); use label or target encoding.")
    if max_imbalance is not None and max_imbalance > 0.7:
        out.append(f"{col} is highly imbalanced (>70% in one class); consider resampling or reweighting.")
    if any(isinstance(v, str) and v.lower() != v for v in sample):
        out.append(f"{col} contains inconsistent labels; normalize spelling and case.")
    if not out:
        out.append(f"{col} is a clean, typical categorical column.")
    return out
 
def missingness_narrative(stats: dict) -> list:
    col = stats['column']
    pct = stats.get('missing_pct', 0)
    out = []
    if pct > 30:
        out.append(f"{col} has substantial missingness ({pct:.1f}%); dropping is advised.")
    elif 5 < pct <= 30:
        out.append(f"{col} has moderate missingness ({pct:.1f}%); imputation is recommended.")
    elif 0 < pct <= 5:
        out.append(f"{col} has minor missingness ({pct:.1f}%); add a missing flag feature.")
    # Return empty list if no missing data - don't clutter insights with "no missing data" messages
    return out
 
def correlation_narrative(col1, col2, value, kind='pearson'):
    out = []
    if kind == 'pearson' or kind == 'spearman':
        if abs(value) > 0.9:
            out.append(f"{col1} and {col2} are highly correlated ({kind}={value:.2f}); consider dropping one.")
    elif kind == 'cramers_v':
        if value > 0.5:
            out.append(f"{col1} and {col2} have strong categorical association (Cramér’s V={value:.2f}); feature selection may be needed.")
    return out or None
 