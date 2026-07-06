"""
Intermittency extraction for the criticality tool.

Inputs come from the PLL bank as binary lock_map[N_pll × T] arrays.  This
module turns those into:

  • Dwell-time sequences (lock_dwells, slip_dwells) per PLL — run-length
    encoding of the binary series.
  • Lock-event point process (lock_onsets) per PLL — sample indices of
    each 0→1 transition.
  • Power-law MLE fit on dwell sequences (Clauset-Shalizi-Newman) plus a
    Kolmogorov–Smirnov goodness-of-fit test.
  • Fano factor F(T) = var(N(T)) / mean(N(T)) — fast pre-screen of
    sub/super-Poisson statistics.  F = 1 for Poisson; F < 1 indicates
    level repulsion (GUE-like); F > 1 indicates clustering.
  • Aggregate point process across PLLs — each PLL's events unfolded by
    its own local mean spacing before pooling, so the combined process
    has unit mean spacing regardless of per-PLL lock rate.
  • Stern-Brocot depth of each locking rational and depth-of-events
    histogram, comparable to the geometric (2^−d) p-adic uniform prior.

All of the analysis runs on numpy arrays; no GPU dependency.  This is the
"refine on CPU" half of the GPU-sweep / CPU-refine workflow.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np


# ── Dwell-time extraction (RLE) ───────────────────────────────────────────────
@dataclass
class DwellRecord:
    """Per-PLL intermittency summary."""
    lock_dwells:  np.ndarray   # int — durations of locked runs (samples)
    slip_dwells:  np.ndarray   # int — durations of slipped runs (samples)
    lock_onsets:  np.ndarray   # int — sample index of each 0→1 transition
    lock_offsets: np.ndarray   # int — sample index of each 1→0 transition
    lock_fraction: float
    n_events:     int          # number of lock onsets


def extract_dwells(lock_series: np.ndarray) -> DwellRecord:
    """
    Run-length encode a binary lock series.  Returns lock and slip dwell
    arrays plus the sample indices of state transitions.

    A "lock onset" is a 0→1 transition; if the series begins with 1, that
    leading run is *not* counted as an onset (we don't know when it
    started).  Trailing runs at either end are kept as dwells (they're
    valid duration measurements; the only ambiguity is whether they would
    have continued past the recording).
    """
    s = np.asarray(lock_series, dtype=np.uint8)
    if s.size == 0:
        return DwellRecord(np.zeros(0, int), np.zeros(0, int),
                            np.zeros(0, int), np.zeros(0, int), 0.0, 0)

    # Find transition indices.  diff[i] = 1 means s[i+1]=1, s[i]=0  (onset at i+1).
    d = np.diff(s.astype(np.int8))
    onsets  = np.where(d ==  1)[0] + 1   # 0→1 at index i+1
    offsets = np.where(d == -1)[0] + 1   # 1→0 at index i+1

    # Build runs.  Append sentinel boundaries at 0 and N to capture leading/trailing.
    boundaries = np.concatenate([[0], np.where(d != 0)[0] + 1, [s.size]])
    runs = np.diff(boundaries)
    states = np.empty(len(runs), dtype=np.uint8)
    pos = 0
    for i, r in enumerate(runs):
        states[i] = s[pos]
        pos += r

    lock_dwells = runs[states == 1].astype(np.int64)
    slip_dwells = runs[states == 0].astype(np.int64)
    lock_fraction = float(s.mean()) if s.size > 0 else 0.0
    return DwellRecord(
        lock_dwells=lock_dwells,
        slip_dwells=slip_dwells,
        lock_onsets=onsets,
        lock_offsets=offsets,
        lock_fraction=lock_fraction,
        n_events=int(onsets.size),
    )


# ── Power-law MLE (Clauset–Shalizi–Newman) ────────────────────────────────────
@dataclass
class PowerLawFit:
    alpha:       float          # estimated exponent
    alpha_stderr: float         # standard error of α
    tau_min:     float          # lower-cutoff used
    n_used:      int            # # of dwells ≥ τ_min
    ks_stat:     float          # Kolmogorov–Smirnov statistic
    ks_pvalue:   float          # asymptotic p-value
    valid:       bool           # True if fit was performable (n ≥ 20)


def fit_power_law_mle(
    dwells:  np.ndarray,
    tau_min: float = 10.0,
    auto_tau_min: bool = False,
    tau_min_candidates: Optional[np.ndarray] = None,
) -> PowerLawFit:
    """
    Maximum-likelihood fit of P(τ) ∝ τ^(-α) to discrete dwell durations.

    Estimator (CSN, discrete-data approximation):
        α_hat = 1 + n / Σ ln(τ_i / (τ_min − ½))

    Standard error: (α_hat − 1) / sqrt(n)  (also from CSN).

    Goodness of fit: KS distance between the empirical CDF of dwells
    ≥ τ_min and the analytic discrete-power-law CDF, with p-value from
    the asymptotic Kolmogorov distribution.

    With auto_tau_min=True, sweeps tau_min over `tau_min_candidates`
    (default: unique dwells in [2, dwells.max() / 4]) and picks the
    candidate that minimises KS distance.  This is the full CSN τ_min
    procedure.
    """
    dwells = np.asarray(dwells, dtype=np.int64)

    def _fit_at(tm):
        sel = dwells[dwells >= tm]
        n = sel.size
        if n < 20:
            return PowerLawFit(np.nan, np.nan, float(tm), n, np.nan, np.nan, False)
        denom = np.log(sel.astype(np.float64) / (tm - 0.5)).sum()
        if denom <= 0:
            return PowerLawFit(np.nan, np.nan, float(tm), n, np.nan, np.nan, False)
        alpha = 1.0 + n / denom
        stderr = (alpha - 1.0) / np.sqrt(n)

        # KS test: empirical CDF vs continuous-power-law CDF.
        # F_theory(τ) = 1 − (τ / (τ_min − ½))^(−(α − 1))
        sorted_sel = np.sort(sel.astype(np.float64))
        emp_cdf = np.arange(1, n + 1) / n
        F_th = 1.0 - (sorted_sel / (tm - 0.5)) ** (-(alpha - 1.0))
        ks = float(np.max(np.abs(emp_cdf - F_th)))
        # Asymptotic Kolmogorov distribution for the p-value.
        sqrt_n = np.sqrt(n)
        x = ks * (sqrt_n + 0.12 + 0.11 / sqrt_n)
        # Q-Kolmogorov series:  P(K > x) = 2 Σ_{k=1..} (-1)^{k-1} exp(-2 k² x²)
        if x < 1e-12:
            p = 1.0
        else:
            p = 0.0
            for k in range(1, 100):
                term = 2.0 * ((-1) ** (k - 1)) * np.exp(-2.0 * k * k * x * x)
                p += term
                if abs(term) < 1e-12:
                    break
            p = float(np.clip(p, 0.0, 1.0))
        return PowerLawFit(float(alpha), float(stderr), float(tm),
                           int(n), float(ks), float(p), True)

    if not auto_tau_min:
        return _fit_at(tau_min)

    if tau_min_candidates is None:
        if dwells.size == 0:
            return _fit_at(tau_min)
        hi = max(2, int(dwells.max() // 4))
        tau_min_candidates = np.unique(np.clip(np.arange(2, hi + 1), 2, hi))

    best = None
    for tm in tau_min_candidates:
        fit = _fit_at(int(tm))
        if not fit.valid:
            continue
        if best is None or fit.ks_stat < best.ks_stat:
            best = fit
    return best if best is not None else _fit_at(tau_min)


# ── Fano factor F(T) ──────────────────────────────────────────────────────────
def fano_factor(
    events:           np.ndarray,
    total_samples:    int,
    window_samples:   np.ndarray,
    n_windows_min:    int = 20,
) -> dict:
    """
    Fano factor F(T) = var(N(T)) / mean(N(T)) for a point process.
    `events` is sorted sample indices of lock onsets.  `window_samples` is
    a 1-D array of window sizes T (in samples) at which to evaluate F.

    The signal is partitioned into disjoint windows of length T (any
    short trailing remainder dropped); we count events per window, then
    compute variance over those counts divided by the mean count.

    Returns a dict with keys:
        'T_samples'   — window sizes used
        'F'           — Fano factor at each T (NaN if too few windows)
        'mean_count'  — mean events per window
        'var_count'   — variance of counts per window
    """
    events = np.asarray(events, dtype=np.int64)
    window_samples = np.asarray(window_samples, dtype=np.int64)
    F = np.full(window_samples.shape, np.nan, dtype=np.float64)
    mean_c = np.full(window_samples.shape, np.nan, dtype=np.float64)
    var_c  = np.full(window_samples.shape, np.nan, dtype=np.float64)

    if events.size == 0 or total_samples <= 0:
        return dict(T_samples=window_samples, F=F, mean_count=mean_c, var_count=var_c)

    for i, T in enumerate(window_samples):
        if T <= 0:
            continue
        nW = total_samples // T
        if nW < n_windows_min:
            continue
        # Bin events into the disjoint windows.
        idx = events[events < nW * T] // T   # integer in [0, nW)
        counts = np.bincount(idx, minlength=nW).astype(np.float64)
        m = counts.mean()
        if m <= 0:
            F[i] = 0.0
        else:
            v = counts.var(ddof=1) if nW > 1 else 0.0
            F[i] = float(v / m)
        mean_c[i] = m
        var_c[i]  = counts.var(ddof=1) if nW > 1 else 0.0

    return dict(T_samples=window_samples, F=F, mean_count=mean_c, var_count=var_c)


# ── Aggregate (unfolded, pooled) lock-event process ───────────────────────────
def aggregate_unfolded_events(
    per_pll_onsets: list[np.ndarray],
) -> np.ndarray:
    """
    Pool lock-onset events across PLLs after unfolding each PLL's process
    by its own mean spacing.  The result has unit mean spacing.

    Per-PLL processes with too few events (< 4) are skipped.
    """
    pooled = []
    for ons in per_pll_onsets:
        ons = np.asarray(ons, dtype=np.float64)
        if ons.size < 4:
            continue
        spacings = np.diff(ons)
        d = float(spacings.mean())
        if d <= 0:
            continue
        pooled.append(ons / d)
    if not pooled:
        return np.zeros(0, dtype=np.float64)
    return np.sort(np.concatenate(pooled))


# ── Stern-Brocot depth ────────────────────────────────────────────────────────
def stern_brocot_depth(p: int, q: int) -> int:
    """
    Depth of the rational p/q in the Stern-Brocot tree.  The root 1/1 is
    depth 0; 1/2 and 2/1 are depth 1; 1/3, 2/3, 3/2, 3/1 are depth 2; etc.

    Computed from the continued-fraction expansion of p/q:
      depth = (Σ partial quotients) − 1
    after dropping the leading 0 if p < q.  (The −1 accounts for the
    final step that *reaches* the rational rather than descending past it.)

    Examples:
      1/1 → 0,  1/2 → 1,  2/3 → 2,  3/5 → 3,  5/8 → 4
    """
    from math import gcd
    g = gcd(int(p), int(q))
    if g <= 0:
        return 0
    a, b = int(p) // g, int(q) // g
    if a == 0 or b == 0:
        return 0
    coefs = []
    while b > 0:
        coefs.append(a // b)
        a, b = b, a % b
    if (int(p) // g) < (int(q) // g):
        coefs = coefs[1:]      # drop leading 0 in cf for p<q
    if not coefs:
        return 0
    return int(sum(coefs) - 1)


def depth_histogram(
    per_pll: list[dict],
    weight_by_events: bool = True,
) -> dict:
    """
    Histogram of locking-rational depths.

    `per_pll` should be the IntermittencyReport.per_pll list, each entry
    carrying a `stern_brocot_depth` field (set by analyze_lock_map when
    Farey pairs were provided).  PLLs with zero lock events are excluded.

    With weight_by_events=True (default), each PLL contributes its event
    count to its depth bin — what you want for "how the lock-event mass
    distributes by depth."  With False, each locking PLL contributes 1.

    Returns dict with:
      'depth'             — sorted unique depths present
      'bin_count'         — number of locking PLLs at each depth
      'event_count'       — number of lock events (sum across PLLs at depth)
      'rationals_at_depth' — count of *available* PLLs at each depth in the
                            full bank (locked or not), useful for normalising
      'geometric_ref'     — 2^(−d), the p-adic uniform reference
    """
    by_depth_locked = {}      # depth → # locking PLLs
    by_depth_events = {}      # depth → # events
    by_depth_total  = {}      # depth → # PLLs in bank at that depth
    for d in per_pll:
        depth = d.get('stern_brocot_depth', None)
        if depth is None:
            continue
        by_depth_total[depth] = by_depth_total.get(depth, 0) + 1
        if d['n_events'] > 0:
            by_depth_locked[depth] = by_depth_locked.get(depth, 0) + 1
            by_depth_events[depth] = by_depth_events.get(depth, 0) + d['n_events']
    depths = sorted(by_depth_total.keys())
    geo = np.array([2.0 ** (-d) for d in depths])
    return dict(
        depth=np.array(depths, dtype=int),
        bin_count=np.array([by_depth_locked.get(d, 0) for d in depths], dtype=int),
        event_count=np.array([by_depth_events.get(d, 0) for d in depths], dtype=int),
        rationals_at_depth=np.array([by_depth_total[d] for d in depths], dtype=int),
        geometric_ref=geo / geo.sum() if geo.sum() > 0 else geo,
    )


# ── Streamlined summary for parameter sweeps ──────────────────────────────────
def fast_sweep_summary(
    lock_map:    np.ndarray,
    sr:          float,
    farey_pairs: list[tuple[int, int]],
) -> dict:
    """
    Compact per-cell summary used by parameter sweeps.  Returns ONLY the
    scalar metrics needed for downstream HDF5 storage; skips the per-PLL
    power-law fits and the full Fano curves that analyze_lock_map computes.

    Vectorised RLE per PLL keeps this fast — ~30 ms for 250 PLLs × 1.3 M
    samples.  Memory complexity: O(N_pll · N) for lock_map plus the dwell
    arrays (a few MB).

    Returned dict:
        F_aggregate_L1, F_perpll_mean, F_perpll_std,
        n_locking_plls, n_events_total,
        depth_kl, mean_lock_ms, mean_slip_ms,
        depth_event_counts, depth_pll_counts, depths
    """
    N_pll, N = lock_map.shape

    n_events_per_pll = np.zeros(N_pll, dtype=int)
    lock_fractions   = np.zeros(N_pll, dtype=float)
    fano_per_pll     = np.full(N_pll, np.nan)
    onsets_all       = []
    all_lock_dwells  = []
    all_slip_dwells  = []
    depth_per_pll    = np.zeros(N_pll, dtype=int)

    for p in range(N_pll):
        s = lock_map[p]
        if s.size == 0 or int(s.sum()) == 0:
            onsets        = np.zeros(0, dtype=np.int64)
            lock_dwells   = np.zeros(0, dtype=np.int64)
            slip_dwells   = np.zeros(0, dtype=np.int64)
            lock_fractions[p] = 0.0
        else:
            d = np.diff(s.astype(np.int8))
            onsets  = np.where(d ==  1)[0] + 1
            offsets_idx = np.where(d == -1)[0] + 1   # (kept for completeness)
            change_pts = np.where(d != 0)[0] + 1
            boundaries = np.concatenate([[0], change_pts, [s.size]])
            runs = np.diff(boundaries)
            states = s[boundaries[:-1]].astype(np.uint8)
            lock_dwells = runs[states == 1].astype(np.int64)
            slip_dwells = runs[states == 0].astype(np.int64)
            lock_fractions[p] = float(s.mean())

        n_events_per_pll[p] = onsets.size
        onsets_all.append(onsets.astype(np.int64))
        all_lock_dwells.append(lock_dwells)
        all_slip_dwells.append(slip_dwells)

        # Per-PLL Fano at L=1 in the PLL's own mean-spacing units.
        if onsets.size >= 5:
            spacings_pll = np.diff(onsets)
            ms = float(spacings_pll.mean())
            if ms > 0:
                T_int = max(1, int(round(ms)))
                nW = N // T_int
                if nW >= 5:
                    idx = onsets[onsets < nW * T_int] // T_int
                    counts = np.bincount(idx, minlength=nW).astype(np.float64)
                    m_c = counts.mean()
                    if m_c > 0:
                        v_c = counts.var(ddof=1) if nW > 1 else 0.0
                        fano_per_pll[p] = float(v_c / m_c)

        # Stern-Brocot depth.
        if p < len(farey_pairs):
            pp, qq = farey_pairs[p]
            depth_per_pll[p] = stern_brocot_depth(pp, qq)

    # Aggregate Fano at L=1 (after re-unfolding the pooled events).
    aggregate = aggregate_unfolded_events(onsets_all)
    F_agg = float('nan')
    if aggregate.size >= 20:
        spacings = np.diff(aggregate)
        if spacings.size > 0:
            pooled_mean = float(spacings.mean())
            if pooled_mean > 0:
                re_unfolded = aggregate / pooled_mean
                scale = 1000
                events_int = (re_unfolded * scale).astype(np.int64)
                total_int  = int(np.ceil(float(re_unfolded.max()) * scale))
                T_int = scale
                nW = total_int // T_int
                if nW >= 5:
                    idx = events_int[events_int < nW * T_int] // T_int
                    counts = np.bincount(idx, minlength=nW).astype(np.float64)
                    m_c = counts.mean()
                    if m_c > 0:
                        v_c = counts.var(ddof=1) if nW > 1 else 0.0
                        F_agg = float(v_c / m_c)

    # Depth histogram + KL vs geometric (2^-d).
    unique_depths = np.unique(depth_per_pll)
    depth_pll_counts = np.array(
        [int((depth_per_pll == d).sum()) for d in unique_depths], dtype=int)
    depth_event_counts = np.array(
        [int(n_events_per_pll[depth_per_pll == d].sum()) for d in unique_depths], dtype=int)
    if depth_event_counts.sum() > 0:
        obs = depth_event_counts.astype(np.float64) / depth_event_counts.sum()
        ref = np.array([2.0 ** (-int(d)) for d in unique_depths], dtype=np.float64)
        ref = ref / ref.sum()
        mask = (obs > 0) & (ref > 0)
        kl = float((obs[mask] * np.log(obs[mask] / ref[mask])).sum())
    else:
        kl = float('nan')

    locking_mask = lock_fractions > 0.01
    n_locking    = int(locking_mask.sum())
    total_events = int(n_events_per_pll.sum())

    f_locking = fano_per_pll[locking_mask]
    f_locking = f_locking[~np.isnan(f_locking)]
    F_perpll_mean = float(f_locking.mean()) if f_locking.size > 0 else float('nan')
    F_perpll_std  = float(f_locking.std(ddof=1)) if f_locking.size > 1 else float('nan')

    all_lock = np.concatenate(all_lock_dwells) if all_lock_dwells else np.zeros(0, dtype=np.int64)
    all_slip = np.concatenate(all_slip_dwells) if all_slip_dwells else np.zeros(0, dtype=np.int64)
    mean_lock_ms = float(all_lock.mean() * 1000.0 / sr) if all_lock.size > 0 else float('nan')
    mean_slip_ms = float(all_slip.mean() * 1000.0 / sr) if all_slip.size > 0 else float('nan')

    return dict(
        F_aggregate_L1=F_agg,
        F_perpll_mean=F_perpll_mean,
        F_perpll_std=F_perpll_std,
        n_locking_plls=n_locking,
        n_events_total=total_events,
        depth_kl=kl,
        mean_lock_ms=mean_lock_ms,
        mean_slip_ms=mean_slip_ms,
        depths=unique_depths.astype(int),
        depth_event_counts=depth_event_counts,
        depth_pll_counts=depth_pll_counts,
    )


# ── Top-level bank-level analysis ─────────────────────────────────────────────
@dataclass
class IntermittencyReport:
    per_pll: list[dict] = field(default_factory=list)   # one dict per PLL
    aggregate_unfolded_events: np.ndarray = field(
        default_factory=lambda: np.zeros(0, dtype=np.float64))
    aggregate_n_events: int = 0
    aggregate_fano: Optional[dict] = None
    depth_histogram: Optional[dict] = None
    sr: float = 0.0
    n_samples: int = 0


def analyze_lock_map(
    lock_map: np.ndarray,           # (N_pll, N) uint8
    sr: float,
    pll_freqs: Optional[np.ndarray] = None,
    farey_pairs: Optional[list[tuple[int, int]]] = None,
    fano_T_ms: Optional[np.ndarray] = None,
    pl_tau_min_samples: float = 50.0,
    pl_auto_tau_min: bool = True,
) -> IntermittencyReport:
    """
    Run the full intermittency pipeline against a PLL bank's lock_map.

    For each PLL: extract dwells, fit power law to slip-dwells (the
    intermittency-relevant quantity for criticality), compute Fano factor
    on lock-onset events.  Then pool and unfold across PLLs and report
    the aggregate Fano factor.

    Returns an IntermittencyReport.
    """
    lock_map = np.asarray(lock_map)
    N_pll, N = lock_map.shape
    if fano_T_ms is None:
        fano_T_ms = np.array([5, 10, 25, 50, 100, 250, 500, 1000], dtype=np.float64)
    fano_T_samples = (fano_T_ms * sr * 0.001).astype(np.int64)

    per_pll = []
    onsets_all = []

    for p in range(N_pll):
        s = lock_map[p]
        rec = extract_dwells(s)
        slip_pl = fit_power_law_mle(
            rec.slip_dwells if rec.slip_dwells.size > 0 else np.zeros(0, np.int64),
            tau_min=pl_tau_min_samples,
            auto_tau_min=pl_auto_tau_min,
        )
        lock_pl = fit_power_law_mle(
            rec.lock_dwells if rec.lock_dwells.size > 0 else np.zeros(0, np.int64),
            tau_min=pl_tau_min_samples,
            auto_tau_min=pl_auto_tau_min,
        )
        fano = fano_factor(rec.lock_onsets, N, fano_T_samples)
        depth = None
        rational_pq = None
        if farey_pairs is not None and p < len(farey_pairs):
            pq = farey_pairs[p]
            rational_pq = (int(pq[0]), int(pq[1]))
            depth = stern_brocot_depth(rational_pq[0], rational_pq[1])

        # Per-PLL Fano at L=1.0 in this PLL's own mean-spacing units.
        # F = var(N) / mean(N) computed over disjoint windows of width
        # equal to the per-PLL mean inter-event spacing.  Needs ≥5 windows
        # for a usable estimate.
        fano_at_L1 = float('nan')
        per_pll_mean_spacing_samples = float('nan')
        if rec.n_events >= 5:
            spacings_pll = np.diff(rec.lock_onsets)
            if spacings_pll.size > 0:
                ms = float(spacings_pll.mean())
                per_pll_mean_spacing_samples = ms
                if ms > 0:
                    T_int = max(1, int(round(ms)))
                    nW = N // T_int
                    if nW >= 5:
                        idx = rec.lock_onsets[rec.lock_onsets < nW * T_int] // T_int
                        counts = np.bincount(idx, minlength=nW).astype(np.float64)
                        m = counts.mean()
                        v = counts.var(ddof=1) if nW > 1 else 0.0
                        if m > 0:
                            fano_at_L1 = float(v / m)

        d = dict(
            pll_index=p,
            f_pll=(float(pll_freqs[p]) if pll_freqs is not None else None),
            rational=rational_pq,
            stern_brocot_depth=depth,
            lock_fraction=rec.lock_fraction,
            n_events=rec.n_events,
            n_lock_dwells=int(rec.lock_dwells.size),
            n_slip_dwells=int(rec.slip_dwells.size),
            mean_lock_ms=float(rec.lock_dwells.mean() * 1000.0 / sr) if rec.lock_dwells.size > 0 else np.nan,
            mean_slip_ms=float(rec.slip_dwells.mean() * 1000.0 / sr) if rec.slip_dwells.size > 0 else np.nan,
            mean_event_spacing_ms=(per_pll_mean_spacing_samples * 1000.0 / sr
                                    if not np.isnan(per_pll_mean_spacing_samples) else np.nan),
            slip_dwells=rec.slip_dwells,
            lock_dwells=rec.lock_dwells,
            slip_powerlaw=slip_pl,
            lock_powerlaw=lock_pl,
            fano=fano,
            fano_at_L1=fano_at_L1,
        )
        per_pll.append(d)
        onsets_all.append(rec.lock_onsets)

    aggregate = aggregate_unfolded_events(onsets_all)

    # Aggregate Fano factor.  After per-PLL unfolding then pooling, the
    # combined process has mean spacing ≈ 1/N_pll (each PLL contributes
    # ~unit-spaced events into the same time axis).  Re-unfold by the
    # pooled mean spacing so L expresses windows in *aggregate*
    # mean-spacing units.
    aggregate_fano = None
    if aggregate.size >= 20:
        spacings = np.diff(aggregate)
        pooled_mean = float(spacings.mean()) if spacings.size > 0 else 1.0
        if pooled_mean > 0:
            re_unfolded = aggregate / pooled_mean
            L_values = np.array([0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0], dtype=np.float64)
            scale = 1000
            events_int = (re_unfolded * scale).astype(np.int64)
            total_int  = int(np.ceil(float(re_unfolded.max()) * scale))
            windows    = (L_values * scale).astype(np.int64)
            aggregate_fano = fano_factor(events_int, total_int, windows)
            aggregate_fano['L_units_of_mean_spacing'] = L_values
            aggregate_fano['pooled_mean_spacing_per_pll_units'] = pooled_mean

    return IntermittencyReport(
        per_pll=per_pll,
        aggregate_unfolded_events=aggregate,
        aggregate_n_events=int(aggregate.size),
        aggregate_fano=aggregate_fano,
        depth_histogram=depth_histogram(per_pll) if farey_pairs is not None else None,
        sr=sr,
        n_samples=N,
    )
