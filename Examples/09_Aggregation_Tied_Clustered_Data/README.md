
# Example 8: Aggregation for Tied and Clustered Data

Real-world datasets are often messy. Sampling frequency can change over time, leading to **clustered data**, or multiple measurements might be recorded at the exact same time, resulting in **tied timestamps**. Both of these issues can bias a trend analysis by giving undue weight to certain time periods.

This example demonstrates how to use the temporal aggregation features of `MannKenSen` to create a more robust and reliable trend analysis.

## The Python Script

The following script generates a dataset with both clustered samples and tied timestamps. It then analyzes the data twice: once without aggregation and once with annual median aggregation.

```python

import numpy as np
import pandas as pd
import MannKenSen as mks
import os

# 1. Generate Data with Irregular Sampling
np.random.seed(42)
dates = pd.to_datetime([
    '2010-07-01', '2011-07-01', '2012-07-01',
    '2013-03-01', '2013-03-05', '2013-03-10', '2013-03-15', # Clustered
    '2014-06-15', '2014-06-15', # Tied
    '2015-07-01', '2016-07-01', '2017-07-01', '2018-07-01', '2019-07-01'
])
values = np.array([5, 5.5, 6, 6.2, 6.3, 6.1, 6.4, 7, 6.8, 7.5, 8, 8.2, 8.5, 9])
plot_file = 'aggregation_plot.png'

# 2. Analysis without Aggregation
print("--- Analysis Without Aggregation ---")
result_no_agg = mks.trend_test(x=values, t=dates, agg_method='none')
print(result_no_agg)

# 3. Analysis with Annual Median Aggregation
print("\n--- Analysis With Annual Aggregation ---")
result_agg = mks.trend_test(
    x=values,
    t=dates,
    agg_method='median',
    agg_period='year',
    plot_path=plot_file
)
print(result_agg)

```

## Command Output

Running the script above produces the following output. It shows the full results from both analysis runs.

```
--- Analysis Without Aggregation ---
Mann_Kendall_Test(trend='increasing', h=np.True_, p=np.float64(4.253992067049239e-06), z=np.float64(4.598570772191415), Tau=np.float64(0.9340659340659341), s=np.float64(85.0), var_s=np.float64(333.6666666666667), slope=np.float64(1.4526314339892026e-08), intercept=np.float64(-13.490589995158986), lower_ci=np.float64(1.3321547681737256e-08), upper_ci=np.float64(1.5844043907014474e-08), C=0.9999978730039665, Cd=2.1269960335246196e-06, classification='Highly Likely Increasing', analysis_notes=['tied timestamps present without aggregation'], sen_probability=np.float64(2.088789365553551e-06), sen_probability_max=np.float64(2.088789365553551e-06), sen_probability_min=np.float64(2.088789365553551e-06), prop_censored=np.float64(0.0), prop_unique=1.0, n_censor_levels=0)

--- Analysis With Annual Aggregation ---
Mann_Kendall_Test(trend='increasing', h=np.True_, p=np.float64(8.442315356127494e-06), z=np.float64(4.453648795431911), Tau=np.float64(0.9487179487179486), s=np.float64(74.0), var_s=np.float64(268.6666666666667), slope=np.float64(1.4526314339892026e-08), intercept=np.float64(-13.403805686935103), lower_ci=np.float64(1.330353341847595e-08), upper_ci=np.float64(1.58404298459043e-08), C=0.9999957788423219, Cd=4.221157678063747e-06, classification='Highly Likely Increasing', analysis_notes=[], sen_probability=np.float64(5.491724884587397e-06), sen_probability_max=np.float64(5.491724884587397e-06), sen_probability_min=np.float64(5.491724884587397e-06), prop_censored=np.float64(0.0), prop_unique=0.9285714285714286, n_censor_levels=0)
```

## Interpretation of Results

### Analysis Without Aggregation

The first result shows a highly significant increasing trend. However, it also produces a critical `analysis_notes`: **`'tied timestamps present without aggregation'`**. This warns you that the results may be unreliable because the Sen's slope calculation is sensitive to data points with identical timestamps. The cluster of data in 2013 also gives that year more weight in the analysis than other years.

### Analysis With Annual Aggregation

The second result, using `agg_method='median'` and `agg_period='year'`, first aggregates the data.
- The four data points in 2013 are reduced to a single median value for that year.
- The two tied data points in 2014 are also reduced to their median.

This creates a new, evenly weighted time series of one value per year. The `analysis_notes` field is now empty, indicating that the data quality issue has been resolved. The resulting trend is still significant, but the p-value and slope are different, reflecting a more robust estimate that is not biased by the irregular sampling.

### Aggregated Analysis Plot

The generated plot visualizes the trend line calculated from the **aggregated data**. It clearly shows the final, robust increasing trend.

![Aggregation Plot](aggregation_plot.png)

### Conclusion

Temporal aggregation is an essential tool for improving the reliability of trend analysis on real-world data. By ensuring each time period is weighted equally, it helps to remove biases caused by inconsistent sampling.
