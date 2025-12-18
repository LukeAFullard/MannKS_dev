
import os
import numpy as np
import pandas as pd
import MannKenSen as mks
import textwrap
import io
from contextlib import redirect_stdout

def generate_readme():
    """
    Generates a comprehensive README.md file for Example 17, explaining
    how to interpret the various analysis notes.
    """
    # --- 1. Define Scenarios ---
    scenarios = [
        {
            'title': "Insufficient Unique Values",
            'code': textwrap.dedent("""
                # Data has fewer than 3 unique non-censored values.
                x = [1, 1, 2, 2, 1, 1, 2, 2]
                t = range(len(x))
                result = mks.trend_test(x, t, min_size=None)
                print(result.analysis_notes)
            """),
            'explanation': "This note is triggered when there are fewer than 3 unique non-censored values. With such low variability, a meaningful trend analysis cannot be performed."
        },
        {
            'title': "Insufficient Non-Censored Values",
            'code': textwrap.dedent("""
                # Data has fewer than 5 non-censored values.
                x_censored = ['<1', '<1', '<1', '<1', 5, 6, 7]
                t = range(len(x_censored))
                x = mks.prepare_censored_data(x_censored)
                result = mks.trend_test(x, t, min_size=None)
                print(result.analysis_notes)
            """),
            'explanation': "Triggered when there are fewer than 5 non-censored data points. The statistical power of the test is too low with such a small sample size."
        },
        {
            'title': "Long Run of a Single Value",
            'code': textwrap.dedent("""
                # More than 50% of the data consists of a single value (3).
                x = [1, 2, 3, 3, 3, 3, 3, 3, 4, 5]
                t = range(len(x))
                result = mks.trend_test(x, t)
                print(result.analysis_notes)
            """),
            'explanation': "Occurs if a significant portion of the data consists of a single, repeated value. This high number of ties can reduce the power of the Mann-Kendall test."
        },
        {
            'title': "Tied Timestamps Without Aggregation",
            'code': textwrap.dedent("""
                # The timestamp 2001 is duplicated.
                x = [1, 2, 3, 4]
                t = [2000, 2001, 2001, 2002]
                result = mks.trend_test(x, t, agg_method='none')
                print(result.analysis_notes)
            """),
            'explanation': "Generated when the time vector `t` contains duplicate values and no aggregation method is specified. The Sen's slope calculation is sensitive to this and the result may be biased."
        },
        {
            'title': "Sen's Slope Influenced by Censored Data",
            'code': textwrap.dedent("""
                # The median slope is calculated from a pair involving a censored value.
                x_censored = ['<10', 15, 5, 25]
                t = [2000, 2001, 2002, 2003]
                x = mks.prepare_censored_data(x_censored)
                result = mks.trend_test(x, t)
                print(result.analysis_notes)
            """),
            'explanation': "A `WARNING` that the median Sen's slope was calculated from a pair of data points where at least one was censored. The slope's value is therefore an estimate that depends on the `lt_mult` or `gt_mult` parameters."
        },
        {
            'title': "Sample Size Below Minimum",
            'code': textwrap.dedent("""
                # The dataset size (5) is less than the specified min_size (10).
                x = [1, 2, 3, 4, 5]
                t = range(len(x))
                result = mks.trend_test(x, t, min_size=10)
                print(result.analysis_notes)
            """),
            'explanation': "A note indicating that the number of data points is below the recommended minimum size (`min_size`) for a reliable test."
        }
    ]

    # --- 2. Generate README Content ---
    readme_content = """
# Example 17: Interpreting Analysis Notes

The `MannKenSen` package includes a system of "Analysis Notes" to provide data quality warnings. These notes do not stop the analysis, but they alert you to potential issues in your dataset that could affect the reliability of the trend results.

This example demonstrates how to trigger and interpret the most common notes.
"""

    for scenario in scenarios:
        # Execute the code snippet and capture its stdout
        f = io.StringIO()
        with redirect_stdout(f):
            exec("import numpy as np; import pandas as pd; import MannKenSen as mks;" + scenario['code'])
        output_str = f.getvalue().strip()

        readme_content += f"""
### {scenario['title']}

**Analysis Note Produced:** `{output_str}`

**Explanation:** {scenario['explanation']}

**Code to Reproduce:**
```python
{scenario['code'].strip()}
```
"""

    # --- 3. Write the README file ---
    output_dir = os.path.dirname(__file__)
    readme_file_path = os.path.join(output_dir, 'README.md')
    with open(readme_file_path, 'w') as f:
        f.write(readme_content)

    print("Successfully generated README for Example 17.")

if __name__ == '__main__':
    generate_readme()
