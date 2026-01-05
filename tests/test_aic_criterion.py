import numpy as np
import pytest
from MannKS.segmented_trend_test import find_best_segmentation

def test_aic_criterion():
    """
    Test that AIC can be selected and verifies basic properties.
    Finding a synthetic case where BIC=0 and AIC=1 reliably with fixed seed is tricky
    due to the nature of the penalties, but we ensure:
    1. The API accepts the parameter.
    2. The returned score matches the criterion.
    3. AIC is consistently lower (or equal n) than BIC logic would imply.
    """
    np.random.seed(123)
    n = 50
    t = np.linspace(0, 50, n)

    # Very subtle break
    y = np.concatenate([np.random.normal(10, 1, 25), np.random.normal(11.5, 1, 25)])

    # 1. Run with BIC
    res_bic, _ = find_best_segmentation(y, t, max_breakpoints=1, criterion='bic', n_bootstrap=0)

    # 2. Run with AIC
    res_aic, _ = find_best_segmentation(y, t, max_breakpoints=1, criterion='aic', n_bootstrap=0)

    print(f"\nBIC Result: n={res_bic.n_breakpoints}")
    print(f"AIC Result: n={res_aic.n_breakpoints}")

    # Verify the 'score' attribute matches the requested criterion
    # If BIC selected n=0, res_bic.score should be the BIC of n=0 model.
    assert res_bic.score == res_bic.bic
    assert res_aic.score == res_aic.aic

    # Check that AIC penalty logic is working (AIC value should be < BIC value for same model complexity)
    # For the same model (e.g. n=1), AIC < BIC because 2k < ln(n)k for n=50 (ln(50)~3.9)
    # We can check the summary table for this.
    _, summary = find_best_segmentation(y, t, max_breakpoints=1, criterion='bic', n_bootstrap=0)
    row_n1 = summary[summary['n_breakpoints'] == 1].iloc[0]
    assert row_n1['aic'] < row_n1['bic']

if __name__ == "__main__":
    test_aic_criterion()
