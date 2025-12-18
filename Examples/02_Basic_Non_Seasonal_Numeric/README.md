
# Example 2: Basic Non-Seasonal Trend Test (Numeric Time)

This example demonstrates the simplest use case of the `MannKenSen` package: performing a non-seasonal trend test on a dataset with a simple numeric time vector (e.g., `[0, 1, 2, ...]`).

## The Python Script

The following script generates 50 data points with a clear upward trend and runs the `trend_test` function to perform the analysis.

```python

import numpy as np
import MannKenSen as mks

# 1. Generate Synthetic Data
# This demonstrates the simplest use case with a numeric time vector.
np.random.seed(42)
n_samples = 50
time = np.arange(n_samples)

# Create data with a clear upward trend (slope of approx. 0.1)
values = (0.1 * time) + np.random.normal(0, 0.5, n_samples)

# 2. Perform the Trend Test
result = mks.trend_test(x=values, t=time)

# 3. Print the full result
print(result)

```

## Command Output

Running the script prints the full `Mann_Kendall_Test` namedtuple containing all the results of the analysis.

```
Mann_Kendall_Test(trend='increasing', h=np.True_, p=np.float64(2.220446049250313e-16), z=np.float64(8.21429032830394), Tau=np.float64(0.8024489795918367), s=np.float64(983.0), var_s=np.float64(14291.666666666666), slope=np.float64(0.09382043613738501), intercept=np.float64(0.0681216933263471), lower_ci=np.float64(0.0840984564361), upper_ci=np.float64(0.10348481235419449), C=0.9999999999999999, Cd=1.1102230246251565e-16, classification='Highly Likely Increasing', analysis_notes=[], sen_probability=np.float64(1.1205931662517975e-16), sen_probability_max=np.float64(1.1205931662517975e-16), sen_probability_min=np.float64(1.1205931662517975e-16), prop_censored=np.float64(0.0), prop_unique=1.0, n_censor_levels=0)
```

## Interpretation of Results
The most critical fields for a quick interpretation are:
-   **`p`**: The p-value is extremely low (close to zero), which is well below the standard significance level of 0.05. This indicates a **statistically significant** trend.
-   **`slope`**: The Sen's slope is `~0.1`. Since it's positive, the trend is **increasing**. The value is the estimated rate of change per unit of time.
-   **`classification`**: The final classification of **'Highly Likely Increasing'** provides a clear, human-readable summary, confirming the significant increasing trend.

**Conclusion:** This basic example shows the fundamental workflow for performing a trend test on simple numeric data.
