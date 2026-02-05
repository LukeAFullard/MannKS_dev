# A Guide to Power Analysis for Surrogate Testing

Introduced in v0.6.0, `MannKS` provides a dedicated **Power Analysis** tool for surrogate data testing. This functionality allows you to answer a critical question when your trend test returns a non-significant result:

> *"If a trend actually existed, would I have been able to detect it given the noise in my data?"*

## Why Power Analysis Matters

When you test for a trend against a colored noise background (using `surrogate_test`), the "noise" (serial correlation) can be quite strong, making it hard to distinguish real trends from random wandering.

If your result is **not significant** ($p > 0.05$), there are two possibilities:
1.  **True Null:** There is no trend.
2.  **False Negative (Type II Error):** There is a trend, but it is too small to be detected against the background noise given your sample size.

Power analysis helps you distinguish between these two by calculating the **Minimum Detectable Trend (MDT)**.

## How It Works

The `power_test` function performs a Monte Carlo simulation:

1.  **Model the Noise:** It generates hundreds of synthetic noise realizations that share the spectral properties (autocorrelation) of your input data. These represent the "Null Hypothesis" world.
2.  **Inject Trends:** For each noise realization, it adds a known deterministic trend (Slope $\beta$).
3.  **Test for Significance:** It runs the `surrogate_test` on each synthetic series.
4.  **Calculate Power:** The "Power" for a given slope $\beta$ is the fraction of simulations where the trend was correctly identified as significant.

$$ \text{Power}(\beta) = P(\text{Significant Detection} \mid \text{True Trend} = \beta) $$

## Usage Example

### 1. Import and Prepare Data

```python
import numpy as np
import pandas as pd
from MannKS import power_test, trend_test

# Example: 10 years of monthly data
dates = pd.date_range("2010-01-01", periods=120, freq="ME")
values = np.random.randn(120)  # Your actual data
```

### 2. Define Slopes to Test

You need to define a range of slopes to test. Since the internal time unit is **seconds** (for datetime input), slopes should be specified in "units per second". However, that's hard to visualize.

**Tip:** Define slopes in "units per year" and convert them.

```python
# Define target slopes: 0, 0.5, 1.0, 1.5 units per year
slopes_per_year = np.array([0, 0.5, 1.0, 1.5, 2.0])
seconds_per_year = 365.25 * 24 * 3600

# Convert to units/second for the test
slopes_per_sec = slopes_per_year / seconds_per_year
```

### 3. Run the Power Test

```python
result = power_test(
    x=values,
    t=dates,
    slopes=slopes_per_sec,
    n_simulations=100,      # Number of noise realizations per slope
    n_surrogates=500,       # Surrogates used inside each test
    surrogate_method='auto' # 'iaaft' or 'lomb_scargle'
)
```

**Note:** This can be computationally expensive!
*   Total computations $\approx$ `n_slopes` $\times$ `n_simulations` $\times$ `n_surrogates`.
*   Start with lower numbers (e.g., `n_simulations=50`, `n_surrogates=200`) to test your setup.

### 4. Interpret Results

The `result` object (`PowerResult`) contains the key metrics.

```python
print("Power Analysis Results")
print("-" * 30)

# The MDT is the slope detected with 80% Power (by default)
if result.min_detectable_trend:
    mdt_per_year = result.min_detectable_trend * seconds_per_year
    print(f"Minimum Detectable Trend (80% Power): {mdt_per_year:.3f} units/year")
else:
    print("Could not determine MDT (increase max slope range)")

# View the full power curve table
df = result.simulation_results.copy()
df['slope_per_year'] = df['slope'] * seconds_per_year
print(df[['slope_per_year', 'power']])
```

**Example Output:**
```text
Power Analysis Results
------------------------------
Minimum Detectable Trend (80% Power): 1.250 units/year

   slope_per_year  power
0            0.00   0.05  <-- Power at 0 should be close to alpha (0.05)
1            0.50   0.24
2            1.00   0.65
3            1.50   0.92
4            2.00   1.00
```

## Interpreting the Outcome

*   **Observed Slope < MDT:** If your actual data has an estimated slope of 0.3 units/year, and the MDT is 1.25 units/year, you **cannot reliably distinguish** your observed trend from the background noise. The result is inconclusive.
*   **Observed Slope > MDT:** If your observed slope is 2.0 units/year, and MDT is 1.25, your trend is likely real (and the significance test should confirm this).

## Advanced Configuration

*   **`surrogate_method`**: Use `'lomb_scargle'` explicitly if you have irregular data, or `'iaaft'` for speed on even data.
*   **`alpha`**: Change the significance threshold (default 0.05).
*   **`surrogate_kwargs`**: Pass arguments like `{'dy': errors}` if your data has uncertainties.

```python
# Advanced usage with Lomb-Scargle and errors
result = power_test(
    x=values, t=dates, slopes=slopes,
    surrogate_method='lomb_scargle',
    surrogate_kwargs={'dy': errors, 'freq_method': 'log'}
)
```
