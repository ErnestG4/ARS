"""
phase37/hc_cv_reexpression.py — re-express the GCM ε-knob magnitude↔R result in CV (the Set-4-clean coord).

Banked this session (magnitude_vs_R.py): mass<τ rises monotone with R (rank-corr +0.995), N-invariant
(|Δ|=0.002) ⇒ "within-substrate evidence for magnitude↔R." N-invariance ruled out the DIMENSIONALITY (√N)
confound. But Set 4 (phase37) then established mass<τ = CV + SHAPE: at matched CV, mass<τ varies 15–50%
across renewal families because it's a quantile. ε reshapes the collective attractor's gap distribution
(not only its dispersion), so part of the +0.995 could be SHAPE-DRIFT, not clustering MAGNITUDE.

This decomposes it (data already in the sweep):
  1. rank-corr(CV, R) vs rank-corr(mass<τ, R) over the N-invariant transition region (R∈[0.1,0.85] — CV is
     N-invariant there; only the SATURATED R>0.9 regime makes snapshot-CV the √N trap). Does CV track R with
     comparable strength?
  2. SHAPE residual: overlay the GCM (CV, mass<τ) points against the Set-4 renewal mass<τ(CV) band. On the
     band → mass<τ is fully explained by CV (pure dispersion, no extra shape). Off the band → the GCM gap
     distribution has shape beyond CV, and that part of mass<τ's trend is shape, not magnitude.
Verdict: CV(R) comparably monotone → H-C is CLEAN, restated in the family-invariant variable (CV). mass<τ
outruns / departs the band → restate as "tracks ε, partly through shape."
"""
from __future__ import annotations
import os, sys, json
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import numpy as np
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "cross_substrate"))
sys.path.insert(0, os.path.join(ROOT, "phase36"))
from kaneko_gcm import gcm_run, circular_gaps  # noqa: E402

K, DELTA = 0.6, 0.04
EPS = [0.0, 0.008, 0.015, 0.020, 0.025, 0.030, 0.035, 0.04, 0.06, 0.08, 0.12, 0.20, 0.30]
SEEDS = (0, 1, 2, 3, 4)
NS = (1500, 3000)
TRANS_R = (0.10, 0.85)   # region where snapshot-CV is N-invariant (above it, CV → √N trap)


def _cell(job):
    N, eps, seed = job
    rng = np.random.default_rng(7000 + seed)
    R, snaps = gcm_run(N, K, eps, DELTA, n_iter=300, discard=2000, rng=rng)
    cvs = [float(circular_gaps(t).std()) for t in snaps]
    masses = [float(np.mean(circular_gaps(t) < 0.3)) for t in snaps]
    return (N, eps, R, float(np.mean(cvs)), float(np.mean(masses)))


def spearman(x, y):
    rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def renewal_band():
    """Set-4 renewal mass<τ(CV) band: for each CV bin, the min/max mass03 across families (the shape band)."""
    f = os.path.join(HERE, "set4_calibrator_family_map.jsonl")
    pts = []
    for ln in open(f):
        r = json.loads(ln)
        if not r["family"].startswith("NULL") and r["cv"] is not None and r["mass03"] is not None:
            pts.append((r["cv"], r["mass03"]))
    pts = np.array(pts)
    return pts  # (cv, mass03) renewal calibrator cloud


def main():
    jobs = [(N, e, s) for N in NS for e in EPS for s in SEEDS]
    with ProcessPoolExecutor(max_workers=10) as pool:
        res = list(pool.map(_cell, jobs))
    import collections
    agg = collections.defaultdict(list)
    for N, eps, R, cv, mass in res:
        agg[(N, eps)].append((R, cv, mass))
    curve = {N: [] for N in NS}
    for (N, eps), v in agg.items():
        curve[N].append((float(np.mean([x[0] for x in v])), float(np.mean([x[1] for x in v])),
                         float(np.mean([x[2] for x in v]))))
    for N in NS:
        curve[N].sort()

    print("=== GCM ε-knob: CV and mass<τ vs R (per N) ===")
    for N in NS:
        print(f"  N={N}:  {'R':>6} {'CV':>8} {'mass<τ':>8}")
        for R, cv, mass in curve[N]:
            tag = "" if TRANS_R[0] <= R <= TRANS_R[1] else " (sat/√N)"
            print(f"          {R:6.3f} {cv:8.3f} {mass:8.4f}{tag}")

    # 1. monotone strength in the N-invariant transition region
    print("\n=== (1) monotone strength in transition region R∈[0.10,0.85] (CV N-invariant here) ===")
    for N in NS:
        tr = [(R, cv, mass) for R, cv, mass in curve[N] if TRANS_R[0] <= R <= TRANS_R[1]]
        if len(tr) < 4:
            continue
        Rs = [t[0] for t in tr]; cvs = [t[1] for t in tr]; masses = [t[2] for t in tr]
        print(f"  N={N}: n={len(tr)}  rank-corr(CV,R)={spearman(cvs,Rs):+.3f}  "
              f"rank-corr(mass<τ,R)={spearman(masses,Rs):+.3f}")
    # N-invariance of CV vs mass in transition (interp onto common R grid)
    Rg = np.linspace(0.12, 0.84, 8)
    def interp(N, idx):
        tr = sorted([(R, cv, mass) for R, cv, mass in curve[N] if R <= 0.9])
        return np.interp(Rg, [t[0] for t in tr], [t[idx] for t in tr])
    cv_dev = float(np.mean(np.abs(interp(NS[0], 1) - interp(NS[1], 1))))
    cv_rel = cv_dev / float(np.mean([np.mean(interp(N, 1)) for N in NS]))
    mass_dev = float(np.mean(np.abs(interp(NS[0], 2) - interp(NS[1], 2))))
    print(f"  N-invariance in transition: CV |Δ|={cv_dev:.4f} (rel {cv_rel:.3f})  mass<τ |Δ|={mass_dev:.4f}")

    # 2. shape residual: GCM (CV,mass) vs Set-4 renewal band
    print("\n=== (2) shape residual: GCM mass<τ(CV) vs Set-4 renewal band ===")
    band = renewal_band()
    print("   CV    GCM_mass   renewal_mass(band lo–hi)   on-band?")
    off = 0; checked = 0
    for N in NS[:1]:   # one N suffices for the shape check (CV is the x-axis)
        for R, cv, mass in curve[N]:
            if cv < 0.6 or cv > 1.95:   # within the renewal-band CV coverage
                continue
            near = band[np.abs(band[:, 0] - cv) < 0.12]
            if len(near) < 2:
                continue
            lo, hi = near[:, 1].min(), near[:, 1].max()
            checked += 1
            onband = lo - 0.02 <= mass <= hi + 0.02
            off += (not onband)
            print(f"  {cv:5.2f}  {mass:7.4f}    {lo:.3f}–{hi:.3f}              {'yes' if onband else 'NO (shape)'}")
    print(f"\n  GCM points off the renewal band: {off}/{checked}")

    print("\n=== VERDICT ===")
    print("  If CV(R) rank-corr ≈ mass<τ(R) AND GCM lies on the renewal band → magnitude↔R is CLEAN,")
    print("  re-stated in CV (family-invariant dispersion). If GCM departs the band / mass outruns CV →")
    print("  part of the +0.995 is SHAPE; restate as 'tracks ε, partly through shape.'")
    out = os.path.join(HERE, "hc_cv_reexpression.json")
    json.dump({str(N): curve[N] for N in NS}, open(out, "w"), indent=1)
    print(f"  Wrote {out}")


if __name__ == "__main__":
    main()
