
import pytest
import numpy as np
from MannKS._surrogate import _iaaft_surrogates, _lomb_scargle_surrogates, HAS_ASTROPY

def test_iaaft_amplitude_conservation():
    """IAAFT surrogates must have exactly the same amplitude distribution as the original."""
    rng = np.random.default_rng(42)
    x = rng.normal(size=100)

    surrogates = _iaaft_surrogates(x, n_surrogates=5, random_state=42)

    sorted_x = np.sort(x)
    for s in surrogates:
        sorted_s = np.sort(s)
        np.testing.assert_allclose(sorted_s, sorted_x, err_msg="IAAFT surrogate amplitude distribution mismatch")

@pytest.mark.skipif(not HAS_ASTROPY, reason="Astropy not installed")
def test_lomb_scargle_amplitude_conservation():
    """Lomb-Scargle surrogates (with rank adjustment) must preserve amplitude distribution."""
    rng = np.random.default_rng(42)
    t = np.sort(rng.uniform(0, 100, 50))
    x = np.sin(t) + rng.normal(scale=0.1, size=50)

    surrogates = _lomb_scargle_surrogates(x, t, n_surrogates=5, random_state=42)

    sorted_x = np.sort(x)
    for s in surrogates:
        sorted_s = np.sort(s)
        # Note: Lomb-Scargle implementation does a final rank adjustment, so it should be exact.
        np.testing.assert_allclose(sorted_s, sorted_x, err_msg="Lomb-Scargle surrogate amplitude distribution mismatch")

def test_iaaft_spectrum_conservation():
    """IAAFT surrogates should preserve the power spectrum (autocorrelation)."""
    # Create a strong periodic signal
    t = np.linspace(0, 100, 200)
    x = np.sin(2 * np.pi * t / 20) # Period 20

    surrogates = _iaaft_surrogates(x, n_surrogates=10, random_state=42)

    # Check that surrogates have a peak at the same frequency
    freqs = np.fft.rfftfreq(len(x), d=t[1]-t[0])

    orig_fft = np.abs(np.fft.rfft(x))
    orig_peak_idx = np.argmax(orig_fft[1:]) + 1 # Skip DC

    for s in surrogates:
        surr_fft = np.abs(np.fft.rfft(s))
        surr_peak_idx = np.argmax(surr_fft[1:]) + 1
        assert surr_peak_idx == orig_peak_idx, "IAAFT surrogate lost dominant frequency"
