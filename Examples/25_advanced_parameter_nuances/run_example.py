"""
Example 25: Advanced Parameter Nuances

This example demonstrates several advanced or less common parameters in the
`MannKenSen` package to provide a more complete guide for users.

We will cover:
1. The difference between `tau_method='a'` and `tau_method='b'`.
2. The standalone use of the `classify_trend` function with a custom map.
3. The effect of the `min_size` and `min_size_per_season` parameters.
4. The use of `seasonal_trend_test` with a numeric time vector.
"""
import os
import numpy as np
import pandas as pd
from MannKenSen import trend_test, seasonal_trend_test, classify_trend

def generate_readme(results):
    """Generates the README.md file for this example."""
    # Use a standard multi-line string. Placeholders are for .format()
    # All literal braces in the python code blocks must be escaped (e.g., {{ ... }})
    readme_content = """
# Example 25: Advanced Parameter Nuances

This example demonstrates several advanced or less common parameters in the `MannKenSen` package to provide a more complete guide for users.

## 1. Tau Method ('a' vs. 'b')

Kendall's Tau has two common variants: Tau-a and Tau-b.

- **Tau-a** is the simplest form, calculated as `(concordant pairs - discordant pairs) / total pairs`. It does not account for ties in the data.
- **Tau-b** is more common in trend analysis as it corrects for ties in the data values. This is the default method in `MannKenSen`.

Let's see the difference with data that contains ties.

```python
# --- Section 1: Tau Method ---
print("--- 1. Tau Method ('a' vs. 'b') ---")
# Create data with ties in the values
t_tied = np.arange(10)
x_tied = [1, 2, 3, 3, 4, 5, 6, 6, 6, 7]

# Run the test with the default Tau-b (corrects for ties)
result_b = trend_test(x=x_tied, t=t_tied, min_size=5)
print(f"Tau-b (default): {{result_b.Tau:.4f}}")

# Run the test with Tau-a (does not correct for ties)
result_a = trend_test(x=x_tied, t=t_tied, tau_method='a', min_size=5)
print(f"Tau-a: {{result_a.Tau:.4f}}")
print("-" * 20)
```

**Output:**
```
--- 1. Tau Method ('a' vs. 'b') ---
Tau-b (default): {result_b.Tau:.4f}
Tau-a: {result_a.Tau:.4f}
--------------------
```
As you can see, Tau-b is higher because it correctly accounts for the tied values in the denominator of its calculation, providing a more accurate measure of correlation for this dataset.

---

## 2. Custom Trend Classification

The `classify_trend` function allows you to interpret the trend results with custom confidence labels. This is useful if your organization uses a different standard than the IPCC-style default.

```python
# --- Section 2: Custom Classification ---
print("--- 2. Custom Trend Classification ---")
# Create data with a reasonably clear trend
np.random.seed(42)
t_class = np.arange(20)
x_class = 0.5 * t_class + np.random.normal(0, 2, 20)

# Perform the trend test
result_class = trend_test(x=x_class, t=t_class)
print(f"Default classification: {{result_class.classification}}")

# Define a custom category map
custom_map = {{
    0.99: "Virtually Certain",
    0.95: "Extremely Likely",
    0.80: "Quite Likely",
    0.0: "Uncertain"
}}

# Use the standalone classify_trend function
custom_classification = classify_trend(result_class, category_map=custom_map)
print(f"Custom classification: {{custom_classification}}")
print("-" * 20)
```

**Output:**
```
--- 2. Custom Trend Classification ---
Default classification: {result_class.classification}
Custom classification: {custom_classification}
--------------------
```
The trend is strong enough to meet the `>0.99` threshold, so it gets the "Highly Likely" default label and the "Virtually Certain" custom label.

---

## 3. Minimum Sample Size (`min_size`)

The `trend_test` function will not run if the sample size is below a certain threshold (`min_size`, default=10), returning an "insufficient data" analysis note instead. You can override this for special cases.

```python
# --- Section 3: Minimum Sample Size ---
print("--- 3. Minimum Sample Size ---")
# Create a small dataset with only 8 data points
t_small = np.arange(8)
x_small = np.arange(8)

# Attempt to run with the default min_size=10
result_default_min = trend_test(x=x_small, t=t_small)
note_default_min = result_default_min.analysis_notes[0] if result_default_min.analysis_notes else 'ok'
print(f"Default min_size=10 Note: '{{note_default_min}}'")

# Run again with a lower min_size
result_custom_min = trend_test(x=x_small, t=t_small, min_size=8)
note_custom_min = result_custom_min.analysis_notes[0] if result_custom_min.analysis_notes else 'ok'
print(f"Custom min_size=8 Note: '{{note_custom_min}}'")
print(f"Custom min_size=8 Trend: '{{result_custom_min.trend}}'")
print("-" * 20)
```

**Output:**
```
--- 3. Minimum Sample Size ---
Default min_size=10 Note: '{note_default_min}'
Custom min_size=8 Note: '{note_custom_min}'
Custom min_size=8 Trend: '{result_custom_min.trend}'
--------------------
```
The first test fails due to insufficient data, while the second one runs successfully after lowering the `min_size` requirement.

---

## 4. Seasonal Test with Numeric Time

While `seasonal_trend_test` is often used with `datetime` objects, it also fully supports numeric time vectors. In this case, the `period` parameter is crucial as it defines the length of a full seasonal cycle in the same units as your time vector.

Here, we'll use a time vector measured in **days** and set `period=365` to analyze the annual cycle.

```python
# --- Section 4: Seasonal Test with Numeric Time ---
print("--- 4. Seasonal Test with Numeric Time ---")
# Create 5 years of daily data (numeric time vector in days)
t_numeric = np.arange(5 * 365)
# Create a seasonal pattern (e.g., higher values in the middle of the year)
# and a slight increasing trend
seasonal_cycle = np.sin(2 * np.pi * t_numeric / 365)
trend_component = 0.001 * t_numeric
x_numeric = seasonal_cycle + trend_component + np.random.normal(0, 0.5, len(t_numeric))

# Perform the seasonal test with the numeric time vector
# We must specify the period of the seasonal cycle (365 days)
result_numeric = seasonal_trend_test(
    x=x_numeric,
    t=t_numeric,
    period=365
)

print(f"Trend with numeric time: '{{result_numeric.trend}}'")
print(f"Slope: {{result_numeric.slope:.5f}} units per day")
print("-" * 20)
```

**Output:**
```
--- 4. Seasonal Test with Numeric Time ---
Trend with numeric time: '{result_numeric.trend}'
Slope: {result_numeric.slope:.5f} units per day
--------------------
```
The test correctly identifies the increasing trend within the strong seasonal pattern, demonstrating how to perform seasonal analysis on data without `datetime` timestamps.
"""
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "README.md")

    with open(output_path, "w") as f:
        f.write(readme_content.format(**results))
    print(f"README.md generated successfully at {output_path}")

def main():
    """Runs all parts of the example and generates the README."""
    results = {}

    # --- Section 1: Tau Method ---
    print("--- 1. Tau Method ('a' vs. 'b') ---")
    t_tied = np.arange(10)
    x_tied = [1, 2, 3, 3, 4, 5, 6, 6, 6, 7]
    results['result_b'] = trend_test(x=x_tied, t=t_tied, min_size=5)
    print(f"Tau-b (default): {results['result_b'].Tau:.4f}")
    results['result_a'] = trend_test(x=x_tied, t=t_tied, tau_method='a', min_size=5)
    print(f"Tau-a: {results['result_a'].Tau:.4f}")
    print("-" * 20)

    # --- Section 2: Custom Classification ---
    print("--- 2. Custom Trend Classification ---")
    np.random.seed(42)
    t_class = np.arange(20)
    x_class = 0.5 * t_class + np.random.normal(0, 2, 20)
    results['result_class'] = trend_test(x=x_class, t=t_class)
    print(f"Default classification: {results['result_class'].classification}")
    custom_map = {
        0.99: "Virtually Certain",
        0.95: "Extremely Likely",
        0.80: "Quite Likely",
        0.0: "Uncertain"
    }
    results['custom_classification'] = classify_trend(results['result_class'], category_map=custom_map)
    print(f"Custom classification: {results['custom_classification']}")
    print("-" * 20)

    # --- Section 3: Minimum Sample Size ---
    print("--- 3. Minimum Sample Size ---")
    t_small = np.arange(8)
    x_small = np.arange(8)
    result_default_min = trend_test(x=x_small, t=t_small)
    results['note_default_min'] = result_default_min.analysis_notes[0] if result_default_min.analysis_notes else 'ok'
    print(f"Default min_size=10 Note: '{results['note_default_min']}'")

    results['result_custom_min'] = trend_test(x=x_small, t=t_small, min_size=8)
    results['note_custom_min'] = results['result_custom_min'].analysis_notes[0] if results['result_custom_min'].analysis_notes else 'ok'
    print(f"Custom min_size=8 Note: '{results['note_custom_min']}'")
    print(f"Custom min_size=8 Trend: '{results['result_custom_min'].trend}'")
    print("-" * 20)

    # --- Section 4: Seasonal Test with Numeric Time ---
    print("--- 4. Seasonal Test with Numeric Time ---")
    t_numeric = np.arange(5 * 365)
    seasonal_cycle = np.sin(2 * np.pi * t_numeric / 365)
    trend_component = 0.001 * t_numeric
    x_numeric = seasonal_cycle + trend_component + np.random.normal(0, 0.5, len(t_numeric))
    results['result_numeric'] = seasonal_trend_test(
        x=x_numeric,
        t=t_numeric,
        period=365
    )
    print(f"Trend with numeric time: '{results['result_numeric'].trend}'")
    print(f"Slope: {results['result_numeric'].slope:.5f} units per day")
    print("-" * 20)

    generate_readme(results)

if __name__ == "__main__":
    main()
