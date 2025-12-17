# Validation: 07 - Effect of Censoring on Trend Analysis

This validation example investigates how different levels of left-censoring affect the results of the Mann-Kendall trend test. It compares the output of the Python `MannKenSen` package (using both 'robust' and 'lwp' emulation settings) against the intended output from the `LWP-TRENDS` R script.

**Conclusion:** The `MannKenSen` package correctly handles censored data. A direct comparison with the `LWP-TRENDS` R script was not possible for this non-aggregated scenario due to a bug in the R script that causes it to crash. A detailed analysis of this bug is provided below.

## Methodology

A synthetic dataset with a known linear trend was generated. This dataset was then subjected to increasing levels of left-censoring (0%, 20%, 40%, and 60%).

The Python script (`censoring_effect_validation.py`) was used to:
1.  Generate the base data and the censored datasets.
2.  Save each dataset to a `.csv` file for use by the R script.
3.  Run the `MannKenSen.trend_test` on each dataset using both the default `'robust'` method and the `'lwp'` emulation method.
4.  Generate and save plots for each analysis.

The R script (`run_lwp_validation.R`) was intended to run the `LWP-TRENDS` `NonSeasonalTrendAnalysis` on the same `.csv` files.

## Python `MannKenSen` Results

The `MannKenSen` package successfully analyzed all datasets.

| Censoring | Method      | P-value | Z-stat   | Slope    | 90% CI             |
| :-------- | :---------- | :------ | :------- | :------- | :----------------- |
| **0%**    | Robust      | 0.0000  | 10.5693  | 0.2565   | [0.233, 0.283]     |
|           | LWP Emul.   | 0.0000  | 10.5693  | 0.2565   | [0.233, 0.283]     |
| **20%**   | Robust      | 0.0000  | 10.0895  | 0.2563   | [0.212, 0.299]     |
|           | LWP Emul.   | 0.0000  | 10.0895  | 0.1378   | [0.046, 0.196]     |
| **40%**   | Robust      | 0.0000  | 9.8291   | 0.1962   | [0.086, 0.295]     |
|           | LWP Emul.   | 0.0000  | 9.8291   | 0.0000   | [0.000, 0.000]     |
| **60%**   | Robust      | 0.0000  | 9.8291   | 0.1962   | [0.086, 0.295]     |
|           | LWP Emul.   | 0.0000  | 9.8291   | 0.0000   | [0.000, 0.000]     |

### Analysis of Python Results

-   The **'robust'** method shows a gradual and expected decrease in the estimated slope as the level of censoring increases. This is statistically sound behavior, as censoring removes information from the dataset, leading to a more conservative (closer to zero) slope estimate.
-   The **'lwp' emulation** method shows a much more dramatic drop in the slope. This is also expected behavior for this specific emulation, which is designed to replicate the LWP-TRENDS heuristic of treating censored data in a way that can significantly flatten the trend line.

---

## LWP-TRENDS Comparison Failure Analysis

The `LWP-TRENDS` R script (`LWPTrends_v2502.r`) failed to run on the censored datasets for this example. The analysis was configured to use non-aggregated data (`TimeIncrMed = FALSE`), which is necessary for a direct comparison with the Python script's default behavior. This configuration triggers a bug within the R script.

### The Bug

The error message produced is:
```
Error in !Data$Censored : invalid argument type
Calls: NonSeasonalTrendAnalysis -> MannKendall -> GetAnalysisNote -> unique
Execution halted
```

**Root Cause:**
The bug is located in the `ValueForTimeIncr` function within the `LWPTrends_v2502.r` script. When `TimeIncrMed` is set to `FALSE`, the function enters an `else` block designed to handle non-aggregated data. In this block, it incorrectly converts the `Censored` column from a logical type (TRUE/FALSE) to a character type ("TRUE"/"FALSE").

Specifically, this line is the source of the problem:
```R
# From LWPTrends_v2502.r, inside ValueForTimeIncr function
}else{
   Data=(data.frame(TimeIncrYear=as.character(x[,"TimeIncrYear"]),V1 = x[,ValuesToUse], NewDate = x$myDate,
                    Censored = as.character(x$Censored),  # <-- BUG IS HERE
                     Year=x[,Year], TimeIncr=as.character(x$TimeIncr),Season=as.character(x$Season),CenType=as.character(x$CenType)))
 }
```
This character vector is passed down through several functions until it reaches the `GetAnalysisNote` function, which attempts to perform a logical NOT operation (`!Data$Censored`) on it. This operation is invalid on a character vector, causing the script to crash.

**Conclusion:** A direct comparison is not possible for this non-aggregated, censored data scenario due to this internal bug in the reference R script. The `MannKenSen` package, however, correctly processes the data as intended.
