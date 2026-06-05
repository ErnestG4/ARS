"""
cross_substrate/longrange_discriminator.py — certify the universality CLASS, not
just the marginal spacing.

The Phase-18 STOP CONDITION exposed it: phase-randomized and cumulant-matched
surrogates PRESERVE the marginal spacing distribution and DESTROY everything above
it, yet still reproduce the NNS (rep/ks_gue) verdict on zeta/lmfdb/dirichlet. So an
NNS-only verdict certifies the MARGINAL, not the long-range correlation structure
that DEFINES the universality class. The earned claim on NNS alone is "marginal
spacing matches GUE", not "GUE class".

The clean proof is a decoy: a RENEWAL process with i.i.d. spacings drawn from the
Wigner (GUE NNS) distribution has the GUE NNS and ZERO long-range rigidity (number
variance grows ~linearly like Poisson, not ~log like GUE). NNS cannot tell it from
real GUE; a long-range statistic (Σ²(L) / Δ₃(L)) separates them instantly.

This module supplies (1) the Wigner-renewal decoy, (2) a long-range verdict that
compares Σ²(L)/Δ₃(L) against a real-GUE ensemble and a renewal ensemble at matched
n and L → RIGID_GUE / MARGINAL_ONLY / INTERMEDIATE, and (3) a closed-loop proof:
real GUE → RIGID_GUE while the decoy and a cumulant-matched surrogate of real GUE
(same NNS) → MARGINAL_ONLY. On NNS alone they are indistinguishable; the long-range
statistic is what carries the class claim.

BOUND: "GUE class" requires a long-range statistic the marginal-preserving
surrogates cannot fake. NNS alone earns only "marginal matches GUE".
[[bulk_vs_global_moment_readout]] (RW σ²(K) complement), [[support_set_respecting_nulls]].
"""
from __future__ import annotations

import os
import sys
from typing import Dict, Optional, Sequence

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from axes import II1_sigma2_at_L, II2_delta3_at_L, matched_L
from universality import nns_cdf_gue
from instrument_confound import gue_positions, poisson_positions, axis_values

_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
from surrogates import cumulant_matched_events   # marginal-preserving surrogate


# ── Wigner-renewal decoy: GUE NNS, zero long-range rigidity ──────────────────
_S_GRID = np.linspace(0.0, 6.0, 8000)
_C_GRID = np.asarray(nns_cdf_gue(_S_GRID), dtype=np.float64)


def wigner_renewal(n: int, rng: np.random.Generator) -> np.ndarray:
    """Renewal process whose i.i.d. spacings are drawn from the GUE Wigner surmise
    (inverse-CDF sampling). Same marginal NNS as real GUE, but — being a renewal
    process — its long-range correlations are absent: Σ²(L) grows ~linearly, not
    ~log L. The decoy that NNS cannot distinguish from real GUE."""
    u = rng.random(n)
    spac = np.interp(u, _C_GRID, _S_GRID)
    spac = spac[spac > 0]
    return np.cumsum(spac)


# ── unfolding: the long-range arm's OWN lens (the analog of dead time for NNS) ──
# Σ²(L)/Δ₃(L) require a FLAT mean density; NNS does not. So adding the long-range
# arm stacked a new apparatus stage — unfolding — that can MANUFACTURE rigidity
# (over-unfold → absorbs real fluctuation → spuriously rigid) or ERASE it
# (under-unfold → residual density trend → σ²≫Poisson, spuriously floppy; that is
# exactly what zeta_high_height's σ²=71>Poisson was). The lens degree must be
# carried in the ledger and SWEPT for sensitivity, same discipline as dead time.
def unfold_empirical(positions: Sequence[float], deg: int = 6) -> np.ndarray:
    """Flatten the smooth density: fit a degree-`deg` polynomial to the staircase
    (sorted positions → cumulative rank) and map events through it → unit-mean-
    density, smooth-trend removed. `deg` is a LENS PARAMETER — too low leaves a
    trend (spurious floppiness), too high absorbs real fluctuation (spurious
    rigidity). Applied UNIFORMLY to data and references so the comparison is fair."""
    e = np.sort(np.asarray(positions, dtype=np.float64))
    if e.size < deg + 2:
        return e - e[0] if e.size else e
    y = np.arange(1, e.size + 1, dtype=np.float64)
    x = (e - e[0]) / (e[-1] - e[0] + 1e-12)        # condition to [0,1]
    return np.polyval(np.polyfit(x, y, deg), x)


def rate_aware_unfold(positions: Sequence[float], bw_mult: float = 20.0,
                      bins_per_isi: int = 4) -> np.ndarray:
    """LOCAL-density (rate-aware) unfold via the time-rescaling theorem: estimate
    λ̂(t) by Gaussian-smoothing the binned train (bandwidth bw = bw_mult × mean
    spacing) and unfold by the integrated rate Λ̂(t).

    ⚠ VALIDATION-FAILED FOR Σ²(L) — DO NOT DEPLOY (kept as evidence + swept lens).
    Estimating the rate from the SAME train and unfolding at scales ≤ L removes the
    very correlations Σ²(L) measures: drift and correlation ALIAS at the measurement
    scale. Empirically (see validate_rate_unfold / rate_sensitivity) the decoy reads
    false-RIGID and the GUE↔Poisson separation collapses (60×→<4×) at every usable
    bandwidth; only bw→∞ (which does nothing, ≈ the global poly) is correct. So
    self-estimated rate cannot harden the neural bulk — that needs an EXTERNAL rate
    (behavioral covariates / trial PSTH / simultaneous population), i.e. new
    information beyond the spike train. Use unfold_deg (smooth-poly) for deployment."""
    e = np.sort(np.asarray(positions, dtype=np.float64))
    n = e.size
    span = float(e[-1] - e[0]) if n > 1 else 0.0
    if n < 20 or span <= 0:
        return e - (e[0] if n else 0.0)
    m = span / n                                   # mean spacing (time units)
    dt = m / bins_per_isi
    nb = int(np.clip(span / dt, 32, 400_000))
    edges = np.linspace(e[0], e[-1], nb + 1)
    counts = np.histogram(e, bins=edges)[0].astype(np.float64)
    sig = max(bw_mult * m / dt, 0.5)               # kernel sd in bins
    half = int(min(4 * sig, max(nb // 2 - 1, 1)))  # keep kernel ≤ bins (convolve 'same')
    xk = np.arange(-half, half + 1)
    k = np.exp(-0.5 * (xk / sig) ** 2)
    k /= k.sum()
    rate = np.convolve(counts, k, mode="same")
    cum = np.concatenate([[0.0], np.cumsum(rate)])  # expected count at each edge
    return np.interp(e, edges, cum)


def _apply_unfold(e, unfold_deg, unfold_bw):
    if unfold_bw is not None:
        return np.sort(rate_aware_unfold(e, unfold_bw))
    if unfold_deg is not None:
        return np.sort(unfold_empirical(e, unfold_deg))
    return e


# ── long-range statistics ─────────────────────────────────────────────────────
def longrange_stats(positions: Sequence[float], L: Optional[float] = None,
                    unfold_deg: Optional[int] = None,
                    unfold_bw: Optional[float] = None) -> dict:
    e = _apply_unfold(np.sort(np.asarray(positions, dtype=np.float64)),
                      unfold_deg, unfold_bw)
    if L is None:
        L = matched_L(e.size)
    return {"L": float(L), "sigma2": II1_sigma2_at_L(e, L),
            "delta3": II2_delta3_at_L(e, L)}


def _ensemble(sampler, n: int, L: float, n_seeds: int, base_seed: int,
              unfold_deg: Optional[int] = None, unfold_bw: Optional[float] = None) -> dict:
    s2, d3 = [], []
    for k in range(n_seeds):
        rng = np.random.default_rng(base_seed + k)
        st = longrange_stats(sampler(n, rng), L, unfold_deg=unfold_deg,
                             unfold_bw=unfold_bw)
        if st["sigma2"] is not None:
            s2.append(st["sigma2"])
        if st["delta3"] is not None:
            d3.append(st["delta3"])
    out = {}
    for nm, v in (("sigma2", s2), ("delta3", d3)):
        if v:
            out[nm] = {"mean": float(np.mean(v)), "sd": float(np.std(v) + 1e-12)}
    return out


_ENS_CACHE: Dict[tuple, tuple] = {}


def _reference_ensembles(n_e: int, L: float, n_seeds: int,
                         unfold_deg: Optional[int] = None,
                         unfold_bw: Optional[float] = None) -> tuple:
    """The TWO POLES as reference ensembles — real-GUE (rigid, Σ²~log L) and Poisson
    (independent, Σ²≈L) — at (n_e, L, unfold_deg), memoized with FIXED seeds; the
    same unfolding lens is applied to references and data. Certifies BOTH poles:
    rigidity for the GUE pole AND Σ²(L)≈L for the Poisson pole, because exponential
    NNS is necessary-NOT-sufficient for Poisson (a correlated process can wear an
    exponential marginal). The O(n³) GUE eigensolve is paid ONCE per key."""
    key = (int(n_e), round(float(L), 4), int(n_seeds), unfold_deg, unfold_bw)
    if key not in _ENS_CACHE:
        _ENS_CACHE[key] = (
            _ensemble(gue_positions, n_e, L, n_seeds, 90_000, unfold_deg, unfold_bw),
            _ensemble(poisson_positions, n_e, L, n_seeds, 92_000, unfold_deg, unfold_bw))
    return _ENS_CACHE[key]


def longrange_verdict(positions: Sequence[float], L: Optional[float] = None,
                      n_seeds: int = 16, base_seed: int = 0,
                      n_ref: int = 3000, unfold_deg: Optional[int] = 6,
                      ref_n: Optional[int] = None,
                      unfold_bw: Optional[float] = None) -> dict:
    """Place the data between the TWO POLES (real-GUE rigid, Poisson Σ²≈L) at matched
    n and L. Σ² is primary, Δ₃ a cross-check.
      RIGID_GUE     — at or below the GUE rigidity level → GUE pole earned.
      POISSON_INDEP — consistent with Poisson (Σ²≈L) → Poisson pole earned (genuinely
                      independent, not just an exponential marginal).
      SUPER_POISSON — Σ² above Poisson → clustered (or, on a putative-GUE input,
                      mis-unfolded — see σ²>Poisson guard in the audit).
      INTERMEDIATE  — between GUE and Poisson: sub-Poisson but NOT GUE-rigid (e.g. a
                      renewal process / pooled superposition / NNS-GUE-but-floppy).
      UNDERPOWERED  — too few events for Σ²/Δ₃.
    """
    e = np.sort(np.asarray(positions, dtype=np.float64))
    n = e.size
    if L is None:
        L = matched_L(n)
    obs = longrange_stats(e, L, unfold_deg=unfold_deg, unfold_bw=unfold_bw)
    if obs["sigma2"] is None:
        return {"verdict": "UNDERPOWERED", "n": int(n), "L": float(L)}
    # Σ²(L)/Δ₃(L) at fixed L are windowed statistics ~independent of total n once
    # n >> L, so the reference ensembles use a capped n_ref (the data keeps its own
    # n) — avoids an O(n³) GUE eigensolve at large n while staying matched in L.
    # Σ²(L) at fixed L is ~n-independent for n≫L, so the references may use a FIXED
    # ref_n (shared cache across cells of differing n) or a per-call cap n_ref.
    n_e = ref_n if ref_n is not None else min(n, n_ref)
    gue, pois = _reference_ensembles(n_e, L, n_seeds, unfold_deg, unfold_bw)  # same lens

    def _judge(stat):
        if stat not in gue or stat not in pois or obs[stat] is None:
            return None
        o = obs[stat]
        gm, gs = gue[stat]["mean"], gue[stat]["sd"]
        pm, ps = pois[stat]["mean"], pois[stat]["sd"]
        z_g = (o - gm) / gs                       # SIGNED (− = more rigid than GUE)
        z_p = (o - pm) / ps                       # SIGNED (− = more rigid than Poisson)
        # GUE pole uses the (clean, small-sd) GUE band; the Poisson pole uses RATIO
        # bands around its mean, NOT its sd — Poisson Σ²(L) is intrinsically noisy
        # (sd≈L/3), so an sd-band would swallow renewal-level (sub-Poisson) into
        # POISSON_INDEP. POISSON_INDEP = Σ²≈L within a factor (≥0.6·Poisson);
        # SUPER_POISSON = clustered (>1.5·Poisson); strictly between GUE and the
        # Poisson band (sub-Poisson but not rigid: renewal/pooled) → INTERMEDIATE.
        if o <= gm + 2.5 * gs:
            v = "RIGID_GUE"
        elif o > 1.5 * pm:
            v = "SUPER_POISSON"
        elif o >= 0.6 * pm:
            v = "POISSON_INDEP"
        else:
            v = "INTERMEDIATE"
        return dict(obs=float(o), gue=gue[stat], poisson=pois[stat],
                    z_vs_gue=float(z_g), z_vs_poisson=float(z_p), verdict=v)

    s2j, d3j = _judge("sigma2"), _judge("delta3")
    primary = s2j["verdict"] if s2j else (d3j["verdict"] if d3j else "UNDERPOWERED")
    return {"verdict": primary, "n": int(n), "L": float(L),
            "unfold_deg": unfold_deg, "unfold_bw": unfold_bw,
            "sigma2": s2j, "delta3": d3j}


def unfolding_sensitivity(positions: Sequence[float],
                          degs: Sequence[int] = (3, 6, 10, 15),
                          n_seeds: int = 12, L: Optional[float] = None,
                          n_ref: int = 2500, ref_n: Optional[int] = None) -> dict:
    """The unfolding method-perturbation: sweep the unfolding degree and report
    whether the long-range verdict is LENS-INVARIANT (same verdict across degrees →
    trustworthy) or LENS-COVARIANT (verdict moves with the lens → the rigidity is an
    unfolding artifact, not a substrate property). Same discipline as the apparatus
    method-perturbation. A claim is only promotable if lens-invariant."""
    per = {}
    for d in degs:
        v = longrange_verdict(positions, L=L, n_seeds=n_seeds, n_ref=n_ref,
                              unfold_deg=d, ref_n=ref_n)
        s2 = v.get("sigma2") or {}
        per[d] = {"verdict": v["verdict"], "sigma2": round(s2.get("obs", float("nan")), 3)}
    verdicts = {p["verdict"] for p in per.values()}
    stable = len(verdicts) == 1
    return {"per_degree": per, "verdicts": sorted(verdicts),
            "lens": "INVARIANT" if stable else "COVARIANT",
            "promotable": stable}


def rate_sensitivity(positions: Sequence[float],
                     bws: Sequence[float] = (10.0, 30.0, 100.0),
                     n_seeds: int = 12, L: Optional[float] = None,
                     n_ref: int = 2500, ref_n: Optional[int] = None) -> dict:
    """Rate-aware-unfold method-perturbation: sweep the kernel bandwidth bw_mult and
    report LENS-INVARIANT vs LENS-COVARIANT. Bandwidth (not poly degree) is the lens
    here — the natural knob for non-smooth rate non-stationarity."""
    per = {}
    for bw in bws:
        v = longrange_verdict(positions, L=L, n_seeds=n_seeds, n_ref=n_ref,
                              unfold_bw=bw, ref_n=ref_n)
        s2 = v.get("sigma2") or {}
        per[bw] = {"verdict": v["verdict"], "sigma2": round(s2.get("obs", float("nan")), 3)}
    verdicts = {p["verdict"] for p in per.values()}
    stable = len(verdicts) == 1
    return {"per_bw": per, "verdicts": sorted(verdicts),
            "lens": "INVARIANT" if stable else "COVARIANT", "promotable": stable}


def validate_rate_unfold(verbose: bool = True) -> dict:
    """NEGATIVE validation — documents why rate-aware self-unfold is NOT deployed.
    A correct lens must keep the renewal DECOY out of RIGID and preserve the
    GUE↔Poisson pole separation. Rate-aware self-unfold does NEITHER at any usable
    bandwidth: the decoy reads false-RIGID and the separation collapses. (drift and
    correlation alias at scale L when rate is estimated from the same train.)"""
    real = gue_positions(2500, np.random.default_rng(0))
    decoy = wigner_renewal(2500, np.random.default_rng(1))
    out = {}
    for bw in (10.0, 30.0, 100.0):
        vr = longrange_verdict(real, unfold_bw=bw, n_seeds=10, ref_n=1500)
        vd = longrange_verdict(decoy, unfold_bw=bw, n_seeds=10, ref_n=1500)
        sep = vr["sigma2"]["poisson"]["mean"] / max(vr["sigma2"]["gue"]["mean"], 1e-9)
        out[bw] = {"real": vr["verdict"], "decoy": vd["verdict"], "pole_sep": round(sep, 1)}
    decoy_false_rigid = any(o["decoy"] == "RIGID_GUE" for o in out.values())
    sep_collapsed = all(o["pole_sep"] < 10 for o in out.values())
    out["INADEQUATE"] = bool(decoy_false_rigid and sep_collapsed)
    if verbose:
        print("rate-aware self-unfold NEGATIVE validation (should be INADEQUATE=True):")
        for bw, o in out.items():
            if bw != "INADEQUATE":
                print(f"  bw={bw}: real→{o['real']}  decoy→{o['decoy']}  pole_sep={o['pole_sep']}×")
        print(f"  INADEQUATE = {out['INADEQUATE']}  (decoy false-RIGID + collapsed pole separation)")
    return out


def ks_gue(positions) -> Optional[float]:
    """The NNS marginal statistic (ks_gue) — what the decoy fools."""
    return axis_values(positions, axes=("I.5_ks_gue",)).get("I.5_ks_gue")


from axes import MIN_N_LONGRANGE   # the ≥200-event Σ²/Δ₃ floor


def enough_for_longrange(positions, L: Optional[float] = None) -> dict:
    """Pre-check before running the long-range statistic on a candidate cell.
    Below MIN_N_LONGRANGE events Σ²/Δ₃ are underpowered — on fast low-yield units
    that folds straight back into the pass-2 resolution-floor problem. Returns the
    event count, whether it clears the floor, and a coarse n/L ratio (windows per L
    available). Run this per cell and SKIP the long-range verdict where it fails,
    rather than emit a statistic the data can't support."""
    e = np.asarray(positions, dtype=np.float64)
    n = int(e.size)
    ok = n >= MIN_N_LONGRANGE
    span = float(np.ptp(e)) if n > 1 else 0.0
    L = L if L is not None else (matched_L(n) if n else 0.0)
    n_windows = (span / L) if L > 0 else 0.0
    return {"n": n, "min_required": MIN_N_LONGRANGE, "enough": bool(ok),
            "approx_windows_at_L": round(n_windows, 1), "L": float(L)}


# ── closed-loop proof ─────────────────────────────────────────────────────────
def validate(verbose: bool = True) -> dict:
    """Proof that NNS under-certifies and the long-range statistic carries the class:
      (P1) real GUE and the Wigner-renewal decoy have the SAME NNS (ks_gue).
      (P2) the long-range verdict SEPARATES them: real → RIGID_GUE, decoy → NOT rigid
           (INTERMEDIATE — renewal sits between the GUE and Poisson poles).
      (P3) a cumulant-matched surrogate of real GUE preserves NNS but collapses the
           long-range structure → NOT rigid (the marginal surrogate cannot fake it).
    """
    rep = {}
    n = 2500            # GUE eigensolve is O(n³); 2500 keeps the proof fast
    ns = 12
    rng = np.random.default_rng(0)
    real = gue_positions(n, rng)
    decoy = wigner_renewal(n, np.random.default_rng(1))

    ks_real, ks_decoy = ks_gue(real), ks_gue(decoy)
    rep["P1_same_NNS"] = {
        "pass": bool(ks_real is not None and ks_decoy is not None
                     and ks_real < 0.08 and ks_decoy < 0.08
                     and abs(ks_real - ks_decoy) < 0.05),
        "ks_gue_real": round(ks_real, 4), "ks_gue_decoy": round(ks_decoy, 4)}

    v_real = longrange_verdict(real, n_seeds=ns, base_seed=10)
    v_decoy = longrange_verdict(decoy, n_seeds=ns, base_seed=20)
    rep["P2_longrange_separates"] = {
        "pass": bool(v_real["verdict"] == "RIGID_GUE"
                     and v_decoy["verdict"] != "RIGID_GUE"),
        "real_verdict": v_real["verdict"], "decoy_verdict": v_decoy["verdict"],
        "real_sigma2": round(v_real["sigma2"]["obs"], 3),
        "decoy_sigma2": round(v_decoy["sigma2"]["obs"], 3),
        "gue_sigma2_mean": round(v_real["sigma2"]["gue"]["mean"], 3),
        "poisson_sigma2_mean": round(v_real["sigma2"]["poisson"]["mean"], 3)}

    surr = cumulant_matched_events(real, rng=np.random.default_rng(2))
    ks_surr = ks_gue(surr)
    v_surr = longrange_verdict(surr, n_seeds=ns, base_seed=30)
    rep["P3_cumulant_surrogate_collapses_longrange"] = {
        "pass": bool(ks_surr is not None and ks_surr < 0.10
                     and v_surr["verdict"] != "RIGID_GUE"),
        "ks_gue_surrogate": round(ks_surr, 4) if ks_surr else None,
        "surrogate_longrange_verdict": v_surr["verdict"],
        "note": "marginal preserved (NNS still ~GUE) but long-range structure gone"}

    rep["ALL_PASS"] = all(v["pass"] for v in rep.values()
                          if isinstance(v, dict) and "pass" in v)
    if verbose:
        print("=" * 74)
        print("longrange_discriminator — closed-loop proof (NNS under-certifies)")
        print("=" * 74)
        for k, v in rep.items():
            if isinstance(v, dict) and "pass" in v:
                print(f"[{'PASS' if v['pass'] else 'FAIL'}] {k}")
                for kk, vv in v.items():
                    if kk != "pass":
                        print(f"        {kk}: {vv}")
        print("-" * 74)
        print(f"ALL_PASS = {rep['ALL_PASS']}")
    return rep


if __name__ == "__main__":
    validate()
