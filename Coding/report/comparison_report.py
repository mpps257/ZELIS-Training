"""
Comparison report generator for versioned EDA reports.
"""
import pandas as pd
from datetime import datetime
def comparison_section(comparison, version1_info, version2_info):
    """
    Generate a comparison section showing differences between two versions.
    
    Args:
        comparison: Comparison dict from VersionManager.compare_versions()
        version1_info: Full version info dict for version 1
        version2_info: Full version info dict for version 2
    """
    v1_id = comparison['version1']
    v2_id = comparison['version2']
    v1_time = datetime.fromisoformat(comparison['timestamp1']).strftime('%Y-%m-%d %H:%M:%S')
    v2_time = datetime.fromisoformat(comparison['timestamp2']).strftime('%Y-%m-%d %H:%M:%S')
    
    content = []
    
    # Header
    content.append("## Version Comparison\n\n")
    content.append(f"**Version 1:** {v1_id} ({v1_time})\n")
    content.append(f"**Version 2:** {v2_id} ({v2_time})\n\n")
    
    # Quality Score Comparison
    q1 = comparison['quality_score1']
    q2 = comparison['quality_score2']
    q_diff = comparison['quality_diff']
    better = comparison['better_version']
    
    content.append("### Quality Score Comparison\n\n")
    content.append(f"| Metric | Version 1 | Version 2 | Difference |\n")
    content.append(f"|--------|-----------|-----------|------------|\n")
    content.append(f"| **Quality Score** | {q1:.2f}/100 | {q2:.2f}/100 | {q_diff:+.2f} |\n\n")
    
    if better == 'version2':
        content.append(f"✅ **Version 2 has better data quality** (score: {q2:.2f} vs {q1:.2f})\n\n")
    elif better == 'version1':
        content.append(f"✅ **Version 1 has better data quality** (score: {q1:.2f} vs {q2:.2f})\n\n")
    else:
        content.append(f"⚖️ **Both versions have similar quality** (score: {q1:.2f})\n\n")
    
    # Shape Comparison
    if comparison['shape_changed']:
        s1 = comparison['shape1']
        s2 = comparison['shape2']
        content.append("### Dataset Shape Changes\n\n")
        content.append(f"- **Version 1:** {s1[0]} rows × {s1[1]} columns\n")
        content.append(f"- **Version 2:** {s2[0]} rows × {s2[1]} columns\n")
        content.append(f"- **Change:** {s2[0]-s1[0]:+d} rows, {s2[1]-s1[1]:+d} columns\n\n")
    else:
        content.append("### Dataset Shape\n\n")
        s1 = comparison['shape1']
        content.append(f"- **No change:** {s1[0]} rows × {s1[1]} columns\n\n")
    
    # Column Changes
    cols_added = comparison['columns_added']
    cols_removed = comparison['columns_removed']
    
    if cols_added or cols_removed:
        content.append("### Column Changes\n\n")
        if cols_added:
            content.append(f"**Added columns ({len(cols_added)}):**\n")
            for col in sorted(cols_added):
                content.append(f"- ✅ {col}\n")
            content.append("\n")
        if cols_removed:
            content.append(f"**Removed columns ({len(cols_removed)}):**\n")
            for col in sorted(cols_removed):
                content.append(f"- ❌ {col}\n")
            content.append("\n")
    else:
        content.append("### Column Changes\n\n")
        content.append("- **No column changes** (same columns in both versions)\n\n")
    
    # Missing Data Comparison
    miss1 = comparison['missing_pct1']
    miss2 = comparison['missing_pct2']
    miss_diff = comparison['missing_diff']
    
    content.append("### Missing Data Comparison\n\n")
    content.append(f"| Version | Missing % |\n")
    content.append(f"|---------|----------|\n")
    content.append(f"| Version 1 | {miss1:.2f}% |\n")
    content.append(f"| Version 2 | {miss2:.2f}% |\n")
    content.append(f"| **Change** | **{miss_diff:+.2f}%** |\n\n")
    
    if miss_diff < 0:
        content.append(f"✅ **Improvement:** Missing data decreased by {abs(miss_diff):.2f}%\n\n")
    elif miss_diff > 0:
        content.append(f"⚠️ **Warning:** Missing data increased by {miss_diff:.2f}%\n\n")
    else:
        content.append("➡️ **No change** in missing data percentage\n\n")
    
    # Quality Breakdown Comparison
    if 'quality_breakdown' in version1_info and 'quality_breakdown' in version2_info:
        content.append("### Quality Breakdown Comparison\n\n")
        content.append("| Component | Version 1 | Version 2 | Difference |\n")
        content.append("|-----------|-----------|-----------|------------|\n")
        
        breakdown1 = version1_info['quality_breakdown']
        breakdown2 = version2_info['quality_breakdown']
        
        components = ['completeness', 'consistency', 'distribution', 'balance', 'correlation']
        for comp in components:
            if comp in breakdown1 and comp in breakdown2:
                s1 = breakdown1[comp].get('score', 0)
                s2 = breakdown2[comp].get('score', 0)
                diff = s2 - s1
                content.append(f"| {comp.capitalize()} | {s1:.2f} | {s2:.2f} | {diff:+.2f} |\n")
        
        content.append("\n")
    
    # Duplicate Detection
    if comparison['is_duplicate']:
        content.append("⚠️ **Note:** These versions appear to have identical data (same hash).\n\n")
    
    # Recommendations
    content.append("### Recommendations\n\n")
    if better == 'version2':
        content.append(f"- ✅ **Use Version 2** ({v2_id}) - Higher quality score\n")
        content.append(f"- Consider investigating improvements in Version 2\n")
    elif better == 'version1':
        content.append(f"- ✅ **Use Version 1** ({v1_id}) - Higher quality score\n")
        content.append(f"- Consider reverting to Version 1 or investigating what changed\n")
    else:
        content.append("- Both versions have similar quality\n")
        content.append("- Choose based on other factors (timeliness, completeness, etc.)\n")
    
    content.append("\n---\n")
    
    return ''.join(content)

def detailed_comparison_section(prev_analysis, curr_analysis, prev_version_info, curr_version_info):
    """
    Generate detailed comparison section with stats, distribution, correlation, and feature usefulness.
    
    Args:
        prev_analysis: Analysis results dict from previous version
        curr_analysis: Analysis results dict from current version
        prev_version_info: Version info dict for previous version
        curr_version_info: Version info dict for current version
    """
    if not prev_analysis or not curr_analysis:
        return ""
    
    import pandas as pd
    content = []
    
    content.append("## 📊 Detailed Version Comparison\n\n")
    content.append(f"**Previous Version:** {prev_version_info['version_id']}\n")
    content.append(f"**Current Version:** {curr_version_info['version_id']}\n\n")
    
    # 1. Statistical Comparison for Numeric Columns
    prev_numeric = prev_analysis.get('numeric_df', pd.DataFrame())
    curr_numeric = curr_analysis.get('numeric_df', pd.DataFrame())
    
    # Ensure they are DataFrames
    if not isinstance(prev_numeric, pd.DataFrame):
        prev_numeric = pd.DataFrame(prev_numeric) if prev_numeric else pd.DataFrame()
    if not isinstance(curr_numeric, pd.DataFrame):
        curr_numeric = pd.DataFrame(curr_numeric) if curr_numeric else pd.DataFrame()
    
    if not prev_numeric.empty and not curr_numeric.empty and 'column' in prev_numeric.columns and 'column' in curr_numeric.columns:
        content.append("### 📈 Statistical Comparison (Numeric Columns)\n\n")
        
        # Find common columns
        prev_cols = set(prev_numeric['column'].values) if 'column' in prev_numeric.columns else set()
        curr_cols = set(curr_numeric['column'].values) if 'column' in curr_numeric.columns else set()
        common_cols = prev_cols & curr_cols
        
        if common_cols:
            content.append("| Column | Metric | Previous | Current | Change |\n")
            content.append("|--------|--------|----------|---------|--------|\n")
            
            for col in sorted(common_cols):
                prev_row = prev_numeric[prev_numeric['column'] == col].iloc[0] if len(prev_numeric[prev_numeric['column'] == col]) > 0 else None
                curr_row = curr_numeric[curr_numeric['column'] == col].iloc[0] if len(curr_numeric[curr_numeric['column'] == col]) > 0 else None
                
                if prev_row is not None and curr_row is not None:
                    metrics = ['mean', 'median', 'std', 'min', 'max']
                    for metric in metrics:
                        if metric in prev_row and metric in curr_row:
                            prev_val = prev_row[metric]
                            curr_val = curr_row[metric]
                            if pd.notna(prev_val) and pd.notna(curr_val):
                                change = curr_val - prev_val
                                pct_change = (change / prev_val * 100) if prev_val != 0 else 0
                                content.append(f"| {col} | {metric.capitalize()} | {prev_val:.2f} | {curr_val:.2f} | {change:+.2f} ({pct_change:+.1f}%) |\n")
            
            content.append("\n")
# 2. Distribution Comparison
    if not prev_numeric.empty and not curr_numeric.empty and common_cols:
        content.append("### 📉 Distribution Comparison\n\n")
        content.append("| Column | Metric | Previous | Current | Change |\n")
        content.append("|--------|--------|----------|---------|--------|\n")
        
        for col in sorted(common_cols):
            prev_row = prev_numeric[prev_numeric['column'] == col].iloc[0] if len(prev_numeric[prev_numeric['column'] == col]) > 0 else None
            curr_row = curr_numeric[curr_numeric['column'] == col].iloc[0] if len(curr_numeric[curr_numeric['column'] == col]) > 0 else None
            
            if prev_row is not None and curr_row is not None:
                dist_metrics = ['skewness', 'kurtosis']
                for metric in dist_metrics:
                    if metric in prev_row and metric in curr_row:
                        prev_val = prev_row[metric]
                        curr_val = curr_row[metric]
                        if pd.notna(prev_val) and pd.notna(curr_val):
                            change = curr_val - prev_val
                            content.append(f"| {col} | {metric.capitalize()} | {prev_val:.2f} | {curr_val:.2f} | {change:+.2f} |\n")
                
                # Outlier comparison
                if 'outliers' in prev_row and 'outliers' in curr_row and 'count' in prev_row and 'count' in curr_row:
                    prev_outlier_pct = (prev_row['outliers'] / prev_row['count'] * 100) if prev_row['count'] > 0 else 0
                    curr_outlier_pct = (curr_row['outliers'] / curr_row['count'] * 100) if curr_row['count'] > 0 else 0
                    change = curr_outlier_pct - prev_outlier_pct
                    content.append(f"| {col} | Outlier % | {prev_outlier_pct:.2f}% | {curr_outlier_pct:.2f}% | {change:+.2f}% |\n")
        
        content.append("\n")
    
    # 3. Correlation Comparison
    prev_corrs = prev_analysis.get('corrs', {}).get('pearson', pd.DataFrame())
    curr_corrs = curr_analysis.get('corrs', {}).get('pearson', pd.DataFrame())
    
    if not prev_corrs.empty and not curr_corrs.empty:
        content.append("### 🔗 Correlation Comparison\n\n")
        
        # Find common column pairs
        prev_pairs = set()
        for col1 in prev_corrs.columns:
            for col2 in prev_corrs.index:
                if col1 != col2:
                    prev_pairs.add(tuple(sorted([str(col1), str(col2)])))
        
        curr_pairs = set()
        for col1 in curr_corrs.columns:
            for col2 in curr_corrs.index:
                if col1 != col2:
                    curr_pairs.add(tuple(sorted([str(col1), str(col2)])))
        
        common_pairs = prev_pairs & curr_pairs
        
        if common_pairs:
            content.append("| Column Pair | Previous Correlation | Current Correlation | Change |\n")
            content.append("|-------------|---------------------|---------------------|--------|\n")
            
            significant_changes = []
            for pair in sorted(common_pairs)[:20]:  # Limit to top 20
                col1, col2 = pair
                try:
                    prev_corr = prev_corrs.loc[col1, col2] if col1 in prev_corrs.index and col2 in prev_corrs.columns else prev_corrs.loc[col2, col1]
                    curr_corr = curr_corrs.loc[col1, col2] if col1 in curr_corrs.index and col2 in curr_corrs.columns else curr_corrs.loc[col2, col1]
                    
                    if pd.notna(prev_corr) and pd.notna(curr_corr):
                        change = curr_corr - prev_corr
                        if abs(change) > 0.1:  # Significant change
                            significant_changes.append((pair, prev_corr, curr_corr, change))
                        content.append(f"| {col1} ↔ {col2} | {prev_corr:.3f} | {curr_corr:.3f} | {change:+.3f} |\n")
                except:
                    pass
            
            if significant_changes:
                content.append("\n**⚠️ Significant Correlation Changes (>0.1):**\n")
                for pair, prev, curr, change in significant_changes[:5]:
                    content.append(f"- {pair[0]} ↔ {pair[1]}: {prev:.3f} → {curr:.3f} ({change:+.3f})\n")
            
            content.append("\n")
    
    # 4. Feature Usefulness Comparison
    content.append("### 🎯 Feature Usefulness Comparison\n\n")
    content.append("| Column | Previous Score | Current Score | Change | Status |\n")
    content.append("|--------|---------------|---------------|--------|--------|\n")
    
    # Calculate feature usefulness scores
    def calc_feature_score(col, numeric_df, categorical_df, missing_df, corrs):
        score = 50  # Base score
        
        # Check missingness
        if not missing_df.empty and col in missing_df['column'].values:
            miss_row = missing_df[missing_df['column'] == col]
            if len(miss_row) > 0:
                miss_pct = miss_row.iloc[0].get('missing_pct', 0)
                score -= (miss_pct / 100) * 30  # Penalty for missing data
        
        # Check variance (for numeric) or cardinality (for categorical)
        if not numeric_df.empty and col in numeric_df['column'].values:
            num_row = numeric_df[numeric_df['column'] == col]
            if len(num_row) > 0:
                std_val = num_row.iloc[0].get('std', 0)
                mean_val = num_row.iloc[0].get('mean', 1)
                if mean_val != 0:
                    cv = std_val / abs(mean_val)  # Coefficient of variation
                    score += min(20, cv * 10)  # Reward for variance
        elif not categorical_df.empty and col in categorical_df['column'].values:
            cat_row = categorical_df[categorical_df['column'] == col]
            if len(cat_row) > 0:
                unique_count = cat_row.iloc[0].get('unique', 0)
                # Moderate cardinality is good (not too low, not too high)
                if 2 <= unique_count <= 20:
                    score += 15
                elif unique_count > 20:
                    score += 5
        
        # Check correlation (high correlation with many features = useful)
        if not corrs.empty:
            try:
                if col in corrs.columns or col in corrs.index:
                    corr_vals = []
                    if col in corrs.columns:
                        corr_vals.extend([abs(v) for v in corrs[col].values if pd.notna(v) and v != 1.0])
                    if col in corrs.index:
                        corr_vals.extend([abs(v) for v in corrs.loc[col].values if pd.notna(v) and v != 1.0])
                    
                    if corr_vals:
                        avg_corr = sum(corr_vals) / len(corr_vals)
                        score += min(15, avg_corr * 20)  # Reward for correlations
            except:
                pass
        
        return max(0, min(100, score))
    
    # Get all columns from both versions
    all_cols = set()
    if 'columns' in prev_version_info:
        all_cols.update(prev_version_info['columns'])
    if 'columns' in curr_version_info:
        all_cols.update(curr_version_info['columns'])
    
    for col in sorted(all_cols):
        prev_score = calc_feature_score(col, prev_analysis.get('numeric_df', pd.DataFrame()),
                                       prev_analysis.get('categorical_df', pd.DataFrame()),
                                       prev_analysis.get('missing_df', pd.DataFrame()),
                                       prev_analysis.get('corrs', {}).get('pearson', pd.DataFrame()))
        
        curr_score = calc_feature_score(col, curr_analysis.get('numeric_df', pd.DataFrame()),
                                       curr_analysis.get('categorical_df', pd.DataFrame()),
                                       curr_analysis.get('missing_df', pd.DataFrame()),
                                       curr_analysis.get('corrs', {}).get('pearson', pd.DataFrame()))
        
        change = curr_score - prev_score
        status = "✅ Improved" if change > 5 else "⚠️ Declined" if change < -5 else "➡️ Stable"
        content.append(f"| {col} | {prev_score:.1f} | {curr_score:.1f} | {change:+.1f} | {status} |\n")
    
    content.append("\n---\n")
    
    return ''.join(content)
 
 
def version_history_section(versions, source_name):
    """
    Generate a section showing version history.
    
    Args:
        versions: List of version info dicts
        source_name: Name of the data source
    """
    if not versions:
        return ""
    
    content = []
    content.append("## Version History\n\n")
    content.append(f"**Data Source:** {source_name}\n\n")
    content.append("| Version ID | Timestamp | Quality Score | Shape | Missing % |\n")
    content.append("|------------|-----------|---------------|-------|----------|\n")
    
    for v in versions[:10]:  # Show last 10 versions
        v_id = v['version_id']
        timestamp = datetime.fromisoformat(v['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        score = v.get('quality_score', 0)
        shape = f"{v['shape'][0]}×{v['shape'][1]}"
        missing = v.get('missing_pct', 0)
        content.append(f"| {v_id} | {timestamp} | {score:.2f}/100 | {shape} | {missing:.2f}% |\n")
    
    if len(versions) > 10:
        content.append(f"\n*Showing 10 most recent versions (total: {len(versions)})\n")
    
    content.append("\n---\n")
    
    return ''.join(content)
def best_version_section(best_version, source_name):
        """
        Generate a section highlighting the best version.
        
        Args:
            best_version: Version info dict with highest quality score
            source_name: Name of the data source
        """
        if not best_version:
            return ""
        
        content = []
        content.append("## 🏆 Best Version\n\n")
        content.append(f"**Best Quality Version:** {best_version['version_id']}\n\n")
        content.append(f"- **Quality Score:** {best_version.get('quality_score', 0):.2f}/100\n")
        content.append(f"- **Timestamp:** {datetime.fromisoformat(best_version['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}\n")
        content.append(f"- **Shape:** {best_version['shape'][0]} rows × {best_version['shape'][1]} columns\n")
        content.append(f"- **Missing Data:** {best_version.get('missing_pct', 0):.2f}%\n\n")
        
        if 'quality_breakdown' in best_version:
            breakdown = best_version['quality_breakdown']
            if 'total' in breakdown:
                grade = breakdown['total'].get('grade', 'N/A')
                content.append(f"- **Grade:** {grade}\n\n")
        
        content.append("---\n")
        
        return ''.join(content)
    