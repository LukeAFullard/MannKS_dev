
# Example 16: Interpreting the Full Output

This example provides a detailed explanation of every field in the `namedtuple` returned by the `MannKenSen.trend_test` and `MannKenSen.seasonal_trend_test` functions.

## 1. Running the Code

The following Python code generates a simple dataset and performs a trend test.

```python
import numpy as np
import pandas as pd
import MannKenSen

# Generate Synthetic Data
np.random.seed(42)
n = 50
t = pd.to_datetime(pd.date_range(start='2000-01-01', periods=n, freq='YE'))
x = np.linspace(0, 10, n) + np.random.normal(0, 1.0, n)

# Run the Trend Test
result = MannKenSen.trend_test(x, t)

print(result)
```

## 2. Results

The test returns a `namedtuple` object with the following values:

```
trend: increasing\nh: True\np: 0.0000\nz: 8.2645\nTau: 0.8073\ns: 989.0\nvar_s: 14291.6667\nslope: 0.0000 (units/sec), 0.1917 (units/year)\nintercept: -5.8044\nlower_ci: 0.1723 (units/year)\nupper_ci: 0.2110 (units/year)\nC: 1.0000\nCd: 0.0000\nclassification: Highly Likely Increasing\nanalysis_notes: ['WARNING: Sen slope based on tied non-censored values']\nsen_probability: 0.0000\nsen_probability_max: 0.0000\nsen_probability_min: 0.0000\nprop_censored: 0.00%\nprop_unique: 100.00%\nn_censor_levels: 0
```

## 3. Explanation of Each Field

Here is a breakdown of what each field means:

### Trend Classification

-   **`trend`** (`str`): A high-level summary of the trend direction ('increasing', 'decreasing', or 'no trend').
-   **`h`** (`bool`): The hypothesis result. `True` if the trend is statistically significant (i.e., if `p` < `alpha`), `False` otherwise.
-   **`classification`** (`str`): A more detailed, confidence-based trend classification (e.g., 'Highly Significant Increasing', 'No Clear Trend'). This is derived from the confidence scores.

### Statistical Significance (Mann-Kendall Test)

-   **`p`** (`float`): The p-value of the Mann-Kendall test. It represents the probability of observing the detected trend by chance. A small p-value (typically < 0.05) indicates a statistically significant trend.
-   **`z`** (`float`): The Z-statistic. It measures how many standard deviations the observed Mann-Kendall score (`s`) is from the expected score of zero (assuming no trend). Positive values indicate an increasing trend; negative values indicate a decreasing trend.
-   **`s`** (`int`): The Mann-Kendall score. It is the sum of the signs of the differences between all pairs of data points. A large positive score indicates a strong increasing trend, while a large negative score indicates a strong decreasing trend.
-   **`var_s`** (`float`): The variance of the `s` score, which accounts for ties in the data. This is used to calculate the Z-statistic.

### Trend Magnitude (Sen's Slope)

-   **`slope`** (`float`): The Sen's slope, which is the median of the slopes calculated between all pairs of data points. It represents the estimated rate of change over time. **Note:** When using datetime objects, the raw slope is in **units per second**. You must multiply it by the number of seconds in your desired time unit (e.g., `365.25 * 24 * 60 * 60` for units per year).
-   **`intercept`** (`float`): The intercept of the Sen's slope line, calculated to pass through the median data point.
-   **`lower_ci`** (`float`): The lower bound of the confidence interval for the Sen's slope.
-   **`upper_ci`** (`float`): The upper bound of the confidence interval for the Sen's slope.

### Confidence Scores

-   **`C`** (`float`): The confidence in the trend direction, calculated as `1 - p`. A value of 0.98 means there is a 98% confidence that a trend exists in some direction.
-   **`Cd`** (`float`): The confidence that the trend is **decreasing**. For an increasing trend, this value will be very small. For a decreasing trend, it will be close to 1.0.

### Sen's Slope Probabilities

These values provide insight into the distribution of the pairwise slopes calculated for the Sen's slope.

-   **`sen_probability`** (`float`): The probability that any randomly chosen pairwise slope is positive (increasing). A value close to 1.0 indicates a consistent increasing trend, while a value close to 0 indicates a consistent decreasing trend.
-   **`sen_probability_max`** (`float`): The probability of a positive slope *if* all ambiguous censored slopes were positive.
-   **`sen_probability_min`** (`float`): The probability of a positive slope *if* all ambiguous censored slopes were negative.

### Data & Analysis Metadata

-   **`analysis_notes`** (`list`): A list of strings containing important data quality warnings or notes about the analysis (e.g., "tied timestamps present without aggregation"). An empty list means no issues were flagged.
-   **`prop_censored`** (`float`): The proportion (0.0 to 1.0) of the data that is censored.
-   **`prop_unique`** (`float`): The proportion of unique, non-censored values in the dataset. A low value indicates many tied data points.
-   **`n_censor_levels`** (`int`): The number of unique censoring levels detected in the data (e.g., `<1`, `<5`, `>50` would be 3 levels).
