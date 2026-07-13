"""
cross_substrate/trial_psth_unfold.py — EXTERNAL-rate (trial-PSTH) unfold for the Allen
V1 gratings long-range audit, with its decoy battery.

#2 showed a SELF-derived rate-unfold is structurally circular (drift aliases with the
correlation Σ²(L) measures). The trial-PSTH rate is EXTERNAL: λ_c(τ) = the rate as a
function of within-trial time τ, AVERAGED ACROSS OTHER PRESENTATIONS of the same
stimulus condition c (leave-one-out). It is derived from the stimulus-conditioned
cross-trial mean, NOT from the cell's own spike autocorrelation at scale L — so it
removes the stimulus-locked rate (orientation-tuning steps + within-trial F1) without
the self-circularity. Time-rescaling theorem: unfold each spike by ∫λ_c^{-p}.

DECOY BATTERY FIRST (standing rule, [[longrange_lens_discipline]]): external rate
removes #2's circularity but the trial structure could induce its OWN scale-L alias.
Test on synthetic GUE/Poisson/renewal with a KNOWN stimulus modulation imposed via
inverse time-rescaling — the unfold must RECOVER the intrinsic class (GUE→RIGID,
Poisson→POISSON_INDEP, renewal→not-RIGID) and NEVER read a non-rigid intrinsic as
false-RIGID. Only if it passes do we trust it on real cells.
"""
from __future__ import annotations

import os
import sys
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import longrange_discriminator as LD

K = 10                       # within-trial PSTH bins
EPS = 1e-9


def psth_unfold(pres):
    """pres = list of (cond_key, dur, rel_spike_times) per presentation, in timeline
    order. Returns unit-mean unfolded positions via LEAVE-ONE-OUT condition PSTH."""
    # group presentation indices + per-presentation bin counts by condition
    by_cond = {}
    binc = []                                  # per-presentation [K] counts
    durs = []
    for i, (c, dur, rel) in enumerate(pres):
        durs.append(dur)
        h = np.histogram(rel, bins=np.linspace(0, dur, K + 1))[0].astype(float)
        binc.append(h)
        by_cond.setdefault(c, []).append(i)
    binc = np.asarray(binc)                     # [P, K]
    P = len(pres)
    # LOO condition-summed counts → rate per bin (spikes per bin) for each presentation
    lam = np.zeros((P, K))
    for c, idx in by_cond.items():
        tot = binc[idx].sum(axis=0)
        for i in idx:
            denom = max(len(idx) - 1, 1)
            lam[i] = (tot - binc[i]) / denom    # expected counts per bin (LOO)
    lam = np.maximum(lam, EPS)
    Ep = lam.sum(axis=1)                        # expected count per presentation
    offsets = np.concatenate([[0.0], np.cumsum(Ep)])
    # unfold each spike: offset + cumulative expected count to its within-trial time
    out = []
    for i, (c, dur, rel) in enumerate(pres):
        if len(rel) == 0:
            continue
        w = dur / K
        cum = np.concatenate([[0.0], np.cumsum(lam[i])])   # expected count at bin edges
        k = np.clip((np.asarray(rel) / w).astype(int), 0, K - 1)
        frac = (np.asarray(rel) - k * w) / w
        Lam = cum[k] + frac * lam[i][k]
        out.append(offsets[i] + Lam)
    if not out:
        return np.zeros(0)
    u = np.sort(np.concatenate(out))
    d = np.diff(u); d = d[d > 0]
    return np.cumsum(np.concatenate([[0.0], d / d.mean()])) if d.size else u


# ── decoy battery ─────────────────────────────────────────────────────────────
def _impose_stimulus(intrinsic_sampler, starts, stops, conds, rng, m=0.6):
    """Generate a synthetic train with a KNOWN intrinsic class AND a known stimulus
    rate (orientation tuning + within-trial F1), via inverse time-rescaling, then
    return it as a presentation list for psth_unfold. The stimulus rate is EXTERNAL
    truth; a good unfold recovers the intrinsic class."""
    durs = stops - starts
    oris = sorted(set(c[0] for c in conds))
    pref = oris[len(oris) // 3]                 # an arbitrary preferred orientation
    tune = {o: 1.0 + 3.0 * np.exp(-((o - pref) ** 2) / (2 * 45.0 ** 2)) for o in oris}
    # build λ(t) on a fine grid over concatenated-presentation time
    grid_t, grid_lam, t0 = [], [], 0.0
    base = 8.0                                   # base rate scale (spikes/s)
    for (c, dur) in zip(conds, durs):
        tf = c[1] if np.isfinite(c[1]) else 2.0
        nb = 40
        tau = (np.arange(nb) + 0.5) * dur / nb
        s = base * tune[c[0]] * (1.0 + m * np.cos(2 * np.pi * tf * tau))
        grid_t.append(t0 + tau); grid_lam.append(np.maximum(s, EPS)); t0 += dur
    gt = np.concatenate(grid_t); gl = np.concatenate(grid_lam)
    # cumulative rate Λ(t); total expected count
    dt = np.gradient(gt)
    Lam = np.cumsum(gl * dt)
    Ntot = int(Lam[-1])
    X = intrinsic_sampler(Ntot, rng)            # unit-rate intrinsic on [0,~Ntot]
    X = X / X[-1] * Lam[-1]                      # scale to [0, Lam_total]
    t = np.interp(X, Lam, gt)                    # inverse-rescale → real (concat) time
    # assign to presentations
    pe = np.concatenate([[0.0], np.cumsum(durs)])
    pres = []
    pidx = np.searchsorted(pe, t, side="right") - 1
    pidx = np.clip(pidx, 0, len(durs) - 1)
    for i in range(len(durs)):
        rel = t[pidx == i] - pe[i]
        pres.append((conds[i], durs[i], rel))
    return pres


def decoy_battery(starts, stops, conds, n_seeds=10, ref_n=1500, L=50.0, verbose=True):
    samplers = {"GUE": LD.gue_positions, "Poisson": LD.poisson_positions,
                "renewal": LD.wigner_renewal}
    want = {"GUE": "RIGID_GUE", "Poisson": "POISSON_INDEP", "renewal": "INTERMEDIATE"}
    res = {}
    for name, samp in samplers.items():
        pres = _impose_stimulus(samp, starts, stops, conds, np.random.default_rng(7))
        u = psth_unfold(pres)
        v = LD.longrange_verdict(u, L=L, n_seeds=n_seeds, unfold_deg=None, ref_n=ref_n)
        res[name] = {"verdict": v["verdict"], "sigma2": round(v["sigma2"]["obs"], 2)}
    decoy_not_rigid = res["renewal"]["verdict"] != "RIGID_GUE"
    poisson_not_rigid = res["Poisson"]["verdict"] != "RIGID_GUE"
    gue_rigid = res["GUE"]["verdict"] == "RIGID_GUE"
    passed = bool(decoy_not_rigid and poisson_not_rigid)   # no false-RIGID is the gate
    res["PASS"] = passed
    res["gue_recovered"] = gue_rigid
    if verbose:
        print("TRIAL-PSTH DECOY BATTERY (impose stimulus on known class → unfold → recover?):")
        for n in ("GUE", "Poisson", "renewal"):
            print(f"  {n:8s} intrinsic → {res[n]['verdict']:13s} (σ²={res[n]['sigma2']})  "
                  f"want {want[n]}")
        print(f"  no-false-RIGID gate (Poisson & renewal not RIGID): {passed}; "
              f"GUE recovered as RIGID: {gue_rigid}")
    return res


if __name__ == "__main__":
    import glob, h5py
    f = sorted(glob.glob(os.path.expanduser(
        os.path.expanduser("~/fmexplorer/allen_cache/session_*/session_*.nwb"))))[0]
    with h5py.File(f, "r") as h:
        g = h["intervals/drifting_gratings_presentations"]
        starts, stops = g["start_time"][:], g["stop_time"][:]
        ori = g["orientation"][:]
        tf = g["temporal_frequency"][:]
    conds = [(float(o) if np.isfinite(o) else -1.0,
              float(t) if np.isfinite(t) else 2.0) for o, t in zip(ori, tf)]
    decoy_battery(np.asarray(starts), np.asarray(stops), conds)
