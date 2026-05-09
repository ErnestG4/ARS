"""
Tests for extractor_distinctness.py — Phase 19 Tier 1 acceptance.

Verification on three synthetic pairs:

  1. **Known-equivalent pair** — `find_peaks_prominence(prom=0.30)` vs
     `find_peaks_prominence(prom=0.31)`.  Should return distinct=False
     across the standard 8-class calibrator panel.
  2. **Known-distinct pair** — `direct_events` vs `find_peaks_prominence`.
     Should return distinct=True with disagreeing_class='poisson' (per
     the §7.ter.19 / Phase 16 Tier 1 finding that find_peaks induces TR
     on Poisson input while direct_events correctly reads BL).
  3. **Borderline pair** — `threshold_crossing(k=1.0)` vs
     `threshold_crossing(k=2.0)`.  May or may not be distinct; the test
     records the verdict (this is the "informative either way" cell of
     the spec).
"""
import os, sys
import numpy as np
import pytest

THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS))

from extractors import EXTRACTORS
from extractor_distinctness import (
    distinct_pair, STANDARD_CALIBRATORS, extractor_for_events,
)


# Reduced-cost verification: 3 seeds (smaller than the operational 5),
# at_n_min=2 disagreeing seeds for the threshold (3 of 3 → "robust"; 2 of 3
# → present but borderline).  Operational distinctness in run scripts uses
# 5 seeds with seed_threshold=4 (≈ α=0.05).
TEST_N_SEEDS = 3


def test_known_equivalent_pair_returns_False():
    """find_peaks_prominence at prom=0.30 vs prom=0.31 should not produce
    a robust per-q disagreement on any calibrator class."""
    a = extractor_for_events('find_peaks_prominence', prominence=0.30)
    b = extractor_for_events('find_peaks_prominence', prominence=0.31)
    res = distinct_pair(a, b, n_seeds=TEST_N_SEEDS, seed_threshold=3)
    assert res['distinct'] is False, (
        f"Equivalent pair flagged distinct: disagreeing_class="
        f"{res['disagreeing_class']}, max_disagree_seeds="
        f"{res['max_disagreement_seeds']}")


def test_known_distinct_pair_returns_True():
    """direct_events vs find_peaks_prominence should be distinct via the
    Poisson disagreement: find_peaks induces a non-BL classification on
    Poisson input where direct_events reads it as BL.  The spec
    explicitly identifies this as the canonical disagreeing class."""
    a = extractor_for_events('direct_events')
    b = extractor_for_events('find_peaks_prominence')
    res = distinct_pair(a, b, n_seeds=TEST_N_SEEDS, seed_threshold=3)
    assert res['distinct'] is True, (
        f"Known-distinct pair flagged equivalent.  per_class results: "
        f"{res['per_class']}")
    # The disagreement should be present on most calibrator classes
    # (these two extractors disagree broadly), and at least on poisson.
    poisson_row = next((r for r in res['per_class']
                        if r['calibrator'] == 'poisson'), None)
    assert poisson_row is not None
    assert poisson_row['n_disagree_seeds'] >= 2, (
        f"Poisson disagreement seeds: {poisson_row}")


def test_borderline_pair_records_verdict():
    """threshold_crossing(k=1.0) vs threshold_crossing(k=2.0): the spec
    treats this as borderline and "informative either way."  We just
    require the test runs to completion and produces a structured result.
    The verdict is recorded for documentation (printed to stdout)."""
    a = extractor_for_events('threshold_crossing', k=1.0)
    b = extractor_for_events('threshold_crossing', k=2.0)
    res = distinct_pair(a, b, n_seeds=TEST_N_SEEDS, seed_threshold=3)
    assert isinstance(res['distinct'], bool)
    assert isinstance(res['per_class'], list)
    assert len(res['per_class']) == len(STANDARD_CALIBRATORS)
    print(f"\nborderline (threshold k=1 vs k=2): distinct={res['distinct']}, "
          f"max_disagree_seeds={res['max_disagreement_seeds']}, "
          f"disagreeing_class={res['disagreeing_class']}")


if __name__ == '__main__':
    sys.exit(pytest.main([__file__, '-v', '-s']))
