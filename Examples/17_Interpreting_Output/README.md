
# Example 16: Interpreting the Full Output

The `MannKenSen` trend test functions return a `namedtuple` object that contains a wealth of statistical information. Understanding each field is key to interpreting your trend analysis correctly.

This example provides a detailed explanation of every field in the output.

## The Python Script

The following script generates a simple dataset with a clear increasing trend and runs the `trend_test` to produce the result object we will be examining.

```python

import numpy as np
import pandas as pd
import MannKenSen as mks

# 1. Generate Synthetic Data
np.random.seed(42)
n = 50
t = pd.to_datetime(pd.date_range(start='2000-01-01', periods=n, freq='YE'))
x = np.linspace(0, 10, n) + np.random.normal(0.1, 1.0, n)

# 2. Run the Trend Test
result = mks.trend_test(x, t)

# 3. Print the full result object after filtering misleading warnings
final_result = result._replace(
    analysis_notes=[note for note in result.analysis_notes if "tied non-censored" not in note]
)
print(final_result)

```

## Command Output

Running the script above prints the full `Mann_Kendall_Test` namedtuple:

```
Mann_Kendall_Test(trend='increasing', h=np.True_, p=np.float64(2.220446049250313e-16), z=np.float64(8.264479474912722), Tau=np.float64(0.8073469387755102), s=np.float64(989.0), var_s=np.float64(14291.666666666666), slope=np.float64(6.075165563774819e-09), intercept=np.float64(-5.704384429915891), lower_ci=np.float64(5.459090782705589e-09), upper_ci=np.float64(6.687641241680511e-09), C=0.9999999999999999, Cd=1.1102230246251565e-16, classification='Highly Likely Increasing', analysis_notes=[], sen_probability=np.float64(7.021083561986885e-17), sen_probability_max=np.float64(7.021083561986885e-17), sen_probability_min=np.float64(7.021083561986885e-17), prop_censored=np.float64(0.0), prop_unique=1.0, n_censor_levels=0)
```

## Explanation of Each Field

Here is a breakdown of what each field in the output means:

### Trend Classification
*   **`trend`** (`str`): A high-level summary of the trend direction ('increasing', 'decreasing', or 'no trend').
*   **`h`** (`bool`): The hypothesis result. `True` if the trend is statistically significant (i.e., if `p` < `alpha`), `False` otherwise.
*   **`classification`** (`str`): A more detailed, confidence-based trend classification (e.g., 'Highly Likely Increasing', 'No Trend').

### Statistical Significance (Mann-Kendall Test)
*   **`p`** (`float`): The **p-value**. It represents the probability of observing the detected trend by pure chance. A small p-value (typically < 0.05) indicates a statistically significant trend.
*   **`z`** (`float`): The **Z-statistic**. It measures how many standard deviations the Mann-Kendall score (`s`) is from the expected score of zero (assuming no trend).
*   **`s`** (`float`): The **Mann-Kendall score**. It is the sum of the signs of the differences between all pairs of data points.
*   **`var_s`** (`float`): The **variance of `s`**. This value accounts for ties in the data and is used to calculate the Z-statistic.
*   **`Tau`** (`float`): **Kendall's Tau**. A measure of correlation between the data and time, ranging from -1 to +1.

### Trend Magnitude (Sen's Slope)
*   **`slope`** (`float`): The **Sen's slope**. The median of slopes between all pairs of points. **Note:** For datetime inputs, the raw slope is in **units per second**.
*   **`intercept`** (`float`): The intercept of the Sen's slope line.
*   **`lower_ci`** / **`upper_ci`** (`float`): The confidence intervals for the Sen's slope.

### Confidence Scores
*   **`C`** (`float`): The confidence in the trend direction, calculated as `1 - p / 2`.
*   **`Cd`** (`float`): The confidence that the trend is specifically **decreasing**.

### Sen's Slope Probabilities
*   **`sen_probability`** (`float`): The probability that any randomly chosen pairwise slope is positive.
*   **`sen_probability_max`** / **`min`** (`float`): Probabilities if ambiguous (censored) slopes were resolved.

### Data & Analysis Metadata
*   **`analysis_notes`** (`list`): A list of data quality warnings.
*   **`prop_censored`** (`float`): The proportion (0.0 to 1.0) of the data that is censored.
*   **`prop_unique`** (`float`): The proportion of unique, non-censored values.
*   **`n_censor_levels`** (`int`): The number of unique censoring levels.
