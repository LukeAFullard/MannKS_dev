# Continuous Confidence Levels for Trend Direction

### Purpose

The method replaces binary “significant / not significant” hypothesis testing with a **continuous probability-based measure of confidence in trend direction** (increasing or decreasing). It is designed for environmental monitoring data where decision-making depends on *how confident* we are that a trend is real, not merely whether it passes an arbitrary p-value threshold.

---

### Core idea

Instead of testing whether a trend equals zero, the method asks:

> *What is the probability that the inferred trend direction is correct?*

This probability is reported directly as a **confidence value between 0.5 and 1.0**.

---

## 1. Site-level confidence in trend direction

### Trend estimation

* A monotonic trend is estimated using **Mann–Kendall** (or Seasonal Kendall) statistics.
* The Mann–Kendall statistic $S$ (sometimes denoted as $\hat{S}$ for the observed value) measures the balance of increasing vs decreasing observation pairs.
* In this text, $\hat{S}$ refers to the observed statistic calculated from the sample data.

### Statistical model

* The *true* (population) value of trend strength $S$ is treated as a random variable.
* Its **posterior distribution** is approximated by a **Normal distribution**:

  * Mean = observed $\hat{S}$
  * Variance = $\mathrm{Var}(S)$ (standard Mann–Kendall variance, including tie/censoring adjustments if needed)

**Assumption**: This normal approximation holds when the sample size $n \ge 10$. For smaller sample sizes, the exact distribution of $S$ should ideally be used, though the package currently relies on the normal approximation.

### Confidence calculation

* **Confidence in trend direction** ($C_\tau$) is defined as the **probability that the true $S$ has the same sign as $\hat{S}$**.
* Mathematically, this is the **area of the posterior distribution on the same side of zero as $\hat{S}$**.

Interpretation:

* $C_\tau = 0.5$: no directional information (comparable to $p=1.0$)
* $C_\tau \to 1$: near certainty that the trend direction is correct (comparable to $p \to 0$)

> Importantly, the method **never concludes “no trend”**—only weaker or stronger confidence in a direction. Even a trend with $p=0.99$ will be assigned a direction (based on the sign of $S$) with a confidence near 0.5. This prevents "absence of evidence" being mistaken for "evidence of absence," but requires careful interpretation to avoid over-interpreting weak signals.

---

## 2. Aggregate (multi-site) confidence in trend direction

### Aggregate trend direction

* The **modal direction** (most common sign) across sites defines the aggregate trend direction.

### Aggregate trend strength

* A statistic $\hat{T}$ is defined as the **expected proportion of sites whose true trends align with the aggregate direction**.
* Each site contributes probabilistically, weighted by its own $C_\tau$.

### Confidence in aggregate direction

* A posterior distribution for $T$ is constructed.
* **Aggregate confidence** ($C_T$) is the probability that $T > 0.5$, i.e., that a majority of sites truly share the aggregate direction.

---

## 3. Accounting for spatial correlation

* Environmental sites are often **spatially correlated**, reducing the effective sample size.
* The method adjusts the variance of $\hat{T}$ using **pairwise cross-correlations** between the site time series data (aggregated to common time steps).
* This correction typically **reduces overconfident aggregate conclusions**, making results more defensible.

---

## 4. Key advantages over NHST

* No null hypothesis of “zero trend”
* No arbitrary significance threshold (e.g. $\alpha = 0.05$)
* Avoids misinterpretation of non-significant results as “no change”
* Naturally supports **graded confidence statements** (e.g. likely, very likely)
* Coherent from **site to regional/national scales**

---

## 5. Limitations & Failure Modes

While this method provides a continuous measure of confidence, it relies on specific assumptions:

*   **Autocorrelation**: The standard Mann-Kendall test assumes independent observations. High serial correlation (autocorrelation) can inflate the significance ($S$ statistic) and thus the calculated confidence, leading to spurious high confidence. Pre-whitening or block bootstrapping may be needed if autocorrelation is present.
*   **Non-monotonic trends**: The test detects monotonic (consistently increasing or decreasing) trends. It may fail to detect or meaningfully characterize complex non-linear patterns (e.g., a "U" shape).
*   **Insufficient data**:
    *   **Sample Size**: As noted, $n < 10$ may invalidate the normal approximation.
    *   **Censoring**: Heavy censoring reduces the effective information content.
    *   **Site Count**: For regional aggregation, having too few sites limits the reliability of the spatial correlation adjustment.
*   **Directional Bias**: By design, the method assigns a direction to every dataset, even those that are essentially flat noise. Users must look at the *Confidence* value ($C$) alongside the direction. A direction with $C \approx 0.5$ is effectively noise.

---

## Conceptual interpretation

The Continuous Confidence Levels method reframes trend analysis as:

> **Inference about direction under uncertainty**, not hypothesis rejection.

It answers the question decision-makers actually care about:

> *How confident are we that this variable is increasing or decreasing?*

---
Fraser, C., & Whitehead, A. L. (2022). Continuous measures of confidence in direction of environmental trends at site and other spatial scales. Environmental Challenges, 9, 100601.
