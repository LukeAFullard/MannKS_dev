# v0.7.0 Development Plan: Generalized Quantile-Kendall

This document outlines the plan for implementing a **Generalized Quantile-Kendall Analysis** in `MannKS` v0.7.0. Unlike the specific implementation in USGS `EGRET` (which is hard-coded to 365 daily values), this implementation will be frequency-agnostic, supporting weekly, monthly, or irregular data over user-defined aggregation periods.

## Rationale

Environmental monitoring schemes vary widely. A user might have:

* **Weekly sampling** (~52/year) and want to test trends in the annual distribution.
* **Monthly sampling** (12/year) and want to test trends in the annual distribution.
* **Daily sampling** but need to aggregate over **5-year blocks** (e.g., to smooth out ENSO cycles).

The standard "Leap Year Reduction" ($366 \to 365$) is just a specific case of a general problem: **Length Standardization**. To compare the "$k$-th sorted value" across blocks, every block must be normalized to the same length or mapped to the same percentile grid.

## Core Feature: `quantile_trend_test`

The function will be redesigned to handle flexible blocking and resolution.

```python
def quantile_trend_test(
    x: pd.Series,
    t: pd.Series,
    block_frequency: str = 'YE',   # 'YE' (Yearly), '2YE' (2-Year), 'QS' (Quarterly)
    min_samples: int = 10,         # Minimum samples required per block to be valid
    quantiles: Union[str, int, list] = 'auto',
    **mk_kwargs
) -> QuantileResult:
    """
    Performs a generalized Quantile-Kendall trend test.

    Parameters
    ----------
    block_frequency : pandas offset alias
        The period over which to construct the distribution.
        e.g., 'YE' compares Annual distributions, '5YE' compares 5-Year distributions.
    quantiles : 'auto', int, or list of floats
        - 'auto': Detects the median sample size (N) and interpolates
                  all blocks to this length (preserving 'native' resolution).
        - int (e.g., 100): Interpolates data to 100 evenly spaced percentiles.
        - list (e.g., [0.1, 0.5, 0.9]): Computes only specific percentiles.
    """

```

## Algorithms

### 1. Flexible Blocking (The "Bucket" Step)

Instead of hard-coding "Water Year", we utilize pandas `Grouper` to bin data into user-defined periods.

* **User Input:** `block_frequency='2YE'` (2-Year blocks).
* **Action:** Group data into 2-year bins.
* **Validation:** Drop any bins that do not meet `min_samples` (e.g., a 2-year block with only 3 observations is statistically unsafe for quantile estimation).

### 2. Length Standardization (The "Normalization" Step)

To create the matrix $M$ (Blocks $\times$ Ranks), we must standardize the varying number of observations $N_{block}$ in each block (e.g., Year A has 52 weeks, Year B has 53 weeks).

**Strategy A: 'Auto' (Native Resolution Approximation)**
This effectively generalizes the "Leap Year Reduction."

1. Determine the **median sample size** ($N_{med}$) across all valid blocks.
2. For each block, interpolate the sorted values to exactly $N_{med}$ points using linear interpolation on the percentile scale.
* *Note:* Linear interpolation at 0.0 (min) and 1.0 (max) preserves the true extremes, which is critical for this analysis.



**Strategy B: Fixed Quantiles**
If the user requests `quantiles=100` (percentiles) or `quantiles=[0.05, 0.95]`:

1. Compute `np.percentile(block_data, q)` for each block.
2. This naturally handles varying sample sizes by mathematically estimating the value at that probability.

### 3. The Trend Loop

(Unchanged)

1. Construct Matrix $M$ where rows = Time Blocks, columns = Quantiles/Ranks.
2. Iterate through columns.
3. Run `MannKS.trend_test` on each column.

## Visualization

The `plot_quantile_kendall` function will be updated to reflect this flexibility.

* **X-Axis:** Labeled "Non-Exceedance Probability" (0 to 1).
* Since we aren't strictly using "Days" anymore, the x-axis will be generalized to **Probability**.
* We will retain the **Z-scale transformation** (Standard Normal Deviate) option, as it remains the best way to visualize tails regardless of sampling frequency.


* **Y-Axis:** Slope (Trend Magnitude).

## Migration of EGRET Logic

The specific "Leap Year Reduction" (averaging indices 182/183) is technically a form of **Nearest-Neighbor Interpolation**.

* **Decision:** We will use **Linear Interpolation** as the default for the 'auto' mode. It is mathematically smoother and generalizes better to "$52 \to 53$" (weekly) or "$12 \to 13$" (monthly) adjustments than the rigid "drop one value" method.

## Example Use Cases

### Case 1: Weekly Water Quality (Nitrate)

* **Data:** Weekly samples for 20 years.
* **Goal:** Are peak winter nitrate flushes increasing?
* **Code:**
```python
# block_frequency='YE' (Annual), quantiles='auto' (Approx 52 ranks)
result = quantile_trend_test(nitrate, dates, block_frequency='YE', quantiles='auto')

```



### Case 2: Daily Flow, Decadal Shifts

* **Data:** 50 years of daily flow.
* **Goal:** Compare distributions of 5-year epochs to smooth out ENSO noise.
* **Code:**
```python
# Aggregates 5 years of daily data (~1825 points) into one distribution
result = quantile_trend_test(flow, dates, block_frequency='5YE')

```



### Case 3: Sparse Data (Irregular)

* **Data:** Random sampling, 10-20 times per year.
* **Goal:** Trend in the median and 90th percentile.
* **Code:**
```python
# Interpolates to specific percentiles regardless of count (N)
result = quantile_trend_test(data, dates, quantiles=[0.5, 0.9])

```



## Implementation Roadmap

| Component | Priority | Notes |
| --- | --- | --- |
| **`mannks.quantile.resample_block`** | High | Helper to interpolate a block of $N$ values to $N_{target}$ points. |
| **`mannks.quantile.quantile_trend_test`** | High | Main driver. Replaces the rigid "Annual/Daily" logic with pandas Grouper. |
| **`mannks.plotting.plot_qk`** | Medium | Update x-axis to be purely probability-based, not "Day of Year". |
| **Tests** | High | Verify `block_frequency='YE'` matches standard behavior; verify `quantiles=list` works on irregular data. |
