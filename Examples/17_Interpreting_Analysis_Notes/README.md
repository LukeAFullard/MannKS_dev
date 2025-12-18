
# Example 17: Interpreting Analysis Notes

The `MannKenSen` package includes a system of "Analysis Notes" to provide data quality warnings. These notes do not stop the analysis, but they alert you to potential issues in your dataset that could affect the reliability of the trend results.

This example demonstrates how to trigger and interpret the most common notes.

### Insufficient Unique Values

**Analysis Note Produced:** `['< 3 unique values', 'sample size (8) below minimum (10)', 'WARNING: Sen slope based on tied non-censored values']`

**Explanation:** This note is triggered when there are fewer than 3 unique non-censored values. With such low variability, a trend analysis is not meaningful.

**Code to Reproduce:**
```python
import pandas as pd
import MannKenSen

# Data
x = [1, 1, 2, 2, 1, 1, 2, 2]
t = [0, 1, 2, 3, 4, 5, 6, 7]

# Analysis
result = MannKenSen.trend_test(x, t, **{})
print(result.analysis_notes)
```

### Insufficient Non-Censored Values

**Analysis Note Produced:** `['< 5 Non-censored values', 'sample size (7) below minimum (10)', 'Long run of single value']`

**Explanation:** Triggered when there are fewer than 5 non-censored data points available for the analysis.

**Code to Reproduce:**
```python
import pandas as pd
import MannKenSen

# Data
x_censored = ['<1', '<1', '<1', '<1', 5, 6, 7]\nx = MannKenSen.prepare_censored_data(x_censored)
t = [0, 1, 2, 3, 4, 5, 6]

# Analysis
result = MannKenSen.trend_test(x, t, **{})
print(result.analysis_notes)
```

### Long Run of a Single Value

**Analysis Note Produced:** `['Long run of single value']`

**Explanation:** Occurs if more than 50% of the data consists of a single, repeated value. This can heavily bias the Mann-Kendall test and reduce its power.

**Code to Reproduce:**
```python
import pandas as pd
import MannKenSen

# Data
x = [1, 2, 3, 3, 3, 3, 3, 3, 4, 5]
t = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Analysis
result = MannKenSen.trend_test(x, t, **{})
print(result.analysis_notes)
```

### Tied Timestamps Without Aggregation

**Analysis Note Produced:** `['< 5 Non-censored values', 'sample size (4) below minimum (10)', 'tied timestamps present without aggregation']`

**Explanation:** Generated when the time vector `t` contains duplicate values and the default `agg_method='none'` is used. The Sen's slope calculation can be sensitive to this.

**Code to Reproduce:**
```python
import pandas as pd
import MannKenSen

# Data
x = [1, 2, 3, 4]
t = [2000, 2001, 2001, 2002]

# Analysis
result = MannKenSen.trend_test(x, t, **{'agg_method': 'none'})
print(result.analysis_notes)
```

### Sen's Slope Influenced by Censored Data

**Analysis Note Produced:** `['< 5 Non-censored values', 'sample size (4) below minimum (10)']`

**Explanation:** This is a `WARNING` that the median Sen's slope was calculated from a pair of data points where at least one was censored. The slope's value is therefore an estimate based on the `lt_mult` or `gt_mult` parameters.

**Code to Reproduce:**
```python
import pandas as pd
import MannKenSen

# Data
x_censored = ['<1', 10, 12, 14]\nx = MannKenSen.prepare_censored_data(x_censored)
t = [2000, 2001, 2002, 2003]

# Analysis
result = MannKenSen.trend_test(x, t, **{})
print(result.analysis_notes)
```

### Sample Size Below Minimum

**Analysis Note Produced:** `['sample size (5) below minimum (10)']`

**Explanation:** A note indicating that the number of data points (n=5) is below the recommended minimum size (`min_size=10`) for a reliable test.

**Code to Reproduce:**
```python
import pandas as pd
import MannKenSen

# Data
x = [1, 2, 3, 4, 5]
t = [0, 1, 2, 3, 4]

# Analysis
result = MannKenSen.trend_test(x, t, **{'min_size': 10})
print(result.analysis_notes)
```
