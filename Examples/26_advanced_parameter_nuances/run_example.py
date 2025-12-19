
import os
import numpy as np
import pandas as pd
import MannKenSen as mks
import textwrap
import io
from contextlib import redirect_stdout

def generate_readme():
    """
    Generates a comprehensive README.md file for Example 25, demonstrating
    several advanced or less common parameters.
    """
    # --- 1. Define Paths and Code Blocks for each section ---
    output_dir = os.path.dirname(__file__)

    # --- Section 1: Tau Method ---
    code_tau = textwrap.dedent("""
        import numpy as np
        from MannKenSen import trend_test

        # Create data with ties in the values
        t_tied = np.arange(10)
        x_tied = [1, 2, 3, 3, 4, 5, 6, 6, 6, 7]

        # Run with default Tau-b (corrects for ties)
        result_b = trend_test(x=x_tied, t=t_tied, min_size=5)
        print(f"Tau-b (default): {result_b.Tau:.4f}")

        # Run with Tau-a (does not correct for ties)
        result_a = trend_test(x=x_tied, t=t_tied, tau_method='a', min_size=5)
        print(f"Tau-a: {result_a.Tau:.4f}")
    """)

    # --- Section 2: Custom Classification ---
    code_classify = textwrap.dedent("""
        import numpy as np
        from MannKenSen import trend_test, classify_trend

        np.random.seed(42)
        t_class = np.arange(20)
        x_class = 0.5 * t_class + np.random.normal(0, 2, 20)
        result_class = trend_test(x=x_class, t=t_class)
        print(f"Default classification: {result_class.classification}")

        custom_map = {0.99: "Virtually Certain", 0.95: "Extremely Likely", 0.80: "Quite Likely", 0.0: "Uncertain"}
        custom_classification = classify_trend(result_class, category_map=custom_map)
        print(f"Custom classification: {custom_classification}")
    """)

    # --- Section 3: Min Size ---
    code_min_size = textwrap.dedent("""
        import numpy as np
        from MannKenSen import trend_test

        t_small = np.arange(8)
        x_small = np.arange(8)

        result_default_min = trend_test(x=x_small, t=t_small)
        print(f"Default min_size=10 Note: '{result_default_min.analysis_notes[0]}'")

        result_custom_min = trend_test(x=x_small, t=t_small, min_size=8)
        print(f"Custom min_size=8 Trend: '{result_custom_min.trend}'")
    """)

    # --- Section 4: Seasonal with Numeric Time ---
    code_seasonal_numeric = textwrap.dedent("""
        import numpy as np
        from MannKenSen import seasonal_trend_test

        t_numeric = np.arange(5 * 365)
        seasonal_cycle = np.sin(2 * np.pi * t_numeric / 365)
        trend_component = 0.001 * t_numeric
        x_numeric = seasonal_cycle + trend_component + np.random.normal(0, 0.5, len(t_numeric))

        result_numeric = seasonal_trend_test(x=x_numeric, t=t_numeric, period=365)
        print(f"Trend: '{result_numeric.trend}', Slope: {result_numeric.slope:.5f} units/day")
    """)

    sections = [
        ("1. Tau Method ('a' vs. 'b')", code_tau),
        ("2. Custom Trend Classification", code_classify),
        ("3. Minimum Sample Size (`min_size`)", code_min_size),
        ("4. Seasonal Test with Numeric Time", code_seasonal_numeric)
    ]

    # --- 2. Construct the README ---
    readme_content = "# Example 25: Advanced Parameter Nuances\\n\\n"
    readme_content += "This example demonstrates several advanced or less common parameters in the `MannKenSen` package.\\n"

    for title, code in sections:
        f = io.StringIO()
        with redirect_stdout(f):
            exec(code)
        output_str = f.getvalue().strip()

        readme_content += f"""
---
## {title}
```python
{code.strip()}
```
**Output:**
```
{output_str}
```
"""

    # --- 3. Write the README file ---
    readme_file_path = os.path.join(output_dir, 'README.md')
    with open(readme_file_path, 'w') as f:
        f.write(readme_content)

    print("Successfully generated README for Example 25.")

if __name__ == '__main__':
    generate_readme()
