"""
r077_blockboot_diagnosis.py — is n_eff/n > 1 a BUG in the bootstrap, or a property of the process?

THE OPEN ITEM. R-158 discarded the |t|=5 rows because their block bootstrap returns
n_eff/n = se_iid^2/se_block^2 > 1 (se_block < se_iid), which it read as "overlapping blocks
UNDER-dispersing" -- i.e. a defect. The review agent tested the rival explanation (orbit
duplication) and found it only partly holds: dedup moves it the right way at |t|=13 (0.94->0.79),
|t|=17 (1.00->0.96) and |t|=29 (0.77->0.66), but |t|=5 STAYS at 1.47 and |t|=2 RISES (1.12->1.28).
It then refused to turn "not refuted" into a verdict. Correct call, and it left this open.

HYPOTHESES, WRITTEN BEFORE THE RUN, WITH THE MEASUREMENT THAT SEPARATES THEM
  H_BUG   The moving-block resampler is implemented wrongly (overlap, block straddling, resample
          size), so se_block is wrong for ANY input.
          PREDICTS: a SHUFFLED surrogate -- same values, serial structure destroyed, so the truth
          is exactly n_eff/n = 1 by construction -- still returns n_eff/n != 1.
  H_REAL  The estimator is fine and the g-indicator sequence is genuinely NEGATIVELY autocorrelated,
          which makes the long-run variance SMALLER than the iid variance. This is textbook, not
          pathology: Var(mean) = (gamma_0/n)(1 + 2*sum rho_k), so sum rho_k < 0 => n_eff > n.
          PREDICTS: (i) the shuffled surrogate returns n_eff/n = 1.00 within its own error;
                    (ii) the Bartlett long-run-variance ratio computed DIRECTLY from the ACF
                         predicts the bootstrap ratio, with no bootstrap involved.
  H_STRAT The MECHANISM behind H_REAL: the residue (p_n,q_n) mod Delta is a Markov chain on a state
          space whose size grows with Delta. When the space is SMALL relative to the block length,
          every block covers it near-exhaustively, so each block's g-composition is close to the
          exact marginal -- systematic/stratified sampling, which reduces variance below binomial.
          When Delta is large the block cannot cover the space and the benefit disappears.
          PREDICTS: the variance reduction STRENGTHENS with block length B for small Delta
                    (|t|=2, Delta=4; |t|=5, Delta=25) and is absent for large Delta
                    (|t|=13, Delta=169; |t|=17, 289; |t|=29, 841).

WHY IT MATTERS BEYOND THIS ROW. If H_REAL holds, then "n_eff/n > 1" is NOT a bug signature, and
R-158 discarded a row for a reason that does not exist -- on top of R-162, where it discarded the
row's z_iid on a diagnostic that only impeached z_block. Two different errors, same discarded row.

Run:  $HOME/fmexplorer/bin/python3 arsrh/cubic/r077_blockboot_diagnosis.py
Writes: arsrh/cubic/r077_blockboot_diagnosis_measured.json
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
from gate0e_precision import collect_cyclic, gl2z_orbit_reps           # noqa: E402
from gate0e_precision import cf_of_mpf                                 # noqa: E402
from r077_control import orbit, A_EV                                   # noqa: E402

STRATA = (2, 5, 13, 17, 29)
BLOCKS = (10, 25, 50, 100, 200)
N_BOOT = 600
SEED = 20260728
p_ = lambda *a: print(*a, flush=True)


def event_indicator(t):
    """The g-indicator sequence RESTRICTED TO EVENTS, per deduped orbit, for branch g = |t|.

    Restricted to events because that is what the estimator averages: meas = mean over events of
    1{g == t}. The serial dependence that matters is the dependence along the EVENT subsequence,
    not along all convergents.
    """
    reps = gl2z_orbit_reps(collect_cyclic(box=14, per=8)[t])
    seqs = []
    for (A, B, C, M) in reps:
        r = sorted(mp.re(x) for x in mp.polyroots([1, A, B, C], maxsteps=600, extraprec=1200))
        G, Y, L, _n = orbit(cf_of_mpf(r[0]), M)
        ev = L >= A_EV
        seqs.append((G[ev] == t).astype(np.float64))
    return seqs, reps


def bartlett_lrv_ratio(x, L=None):
    """LRV / gamma_0 by the Bartlett kernel. < 1 means negative net autocorrelation, which is
    exactly the condition for n_eff > n. No bootstrap involved -- this is the independent witness."""
    x = np.asarray(x, float)
    n = len(x)
    if L is None:
        L = max(1, int(round(4 * (n / 100.0) ** (2.0 / 9.0))))   # Newey-West rule of thumb
    xc = x - x.mean()
    g0 = float(np.dot(xc, xc) / n)
    if g0 <= 0:
        return None, L
    s = g0
    for k in range(1, min(L, n - 1) + 1):
        gk = float(np.dot(xc[:-k], xc[k:]) / n)
        s += 2.0 * (1.0 - k / (L + 1.0)) * gk
    return s / g0, L


def block_neff(x, rng, B=50, n_boot=N_BOOT):
    """n_eff/n from a moving-block bootstrap of the MEAN of x -- the same resampling shape the
    original r077d.py used, applied to the event-restricted indicator."""
    x = np.asarray(x, float)
    n = len(x)
    if n <= B + 2:
        return None
    nb = max(1, n // B)
    boot = np.empty(n_boot)
    for b in range(n_boot):
        starts = rng.integers(0, n - B, size=nb)
        idx = (starts[:, None] + np.arange(B)[None, :]).ravel()
        boot[b] = x[idx].mean()
    se_blk = float(boot.std(ddof=1))
    p = float(x.mean())
    se_iid = math.sqrt(max(p * (1 - p), 1e-12) / n)
    return (se_iid / se_blk) ** 2 if se_blk > 0 else None


def main():
    rng = np.random.default_rng(SEED)
    p_("=" * 82)
    p_("R-077 — is n_eff/n > 1 a BUG, or negative serial correlation in the process?")
    p_("  hypotheses and their separating predictions are in the module docstring, written unrun")
    p_("=" * 82)

    out = {}
    p_(f"\n{'stratum':>9s} {'Delta':>6s} {'orbits':>7s} {'n_ev':>6s} {'p':>7s} "
       f"{'LRV/g0':>8s} {'1/LRV':>7s} {'neff/n B=50':>12s} {'SHUFFLED':>10s}")
    for t in STRATA:
        seqs, reps = event_indicator(t)
        x = np.concatenate(seqs)
        n, p = len(x), float(x.mean())
        lrv, L = bartlett_lrv_ratio(x)
        ne = block_neff(x, rng, B=50)
        # SPECIFICITY CONTROL: destroy serial structure, keep the values. Truth is n_eff/n = 1.
        xs = rng.permutation(x)
        ne_shuf = block_neff(xs, rng, B=50)
        out[str(t)] = {"Delta": t * t, "n_orbits": len(reps), "n_events": n, "p": p,
                       "bartlett_lrv_ratio": lrv, "bartlett_L": L,
                       "predicted_neff_over_n": (1.0 / lrv) if lrv else None,
                       "block_neff_over_n_B50": ne, "shuffled_neff_over_n_B50": ne_shuf}
        p_(f"{'|t|='+str(t):>9s} {t*t:>6d} {len(reps):>7d} {n:>6d} {p:>7.4f} "
           f"{(f'{lrv:.3f}' if lrv else 'n/a'):>8s} {(f'{1/lrv:.3f}' if lrv else 'n/a'):>7s} "
           f"{(f'{ne:.3f}' if ne else 'n/a'):>12s} {(f'{ne_shuf:.3f}' if ne_shuf else 'n/a'):>10s}")

    # ---- H_STRAT: does the reduction strengthen with block length for small Delta? ----
    p_(f"\n[H_STRAT] n_eff/n vs block length B  (stratification predicts: grows with B for small "
       f"Delta, flat ~1 for large)")
    p_(f"{'stratum':>9s} " + "".join(f"{'B='+str(b):>9s}" for b in BLOCKS))
    sweep = {}
    for t in STRATA:
        seqs, _ = event_indicator(t)
        x = np.concatenate(seqs)
        row = [block_neff(x, rng, B=b) for b in BLOCKS]
        sweep[str(t)] = {str(b): v for b, v in zip(BLOCKS, row)}
        p_(f"{'|t|='+str(t):>9s} " + "".join(
            f"{(f'{v:.3f}' if v else 'n/a'):>9s}" for v in row))

    # ---- verdict ----
    shuf = [v["shuffled_neff_over_n_B50"] for v in out.values() if v["shuffled_neff_over_n_B50"]]
    shuf_ok = all(abs(s - 1.0) < 0.15 for s in shuf)
    agree = []
    for v in out.values():
        if v["predicted_neff_over_n"] and v["block_neff_over_n_B50"]:
            agree.append(abs(v["predicted_neff_over_n"] - v["block_neff_over_n_B50"])
                         / v["block_neff_over_n_B50"])
    acf_predicts = bool(agree) and float(np.median(agree)) < 0.25

    p_("\n" + "=" * 82)
    if not shuf_ok:
        verdict = "H_BUG"
        p_("VERDICT: H_BUG — the shuffled surrogate does NOT return 1.0, so the resampler is wrong")
        p_(f"  shuffled n_eff/n: {[round(s,3) for s in shuf]}  (truth is 1.0 by construction)")
    elif acf_predicts:
        verdict = "H_REAL"
        p_("VERDICT: H_REAL — the bootstrap is CORRECT and the sequence is genuinely negatively")
        p_("  autocorrelated where n_eff/n > 1. The shuffled control returns 1.0, and the Bartlett")
        p_(f"  long-run variance predicts the bootstrap ratio with no bootstrap involved")
        p_(f"  (median relative disagreement {100*np.median(agree):.1f}%).")
        p_("  => 'n_eff/n > 1' IS NOT A BUG SIGNATURE. R-158 discarded the |t|=5 row for a reason")
        p_("     that does not exist.")
    else:
        verdict = "INDETERMINATE"
        p_("VERDICT: INDETERMINATE — shuffle control is clean but the ACF does not predict the")
        p_(f"  bootstrap (median relative disagreement {100*np.median(agree):.1f}%). Neither")
        p_("  hypothesis is established; do not launder this into a verdict.")
    p_("=" * 82)

    res = {"verdict": verdict, "per_stratum": out, "block_sweep": sweep,
           "shuffled_control_ok": shuf_ok,
           "acf_predicts_bootstrap": acf_predicts,
           "median_rel_disagreement": float(np.median(agree)) if agree else None}
    dest = os.path.join(_HERE, "r077_blockboot_diagnosis_measured.json")
    with open(dest, "w") as f:
        json.dump(res, f, indent=2)
    p_(f"-> wrote {dest}")


if __name__ == "__main__":
    main()
