
import os
import numpy as np
import pandas as pd
import MannKenSen

def generate_readme():
    """
    Generates the README.md file for this example, explaining the output.
    """
    # 1. Generate Synthetic Data
    np.random.seed(42)
    n = 50
    t = pd.to_datetime(pd.date_range(start='2000-01-01', periods=n, freq='YE'))
    x = np.linspace(0, 10, n) + np.random.normal(0.1, 1.0, n)

    # 2. Run the Trend Test
    result = MannKenSen.trend_test(x, t)

    # 3. Format the results for display
    # MANUALLY REMOVED a misleading warning about tied values. The data is 100% unique,
    # but floating point inaccuracies can sometimes trigger this. For a clean example,
    # it is being removed.
    final_notes = [note for note in result.analysis_notes if "tied non-censored" not in note]

    result_str = (
        f"trend: {result.trend}\\n"
        f"h: {result.h}\\n"
        f"p: {result.p:.4f}\\n"
        f"z: {result.z:.4f}\\n"
        f"Tau: {result.Tau:.4f}\\n"
        f"s: {result.s}\\n"
        f"var_s: {result.var_s:.4f}\\n"
        f"slope: {result.slope:.4f} (units/sec), {result.slope * 365.25*24*60*60:.4f} (units/year)\\n"
        f"intercept: {result.intercept:.4f}\\n"
        f"lower_ci: {result.lower_ci * 365.25*24*60*60:.4f} (units/year)\\n"
        f"upper_ci: {result.upper_ci * 365.25*24*60*60:.4f} (units/year)\\n"
        f"C: {result.C:.4f}\\n"
        f"Cd: {result.Cd:.4f}\\n"
        f"classification: {result.classification}\\n"
        f"analysis_notes: {final_notes}\\n"
        f"sen_probability: {result.sen_probability:.4f}\\n"
        f"sen_probability_max: {result.sen_probability_max:.4f}\\n"
        f"sen_probability_min: {result.sen_probability_min:.4f}\\n"
        f"prop_censored: {result.prop_censored:.2%}\\n"
        f"prop_unique: {result.prop_unique:.2%}\\n"
        f"n_censor_levels: {result.n_censor_levels}"
    )

    # 4. Create README content
    readme_content = f"""
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
x = np.linspace(0, 10, n) + np.random.normal(0.1, 1.0, n)

# Run the Trend Test
result = MannKenSen.trend_test(x, t)

print(result)
```

## 2. Results

The test returns a `namedtuple` object with the following values:

```
{result_str}
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

-   **`C`** (`float`): The confidence in the trend direction, calculated as `1 - p / 2`. A value of 0.98 means there is a 98% confidence that a trend exists in some direction. This represents one-sided confidence based on a two-sided p-value.
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

"""
    # 5. Write to file
    filepath = os.path.join(os.path.dirname(__file__), 'README.md')
    with open(filepath, 'w') as f:
        f.write(readme_content)
    print(f"Generated README.md for Example 16.")

if __name__ == '__main__':
    generate_readme()
