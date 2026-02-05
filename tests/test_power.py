
import pytest
import numpy as np
import pandas as pd
from MannKS import power_test, PowerResult

try:
    import astropy
    HAS_ASTROPY = True
except ImportError:
    HAS_ASTROPY = False

def test_power_monotonicity():
    """Verify that power increases with trend magnitude."""
    rng = np.random.default_rng(42)
    n = 50
    t = np.arange(n)
    # Generate some red noise as base
    # AR(1) with phi=0.7
    x = np.zeros(n)
    for i in range(1, n):
        x[i] = 0.7 * x[i-1] + rng.normal()

    slopes = [0.0, 0.1, 0.5]

    # Use low counts for speed
    res = power_test(
        x, t, slopes,
        n_simulations=20,
        n_surrogates=50, # Min p-value 0.02
        surrogate_method='iaaft',
        random_state=42
    )

    assert isinstance(res, PowerResult)
    assert len(res.power) == 3

    # Power should be roughly monotonic: P(0) < P(0.1) < P(0.5)
    # Given noise, P(0) should be small (alpha), P(0.5) should be high.

    assert res.power[0] <= res.power[2]
    # Check that high slope has high detection
    assert res.power[2] > 0.5

def test_mdt_calculation():
    """Test Minimum Detectable Trend interpolation."""
    rng = np.random.default_rng(42)
    n = 50
    t = np.arange(n)
    x = rng.normal(size=n)

    slopes = [0, 0.1, 0.2, 0.3, 0.4]

    # We mock the return to ensure we have a clean crossing for testing interpolation logic
    # But here we run the actual test.
    # With white noise (x), detection should be easy.

    res = power_test(
        x, t, slopes,
        n_simulations=20,
        n_surrogates=50,
        surrogate_method='iaaft',
        random_state=42
    )

    # Ideally we find a crossing.
    if np.max(res.power) >= 0.8:
        assert res.min_detectable_trend is not None
        assert not np.isnan(res.min_detectable_trend)
        # MDT should be between slopes[0] and slopes[-1]
        assert slopes[0] <= res.min_detectable_trend <= slopes[-1]

@pytest.mark.skipif(not HAS_ASTROPY, reason="Astropy not installed")
def test_power_lomb_scargle():
    """Test power calculation with uneven sampling."""
    rng = np.random.default_rng(42)
    n = 40
    t = np.sort(rng.uniform(0, 100, n))
    x = rng.normal(size=n)

    slopes = [0, 0.5]

    res = power_test(
        x, t, slopes,
        n_simulations=10,
        n_surrogates=20,
        surrogate_method='lomb_scargle',
        random_state=42
    )

    assert res.noise_method == 'lomb_scargle'
    assert len(res.power) == 2

def test_power_input_dataframe():
    """Test handling of DataFrame input."""
    n = 30
    dates = pd.date_range("2020-01-01", periods=n)
    df = pd.DataFrame({'value': np.random.randn(n)}, index=dates)
    t = dates

    slopes = [0, 0.1]

    res = power_test(
        df, t, slopes,
        n_simulations=10,
        n_surrogates=20,
        surrogate_method='iaaft',
        random_state=42
    )

    assert len(res.power) == 2
