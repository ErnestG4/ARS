"""
phase36/falsification_calibrator.py — Poisson-pivot taxonomy falsification calibrator.

The rigidity-vs-clustering taxonomy ([[torus_transition_rigidity_vs_clustering]]) was sharpened last
session to a PREDICTIVE claim: Poisson is the PIVOT where BOTH ARS axes go blind. The repulsion axis is
ONE-SIDED (resolves sub-Poisson/rigid, collapses >=Poisson onto BL); the clustering axis lives on the
super-Poisson side. Predictions:
  (i)  a transition that CROSSES Poisson (sub -> super) lights repulsion THEN clustering, with a blind
       pivot at CV=1;
  (ii) a transition that STAYS near Poisson throughout is invisible to BOTH axes.

This script builds two arms, each able to come back POSITIVE (Will's generalization-test guard):

ARM A (CROSSING, positive control + pivot demonstration) — single Gamma-renewal family, shape k swept so
  CV = 1/sqrt(k) passes through 1.0:
    k=4   -> CV 0.50 (sub-Poisson / repulsion side)   EXPECT: repulsion fires, clustering null
    k=1   -> CV 1.00 (Poisson pivot)                  EXPECT: BOTH null  <-- the load-bearing prediction
    k=1/4 -> CV 2.00 (super-Poisson / clustering side) EXPECT: clustering fires, repulsion null
  If the pivot (k=1) lights EITHER axis, or if the sides don't partition as predicted, the taxonomy is wrong.

ARM B (NULL calibrator / the actual falsification) — exponential marginals (Poisson, CV=1) held FIXED while
  serial correlation between successive IEIs is cranked 0 -> high. This is a genuine dynamical transition
  (long-range temporal structure changes) that stays AT the Poisson pivot in marginal spacing stats. The
  taxonomy predicts BOTH axes read null throughout. If either axis fires, the two-axis MARGINAL-spacing
  picture is incomplete (ARS would be reading correlation structure it is not supposed to see via NNS).

ARTIFACT-AWARE (lesson from RE_AUDIT_CONFOUND_FINGERPRINT.md): continuous-time event sequences, unit-mean
spacings, NO temporal grid / binning / high pooled rate -> no quantization confound. Single renewal stream
per condition (not pooled).
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import numpy as np
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic  # noqa: E402

N_EVENTS = 4000          # plenty for q_max=25, min_events_per_q=100
SEEDS = (0, 1, 2, 3, 4)


def both_axes(iei: np.ndarray) -> dict:
    """Read both ARS axes from an inter-event-interval sequence (continuous-time, unit-mean)."""
    s = np.asarray(iei, float); s = s[s > 0]; s = s / s.mean()
    cv = float(s.std()); mass = float(np.mean(s < 0.3))           # clustering axis
    rep = quad = ks_gue = ks_poi = None
    if s.size >= 400:
        pos = np.cumsum(np.concatenate([[0.0], s]))
        try:
            j = joint_q_profile(pos, q_max=25, min_events_per_q=100)
            qd = joint_quadrant_diagnostic(j); w = qd[~qd['underpowered']]
            if len(w):
                rep = round(float(w['rep_int_q'].median()), 4)
                quad = str(w['quadrant'].value_counts().idxmax())
        except Exception:
            pass
    # direct KS for cross-reference (band-invariance load-bearing stats)
    ss = np.sort(s)
    emp = np.arange(1, ss.size + 1) / ss.size
    ks_poi = float(np.max(np.abs(emp - (1 - np.exp(-ss)))))
    ks_gue = float(np.max(np.abs(emp - (1 - np.exp(-np.pi * ss ** 2 / 4)))))
    return dict(cv=round(cv, 3), mass_lt_0p3=round(mass, 4), rep_med=rep, quad=quad,
                ks_poisson=round(ks_poi, 3), ks_gue=round(ks_gue, 3))


# ---------- ARM A: Gamma-renewal CV sweep through the pivot ----------
def _gamma_cell(job):
    k, seed = job
    rng = np.random.default_rng(1000 + seed)
    iei = rng.gamma(shape=k, scale=1.0 / k, size=N_EVENTS)   # mean 1, CV = 1/sqrt(k)
    ax = both_axes(iei)
    return (k, ax)


# ---------- ARM B: exponential marginals, induced serial correlation (Poisson pivot held fixed) ----------
def _corr_cell(job):
    """
    rho controls serial correlation of successive IEIs while the MARGINAL stays exact-exponential.
    Construction: an AR(1) Gaussian latent z_t (corr rho), mapped through its own CDF to U(0,1)
    (rank-preserving), then exponential-inverse-CDF. Marginal is exactly Exp(1) for every rho;
    only the serial dependence changes. rho=0 -> i.i.d. Poisson; rho->1 -> strongly correlated IEIs
    (a real long-range-structure transition) with IDENTICAL Poisson marginal.
    """
    rho, seed = job
    rng = np.random.default_rng(2000 + seed)
    n = N_EVENTS
    z = np.empty(n)
    z[0] = rng.standard_normal()
    s = np.sqrt(1 - rho ** 2)
    for t in range(1, n):
        z[t] = rho * z[t - 1] + s * rng.standard_normal()
    # standard-normal CDF -> uniform -> exponential inverse-CDF (marginal exactly Exp(1))
    from math import erf, sqrt
    u = 0.5 * (1.0 + np.vectorize(lambda x: erf(x / sqrt(2)))(z))
    u = np.clip(u, 1e-12, 1 - 1e-12)
    iei = -np.log(1.0 - u)
    ax = both_axes(iei)
    return (rho, ax)


def _agg(results, key_name):
    by = {}
    for kv, ax in results:
        by.setdefault(kv, []).append(ax)
    rows = {}
    for kv in sorted(by, reverse=(key_name == 'k')):
        axs = by[kv]
        reps = [a['rep_med'] for a in axs if a['rep_med'] is not None]
        quads = [a['quad'] for a in axs if a['quad'] is not None]
        rows[kv] = dict(
            cv=round(float(np.mean([a['cv'] for a in axs])), 3),
            mass=round(float(np.mean([a['mass_lt_0p3'] for a in axs])), 4),
            rep=round(float(np.mean(reps)), 4) if reps else None,
            quad=max(set(quads), key=quads.count) if quads else None,
            ks_poi=round(float(np.mean([a['ks_poisson'] for a in axs])), 3),
            ks_gue=round(float(np.mean([a['ks_gue'] for a in axs])), 3),
        )
    return rows


def main():
    K_SWEEP = [4.0, 2.0, 1.5, 1.0, 0.75, 0.5, 0.25]      # CV 0.5 .. 2.0 through pivot at k=1
    RHO_SWEEP = [0.0, 0.3, 0.6, 0.85, 0.95]

    with ProcessPoolExecutor(max_workers=10) as pool:
        a = list(pool.map(_gamma_cell, [(k, s) for k in K_SWEEP for s in SEEDS]))
        b = list(pool.map(_corr_cell, [(r, s) for r in RHO_SWEEP for s in SEEDS]))

    ra = _agg(a, 'k')
    print("\n=== ARM A — Gamma-renewal CV sweep THROUGH the Poisson pivot ===")
    print(f"  {'k':>5} {'CV(1/sqrtk)':>11} | {'rep_med':>8} {'quad':>12} | {'mass<.3':>8} | {'ksPoi':>6} {'ksGUE':>6}")
    for k in K_SWEEP:
        v = ra[k]
        print(f"  {k:5.2f} {1/np.sqrt(k):11.3f} | {str(v['rep']):>8} {str(v['quad']):>12} | {v['mass']:8.4f} | {v['ks_poi']:6.3f} {v['ks_gue']:6.3f}")
    print("  EXPECT: k>1 (sub-Poisson) -> repulsion fires (TR/BR, rep high); k=1 -> BOTH null (BL, CV~1);")
    print("          k<1 (super-Poisson) -> clustering fires (mass<.3 up), repulsion stays BL.")

    rb = _agg(b, 'rho')
    print("\n=== ARM B — NULL calibrator: exponential marginals, serial-correlation transition ===")
    print(f"  {'rho':>5} | {'rep_med':>8} {'quad':>12} | {'CV':>6} {'mass<.3':>8} | {'ksPoi':>6} {'ksGUE':>6}")
    for r in RHO_SWEEP:
        v = rb[r]
        print(f"  {r:5.2f} | {str(v['rep']):>8} {str(v['quad']):>12} | {v['cv']:6.3f} {v['mass']:8.4f} | {v['ks_poi']:6.3f} {v['ks_gue']:6.3f}")
    print("  EXPECT (taxonomy holds): BOTH axes null (BL, CV~1, low mass) across ALL rho — a genuine")
    print("  transition (serial dependence) invisible to both. If an axis fires -> picture incomplete.")

    # Adjudication
    def quad_at(rows, kv): return rows[kv]['quad']
    print("\n=== ADJUDICATION ===")
    pivot = ra[1.0]
    print(f"  ARM A pivot (k=1): quad={pivot['quad']} rep={pivot['rep']} CV={pivot['cv']} "
          f"-> {'PIVOT BLIND (BL/near-Poisson) — predicted' if pivot['quad']=='BL' else 'PIVOT NOT BLIND — taxonomy FALSIFIED'}")
    sub = ra[4.0]; sup = ra[0.25]
    sub_fires = (sub['quad'] in ('TR', 'BR_novel', 'BR_artifact')) or (sub['rep'] and sub['rep'] > 0.2)
    sup_clusters = sup['mass'] > pivot['mass'] + 0.05
    print(f"  ARM A sub-side (k=4, CV0.5): quad={sub['quad']} rep={sub['rep']} -> repulsion {'FIRES (predicted)' if sub_fires else 'silent (unexpected)'}")
    print(f"  ARM A super-side (k=0.25, CV2): mass<.3={sup['mass']} vs pivot {pivot['mass']} -> clustering {'FIRES (predicted)' if sup_clusters else 'silent (unexpected)'}")
    b_quads = [rb[r]['quad'] for r in RHO_SWEEP]
    b_all_bl = all(q == 'BL' for q in b_quads)
    print(f"  ARM B quads across rho: {b_quads} -> {'ALL BL: near-Poisson transition INVISIBLE to both (taxonomy holds)' if b_all_bl else 'an axis FIRED: marginal-spacing picture INCOMPLETE'}")


if __name__ == "__main__":
    main()
