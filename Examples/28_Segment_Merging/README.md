# Example 28: Merging Similar Segments

This example demonstrates how the `merge_similar_segments=True` option, combined with robust confidence intervals (via block bootstrapping), can simplify a model where the standard BIC criterion might select 'spurious' breakpoints.

## 1. The Data
We generated synthetic data representing a single constant trend (Slope=1.0) with a noise 'bump' in the middle. This localized disturbance mimics autocorrelation or a structural artifact, which often tricks statistical criteria into fitting multiple segments.

## 2. Before Merging (Standard BIC)
The standard analysis identified **2** breakpoints.

![Before Merging](plot_before.png)

### Segment Details
|    |    slope |   lower_ci |   upper_ci |
|---:|---------:|-----------:|-----------:|
|  0 | 0.953524 |   0.90358  |   0.997333 |
|  1 | 1.33342  |   1.04869  |   1.57051  |
|  2 | 0.914887 |   0.890638 |   0.942101 |

## 3. After Merging (With Block Bootstrap)
We enabled `merge_similar_segments=True` and `autocorr_method='block_bootstrap'` (with `block_size=8`). Block bootstrapping accounts for the serial correlation (the 'bump') by generating wider, more robust confidence intervals. The algorithm checked adjacent segments, and finding their confidence intervals overlapped, merged them.

The final merged model identified **0** breakpoints.

![After Merging](plot_after.png)

### Segment Details
|    |   slope |   lower_ci |   upper_ci |
|---:|--------:|-----------:|-----------:|
|  0 | 1.00068 |   0.942219 |    1.05682 |

## Conclusion
The merging process successfully removed all spurious breakpoints, correctly identifying the single underlying trend.