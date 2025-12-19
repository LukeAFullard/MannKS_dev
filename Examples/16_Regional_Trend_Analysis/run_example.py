
import os
import numpy as np
import pandas as pd
import MannKenSen as mks
import textwrap
import io
from contextlib import redirect_stdout

def generate_readme():
    """
    Generates a comprehensive README.md file for Example 15, demonstrating
    regional trend analysis.
    """
    # --- 1. Define Paths and Code Block ---
    output_dir = os.path.dirname(__file__)

    code_block = textwrap.dedent("""
        import numpy as np
        import pandas as pd
        import MannKenSen as mks

        # 1. Generate Data for Multiple Sites
        np.random.seed(42)
        sites = ['Site A', 'Site B', 'Site C']
        years = np.arange(2010, 2021)

        # Site A: Clear increasing trend
        values_a = 10 + np.linspace(0, 5, len(years)) + np.random.normal(0, 1, len(years))
        # Site B: Weaker increasing trend
        values_b = 15 + np.linspace(0, 2, len(years)) + np.random.normal(0, 1, len(years))
        # Site C: No clear trend (stable)
        values_c = 12 + np.linspace(0, 0, len(years)) + np.random.normal(0, 1, len(years))

        # Combine into a single DataFrame
        df_a = pd.DataFrame({'site': 'Site A', 'year': years, 'value': values_a})
        df_b = pd.DataFrame({'site': 'Site B', 'year': years, 'value': values_b})
        df_c = pd.DataFrame({'site': 'Site C', 'year': years, 'value': values_c})
        regional_data = pd.concat([df_a, df_b, df_c], ignore_index=True)

        # 2. Perform Trend Test on Each Site
        print("--- Individual Site Results ---")
        site_results = []
        for site in sites:
            site_data = regional_data[regional_data['site'] == site]
            result = mks.trend_test(x=site_data['value'], t=site_data['year'])
            print(f"{site}: classification='{result.classification}', p={result.p:.4f}, slope={result.slope:.4f}")
            site_results.append(result)

        # 3. Perform Regional Test
        print("\\n--- Regional Test Result ---")
        results_df = pd.DataFrame(site_results)
        results_df['site'] = sites
        regional_result = mks.regional_test(
            trend_results=results_df,
            time_series_data=regional_data,
            site_col='site', value_col='value', time_col='year'
        )
        print(regional_result)
    """)

    # --- 2. Execute the Code Block to Get Outputs ---
    f = io.StringIO()
    with redirect_stdout(f):
        exec(code_block, {'np': np, 'pd': pd, 'mks': mks})
    output_str = f.getvalue().strip()

    # --- 3. Construct the README ---
    readme_content = f"""
# Example 15: Regional Trend Analysis

This example demonstrates how to use the `regional_test` function to aggregate trend results from multiple sites to determine if there is a significant trend across an entire region.

## Key Concepts
A regional test answers the question: "Is there a general, region-wide trend?" It is more powerful than simply averaging the results of individual sites because it properly accounts for the variance of each site's trend and the correlation between sites. The workflow is:
1.  Perform a standard `trend_test` on each individual site.
2.  Combine the individual site results and the raw time series data into the `regional_test` function.

## The Python Script
The script simulates a scenario with three sites: two with increasing trends of different strengths and one with no trend. It analyzes each site individually and then passes all the results to the `regional_test` function for a final, aggregated analysis.

```python
{code_block}
```

## Command Output
Running the script produces the following output, showing the individual site results first, followed by the final regional test result.

```
{output_str}
```

## Interpretation of Results

### Individual Site Results
-   **Site A** and **Site B** both show statistically significant increasing trends.
-   **Site C** shows 'No Trend'.

### Regional Test Result
Despite Site C having no trend, the `regional_test` combines the strong evidence from Sites A and B to conclude that there is a **'Highly Likely Increasing'** trend across the region as a whole. The `DT` (Direction of Trend) field confirms this.

**Conclusion:** The `regional_test` function provides a statistically sound method for assessing large-scale environmental changes by synthesizing trend information from multiple, potentially correlated, time series.
"""

    # Write the README file
    readme_file_path = os.path.join(output_dir, 'README.md')
    with open(readme_file_path, 'w') as f:
        f.write(readme_content)

    print("Successfully generated README for Example 15.")

if __name__ == '__main__':
    generate_readme()
