"""
phase36/kaneko_gcm.py — Track 1.4 Kaneko globally-coupled circle maps (Phase 36 generalization test).

Pre-registration: phase36/TRACK1_4_KANEKO_CONFIG_JUSTIFICATION.md. Headline observable = SNAPSHOT
SPATIAL NNS (sorted phases on S¹ → circular gaps → joint_q_profile), the high-D structure Chialvo
lacked, where the clustering↔desynchronization transition could land in the spectral/repulsion axis.
NOT temporal timing (that's the reconfirmation trap). Independent regime marker = sync order parameter R.

Mean-field (Kuramoto-style) coupled circle map, O(N)/step:
  θ_i(t+1) = θ_i + Ω_i + (K/2π)sin(2πθ_i) + ε·R·sin(2π(ψ−θ_i))  mod 1,  R e^{i2πψ}=(1/N)Σ e^{i2πθ_j}.
Heterogeneous natural frequencies Ω_i (uniform spread Δ) make the sync transition nontrivial. Sweep
coupling ε at fixed (K, Δ): low ε → desynchronised (R≈0), high ε → clustered (R≈1).
"""
from __future__ import annotations
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
for p in (ROOT,):
    sys.path.insert(0, p)


def gcm_step(theta, Om, K, eps):
    z = np.exp(2j * np.pi * theta)
    Z = z.mean(); R = np.abs(Z); psi = np.angle(Z) / (2 * np.pi)
    theta = theta + Om + (K / (2 * np.pi)) * np.sin(2 * np.pi * theta) \
        + eps * R * np.sin(2 * np.pi * (psi - theta))
    return np.mod(theta, 1.0), R


def gcm_run(N, K, eps, Delta, n_iter, discard, rng, snap_every=20):
    Om = rng.uniform(0.5 - Delta, 0.5 + Delta, N)          # heterogeneous natural frequencies
    theta = rng.uniform(0, 1, N)
    for _ in range(discard):
        theta, _ = gcm_step(theta, Om, K, eps)
    Rs, snaps = [], []
    for i in range(n_iter):
        theta, R = gcm_step(theta, Om, K, eps)
        Rs.append(R)
        if i % snap_every == 0:
            snaps.append(theta.copy())
    return float(np.mean(Rs)), snaps


def circular_gaps(theta):
    """Circular nearest-neighbour gaps on S¹ (sum to 1), renormalised to unit mean (×N)."""
    s = np.sort(np.mod(theta, 1.0))
    g = np.diff(s)
    g = np.append(g, s[0] + 1.0 - s[-1])     # wrap-around gap
    g = g[g > 0]
    return g / g.mean()


def snapshot_gap_cv(snaps):
    """CV of the circular-gap distribution, averaged over snapshots. Poisson(uniform)→1, clock→0,
    clustered→>1."""
    cvs = [circular_gaps(t).std() for t in snaps]
    return float(np.mean(cvs))


def feasibility(N=3000, K=0.6, Delta=0.04, n_iter=400, discard=2000):
    """PRE-CHECK (gates the instrument run): does the snapshot gap distribution CHANGE across the
    desync→clustered transition? If R rises 0→1 AND gap-CV moves, the snapshot-NNS test CAN be positive."""
    rng = np.random.default_rng(0)
    print(f"FEASIBILITY pre-check — GCM N={N}, K={K}, Δ={Delta}; sweep coupling ε")
    print(f"  (R: sync order param, 0=desync→1=clustered;  gap-CV: Poisson~1, clock~0, clustered>1)")
    print(f"  {'ε':>5s} {'R':>6s} {'gap-CV':>8s}  regime")
    rows = []
    for eps in (0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.6):
        R, snaps = gcm_run(N, K, eps, Delta, n_iter, discard, rng)
        cv = snapshot_gap_cv(snaps)
        regime = "clustered" if R > 0.6 else ("partial" if R > 0.25 else "desync")
        rows.append((eps, R, cv))
        print(f"  {eps:5.2f} {R:6.3f} {cv:8.3f}  {regime}")
    cvs = [r[2] for r in rows]; Rs = [r[1] for r in rows]
    print(f"\n  R range {min(Rs):.3f}→{max(Rs):.3f}; gap-CV range {min(cvs):.3f}→{max(cvs):.3f} (spread {max(cvs)-min(cvs):.3f})")
    can_be_positive = (max(Rs) - min(Rs) > 0.4) and (max(cvs) - min(cvs) > 0.15)
    print(f"  >>> snapshot distribution {'CHANGES across the transition — test CAN be positive, proceed to instrument' if can_be_positive else 'does NOT change enough — observable likely blind; reconsider'}")
    return rows, can_be_positive


def snapshot_fingerprint(snaps):
    """Average ARS readout over snapshots, on BOTH axes:
      repulsion axis  — rep_med (joint_q_profile) + dominant quadrant  [Poisson↔GUE; may be clustering-blind]
      clustering axis — gap-CV + mass<0.3 (fraction of unit-mean gaps below 0.3) [Poisson↔super-Poisson]."""
    from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic
    reps, masses, cvs, quads = [], [], [], []
    for theta in snaps:
        g = circular_gaps(theta)
        cvs.append(g.std()); masses.append(float(np.mean(g < 0.3)))
        pos = np.cumsum(np.concatenate([[0.0], g]))    # event positions for the spectral instrument
        try:
            j = joint_q_profile(pos, q_max=25, min_events_per_q=100)
            qd = joint_quadrant_diagnostic(j); w = qd[~qd['underpowered']]
            if len(w):
                reps.append(float(w['rep_int_q'].median()))
                quads.append(str(w['quadrant'].value_counts().idxmax()))
        except Exception:
            pass
    return dict(rep_med=round(float(np.mean(reps)), 4) if reps else None,
                quad=(max(set(quads), key=quads.count) if quads else None),
                cv=round(float(np.mean(cvs)), 3), mass_lt_0p3=round(float(np.mean(masses)), 4))


def instrument(N=3000, K=0.6, Delta=0.04, n_iter=600, discard=2000, label="in-sample"):
    rng = np.random.default_rng(1)
    print(f"\nINSTRUMENT ({label}) — GCM N={N}, K={K}, Δ={Delta}; snapshot-NNS on BOTH axes vs coupling ε")
    print(f"  {'ε':>5s} {'R':>6s} | {'rep_med':>8s} {'quad':>12s} (repulsion) | {'CV':>7s} {'mass<.3':>8s} (clustering)")
    out = {}
    for eps in (0.0, 0.01, 0.02, 0.03, 0.04, 0.08, 0.2):
        R, snaps = gcm_run(N, K, eps, Delta, n_iter, discard, rng)
        fp = snapshot_fingerprint(snaps)
        out[eps] = dict(R=round(R, 3), **fp)
        print(f"  {eps:5.2f} {R:6.3f} | {str(fp['rep_med']):>8s} {str(fp['quad']):>12s}            "
              f"| {fp['cv']:7.2f} {fp['mass_lt_0p3']:8.4f}")
    return out


def _mag_cell(job):
    """One (N, Delta) magnitude cell — picklable. Separation (clustered ε=0.2 minus desync ε=0) on the
    clustering axis, in BOTH CV (N-scaling-prone) and mass<τ (bounded, N-robust), + the R-jump."""
    import numpy as _np
    N, Delta = job
    rng = _np.random.default_rng(7)
    def read(eps):
        R, snaps = gcm_run(N, 0.6, eps, Delta, 300, 2000, rng)
        gaps = [circular_gaps(t) for t in snaps]
        cv = float(_np.mean([g.std() for g in gaps]))
        mass = float(_np.mean([_np.mean(g < 0.3) for g in gaps]))
        return R, cv, mass
    Rd, cvd, md = read(0.0); Rc, cvc, mc = read(0.2)
    return dict(N=N, Delta=Delta, R_jump=round(Rc - Rd, 3),
                cv_sep=round(cvc - cvd, 3), mass_sep=round(mc - md, 4),
                R_desync=round(Rd, 3), R_clustered=round(Rc, 3))


def magnitude_probe():
    """Does the clustering-axis separation track a PHYSICAL variable (R-jump) or just N (artifact)?
    (a) vary N at fixed Δ: CV-sep should scale with N (artifact), mass-sep ~N-robust.
    (b) vary Δ at fixed N: does the separation track the R-jump (physical transition sharpness)?"""
    from concurrent.futures import ProcessPoolExecutor
    jobs = [(N, 0.04) for N in (1000, 2000, 4000, 8000)] + [(2000, d) for d in (0.02, 0.06, 0.10, 0.15)]
    with ProcessPoolExecutor(max_workers=10) as pool:
        rows = list(pool.map(_mag_cell, jobs))
    print("MAGNITUDE PROBE — clustering-axis separation (clustered−desync) vs physical knobs")
    print("(a) vary N at Δ=0.04 (CV-sep ~√N artifact? mass-sep N-robust?):")
    for r in [x for x in rows if x['Delta'] == 0.04]:
        print(f"   N={r['N']:5d}: R-jump={r['R_jump']:.3f}  CV-sep={r['cv_sep']:8.3f}  mass<.3-sep={r['mass_sep']:.4f}")
    print("(b) vary Δ at N=2000 (does separation track the R-jump?):")
    for r in [x for x in rows if x['N'] == 2000]:
        print(f"   Δ={r['Delta']:.2f}: R-jump={r['R_jump']:.3f} (R {r['R_desync']}→{r['R_clustered']})  "
              f"CV-sep={r['cv_sep']:8.3f}  mass<.3-sep={r['mass_sep']:.4f}")
    return rows


if __name__ == "__main__":
    import sys as _s
    if len(_s.argv) > 1 and _s.argv[1] == "magnitude":
        magnitude_probe()
    elif len(_s.argv) > 1 and _s.argv[1] == "instrument":
        a = instrument()
        # out-of-sample: different N_osc AND K, regimes marked independently by R
        b = instrument(N=1500, K=1.0, Delta=0.06, label="out-of-sample")
        def sep_rep(d):
            lo = [v['rep_med'] for k, v in d.items() if v['R'] < 0.3 and v['rep_med'] is not None]
            hi = [v['rep_med'] for k, v in d.items() if v['R'] > 0.6 and v['rep_med'] is not None]
            return (round(np.mean(hi) - np.mean(lo), 4) if lo and hi else None)
        def sep_clust(d):
            lo = [v['cv'] for k, v in d.items() if v['R'] < 0.3]
            hi = [v['cv'] for k, v in d.items() if v['R'] > 0.6]
            return (round(np.mean(hi) - np.mean(lo), 3) if lo and hi else None)
        print("\n=== ADJUDICATION ===")
        print(f"  repulsion-axis (rep_med) separation desync→clustered: in-sample {sep_rep(a)}, out-of-sample {sep_rep(b)}")
        print(f"  clustering-axis (CV)      separation desync→clustered: in-sample {sep_clust(a)}, out-of-sample {sep_clust(b)}")
    else:
        feasibility()
