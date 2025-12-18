
# Example 17: Interpreting Analysis Notes

The `MannKenSen` package includes a system of "Analysis Notes" to provide data quality warnings. These notes do not stop the analysis, but they alert you to potential issues in your dataset that could affect the reliability of the trend results.

This example demonstrates how to trigger and interpret the most common notes.

### Insufficient Unique Values

**Analysis Note Produced:** `['< 3 unique values', 'WARNING: Sen slope based on tied non-censored values']`

**Explanation:** This note is triggered when there are fewer than 3 unique non-censored values. With such low variability, a meaningful trend analysis cannot be performed.

**Code to Reproduce:**
```python
# Data has fewer than 3 unique non-censored values.
x = [1, 1, 2, 2, 1, 1, 2, 2]
t = range(len(x))
result = mks.trend_test(x, t, min_size=None)
print(result.analysis_notes)
```

### Insufficient Non-Censored Values

**Analysis Note Produced:** `['< 5 Non-censored values', 'Long run of single value']`

**Explanation:** Triggered when there are fewer than 5 non-censored data points. The statistical power of the test is too low with such a small sample size.

**Code to Reproduce:**
```python
# Data has fewer than 5 non-censored values.
x_censored = ['<1', '<1', '<1', '<1', 5, 6, 7]
t = range(len(x_censored))
x = mks.prepare_censored_data(x_censored)
result = mks.trend_test(x, t, min_size=None)
print(result.analysis_notes)
```

### Long Run of a Single Value

**Analysis Note Produced:** `['Long run of single value']`

**Explanation:** Occurs if a significant portion of the data consists of a single, repeated value. This high number of ties can reduce the power of the Mann-Kendall test.

**Code to Reproduce:**
```python
# More than 50% of the data consists of a single value (3).
x = [1, 2, 3, 3, 3, 3, 3, 3, 4, 5]
t = range(len(x))
result = mks.trend_test(x, t)
print(result.analysis_notes)
```

### Tied Timestamps Without Aggregation

**Analysis Note Produced:** `['< 5 Non-censored values', 'sample size (4) below minimum (10)', 'tied timestamps present without aggregation']`

**Explanation:** Generated when the time vector `t` contains duplicate values and no aggregation method is specified. The Sen's slope calculation is sensitive to this and the result may be biased.

**Code to Reproduce:**
```python
# The timestamp 2001 is duplicated.
x = [1, 2, 3, 4]
t = [2000, 2001, 2001, 2002]
result = mks.trend_test(x, t, agg_method='none')
print(result.analysis_notes)
```

### Sen's Slope Influenced by Censored Data

**Analysis Note Produced:** `['< 5 Non-censored values', 'sample size (4) below minimum (10)', 'WARNING: Sen slope influenced by left-censored values.']`

**Explanation:** A `WARNING` that the median Sen's slope was calculated from a pair of data points where at least one was censored. The slope's value is therefore an estimate that depends on the `lt_mult` or `gt_mult` parameters.

**Code to Reproduce:**
```python
# The median slope is calculated from a pair involving a censored value.
x_censored = ['<10', 15, 5, 25]
t = [2000, 2001, 2002, 2003]
x = mks.prepare_censored_data(x_censored)
result = mks.trend_test(x, t)
print(result.analysis_notes)
```

### Sample Size Below Minimum

**Analysis Note Produced:** `['sample size (5) below minimum (10)']`

**Explanation:** A note indicating that the number of data points is below the recommended minimum size (`min_size`) for a reliable test.

**Code to Reproduce:**
```python
# The dataset size (5) is less than the specified min_size (10).
x = [1, 2, 3, 4, 5]
t = range(len(x))
result = mks.trend_test(x, t, min_size=10)
print(result.analysis_notes)
```
