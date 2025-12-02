import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path
 
 
def _dynamic_figsize(count, base=(5, 3), scale=(0.3, 0.15), min_size=(4, 2.2), max_size=(14, 7)):
    """Utility to compute dynamic figsize based on element count."""
    width = max(min_size[0], min(max_size[0], base[0] + count * scale[0]))
    height = max(min_size[1], min(max_size[1], base[1] + count * scale[1]))
    return (width, height)
 
 
def _compute_axis_limits(values, pad_ratio=0.08, hard_min=None, hard_max=None):
    """Compute dynamic y-limits given iterable of values."""
    arr = np.array(values, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return hard_min, hard_max
    vmin = arr.min()
    vmax = arr.max()
    if vmin == vmax:
        pad = max(1.0, abs(vmin) * 0.1 + 1)
        vmin -= pad
        vmax += pad
    else:
        pad = max(0.5, (vmax - vmin) * pad_ratio)
        vmin -= pad
        vmax += pad
    if hard_min is not None:
        vmin = max(hard_min, vmin)
    if hard_max is not None:
        vmax = min(hard_max, vmax)
    return vmin, vmax
 
 
def plot_histogram(series, out_path):
    clean = series.dropna()
    if clean.empty:
        return
    bins = min(50, max(10, int(np.sqrt(len(clean)))))
    fig_w, fig_h = _dynamic_figsize(len(clean) // 500 + 1, base=(5, 3), scale=(0.4, 0.05))
    plt.figure(figsize=(fig_w, fig_h))
    plt.hist(clean, bins=bins, color='#6fa6e6', edgecolor='white')
    plt.title(f"Histogram: {series.name}")
    plt.xlabel(series.name)
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
 
 
def plot_boxplot(series, out_path):
    clean = series.dropna()
    if clean.empty:
        return
    fig_w, fig_h = _dynamic_figsize(len(clean) // 1000 + 1, base=(4.5, 2.6), scale=(0.2, 0.05))
    plt.figure(figsize=(fig_w, fig_h))
    sns.boxplot(x=clean, color='#7ed6a2')
    plt.title(f"Boxplot: {series.name}")
    plt.xlabel(series.name)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
 
 
def plot_bar(series, out_path, max_cats=20):
    vc = series.value_counts().iloc[:max_cats]
    if vc.empty:
        return
    fig_w, fig_h = _dynamic_figsize(len(vc), base=(5.5, 3), scale=(0.35, 0.07))
    plt.figure(figsize=(fig_w, fig_h))
    sns.barplot(x=vc.index.astype(str), y=vc.values, palette='muted')
    plt.title(f"Bar Chart: {series.name}")
    plt.ylabel('Count')
    plt.xlabel(series.name)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
 
 
def plot_missingness_heatmap(df, out_path):
    if df.empty:
        return
    fig_w = max(6, min(18, df.shape[1] * 0.4 + 4))
    fig_h = max(2.5, min(10, df.shape[0] / 400 + 2.5))
    plt.figure(figsize=(fig_w, fig_h))
    sns.heatmap(df.isnull(), cbar=False, cmap='Reds', yticklabels=False)
    plt.title('Missingness Heatmap')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
 
 
def plot_corr_heatmap(corr_df, out_path):
    if corr_df.empty:
        return
    cols = len(corr_df.columns)
    fig_w = max(4.5, min(18, 3 + cols * 0.4))
    fig_h = max(4, min(18, 3 + cols * 0.3))
    plt.figure(figsize=(fig_w, fig_h))
    sns.heatmap(corr_df, annot=cols <= 15, fmt='.2f', cmap='vlag', square=False)
    plt.title('Correlation Heatmap')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
 
 
def _ensure_parent_dir(path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
 
 
def plot_quality_trend(versions, out_path, max_points=12):
    """Plot quality score trend across versions."""
    if not versions:
        return False
    # Versions are stored newest-first; reverse to chronological
    sorted_versions = sorted(versions[:max_points], key=lambda v: v['timestamp'])
    scores = [v.get('quality_score', 0) for v in sorted_versions]
    timestamps = [pd.to_datetime(v['timestamp']) for v in sorted_versions]
    if len(scores) < 2:
        return False
    fig_w = max(5.5, min(16, 4 + len(scores) * 0.6))
    plt.figure(figsize=(fig_w, 3.5))
    plt.plot(timestamps, scores, marker='o', color='#4a90e2')
    plt.fill_between(timestamps, scores, alpha=0.15, color='#4a90e2')
    y_min, y_max = _compute_axis_limits(scores, hard_min=0, hard_max=100)
    if y_min is not None and y_max is not None:
        plt.ylim(y_min, y_max)
    plt.ylabel('Quality Score (0-100)')
    plt.xlabel('Version Timestamp')
    plt.title('Quality Score Trend')
    plt.grid(alpha=0.3)
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    _ensure_parent_dir(out_path)
    plt.savefig(out_path)
    plt.close()
    return True
 
 
def plot_missingness_comparison(prev_missing, curr_missing, out_path, top_n=15):
    """Plot missingness percentage changes between two versions."""
    if prev_missing is None or curr_missing is None or prev_missing.empty or curr_missing.empty:
        return False
    cols = {'column', 'missing_pct'}
    if not cols.issubset(prev_missing.columns) or not cols.issubset(curr_missing.columns):
        return False
    merged = prev_missing[['column', 'missing_pct']].rename(columns={'missing_pct': 'prev'})
    merged = merged.merge(curr_missing[['column', 'missing_pct']].rename(columns={'missing_pct': 'curr'}),
                          on='column', how='inner')
    if merged.empty:
        return False
    merged['diff'] = merged['curr'] - merged['prev']
    merged['abs_diff'] = merged['diff'].abs()
    merged = merged.sort_values('abs_diff', ascending=False).head(top_n)
    if merged['abs_diff'].max() < 0.1:
        return False
    fig_w = max(6, min(18, 4 + len(merged) * 0.4))
    plt.figure(figsize=(fig_w, 3.5))
    idx = np.arange(len(merged))
    width = 0.35
    plt.bar(idx - width/2, merged['prev'], width, label='Previous', color='#b0c4de')
    plt.bar(idx + width/2, merged['curr'], width, label='Current', color='#6fa6e6')
    plt.xticks(idx, merged['column'], rotation=45, ha='right')
    y_min, y_max = _compute_axis_limits(
        merged[['prev', 'curr']].values.flatten(),
        hard_min=0,
        hard_max=100,
    )
    if y_min is not None and y_max is not None:
        plt.ylim(y_min, y_max)
    plt.ylabel('Missing %')
    plt.title('Missingness Comparison (Top Changes)')
    plt.legend()
    plt.tight_layout()
    _ensure_parent_dir(out_path)
    plt.savefig(out_path)
    plt.close()
    return True
def plot_numeric_stat_change(prev_numeric, curr_numeric, out_path, stat='mean', top_n=12):
    """Plot change in numeric column statistics between two versions."""
    if prev_numeric is None or curr_numeric is None or prev_numeric.empty or curr_numeric.empty:
        return False
    if 'column' not in prev_numeric.columns or stat not in prev_numeric.columns:
        return False
    if stat not in curr_numeric.columns:
        return False
    merged = prev_numeric[['column', stat]].rename(columns={stat: 'prev'})
    merged = merged.merge(curr_numeric[['column', stat]].rename(columns={stat: 'curr'}),
                          on='column', how='inner')
    if merged.empty:
        return False
    merged['diff'] = merged['curr'] - merged['prev']
    merged['abs_diff'] = merged['diff'].abs()
    merged = merged.sort_values('abs_diff', ascending=False).head(top_n)
    if merged['abs_diff'].max() == 0:
        return False
    fig_w = max(5.5, min(18, 4 + len(merged) * 0.45))
    plt.figure(figsize=(fig_w, 3.4))
    sns.barplot(x='column', y='diff', data=merged, palette='coolwarm')
    plt.axhline(0, color='black', linewidth=0.8)
    plt.ylabel(f'{stat.capitalize()} Change')
    plt.title(f'Top {stat.capitalize()} Changes (Current - Previous)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    _ensure_parent_dir(out_path)
    plt.savefig(out_path)
    plt.close()
    return True
 
 
def plot_correlation_change(prev_corr, curr_corr, out_path, top_cols=10):
    """Plot heatmap of correlation changes for overlapping numeric columns."""
    if prev_corr is None or curr_corr is None or prev_corr.empty or curr_corr.empty:
        return False
    common_cols = prev_corr.columns.intersection(curr_corr.columns)
    if len(common_cols) < 2:
        return False
    diff = (curr_corr.loc[common_cols, common_cols] - prev_corr.loc[common_cols, common_cols]).abs()
    if diff.empty:
        return False
    col_scores = diff.sum().sort_values(ascending=False).head(top_cols)
    focus_cols = col_scores.index
    diff_focus = curr_corr.loc[focus_cols, focus_cols] - prev_corr.loc[focus_cols, focus_cols]
    fig_w = max(5, min(18, 3 + len(focus_cols) * 0.5))
    fig_h = max(4, min(18, 3 + len(focus_cols) * 0.4))
    plt.figure(figsize=(fig_w, fig_h))
    sns.heatmap(diff_focus, cmap='coolwarm', center=0, annot=len(focus_cols) <= 12, fmt='.2f')
    plt.title('Correlation Change (Current - Previous)')
    plt.tight_layout()
    _ensure_parent_dir(out_path)
    plt.savefig(out_path)
    plt.close()
    return True
 