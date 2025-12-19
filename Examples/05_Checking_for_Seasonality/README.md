
# Example 05: Checking For & Visualizing Seasonality

Before running a seasonal trend test, it's essential to determine if your data actually exhibits a seasonal pattern. This example demonstrates how to use the `check_seasonality` and `plot_seasonal_distribution` functions to verify a suspected seasonal pattern.

## Python Code

```python
import numpy as np
import pandas as pd
import MannKenSen as mks

# --- Data Generation ---
# Create a synthetic dataset with a clear seasonal pattern but no long-term trend.
# We generate data with one record per month ('MS' frequency).
np.random.seed(42)
n_years = 10
dates = pd.to_datetime(pd.date_range(start='2010-01-01', periods=n_years * 12, freq='MS'))

# Create a seasonal cycle (e.g., higher values in summer)
seasonal_cycle = 10 * np.sin(np.linspace(0, 2 * np.pi * n_years, n_years * 12))
noise = np.random.normal(0, 2, n_years * 12)
data = 50 + seasonal_cycle + noise

# --- Analysis ---
# Step 1: Visually inspect the data for a suspected seasonal pattern.
# We suspect a 'month' pattern, so we specify it explicitly.
plot_filename = "seasonal_distribution_plot.png"
mks.plot_seasonal_distribution(x_old=data, t_old=dates, season_type='month', save_path=plot_filename)
print(f"Plot saved to {plot_filename}")

# Step 2: Statistically verify the suspected seasonal pattern.
# We explicitly test for 'month' seasonality.
seasonality_result = mks.check_seasonality(x_old=data, t_old=dates, season_type='month')
print("\n--- Statistical Seasonality Check ---")
print(seasonality_result)
```

## Output

### Plot Generation and Statistical Results
```
Plot saved to seasonal_distribution_plot.png

--- Statistical Seasonality Check ---
Seasonality_Test(h_statistic=np.float64(108.02049586776855), p_value=np.float64(4.549364352713582e-18), is_seasonal=np.True_, seasons_tested=[np.int32(1), np.int32(2), np.int32(3), np.int32(4), np.int32(5), np.int32(6), np.int32(7), np.int32(8), np.int32(9), np.int32(10), np.int32(11), np.int32(12)], seasons_skipped=[])
```

### Seasonal Distribution Plot
![Seasonal Distribution Plot](seasonal_distribution_plot.png)


### Interpretation

This example demonstrates the correct workflow for starting a seasonal analysis. The goal is to first form a hypothesis about the type of seasonality in your data (e.g., monthly) and then use the `MannKenSen` tools to verify it.

**The `check_seasonality` function is a verification tool, not a discovery tool.** You tell it *what kind of seasonality to check for* (e.g., `'month'`, `'quarter'`). It does not automatically find the "best" seasonal period for you.

1.  **Forming a Hypothesis (Visual Inspection):**
    -   Before any statistical test, it's best practice to plot your data. The `plot_seasonal_distribution` function is designed for this. We explicitly set `season_type='month'` because we suspect a monthly pattern.
    -   The resulting box plot clearly shows a cyclical pattern, with values peaking in the summer months (7-Jul, 8-Aug). This visual evidence supports our hypothesis of monthly seasonality.

2.  **Verifying the Hypothesis (Statistical Test):**
    -   Now we use `check_seasonality`, again explicitly setting `season_type='month'`, to get a statistical measure of our observation.
    -   The function returns an extremely small **p-value** (`< 0.001`). This tells us that the monthly pattern we see is statistically significant and not a result of random chance.
    -   The output `is_seasonal=True` confirms our hypothesis.
    -   The `seasons_tested=[1, 2, ..., 12]` field shows that the function tested for 12 distinct seasons (January to December), which are represented by integers.

3.  **A Note on Aggregation:**
    -   In this example, we did not need to use the `agg_method` parameter. This is because our data was generated with `freq='MS'` (Month Start), guaranteeing only one data point for each month. If you have data where multiple measurements can occur in the same month of the same year, you would need to use aggregation.

**Conclusion: What to do Next**

Because we have confirmed our hypothesis that the data has a significant **monthly** seasonal pattern, the correct next step is to use the `seasonal_trend_test` function, configured specifically for that pattern: `seasonal_trend_test(..., season_type='month')`.
