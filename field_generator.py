"""
field_generator.py — synthetic point-process generator with known
universality-class structure for Phase 17 (boundary-recovers-bulk
inverse-problem characterization).

For each class, `generate(class_name, params, n_events, seed)` returns
a sorted np.float64 t_k array of size ≈ n_events with the underlying
structure parameterised by `params`.  Ground truth is by construction
— the recovery routines in `bulk_recovery.py` then attempt to recover
`params` from `joint_q_profile(t_k)`.

Tier 1 supports six classes; Tier 2 (mixed-class) extends via
`generate_mixed`.

Reference: Tier 1 boundary-extraction operates on t_k directly via the
canonical `pll_passage` and `direct_events` extractors (8/8 reliable
in Phase 16 Tier 1).  Continuous-signal synthesis is exercised in
Tier 3 alongside threshold-style extractors.
"""
from __future__ import annotations
import numpy as np
from typing import Optional


# ─── Pure-class generators ──────────────────────────────────────────────────

def _gen_poisson(rate: float, n_events: int, seed: int) -> np.ndarray:
    """Inhomogeneous-Poisson at constant rate λ; emit n_events arrivals."""
    rng = np.random.default_rng(seed)
    intervals = rng.exponential(1.0 / max(rate, 1e-9), size=n_events)
    return np.cumsum(intervals)


def _gen_wigner_beta(beta: float, n_events: int, seed: int) -> np.ndarray:
    """Hermite β-ensemble eigenvalues, semicircle-unfolded to unit-mean spacing."""
    from signal_gen import make_beta_ensemble_eigenvalues
    return make_beta_ensemble_eigenvalues(n_events, beta=beta, seed=seed)


def _gen_periodic(q: int, jitter: float, n_events: int, seed: int) -> np.ndarray:
    """Events at integer multiples of q (the period) with Gaussian jitter.

    Resulting t_k = q · k + jitter · q · N(0, 1), k = 1..n_events.
    Indicator-mode RF on integer time bins peaks at coefficient q
    because c_q(qk) = φ(q) (the maximal Ramanujan-sum value), giving
    |a_q| dominance.  Recovery reads q via argmax of |a_q| spectrum at q ≥ 2.
    """
    rng = np.random.default_rng(seed)
    base = np.arange(1, n_events + 1, dtype=np.float64) * q
    return np.sort(base + jitter * q * rng.standard_normal(n_events))


def _gen_uniform_jitter(jitter: float, n_events: int, seed: int) -> np.ndarray:
    """Uniform-spacing process with Gaussian jitter (the BR_artifact regime).

    t_n = n + jitter · N(0, 1) ; resolves collisions for large jitter.
    """
    from signal_gen import make_uniform_jitter
    return make_uniform_jitter(n_events, jitter, seed=seed)


# ─── Public dispatch ─────────────────────────────────────────────────────────

CLASSES = ('poisson', 'wigner_gue', 'wigner_goe', 'wigner_gse',
           'periodic', 'uniform_jitter')


def generate(class_name: str, params: dict, n_events: int = 2000,
             seed: int = 0) -> np.ndarray:
    """Dispatch to the named class with its parameters.

    Class signatures:
        poisson:        params = {'rate': λ}
        wigner_gue:     params = {} (β=2 fixed)
        wigner_goe:     params = {} (β=1 fixed)
        wigner_gse:     params = {} (β=4 fixed)
        periodic:       params = {'q': int, 'jitter': float}
        uniform_jitter: params = {'sigma': float}
    """
    if class_name == 'poisson':
        return _gen_poisson(params.get('rate', 1.0), n_events, seed)
    if class_name == 'wigner_gue':
        return _gen_wigner_beta(2.0, n_events, seed)
    if class_name == 'wigner_goe':
        return _gen_wigner_beta(1.0, n_events, seed)
    if class_name == 'wigner_gse':
        return _gen_wigner_beta(4.0, n_events, seed)
    if class_name == 'periodic':
        return _gen_periodic(int(params['q']), float(params.get('jitter', 0.05)),
                              n_events, seed)
    if class_name == 'uniform_jitter':
        return _gen_uniform_jitter(float(params.get('sigma', 0.10)),
                                    n_events, seed)
    raise ValueError(f"unknown class: {class_name!r}; valid: {CLASSES}")


def generate_mixed(component_specs: list[dict], n_events: int = 2000,
                    seed: int = 0,
                    target_span: float = None) -> np.ndarray:
    """Generate a mixed-class field by superposing component point processes.

    `component_specs`: list of {'class': str, 'params': dict, 'weight': float}.
    Total events ≈ n_events; per-component count ∝ weight.

    Each component is generated on its natural time scale, then *all
    components* are rescaled together to share a common time span.
    The natural time-scale relationships (e.g., a periodic-q=7 component
    keeping its event-at-multiples-of-7 structure) are preserved relative
    to one another.  Final t_k is sorted but **not** unit-mean-normalised,
    so component-internal periodicities remain visible to RF on the
    integer-bin indicator.
    """
    rng = np.random.default_rng(seed)
    streams = []
    weights = np.array([c.get('weight', 1.0) for c in component_specs])
    weights = weights / weights.sum()
    for i, c in enumerate(component_specs):
        n_c = int(round(n_events * weights[i]))
        if n_c < 5: continue
        sub = generate(c['class'], c.get('params', {}),
                        n_events=n_c, seed=seed + 1000 * (i + 1))
        streams.append(sub)
    if not streams:
        return np.zeros(0)
    # Find the longest natural time span across components and rescale
    # each stream to that span (preserves relative time scales after
    # placing all components on a common axis [0, span]).
    if target_span is None:
        target_span = max(float(s[-1] - s[0]) for s in streams if s.size > 1)
    rescaled = []
    for s in streams:
        if s.size < 2: continue
        natural_span = float(s[-1] - s[0])
        if natural_span > 0:
            # Map to [0, target_span] preserving internal structure
            rescaled.append((s - s[0]) * (target_span / natural_span))
        else:
            rescaled.append(s)
    pooled = np.sort(np.concatenate(rescaled))
    return np.maximum.accumulate(pooled + 1e-9 * np.arange(pooled.size))


__all__ = ['generate', 'generate_mixed', 'CLASSES']
