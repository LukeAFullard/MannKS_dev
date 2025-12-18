
import os
import numpy as np
import pandas as pd
import MannKenSen as mks
import textwrap
import io
from contextlib import redirect_stdout

def generate_readme():
    """
    Generates a comprehensive README.md file for Example 24, demonstrating
    'day_of_year' seasonality.
    """
    # --- 1. Define Paths and Code Block ---
    output_dir = os.path.dirname(__file__)

    code_block = textwrap.dedent("""
        import numpy as np
        import pandas as pd
        import MannKenSen as mks
        import os

        # 1. Generate Synthetic Data
        np.random.seed(1)
        n_years = 5
        t = pd.to_datetime(pd.date_range(start='2016-01-01', periods=n_years * 365, freq='D'))

        # Create a subtle long-term increasing trend
        long_term_trend = np.linspace(0, 5, len(t))

        # Create a seasonal pattern with a spike between day 120 and 150
        day_of_year = t.dayofyear
        seasonal_pattern = np.zeros(len(t))
        spike_mask = (day_of_year >= 120) & (day_of_year <= 150)
        seasonal_pattern[spike_mask] = 10

        # Combine with noise
        noise = np.random.normal(0, 2.0, len(t))
        x = long_term_trend + seasonal_pattern + noise

        # 2. Run the Seasonal Trend Test
        plot_path = 'seasonal_day_of_year_trend.png'
        # For day_of_year, set period=366 to handle leap years
        result = mks.seasonal_trend_test(x, t, season_type='day_of_year', period=366, plot_path=plot_path)

        # 3. Print the result
        print(result)
    """)

    # --- 2. Execute the Code Block to Get Outputs ---
    f = io.StringIO()
    original_dir = os.getcwd()
    os.chdir(output_dir)
    with redirect_stdout(f):
        exec(code_block, {'np': np, 'pd': pd, 'mks': mks, 'os': os})
    os.chdir(original_dir)
    output_str = f.getvalue().strip()


    # --- 3. Construct the README ---
    readme_content = f"""
# Example 24: Advanced Seasonality with `day_of_year`

For some datasets, particularly in environmental science, seasonality is tied to specific days of the year rather than just the month. For example, a river's flow might be highest during a specific week of spring due to snowmelt.

The `MannKenSen` package supports this type of granular analysis using `season_type='day_of_year'`.

## The Python Script

The following script generates 5 years of daily data with two patterns:
1.  A subtle long-term **increasing** trend.
2.  A sharp **spike** in values for a 30-day period each year (days 120-150), simulating an annual event.

```python
{code_block}
```

## Command Output

Running the script produces a single result object, summarizing the overall trend across all 366 days of the year.

```
{output_str}
```

## Interpretation of Results

The test is configured with `season_type='day_of_year'` and `period=366`. The period must be 366 to correctly handle leap years, preventing day numbers from shifting. The test compares the value for each specific day across all years (e.g., Jan 1st 2016 vs. Jan 1st 2017, etc.).

The result is a **'Highly Likely Increasing'** trend. The test successfully identified the subtle, long-term increasing trend that was present on each day, independent of the large annual spike.

## Plot

**Note:** The plot for this analysis is very large, as it generates a subplot for every day of the year (366 in total). It is still a useful diagnostic tool but can be slow to generate and view.

The plot below shows the overall data and the first few seasonal subplots. Each subplot for each day of the year would show a slight increasing trend line, consistent with the overall result.

![Seasonal Day of Year Trend Plot](seasonal_day_of_year_trend.png)
"""

    # Write the README file
    readme_file_path = os.path.join(output_dir, 'README.md')
    with open(readme_file_path, 'w') as f:
        f.write(readme_content)

    print("Successfully generated README and plot for Example 24.")

if __name__ == '__main__':
    generate_readme()
