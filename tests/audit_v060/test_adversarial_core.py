
import pytest
import numpy as np
import pandas as pd
import warnings
from MannKS._surrogate import _lomb_scargle_surrogates, surrogate_test
from MannKS.power import power_test

class TestAdversarialCore:
    """
    Adversarial tests for core v0.6.0 features (Surrogates, Power).
    Designed to break the system with edge cases.
    """

    def test_lomb_scargle_constant_data(self):
        """
        Test that Lomb-Scargle handles constant data (variance=0) gracefully.
        Expected: Returns constant surrogates (or near-constant).
        Crash Check: Division by zero in normalization.
        """
        n = 100
        x = np.ones(n) * 42.0
        t = np.arange(n)

        # Should not raise error
        surrogates = _lomb_scargle_surrogates(x, t, n_surrogates=5, fit_mean=True)

        # Verify surrogates are also constant 42
        assert surrogates.shape == (5, n)
        assert np.allclose(surrogates, 42.0), "Surrogates of constant data should be constant"

    def test_lomb_scargle_massive_offset(self):
        """
        Test spectral synthesis with massive time offsets (e.g., current Unix timestamp).
        Expected: No precision loss in phase (should behave like t=0..N).
        """
        n = 50
        # Year 2026 timestamps ~ 1.77e9
        t_base = np.linspace(0, 100, n)
        t_huge = t_base + 1.77e9

        # Sine wave signal
        x = np.sin(2 * np.pi * t_base / 20.0)

        # Generate surrogates for both
        rng1 = np.random.default_rng(42)
        surr_base = _lomb_scargle_surrogates(x, t_base, n_surrogates=1, random_state=42)

        rng2 = np.random.default_rng(42)
        surr_huge = _lomb_scargle_surrogates(x, t_huge, n_surrogates=1, random_state=42)

        # The internal logic should subtract min(t), so these should be identical
        # (Assuming the implementation does `t - min(t)` before trig operations)
        assert np.allclose(surr_base, surr_huge), "Time shift invariance failed for large offsets"

    def test_power_detrend_perfect_linear(self):
        """
        Test that detrend=True effectively removes a perfect linear trend
        before generating surrogates.
        """
        n = 50
        t = np.arange(n).astype(float)
        slope = 2.0
        x = slope * t  # Perfect trend

        res = power_test(
            x, t,
            slopes=[slope],
            n_simulations=10,
            n_surrogates=50,
            detrend=True,
            surrogate_method='lomb_scargle' # Force LS to test complex path
        )

        # With perfect trend injection on 0 noise, detection should be 100%
        assert res.power[0] == 1.0

    def test_power_invalid_slope_scaling(self):
        """
        Test that invalid slope_scaling raises a clear ValueError.
        """
        x = np.arange(10)
        t = np.arange(10)
        with pytest.raises(ValueError, match="Invalid time unit"):
            power_test(x, t, slopes=[0.1], slope_scaling='invalid_unit')

    def test_power_dataframe_missing_columns(self):
        """
        Test DataFrame input without 'value' column.
        """
        # 2 columns, neither is 'value' -> ambiguous, should fail
        df = pd.DataFrame({'wrong': np.arange(10), 'also_wrong': np.arange(10)})
        t = np.arange(10)
        with pytest.raises(ValueError, match="Input DataFrame `x` must be 1-dimensional"):
            power_test(df, t, slopes=[0.1])

    def test_iaaft_uneven_warning(self):
        """
        Test that IAAFT warns on uneven data if method='iaaft' is forced.
        """
        t = np.array([0, 1, 3, 4]) # Gap
        x = np.random.randn(4)

        with pytest.warns(UserWarning, match="unevenly spaced"):
            surrogate_test(x, t, method='iaaft', n_surrogates=10)
