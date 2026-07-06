"""
phase36/magnitude_vs_R.py — within-GCM magnitude↔R test (converts the guardrail item coherence→evidence).

GUARDRAIL (banked): the cross-substrate "Kuramoto 2.87 vs Kaneko ~50" magnitude COHERES with
"clustering magnitude tracks the order-parameter jump ΔR" but does NOT test it (Kaneko≠Kuramoto in
family/topology/N). The banked within-Kaneko Δ-sweep is suggestive but Δ co-varies more than ΔR (Δ is the
natural-frequency heterogeneity — it changes the substrate itself, not just R).

CLEAN TEST (Will's spec): vary COUPLING ε at fixed (family, topology, N) → ε enters ONLY through the sync
term ε·R·sin(·), so it is the purest R-knob. Trace the N-robust clustering magnitude (mass<τ on the snapshot
— CV is the √N H-D trap, per the Kaneko magnitude probe + [[observable_choice_is_per_axis]]) as a function of
the DIRECTLY-MEASURED R along the ε-sweep. Do it at TWO N: if the magnitude-vs-R curve OVERLAYS (N-invariant),
the magnitude is a function of R (physical), not N (artifact) ⇒ magnitude↔R is within-substrate EVIDENCE.

Artifact-aware: snapshot observable (instantaneous spatial config, no temporal grid/binning/pooling) —
no quantization confound ([[pooled_rhythmic_repulsion_confound]]).
Falsifiable: if mass<τ is flat in R, or non-monotone, or the two-N curves DON'T overlay → magnitude does NOT
cleanly track R and the guardrail stands (stays coherence).
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import numpy as np
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)
from kaneko_gcm import gcm_run, circular_gaps  # noqa: E402

K = 0.6
DELTA = 0.04
EPS_GRID = [0.0, 0.008, 0.015, 0.020, 0.025, 0.030, 0.035, 0.04, 0.06, 0.08, 0.12, 0.20, 0.30]
SEEDS = (0, 1, 2, 3, 4)
TAU = 0.3


def _cell(job):
    N, eps, seed = job
    rng = np.random.default_rng(7000 + seed)
    R, snaps = gcm_run(N, K, eps, DELTA, n_iter=300, discard=2000, rng=rng)
    masses = [float(np.mean(circular_gaps(t) < TAU)) for t in snaps]
    cvs = [float(circular_gaps(t).std()) for t in snaps]
    return (N, eps, R, float(np.mean(masses)), float(np.mean(cvs)))


def main():
    Ns = (1500, 3000)
    jobs = [(N, e, s) for N in Ns for e in EPS_GRID for s in SEEDS]
    with ProcessPoolExecutor(max_workers=10) as pool:
        res = list(pool.map(_cell, jobs))

    # aggregate per (N, eps)
    agg = {}
    for N, eps, R, mass, cv in res:
        agg.setdefault((N, eps), []).append((R, mass, cv))
    curve = {N: [] for N in Ns}
    for (N, eps), vals in sorted(agg.items()):
        R = float(np.mean([v[0] for v in vals]))
        mass = float(np.mean([v[1] for v in vals]))
        cv = float(np.mean([v[2] for v in vals]))
        curve[N].append((eps, R, mass, cv))

    for N in Ns:
        print(f"\n=== N={N}: ε-sweep (fixed K={K}, Δ={DELTA}) — clustering magnitude vs measured R ===")
        print(f"  {'ε':>5} {'R':>6} {'mass<τ':>8} {'CV(√N trap)':>12}")
        for eps, R, mass, cv in curve[N]:
            print(f"  {eps:5.2f} {R:6.3f} {mass:8.4f} {cv:12.3f}")

    # Monotonicity of mass<τ in R, and N-invariance of the mass-vs-R curve
    print("\n=== ADJUDICATION ===")
    for N in Ns:
        Rs = [c[1] for c in curve[N]]; ms = [c[2] for c in curve[N]]
        order = np.argsort(Rs); Rs = np.array(Rs)[order]; ms = np.array(ms)[order]
        # Spearman-ish monotonicity via rank correlation
        rho = np.corrcoef(np.argsort(np.argsort(Rs)), np.argsort(np.argsort(ms)))[0, 1]
        print(f"  N={N}: R range {Rs.min():.3f}→{Rs.max():.3f}; mass<τ {ms.min():.3f}→{ms.max():.3f}; "
              f"rank-corr(mass,R)={rho:+.3f} {'(monotone↑)' if rho>0.8 else '(NOT monotone)'}")
    # N-invariance: interpolate both curves onto a common R grid and compare mass
    Rgrid = np.linspace(0.1, 0.85, 8)
    def interp(N):
        c = sorted(curve[N], key=lambda x: x[1])
        return np.interp(Rgrid, [x[1] for x in c], [x[2] for x in c])
    m1, m2 = interp(Ns[0]), interp(Ns[1])
    dev = float(np.mean(np.abs(m1 - m2)))
    print(f"  N-invariance of mass<τ-vs-R curve (|Δmass| over R∈[0.1,0.85], avg): {dev:.4f}")
    print(f"    {'OVERLAYS → magnitude is a function of R, not N: within-substrate EVIDENCE for magnitude↔R'  if dev < 0.05 else 'curves DIVERGE → magnitude is N-contaminated even on mass<τ: guardrail stands'}")
    # Contrast: does CV (the √N trap) overlay? Should NOT.
    def interp_cv(N):
        c = sorted(curve[N], key=lambda x: x[1])
        return np.interp(Rgrid, [x[1] for x in c], [x[3] for x in c])
    cv1, cv2 = interp_cv(Ns[0]), interp_cv(Ns[1])
    cvdev = float(np.mean(np.abs(cv1 - cv2)))
    print(f"  (contrast) CV-vs-R curve N-divergence: {cvdev:.4f} — CV is the √N trap, expected to diverge MORE than mass<τ")


if __name__ == "__main__":
    main()
