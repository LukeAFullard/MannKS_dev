
import os
import numpy as np
import MannKenSen as mks
import textwrap
import io
from contextlib import redirect_stdout

def generate_readme():
    """
    Generates a comprehensive README.md file for Example 2, demonstrating a
    basic non-seasonal trend test with a numeric time vector.
    """
    # --- 1. Define Paths and Code Block ---
    output_dir = os.path.dirname(__file__)

    code_block = textwrap.dedent("""
        import numpy as np
        import MannKenSen as mks

        # 1. Generate Synthetic Data
        # This demonstrates the simplest use case with a numeric time vector.
        np.random.seed(42)
        n_samples = 50
        time = np.arange(n_samples)

        # Create data with a clear upward trend (slope of approx. 0.1)
        values = (0.1 * time) + np.random.normal(0, 0.5, n_samples)

        # 2. Perform the Trend Test
        result = mks.trend_test(x=values, t=time)

        # 3. Print the full result
        print(result)
    """)

    # --- 2. Execute the Code Block to Get Outputs ---
    f = io.StringIO()
    with redirect_stdout(f):
        exec(code_block, {'np': np, 'mks': mks})
    output_str = f.getvalue().strip()

    # --- 3. Construct the README ---
    readme_content = f"""
# Example 2: Basic Non-Seasonal Trend Test (Numeric Time)

This example demonstrates the simplest use case of the `MannKenSen` package: performing a non-seasonal trend test on a dataset with a simple numeric time vector (e.g., `[0, 1, 2, ...]`).

## The Python Script

The following script generates 50 data points with a clear upward trend and runs the `trend_test` function to perform the analysis.

```python
{code_block}
```

## Command Output

Running the script prints the full `Mann_Kendall_Test` namedtuple containing all the results of the analysis.

```
{output_str}
```

## Interpretation of Results
The most critical fields for a quick interpretation are:
-   **`p`**: The p-value is extremely low (close to zero), which is well below the standard significance level of 0.05. This indicates a **statistically significant** trend.
-   **`slope`**: The Sen's slope is `~0.1`. Since it's positive, the trend is **increasing**. The value is the estimated rate of change per unit of time.
-   **`classification`**: The final classification of **'Highly Likely Increasing'** provides a clear, human-readable summary, confirming the significant increasing trend.

**Conclusion:** This basic example shows the fundamental workflow for performing a trend test on simple numeric data.
"""

    # Write the README file
    readme_file_path = os.path.join(output_dir, 'README.md')
    with open(readme_file_path, 'w') as f:
        f.write(readme_content)

    print("Successfully generated README for Example 2.")

if __name__ == '__main__':
    generate_readme()
