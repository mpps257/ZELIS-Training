import click
from utils.io import load_table
from analyzers.numeric import analyze_numeric
from analyzers.categorical import analyze_categorical
from analyzers.missingness import analyze_missingness
from templates.narrative import numeric_narrative, categorical_narrative, missingness_narrative
from report.markdown_report import (overview_section, sample_records_section, numeric_section, categorical_section, missingness_section,  class_balance_section)
from report.html_report import html_report
from utils.plots import plot_histogram, plot_boxplot, plot_bar, plot_missingness_heatmap, plot_corr_heatmap
import os
 
@click.command()
@click.argument('source', type=str)
@click.option('--output-dir', '-o', default='reports/')
@click.option('--target', type=str, default=None, help='(Optional) Target/class column for class balance analysis')
def main(source, output_dir, target=None):
    """Run EDA report on a data SOURCE (csv, excel, parquet, or url)"""
    try:
        df = load_table(source)
    except Exception as e:
        click.secho(f"Error loading data: {e}", fg='red')
        return
    click.secho(f"Loaded data with shape {df.shape}", fg='green')
 
    # ANALYSIS
    numeric_df = analyze_numeric(df)
    categorical_df = analyze_categorical(df)
    missing_df, missing_overall = analyze_missingness(df)

 
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
 
 
    # NARRATIVES (now lists of lines per col)
    num_narr = {row['column']: numeric_narrative(row) for _, row in numeric_df.iterrows()} if not numeric_df.empty else {}
    cat_narr = {row['column']: categorical_narrative(row) for _, row in categorical_df.iterrows()} if not categorical_df.empty else {}
    miss_narr = {row['column']: missingness_narrative(row) for _, row in missing_df.iterrows()} if not missing_df.empty else {}
    # Filter out columns with no missing data from narratives
    miss_narr = {col: narr for col, narr in miss_narr.items() if narr}  # Only keep columns with non-empty narratives
 
 
    # Filter missing_df to only show columns with missing data
    missing_df_filtered = missing_df[missing_df['missing'] > 0] if not missing_df.empty else missing_df
    
    # REPORT GENERATION
    out_md = (
        overview_section(df)
        + sample_records_section(df)
        + (class_balance_section_md or '')
        + numeric_section(numeric_df, num_narr)
        + categorical_section(categorical_df, cat_narr)
        + missingness_section(missing_df_filtered, miss_narr)
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
    os.makedirs(output_dir, exist_ok=True)
    outfile_md = os.path.join(output_dir, 'eda_report.md')
    with open(outfile_md, 'w', encoding='utf8') as f:
        f.write(out_md)
    click.secho(f"Markdown report saved to {outfile_md}", fg='blue')
    # HTML conversion - extract filename from source
    source_name = os.path.basename(source) if not source.startswith('http') else source.split('/')[-1].split('?')[0] or 'Remote Dataset'
    if not source_name or source_name == source:
        source_name = 'Dataset'
    outfile_html = os.path.join(output_dir, 'eda_report.html')
    html_report(out_md, outfile_html, source_name)
    click.secho(f"HTML report saved to {outfile_html}", fg='blue')
    print(out_md)
 
if __name__ == '__main__':
    main()