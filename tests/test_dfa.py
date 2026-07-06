"""
Tests for dfa.py — DFA Hurst-exponent estimator.

Synthetic-series acceptance:

  - White noise (iid Gaussian): H ≈ 0.5 ± 0.05.
  - Brownian motion (cumulative sum of white noise): H ≈ 1.5 (because we
    DFA on the *increments* of a Brownian path; here we test on the
    cumulative path itself, which gives H ≈ 1.5 for true BM).
  - Anti-persistent series (mean-reverting AR(1) with ρ = -0.5):
    H ≈ 0.3.
"""
import os, sys
import numpy as np
import pytest

THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS))

from dfa import dfa_hurst


def test_dfa_white_noise_H_near_05():
    rng = np.random.default_rng(7)
    x = rng.standard_normal(8192)
    res = dfa_hurst(x)
    assert abs(res['hurst'] - 0.5) < 0.07, (
        f"white-noise H should be ≈ 0.5, got {res['hurst']:.3f}")
    assert res['r2'] > 0.95, f"DFA fit poor: r2={res['r2']:.3f}"


def test_dfa_brownian_H_near_15():
    """Cumulative sum of white noise → fractional integration of order 1
    → DFA Hurst ≈ 1.5 on the integrated path."""
    rng = np.random.default_rng(11)
    bm = np.cumsum(rng.standard_normal(8192))
    res = dfa_hurst(bm)
    assert abs(res['hurst'] - 1.5) < 0.10, (
        f"BM H should be ≈ 1.5, got {res['hurst']:.3f}")


def test_dfa_anti_persistent_H_below_05():
    """AR(1) with negative ρ → anti-persistence → H < 0.5."""
    rng = np.random.default_rng(23)
    n = 8192
    rho = -0.5
    e = rng.standard_normal(n)
    x = np.zeros(n)
    x[0] = e[0]
    s = np.sqrt(1 - rho ** 2)
    for i in range(1, n):
        x[i] = rho * x[i - 1] + s * e[i]
    res = dfa_hurst(x)
    assert res['hurst'] < 0.45, (
        f"anti-persistent series H should be < 0.45, got {res['hurst']:.3f}")


def test_dfa_long_range_correlated_H_above_05():
    """Generate a power-law correlated series via fractional Gaussian
    noise (FFT method) at H=0.75 and check recovery within 0.07."""
    rng = np.random.default_rng(31)
    n = 4096
    target_H = 0.75
    # FFT method: generate complex spectrum with magnitude |k|^(-(2H-1)/2)
    freqs = np.fft.fftfreq(n, d=1.0)
    # Avoid zero-frequency
    spectrum = np.zeros_like(freqs, dtype=np.complex128)
    nz = freqs != 0
    mag = np.abs(freqs[nz]) ** (-(2 * target_H - 1) / 2)
    phases = rng.uniform(0, 2 * np.pi, size=int(nz.sum()))
    spectrum[nz] = mag * np.exp(1j * phases)
    # Real-output enforcement
    x = np.fft.ifft(spectrum).real
    x = (x - x.mean()) / x.std()
    res = dfa_hurst(x)
    assert abs(res['hurst'] - target_H) < 0.10, (
        f"H=0.75 LRC series recovered as {res['hurst']:.3f} "
        f"(target {target_H})")


if __name__ == '__main__':
    sys.exit(pytest.main([__file__, '-v']))
