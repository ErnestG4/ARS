"""
phase36/kuramoto_snapshot_repulsion.py — settle Kuramoto's repulsion-axis conclusiveness (Phase 36).

Per the per-axis-observable principle: the pooled-TEMPORAL train is superposition-contaminated on the
REPULSION axis (finite-N superposition of near-periodic crossings → residual sub-Poisson regularity →
high rep_med in a non-Wigner superposed-periodic shape → KS declines → BR_artifact = INCONCLUSIVE). The
SPATIAL SNAPSHOT drops that superposition structure → the right observable for the repulsion axis.

Prediction (Will): desync snapshot phases ~uniform on the circle → Poisson gaps → CLEAN BL (like Kaneko).
- Clean BL ⇒ Kuramoto upgrades to repulsion-BLIND; the Kaneko/Kuramoto substrate-split DISSOLVES into an
  observable effect (pooled-temporal was the wrong observable for the repulsion axis).
- Still declines (BR_artifact) on the matched snapshot observable ⇒ the substrate split is REAL/earned.
Either way a finding. Matched to Kaneko's snapshot readout (circular gaps → joint_q_profile).

Kuramoto phases integrated directly (the Phase 30 sim returns spike trains, not phase snapshots): mean-
field forward-Euler dθ_i = ω_i + K·R·sin(ψ−θ_i), Lorentzian ω_i (matched to phase30/kuramoto), K_c=2γ.
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import numpy as np
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
for p in (ROOT, os.path.join(ROOT, "phase30")):
    sys.path.insert(0, p)
import kuramoto as KUR                                                   # noqa: E402
from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic  # noqa: E402

GAMMA = 0.5 * 2.0 * np.pi
OMEGA0 = 2.0 * np.pi
KC = KUR.critical_coupling(GAMMA)        # = 2γ


def integrate_snapshots(K, N, seed, dt=0.01, T_sim=150.0, T_transient=50.0, snap_every=150):
    omega = KUR._draw_lorentzian(N, OMEGA0, GAMMA, seed=seed)   # matched to Phase 30 substrate
    rng = np.random.default_rng(seed + 999)
    th = rng.uniform(0, 2 * np.pi, N)
    n_total = int(T_sim / dt); n_trans = int(T_transient / dt)
    snaps, Rs = [], []
    for i in range(n_total):
        z = np.exp(1j * th).mean(); R = np.abs(z); psi = np.angle(z)
        th = th + dt * (omega + K * R * np.sin(psi - th))
        if i >= n_trans:
            Rs.append(R)
            if (i - n_trans) % snap_every == 0:
                snaps.append(np.mod(th, 2 * np.pi).copy())
    return snaps, float(np.mean(Rs))


def circular_gaps(theta_2pi):
    s = np.sort(np.mod(theta_2pi / (2 * np.pi), 1.0))          # → [0,1), matched to Kaneko
    g = np.diff(s); g = np.append(g, s[0] + 1.0 - s[-1]); g = g[g > 0]
    return g / g.mean()


def snapshot_axes(snaps):
    reps, quads, cvs = [], [], []
    for th in snaps:
        g = circular_gaps(th); cvs.append(float(g.std()))
        pos = np.cumsum(np.concatenate([[0.0], g]))
        try:
            j = joint_q_profile(pos, q_max=25, min_events_per_q=100)
            qd = joint_quadrant_diagnostic(j); w = qd[~qd['underpowered']]
            if len(w):
                reps.append(float(w['rep_int_q'].median())); quads.append(str(w['quadrant'].value_counts().idxmax()))
        except Exception:
            pass
    return (round(float(np.mean(reps)), 4) if reps else None,
            (max(set(quads), key=quads.count) if quads else None),
            round(float(np.mean(cvs)), 3))


def _cell(job):
    N, kf, seed = job
    snaps, R = integrate_snapshots(kf * KC, N, seed)
    if len(snaps) < 3:
        return None
    rep, quad, cv = snapshot_axes(snaps)
    return (N, kf, round(R, 3), rep, quad, cv)


def main():
    N = 2000   # matched to Kaneko snapshot N (one snapshot ⇒ enough gaps for joint_q_profile)
    KF = [0.0, 0.5, 0.8, 1.0, 1.5, 2.0]
    jobs = [(N, kf, s) for kf in KF for s in (0, 1, 2)]
    with ProcessPoolExecutor(max_workers=10) as pool:
        res = [r for r in pool.map(_cell, jobs) if r]
    print(f"KURAMOTO repulsion axis on the SPATIAL SNAPSHOT (N={N}, matched to Kaneko) — does desync land clean BL?")
    print(f"  {'K/Kc':>5s} {'R':>6s} | {'rep_med':>8s} {'quad':>12s} (repulsion) | {'CV':>7s} (clustering xcheck)")
    by = {}
    for kf in KF:
        cells = [r for r in res if r[1] == kf]
        if not cells:
            continue
        R = np.mean([c[2] for c in cells]); cv = np.mean([c[5] for c in cells])
        reps = [c[3] for c in cells if c[3] is not None]
        quads = [c[4] for c in cells if c[4] is not None]
        rep = round(float(np.mean(reps)), 4) if reps else None
        quad = max(set(quads), key=quads.count) if quads else None
        by[kf] = (R, rep, quad, cv)
        print(f"  {kf:5.2f} {R:6.3f} | {str(rep):>8s} {str(quad):>12s}            | {cv:7.3f}")
    # adjudication: desync (K/Kc=0) quadrant
    d = by.get(0.0)
    print("\n=== ADJUDICATION ===")
    if d:
        print(f"  desync (K/Kc=0): rep_med={d[1]}, quad={d[2]}")
        if d[2] == 'BL':
            print("  >>> CLEAN BL on the snapshot ⇒ Kuramoto repulsion-BLIND; the BR_artifact was a pooled-temporal")
            print("      superposition artifact; Kaneko/Kuramoto substrate-split DISSOLVES into an observable effect.")
        elif d[2] and 'BR' in d[2]:
            print("  >>> still BR/declines on the matched snapshot ⇒ substrate split is REAL/earned (genuine rigidity).")
        else:
            print(f"  >>> {d[2]} — inspect (neither clean-BL nor BR).")


if __name__ == "__main__":
    main()
