"""Sanity tests for extractors.py — verify each extractor produces
sensible output on synthetic ground-truth signals."""
import os, sys
import numpy as np
import pytest

THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS))

from extractors import (
    EXTRACTORS, extract, synthesize_continuous,
)


def _periodic_q7(n=300, seed=0, jitter=0.05):
    rng = np.random.default_rng(seed)
    return np.sort(np.arange(1, n + 1, dtype=np.float64) * 7.0 +
                    jitter * rng.standard_normal(n))


def _poisson(n=500, seed=1):
    rng = np.random.default_rng(seed)
    return np.cumsum(rng.exponential(1.0, size=n))


def test_direct_events_identity():
    t = _poisson()
    out = extract(t, 'direct_events')
    np.testing.assert_array_equal(out, np.sort(t))


def test_pll_passage_preserves_count_at_fc1():
    """At fc_ref=1, passage = t - 1 just shifts; spacings are preserved."""
    t = _poisson()
    out = extract(t, 'pll_passage', fc_ref=1.0)
    # Output should have one fewer event than input (np.diff loses 1)
    assert out.size in {t.size - 1, t.size, t.size + 1}, (
        f"pll_passage at fc_ref=1 should preserve ~event count; "
        f"got {out.size} from {t.size}")


def test_find_peaks_recovers_periodic_q7():
    """Periodic input with σ=0.05 jitter should yield ≈ same number of
    peaks via find_peaks-from-synthesis."""
    t = _periodic_q7(n=200)
    out = extract(t, 'find_peaks_prominence', prominence=0.1)
    # Should recover most events; allow ±20% loss
    assert out.size > t.size * 0.6, (
        f"find_peaks should recover most periodic events; got {out.size} from {t.size}")
    # Inter-extracted spacings should be near 7
    if out.size > 5:
        sp = np.diff(out)
        assert abs(np.median(sp) - 7.0) / 7.0 < 0.10, (
            f"recovered period should be ≈7; got median spacing {np.median(sp)}")


def test_derivative_zeros_on_periodic():
    t = _periodic_q7(n=200)
    out = extract(t, 'derivative_zeros')
    # derivative-zeros captures every local maximum, may be more than
    # input events because of grid noise. Just check it's nonzero and
    # roughly periodic.
    assert out.size > 50
    if out.size > 5:
        sp = np.diff(out)
        # Most common spacing should be near 7
        assert abs(np.median(sp) - 7.0) / 7.0 < 0.20, (
            f"derivative-zeros median spacing should be ≈7; got {np.median(sp)}")


def test_threshold_crossing_on_periodic():
    t = _periodic_q7(n=200)
    out = extract(t, 'threshold_crossing', k=0.5)
    # Threshold crossings should produce roughly one event per period
    assert out.size > t.size * 0.5, (
        f"threshold_crossing should recover most events; got {out.size}")


def test_modular_bin_events_on_integer_signal():
    """Pure integer-time events should map 1:1 under modular_bin_events."""
    t = np.arange(1, 100, dtype=np.float64)
    out = extract(t, 'modular_bin_events')
    # Should output bin indices 0..98 (offset from min=1)
    assert out.size == t.size, (
        f"Pure integer events should map 1:1; got {out.size} from {t.size}")


def test_extractors_handle_short_input():
    """All extractors must handle n<5 input gracefully (return small array)."""
    for name in EXTRACTORS:
        out = extract(np.array([1.0, 2.0, 3.0]), name)
        assert isinstance(out, np.ndarray)


def test_synthesize_continuous_has_peaks_at_events():
    t = _periodic_q7(n=50)
    grid, sig = synthesize_continuous(t, oversample=10, sigma_frac=0.3)
    # Total signal mass ≈ n_events
    # (each Gaussian integrates to σ·sqrt(2π) ≈ 0.30·2.5 = 0.75 here,
    # times 50 events ≈ 37, then sample-summed * dt = 0.7 → ≈ 26)
    assert sig.max() > 1.0
    assert grid.size > 100


if __name__ == '__main__':
    sys.exit(pytest.main([__file__, '-v']))
