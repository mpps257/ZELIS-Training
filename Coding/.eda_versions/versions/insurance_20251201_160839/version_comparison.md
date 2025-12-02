# Version Comparison Report

**Dataset:** insurance

> 📘 Back to [EDA Report](eda_report.md) · [HTML](eda_report.html)

---

## 🏆 Best Version

**Best Quality Version:** 20251201_160839

- **Quality Score:** 94.98/100
- **Timestamp:** 2025-12-01 16:08:43
- **Shape:** 1338 rows × 7 columns
- **Missing Data:** 0.00%

- **Grade:** A (Excellent)

---
## Version History

**Data Source:** insurance

| Version ID | Timestamp | Quality Score | Shape | Missing % |
|------------|-----------|---------------|-------|----------|
| 20251201_160839 | 2025-12-01 16:08:43 | 94.98/100 | 1338×7 | 0.00% |
| 20251201_160633 | 2025-12-01 16:06:37 | 94.44/100 | 1338×7 | 0.11% |
| 20251201_154823 | 2025-12-01 15:48:26 | 94.44/100 | 1338×7 | 0.11% |
| 20251201_143526 | 2025-12-01 14:35:29 | 94.44/100 | 1338×7 | 0.11% |
| 20251201_143001 | 2025-12-01 14:30:05 | 94.44/100 | 1338×7 | 0.11% |
| 20251201_130826 | 2025-12-01 13:08:30 | 94.98/100 | 1338×7 | 0.00% |

---
## Version Comparison

**Version 1:** 20251201_160633 (2025-12-01 16:06:37)
**Version 2:** 20251201_160839 (2025-12-01 16:08:43)

### Quality Score Comparison

| Metric | Version 1 | Version 2 | Difference |
|--------|-----------|-----------|------------|
| **Quality Score** | 94.44/100 | 94.98/100 | +0.54 |

✅ **Version 2 has better data quality** (score: 94.98 vs 94.44)

### Dataset Shape

- **No change:** 1338 rows × 7 columns

### Column Changes

- **No column changes** (same columns in both versions)

### Missing Data Comparison

| Version | Missing % |
|---------|----------|
| Version 1 | 0.11% |
| Version 2 | 0.00% |
| **Change** | **-0.11%** |

✅ **Improvement:** Missing data decreased by 0.11%

### Quality Breakdown Comparison

| Component | Version 1 | Version 2 | Difference |
|-----------|-----------|-----------|------------|
| Completeness | 29.97 | 30.00 | +0.03 |
| Consistency | 25.00 | 25.00 | +0.00 |
| Distribution | 16.48 | 16.98 | +0.51 |
| Balance | 13.00 | 13.00 | +0.00 |
| Correlation | 10.00 | 10.00 | +0.00 |

### Recommendations

- ✅ **Use Version 2** (20251201_160839) - Higher quality score
- Consider investigating improvements in Version 2

---
## 📊 Detailed Version Comparison

**Previous Version:** 20251201_160633
**Current Version:** 20251201_160839

### 📈 Statistical Comparison (Numeric Columns)

| Column | Metric | Previous | Current | Change |
|--------|--------|----------|---------|--------|
| age | Mean | 39.21 | 39.21 | +0.00 (+0.0%) |
| age | Median | 39.00 | 39.00 | +0.00 (+0.0%) |
| age | Std | 14.05 | 14.05 | +0.00 (+0.0%) |
| age | Min | 18.00 | 18.00 | +0.00 (+0.0%) |
| age | Max | 64.00 | 64.00 | +0.00 (+0.0%) |
| bmi | Mean | 30.61 | 30.66 | +0.06 (+0.2%) |
| bmi | Median | 30.40 | 30.40 | +0.00 (+0.0%) |
| bmi | Std | 6.46 | 6.10 | -0.36 (-5.5%) |
| bmi | Min | -45.00 | 15.96 | +60.96 (-135.5%) |
| bmi | Max | 53.13 | 53.13 | +0.00 (+0.0%) |
| charges | Mean | 13203.00 | 13270.42 | +67.42 (+0.5%) |
| charges | Median | 9303.30 | 9382.03 | +78.74 (+0.8%) |
| charges | Std | 12076.03 | 12110.01 | +33.98 (+0.3%) |
| charges | Min | 0.00 | 1121.87 | +1121.87 (+0.0%) |
| charges | Max | 63770.43 | 63770.43 | +0.00 (+0.0%) |
| children | Mean | 1.12 | 1.09 | -0.03 (-2.3%) |
| children | Median | 1.00 | 1.00 | +0.00 (+0.0%) |
| children | Std | 1.38 | 1.21 | -0.17 (-12.7%) |
| children | Min | 0.00 | 0.00 | +0.00 (+0.0%) |
| children | Max | 25.00 | 5.00 | -20.00 (-80.0%) |

### 📉 Distribution Comparison

| Column | Metric | Previous | Current | Change |
|--------|--------|----------|---------|--------|
| age | Skewness | 0.06 | 0.06 | +0.00 |
| age | Kurtosis | -1.24 | -1.24 | +0.00 |
| age | Outlier % | 0.00% | 0.00% | +0.00% |
| bmi | Skewness | -0.95 | 0.28 | +1.23 |
| bmi | Kurtosis | 13.49 | -0.06 | -13.54 |
| bmi | Outlier % | 2.02% | 2.39% | +0.37% |
| charges | Skewness | 1.52 | 1.51 | -0.01 |
| charges | Kurtosis | 1.63 | 1.60 | -0.04 |
| charges | Outlier % | 10.24% | 10.16% | -0.07% |
| children | Skewness | 4.52 | 0.94 | -3.58 |
| children | Kurtosis | 66.21 | 0.20 | -66.01 |
| children | Outlier % | 1.50% | 3.21% | +1.72% |

### 🔗 Correlation Comparison

| Column Pair | Previous Correlation | Current Correlation | Change |
|-------------|---------------------|---------------------|--------|
| age ↔ bmi | 0.100 | 0.109 | +0.010 |
| age ↔ charges | 0.298 | 0.299 | +0.001 |
| age ↔ children | 0.055 | 0.042 | -0.012 |
| bmi ↔ charges | 0.193 | 0.198 | +0.005 |
| bmi ↔ children | 0.010 | 0.013 | +0.002 |
| charges ↔ children | 0.091 | 0.068 | -0.023 |

### 🎯 Feature Usefulness Comparison

| Column | Previous Score | Current Score | Change | Status |
|--------|---------------|---------------|--------|--------|
| age | 56.6 | 56.6 | -0.0 | ➡️ Stable |
| bmi | 54.1 | 54.1 | +0.0 | ➡️ Stable |
| charges | 63.0 | 62.9 | -0.1 | ➡️ Stable |
| children | 63.3 | 61.8 | -1.5 | ➡️ Stable |
| region | 49.9 | 50.0 | +0.1 | ➡️ Stable |
| sex | 50.0 | 50.0 | +0.0 | ➡️ Stable |
| smoker | 50.0 | 50.0 | +0.0 | ➡️ Stable |

---

## 📈 Comparison Visuals

### Quality Score Trend

![Quality Score Trend](comparison_figs/quality_trend.png)

Quality score movement across the most recent versions.

### Missingness Comparison

![Missingness Comparison](comparison_figs/missingness_change.png)

Columns with the largest changes in missing data percentage.

### Numeric Mean Changes

![Numeric Mean Changes](comparison_figs/numeric_mean_change.png)

Top numeric columns sorted by absolute change in mean.

### Correlation Change Heatmap

![Correlation Change Heatmap](comparison_figs/correlation_change.png)

Correlation differences (current minus previous) for the most impacted numeric columns.

