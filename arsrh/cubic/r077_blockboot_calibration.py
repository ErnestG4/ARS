"""
r077_blockboot_calibration.py — calibrate the n_eff/n diagnostic R-158 used to discard a row.

WHAT THE FIRST PASS FOUND (r077_blockboot_diagnosis.py), and why this second pass exists:
the SHUFFLED surrogate -- same values, serial order destroyed, so the truth is n_eff/n = 1.0 BY
CONSTRUCTION -- returned 0.675, 2.359, 0.934, 5.546, 0.861 across the five strata. And n_eff/n rose
MONOTONICALLY with block length in every stratum, reaching 104.7 at B=200. No property of a process
behaves like that. So the first pass tested the WRONG resampler shape (blocks over the event
subsequence) and, more importantly, showed the diagnostic itself needs calibrating before any
verdict is read off it.

  ⚠ My first pass also had a defect I am recording rather than quietly fixing: it CONCATENATED
  orbits before computing the autocorrelation. Concatenating sequences with different means
  manufactures POSITIVE long-range autocorrelation, so the Bartlett ratio it reported was
  contaminated. Fixed here by working per-orbit.

THIS PASS TESTS THE ACTUAL RESAMPLER, faithfully:
  r077d.py blocks over ALL CONVERGENTS (len(G) ~ 9000 pooled), then subsets to events inside each
  replicate. That is a different object from blocking the event subsequence, and it is the one that
  produced R-158's numbers.

TWO ARMS, both with a known truth so the instrument can be graded:

  ARM 1  SHUFFLED CONTROL on the faithful resampler. Jointly permute (G, Y, L) with ONE permutation:
         the joint marginal -- and hence the event rate and the conditional g-composition -- is
         preserved exactly, while serial order is destroyed. Truth: n_eff/n = 1.0.
         Repeated over many independent shuffles, so the SPREAD of the diagnostic is measured, not
         just one draw. A diagnostic whose own sampling distribution is wide cannot support
         "n_eff/n = 1.47, therefore the row is untrustworthy".

  ARM 2  SYNTHETIC n/B CALIBRATION on i.i.d. Bernoulli, where the truth is 1.0 by construction.
         Sweeps the ratio of series length to block length and reports where the estimator is
         usable. Produces a REUSABLE RULE rather than a one-off answer.

PRE-REGISTERED READINGS (written before this ran):
  - If ARM 1 is centred on 1.0 with a tight spread, the resampler is sound and the real n_eff/n
    values carry information about serial structure.
  - If ARM 1 is centred off 1.0, or its spread is wide enough to contain both 0.7 and 1.5, then
    the diagnostic cannot distinguish "under-dispersing" from "fine", and R-158 discarded the
    |t|=5 row on a reading the instrument could not support.

Run:  $HOME/fmexplorer/bin/python3 arsrh/cubic/r077_blockboot_calibration.py
Writes: arsrh/cubic/r077_blockboot_calibration_measured.json
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
for _p in (_HERE, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import mpmath as mp                                                    # noqa: E402
from gate0e_precision import collect_cyclic, gl2z_orbit_reps, cf_of_mpf  # noqa: E402
from r077_control import orbit, A_EV                                   # noqa: E402

SEED = 20260729
N_BOOT = 600
N_SHUFFLE = 60
p_ = lambda *a: print(*a, flush=True)


def stratum_arrays(t):
    """G, Y, L over ALL convergents, pooled over the DEDUPED orbits -- the array r077d.py blocks."""
    reps = gl2z_orbit_reps(collect_cyclic(box=14, per=8)[t])
    G, Y, L = [], [], []
    for (A, B, C, M) in reps:
        r = sorted(mp.re(x) for x in mp.polyroots([1, A, B, C], maxsteps=600, extraprec=1200))
        g_, y_, l_, _ = orbit(cf_of_mpf(r[0]), M)
        G.append(g_); Y.append(y_); L.append(l_)
    return np.concatenate(G), np.concatenate(Y), np.concatenate(L), len(reps)


def neff_r077d(G, Y, L, g, rng, B=50, n_boot=N_BOOT):
    """EXACTLY r077d.py's shape: block over all convergents, subset to events inside the replicate."""
    w = 1.0 + Y
    ev = L >= A_EV
    n = int(ev.sum())
    if n < 20:
        return None
    pred = float((w * (G == g)).sum() / w.sum())
    se_iid = math.sqrt(max(pred * (1 - pred), 1e-12) / n)
    nb = len(G) // B
    boot = []
    for _ in range(n_boot):
        starts = rng.integers(0, len(G) - B, size=nb)
        idx = (starts[:, None] + np.arange(B)[None, :]).ravel()
        e2 = L[idx] >= A_EV
        if e2.sum() > 10:
            boot.append(float((G[idx][e2] == g).mean()))
    if len(boot) < 50:
        return None
    se_blk = float(np.std(boot, ddof=1))
    return (se_iid / se_blk) ** 2 if se_blk > 0 else None


def synthetic_neff(n, B, p, rng, n_boot=400):
    """i.i.d. Bernoulli -- truth is n_eff/n = 1.0 by construction."""
    x = (rng.random(n) < p).astype(np.float64)
    nb = max(1, n // B)
    boot = np.empty(n_boot)
    for b in range(n_boot):
        starts = rng.integers(0, max(1, n - B), size=nb)
        idx = (starts[:, None] + np.arange(B)[None, :]).ravel()
        boot[b] = x[idx].mean()
    se_blk = float(boot.std(ddof=1))
    ph = float(x.mean())
    se_iid = math.sqrt(max(ph * (1 - ph), 1e-12) / n)
    return (se_iid / se_blk) ** 2 if se_blk > 0 else None


def main():
    rng = np.random.default_rng(SEED)
    p_("=" * 84)
    p_("R-077 — CALIBRATING the n_eff/n diagnostic before reading any verdict off it")
    p_("=" * 84)

    # ---------------- ARM 1: shuffled control on the FAITHFUL resampler ----------------
    p_(f"\n[ARM 1] shuffled control, r077d.py's own resampler, {N_SHUFFLE} independent shuffles")
    p_("        joint permutation of (G,Y,L): marginal preserved exactly, serial order destroyed")
    p_("        TRUTH = 1.000 by construction\n")
    p_(f"{'stratum':>9s} {'n_conv':>7s} {'n_ev':>6s} {'REAL':>7s} "
       f"{'shuffled mean':>14s} {'sd':>7s} {'5%':>7s} {'95%':>7s} {'|1.0 inside?':>13s}")
    arm1 = {}
    for t in (2, 5, 13, 17, 29):
        G, Y, L, n_orb = stratum_arrays(t)
        real = neff_r077d(G, Y, L, t, rng)
        vals = []
        for _ in range(N_SHUFFLE):
            perm = rng.permutation(len(G))
            v = neff_r077d(G[perm], Y[perm], L[perm], t, rng)
            if v:
                vals.append(v)
        v = np.array(vals)
        lo, hi = np.percentile(v, [5, 95])
        inside = bool(lo <= 1.0 <= hi)
        arm1[str(t)] = {"n_conv": int(len(G)), "n_events": int((L >= A_EV).sum()),
                        "n_orbits": n_orb, "real_neff": real,
                        "shuffled_mean": float(v.mean()), "shuffled_sd": float(v.std(ddof=1)),
                        "shuffled_p5": float(lo), "shuffled_p95": float(hi),
                        "truth_inside_90pct": inside,
                        "real_inside_shuffled_range": bool(real is not None and lo <= real <= hi)}
        p_(f"{'|t|='+str(t):>9s} {len(G):>7d} {int((L>=A_EV).sum()):>6d} "
           f"{(f'{real:.3f}' if real else 'n/a'):>7s} {v.mean():>14.3f} {v.std(ddof=1):>7.3f} "
           f"{lo:>7.3f} {hi:>7.3f} {('YES' if inside else 'NO'):>13s}")

    # ---------------- ARM 2: synthetic n/B calibration ----------------
    p_(f"\n[ARM 2] i.i.d. Bernoulli(p=0.15) calibration -- truth 1.000; where is the estimator usable?")
    p_(f"{'n/B':>7s} " + "".join(f"{'n='+str(n):>10s}" for n in (500, 1000, 4000, 9000)))
    arm2 = {}
    for ratio in (2, 5, 10, 25, 50, 100, 200):
        row = []
        for n in (500, 1000, 4000, 9000):
            B = max(2, n // ratio)
            vals = [synthetic_neff(n, B, 0.15, rng) for _ in range(12)]
            vals = [x for x in vals if x]
            row.append(float(np.median(vals)) if vals else None)
        arm2[str(ratio)] = {str(n): r for n, r in zip((500, 1000, 4000, 9000), row)}
        p_(f"{ratio:>7d} " + "".join(
            f"{(f'{r:.3f}' if r else 'n/a'):>10s}" for r in row))
    p_("  (n/B = number of blocks. As blocks get LONGER relative to the series, every replicate")
    p_("   covers more of the data, replicate means stop varying, se_block collapses and n_eff/n")
    p_("   inflates -- with NO serial structure present at all.)")

    # ---------------- verdict ----------------
    truth_covered = sum(1 for v in arm1.values() if v["truth_inside_90pct"])
    wide = sum(1 for v in arm1.values() if v["shuffled_p5"] <= 0.7 and v["shuffled_p95"] >= 1.5)
    real_in_null = sum(1 for v in arm1.values() if v["real_inside_shuffled_range"])

    p_("\n" + "=" * 84)
    if truth_covered == len(arm1) and wide == 0:
        verdict = "DIAGNOSTIC_SOUND"
        p_("VERDICT: the diagnostic is SOUND -- shuffled control brackets 1.0 tightly in every")
        p_("  stratum, so the real n_eff/n values do carry information about serial structure.")
    else:
        verdict = "DIAGNOSTIC_UNUSABLE_AT_THIS_NB"
        p_("VERDICT: the n_eff/n DIAGNOSTIC IS NOT USABLE at this series-length/block-length ratio.")
        p_(f"  Shuffled control (truth = 1.000) brackets 1.0 in only {truth_covered}/{len(arm1)} strata;")
        p_(f"  {wide}/{len(arm1)} strata have a null 90% interval so wide it contains BOTH 0.7 and 1.5;")
        p_(f"  and the REAL value falls inside the shuffled null in {real_in_null}/{len(arm1)} strata.")
        p_("  => R-158 discarded the |t|=5 row on a reading this instrument cannot support.")
        p_("     'n_eff/n > 1' was neither evidence of under-dispersion nor evidence against it.")
    p_("=" * 84)

    res = {"verdict": verdict, "arm1_shuffled_control": arm1, "arm2_synthetic_nb": arm2,
           "n_shuffle": N_SHUFFLE, "n_boot": N_BOOT,
           "truth_covered": truth_covered, "n_strata": len(arm1),
           "strata_with_useless_width": wide, "real_inside_null": real_in_null}
    dest = os.path.join(_HERE, "r077_blockboot_calibration_measured.json")
    with open(dest, "w") as f:
        json.dump(res, f, indent=2)
    p_(f"-> wrote {dest}")


if __name__ == "__main__":
    main()
