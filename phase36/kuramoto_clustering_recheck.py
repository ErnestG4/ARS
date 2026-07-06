"""
phase36/kuramoto_clustering_recheck.py — retrospective two-axis audit, TOP candidate.

Phase 30 banked Kuramoto as INSENSITIVE / RATE_CONFOUNDED / NO_MATCH — but on the REPULSION axis only
(rep_int modal = BR_artifact at every K, NNS engine). Kuramoto is THE canonical synchronization model
⇒ a CLUSTERING-type transition (desync≈Poisson → sync≈clustered bursts). Tonight's Kaneko/Chialvo
showed clustering-type transitions are repulsion-axis-BLIND but clustering-axis-VISIBLE. So Phase 30's
INSENSITIVE is a prime axis-incomplete suspect.

Re-check: across the K-sweep (K_factor 0→2, K_c=2γ), on the AGGREGATE (pooled) population spike train
(synchronized ⇒ all oscillators fire in tight phase-locked bursts ⇒ super-Poisson pooled IEIs):
  - repulsion axis: rep_med (joint_q_profile) — expect FLAT across K (reproduce INSENSITIVE)
  - clustering axis: CV, mass<0.3 of unit-mean pooled IEIs — expect to RISE across K_c if axis-incomplete
  - order parameter R (sim.r_trace) — independent regime marker (the λ₁/R analogue)
Out-of-sample: different N. If clustering axis separates desync→sync where rep_med is flat ⇒ Phase 30
INSENSITIVE was AXIS-INCOMPLETE; Kuramoto IS sensitive (clustering-type), confirming the taxonomy on a
banked past negative.
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")          # 1 thread/worker — we parallelize across cells instead
import numpy as np
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
for p in (ROOT, os.path.join(ROOT, "phase30")):
    sys.path.insert(0, p)
import kuramoto as KUR                                                   # noqa: E402
from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic  # noqa: E402

KF = [0.0, 0.5, 0.8, 1.0, 1.2, 1.5, 2.0]   # K_factor (×K_c); K_c at K_factor=1


def both_axes(ieis):
    s = np.asarray(ieis, float); s = s[s > 0]; s = s / s.mean()
    cv = float(s.std()); mass = float(np.mean(s < 0.3))         # clustering axis
    rep = quad = None
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
    return dict(cv=round(cv, 3), mass_lt_0p3=round(mass, 4), rep_med=rep, quad=quad)


def _cell(job):
    """One (N, kf, seed) cell — picklable worker. Returns (N, kf, R, axes-dict) or None."""
    N, kf, seed = job
    Kc = KUR.critical_coupling(0.5 * 2.0 * np.pi)
    sim = KUR.simulate(K=kf * Kc, N=N, seed=seed)
    agg = KUR.aggregate_spikes(sim)
    if agg.size < 500:
        return None
    ax = both_axes(np.diff(agg))
    return (N, kf, float(np.mean(sim.r_trace)), ax)


def run(N=100, seeds=(0, 1, 2), label="in-sample", pool=None):
    Kc = KUR.critical_coupling(0.5 * 2.0 * np.pi)
    jobs = [(N, kf, s) for kf in KF for s in seeds]
    results = list(pool.map(_cell, jobs))
    by_kf = {kf: [] for kf in KF}
    for r in results:
        if r is not None:
            by_kf[r[1]].append((r[2], r[3]))
    print(f"\nKURAMOTO re-check ({label}) — N={N}, K_c={Kc:.3f}; AGGREGATE pooled train, BOTH axes")
    print(f"  {'K/Kc':>5s} {'R':>6s} | {'rep_med':>8s} {'quad':>12s} (repulsion) | {'CV':>7s} {'mass<.3':>8s} (clustering)")
    rows = {}
    for kf in KF:
        cells = by_kf[kf]
        if not cells:
            continue
        rs = [c[0] for c in cells]; cvs = [c[1]['cv'] for c in cells]
        masses = [c[1]['mass_lt_0p3'] for c in cells]
        reps = [c[1]['rep_med'] for c in cells if c[1]['rep_med'] is not None]
        quads = [c[1]['quad'] for c in cells if c[1]['quad'] is not None]
        R = np.mean(rs); cv = np.mean(cvs); mass = np.mean(masses)
        rep = round(float(np.mean(reps)), 4) if reps else None
        quad = max(set(quads), key=quads.count) if quads else None
        rows[kf] = dict(R=round(R, 3), rep_med=rep, quad=quad, cv=round(cv, 3), mass_lt_0p3=round(mass, 4))
        print(f"  {kf:5.2f} {R:6.3f} | {str(rep):>8s} {str(quad):>12s}            | {cv:7.2f} {mass:8.4f}")
    return rows


def main():
    with ProcessPoolExecutor(max_workers=10) as pool:
        a = run(N=100, label="in-sample", pool=pool)
        b = run(N=200, seeds=(0, 1), label="out-of-sample (N=200)", pool=pool)

    def sep(d, key):
        lo = [v[key] for k, v in d.items() if v['R'] < 0.35 and v[key] is not None]
        hi = [v[key] for k, v in d.items() if v['R'] > 0.65 and v[key] is not None]
        return (round(np.mean(hi) - np.mean(lo), 4) if lo and hi else None)

    print("\n=== ADJUDICATION (desync R<0.35 → sync R>0.65) ===")
    for lab, d in (("in-sample", a), ("out-of-sample", b)):
        print(f"  {lab}: repulsion (rep_med) sep = {sep(d,'rep_med')} ; clustering (CV) sep = {sep(d,'cv')} ; (mass<.3) sep = {sep(d,'mass_lt_0p3')}")
    print("\n  Phase 30 banked verdict: INSENSITIVE (repulsion axis). If rep_med sep≈0 but CV/mass sep is")
    print("  large & same-sign in+oos ⇒ AXIS-INCOMPLETE: Kuramoto IS sensitive on the clustering axis.")


if __name__ == "__main__":
    main()
