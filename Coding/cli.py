import click
from utils.io import load_table
from analyzers.numeric import analyze_numeric
from analyzers.categorical import analyze_categorical
from analyzers.missingness import analyze_missingness
from analyzers.correlation import analyze_correlation
from templates.narrative import numeric_narrative, categorical_narrative, missingness_narrative, correlation_narrative
from report.markdown_report import (overview_section, sample_records_section, numeric_section, categorical_section, missingness_section, correlation_section, class_balance_section)
from report.html_report import html_report
from report.comparison_report import comparison_section, detailed_comparison_section, version_history_section, best_version_section
from utils.plots import (
    plot_histogram,
    plot_boxplot,
    plot_bar,
    plot_missingness_heatmap,
    plot_corr_heatmap,
    plot_quality_trend,
    plot_missingness_comparison,
    plot_numeric_stat_change,
    plot_correlation_change,
)
from utils.versioning import VersionManager
from utils.quality_scorer import compute_quality_score
import os
 
@click.command()
@click.argument('source', type=str)
@click.option('--output-dir', '-o', default=None, help='Optional output directory (default: saves to .eda_versions/)')
@click.option('--target', type=str, default=None, help='(Optional) Target/class column for class balance analysis')
@click.option('--version-storage', default='.eda_versions', help='Directory for version storage (default: .eda_versions)')
@click.option('--no-version', is_flag=True, help='Disable versioning and use output-dir only')
def main(source, output_dir, target, version_storage, no_version):
    """Run EDA report on a data SOURCE (csv, excel, parquet, or url)"""
    try:
        df = load_table(source)
    except Exception as e:
        click.secho(f"Error loading data: {e}", fg='red')
        return
    click.secho(f"Loaded data with shape {df.shape}", fg='green')
    
    # Initialize version manager
    version_manager = None
    if not no_version:
        version_manager = VersionManager(storage_dir=version_storage)
    
    # Extract source name for versioning
    if not source.startswith('http'):
        source_name = os.path.splitext(os.path.basename(source))[0]
    else:
        source_name = source.split('/')[-1].split('?')[0] or 'Remote Dataset'
        source_name = os.path.splitext(source_name)[0] or 'Remote Dataset'
    
    if not source_name or source_name == source:
        source_name = 'Dataset'
    
    # Determine output directory - use versioning storage by default
    version_id = None
    if output_dir is None and not no_version:
        # Create version directory path
        from datetime import datetime
        version_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        version_key = f"{source_name}_{version_id}"
        output_dir = str(version_manager.versions_dir / version_key)
        os.makedirs(output_dir, exist_ok=True)
        click.secho(f"Output will be saved to versioned storage: {output_dir}", fg='cyan')
    elif output_dir is None:
        output_dir = 'reports/'
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
 
    # ANALYSIS
    numeric_df = analyze_numeric(df)
    categorical_df = analyze_categorical(df)
    missing_df, missing_overall = analyze_missingness(df)
    corrs = analyze_correlation(df)
 
    # Class balance
    class_balance_section_md = ''
    if target and target in df.columns:
        out_path = os.path.join(output_dir, 'figs', f'{target}_class_dist.png')
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        plot_bar(df[target], out_path, max_cats=30)
        rel_path = os.path.relpath(out_path, output_dir).replace('\\', '/')
        class_balance_section_md = class_balance_section(df[target], rel_path)
 
    # PLOT OUT DIR
    plotdir = os.path.join(output_dir, 'figs')
    os.makedirs(plotdir, exist_ok=True)
 
    # PLOTS: NUMERIC
    numeric_plots = {}
    for _, row in numeric_df.iterrows():
        col = row['column']
        s = df[col]
        hist_path = os.path.join(plotdir, f'{col}_hist.png')
        box_path = os.path.join(plotdir, f'{col}_box.png')
        plot_histogram(s, hist_path)
        plot_boxplot(s, box_path)
        numeric_plots[col] = {'histogram': hist_path, 'boxplot': box_path}
 
    # PLOTS: CATEGORICAL
    categorical_plots = {}
    for _, row in categorical_df.iterrows():
        col = row['column']
        s = df[col].astype(str)
        bar_path = os.path.join(plotdir, f'{col}_bar.png')
        plot_bar(s, bar_path)
        categorical_plots[col] = {'bar': bar_path}
 
    # PLOTS: MISSINGNESS
    missmap_path = os.path.join(plotdir, 'missingness_heatmap.png')
    plot_missingness_heatmap(df, missmap_path)
 
    # PLOTS: CORRELATION
    corrplot_path = os.path.join(plotdir, 'correlation_heatmap.png')
    if not corrs['pearson'].empty:
        plot_corr_heatmap(corrs['pearson'], corrplot_path)
 
    # NARRATIVES (now lists of lines per col)
    num_narr = {row['column']: numeric_narrative(row) for _, row in numeric_df.iterrows()} if not numeric_df.empty else {}
    cat_narr = {row['column']: categorical_narrative(row) for _, row in categorical_df.iterrows()} if not categorical_df.empty else {}
    miss_narr = {row['column']: missingness_narrative(row) for _, row in missing_df.iterrows()} if not missing_df.empty else {}
    # Filter out columns with no missing data from narratives
    miss_narr = {col: narr for col, narr in miss_narr.items() if narr}  # Only keep columns with non-empty narratives
 
    corr_narr = []
    if 'pearson' in corrs:
        for c1 in corrs['pearson'].columns:
            for c2 in corrs['pearson'].index:
                if c1 < c2:
                    narrs = correlation_narrative(c1, c2, corrs['pearson'].loc[c1, c2], 'pearson')
                    if narrs: corr_narr.extend(narrs)
    if 'categorical' in corrs:
        for c1 in corrs['categorical'].columns:
            for c2 in corrs['categorical'].index:
                if c1 < c2:
                    narrs = correlation_narrative(c1, c2, corrs['categorical'].loc[c1, c2], 'cramers_v')
                    if narrs: corr_narr.extend(narrs)
 
    # Filter missing_df to only show columns with missing data
    missing_df_filtered = missing_df[missing_df['missing'] > 0] if not missing_df.empty else missing_df
    
    # Check if there's a previous version (for adding comparison link)
    has_previous_version = False
    if version_manager:
        prev_check = version_manager.get_latest_version(source_name)
        has_previous_version = prev_check is not None
    
    # REPORT GENERATION
    out_md = (
        overview_section(df)
        + sample_records_section(df)
        + (class_balance_section_md or '')
        + numeric_section(numeric_df, num_narr)
        + categorical_section(categorical_df, cat_narr)
        + missingness_section(missing_df_filtered, miss_narr)
        + correlation_section(corrs, corr_narr)
    )
    
    # Add note about comparison report if versioning is enabled and previous version exists
    if version_manager and has_previous_version:
        out_md = (
            "> 📊 **Version Comparison Available:** Jump to the latest changes via "
            "[Markdown](version_comparison.md) or [HTML](version_comparison.html).\n\n"
            + "---\n\n"
            + out_md
        )
    # Append Figure Gallery
    def img(relpath, alt='', width=340):
        rel_path = os.path.relpath(relpath, output_dir).replace('\\', '/')
        return f'<img src="{rel_path}" alt="{alt}" width="{width}" />'
    out_md += '\n## Visual Summary\n\n'
    if numeric_plots:
        out_md += "### Numeric Distributions\n"
        for col, pdict in numeric_plots.items():
            out_md += f"- **{col}**\n\n  {img(pdict['histogram'], f'{col} histogram')} {img(pdict['boxplot'], f'{col} boxplot')}\n\n"
    if categorical_plots:
        out_md += "### Categorical Distributions\n"
        for col, pdict in categorical_plots.items():
            out_md += f"- **{col}**\n\n  {img(pdict['bar'], f'{col} bar chart')}\n\n"
    out_md += f"### Missingness Map\n\n{img(missmap_path, 'missingness heatmap', 520)}\n\n"
    if not corrs['pearson'].empty:
        out_md += f"### Correlation Heatmap\n\n{img(corrplot_path, 'correlation heatmap', 520)}\n\n"
    # Save report (will be updated with comparisons if needed)
    os.makedirs(output_dir, exist_ok=True)
    outfile_md = os.path.join(output_dir, 'eda_report.md')
    # Compute quality score and save version (this may update out_md with comparisons)
    if version_manager:
        # Prepare analysis results for quality scoring
        analysis_results = {
            'numeric_df': numeric_df,
            'categorical_df': categorical_df,
            'missing_df': missing_df,
            'missing_overall': missing_overall,
            'corrs': corrs
        }
 # Compute quality score
        quality_result = compute_quality_score(df, numeric_df, categorical_df, missing_df, missing_overall, corrs)
        quality_score = quality_result['score']
        
        # Add quality breakdown to analysis results
        analysis_results['quality_breakdown'] = quality_result['breakdown']
        analysis_results['missing_overall'] = missing_overall
        
        # Get previous version BEFORE saving (to compare with)
        prev_version_info = version_manager.get_latest_version(source_name)
        
        # Save version
        version_info = version_manager.save_version(
            source_name=source_name,
            df=df,
            analysis_results=analysis_results,
            quality_score=quality_score,
            output_dir=output_dir,
            version_id=version_id
        )
        
        click.secho(f"Version saved: {version_info['version_id']} (Quality Score: {quality_score:.2f}/100)", fg='green')
        
        # Save main EDA report (without comparisons)
        with open(outfile_md, 'w', encoding='utf8') as f:
            f.write(out_md)
        click.secho(f"EDA report saved to {outfile_md}", fg='blue')
        
        outfile_html = os.path.join(output_dir, 'eda_report.html')
        html_report(out_md, outfile_html, source_name)
        click.secho(f"EDA HTML report saved to {outfile_html}", fg='blue')
        
        # Generate separate comparison report if previous version exists
        if prev_version_info and prev_version_info.get('version_id') != version_info.get('version_id'):
            prev_analysis = version_manager.load_analysis_results(prev_version_info)
            if prev_analysis:
                # Generate comparison sections
                comparison = version_manager.compare_versions(prev_version_info, version_info)
                comparison_md = comparison_section(comparison, prev_version_info, version_info)
                
                # Generate detailed comparison
                detailed_comparison_md = detailed_comparison_section(
                    prev_analysis, analysis_results, prev_version_info, version_info
                )
                
                # Get version history and best version sections
                versions = version_manager.get_versions(source_name)
                history_md = ""
                best_md = ""
                
                if len(versions) > 1:
                    # Add version history section
                    history_md = version_history_section(versions, source_name)
                    
                    # Add best version section
                    best_version = version_manager.get_best_version(source_name)
                    if best_version:
                        best_md = best_version_section(best_version, source_name)
                
                # Combine all comparison sections
                comparison_report_md = (
                    f"# Version Comparison Report\n\n"
                    f"**Dataset:** {source_name}\n\n"
                    f"> 📘 Back to [EDA Report](eda_report.md) · [HTML](eda_report.html)\n\n"
                    f"---\n\n"
                    + best_md
                    + history_md
                    + comparison_md
                    + detailed_comparison_md
                )
 
                # Generate comparison visualizations
                comparison_figs_dir = os.path.join(output_dir, 'comparison_figs')
                os.makedirs(comparison_figs_dir, exist_ok=True)
                fig_sections = []
 
                def add_fig_section(title, fig_path, description):
                    rel = os.path.relpath(fig_path, output_dir).replace('\\', '/')
                    fig_sections.append(
                        f"### {title}\n\n"
                        f"![{title}]({rel})\n\n"
                        f"{description}\n\n"
                    )
 
                quality_fig = os.path.join(comparison_figs_dir, 'quality_trend.png')
                if plot_quality_trend(versions, quality_fig):
                    add_fig_section(
                        "Quality Score Trend",
                        quality_fig,
                        "Quality score movement across the most recent versions.",
                    )
 
                missing_fig = os.path.join(comparison_figs_dir, 'missingness_change.png')
                if plot_missingness_comparison(
                    prev_analysis.get('missing_df'),
                    analysis_results.get('missing_df'),
                    missing_fig,
                ):
                    add_fig_section(
                        "Missingness Comparison",
                        missing_fig,
                        "Columns with the largest changes in missing data percentage.",
                    )
 
                numeric_fig = os.path.join(comparison_figs_dir, 'numeric_mean_change.png')
                if plot_numeric_stat_change(
                    prev_analysis.get('numeric_df'),
                    analysis_results.get('numeric_df'),
                    numeric_fig,
                    stat='mean',
                ):
                    add_fig_section(
                        "Numeric Mean Changes",
                        numeric_fig,
                        "Top numeric columns sorted by absolute change in mean.",
                    )
 
                corr_fig = os.path.join(comparison_figs_dir, 'correlation_change.png')
                if plot_correlation_change(
                    prev_analysis.get('corrs', {}).get('pearson'),
                    analysis_results.get('corrs', {}).get('pearson'),
                    corr_fig,
                ):
                    add_fig_section(
                        "Correlation Change Heatmap",
                        corr_fig,
                        "Correlation differences (current minus previous) for the most impacted numeric columns.",
                    )
 
                if fig_sections:
                    comparison_report_md += "\n## 📈 Comparison Visuals\n\n" + ''.join(fig_sections)
                
                # Save comparison report as separate file
                comparison_md_file = os.path.join(output_dir, 'version_comparison.md')
                with open(comparison_md_file, 'w', encoding='utf8') as f:
                    f.write(comparison_report_md)
                click.secho(f"Version comparison report saved to {comparison_md_file}", fg='cyan')
                
                # Save comparison HTML report
                comparison_html_file = os.path.join(output_dir, 'version_comparison.html')
                html_report(comparison_report_md, comparison_html_file, f"{source_name} - Version Comparison")
                click.secho(f"Version comparison HTML saved to {comparison_html_file}", fg='cyan')
                
                click.secho(f"Comparison generated with previous version: {prev_version_info['version_id']}", fg='green')
        
        # Show version count
        versions = version_manager.get_versions(source_name)
        if len(versions) > 1:
            click.secho(f"Total versions for '{source_name}': {len(versions)}", fg='cyan')
    else:
        # No versioning - save report as is
        with open(outfile_md, 'w', encoding='utf8') as f:
            f.write(out_md)
        click.secho(f"Markdown report saved to {outfile_md}", fg='blue')
        
        outfile_html = os.path.join(output_dir, 'eda_report.html')
        html_report(out_md, outfile_html, source_name)
        click.secho(f"HTML report saved to {outfile_html}", fg='blue')
    
    print(out_md)
 
if __name__ == '__main__':
    main()
 