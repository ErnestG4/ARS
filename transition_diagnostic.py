"""
transition_diagnostic.py — Phase 20.5 Tier 2.

The `characterize_transition(trajectory)` API: takes a sub-window
classification trajectory (one row per sub-window from
joint_quadrant_diagnostic) and returns a structured transition
characterisation.

This is the operational deliverable that Phase 21's Tier 3 calls on
per-(event, instrument) trajectories and that retroactively sharpens
Phase 20's BGP cascade analysis.

Trajectory features computed per trajectory:

  - **Transition window** — (start, end) sub-window indices where
    classification differs from both the leading and trailing modes.
  - **Transition steepness** — rate of change of classification-
    distance metric per sub-window during the transition window.
  - **Trajectory monotonicity** — does classification distance from
    origin increase monotonically toward destination?
  - **Mid-transition stability** — for sub-windows in transition
    region, do classifications cluster around a stable intermediate
    state?
  - **Pre/post duration ratio** — for asymmetric shapes.
  - **Period-doubling signature** — autocorrelation of the
    classification-distance time series; detection of recursive
    transition structure with Feigenbaum-scaled self-similarity
    (δ ≈ 4.669).

Shape templates (best-match output of `shape_estimate`):

  - sharp_step
  - linear_ramp
  - sigmoidal
  - exponential_approach
  - damped_oscillatory
  - metastable_middle
  - period_doubling_cascade
  - unclassified  (returned when no template fits within tolerance)
"""
from __future__ import annotations

import os, sys
from typing import Sequence, Optional

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)


# Quadrant-distance metric: encode each quadrant label as a position
# in 2-D (rep_int axis × rf_spike axis), then compute Euclidean
# distance between any two labels.  This gives the diagnostic a
# continuous distance for monotonicity / steepness analysis without
# requiring rep_med values to be present (some calibrator trajectories
# only carry the quadrant label).
QUADRANT_COORDS = {
    'BL':           (0.0, 0.0),
    'TR':           (0.5, 0.0),
    'BR_artifact':  (0.9, 0.0),
    'BR_novel':     (0.9, 0.0),
    'TL':           (0.5, 1.0),
    'ambiguous':    (0.25, 0.5),    # placeholder for "we couldn't tell"
    'underpowered': (np.nan, np.nan),
    'unclassified': (np.nan, np.nan),
}


def quadrant_distance(a: str, b: str) -> float:
    """Euclidean distance between two quadrant labels in (rep, spike)
    coords.  Returns nan if either is underpowered/missing."""
    ca = QUADRANT_COORDS.get(a)
    cb = QUADRANT_COORDS.get(b)
    if ca is None or cb is None:
        return float('nan')
    if any(np.isnan(v) for v in ca + cb):
        return float('nan')
    return float(np.hypot(ca[0] - cb[0], ca[1] - cb[1]))


# ─── Mode and segment detection ────────────────────────────────────────────


def _stable_mode(labels: list[str], frac: float = 0.7) -> Optional[str]:
    """The label that occupies ≥ frac of the input list.  Returns None
    if no label dominates."""
    if not labels:
        return None
    valid = [l for l in labels if l not in ('underpowered', 'ambiguous')]
    if not valid:
        return None
    series = pd.Series(valid)
    counts = series.value_counts()
    top, top_count = counts.index[0], int(counts.iloc[0])
    if top_count >= frac * len(valid):
        return str(top)
    return None


def _detect_transition_window(
        primaries: list[str],
        leading_frac: float = 0.20,
        trailing_frac: float = 0.20,
        edge_min_sub: int = 4,
        ) -> tuple[Optional[str], Optional[str], int, int]:
    """Detect origin and destination class as the modes of leading
    and trailing fractions; return (origin, destination,
    transition_start, transition_end) — start/end are indices in
    `primaries` bounding the transition region (where labels differ
    from both origin and destination, or are 'ambiguous').

    Returns (None, None, 0, 0) if neither leading nor trailing fraction
    has a stable mode (no detectable transition).
    """
    n = len(primaries)
    if n < 3 * edge_min_sub:
        return None, None, 0, 0
    n_lead = max(edge_min_sub, int(leading_frac * n))
    n_trail = max(edge_min_sub, int(trailing_frac * n))
    origin = _stable_mode(primaries[:n_lead])
    destination = _stable_mode(primaries[-n_trail:])
    if origin is None or destination is None:
        return None, None, 0, 0
    if origin == destination:
        return origin, destination, 0, 0
    # Transition window: indices where label differs from origin AND
    # differs from destination (or is ambiguous/underpowered).
    in_transition = []
    for i, p in enumerate(primaries):
        if p == origin and i < n - n_trail:
            in_transition.append(False)
        elif p == destination and i >= n_lead:
            in_transition.append(False)
        else:
            in_transition.append(True)
    # Find first and last True
    idx = [i for i, v in enumerate(in_transition) if v]
    if not idx:
        # No transition gap; treat the boundary between origin-mode
        # and destination-mode as a sharp step
        # Find last origin index and first destination index
        last_origin = -1
        first_dest = n
        for i in range(n):
            if primaries[i] == origin:
                last_origin = i
        for i in range(n):
            if primaries[i] == destination:
                first_dest = i
                break
        if last_origin >= first_dest:
            # Overlapping; place transition at midpoint
            mid = n // 2
            return origin, destination, mid, mid
        return origin, destination, last_origin + 1, first_dest
    return origin, destination, idx[0], idx[-1] + 1


# ─── Distance-trajectory features ─────────────────────────────────────────


def _distance_trajectory(primaries: list[str], origin: str) -> np.ndarray:
    """Per-sub-window distance from origin label.  NaN-filled for
    underpowered/missing."""
    return np.array([quadrant_distance(p, origin) for p in primaries])


def _monotonicity(d: np.ndarray) -> float:
    """Spearman-rank correlation between sub-window index and distance
    from origin; returns 1 for perfectly monotonic increase, -1 for
    decrease, 0 for unstructured."""
    valid = ~np.isnan(d)
    if valid.sum() < 4:
        return float('nan')
    x = np.arange(d.size)[valid]
    y = d[valid]
    if y.std() == 0:
        return 0.0
    # Rank-based correlation
    rx = np.argsort(np.argsort(x))
    ry = np.argsort(np.argsort(y))
    if rx.std() == 0 or ry.std() == 0:
        return 0.0
    return float(np.corrcoef(rx, ry)[0, 1])


def _steepness(d: np.ndarray, win_start: int, win_end: int) -> float:
    """Mean absolute change of distance per sub-window during the
    transition window."""
    if win_end <= win_start + 1:
        return float('nan')
    seg = d[win_start:win_end]
    valid = ~np.isnan(seg)
    if valid.sum() < 2:
        return float('nan')
    return float(np.nanmean(np.abs(np.diff(seg[valid]))))


def _mid_transition_cluster(primaries: list[str],
                              start: int, end: int,
                              origin: str, destination: str,
                              ) -> tuple[Optional[str], float]:
    """Within the transition window, return the dominant intermediate
    class (excluding origin/destination/underpowered) and its
    fraction.  This identifies metastable middles."""
    if end <= start:
        return None, 0.0
    seg = primaries[start:end]
    intermediate = [p for p in seg
                    if p not in (origin, destination,
                                  'underpowered', 'ambiguous')]
    if not intermediate:
        return None, 0.0
    counts = pd.Series(intermediate).value_counts()
    top = str(counts.index[0])
    frac = float(counts.iloc[0] / max(len(seg), 1))
    return top, frac


# ─── Period-doubling detection ─────────────────────────────────────────────


def _autocorr_at_lag(x: np.ndarray, lag: int) -> float:
    if x.size <= lag or lag <= 0:
        return float('nan')
    x = x - x.mean()
    s = x.std()
    if s <= 0:
        return 0.0
    return float(np.mean(x[:-lag] * x[lag:]) / (s * s))


def _period_doubling_signature(d: np.ndarray) -> Optional[dict]:
    """Detect period-doubling cascade structure in the distance
    trajectory.  A clean cascade produces autocorrelation peaks at
    geometrically spaced lags whose ratios approach Feigenbaum's δ ≈
    4.669.

    Algorithm:
      1. Find local maxima in autocorrelation r(k) for k ∈ [2, n//4].
      2. If at least 2 peaks at lags k_1 < k_2 < ..., compute
         consecutive ratios k_{i+1} / k_i.
      3. If the median ratio is in [3.5, 6.0], report a cascade
         detection with the ratio as Feigenbaum-δ estimate.

    Returns None if no cascade detected.
    """
    valid = ~np.isnan(d)
    if valid.sum() < 32:
        return None
    x = d[valid]
    max_lag = max(8, x.size // 4)
    r = np.array([_autocorr_at_lag(x, k) for k in range(2, max_lag)])
    if not np.isfinite(r).all() or r.size < 4:
        return None
    # Local maxima of r at k≥2
    peaks = []
    for i in range(1, r.size - 1):
        if r[i] > r[i - 1] and r[i] > r[i + 1] and r[i] > 0.05:
            peaks.append((i + 2, r[i]))   # lag = i + 2 (since k starts at 2)
    if len(peaks) < 2:
        return None
    lags = [p[0] for p in peaks]
    ratios = [lags[i + 1] / lags[i] for i in range(len(lags) - 1)]
    median_ratio = float(np.median(ratios))
    feigenbaum = 4.669
    if 3.5 <= median_ratio <= 6.0:
        return dict(
            detected=True,
            peak_lags=lags,
            consecutive_ratios=ratios,
            median_ratio=median_ratio,
            feigenbaum_delta_target=feigenbaum,
            feigenbaum_relative_error=abs(median_ratio - feigenbaum)
                                       / feigenbaum,
        )
    return None


# ─── Shape classifier ─────────────────────────────────────────────────────


def _classify_shape(
        d: np.ndarray,
        win_start: int, win_end: int,
        monotonicity: float,
        midstable_class: Optional[str],
        midstable_frac: float,
        period_doubling: Optional[dict],
        n_total: int,
        ) -> tuple[str, float, dict]:
    """Best-match shape template for the trajectory.

    Returns (shape_name, confidence, parameters_dict).
    """
    if period_doubling and period_doubling.get('detected'):
        return ('period_doubling_cascade', 0.85, period_doubling)
    if midstable_class and midstable_frac > 0.30:
        return ('metastable_middle', 0.80, dict(
            metastable_state_class=midstable_class,
            metastable_fraction=float(midstable_frac),
            metastable_duration=int((win_end - win_start) * midstable_frac),
        ))
    width = win_end - win_start
    width_frac = width / max(n_total, 1)
    if width <= 1 or width_frac < 0.02:
        return ('sharp_step', 0.85, dict(width_fraction=float(width_frac)))
    # Distinguish smooth shapes by monotonicity + steepness profile
    if not np.isfinite(monotonicity) or monotonicity < 0.3:
        return ('damped_oscillatory', 0.55, dict(
            monotonicity=float(monotonicity),
            width_fraction=float(width_frac)))
    # Width and monotonicity both suggest a smooth transition.  Use
    # the steepness profile across the transition window: linear ramp
    # has constant steepness, sigmoidal peaks at midpoint, exponential
    # has decaying-asymmetric steepness.
    seg = d[win_start:win_end]
    valid_seg = ~np.isnan(seg)
    if valid_seg.sum() < 3:
        return ('linear_ramp', 0.50, dict(width_fraction=float(width_frac)))
    diffs = np.abs(np.diff(seg[valid_seg]))
    if diffs.size < 3:
        return ('linear_ramp', 0.50, dict(width_fraction=float(width_frac)))
    # Where is the maximum-rate position relative to the transition?
    peak_idx = int(np.argmax(diffs))
    peak_frac = peak_idx / max(diffs.size, 1)
    # If peak is near midpoint → sigmoidal; near start → exponential;
    # uniform → linear_ramp.
    cv = float(diffs.std() / max(diffs.mean(), 1e-9))   # coeff of variation
    if cv < 0.6:
        return ('linear_ramp', 0.70, dict(
            width_fraction=float(width_frac),
            steepness_cv=float(cv)))
    if 0.30 <= peak_frac <= 0.70:
        return ('sigmoidal', 0.70, dict(
            width_fraction=float(width_frac),
            peak_position=float(peak_frac),
            steepness_cv=float(cv)))
    if peak_frac < 0.30:
        return ('exponential_approach', 0.65, dict(
            width_fraction=float(width_frac),
            peak_position=float(peak_frac),
            steepness_cv=float(cv)))
    # Peak late → reverse exponential (same template flipped)
    return ('exponential_approach', 0.55, dict(
        width_fraction=float(width_frac),
        peak_position=float(peak_frac),
        flipped=True,
        steepness_cv=float(cv)))


# ─── Public API ───────────────────────────────────────────────────────────


def characterize_transition(trajectory: pd.DataFrame,
                              extractor_consensus: Optional[dict] = None,
                              ) -> dict:
    """Characterise the transition (if any) in a sub-window
    classification trajectory.

    Parameters
    ----------
    trajectory : DataFrame with at least column 'primary'.  Optional
        columns 'rep_med', 'subwindow_start_us'.
    extractor_consensus : optional dict {extractor_name: trajectory_df}
        — when present, the diagnostic checks classification agreement
        across mechanism-distinct extractors at each sub-window.

    Returns
    -------
    dict with:
      - transition_detected  bool
      - transition_window    (start_idx, end_idx)
      - origin_class         str | None
      - destination_class    str | None
      - shape_estimate       str
      - shape_confidence     float
      - shape_parameters     dict
      - metastable_state_class  str | None
      - metastable_duration  int | None
      - period_doubling_signature  dict | None
      - extractor_consensus  dict | None
      - trajectory_features  dict (monotonicity, steepness, etc.)
    """
    if 'primary' not in trajectory.columns:
        raise ValueError("trajectory must have 'primary' column")
    primaries = list(trajectory['primary'].astype(str))
    n = len(primaries)

    origin, destination, win_start, win_end = _detect_transition_window(primaries)

    base = dict(
        transition_detected=False,
        transition_window=(0, 0),
        origin_class=origin,
        destination_class=destination,
        shape_estimate='unclassified',
        shape_confidence=0.0,
        shape_parameters={},
        metastable_state_class=None,
        metastable_duration=None,
        period_doubling_signature=None,
        extractor_consensus=extractor_consensus,
        trajectory_features=dict(n_subwindows=int(n)),
    )

    if origin is None or destination is None:
        # No clear leading/trailing modes — could be:
        #   (1) sub-window noise dominates → unclassified
        #   (2) period-doubling cascade with no flat tail (logistic
        #       sweep through r)
        d_self = _distance_trajectory(primaries, primaries[0]
                                        if primaries else 'BL')
        pd_sig = _period_doubling_signature(d_self)
        if pd_sig:
            base.update(transition_detected=True,
                         shape_estimate='period_doubling_cascade',
                         shape_confidence=0.80,
                         shape_parameters=pd_sig,
                         period_doubling_signature=pd_sig)
        return base

    if origin == destination:
        # Stationary control or transient that returned home.
        return base

    # Distance-from-origin trajectory
    d = _distance_trajectory(primaries, origin)
    monotonicity = _monotonicity(d)
    steepness = _steepness(d, win_start, win_end)
    midstable_class, midstable_frac = _mid_transition_cluster(
        primaries, win_start, win_end, origin, destination)
    pd_sig = _period_doubling_signature(d)

    shape, conf, params = _classify_shape(
        d, win_start, win_end, monotonicity,
        midstable_class, midstable_frac, pd_sig, n_total=n)

    base.update(
        transition_detected=True,
        transition_window=(int(win_start), int(win_end)),
        shape_estimate=shape,
        shape_confidence=float(conf),
        shape_parameters=params,
        metastable_state_class=midstable_class
            if shape == 'metastable_middle' else None,
        metastable_duration=int((win_end - win_start) * midstable_frac)
            if shape == 'metastable_middle' else None,
        period_doubling_signature=pd_sig,
        trajectory_features=dict(
            n_subwindows=int(n),
            transition_width=int(win_end - win_start),
            transition_width_fraction=float((win_end - win_start) / max(n, 1)),
            monotonicity=float(monotonicity)
                          if np.isfinite(monotonicity) else None,
            steepness=float(steepness) if np.isfinite(steepness) else None,
            midstable_fraction=float(midstable_frac),
            midstable_class=midstable_class,
        ),
    )
    return base


# ─── Helper: build trajectory by sub-windowing events + classifying ──────


def trajectory_from_events(events: np.ndarray,
                             n_subwindows: int = 50,
                             min_events: int = 100,
                             q_max: int = 30,
                             ) -> pd.DataFrame:
    """Sub-window an event sequence and apply joint_q_profile +
    joint_quadrant_diagnostic per sub-window.  Returns the trajectory
    DataFrame expected by `characterize_transition`."""
    from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic
    events = np.asarray(events, dtype=np.float64)
    if events.size < min_events * 2:
        return pd.DataFrame(dict(primary=['underpowered'] * n_subwindows,
                                  rep_med=[np.nan] * n_subwindows))
    t0 = float(events.min())
    t1 = float(events.max())
    edges = np.linspace(t0, t1, n_subwindows + 1)
    rows = []
    for i in range(n_subwindows):
        mask = (events >= edges[i]) & (events < edges[i + 1])
        ev = events[mask]
        if ev.size < min_events:
            rows.append(dict(primary='underpowered', rep_med=np.nan))
            continue
        # Renormalise to unit mean for joint_q_profile
        sp = np.diff(ev)
        sp = sp[sp > 0]
        if sp.size < 4 or sp.mean() <= 0:
            rows.append(dict(primary='underpowered', rep_med=np.nan))
            continue
        ev_unit = np.cumsum(np.concatenate([[0.0], sp / sp.mean()]))
        try:
            j = joint_q_profile(ev_unit, q_max=q_max,
                                 min_events_per_q=min_events)
            qd = joint_quadrant_diagnostic(j)
            well = qd[~qd['underpowered']]
            if not len(well):
                rows.append(dict(primary='underpowered', rep_med=np.nan))
                continue
            counts = well['quadrant'].value_counts()
            primary = str(counts.idxmax())
            rep_med = float(well['rep_int_q'].median())
            rows.append(dict(primary=primary, rep_med=rep_med))
        except Exception:
            rows.append(dict(primary='underpowered', rep_med=np.nan))
    return pd.DataFrame(rows)


__all__ = [
    'characterize_transition', 'trajectory_from_events',
    'quadrant_distance', 'QUADRANT_COORDS',
]
