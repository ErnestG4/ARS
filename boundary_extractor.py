"""
boundary_extractor.py — standardized field-to-events pipeline for Phase 17.

Wraps the existing extractors.{pll_passage,direct_events} as the canonical
boundary-extraction layer for the inverse-problem characterization.  These
are the two extractors that scored 8/8 on Phase 16 Tier 1 invariance —
they preserve class on every signal where ground truth is known.

Tier 1 / 2 / 4 use these.  Tier 3 (recovery limits) extends to the full
extractor panel from `extractors.py` to characterize how recovery
degrades under less-reliable extractors.
"""
from __future__ import annotations
import numpy as np

from extractors import (
    extract_direct_events, extract_pll_passage,
    extract as _extract_any,
)


CANONICAL = ('direct_events', 'pll_passage')


def extract(t_k: np.ndarray, method: str = 'pll_passage', **kwargs) -> np.ndarray:
    """Apply the named extractor.  For Tier 1/2/4 use 'direct_events' or
    'pll_passage'; for Tier 3 the full `extractors.EXTRACTORS` registry
    is available."""
    return _extract_any(t_k, method, **kwargs)


__all__ = ['extract', 'CANONICAL']
