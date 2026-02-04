# v0.7.0 Development Plan: Quantile-Kendall Analysis

This document outlines the plan for introducing **Quantile-Kendall Analysis** to the `MannKS` package in version 0.7.0. This major feature addition brings `MannKS` to parity with the USGS `EGRET` R package, enabling users to detect trends across the entire probability distribution of a variable (e.g., changes in flood magnitude vs. baseflow) rather than just the central tendency.

## Rationale

Standard trend tests (Mann-Kendall on mean/median) often mask complex environmental behaviors. For example, a river may show no significant trend in average flow but a significant increase in extreme flood events (99th percentile) or a decrease in drought flows (5th percentile).

**Quantile-Kendall** (Hirsch et al.) addresses this by:
1.  Treating every day of the year (sorted by magnitude) as a distinct time series.
2.  Visualizing the trend slope as a function of "exceedance probability."
3.  Revealing whether changes are driven by shifts in the background signal or changes in extreme events.

## Proposed Features

We will introduce a new module `mannks.quantile` containing the logic for high-resolution distribution trending.

### 1. `quantile_trend_test` Function

This is the primary user-facing function. It orchestrates the data transformation, leap-year adjustment, and iterative trend testing.

```python
def quantile_trend_test(
    x: pd.Series,         # High-frequency values (e.g., Daily Discharge)
    t: pd.Series,         # Datetime index
    season: Tuple[int, int] = None,  # (start_month, duration_months)
    slope_scaling: str = 'year',
    **mk_kwargs           # Arguments passed to core trend_test (e.g. alpha)
) -> QuantileResult:
    """
    Performs the USGS Quantile-Kendall trend test.

    Returns a result object containing 365 separate trend tests,
    mapping the distribution of the variable over time.
    """

```

### 2. Algorithms

#### A. Leap Year Reduction (The "Stacking" Problem)

To analyze the "1st order statistic" (smallest value) across years, every year must have an identical number of observations ($D$).

* **Standard Year:** $D=365$.
* **Leap Year:** $D=366$.
* **Algorithm:** We will implement the `EGRET` reduction method:
1. Sort the 366 daily values of the leap year.
2. Identify the middle two values (indices 182 and 183).
3. Replace them with their mean.
4. Resulting vector length is 365.


* **Seasonal Handling:** If a custom season is defined (e.g., March-June), the target $D$ is the number of days in that season for a non-leap year.

#### B. The Iterative Test Loop

1. **Matrix Construction:** Construct a matrix $M$ of shape `[n_years, n_daily_ranks]`.
* $M_{y, r}$ = The $r$-th lowest value observed in Year $y$.


2. **Vectorized Testing:** Iterate through columns $r$:
* Extract time series $TS_r = M_{:, r}$.
* Run `MannKS.trend_test(TS_j, years)`.
* Store `slope`, `p_value`, and `significance_code`.



#### C. Probability Scaling (Z-Scale)

To visualize the results effectively, we map the rank to a Z-score (Standard Normal Deviate). This expands the X-axis at the tails (high/low extremes) where trends are often most critical.

* $P = (r - 0.4) / (D + 0.2)$
* $Z = \text{norm.ppf}(P)$

### 3. Visualization: `plot_quantile_kendall`

A specialized plotting function to replicate the distinct USGS visual style.

* **X-Axis:** Daily Non-Exceedance Probability (formatted as probability, plotted on Z-scale).
* **Y-Axis:** Sen's Slope (Trend Magnitude).
* **Data Points:** 365 dots representing the trend at each slice of the distribution.
* **Color Coding:**
* 🔴 **Red:** Significant ($p < 0.05$)
* ⚫ **Black:** Near Significant ($0.05 < p < 0.1$)
* ⚪ **Grey:** Not Significant ($p > 0.1$)



## Implementation Roadmap

| Component | Description | Complexity |
| --- | --- | --- |
| **`mannks.quantile.adjust_leap`** | Helper to perform the 366->365 reduction logic. | Low |
| **`mannks.quantile.matrix_builder`** | Logic to group data by Water Year (or custom season) and build the rank matrix. | Medium |
| **`mannks.quantile.quantile_test`** | The main loop calling `trend_test`. | Low |
| **`mannks.plotting.plot_qk`** | Matplotlib logic for the Z-scale axis and significance coloring. | Medium |
| **Documentation** | New guide "Quantile-Kendall Analysis" comparing it to standard Mann-Kendall. | Medium |

## Validation Strategy

To ensure parity with `EGRET`, we will use the following validation tests:

1. **Leap Year Integrity:**
* Input: A synthesized leap year of data (integers 1..366).
* Check: Output length is 365.
* Check: The removed value is the average of 183 and 184.
* Check: Min and Max values are preserved exactly.


2. **Tie Handling (Zero Slopes):**
* Input: A dataset dominated by detection limits (e.g., 50% of values are `<0.1`).
* Expectation: The lower 50% of order statistics should return a slope of 0.0 without errors.


3. **Seasonality Check:**
* Input: `season=(3, 4)` (March, 4 months).
* Check: Only data from Mar-Jun is used.
* Check: Matrix columns equal the number of days in Mar-Jun (122).



## User Example

```python
from MannKS import quantile_trend_test, plot_quantile_kendall

# 1. Run the test on daily flow data
# Automatically handles Water Years and Leap Years
qk_result = quantile_trend_test(
    df['flow'],
    df['date'],
    slope_scaling='year'
)

# 2. Visualize
# Shows trends for droughts (left) vs floods (right)
fig = plot_quantile_kendall(
    qk_result,
    title="Choptank River: Trends in Extremes"
)

```
