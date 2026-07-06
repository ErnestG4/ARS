"""
phase37/calibrator_family_map.py — Set 4: map the Poisson-pivot blind spot across renewal families.

Phase 36 confirmed the two-axis taxonomy on a single Gamma-renewal sweep + a serial-correlation null arm.
Set 4 asks: is the partition FAMILY-GENERAL? For each renewal family we sweep a shape knob that carries CV
across the Poisson pivot (sub-Poisson → CV=1 → super-Poisson) and read both axes:
  repulsion: rep_med (joint_q_profile quadrant) + I.5_ks_gue ; clustering: I.10_cv, I.11_mass03.
Prediction (family-general): repulsion fires only sub-Poisson, clustering only super-Poisson, BOTH blind at
the CV=1 pivot. Plus null arms (transitions that should stay invisible to both). Continuous-time, no grid
(artifact-aware). A family that breaks the partition is a FINDING (banked, not discarded).
"""
from __future__ import annotations
import os, sys, json
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import numpy as np
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "cross_substrate"))
from axes import compute_family_I  # noqa: E402
from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic  # noqa: E402

N = 4000
SEEDS = (0, 1, 2, 3, 4)
OUT = os.path.join(HERE, "set4_calibrator_family_map.jsonl")


def quad_of(iei):
    s = np.asarray(iei, float); s = np.cumsum(s)
    try:
        j = joint_q_profile(s, q_max=25, min_events_per_q=100)
        qd = joint_quadrant_diagnostic(j); w = qd[~qd['underpowered']]
        if len(w):
            return round(float(w['rep_int_q'].median()), 4), str(w['quadrant'].value_counts().idxmax())
    except Exception:
        pass
    return None, None


def gen(family, knob, rng):
    """Return a unit-mean IEI array for the given family at the given shape knob."""
    if family == "gamma":            # CV = 1/sqrt(k)
        return rng.gamma(knob, 1.0 / knob, N)
    if family == "weibull":          # shape c; mean=Γ(1+1/c); CV from Γ ratios. c>1 sub-, c<1 super-Poisson
        x = rng.weibull(knob, N); return x / x.mean()
    if family == "lognormal":        # CV = sqrt(e^{σ²}-1); σ small→sub-ish(<1 near 0), large→super
        sig = knob; x = rng.lognormal(0.0, sig, N); return x / x.mean()
    if family == "invgauss":         # CV = sqrt(1/λ) in mean-1 param; λ large→sub, small→super
        x = rng.wald(1.0, knob, N); return x / x.mean()
    if family == "hyperexp":         # mixture of two exponentials → CV>1 (super-Poisson only side)
        p = 0.5; r = knob  # rate ratio; bigger r → more dispersion
        comp = rng.random(N) < p
        x = np.where(comp, rng.exponential(1.0, N), rng.exponential(r, N))
        return x / x.mean()
    raise ValueError(family)


# knob grids chosen so CV sweeps through 1.0 where the family allows both sides
FAMILIES = {
    "gamma":     [4.0, 2.0, 1.5, 1.0, 0.75, 0.5, 0.25],          # CV 0.5 .. 2.0 (both sides)
    "weibull":   [3.0, 2.0, 1.5, 1.0, 0.8, 0.6, 0.5],            # c>1 sub .. c<1 super
    "lognormal": [0.2, 0.4, 0.6, 0.83, 1.0, 1.2, 1.5],           # σ; CV crosses 1 near σ≈0.83
    "invgauss":  [8.0, 4.0, 2.0, 1.0, 0.5, 0.3, 0.2],            # λ; large sub .. small super
    "hyperexp":  [1.0, 2.0, 4.0, 8.0, 16.0],                     # super-Poisson-only (CV≥1) — one-sided
}


def _cell(job):
    family, knob, seed = job
    rng = np.random.default_rng(13000 + seed + hash((family, knob)) % 10000)
    iei = gen(family, knob, rng)
    fI = compute_family_I(np.cumsum(iei))
    rep, quad = quad_of(iei)
    return dict(family=family, knob=knob, seed=seed,
                cv=fI["I.10_cv"], mass03=fI["I.11_mass03"],
                ks_gue=fI["I.5_ks_gue"], ks_poisson=fI["I.7_ks_poisson"],
                rep_med=rep, quad=quad)


def _null_cell(job):
    """Null arms: genuine transitions that should stay invisible to both axes."""
    kind, knob, seed = job
    rng = np.random.default_rng(23000 + seed + int(knob * 100))
    if kind == "serial_corr":   # exponential marginal held exact, AR(1) serial correlation = knob
        rho = knob; z = np.empty(N); z[0] = rng.standard_normal(); sd = np.sqrt(1 - rho ** 2)
        for t in range(1, N):
            z[t] = rho * z[t - 1] + sd * rng.standard_normal()
        from math import erf, sqrt
        u = np.clip(0.5 * (1 + np.vectorize(lambda x: erf(x / sqrt(2)))(z)), 1e-12, 1 - 1e-12)
        iei = -np.log(1 - u)
    elif kind == "slow_rate_drift":  # Poisson with a slow sinusoidal rate drift of small amplitude=knob
        t = np.linspace(0, 1, N); rate = 1.0 + knob * np.sin(2 * np.pi * 3 * t)
        iei = rng.exponential(1.0, N) / rate; iei = iei / iei.mean()
    else:
        raise ValueError(kind)
    fI = compute_family_I(np.cumsum(iei))
    rep, quad = quad_of(iei)
    return dict(family=f"NULL:{kind}", knob=knob, seed=seed,
                cv=fI["I.10_cv"], mass03=fI["I.11_mass03"],
                ks_gue=fI["I.5_ks_gue"], ks_poisson=fI["I.7_ks_poisson"], rep_med=rep, quad=quad)


def main():
    jobs = [(f, k, s) for f, ks in FAMILIES.items() for k in ks for s in SEEDS]
    null_jobs = [(kind, k, s) for kind in ("serial_corr", "slow_rate_drift")
                 for k in (0.0, 0.3, 0.6, 0.85, 0.95) for s in SEEDS]
    rows = []
    with ProcessPoolExecutor(max_workers=10) as pool:
        rows += list(pool.map(_cell, jobs))
        rows += list(pool.map(_null_cell, null_jobs))
    with open(OUT, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")

    # aggregate per (family, knob)
    import collections
    agg = collections.defaultdict(list)
    for r in rows:
        agg[(r["family"], r["knob"])].append(r)

    def m(rs, k):
        v = [x[k] for x in rs if x[k] is not None]
        return float(np.mean(v)) if v else None

    print(f"{'family':16s} {'knob':>6} {'CV':>6} {'mass03':>7} {'ksGUE':>6} {'rep_med':>8} {'quad':>12}")
    for (fam, knob) in sorted(agg):
        rs = agg[(fam, knob)]
        quads = [x["quad"] for x in rs if x["quad"]]
        cv = m(rs, "cv"); mass = m(rs, "mass03")
        print(f"{fam:16s} {knob:6.2f} {cv:6.3f} {mass:7.4f} {m(rs,'ks_gue'):6.3f} "
              f"{str(round(m(rs,'rep_med'),3)) if m(rs,'rep_med') is not None else 'None':>8} "
              f"{(max(set(quads),key=quads.count) if quads else 'None'):>12}")

    # adjudication: across families, does the partition hold? (sub-Poisson→repulsion, super→clustering, pivot blind)
    print("\n=== PARTITION CHECK (per family, where it spans the pivot) ===")
    for fam in FAMILIES:
        pts = [(m(agg[(fam, k)], "cv"), m(agg[(fam, k)], "rep_med"), m(agg[(fam, k)], "mass03"))
               for k in FAMILIES[fam]]
        pts = [p for p in pts if p[0] is not None]
        sub = [p for p in pts if p[0] < 0.9]; sup = [p for p in pts if p[0] > 1.1]
        rep_sub = np.mean([p[1] for p in sub if p[1] is not None]) if sub else None
        rep_sup = np.mean([p[1] for p in sup if p[1] is not None]) if sup else None
        mass_sup = np.mean([p[2] for p in sup]) if sup else None
        print(f"  {fam:12s}: sub-Poisson rep_med={rep_sub} ; super-Poisson rep_med={rep_sup} mass={mass_sup}"
              f"  -> {'PARTITION HOLDS' if (rep_sub is None or rep_sup is None or (rep_sub>rep_sup)) else 'CHECK: super-side repulsion not lower'}")
    print(f"\nWrote {OUT} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
