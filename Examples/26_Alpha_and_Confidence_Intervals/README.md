# Example 26: Alpha and Confidence Intervals

This example demonstrates how the `alpha` parameter influences the **Confidence Intervals (CI)** of the Sen's slope and the final trend classification.

## The Role of Alpha
The `alpha` parameter sets the significance level for the confidence intervals.
*   **Lower `alpha` (e.g., 0.05):** corresponds to a **higher confidence level** (e.g., 95%). This produces a **wider** interval because we want to be more certain that the true slope lies within it.
*   **Higher `alpha` (e.g., 0.40):** corresponds to a **lower confidence level** (e.g., 60%). This produces a **narrower** interval because we are accepting a higher risk that the true slope is outside the range.

## Synthetic Data
We generate a dataset with a clear increasing trend and some random noise.

```python
import numpy as np
import pandas as pd
import MannKS as mk

# Generate Data
np.random.seed(42)
n = 30
dates = pd.date_range(start='2020-01-01', periods=n, freq='ME')
values = np.linspace(10, 20, n) + np.random.normal(0, 2, n)
```

## Analysis with alpha = 0.05
This corresponds to a **95% Confidence Interval**.

```python
result = mk.trend_test(
    x=values,
    t=dates,
    alpha=0.05,
    slope_scaling='year',
    plot_path='plot_alpha_0.05.png'
)
print(result)
```

**Output:**
```
Mann_Kendall_Test(trend='increasing', h=np.True_, p=np.float64(2.0777186033882344e-06), z=np.float64(4.74571424693142), Tau=np.float64(0.6137931034482759), s=np.float64(267.0), var_s=np.float64(3141.6666666666665), slope=np.float64(3.3061932849808984), intercept=np.float64(-155.42495892708274), lower_ci=np.float64(2.4519195803204368), upper_ci=np.float64(4.0831690185164975), C=0.9999989611406983, Cd=1.0388593016941172e-06, classification='Highly Likely Increasing', analysis_notes=[], sen_probability=np.float64(9.817086049817115e-07), sen_probability_max=np.float64(9.817086049817115e-07), sen_probability_min=np.float64(9.817086049817115e-07), prop_censored=np.float64(0.0), prop_unique=1.0, n_censor_levels=0, slope_per_second=np.float64(1.0476694314462755e-07), lower_ci_per_second=np.float64(7.7696642974131e-08), upper_ci_per_second=np.float64(1.2938781841827318e-07), scaled_slope=np.float64(3.3061932849808984), slope_units='units per year')
```

![Trend Plot alpha=0.05](plot_alpha_0.05.png)

**Interpretation:**
*   **Slope:** 3.3062 units/year
*   **Confidence Interval:** [2.4519, 4.0832]
*   **Width of Interval:** 1.6312

Notice that the interval width for alpha=0.05 is **wider** compared to the others.

## Analysis with alpha = 0.2
This corresponds to a **80% Confidence Interval**.

```python
result = mk.trend_test(
    x=values,
    t=dates,
    alpha=0.2,
    slope_scaling='year',
    plot_path='plot_alpha_0.2.png'
)
print(result)
```

**Output:**
```
Mann_Kendall_Test(trend='increasing', h=np.True_, p=np.float64(2.0777186033882344e-06), z=np.float64(4.74571424693142), Tau=np.float64(0.6137931034482759), s=np.float64(267.0), var_s=np.float64(3141.6666666666665), slope=np.float64(3.3061932849808984), intercept=np.float64(-155.42495892708274), lower_ci=np.float64(2.8098816639004567), upper_ci=np.float64(3.881602397198264), C=0.9999989611406983, Cd=1.0388593016941172e-06, classification='Highly Likely Increasing', analysis_notes=[], sen_probability=np.float64(9.817086049817115e-07), sen_probability_max=np.float64(9.817086049817115e-07), sen_probability_min=np.float64(9.817086049817115e-07), prop_censored=np.float64(0.0), prop_unique=1.0, n_censor_levels=0, slope_per_second=np.float64(1.0476694314462755e-07), lower_ci_per_second=np.float64(8.903977691270745e-08), upper_ci_per_second=np.float64(1.2300055762156388e-07), scaled_slope=np.float64(3.3061932849808984), slope_units='units per year')
```

![Trend Plot alpha=0.2](plot_alpha_0.2.png)

**Interpretation:**
*   **Slope:** 3.3062 units/year
*   **Confidence Interval:** [2.8099, 3.8816]
*   **Width of Interval:** 1.0717

Notice that the interval width for alpha=0.2 is **intermediate** compared to the others.

## Analysis with alpha = 0.4
This corresponds to a **60% Confidence Interval**.

```python
result = mk.trend_test(
    x=values,
    t=dates,
    alpha=0.4,
    slope_scaling='year',
    plot_path='plot_alpha_0.4.png'
)
print(result)
```

**Output:**
```
Mann_Kendall_Test(trend='increasing', h=np.True_, p=np.float64(2.0777186033882344e-06), z=np.float64(4.74571424693142), Tau=np.float64(0.6137931034482759), s=np.float64(267.0), var_s=np.float64(3141.6666666666665), slope=np.float64(3.3061932849808984), intercept=np.float64(-155.42495892708274), lower_ci=np.float64(2.9892007668904217), upper_ci=np.float64(3.7039043255947157), C=0.9999989611406983, Cd=1.0388593016941172e-06, classification='Highly Likely Increasing', analysis_notes=[], sen_probability=np.float64(9.817086049817115e-07), sen_probability_max=np.float64(9.817086049817115e-07), sen_probability_min=np.float64(9.817086049817115e-07), prop_censored=np.float64(0.0), prop_unique=1.0, n_censor_levels=0, slope_per_second=np.float64(1.0476694314462755e-07), lower_ci_per_second=np.float64(9.472205639498636e-08), upper_ci_per_second=np.float64(1.1736964552420703e-07), scaled_slope=np.float64(3.3061932849808984), slope_units='units per year')
```

![Trend Plot alpha=0.4](plot_alpha_0.4.png)

**Interpretation:**
*   **Slope:** 3.3062 units/year
*   **Confidence Interval:** [2.9892, 3.7039]
*   **Width of Interval:** 0.7147

Notice that the interval width for alpha=0.4 is **narrower** compared to the others.
