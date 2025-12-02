import pandas as pd
import numpy as np
 
def section_container(title, content, level=2):
    return f"\n{'#' * level} {title}\n\n{content}\n\n---\n"
 
def suggestions_block(suggestions):
    if not suggestions: return ''
    # If suggestions are already grouped by column (dict), format them
    if isinstance(suggestions, dict):
        result = []
        for col, sugg_list in suggestions.items():
            if sugg_list:
                result.append(f"- **{col}**")
                for s in sugg_list:
                    result.append(f"  - {s}")
        bullets = '\n'.join(result)
    else:
        # Legacy flat list format - try to group by column name
        grouped = {}
        for s in suggestions:
            if not s: continue
            # Try to extract column name from "**Col**: suggestion" format
            if '**: ' in s:
                col, sugg = s.split('**: ', 1)
                col = col.replace('**', '').strip()
                if col not in grouped:
                    grouped[col] = []
                grouped[col].append(sugg)
            else:
                # Fallback: add as-is
                if 'Uncategorized' not in grouped:
                    grouped['Uncategorized'] = []
                grouped['Uncategorized'].append(s)
        if grouped:
            result = []
            for col, sugg_list in grouped.items():
                result.append(f"- **{col}**")
                for s in sugg_list:
                    result.append(f"  - {s}")
            bullets = '\n'.join(result)
        else:
            bullets = '\n'.join(f'- {s}' for s in suggestions if s)
    return f"\n> **Suggested Transforms / Actions:**\n>\n> {bullets}\n\n"
 
def df_to_md_table(df: pd.DataFrame, floatfmt=".3g", max_rows=15):
    if df.empty:
        return 'No data.'
    df = df.copy().iloc[:max_rows]
    tbl = df.to_markdown(index=False, floatfmt=floatfmt)
    return f"\n{tbl}\n"
 
def detect_mixed_types(col, series):
    """Detect if a column has mixed data types (e.g., numbers and strings)"""
    if pd.api.types.is_numeric_dtype(series):
        # Check if numeric column has non-numeric values when converted to string
        non_numeric = pd.to_numeric(series, errors='coerce').isna().sum()
        if non_numeric > 0 and non_numeric < len(series) * 0.5:
            return True, f"Contains {non_numeric} non-numeric values in numeric column"
    elif series.dtype == 'object':
        # Check if object column has mixed numeric and non-numeric
        numeric_count = pd.to_numeric(series, errors='coerce').notna().sum()
        if numeric_count > 0 and numeric_count < len(series) * 0.95:
            return True, f"Contains {numeric_count} numeric and {len(series) - numeric_count} non-numeric values"
    return False, None
 
def detect_column_type(col, series):
    """Detect column type: numeric, categorical, text, datetime"""
    if pd.api.types.is_datetime64_any_dtype(series) or pd.api.types.is_datetime64_ns_dtype(series):
        return 'datetime'
    elif pd.api.types.is_numeric_dtype(series):
        return 'numeric'
    elif pd.api.types.is_categorical_dtype(series):
        return 'categorical'
    else:
        # Check if it's text (long strings) vs categorical (few unique values)
        unique_ratio = series.nunique() / len(series) if len(series) > 0 else 0
        if unique_ratio > 0.8 and series.astype(str).str.len().mean() > 20:
            return 'text'
        else:
            return 'categorical'
 
def overview_section(df: pd.DataFrame):
    # Data type detection
    col_types = {}
    type_counts = {'numeric': 0, 'categorical': 0, 'text': 0, 'datetime': 0}
    mixed_type_cols = []
    
    for col in df.columns:
        col_type = detect_column_type(col, df[col])
        col_types[col] = col_type
        type_counts[col_type] = type_counts.get(col_type, 0) + 1
        
        # Check for mixed types
        is_mixed, mixed_info = detect_mixed_types(col, df[col])
        if is_mixed:
            mixed_type_cols.append((col, mixed_info))
    
    # Create column type table
    type_table_data = []
    for col, dtype in col_types.items():
        mixed_flag = "⚠️ Mixed" if any(c[0] == col for c in mixed_type_cols) else ""
        type_table_data.append({
            'Column': col, 
            'Type': dtype, 
            'Pandas dtype': str(df[col].dtype),
            'Mixed Types': mixed_flag
        })
    type_df = pd.DataFrame(type_table_data)
    
    overview_items = [
        f"- Shape: **{df.shape[0]} rows** × **{df.shape[1]} columns**",
        f"- Memory usage: **{df.memory_usage().sum()//1024} KB**",
        f"- **Data Type Distribution:**",
        f"  - Numeric: {type_counts['numeric']}",
        f"  - Categorical: {type_counts['categorical']}",
        f"  - Text: {type_counts['text']}",
        f"  - Datetime: {type_counts['datetime']}",
    ]
    
    # Add mixed type warning if found
    if mixed_type_cols:
        overview_items.append(f"\n> ⚠️ **Data Quality Issue: Mixed Data Types Detected**\n>")
        overview_items.append("> The following columns contain mixed data types (e.g., numeric and text values):\n>")
        for col, info in mixed_type_cols:
            overview_items.append(f"> - **{col}**: {info}")
        overview_items.append(f">\n> **Recommendation:** Normalize data types (convert to consistent format) or split into separate columns.\n")
    
    overview_items.append(f"\n**Column Data Types:**\n" + df_to_md_table(type_df, max_rows=100))
    
    return section_container('Overview', '\n'.join(overview_items), level=2)
def sample_records_section(df: pd.DataFrame):
        samples = df.head(8).to_markdown(index=False)
        return section_container('Sample Records', samples, level=2)
 
def format_insights(narratives):
    """Display each column's narrative as bolded name; each list item is a sub-bullet. Extra \n for separation."""
    result = []
    for col, narrative_lines in narratives.items():
        if isinstance(narrative_lines, str):
            narrative_lines = [narrative_lines]
        elif not isinstance(narrative_lines, list):
            continue
        # Skip columns with no insights (empty lists)
        if not narrative_lines:
            continue
        # Remove leading column names for redundancy
        formatted = []
        for f in narrative_lines:
            lowf = f.lower()
            if lowf.startswith(col.lower()):
                f = f[len(col):].lstrip().capitalize()
            formatted.append(f"  - {f}")
        result.append(f"- **{col}**\n" + '\n'.join(formatted))
    return '\n\n'.join(result)
 
def numeric_section(numeric_df: pd.DataFrame, narratives: dict):
    all_suggestions = {}
    for _, row in numeric_df.iterrows():
        col = row['column']
        sugg = row.get('suggestions', []) or []
        if sugg: all_suggestions[col] = sugg
    tbl = df_to_md_table(numeric_df)
    content = f"{tbl}\n{suggestions_block(all_suggestions)}\n**Insights:**\n\n" + format_insights(narratives)
    return section_container('Numeric Column Insights', content, level=2)
 
def categorical_section(cat_df: pd.DataFrame, narratives: dict):
    all_suggestions = {}
    for _, row in cat_df.iterrows():
        col = row['column']
        sugg = row.get('suggestions', []) or []
        if sugg: all_suggestions[col] = sugg
    tbl = df_to_md_table(cat_df)
    content = f"{tbl}\n{suggestions_block(all_suggestions)}\n**Insights:**\n\n" + format_insights(narratives)
    return section_container('Categorical Column Insights', content, level=2)
 
def missingness_section(miss_df: pd.DataFrame, narratives: dict):
    all_suggestions = {}
    for _, row in miss_df.iterrows():
        col = row['column']
        sugg = row.get('suggestions', []) or []
        if sugg: all_suggestions[col] = sugg
    tbl = df_to_md_table(miss_df)
    content = f"{tbl}\n{suggestions_block(all_suggestions)}\n**Insights:**\n\n" + format_insights(narratives)
    return section_container('Missingness', content, level=2)
 
def correlation_section(corrs: dict, narratives: list):
    all_suggestions = corrs.get('suggestions', [])
    blocks = []
    if not corrs['pearson'].empty:
        blocks.append('**Pearson Correlation:**\n' + df_to_md_table(corrs['pearson']))
    if not corrs['categorical'].empty:
        blocks.append('**Cramér’s V (Categorical):**\n' + df_to_md_table(corrs['categorical']))
    block = '\n'.join(blocks)
    insight_lines = []
    for s in narratives:
        if ':' in s:
            label, msg = s.split(':', 1)
            insight_lines.append(f"- **{label.strip()}**\n  - {msg.strip()}")
        else:
            insight_lines.append("  - " + s.strip())
    content = f"{block}\n{suggestions_block(all_suggestions)}\n**Insights:**\n\n" + '\n\n'.join(insight_lines)
    return section_container('Correlation/Association', content, level=2)
 
def class_balance_section(s: pd.Series, bar_img: str, max_cats: int = 25):
    vc = s.value_counts(dropna=False).iloc[:max_cats]
    tbl = vc.reset_index().rename(columns={'index': 'Label', s.name: 'Count'}).to_markdown(index=False)
    # Use HTML img tag for proper width control (bar_img is already relative path)
    img_md = f'<img src="{bar_img}" alt="Class distribution" width="390" />'
    suggestions = []
    if vc.iloc[0] / vc.sum() > 0.7:
        suggestions.append('Severe class imbalance detected (>70% in one class). Use resampling or class weighting.')
    content = f'{tbl}\n\n{img_md}\n\n{suggestions_block(suggestions)}'
    return section_container('Class Balance', content, level=2)
 