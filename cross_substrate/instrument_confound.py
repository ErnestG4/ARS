"""
cross_substrate/instrument_confound.py — subtract the apparatus before the substrate.

REFRAME
-------
The fingerprint classifies a point process, but a point process is already
(substrate ⊗ instrument). The collection method imprints structure in the exact
observable we classify on — the spacings. Two apparatus artifacts impersonate
our two endpoints:

  • dead time / refractory window  → carves a short-range hole in the spacings
                                      → FAKES GUE-style level repulsion.
  • finite detection efficiency     → acts as random thinning of events
                                      → drives any process toward Poisson,
                                        FAKING the null.

This module is the apparatus-subtraction stage. It provides (1) apparatus
OPERATORS that act on event positions, (2) apparatus-INJECTED nulls (apply the
dataset's estimated dead time to the candidate null and compare against THAT,
not the bare null), (3) a THINNING sweep that flags efficiency-driven features,
(4) a METHOD-PERTURBATION discriminant that labels each axis covariant vs
invariant — only method-invariant axes promote to substrate candidates, and
(5) a LENSING LEDGER schema: the durable output is the metadata + the
perturbations a result survived, not the class label.

INSERTION POINT
---------------
Everything operates on raw event POSITIONS (times / sorted spectrum), upstream
of axes.canonical_spacings / axes.compute_family_I — so it is substrate-agnostic
and reuses the entire Family-I axis stack unchanged.

BOUND (stated, load-bearing)
----------------------------
Method-invariance means "robust to the manipulations we could run", NEVER "the
territory". The ledger records the perturbation SET survived; it makes no
universality claim. See [[carry_viewpoints_annotate_validity]],
[[false_positive_equivalence_classes]], [[support_set_respecting_nulls]].
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field, asdict
from typing import Callable, Dict, List, Optional, Sequence

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from axes import compute_family_I  # the matched axis stack (Family I + local)


# ── Axes we read the apparatus on ────────────────────────────────────────────
# Deliberately the SMALL-SPACING-sensitive subset: a dead-time hole and random
# thinning both act first on the short-range end of the NNS distribution, which
# is exactly what these four resolve. ks_gue↓ + mass03↓ is the dead-time
# repulsion signature; everything→Poisson is the thinning signature.
AXES = ("I.5_ks_gue", "I.11_mass03", "I.10_cv", "I.12_cv2", "I.8_brody_q")

# Finite boundaries each axis can RAIL against. An axis sitting NEAR a boundary
# barely moves under perturbation whether the structure is substrate OR apparatus
# (the GRB dead-time hole pins mass03→0 and brody→1, the GUE rails) — so low
# movement near a rail is INDETERMINATE, not invariant. The discriminant tests
# HEADROOM (proximity to a rail), not exact railing: an axis is promotable only if
# it has room to move AND chose not to; near a rail it is indeterminate unless it
# demonstrably swings OFF the rail (large absolute movement → covariant). Same
# railed-estimator trap as the KPM-floor lesson. None = unbounded on that side.
AXIS_BOUNDS = {
    "I.5_ks_gue": (0.0, None),   # KS distance — floor 0 (perfect GUE match)
    "I.11_mass03": (0.0, 1.0),   # fraction — floor 0 (dead-time hole), ceiling 1
    "I.10_cv": (0.0, None),      # CV — floor 0 (perfectly regular)
    "I.12_cv2": (0.0, None),     # CV2 — floor 0
    "I.8_brody_q": (0.0, 1.0),   # Brody q — 0 Poisson rail, 1 GUE rail
}
RAIL_MARGIN = 0.05               # headroom (axis units) below which an axis is "near a rail"

_POISSON_ANCHOR_CACHE: Dict[str, float] = {}


def poisson_anchors(n_events: int = 3000, n_seeds: int = 24) -> Dict[str, float]:
    """Where each axis sits for Poisson UNDER OUR OWN EXTRACTOR (the 2–98% trim +
    unit-mean renorm of canonical_spacings shifts the textbook values — e.g.
    trimmed Poisson ks_gue ≈ 0.286, not the untrimmed 0.34). Calibrated
    empirically + cached so the washout metric measures gap-to-Poisson against
    the same lens it reads the data through. Used only to express how much of
    the gap a perturbation closes — direction/magnitude, not absolute truth."""
    if not _POISSON_ANCHOR_CACHE:
        acc: Dict[str, list] = {a: [] for a in AXES}
        for k in range(n_seeds):
            rng = np.random.default_rng(70_000 + k)
            for a, v in axis_values(poisson_positions(n_events, rng)).items():
                acc[a].append(v)
        _POISSON_ANCHOR_CACHE.update(
            {a: float(np.mean(v)) for a, v in acc.items() if v})
    return _POISSON_ANCHOR_CACHE


def axis_values(positions: Sequence[float], axes=AXES) -> Dict[str, float]:
    """Compute the apparatus-readout axes from raw positions (routes through
    compute_family_I, which unit-mean-unfolds + trims identically to every
    port). Drops axes that return None (under-powered)."""
    full = compute_family_I(positions)
    return {a: full[a] for a in axes if full.get(a) is not None}


# ════════════════════════════════════════════════════════════════════════════
# 1. APPARATUS OPERATORS  (act on positions, in the position's own time units)
# ════════════════════════════════════════════════════════════════════════════

def apply_deadtime(times: Sequence[float], tau: float,
                   paralyzable: bool = False) -> np.ndarray:
    """Detector dead time / absolute refractory window of length `tau` (same
    units as `times`). After a kept event, any event arriving within `tau` is
    deleted — carving a hole at small spacings.

    paralyzable=False (default): non-extending dead time. The clock restarts
        only on KEPT events. Mirrors run_phase21_calibrators.synthesise_deadtime
        and a neuron's absolute refractory period.
    paralyzable=True: extending dead time. Every arrival (even a lost one)
        restarts the clock — the detector-saturation regime, where a dense burst
        can blank the instrument for longer than one tau.
    """
    t = np.sort(np.asarray(times, dtype=np.float64))
    if t.size == 0:
        return t
    kept = [t[0]]
    last_seen = t[0]      # last ARRIVAL (paralyzable) — clock reference
    last_kept = t[0]      # last KEPT event   (non-paralyzable) — clock reference
    for x in t[1:]:
        ref = last_seen if paralyzable else last_kept
        if x - ref >= tau:
            kept.append(x)
            last_kept = x
        last_seen = x     # arrival always seen; only matters when paralyzable
    return np.asarray(kept, dtype=np.float64)


def random_thin(times: Sequence[float], p_keep: float,
                rng: np.random.Generator) -> np.ndarray:
    """Finite detection efficiency as independent Bernoulli(p_keep) retention —
    random thinning. Thinning a Poisson process leaves Poisson; thinning ANY
    process drives its NNS toward Poisson. p_keep = estimated efficiency."""
    t = np.asarray(times, dtype=np.float64)
    if t.size == 0:
        return t
    return np.sort(t[rng.random(t.size) <= p_keep])


def mean_isi(times: Sequence[float]) -> float:
    t = np.sort(np.asarray(times, dtype=np.float64))
    d = np.diff(t)
    d = d[d > 0]
    return float(d.mean()) if d.size else float("nan")


def deadtime_fraction(times: Sequence[float], tau: float) -> float:
    """Estimated dead time as a fraction of the mean ISI — the unit in which a
    dead-time hole becomes comparable across substrates/rates. ~0.3 already
    fakes appreciable repulsion; ≳1 saturates the detector."""
    m = mean_isi(times)
    return float(tau / m) if m > 0 else float("nan")


# ════════════════════════════════════════════════════════════════════════════
# 1b. CONTAMINATION  (the ADDITIVE apparatus effect — the one that fakes clustering)
# ════════════════════════════════════════════════════════════════════════════

def refractory_violation_rate(times: Sequence[float],
                              refractory_s: float = 0.002) -> dict:
    """Dead time and thinning are SUBTRACTIVE (they remove spikes) — they suppress
    clustering and fake repulsion, so the dead-time bracket ARMORS a clustering
    finding. Sort over-merge is the opposite: ADDITIVE. Merging two units injects
    another cell's spikes, producing sub-refractory ISIs and spurious short-lag
    structure that reads as burstiness — the ONE apparatus effect that can FAKE
    clustering. The cheap tell is the refractory-violation rate (RPV): the fraction
    of ISIs below the biological absolute refractory (a single well-isolated neuron
    cannot fire faster). A clustered unit with high RPV is a MERGE SUSPECT, not a
    substrate finding. Pair with any isolation / L-ratio the sort already carries."""
    t = np.sort(np.asarray(times, dtype=np.float64))
    d = np.diff(t)
    d = d[d >= 0]
    if d.size < 50:
        return {"rpv": None, "n_isi": int(d.size), "refractory_s": refractory_s}
    return {"rpv": float(np.mean(d < refractory_s)),
            "rpv_1ms": float(np.mean(d < 0.001)),
            "n_violations": int(np.sum(d < refractory_s)),
            "n_isi": int(d.size), "refractory_s": refractory_s}


def contamination_flag(rpv: Optional[float], clean: float = 0.005,
                       suspect: float = 0.02) -> str:
    """CLEAN (<0.5% RPV) / MARGINAL / MERGE_SUSPECT (>2% RPV) / UNKNOWN.
    Thresholds follow the common bad-cluster heuristic; a MERGE_SUSPECT clustering
    verdict is contamination, not substrate."""
    if rpv is None:
        return "UNKNOWN"
    if rpv > suspect:
        return "MERGE_SUSPECT"
    if rpv > clean:
        return "MARGINAL"
    return "CLEAN"


# ════════════════════════════════════════════════════════════════════════════
# 2. CANDIDATE NULLS  (positions; unit-rate so tau is in mean-ISI units)
# ════════════════════════════════════════════════════════════════════════════

def poisson_positions(n: int, rng: np.random.Generator) -> np.ndarray:
    """Homogeneous Poisson, unit mean ISI (cumsum of Exp(1))."""
    return np.cumsum(rng.exponential(1.0, size=n))


def gue_positions(n: int, rng: np.random.Generator) -> np.ndarray:
    """GUE eigenvalue spectrum, unfolded to unit mean spacing (Dumitriu–Edelman
    tridiagonal + Wigner-semicircle unfold) — the canonical level-repulsion
    reference. Falls back to a hard-core surrogate if the eigensolve is
    unavailable, so the module stays runnable headless."""
    try:
        # χ-distributed sub/super-diagonal (β=2) tridiagonal Hermite model.
        d = rng.standard_normal(n)
        beta = 2
        off = np.array([np.sqrt(rng.chisquare(beta * k) / 2.0)
                        for k in range(n - 1, 0, -1)])
        m = np.diag(d) + np.diag(off, 1) + np.diag(off, -1)
        ev = np.sort(np.linalg.eigvalsh(m))
        # unfold by Wigner semicircle CDF, R = sqrt(2 beta n)
        R = np.sqrt(2.0 * beta * n)
        x = np.clip(ev / R, -1, 1)
        cdf = 0.5 + (x * np.sqrt(1 - x * x) + np.arcsin(x)) / np.pi
        u = cdf * n
        return u - u.min()
    except Exception:
        # hard-core fallback (Matérn-II style): repulsion without the eigensolve
        base = np.cumsum(rng.exponential(1.0, size=4 * n))
        kept = [base[0]]
        for x in base[1:]:
            if x - kept[-1] >= 0.7:
                kept.append(x)
            if len(kept) >= n:
                break
        return np.asarray(kept)


NULLS: Dict[str, Callable[[int, np.random.Generator], np.ndarray]] = {
    "poisson": poisson_positions,
    "gue": gue_positions,
}


# ════════════════════════════════════════════════════════════════════════════
# 3. APPARATUS-INJECTED NULL  (compare empirical against the dead-time-convolved
#    null, NOT the bare null)
# ════════════════════════════════════════════════════════════════════════════

def _ensemble_axes(sampler, n: int, n_seeds: int, base_seed: int,
                   op=None) -> Dict[str, dict]:
    """mean ± sd of each axis over `n_seeds` realizations of `sampler` (n events),
    optionally pushed through apparatus operator `op(positions, rng)`."""
    acc: Dict[str, list] = {a: [] for a in AXES}
    for k in range(n_seeds):
        rng = np.random.default_rng(base_seed + k)
        pos = sampler(n, rng)
        if op is not None:
            pos = op(pos, rng)
        for a, v in axis_values(pos).items():
            acc[a].append(v)
    return {a: {"mean": float(np.mean(v)), "sd": float(np.std(v)), "n": len(v)}
            for a, v in acc.items() if v}


def apparatus_subtracted_comparison(
        positions: Sequence[float], tau_frac: float,
        tau_frac_rel_err: float = 0.0,
        null_kind: str = "poisson", n_seeds: int = 24,
        base_seed: int = 0) -> Dict[str, dict]:
    """Re-derive the expected NNS under the apparatus and compare the empirical
    axes against THAT, not the bare null.

    tau_frac is the ESTIMATED dead time as a fraction of the mean ISI;
    tau_frac_rel_err is its relative uncertainty. On real data τ is ESTIMATED,
    not known — so its error bars must widen the injected null (τ drawn per seed
    from tau_frac·(1 + rel_err·N(0,1))). A point-estimate null (rel_err=0) is
    itself wrong: too-narrow it UNDER-absorbs (promotes an artifact), and an
    over-large fixed τ OVER-absorbs (buries real residual). Propagating the
    uncertainty makes RESIDUAL_STRUCTURE a conservative call.

    For each axis returns: empirical value, bare-null band, dead-time-injected-
    null band (null + dead time at tau_frac·mean-ISI, marginalized over τ error),
    and a verdict:
      APPARATUS_EXPLAINS  — emp consistent with injected-null, far from bare null
                            (the 'structure' is the dead-time hole, not substrate)
      RESIDUAL_STRUCTURE  — emp departs from the injected-null too
                            (structure survives apparatus subtraction)
      NULL                — emp already consistent with the bare null
    """
    emp = axis_values(positions)
    n = max(len(np.asarray(positions)), 200)
    sampler = NULLS[null_kind]

    def dt_op(pos, rng):
        tf = tau_frac * (1.0 + tau_frac_rel_err * rng.standard_normal())
        tf = max(tf, 0.0)                      # τ cannot be negative
        tau = tf * mean_isi(pos)
        return apply_deadtime(pos, tau) if np.isfinite(tau) else pos

    bare = _ensemble_axes(sampler, n, n_seeds, base_seed)
    inj = _ensemble_axes(sampler, n, n_seeds, base_seed + 10_000, op=dt_op)

    out: Dict[str, dict] = {}
    for a in emp:
        if a not in bare or a not in inj:
            continue
        b, j = bare[a], inj[a]
        z_bare = abs(emp[a] - b["mean"]) / (b["sd"] + 1e-12)
        z_inj = abs(emp[a] - j["mean"]) / (j["sd"] + 1e-12)
        if z_bare < 2.5:
            verdict = "NULL"
        elif z_inj < 2.5:
            verdict = "APPARATUS_EXPLAINS"
        else:
            verdict = "RESIDUAL_STRUCTURE"
        out[a] = dict(empirical=float(emp[a]),
                      bare_null=b, injected_null=j,
                      z_vs_bare=float(z_bare), z_vs_injected=float(z_inj),
                      verdict=verdict)
    return out


def estimate_deadtime_floor(times: Sequence[float], pct: float = 0.5,
                            rel_err: float = 0.5) -> dict:
    """Estimate the empirical short-ISI floor τ for the MAXIMAL-apparatus (WIDE)
    null — the dead time that would have to exist to censor everything below the
    observed floor.

    Uses the `pct`-th PERCENTILE of the ISIs, NOT the sample minimum: the min is
    an extreme order statistic whose variance the bootstrap badly underestimates,
    so a min-based τ and a bootstrapped error on it both read optimistically
    tight. We take P0.5 and DELIBERATELY WIDEN rel_err past any bootstrap value
    (default 0.5) — given the apparatus must not be under-modeled, the band should
    err wide. Returns τ as a fraction of the mean ISI (the unit the injected null
    uses) plus the widened rel_err."""
    d = np.diff(np.sort(np.asarray(times, dtype=np.float64)))
    d = d[d > 0]
    if d.size < 50:
        return {"tau_frac": None, "rel_err": rel_err, "n_isi": int(d.size)}
    floor = float(np.percentile(d, pct))
    m = float(d.mean())
    return {"tau_frac": floor / m if m > 0 else None, "rel_err": rel_err,
            "floor_abs": floor, "mean_isi": m, "n_isi": int(d.size)}


def apparatus_bracket(positions: Sequence[float],
                      tau_tight: float, tau_wide: float,
                      rel_err_tight: float = 0.2, rel_err_wide: float = 0.5,
                      null_kind: str = "poisson", n_seeds: int = 24,
                      base_seed: int = 0) -> Dict[str, dict]:
    """Bracket the apparatus between a TIGHT null (hardware / sorter refractory —
    minimal, known apparatus) and a WIDE null (empirical ISI-floor — maximal
    apparatus, attributing ALL short-ISI censoring to the instrument).

    The two are a BRACKET, not a redundancy. The short-ISI hole in tetrode data
    MIXES genuine biological refractoriness (substrate — keep) with pipeline
    censoring (sorter refractory + DAQ dead time — apparatus — subtract). The
    empirical floor captures whichever binds, so it OVER-absorbs when biology
    dominates. That is the right conservative bar for PROMOTION, but it corrupts
    ATTRIBUTION if stamped APPARATUS_EXPLAINS — so we record the ZONE:

      SUBSTRATE_ROBUST  — survives (departs from) even the WIDE null → beyond
                          maximal plausible apparatus → promotable substrate.
      INDETERMINATE     — survives the TIGHT null but not the WIDE → attribution
                          genuinely ambiguous between biological refractoriness
                          and pipeline censoring. NOT promoted, NOT stamped apparatus.
      APPARATUS_EXPLAINS— explained by even the TIGHT null → instrument/efficiency.
      NULL              — consistent with the bare null to begin with.
    """
    tight = apparatus_subtracted_comparison(
        positions, tau_tight, rel_err_tight, null_kind, n_seeds, base_seed)
    wide = apparatus_subtracted_comparison(
        positions, tau_wide, rel_err_wide, null_kind, n_seeds, base_seed + 20_000)
    out: Dict[str, dict] = {}
    for a in tight:
        if a not in wide:
            continue
        tv, wv = tight[a]["verdict"], wide[a]["verdict"]
        if wv == "RESIDUAL_STRUCTURE":
            zone = "SUBSTRATE_ROBUST"
        elif tv == "RESIDUAL_STRUCTURE":
            zone = "INDETERMINATE"          # survives tight, absorbed by wide
        elif tv == "NULL" and wv == "NULL":
            zone = "NULL"
        else:
            zone = "APPARATUS_EXPLAINS"
        out[a] = dict(zone=zone, promotable=(zone == "SUBSTRATE_ROBUST"),
                      z_vs_tight=tight[a]["z_vs_injected"],
                      z_vs_wide=wide[a]["z_vs_injected"],
                      tight=tight[a], wide=wide[a])
    return out


# ════════════════════════════════════════════════════════════════════════════
# 4. THINNING SWEEP  (finite-efficiency probe)
# ════════════════════════════════════════════════════════════════════════════

def thin_sweep(positions: Sequence[float],
               fracs: Sequence[float] = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5),
               n_seeds: int = 12, base_seed: int = 0,
               washout_gap_threshold: float = 0.5) -> Dict[str, dict]:
    """Randomly delete a range of point fractions; track how each axis moves.

    A feature that moves substantially toward the Poisson anchor under MILD
    thinning (≤0.3 deleted) is flagged EFFICIENCY_DRIVEN — it is at least partly
    an artifact of detection completeness, not a robust substrate feature.

    Returns per-axis: the (frac → mean±sd) trajectory, the slope d(axis)/d(frac),
    the fraction of the gap-to-Poisson closed by frac=0.3, and a washout flag.
    """
    t = np.asarray(positions, dtype=np.float64)
    traj: Dict[str, Dict[float, dict]] = {a: {} for a in AXES}
    for f in fracs:
        vals: Dict[str, list] = {a: [] for a in AXES}
        for k in range(n_seeds):
            rng = np.random.default_rng(base_seed + int(f * 1000) + k)
            pos = t if f == 0.0 else random_thin(t, 1.0 - f, rng)
            for a, v in axis_values(pos).items():
                vals[a].append(v)
        for a in AXES:
            if vals[a]:
                traj[a][f] = {"mean": float(np.mean(vals[a])),
                              "sd": float(np.std(vals[a]))}

    out: Dict[str, dict] = {}
    anchors = poisson_anchors()
    fr = np.asarray([f for f in fracs], dtype=float)
    for a in AXES:
        pts = traj[a]
        if 0.0 not in pts or len(pts) < 3:
            continue
        xs = np.asarray([f for f in fr if f in pts])
        ys = np.asarray([pts[f]["mean"] for f in xs])
        slope = float(np.polyfit(xs, ys, 1)[0])
        a0 = pts[0.0]["mean"]
        anchor = anchors.get(a)
        # Noise scale = typical seed-to-seed sd at the THINNED levels (frac=0 is
        # deterministic → sd=0 there, useless as a noise estimate).
        thinned_sd = [pts[f]["sd"] for f in xs if f > 0.0]
        noise = float(np.median(thinned_sd)) if thinned_sd else 0.0
        noise = max(noise, 1e-3)
        # A feature can only WASH OUT toward Poisson if it was distinguishable
        # from Poisson to begin with AND actually moved by more than noise.
        # A Poisson input sits on its own anchor within noise → never flags.
        near = min((f for f in pts if f >= 0.3), default=None)
        gap_closed = None
        distinguishable = anchor is not None and abs(a0 - anchor) > 3.0 * noise
        if distinguishable and near is not None:
            moved = a0 - pts[near]["mean"]
            gap_closed = float(moved / (a0 - anchor))
            if abs(moved) < 2.0 * noise:        # the move itself is noise-level
                gap_closed = 0.0
        washed = bool(gap_closed is not None and gap_closed > washout_gap_threshold)
        out[a] = dict(trajectory={float(f): pts[f] for f in xs},
                      slope_per_frac=slope, gap_to_poisson_closed_by_0p3=gap_closed,
                      flag="EFFICIENCY_DRIVEN" if washed else "THINNING_ROBUST")
    return out


# ════════════════════════════════════════════════════════════════════════════
# 5. METHOD-PERTURBATION DISCRIMINANT  (covariant vs invariant)
# ════════════════════════════════════════════════════════════════════════════

def _default_perturbations(positions) -> Dict[str, Callable]:
    """A standard perturbation grid: identity, dead-time on at a plausible tau,
    a heavier dead time, mild + moderate thinning, and a coarse time-bin
    (timestamp quantization). Each maps positions -> perturbed positions."""
    m = mean_isi(positions)
    return {
        "identity":      lambda p, rng: np.asarray(p, float),
        "deadtime_0.15": lambda p, rng: apply_deadtime(p, 0.15 * m),
        "deadtime_0.30": lambda p, rng: apply_deadtime(p, 0.30 * m),
        "thin_0.10":     lambda p, rng: random_thin(p, 0.90, rng),
        "thin_0.25":     lambda p, rng: random_thin(p, 0.75, rng),
        "binned_0.10":   lambda p, rng: np.unique(np.round(np.asarray(p, float)
                                                           / (0.10 * m)) * (0.10 * m)),
    }


def method_perturbation(positions: Sequence[float],
                        perturbations: Optional[Dict[str, Callable]] = None,
                        n_seeds: int = 8, base_seed: int = 0,
                        cv_invariant_threshold: float = 0.10,
                        rail_margin: float = RAIL_MARGIN) -> Dict[str, dict]:
    """Vary collection settings (dead-time model, threshold/efficiency proxy via
    thinning, time-bin) and report which spacing features are METHOD-COVARIANT
    vs METHOD-INVARIANT across the grid.

    Per axis: the value under each perturbation, the coefficient of variation of
    the axis across the grid, and a verdict. ONLY METHOD_INVARIANT axes are
    promoted to substrate candidates — covariant axes are apparatus-contaminated.
    """
    perturbations = perturbations or _default_perturbations(positions)
    per_axis_vals: Dict[str, Dict[str, float]] = {a: {} for a in AXES}
    for name, op in perturbations.items():
        seeds = []
        for k in range(n_seeds):
            rng = np.random.default_rng(base_seed + k)
            pos = op(positions, rng)
            seeds.append(axis_values(pos))
        for a in AXES:
            vv = [s[a] for s in seeds if a in s]
            if vv:
                per_axis_vals[a][name] = float(np.mean(vv))

    out: Dict[str, dict] = {}
    for a in AXES:
        vals = per_axis_vals[a]
        if len(vals) < 2:
            continue
        arr = np.asarray(list(vals.values()), dtype=float)
        spread = float(np.std(arr))           # ABSOLUTE movement across methods
        scale = float(np.mean(np.abs(arr))) + 1e-9
        cv = spread / scale                   # relative movement (away from rails)
        v = float(np.mean(arr))
        # Headroom to the nearest finite boundary, in axis units.
        lo, hi = AXIS_BOUNDS.get(a, (None, None))
        margins = [abs(v - b) for b in (lo, hi) if b is not None]
        headroom = min(margins) if margins else float("inf")
        near_rail = headroom < rail_margin
        if near_rail:
            # Near a rail the relative cv is unreliable (tiny denominator). Use
            # ABSOLUTE movement: if it swings off the rail it is demonstrably
            # method-sensitive (covariant); if it stays pinned it is indeterminate.
            if spread >= rail_margin:
                verdict, promotable = "METHOD_COVARIANT", False
            else:
                verdict, promotable = "METHOD_SATURATED", False
        elif cv <= cv_invariant_threshold:
            verdict, promotable = "METHOD_INVARIANT", True
        else:
            verdict, promotable = "METHOD_COVARIANT", False
        out[a] = dict(per_perturbation=vals, cv_across_methods=cv,
                      abs_spread=spread, headroom=float(headroom),
                      verdict=verdict, promotable=promotable)
    return out


# ════════════════════════════════════════════════════════════════════════════
# 6. LENSING LEDGER  (the durable output)
# ════════════════════════════════════════════════════════════════════════════

@dataclass
class Provenance:
    """Collection metadata carried per dataset/result. None = not estimated/known
    (never stubbed with a sentinel number — see axes.py N/A convention)."""
    substrate: str
    dataset_id: str
    n_events: int
    sampling_rate_hz: Optional[float] = None
    dead_time: Optional[float] = None        # in the position's time units
    dead_time_rel_err: Optional[float] = None  # relative uncertainty on dead_time
    refractory: Optional[float] = None
    bin_width: Optional[float] = None
    obs_window: Optional[float] = None
    efficiency_estimate: Optional[float] = None
    sort_label: Optional[str] = None
    threshold: Optional[float] = None
    notes: str = ""


@dataclass
class LensingRecord:
    """One result + the apparatus it survived. The LEDGER, not the class label,
    is the durable artifact."""
    provenance: Provenance
    axes_raw: Dict[str, float]
    apparatus_subtracted: Dict[str, dict] = field(default_factory=dict)
    thinning: Dict[str, dict] = field(default_factory=dict)
    method_perturbation: Dict[str, dict] = field(default_factory=dict)
    promoted_axes: List[str] = field(default_factory=list)
    caveats: List[str] = field(default_factory=list)
    bound: str = ("method-invariance = robust to the manipulations run, "
                  "NOT the territory")

    def to_json(self) -> dict:
        d = asdict(self)
        return d


def poisson_thinning_ambiguity(axes_raw: Dict[str, float],
                               efficiency_estimate: Optional[float],
                               eff_floor: float = 0.7,
                               tol: float = 0.08) -> Optional[str]:
    """Finding-1 corollary: if sub-Poisson is the thinning-fragile endpoint, then
    an apparent-Poisson read under LOW efficiency could be a THINNED sub-Poisson
    substrate. So the caveat attaches to the Poisson null too: when efficiency is
    low you can neither claim sub-Poisson NOR cleanly trust Poisson. Flags a
    Poisson-consistent read (CV/CV2 near the Poisson anchor) at low efficiency."""
    if efficiency_estimate is None or efficiency_estimate >= eff_floor:
        return None
    anch = poisson_anchors()
    near = []
    for a in ("I.10_cv", "I.12_cv2"):
        if axes_raw.get(a) is not None and a in anch:
            near.append(abs(axes_raw[a] - anch[a]) < tol)
    if near and all(near):
        return ("POISSON_CONSISTENT_WITH_THINNED_SUB_POISSON: efficiency "
                f"{efficiency_estimate:.2f} < {eff_floor}; an apparent-Poisson "
                "read cannot be distinguished from a thinned sub-Poisson substrate")
    return None


def build_lensing_record(positions, provenance: Provenance,
                         tau_frac_for_subtraction: float = 0.30,
                         **kw) -> LensingRecord:
    """Run the full apparatus-subtraction battery and assemble the ledger record.
    promoted_axes = those the method-perturbation discriminant calls invariant.
    Dead-time uncertainty (provenance.dead_time_rel_err) widens the injected null."""
    axes_raw = axis_values(positions)
    rel_err = provenance.dead_time_rel_err or 0.0
    sub = apparatus_subtracted_comparison(positions, tau_frac_for_subtraction,
                                          tau_frac_rel_err=rel_err)
    thin = thin_sweep(positions)
    meth = method_perturbation(positions)
    promoted = [a for a, r in meth.items() if r["promotable"]]
    caveats = []
    amb = poisson_thinning_ambiguity(axes_raw, provenance.efficiency_estimate)
    if amb:
        caveats.append(amb)
    return LensingRecord(provenance=provenance, axes_raw=axes_raw,
                         apparatus_subtracted=sub, thinning=thin,
                         method_perturbation=meth, promoted_axes=promoted,
                         caveats=caveats)


def write_ledger(record: LensingRecord, path: str) -> None:
    """Append one ledger record as a JSONL line (mirrors coordinates/*.jsonl)."""
    with open(path, "a") as f:
        f.write(json.dumps(record.to_json()) + "\n")


# ════════════════════════════════════════════════════════════════════════════
# CLOSED-LOOP VALIDATION  (no new data; runs on synthetic calibrators)
# ════════════════════════════════════════════════════════════════════════════

def _synthesise_deadtime_signal(rate_per_sec=100_000.0, duration_sec=1.0,
                                 deadtime_us=2.6, seed=0) -> np.ndarray:
    """Local copy of run_phase21_calibrators.synthesise_deadtime_signal (the
    known-answer GRB apparatus artifact) — kept local so this module stays
    self-contained / headless. Returns event times in SECONDS."""
    rng = np.random.default_rng(seed)
    n_expected = int(rate_per_sec * duration_sec * 1.5)
    raw = np.cumsum(rng.exponential(1.0 / rate_per_sec, size=n_expected))
    raw = raw[raw < duration_sec]
    return apply_deadtime(raw, deadtime_us / 1e6)


def validate(verbose: bool = True) -> dict:
    """Closed loop on synthetic calibrators (no new data). Asserts:
      (A) Poisson is thinning-INVARIANT (no efficiency artifact).
      (B) Dead time on Poisson FAKES repulsion and the injected null ABSORBS it
          → APPARATUS_EXPLAINS / NULL, not RESIDUAL_STRUCTURE.
      (C) Phase-21 GRB deadtime synthetic → NO promotable substrate candidate.
      (D) positive control — the regular endpoint washes out under mild thinning
          (the sweep actually FIRES, so A is not vacuous).
      (E) crux — genuine GUE vs a realistic-dead-time-injected null reads
          RESIDUAL_STRUCTURE (same observable as B, opposite origin, separated).
      (F) dead-time estimation uncertainty widens the injected null, artifact
          still absorbed.
      (G) low-efficiency Poisson read flags POISSON_CONSISTENT_WITH_THINNED_SUB_POISSON.
      (H) soft saturation — a near-rail (not exactly railed) axis reads SATURATED.
    """
    report = {}

    # (A) Poisson under thinning -------------------------------------------------
    rng = np.random.default_rng(1)
    pois = poisson_positions(3000, rng)
    A = thin_sweep(pois)
    a_ok = all(r["flag"] == "THINNING_ROBUST" for r in A.values())
    report["A_poisson_thinning_invariant"] = {"pass": bool(a_ok),
        "flags": {a: r["flag"] for a, r in A.items()}}

    # (B) Dead time fakes repulsion, injected null absorbs it ---------------------
    rng = np.random.default_rng(2)
    pois2 = poisson_positions(4000, rng)
    tau = 0.35 * mean_isi(pois2)
    dt_pois = apply_deadtime(pois2, tau)
    raw_ax = axis_values(pois2)
    dt_ax = axis_values(dt_pois)
    faked_repulsion = (dt_ax["I.11_mass03"] < raw_ax["I.11_mass03"]
                       and dt_ax["I.5_ks_gue"] < raw_ax["I.5_ks_gue"])
    sub = apparatus_subtracted_comparison(dt_pois, tau_frac=0.35, n_seeds=24)
    no_false_substrate = all(
        sub[a]["verdict"] in ("APPARATUS_EXPLAINS", "NULL") for a in sub)
    report["B_deadtime_fakes_repulsion_and_is_subtracted"] = {
        "pass": bool(faked_repulsion and no_false_substrate),
        "faked_repulsion": bool(faked_repulsion),
        "raw_mass03": raw_ax["I.11_mass03"], "deadtime_mass03": dt_ax["I.11_mass03"],
        "raw_ks_gue": raw_ax["I.5_ks_gue"], "deadtime_ks_gue": dt_ax["I.5_ks_gue"],
        "subtraction_verdicts": {a: sub[a]["verdict"] for a in sub}}

    # (C) GRB Phase-21 deadtime synthetic → method-covariant, not promoted --------
    grb = _synthesise_deadtime_signal(rate_per_sec=100_000.0, deadtime_us=6.0, seed=0)
    meth = method_perturbation(grb, n_seeds=6)
    # The dead-time repulsion signature (mass03→0 hole, ks_gue↓, brody→1 rail)
    # must yield NO promotable substrate candidate — each repulsion axis reads
    # COVARIANT (moves with the apparatus knob) or SATURATED (railed, indeterminate),
    # never INVARIANT.
    repulsion = [a for a in ("I.11_mass03", "I.5_ks_gue", "I.8_brody_q") if a in meth]
    none_invariant = all(meth[a]["verdict"] != "METHOD_INVARIANT" for a in repulsion)
    not_promoted = not any(meth[a]["promotable"] for a in repulsion)
    report["C_grb_deadtime_not_promoted"] = {
        "pass": bool(repulsion and none_invariant and not_promoted),
        "n_events": int(grb.size),
        "verdicts": {a: meth[a]["verdict"] for a in meth},
        "promoted": [a for a in meth if meth[a]["promotable"]],
        "cv_across_methods": {a: round(meth[a]["cv_across_methods"], 4) for a in meth}}

    # (D) POSITIVE CONTROL: the sweep must actually FIRE. The REGULAR endpoint
    #     is maximally thinning-fragile — one missed event in a near-periodic
    #     train makes a doubled gap, so its low CV washes out toward Poisson
    #     under mild thinning. CV MUST flag EFFICIENCY_DRIVEN. Guards against (A)
    #     passing vacuously because the detector never triggers.
    #     NOTE (measured here): clustering (mass03) and GUE-repulsion are mild-
    #     thinning-ROBUST (<15% / ~42% of gap closed at 30% deletion); only
    #     regularity is fragile. So moderate detection inefficiency does not
    #     easily fake/erase the clustered or repulsive endpoints — reassuring for
    #     substrate claims that rest on those, a live caveat for sub-Poisson ones.
    rng = np.random.default_rng(11)
    n_reg = 3000
    regular = np.sort(np.arange(n_reg) + 0.05 * rng.standard_normal(n_reg))
    D = thin_sweep(regular)
    fired = D.get("I.10_cv", {}).get("flag") == "EFFICIENCY_DRIVEN"
    report["D_regular_washes_out_positive_control"] = {
        "pass": bool(fired),
        "cv_at_0": round(D.get("I.10_cv", {}).get("trajectory", {})
                         .get(0.0, {}).get("mean", float("nan")), 4),
        "flags": {a: D[a]["flag"] for a in D},
        "gap_closed_by_0p3": {a: (round(D[a]["gap_to_poisson_closed_by_0p3"], 3)
                                  if D[a]["gap_to_poisson_closed_by_0p3"] is not None
                                  else None) for a in D}}

    # (E) THE CRUX: same observable ("looks repulsive"), two origins. Genuine GUE
    #     substrate, compared against a null with the data's REALISTIC (small)
    #     dead time injected, must read RESIDUAL_STRUCTURE on the repulsion axes —
    #     i.e. NOT explained away by a plausible apparatus. This is the complement
    #     of (B): dead-time-Poisson → APPARATUS_EXPLAINS, real GUE → RESIDUAL.
    #     (A large injected dead time would over-subtract and wrongly "explain"
    #     real structure — which is exactly why the ledger carries the ESTIMATED
    #     dead time as provenance rather than a free knob.)
    rng = np.random.default_rng(5)
    gue2 = gue_positions(3000, rng)
    subE = apparatus_subtracted_comparison(gue2, tau_frac=0.05, n_seeds=24,
                                           base_seed=500)
    rep_axes = [a for a in ("I.5_ks_gue", "I.11_mass03") if a in subE]
    residual = all(subE[a]["verdict"] == "RESIDUAL_STRUCTURE" for a in rep_axes) \
        if rep_axes else False
    report["E_genuine_gue_survives_apparatus_subtraction"] = {
        "pass": bool(residual),
        "subtraction_verdicts": {a: subE[a]["verdict"] for a in subE},
        "z_vs_injected": {a: round(subE[a]["z_vs_injected"], 1) for a in rep_axes}}

    # (F) DEAD-TIME UNCERTAINTY widens the injected null. On real data τ is
    #     estimated, not known — propagating its error must broaden the injected-
    #     null band, AND the dead-time artifact must STILL be absorbed (never
    #     falsely promoted to RESIDUAL) under that uncertainty.
    rng = np.random.default_rng(4)
    pois3 = poisson_positions(4000, rng)
    dt_art = apply_deadtime(pois3, 0.35 * mean_isi(pois3))
    sub0 = apparatus_subtracted_comparison(dt_art, tau_frac=0.35,
                                           tau_frac_rel_err=0.0, n_seeds=24)
    subU = apparatus_subtracted_comparison(dt_art, tau_frac=0.35,
                                           tau_frac_rel_err=0.4, n_seeds=24)
    band0 = float(np.mean([sub0[a]["injected_null"]["sd"] for a in sub0]))
    bandU = float(np.mean([subU[a]["injected_null"]["sd"] for a in subU]))
    absorbed = all(subU[a]["verdict"] in ("APPARATUS_EXPLAINS", "NULL")
                   for a in subU)
    report["F_deadtime_uncertainty_widens_null"] = {
        "pass": bool(bandU > band0 and absorbed),
        "injected_band_point_estimate": round(band0, 4),
        "injected_band_with_uncertainty": round(bandU, 4),
        "artifact_still_absorbed": bool(absorbed)}

    # (G) LOW-EFFICIENCY POISSON is consistent with thinned sub-Poisson (Finding-1
    #     cuts both ways). The ledger must flag an apparent-Poisson read at low
    #     efficiency rather than trusting the null.
    rng = np.random.default_rng(9)
    pois4 = poisson_positions(1500, rng)
    prov = Provenance(substrate="test", dataset_id="low_eff_poisson",
                      n_events=1500, efficiency_estimate=0.5)
    rec = build_lensing_record(pois4, prov)
    caveat_fired = any("THINNED_SUB_POISSON" in c for c in rec.caveats)
    report["G_low_efficiency_poisson_caveat"] = {
        "pass": bool(caveat_fired), "caveats": rec.caveats}

    # (H) SOFT SATURATION (headroom): a strong dead time pins mass03 NEAR the
    #     floor but not exactly on it (0.012). The exact-rail guard would miss it;
    #     the headroom guard reads it METHOD_SATURATED — indeterminate, not promoted.
    rng = np.random.default_rng(2)
    pois5 = poisson_positions(5000, rng)
    dt_near = apply_deadtime(pois5, 0.5 * mean_isi(pois5))
    methH = method_perturbation(dt_near, n_seeds=6)
    rH = methH.get("I.11_mass03", {})
    mv = float(np.mean(list(rH.get("per_perturbation", {1: 0}).values())))
    report["H_soft_saturation_near_rail"] = {
        "pass": bool(rH.get("verdict") == "METHOD_SATURATED"
                     and not rH.get("promotable", True)
                     and 1e-3 < mv < RAIL_MARGIN),
        "mass03_value": round(mv, 4), "verdict": rH.get("verdict"),
        "note": "near floor but not exactly railed (>1e-3) — old exact-rail guard would miss"}

    # (I/J/K) THREE-ZONE BRACKET. Two nulls bracket the apparatus; we record the
    #     zone, not a binary. (I) a known dead-time artifact with the bracket
    #     containing the true τ → APPARATUS_EXPLAINS. (J) genuine GUE under a small
    #     realistic bracket → SUBSTRATE_ROBUST (survives even the wide null). (K) a
    #     moderate hole with a span bracket (tight under-absorbs, wide over-absorbs)
    #     → INDETERMINATE: attribution genuinely ambiguous between biological
    #     refractoriness and pipeline censoring — NOT promoted, NOT stamped apparatus.
    rng = np.random.default_rng(2)
    pA = poisson_positions(4000, rng)
    artI = apply_deadtime(pA, 0.35 * mean_isi(pA))
    bI = apparatus_bracket(artI, 0.30, 0.45, n_seeds=20)
    report["I_bracket_artifact_apparatus_explains"] = {
        "pass": bool(bI.get("I.5_ks_gue", {}).get("zone") == "APPARATUS_EXPLAINS"),
        "zones": {a: bI[a]["zone"] for a in bI}}

    rng = np.random.default_rng(5)
    gJ = gue_positions(3000, rng)
    bJ = apparatus_bracket(gJ, 0.03, 0.08, n_seeds=20)
    report["J_bracket_gue_substrate_robust"] = {
        "pass": bool(bJ.get("I.5_ks_gue", {}).get("zone") == "SUBSTRATE_ROBUST"
                     and bJ.get("I.5_ks_gue", {}).get("promotable")),
        "zones": {a: bJ[a]["zone"] for a in bJ}}

    rng = np.random.default_rng(6)
    pK = poisson_positions(4000, rng)
    modK = apply_deadtime(pK, 0.30 * mean_isi(pK))
    bK = apparatus_bracket(modK, 0.08, 0.55, n_seeds=20)
    report["K_bracket_moderate_indeterminate"] = {
        "pass": bool(bK.get("I.5_ks_gue", {}).get("zone") == "INDETERMINATE"
                     and not bK.get("I.5_ks_gue", {}).get("promotable")),
        "zones": {a: bK[a]["zone"] for a in bK}}

    # (L) CONTAMINATION (additive apparatus). A single refractory-RESPECTING train
    #     (every ISI ≥ refractory) reads CLEAN; SUPERPOSING two such trains (a sort
    #     over-merge) injects sub-refractory ISIs → MERGE_SUSPECT. This is the one
    #     apparatus effect that fakes clustering, so the bracket alone can't catch it.
    rng = np.random.default_rng(7)
    refr = 0.002
    isi1 = refr + rng.exponential(0.05, size=4000)
    train1 = np.cumsum(isi1)                              # all ISIs ≥ refractory
    isi2 = refr + rng.exponential(0.05, size=4000)
    train2 = np.cumsum(isi2) + 0.013                      # offset second unit
    merged = np.sort(np.concatenate([train1, train2]))    # over-merge
    rpv_clean = refractory_violation_rate(train1, refr)["rpv"]
    rpv_merge = refractory_violation_rate(merged, refr)["rpv"]
    report["L_contamination_merge_suspect"] = {
        "pass": bool(contamination_flag(rpv_clean) == "CLEAN"
                     and contamination_flag(rpv_merge) == "MERGE_SUSPECT"),
        "clean_rpv": round(rpv_clean, 4), "clean_flag": contamination_flag(rpv_clean),
        "merged_rpv": round(rpv_merge, 4), "merged_flag": contamination_flag(rpv_merge)}

    report["ALL_PASS"] = all(v.get("pass") for k, v in report.items()
                             if isinstance(v, dict) and "pass" in v)

    if verbose:
        print("=" * 74)
        print("instrument_confound — closed-loop validation")
        print("=" * 74)
        for k, v in report.items():
            if isinstance(v, dict) and "pass" in v:
                print(f"[{'PASS' if v['pass'] else 'FAIL'}] {k}")
                for kk, vv in v.items():
                    if kk != "pass":
                        print(f"        {kk}: {vv}")
        print("-" * 74)
        print(f"ALL_PASS = {report['ALL_PASS']}")
    return report


def grb_ledger_pass(ledger_path: Optional[str] = None,
                    detector: str = "RHESSI", deadtime_us: float = 6.0,
                    rate_per_sec: float = 100_000.0,
                    cap: int = 5000) -> LensingRecord:
    """First real-substrate lensing-ledger pass (GRB / Phase-21 deadtime — the
    known-answer apparatus artifact). Builds the full record with provenance and
    writes it to the ledger. EXPECTED: the short-range repulsion axes (ks_gue,
    mass03) are method-covariant and NOT promoted; the durable output records
    exactly which axes survived which perturbations."""
    grb = _synthesise_deadtime_signal(rate_per_sec=rate_per_sec,
                                       deadtime_us=deadtime_us, seed=0)
    if grb.size > cap:                       # JPF_CAP convention — keep it fast
        grb = grb[:: max(1, grb.size // cap)]
    prov = Provenance(
        substrate="GRB_detector_synthetic", dataset_id=f"{detector}_deadtime",
        n_events=int(grb.size), sampling_rate_hz=rate_per_sec,
        dead_time=deadtime_us / 1e6, refractory=deadtime_us / 1e6,
        obs_window=float(grb[-1] - grb[0]) if grb.size else None,
        sort_label="synthetic_no_sort",
        notes=("Phase-21 deadtime calibrator; non-paralyzable; "
               "mirrors run_phase21_calibrators.synthesise_deadtime_signal"))
    rec = build_lensing_record(grb, prov)
    if ledger_path is None:
        ledger_path = os.path.join(_HERE, "coordinates",
                                   "instrument_lensing_ledger.jsonl")
    if os.path.exists(ledger_path):     # single known-answer record — idempotent,
        os.remove(ledger_path)          # not an accumulating log (re-run safe)
    write_ledger(rec, ledger_path)
    print("=" * 74)
    print(f"GRB lensing-ledger pass → {ledger_path}")
    print("=" * 74)
    print(f"  detector={detector}  dead_time={prov.dead_time*1e6:.1f}µs  "
          f"n={prov.n_events}")
    print(f"  raw axes: " + ", ".join(f"{a}={v:.3f}"
                                       for a, v in rec.axes_raw.items()))
    print(f"  method-perturbation verdicts:")
    for a, r in rec.method_perturbation.items():
        print(f"      {a}: {r['verdict']}  (cv_across_methods={r['cv_across_methods']:.3f})")
    print(f"  PROMOTED to substrate candidates: {rec.promoted_axes or '(none)'}")
    print(f"  bound: {rec.bound}")
    return rec


if __name__ == "__main__":
    rep = validate()
    print()
    grb_ledger_pass()
