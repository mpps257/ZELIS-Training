
## Overview

- Shape: **1338 rows** × **7 columns**
- Memory usage: **73 KB**
- **Data Type Distribution:**
  - Numeric: 4
  - Categorical: 3
  - Text: 0
  - Datetime: 0

**Column Data Types:**

| Column   | Type        | Pandas dtype   | Mixed Types   |
|:---------|:------------|:---------------|:--------------|
| age      | numeric     | int64          |               |
| sex      | categorical | object         |               |
| bmi      | numeric     | float64        |               |
| children | numeric     | int64          |               |
| smoker   | categorical | object         |               |
| region   | categorical | object         |               |
| charges  | numeric     | float64        |               |


---

## Sample Records

|   age | sex    |    bmi |   children | smoker   | region    |   charges |
|------:|:-------|-------:|-----------:|:---------|:----------|----------:|
|    19 | female | 27.9   |          0 | yes      | southwest |  16884.9  |
|    18 | male   | 33.77  |          1 | no       | southeast |   1725.55 |
|    28 | male   | 33     |          3 | no       | southeast |   4449.46 |
|    33 | male   | 22.705 |          0 | no       | northwest |  21984.5  |
|    32 | male   | 28.88  |          0 | no       | northwest |   3866.86 |
|    31 | female | 25.74  |          0 | no       | southeast |   3756.62 |
|    46 | female | 33.44  |          1 | no       | southeast |   8240.59 |
|    37 | female | 27.74  |          3 | no       | northwest |   7281.51 |

---

## Numeric Column Insights


| column   |   count |      mean |    median |   variance |       std |       min |       max |   skewness |   kurtosis |   outliers |   missing |   missing_pct |
|:---------|--------:|----------:|----------:|-----------:|----------:|----------:|----------:|-----------:|-----------:|-----------:|----------:|--------------:|
| age      |    1338 | 39.2      | 39        | 197        | 14        | 18        | 64        |     0.0556 |     -1.24  |          0 |         0 |             0 |
| bmi      |    1338 | 30.7      | 30.4      |  37.2      |  6.1      | 16        | 53.1      |     0.284  |     -0.055 |         32 |         0 |             0 |
| children |    1338 |  1.09     |  1        |   1.45     |  1.21     |  0        |  5        |     0.937  |      0.197 |         43 |         0 |             0 |
| charges  |    1338 |  1.33e+04 |  9.38e+03 |   1.47e+08 |  1.21e+04 |  1.12e+03 |  6.38e+04 |     1.51   |      1.6   |        136 |         0 |             0 |


> **Suggested Transforms / Actions:**
>
> - **age**
  - Standardize or normalize (variance much larger than mean).
- **charges**
  - Apply log or Box-Cox transform to reduce right skew.
  - Standardize or normalize (variance much larger than mean).
  - Winsorize or remove outliers (>5%).





---

## Categorical Column Insights


| column   |   count |   cardinality | unique_sample                                        |   top_freq | mode      |   missing |   missing_pct | label_inconsistency   |   max_imbalance | has_mixed_types   |
|:---------|--------:|--------------:|:-----------------------------------------------------|-----------:|:----------|----------:|--------------:|:----------------------|----------------:|:------------------|
| sex      |    1338 |             2 | ['male', 'female']                                   |        676 | male      |         0 |             0 | False                 |           0.505 | False             |
| smoker   |    1338 |             2 | ['no', 'yes']                                        |       1064 | no        |         0 |             0 | False                 |           0.795 | False             |
| region   |    1338 |             4 | ['southeast', 'southwest', 'northwest', 'northeast'] |        364 | southeast |         0 |             0 | False                 |           0.272 | False             |


> **Suggested Transforms / Actions:**
>
> - **sex**
  - One-hot encoding is suitable.
- **smoker**
  - One-hot encoding is suitable.
  - Highly imbalanced (>70% one class); consider resampling or weighting.
- **region**
  - One-hot encoding is suitable.




---

## Missingness Insights

No data.



---

## Visual Summary

### Numeric Distributions
- **age**

  <img src="figs/age_hist.png" alt="age histogram" width="340" /> <img src="figs/age_box.png" alt="age boxplot" width="340" />

- **bmi**

  <img src="figs/bmi_hist.png" alt="bmi histogram" width="340" /> <img src="figs/bmi_box.png" alt="bmi boxplot" width="340" />

- **children**

  <img src="figs/children_hist.png" alt="children histogram" width="340" /> <img src="figs/children_box.png" alt="children boxplot" width="340" />

- **charges**

  <img src="figs/charges_hist.png" alt="charges histogram" width="340" /> <img src="figs/charges_box.png" alt="charges boxplot" width="340" />

### Categorical Distributions
- **sex**

  <img src="figs/sex_bar.png" alt="sex bar chart" width="340" />

- **smoker**

  <img src="figs/smoker_bar.png" alt="smoker bar chart" width="340" />

- **region**

  <img src="figs/region_bar.png" alt="region bar chart" width="340" />

### Missingness Map

<img src="figs/missingness_heatmap.png" alt="missingness heatmap" width="520" />

