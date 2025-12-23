# Validation Case V-13: LWP Aggregation

## Objective
This validation case verifies the LWP-style temporal aggregation for a non-seasonal trend test. The data contains multiple samples for some time periods (months), requiring aggregation to one value per period for a standard LWP-TRENDS analysis.

## Data
A synthetic dataset of 70 samples over 60 months was generated with a positive slope. To test aggregation, 10 months were intentionally given a second data point. The data is non-censored.

![Trend Plot](trend_plot.png)

*Figure 1: Plot of the raw data, showing multiple samples in some months, and the Sen's slope calculated by the standard `mannkensen` method.*

## Analysis Code

```python
import pandas as pd
import numpy as np
import MannKenSen as mk

# Load data
data = pd.read_csv("data.csv", parse_dates=["time"])
x = data['value']
t = data['time']

# Run MannKenSen (Standard, no aggregation)
# This generates a warning for tied timestamps
mk_standard = mk.trend_test(x, t, slope_scaling='year')

# Run MannKenSen (LWP Mode, with monthly aggregation)
mk_lwp = mk.trend_test(
    x, t,
    slope_scaling='year',
    agg_method='lwp',
    agg_period='month',
    # Other LWP compatibility settings...
    mk_test_method='lwp',
    ci_method='lwp',
    sens_slope_method='lwp',
    tie_break_method='lwp'
)
```


## Results Comparison

| Metric              | MannKenSen (Standard) | MannKenSen (LWP Mode) | LWP-TRENDS R Script |
|---------------------|-----------------------|-----------------------|---------------------|
| p-value             | 0.000000   | 0.000000        | 0.000000     |
| Sen's Slope (/yr)   | 0.927039 | 0.926831    | 0.926831       |
| Lower CI (90%)      | 0.861091 | 0.853688 | 0.853688    |
| Upper CI (90%)      | 1.004820 | 1.009661 | 1.009661    |

**MannKenSen (Standard) Analysis Notes:**
`tied timestamps present without aggregation`

## Analysis
The **MannKenSen (Standard)** analysis was run on the raw, un-aggregated data. As expected, it produced an analysis note warning about tied timestamps, which can affect the Sen's slope calculation.

The **MannKenSen (LWP Mode)** analysis, with `agg_method='lwp'` and `agg_period='month'`, aggregates the data to one value per month before performing the trend test. This resolves the tied timestamp issue.

The results show that the **MannKenSen (LWP Mode)** outputs are nearly identical to those from the **LWP-TRENDS R Script**. This confirms that the monthly aggregation logic in `mannkensen` correctly emulates the behavior of the reference R script, which is a critical feature for LWP compatibility. The minor differences can be attributed to floating-point precision differences between Python and R.