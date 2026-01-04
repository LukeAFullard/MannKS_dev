# Example 28: Merging Similar Segments

This example demonstrates how the `merge_similar_segments=True` option can simplify a model where the standard BIC criterion might select 'spurious' breakpoints due to noise or minor irregularities.

## 1. The Data
We generated synthetic data representing a single constant trend (Slope=1.0) with a noise 'bump' in the middle. This pattern often tricks statistical criteria into fitting multiple segments.

## 2. Before Merging (Standard BIC)
The standard analysis identified **1** breakpoints.

![Before Merging](plot_before.png)

### Segment Details
|    |    slope |   lower_ci |   upper_ci |
|---:|---------:|-----------:|-----------:|
|  0 | 0.916232 |   0.824717 |   0.984288 |
|  1 | 0.993019 |   0.970558 |   1.01394  |

## 3. After Merging (Hypothesis Test)
We enabled `merge_similar_segments=True`. The algorithm checked adjacent segments. If their slope confidence intervals overlapped, they were considered indistinguishable, and the model was simplified.

The final merged model identified **0** breakpoints.

![After Merging](plot_after.png)

### Segment Details
|    |   slope |   lower_ci |   upper_ci |
|---:|--------:|-----------:|-----------:|
|  0 | 1.00238 |   0.990031 |    1.01533 |

## Conclusion
The merging process successfully removed unnecessary breakpoints, correctly identifying the underlying simple trend structure.