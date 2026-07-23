"""
thermo/tier1_plateau.py — run E_4's cross-route agreement TO PLATEAU (reviewer's falsifier).

Prereg: thermo/PLATEAU_PREREG_SEALED.json (sealed before this ran).

The tier1 diagnosis showed agreement climbing 10.2->13.4->17.0 for E_4 but never reaching a
plateau, so it could not distinguish truncation (climbs to route-1's ~28-digit ceiling) from a
genuine route-disagreement at digit ~22 (climbs to 22, then knees). This pushes nmax until the
climb either sustains its linear rate past 24 digits (truncation) or knees (disagreement).

WHY THIS IS AFFORDABLE. Naively, route 2 at nmax=11 for a 4-letter alphabet means enumerating
sum_{n<=11} 4^n ~ 5.6M periodic orbits and storing their multipliers. Instead: route 1 already
gives the dimension d1 to ~28 digits, and route 2's truncated root is within 17 digits of it, so
ONE Newton step from d1 lands on route-2's root:

    agreement_digits(nmax) = -log10 | f_nmax(d1) / f'_nmax(d1) |

where f_nmax = det(1 - L_s) truncated at cycle length nmax. This needs the traces t_1..t_nmax
only at s in {d1-h, d1, d1+h}, which a SINGLE depth-first pass accumulates with O(nmax) memory --
no multiplier list is ever stored. Each DFS node extends its parent's 2x2 cocycle matrix by one
letter (O(1) amortized), computes the periodic point's multiplier, and adds its contribution to
the three trace accumulators.

Run:  python3 thermo/tier1_plateau.py
"""
from __future__ import annotations

import json
import os
import sys
import time

import mpmath as mp

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from thermo.gauss_thermo import GaussOperator          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.setrecursionlimit(100000)


def traces_dfs(alphabet, nmax, svals, dps):
    """Accumulate t_n(s) = sum_{|w|=n} |rho_w|^s / (1 - rho_w) for each s in svals,
    by a single DFS carrying the running cocycle matrix. O(nmax) memory."""
    with mp.workdps(dps):
        A = [(mp.matrix([[0, 1], [1, a]])) for a in alphabet]
        t = [[mp.mpf(0)] * (nmax + 1) for _ in svals]      # t[k][n], 1-indexed in n

        def contrib(M, depth):
            p, q, r, s_ = M[0, 0], M[0, 1], M[1, 0], M[1, 1]
            disc = mp.sqrt((s_ - p) ** 2 + 4 * r * q)
            rho = None
            for x in ((-(s_ - p) + disc) / (2 * r), (-(s_ - p) - disc) / (2 * r)):
                cand = (p * s_ - q * r) / (r * x + s_) ** 2
                if rho is None or abs(cand) < abs(rho):
                    rho = cand
            arho, denom = abs(rho), (1 - rho)
            for k, sv in enumerate(svals):
                t[k][depth] += mp.power(arho, sv) / denom

        def rec(M, depth):
            contrib(M, depth)
            if depth < nmax:
                for Ai in A:
                    rec(M * Ai, depth + 1)

        for Ai in A:
            rec(Ai, 1)
        return t


def fredholm_det_from_traces(tn, nmax):
    """det(1 - L_s) = sum c_n via Newton identities from traces t_1..t_nmax."""
    c = [mp.mpf(1)]
    for n in range(1, nmax + 1):
        cn = mp.fsum(c[n - k] * tn[k] for k in range(1, n + 1))
        c.append(-cn / n)
    return mp.fsum(c)


def agreement_at(alphabet, nmax, d1, dps=45):
    """One Newton step from d1: agreement = -log10 |f(d1)/f'(d1)|."""
    with mp.workdps(dps):
        h = mp.mpf(10) ** (-dps // 3)
        svals = [d1 - h, d1, d1 + h]
        t = traces_dfs(alphabet, nmax, svals, dps)
        fm = fredholm_det_from_traces(t[0], nmax)
        f0 = fredholm_det_from_traces(t[1], nmax)
        fp = fredholm_det_from_traces(t[2], nmax)
        fprime = (fp - fm) / (2 * h)
        step = f0 / fprime                       # d1 - root2
        return float(-mp.log10(abs(step) / abs(d1)))


def main():
    mp.mp.dps = 60
    # converged route-1 dimension for E_4, from the sealed tier1 predictions
    sealed = json.load(open(os.path.join(HERE, "TIER1_PREREG_SEALED.json")))
    d1_E4 = mp.mpf(next(p["route1_collocation"] for p in sealed["predictions"]
                        if p["alphabet"] == [1, 2, 3, 4]))
    # route-1 ceiling: re-measure d1 at higher N to know how far route 2 CAN agree
    op_hi = GaussOperator(N=52, dps=80, Ne=110)
    from thermo.tier1_dim_EA import dim_collocation
    d1_hi = dim_collocation(op_hi, (1, 2, 3, 4))
    ceiling = float(-mp.log10(abs(d1_hi - d1_E4) / abs(d1_hi)))
    print(f"E_4 route-1 self-consistency (N=40 vs N=52): {ceiling:.1f} digits "
          f"(route-2 agreement cannot exceed this)\n")

    print("prereg falsifier: a KNEE below the ceiling = genuine disagreement; "
          "sustained linear climb = truncation.\n")
    print(f"  {'nmax':>5s} {'agree (digits)':>16s} {'gain/step':>11s} {'secs':>7s}")
    rows, prev = [], None
    for nmax in (6, 7, 8, 9, 10, 11):
        t = time.time()
        a = agreement_at((1, 2, 3, 4), nmax, d1_hi)
        gain = "" if prev is None else f"{a - prev:+.2f}"
        rows.append({"nmax": nmax, "agree": round(a, 2),
                     "gain": None if prev is None else round(a - prev, 2)})
        print(f"  {nmax:5d} {a:16.2f} {gain:>11s} {time.time() - t:7.0f}")
        prev = a

    gains = [r["gain"] for r in rows if r["gain"] is not None]
    tail_gains = gains[-3:]
    max_reached = rows[-1]["agree"]
    # knee = gain collapsing toward 0 well below the ceiling
    knee = (min(tail_gains) < 1.0 and max_reached < ceiling - 3)
    linear = max(tail_gains) - min(tail_gains) < 1.5 and min(tail_gains) > 2.0
    verdict = ("KNEE_DISAGREEMENT" if knee else
               "LINEAR_TRUNCATION" if (linear and max_reached > 24) else
               "INCONCLUSIVE")
    out = {"route1_ceiling_digits": ceiling, "rows": rows,
           "tail_gains": tail_gains, "max_agreement_reached": max_reached,
           "VERDICT": verdict,
           "reading": ("agreement climbs linearly with no knee and passes 24 digits => the "
                       "diagnosis verdict is corrected from 'no disagreement (period)' to 'no "
                       "disagreement in the first %.0f digits', truncation confirmed to that depth"
                       % max_reached) if verdict == "LINEAR_TRUNCATION" else
                      ("agreement KNEES below the route-1 ceiling => genuine route disagreement at "
                       "that level, the falsifier fired") if verdict == "KNEE_DISAGREEMENT" else
                      "neither clean linear climb nor clean knee; needs more nmax"}
    print(f"\n  route-1 ceiling: {ceiling:.1f} digits")
    print(f"  max agreement reached: {max_reached:.1f} digits")
    print(f"  tail gains/step: {tail_gains}")
    print(f"  VERDICT: {verdict}")
    json.dump(out, open(os.path.join(HERE, "tier1_plateau_measured.json"), "w"),
              indent=2, default=str)
    print("\nwrote tier1_plateau_measured.json")


if __name__ == "__main__":
    main()
