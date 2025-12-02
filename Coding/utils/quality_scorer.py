"""
Data quality scoring system.
Computes a quality score (0-100) based on various data quality metrics.
"""
import pandas as pd
import numpy as np
 
 
def compute_quality_score(df, numeric_df, categorical_df, missing_df, missing_overall, corrs):
    """
    Compute an overall data quality score (0-100) for the dataset.
    
    Args:
        df: Original dataframe
        numeric_df: Results from numeric analysis
        categorical_df: Results from categorical analysis
        missing_df: Results from missingness analysis
        missing_overall: Overall missingness stats
        corrs: Correlation results
        
    Returns:
        Dict with 'score' (0-100) and 'breakdown' of component scores
    """
    breakdown = {}
    
    # 1. Completeness Score (0-30 points)
    # Based on missing data percentage
    total_missing_pct = missing_overall.get('total_missing_pct', 0)
    completeness_score = max(0, 30 * (1 - total_missing_pct / 100))
    breakdown['completeness'] = {
        'score': completeness_score,
        'max': 30,
        'missing_pct': total_missing_pct,
        'reason': f"{total_missing_pct:.1f}% of data is missing"
    }
    
    # 2. Data Consistency Score (0-25 points)
    # Based on mixed types, label inconsistencies, etc.
    consistency_score = 25
    issues = []
    
    # Check for mixed types in categorical analysis
    if not categorical_df.empty:
        mixed_type_cols = categorical_df[categorical_df.get('has_mixed_types', False) == True]
        if not mixed_type_cols.empty:
            penalty = min(10, len(mixed_type_cols) * 2)
            consistency_score -= penalty
            issues.append(f"{len(mixed_type_cols)} columns with mixed data types")
        
        # Check for label inconsistencies
        inconsistent_cols = categorical_df[categorical_df.get('label_inconsistency', False) == True]
        if not inconsistent_cols.empty:
            penalty = min(5, len(inconsistent_cols))
            consistency_score -= penalty
            issues.append(f"{len(inconsistent_cols)} columns with label inconsistencies")
    
    consistency_score = max(0, consistency_score)
    breakdown['consistency'] = {
        'score': consistency_score,
        'max': 25,
        'issues': issues if issues else ['No consistency issues detected']
    }
    
    # 3. Data Distribution Score (0-20 points)
    # Based on skewness, outliers, normality
    distribution_score = 20
    dist_issues = []
    
    if not numeric_df.empty:
        # High skewness penalty
        high_skew = numeric_df[abs(numeric_df['skewness']) > 2]
        if not high_skew.empty:
            penalty = min(5, len(high_skew) * 0.5)
            distribution_score -= penalty
            dist_issues.append(f"{len(high_skew)} columns with high skewness")
        
        # High outlier percentage penalty
        for _, row in numeric_df.iterrows():
            outlier_pct = (row.get('outliers', 0) / row.get('count', 1)) * 100
            if outlier_pct > 10:
                penalty = min(3, outlier_pct / 10)
                distribution_score -= penalty
        if dist_issues:
            dist_issues.append("High outlier percentages detected")
        
        # Non-normality (less severe penalty)
        non_normal = numeric_df[numeric_df.get('shapiro_p', 1) < 0.05]
        if not non_normal.empty and len(non_normal) > len(numeric_df) * 0.5:
            distribution_score -= 2
            dist_issues.append("Many columns are non-normal")
    
    distribution_score = max(0, distribution_score)
    breakdown['distribution'] = {
        'score': distribution_score,
        'max': 20,
        'issues': dist_issues if dist_issues else ['Distribution looks good']
    }
    
    # 4. Class Balance Score (0-15 points)
    # Based on categorical imbalance
    balance_score = 15
    balance_issues = []
    
    if not categorical_df.empty:
        imbalanced = categorical_df[categorical_df.get('max_imbalance', 0) > 0.7]
        if not imbalanced.empty:
            penalty = min(10, len(imbalanced) * 2)
            balance_score -= penalty
            balance_issues.append(f"{len(imbalanced)} highly imbalanced columns")
    
    balance_score = max(0, balance_score)
    breakdown['balance'] = {
        'score': balance_score,
        'max': 15,
        'issues': balance_issues if balance_issues else ['Classes are well balanced']
    }
    
    # 5. Correlation/Multicollinearity Score (0-10 points)
    # Penalty for high multicollinearity
    correlation_score = 10
    corr_issues = []
    
    if 'suggestions' in corrs:
        high_corr_count = len([s for s in corrs['suggestions'] if 'multicollinearity' in s.lower() or 'correlated' in s.lower()])
        if high_corr_count > 0:
            penalty = min(5, high_corr_count)
            correlation_score -= penalty
            corr_issues.append(f"{high_corr_count} multicollinearity issues")
    
    correlation_score = max(0, correlation_score)
    breakdown['correlation'] = {
        'score': correlation_score,
        'max': 10,
        'issues': corr_issues if corr_issues else ['No multicollinearity issues']
    }
    
    # Total score
    total_score = (
        completeness_score +
        consistency_score +
        distribution_score +
        balance_score +
        correlation_score
    )
    
    breakdown['total'] = {
        'score': total_score,
        'max': 100,
        'grade': _score_to_grade(total_score)
    }
    
    return {
        'score': round(total_score, 2),
        'breakdown': breakdown
    }
 
 
def _score_to_grade(score):
    """Convert numeric score to letter grade."""
    if score >= 90:
        return 'A (Excellent)'
    elif score >= 80:
        return 'B (Good)'
    elif score >= 70:
        return 'C (Fair)'
    elif score >= 60:
        return 'D (Poor)'
    else:
        return 'F (Very Poor)'
 