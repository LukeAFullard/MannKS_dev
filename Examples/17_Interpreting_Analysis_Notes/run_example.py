
import os
import numpy as np
import pandas as pd
import MannKenSen

def generate_readme_for_scenario(title, data_dict, trend_test_kwargs, explanation):
    """
    Helper function to run a scenario and format its documentation.
    """
    # Prepare data
    if 'x_censored' in data_dict:
        x_prepared = MannKenSen.prepare_censored_data(data_dict['x_censored'])
        data_code = f"x_censored = {data_dict['x_censored']!r}\\nx = MannKenSen.prepare_censored_data(x_censored)"
    else:
        x_prepared = data_dict['x']
        data_code = f"x = {data_dict['x']!r}"

    t_code = f"t = {data_dict['t']!r}"
    if 'is_datetime' in data_dict and data_dict['is_datetime']:
        t_prepared = pd.to_datetime(data_dict['t'])
        t_code = f"t = pd.to_datetime({data_dict['t']!r})"
    else:
        t_prepared = data_dict['t']

    # Run trend test
    result = MannKenSen.trend_test(x_prepared, t_prepared, **trend_test_kwargs)

    # Format for README
    readme_part = f"""
### {title}

**Analysis Note Produced:** `{result.analysis_notes}`

**Explanation:** {explanation}

**Code to Reproduce:**
```python
import pandas as pd
import MannKenSen

# Data
{data_code}
{t_code}

# Analysis
result = MannKenSen.trend_test(x, t, **{trend_test_kwargs!r})
print(result.analysis_notes)
```
"""
    return readme_part

def generate_full_readme():
    """
    Generates the complete README.md file by running all scenarios.
    """
    readme_content = """
# Example 17: Interpreting Analysis Notes

The `MannKenSen` package includes a system of "Analysis Notes" to provide data quality warnings. These notes do not stop the analysis, but they alert you to potential issues in your dataset that could affect the reliability of the trend results.

This example demonstrates how to trigger and interpret the most common notes.
"""

    # --- Scenario 1: Insufficient Unique Values ---
    sc1 = {
        'title': "Insufficient Unique Values",
        'data_dict': {'x': [1, 1, 2, 2, 1, 1, 2, 2], 't': list(range(8))},
        'trend_test_kwargs': {},
        'explanation': "This note is triggered when there are fewer than 3 unique non-censored values. With such low variability, a trend analysis is not meaningful."
    }
    readme_content += generate_readme_for_scenario(**sc1)

    # --- Scenario 2: Insufficient Non-Censored Values ---
    sc2 = {
        'title': "Insufficient Non-Censored Values",
        'data_dict': {'x_censored': ['<1', '<1', '<1', '<1', 5, 6, 7], 't': list(range(7))},
        'trend_test_kwargs': {},
        'explanation': "Triggered when there are fewer than 5 non-censored data points available for the analysis."
    }
    readme_content += generate_readme_for_scenario(**sc2)

    # --- Scenario 3: Long Run of a Single Value ---
    sc3 = {
        'title': "Long Run of a Single Value",
        'data_dict': {'x': [1, 2, 3, 3, 3, 3, 3, 3, 4, 5], 't': list(range(10))},
        'trend_test_kwargs': {},
        'explanation': "Occurs if more than 50% of the data consists of a single, repeated value. This can heavily bias the Mann-Kendall test and reduce its power."
    }
    readme_content += generate_readme_for_scenario(**sc3)

    # --- Scenario 4: Tied Timestamps ---
    sc4 = {
        'title': "Tied Timestamps Without Aggregation",
        'data_dict': {'x': [1, 2, 3, 4], 't': [2000, 2001, 2001, 2002], 'is_datetime': False},
        'trend_test_kwargs': {'agg_method': 'none'},
        'explanation': "Generated when the time vector `t` contains duplicate values and the default `agg_method='none'` is used. The Sen's slope calculation can be sensitive to this."
    }
    readme_content += generate_readme_for_scenario(**sc4)

    # --- Scenario 5: Sen's Slope Influenced by Censored Data ---
    sc5 = {
        'title': "Sen's Slope Influenced by Censored Data",
        'data_dict': {'x_censored': ['<1', 10, 12, 14], 't': [2000, 2001, 2002, 2003]},
        'trend_test_kwargs': {},
        'explanation': "This is a `WARNING` that the median Sen's slope was calculated from a pair of data points where at least one was censored. The slope's value is therefore an estimate based on the `lt_mult` or `gt_mult` parameters."
    }
    readme_content += generate_readme_for_scenario(**sc5)

    # --- Scenario 6: Sample Size Below Minimum ---
    sc6 = {
        'title': "Sample Size Below Minimum",
        'data_dict': {'x': [1, 2, 3, 4, 5], 't': list(range(5))},
        'trend_test_kwargs': {'min_size': 10},
        'explanation': "A note indicating that the number of data points (n=5) is below the recommended minimum size (`min_size=10`) for a reliable test."
    }
    readme_content += generate_readme_for_scenario(**sc6)

    # Write to file
    filepath = os.path.join(os.path.dirname(__file__), 'README.md')
    with open(filepath, 'w') as f:
        f.write(readme_content)
    print("Generated README.md for Example 17.")

if __name__ == '__main__':
    generate_full_readme()
