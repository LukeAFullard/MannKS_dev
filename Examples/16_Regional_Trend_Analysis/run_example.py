
import os
import numpy as np
import pandas as pd
import MannKenSen as mks
import textwrap
import io
from contextlib import redirect_stdout

def generate_readme():
    """
    Generates a comprehensive README.md file for Example 16, demonstrating
    the regional trend test.
    """
    # --- 1. Define Paths and Code Block ---
    output_dir = os.path.dirname(__file__)

    code_block = textwrap.dedent("""
        import numpy as np
        import pandas as pd
        import MannKenSen as mks

        # 1. Generate Synthetic Data for Multiple Sites
        np.random.seed(10)
        sites = ['A', 'B', 'C', 'D']
        all_series_data = []
        all_trend_results = []

        for site in sites:
            n_samples = 20
            time = np.arange(2000, 2000 + n_samples)
            noise = np.random.normal(0, 2, n_samples)

            # Assign different trends to each site
            if site in ['A', 'B']:
                trend = 0.5 * np.arange(n_samples) # Increasing
            elif site == 'C':
                trend = -0.5 * np.arange(n_samples) # Decreasing
            else:
                trend = 0 # No trend

            value = 10 + trend + noise

            site_df = pd.DataFrame({'site': site, 'time': time, 'value': value})
            all_series_data.append(site_df)

            # 2. Run trend_test for each site to get 's' and 'var_s'
            result = mks.trend_test(x=site_df['value'], t=site_df['time'])
            all_trend_results.append({
                'site': site,
                's': result.s,
                'var_s': result.var_s,
                'C': result.C
            })

        time_series_df = pd.concat(all_series_data).reset_index(drop=True)
        trend_results_df = pd.DataFrame(all_trend_results)

        # 3. Run the Regional Test
        regional_result = mks.regional_test(
            time_series_data=time_series_df,
            trend_results=trend_results_df,
            time_col='time',
            value_col='value',
            site_col='site'
        )

        print("--- Input Time Series Data ---")
        print(time_series_df.head())
        print("\\n--- Input Trend Results ---")
        print(trend_results_df)
        print("\\n--- Regional Test Result ---")
        print(regional_result)
    """)

    # --- 2. Execute the Code Block to Get Outputs ---
    f = io.StringIO()
    original_dir = os.getcwd()
    # Note: No need to chdir as this example doesn't write plots
    with redirect_stdout(f):
        exec(code_block, {'np': np, 'pd': pd, 'mks': mks, 'os': os})
    output_str = f.getvalue().strip()

    # --- 3. Construct the README ---
    readme_content = f"""
# Example 16: Regional Trend Analysis

This example demonstrates how to use the `regional_test` function to determine if there is a consistent, statistically significant trend across multiple locations or sites.

## The Python Script

The script first generates synthetic data for four sites:
-   Sites 'A' and 'B' have a clear **increasing** trend.
-   Site 'C' has a clear **decreasing** trend.
-   Site 'D' has **no trend**.

Next, it runs `mks.trend_test` on each site individually to get the necessary Mann-Kendall score (`s`), variance (`var_s`), and confidence (`C`). Finally, it combines all the site data and individual results into two pandas DataFrames and passes them to `mks.regional_test`.

```python
{code_block}
```

## Command Output

The script prints the head of the input time series data, the summary of individual trend results, and the final result from the regional test.

```
{output_str}
```

## Interpretation of Results

The `regional_test` function aggregates the trend statistics from all sites to provide a region-wide assessment.

-   **Inputs:** The test requires two DataFrames: one with the raw time series data for all sites, and one summarizing the `s`, `var_s` and `C` from each site's individual trend test.
-   **Aggregation:** The test considers the trends from all four sites. In this case, two sites are increasing, one is decreasing, and one has no trend.
-   **Result:**
    -   `TAU` is the aggregate trend strength, which is the proportion of sites trending in the modal direction.
    -   `DT` is the aggregate trend direction. In this case it's **'Increasing'** because two sites were increasing and only one was decreasing.
    -   However, the confidence `CT` is not high enough to be significant.

**Conclusion:** The `regional_test` is a powerful tool for moving beyond site-specific analysis to understand the bigger picture across a geographic region.
"""

    # Write the README file
    readme_file_path = os.path.join(output_dir, 'README.md')
    with open(readme_file_path, 'w') as f:
        f.write(readme_content)

    print("Successfully generated README for Example 16.")

if __name__ == '__main__':
    generate_readme()
