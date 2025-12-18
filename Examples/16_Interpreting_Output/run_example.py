
import os
import numpy as np
import pandas as pd
import MannKenSen as mks
import textwrap
import io
from contextlib import redirect_stdout

def generate_readme():
    """
    Generates a comprehensive README.md file for Example 16, explaining
    every field of the trend test output.
    """
    # --- 1. Define Paths and Code Block ---
    output_dir = os.path.dirname(__file__)

    code_block = textwrap.dedent("""
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
    """)

    # --- 2. Execute the Code Block to Get Outputs ---
    f = io.StringIO()
    exec_globals = {'np': np, 'pd': pd, 'mks': mks}
    with redirect_stdout(f):
        exec(code_block, exec_globals)
    output_str = f.getvalue().strip()

    # --- 3. Construct the README ---
    readme_content = f"""
# Example 16: Interpreting the Full Output

The `MannKenSen` trend test functions return a `namedtuple` object that contains a wealth of statistical information. Understanding each field is key to interpreting your trend analysis correctly.

This example provides a detailed explanation of every field in the output.

## The Python Script

The following script generates a simple dataset with a clear increasing trend and runs the `trend_test` to produce the result object we will be examining.

```python
{code_block}
```

## Command Output

Running the script above prints the full `Mann_Kendall_Test` namedtuple:

```
{output_str}
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
"""

    # Write the README file
    readme_file_path = os.path.join(output_dir, 'README.md')
    with open(readme_file_path, 'w') as f:
        f.write(readme_content)

    print(f"Successfully generated README for Example 16.")

if __name__ == '__main__':
    generate_readme()
