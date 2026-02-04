
### Update on LS Spectral Whitening

**User Question:** "Is the LS spectral whitening solveable?"

**Findings:**
Yes, the spectral whitening observed in the non-iterative Lomb-Scargle surrogate method is solvable using an iterative amplitude correction loop (similar to the Schreiber & Schmitz IAAFT algorithm, but adapted for spectral synthesis).

**Proposed Solution:**
An iterative approach can be implemented as follows:
1.  **Initialize:** Compute target Periodogram ($P_{target}$) from original data.
2.  **Iterate:**
    *   Synthesize surrogate using current input amplitudes ($A_{in}$) and random phases.
    *   Rank-adjust the surrogate to match the original value distribution.
    *   Compute the Periodogram of the rank-adjusted surrogate ($P_{out}$).
    *   **Correct Input:** Update input amplitudes: $A_{in}^{new} = A_{in}^{old} \times \sqrt{P_{target} / P_{out}}$.
    *   Repeat until $P_{out}$ matches $P_{target}$ within tolerance.

**Verification:**
A prototype implementation (`tests/prototype_iterative_ls.py`) confirms that this method restores the correct dominant frequency for a pure sine wave (which was previously distorted/whitened).
*   **Target Frequency:** 0.1 Hz
*   **Non-Iterative Result:** Peak ~0.19 Hz (Distorted)
*   **Iterative Result (100 iters):** Peak ~0.102 Hz (Restored)

**Trade-offs:**
*   **Performance:** The iterative method is significantly slower. Generating 1 surrogate (N=100) with 100 iterations took ~1.8 seconds. Generating 1,000 surrogates would take ~30 minutes, compared to <1 second for the non-iterative method.
*   **Recommendation:** For standard Red Noise testing (Gaussian-like), the non-iterative method is sufficient and much faster. The iterative method should be considered an optional "high-fidelity" mode for users dealing with highly non-Gaussian periodic signals.
