"""
r077_conditional.py — the analyses behind register entries R-156 and R-158, COMMITTED.

WHY THIS FILE EXISTS, and it is the arc's own defect wearing a new face:
R-156 and R-158 banked numbers into `arsrh/LOOK_REGISTER.md` (+3.30 sem, +3.07 sem, the six-point
verification of (1+y)/A, the n_eff/n ratios) from scripts that lived in a session TEMP DIRECTORY.
The prose was committed; the code that produced it was not. That is `knowledge_does_not_propagate`
in its purest form — a right result filed where it cannot be re-run, audited, or regression-tested.
A number whose generating code is in /tmp is a number with no provenance.

So this file is a VERBATIM consolidation of scratchpad r077.py / r077b.py / r077c.py / r077d.py.
It is deliberately NOT an improved version: it must reproduce what was banked, so that the banked
numbers can be checked against their own source. Improvements go in a NEW symbol, not by editing
this one — the same non-destructive rule the repairs followed.

  [1]  r077.py   — verify P(lambda >= A | y) = (1+y)/A numerically              (R-156)
  [2]  r077b.py  — per-object predicted vs measured P(g|event)                  (R-156)
  [3]  r077c.py  — pooled per stratum, binomial errors, z(meas-pred)            (R-156)
  [4]  r077d.py  — block bootstrap over convergent index, blocks of 50          (R-158)

Run:  $HOME/fmexplorer/bin/python3 arsrh/cubic/r077_conditional.py
Writes: arsrh/cubic/r077_conditional_measured.json  (the directory's convention)
"""
from __future__ import annotations

import json
import os
import sys
from math import gcd

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
for _p in (_HERE, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import mpmath as mp                                                        # noqa: E402
from scipy.integrate import quad                                           # noqa: E402

from gate0_ladder import convergents, lam, bigratio, cf_cbrt               # noqa: E402
from gate0e_precision import cf_of_mpf, collect_cyclic                     # noqa: E402

mp.mp.dps = 1260
A = 20
p_ = lambda *a: print(*a, flush=True)


def part1_derivation_check():
    """[1] P(lambda >= A | y) = (1+y)/A -- exact, verified at six (y, A) points."""
    p_("[1] verify  P(lambda >= A | y) = (1+y)/A")
    p_(f"{'y':>8s} {'A':>5s} {'numeric':>10s} {'(1+y)/A':>10s} {'abs err':>10s}")
    rows = []
    for y in (0.1, 0.4, 0.8):
        for A_ in (5.0, 20.0):
            X = min(1.0, 1.0 / (A_ - y))
            num = quad(lambda x: 1.0 / (1 + x * y) ** 2, 0, X)[0]
            den = quad(lambda x: 1.0 / (1 + x * y) ** 2, 0, 1)[0]
            got, exact = num / den, (1 + y) / A_
            rows.append({"y": y, "A": A_, "numeric": got, "exact": exact,
                         "abs_err": abs(got - exact)})
            p_(f"{y:>8.2f} {A_:>5.0f} {got:>10.5f} {exact:>10.5f} {abs(got-exact):>10.2e}")
    return rows


def _orbit(a0, M):
    """(g, y, lambda) along one object's convergent orbit. The 45-tail guard is the
    precision cut inherited from gate0e: the last convergents are not certified."""
    a, b, c, d = M
    P0, Q0 = convergents(a0)
    G, Y, L = [], [], []
    for i in range(1, len(a0) - 45):
        A2, B2 = a * P0[i] + b * Q0[i], c * P0[i] + d * Q0[i]
        if B2 == 0:
            continue
        if B2 < 0:
            A2, B2 = -A2, -B2
        G.append(gcd(abs(A2), B2))
        Y.append(bigratio(Q0[i - 1], Q0[i]))
        L.append(lam(a0, Q0, i))
    return np.array(G), np.array(Y), np.array(L)


def part2_per_object():
    """[2] per-object predicted vs measured. P(g|event) = E[(1+y)1{g}]/E[(1+y)]."""
    p_("\n[2] per-object: is P(g|event) DERIVED by the (1+y) reweighting?")
    p_(f"{'object':>16s} {'g':>5s} {'P(g) marg':>10s} {'PREDICTED':>10s} "
       f"{'MEASURED':>10s} {'pred/meas':>10s}")
    by_t = collect_cyclic(box=14, per=1)
    objs = []
    for t in (2, 5, 13):
        if t in by_t:
            A_, B_, C_, M = by_t[t][0]
            r = sorted(mp.re(x) for x in mp.polyroots([1, A_, B_, C_],
                                                      maxsteps=400, extraprec=800))
            objs.append((f"cyclic |t|={t}", cf_of_mpf(r[0]), M))
    for m in (2, 5, 12):
        objs.append((f"cbrt {m}", cf_cbrt(m, 1, 1200, 1400), (0, m, 1, 0)))

    out, ratios = [], []
    for nm, a0, M in objs:
        G, Y, L = _orbit(a0, M)
        ev, w = L >= A, 1.0 + Y
        for g in sorted(set(G)):
            marg = float((G == g).mean())
            pred = float((w * (G == g)).sum() / w.sum())
            meas = float((G[ev] == g).mean()) if ev.sum() else float("nan")
            if meas > 0.005:
                ratios.append(pred / meas)
                out.append({"object": nm, "g": int(g), "marginal": marg,
                            "predicted": pred, "measured": meas, "ratio": pred / meas})
                p_(f"{nm:>16s} {g:>5d} {marg:>10.4f} {pred:>10.4f} "
                   f"{meas:>10.4f} {pred/meas:>10.3f}")
    r = np.array(ratios)
    p_(f"\n  pred/meas over {len(r)} branches: mean {r.mean():.4f}, "
       f"sd {r.std(ddof=1):.4f}, range {r.min():.3f}..{r.max():.3f}")
    return out


def part3_pooled():
    """[3] pooled per stratum with binomial errors -- the source of '+3.30 sem'.

    NOTE FOR THE AUDIT TRAIL: `z` here is a per-branch, PER-CELL z. The number of cells
    examined is recorded in the JSON as `n_branches_examined` precisely because the banked
    +3.30 was the most extreme cell and no trials factor was ever stated against it.
    """
    p_("\n[3] pooled per stratum, binomial errors")
    p_(f"{'stratum':>12s} {'g':>5s} {'n_ev':>6s} {'marginal':>9s} {'PREDICTED':>10s} "
       f"{'MEASURED':>10s} {'z(meas-pred)':>13s}")
    by_t = collect_cyclic(box=14, per=8)
    out = []
    for t in (2, 5, 13):
        if t not in by_t:
            continue
        G, Y, L = [], [], []
        for A_, B_, C_, M in by_t[t]:
            r = sorted(mp.re(x) for x in mp.polyroots([1, A_, B_, C_],
                                                      maxsteps=400, extraprec=800))
            g_, y_, l_ = _orbit(cf_of_mpf(r[0]), M)
            G.append(g_); Y.append(y_); L.append(l_)
        G, Y, L = np.concatenate(G), np.concatenate(Y), np.concatenate(L)
        w, ev = 1.0 + Y, L >= A
        n = int(ev.sum())
        for g in sorted(set(G)):
            marg = float((G == g).mean())
            pred = float((w * (G == g)).sum() / w.sum())
            meas = float((G[ev] == g).mean())
            se = float(np.sqrt(max(pred * (1 - pred), 1e-12) / n))
            z = (meas - pred) / se
            out.append({"stratum": int(t), "g": int(g), "n_events": n,
                        "marginal": marg, "predicted": pred, "measured": meas, "z_iid": z})
            p_(f"{'|t|='+str(t):>12s} {g:>5d} {n:>6d} {marg:>9.4f} {pred:>10.4f} "
               f"{meas:>10.4f} {z:>+13.2f}")
    p_(f"\n  n_branches_examined = {len(out)}  <- the trials factor R-156 never stated")
    return out


def part4_block_bootstrap(seed=11, n_boot=600, block=50):
    """[4] block bootstrap over convergent index -- the source of '+3.07 sem'.

    R-158's own caveat, retained: |t|=5 returns n_eff/n > 1 (se_block < se_iid), the
    signature of overlapping blocks UNDER-dispersing. Those z's are not trustworthy.
    """
    p_(f"\n[4] block bootstrap (blocks of {block}, {n_boot} replicates)")
    p_(f"{'stratum':>10s} {'g':>4s} {'pred':>8s} {'meas':>8s} {'z_iid':>7s} "
       f"{'z_block':>9s} {'n_eff/n':>9s}")
    rng = np.random.default_rng(seed)
    by_t = collect_cyclic(box=14, per=8)
    out = []
    for t in (5, 13):
        if t not in by_t:
            continue
        G, Y, L = [], [], []
        for A_, B_, C_, M in by_t[t]:
            r = sorted(mp.re(x) for x in mp.polyroots([1, A_, B_, C_],
                                                      maxsteps=400, extraprec=800))
            g_, y_, l_ = _orbit(cf_of_mpf(r[0]), M)
            G.append(g_); Y.append(y_); L.append(l_)
        G, Y, L = np.concatenate(G), np.concatenate(Y), np.concatenate(L)
        w, ev = 1.0 + Y, L >= A
        n = int(ev.sum())
        for g in sorted(set(G)):
            pred = float((w * (G == g)).sum() / w.sum())
            meas = float((G[ev] == g).mean())
            if meas < 0.004 and pred < 0.004:
                continue
            se_iid = float(np.sqrt(pred * (1 - pred) / n))
            boot = []
            for _ in range(n_boot):
                idx = []
                for s0 in rng.integers(0, len(G) - block, size=len(G) // block):
                    idx.extend(range(s0, s0 + block))
                idx = np.array(idx)
                e2 = L[idx] >= A
                if e2.sum() > 10:
                    boot.append(float((G[idx][e2] == g).mean()))
            se_blk = float(np.std(boot, ddof=1))
            rec = {"stratum": int(t), "g": int(g), "predicted": pred, "measured": meas,
                   "z_iid": (meas - pred) / se_iid, "z_block": (meas - pred) / se_blk,
                   "n_eff_over_n": (se_iid / se_blk) ** 2,
                   "block_trustworthy": bool((se_iid / se_blk) ** 2 <= 1.0)}
            out.append(rec)
            p_(f"{'|t|='+str(t):>10s} {g:>4d} {pred:>8.4f} {meas:>8.4f} "
               f"{rec['z_iid']:>+7.2f} {rec['z_block']:>+9.2f} {rec['n_eff_over_n']:>9.2f}")
    return out


if __name__ == "__main__":
    res = {"A": A, "note": "verbatim consolidation of the R-156/R-158 scratchpad scripts; "
                           "committed so the banked numbers have provenance",
           "part1_derivation_check": part1_derivation_check(),
           "part2_per_object": part2_per_object(),
           "part3_pooled": part3_pooled(),
           "part4_block_bootstrap": part4_block_bootstrap()}
    dest = os.path.join(_HERE, "r077_conditional_measured.json")
    with open(dest, "w") as f:
        json.dump(res, f, indent=2)
    p_(f"\n-> wrote {dest}")
