import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
import pandas as pd
 
def plot_histogram(series, out_path):
    plt.figure(figsize=(4,3))
    plt.hist(series.dropna(), bins=30, color='#6fa6e6', edgecolor='white')
    plt.title(f"Histogram: {series.name}")
    plt.xlabel(series.name)
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
 
def plot_boxplot(series, out_path):
    plt.figure(figsize=(4,2.5))
    sns.boxplot(x=series.dropna(), color='#7ed6a2')
    plt.title(f"Boxplot: {series.name}")
    plt.xlabel(series.name)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
 
def plot_bar(series, out_path, max_cats=20):
    vc = series.value_counts().iloc[:max_cats]
    plt.figure(figsize=(5,2.8))
    sns.barplot(x=vc.index.astype(str), y=vc.values,hue=vc.index.astype(str), palette='muted', legend=False)
    plt.title(f"Bar Chart: {series.name}")
    plt.ylabel('Count')
    plt.xlabel(series.name)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
 
def plot_missingness_heatmap(df, out_path):
    plt.figure(figsize=(max(6, int(df.shape[1] * 0.5)), 3))
    sns.heatmap(df.isnull(), cbar=False, cmap='Reds', yticklabels=False)
    plt.title('Missingness Heatmap')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
 
def plot_corr_heatmap(corr_df, out_path):
    plt.figure(figsize=(max(5, int(len(corr_df.columns)*0.5)), 4))
    sns.heatmap(corr_df, annot=True, fmt='.2f', cmap='vlag', square=True)
    plt.title('Correlation Heatmap')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
 