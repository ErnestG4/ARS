"""
r077_depth_check.py — does the R-077 anomaly exist OUTSIDE the window it was found in?

This is the independent verification of the review agent's decisive push. Two things are tested,
and the second is the one that matters:

  (1) DEDUP. `collect_cyclic` enumerates POLYNOMIALS over a coefficient box and dedups by nothing.
      Several polynomials per stratum are GL2(Z) translates of the SAME cubic irrational -- verified
      exactly: at |t|=13, polys (-7,0,7) and (-4,-11,1) have roots differing by exactly 1.0, so
      their continued fractions agree from a_1 on and their (g, y, lambda) arrays are identical.
      Duplicating an orbit k times leaves `meas` and `pred` unchanged and multiplies n by k, so
      |z| inflates by exactly sqrt(k). Every pooled z in R-156/R-158 -- and in my own R-161
      look-elsewhere arm -- was computed on duplicated orbits.

  (2) OUT-OF-SAMPLE. The published numbers come from convergent indices < ~1150, which is simply
      where DIG=1200 ran out. That is a WINDOW, not a process. Extending the same orbits deeper
      gives a DISJOINT remainder on which the same quantity can be measured. If the enrichment is
      a property of the skew product it must persist; if it is a property of the window it will not.

Run:  $HOME/fmexplorer/bin/python3 arsrh/cubic/r077_depth_check.py
Writes: arsrh/cubic/r077_depth_check_measured.json
"""
from __future__ import annotations

import json
import math
import os
import sys
from math import gcd

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
for _p in (_HERE, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import mpmath as mp                                                    # noqa: E402
from gate0_ladder import certified_cf, convergents, lam, bigratio      # noqa: E402
from gate0e_precision import collect_cyclic                            # noqa: E402

A_EV = 20
TAIL = 45
DEEP_DIG = 6000          # 5x the sealed DIG=1200
PUBLISHED_CUT = 1150     # where the sealed window ended
STRATA = (5, 13, 17, 29)
p_ = lambda *a: print(*a, flush=True)


def cf_at(A, B, C, dig):
    mp.mp.dps = dig + 60
    r = sorted(mp.re(x) for x in mp.polyroots([1, A, B, C], maxsteps=600, extraprec=1200))
    x = r[0]
    return certified_cf(int(mp.floor(x * 10 ** dig)), 10 ** dig, 20000)


def dedup_orbits(polys, dig=400):
    """Keep one representative per GL2(Z) orbit. Two cubics are in the same orbit iff their CF
    TAILS coincide up to a shift (Serret). Compared on a signature of 60 partial quotients taken
    well past any transient -- integer translates are the shift-0 case and are caught by this too."""
    reps, sigs = [], []
    for (A, B, C, M) in polys:
        a = cf_at(A, B, C, dig)
        if len(a) < 200:
            continue
        dup = False
        for s in sigs:
            # does this orbit's tail appear anywhere in an existing orbit's tail?
            probe = tuple(a[100:160])
            for off in range(0, 120):
                if tuple(s[100 + off:160 + off]) == probe:
                    dup = True
                    break
            if dup:
                break
            probe2 = tuple(s[100:160])
            for off in range(0, 120):
                if tuple(a[100 + off:160 + off]) == probe2:
                    dup = True
                    break
            if dup:
                break
        if not dup:
            reps.append((A, B, C, M))
            sigs.append(a)
    return reps


def excess_series(a, M, cut):
    """(sum of (1{g=t} - w-weighted pred) contributions) split at `cut`, on the g = |t| branch."""
    aa, bb, cc, dd = M
    P, Q = convergents(a)
    G, Y, L, IDX = [], [], [], []
    for i in range(1, len(a) - TAIL):
        A2, B2 = aa * P[i] + bb * Q[i], cc * P[i] + dd * Q[i]
        if B2 == 0:
            continue
        if B2 < 0:
            A2, B2 = -A2, -B2
        G.append(gcd(abs(A2), B2)); Y.append(bigratio(Q[i - 1], Q[i]))
        L.append(lam(a, Q, i)); IDX.append(i)
    return (np.array(G), np.array(Y), np.array(L), np.array(IDX))


def measure(G, Y, L, g_target, mask):
    """(meas - pred) and its binomial sem on the g_target branch, within `mask`."""
    Gm, Ym, Lm = G[mask], Y[mask], L[mask]
    if len(Gm) == 0:
        return None
    w = 1.0 + Ym
    ev = Lm >= A_EV
    n = int(ev.sum())
    if n < 20:
        return None
    pred = float((w * (Gm == g_target)).sum() / w.sum())
    meas = float((Gm[ev] == g_target).mean())
    se = math.sqrt(max(pred * (1 - pred), 1e-12) / n)
    return {"pred": pred, "meas": meas, "excess": meas - pred, "sem": se, "n_events": n}


def main():
    by_t = collect_cyclic(box=14, per=8)
    p_("=" * 78)
    p_("R-077 DEPTH CHECK — does the anomaly exist outside its own window?")
    p_("=" * 78)

    dedup_report = {}
    p_("\n[1] GL2(Z)-ORBIT DEDUP of collect_cyclic (which dedups by nothing)")
    p_(f"{'stratum':>10s} {'polys':>6s} {'orbits':>7s} {'dup factor':>11s} {'z inflation':>12s}")
    reps = {}
    for t in STRATA:
        polys = by_t[t]
        r = dedup_orbits(polys)
        reps[t] = r
        f = len(polys) / max(len(r), 1)
        dedup_report[str(t)] = {"polys": len(polys), "orbits": len(r), "dup_factor": f,
                                "z_inflation_sqrt": math.sqrt(f)}
        p_(f"{'|t|='+str(t):>10s} {len(polys):>6d} {len(r):>7d} {f:>11.2f} {math.sqrt(f):>12.2f}x")

    p_(f"\n[2] OUT-OF-SAMPLE at DIG={DEEP_DIG} ({DEEP_DIG//1200}x the sealed depth)")
    p_(f"    published window = convergent index < {PUBLISHED_CUT}; remainder is DISJOINT")
    p_(f"{'stratum':>10s} {'orbits':>7s} {'window excess':>16s} {'remainder excess':>19s}")

    win_e, win_v, rem_e, rem_v = [], [], [], []
    per_stratum = {}
    for t in STRATA:
        we, wv, re_, rv = [], [], [], []
        for (A, B, C, M) in reps[t]:
            a = cf_at(A, B, C, DEEP_DIG)
            G, Y, L, IDX = excess_series(a, M, PUBLISHED_CUT)
            for tag, mask, acc_e, acc_v in (("win", IDX < PUBLISHED_CUT, we, wv),
                                            ("rem", IDX >= PUBLISHED_CUT, re_, rv)):
                m = measure(G, Y, L, t, mask)
                if m:
                    acc_e.append(m["excess"]); acc_v.append(m["sem"] ** 2)
        def pool(e, v):
            if not e:
                return None, None
            w = 1.0 / np.array(v)
            return float(np.sum(w * np.array(e)) / w.sum()), float(1.0 / math.sqrt(w.sum()))
        wE, wS = pool(we, wv); rE, rS = pool(re_, rv)
        per_stratum[str(t)] = {"window": {"excess": wE, "sem": wS},
                               "remainder": {"excess": rE, "sem": rS},
                               "n_orbits": len(reps[t])}
        win_e += we; win_v += wv; rem_e += re_; rem_v += rv
        p_(f"{'|t|='+str(t):>10s} {len(reps[t]):>7d} "
           f"{(f'{wE:+.5f}+-{wS:.5f}' if wE is not None else 'n/a'):>16s} "
           f"{(f'{rE:+.5f}+-{rS:.5f}' if rE is not None else 'n/a'):>19s}")

    def pool(e, v):
        w = 1.0 / np.array(v)
        return float(np.sum(w * np.array(e)) / w.sum()), float(1.0 / math.sqrt(w.sum()))
    WE, WS = pool(win_e, win_v)
    RE, RS = pool(rem_e, rem_v)

    p_("\n" + "-" * 78)
    p_(f"  POOLED window    excess = {WE:+.5f} +- {WS:.5f}   ({WE/WS:+.2f} sem)")
    p_(f"  POOLED remainder excess = {RE:+.5f} +- {RS:.5f}   ({RE/RS:+.2f} sem)")
    p_(f"  statistical weight of remainder vs window: {(WS/RS)**2:.1f}x")
    z_h1 = (RE - WE) / RS
    z_h0 = RE / RS
    p_(f"\n  H1 'the window excess is real and constant' predicts {WE:+.5f} in the remainder:")
    p_(f"     observed {RE:+.5f}  ->  H1 rejected at {abs(z_h1):.1f} sem")
    p_(f"  H0 'no excess' predicts 0.0:")
    p_(f"     observed {RE:+.5f}  ->  {z_h0:+.2f} sem, p = {2*(1-0.5*(1+math.erf(abs(z_h0)/math.sqrt(2)))):.3f}")

    verdict = ("WINDOW_ARTIFACT" if abs(z_h1) > 3 and abs(z_h0) < 3 else
               "PERSISTS" if abs(z_h0) > 3 else "INDETERMINATE")
    p_("\n" + "=" * 78)
    if verdict == "WINDOW_ARTIFACT":
        p_("VERDICT: the enrichment is a property of the WINDOW, not of the skew product.")
        p_("  There is no residue->future coupling here to localise. R-160/R-161 stand as")
        p_("  instrument results; the ANOMALY they certify does not survive out of sample.")
    elif verdict == "PERSISTS":
        p_("VERDICT: the enrichment PERSISTS out of sample. The localisation is warranted.")
    else:
        p_("VERDICT: INDETERMINATE at this depth. Neither hypothesis is excluded.")
    p_("=" * 78)

    res = {"deep_dig": DEEP_DIG, "published_cut": PUBLISHED_CUT, "verdict": verdict,
           "dedup": dedup_report, "per_stratum": per_stratum,
           "pooled_window": {"excess": WE, "sem": WS, "z": WE / WS},
           "pooled_remainder": {"excess": RE, "sem": RS, "z": RE / RS},
           "z_reject_H1": z_h1, "z_vs_H0": z_h0,
           "remainder_weight_vs_window": (WS / RS) ** 2}
    dest = os.path.join(_HERE, "r077_depth_check_measured.json")
    with open(dest, "w") as f:
        json.dump(res, f, indent=2)
    p_(f"-> wrote {dest}")


if __name__ == "__main__":
    main()
