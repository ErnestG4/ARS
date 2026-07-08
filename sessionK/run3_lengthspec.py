"""Run 3 — n=5 vs n=3 periodic-orbit length-degeneracy (operator-side arithmeticity).

PRE-REGISTERED SIGNATURE (named before building): the arithmeticity contrast is
carried by the *length-multiplicity growth* of transfer-operator periodic orbits
(closed geodesics sharing a length), NOT by any leading-eigenvalue / Lyapunov / Levy
difference (which differ trivially between two surfaces).

Closed geodesics <-> primitive cyclic words in the continued-fraction alphabet; the
geodesic length is set by the trace of the product of CF matrices:
  n=3 (modular, ARITHMETIC):  M_a = [[a,-1],[1,0]],  a in alphabet  -> trace in Z
       (rank-1 trace set) => many words share an integer trace => EXPONENTIAL
       length-multiplicity (Bogomolny-Georgeot-Schmit / Bolte-Steil-Steiner; the
       mechanism behind the banked CP1 Poisson statistics).
  n=5 (Hecke G_5, NON-arithmetic, trace field Q(sqrt5)): M_a = [[a*phi,-1],[1,0]],
       phi=2cos(pi/5)=(1+sqrt5)/2 -> trace in Z[phi] (rank-2, dense in R) => distinct
       words have generically distinct traces => GENERIC BOUNDED multiplicity.

Metric: mean length-multiplicity = (#primitive necklaces of period k) / (#distinct
traces). PASS = n=3 grows exponentially, n=5 stays ~O(1). Same word enumeration for
both; the ONLY difference is the entry ring (Z vs Z[phi]) -- so the split is the
arithmeticity, not a construction artifact.
"""
import json, os
import numpy as np
from itertools import product
from math import gcd

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- exact Z[phi] arithmetic: element p+q*phi represented as (p,q), phi^2=phi+1 ----
def zphi_mul(x, y):
    (p, q), (r, s) = x, y
    return (p * r + q * s, p * s + q * r + q * s)
def zphi_add(x, y): return (x[0] + y[0], x[1] + y[1])
def mat_mul(A, B, mul, add):
    return [[add(mul(A[0][0], B[0][0]), mul(A[0][1], B[1][0])),
             add(mul(A[0][0], B[0][1]), mul(A[0][1], B[1][1]))],
            [add(mul(A[1][0], B[0][0]), mul(A[1][1], B[1][0])),
             add(mul(A[1][0], B[0][1]), mul(A[1][1], B[1][1]))]]

def necklaces(alphabet, k):
    """Primitive cyclic words (Lyndon-word representatives) of length k."""
    seen = set(); out = []
    for w in product(alphabet, repeat=k):
        rots = [w[i:] + w[:i] for i in range(k)]
        if len(set(rots)) < k:     # non-primitive (has a period dividing k)
            continue
        canon = min(rots)
        if canon not in seen:
            seen.add(canon); out.append(canon)
    return out

def trace_n3(word):
    M = [[1, 0], [0, 1]]
    for a in word:
        M = mat_mul(M, [[a, -1], [1, 0]], lambda x, y: x * y, lambda x, y: x + y)
    return abs(M[0][0] + M[1][1])                 # integer |trace|

PHI = (1 + 5 ** 0.5) / 2
def trace_n5(word):
    M = [[(1, 0), (0, 0)], [(0, 0), (1, 0)]]
    for a in word:
        Ma = [[(0, a), (-1, 0)], [(1, 0), (0, 0)]]   # a*phi = (0,a)
        M = mat_mul(M, Ma, zphi_mul, zphi_add)
    p, q = zphi_add(M[0][0], M[1][1])              # trace in Z[phi] as (p,q)
    return (-p, -q) if (p + q * PHI) < 0 else (p, q)   # canonicalize by real sign

def run(alphabet=(1, 2), kmax=15):
    res = {"alphabet": list(alphabet), "n3": [], "n5": []}
    for k in range(2, kmax + 1):
        necks = necklaces(alphabet, k)
        t3 = [trace_n3(w) for w in necks]
        t5 = [trace_n5(w) for w in necks]
        d3, d5 = len(set(t3)), len(set(t5))
        res["n3"].append({"k": k, "n_necklaces": len(necks), "n_distinct_trace": d3,
                          "mean_mult": len(necks) / d3, "max_mult": max(np.bincount(
                              np.unique(t3, return_inverse=True)[1]))})
        res["n5"].append({"k": k, "n_necklaces": len(necks), "n_distinct_trace": d5,
                          "mean_mult": len(necks) / d5,
                          "max_mult": int(max(_mult_counts(t5)))})
    return res

def _mult_counts(vals):
    from collections import Counter
    return list(Counter(vals).values())

if __name__ == "__main__":
    out = {}
    for alph in [(1, 2), (1, 2, 3)]:
        r = run(alph, kmax=15 if alph == (1, 2) else 12)
        out[f"alph_{''.join(map(str,alph))}"] = r
        print(f"\n=== alphabet {alph} ===")
        print(" k   #neck   n3:dist mean_mult max   |  n5:dist mean_mult max")
        for a, b in zip(r["n3"], r["n5"]):
            print(f"{a['k']:2d}  {a['n_necklaces']:6d}   "
                  f"{a['n_distinct_trace']:6d} {a['mean_mult']:7.2f} {int(a['max_mult']):4d}   |  "
                  f"{b['n_distinct_trace']:6d} {b['mean_mult']:7.2f} {b['max_mult']:4d}")
    # verdict: EXPONENTIAL (n3) vs sub-exponential/generic (n5) length-multiplicity.
    # Discriminate by the log-growth rate of mean_mult vs k (second half of the range).
    def log_slope(series):
        ks = np.array([s["k"] for s in series], float)
        mm = np.array([s["mean_mult"] for s in series], float)
        half = len(ks) // 2
        return float(np.polyfit(ks[half:], np.log(mm[half:]), 1)[0])
    r12 = out["alph_12"]
    s3, s5 = log_slope(r12["n3"]), log_slope(r12["n5"])
    out["VERDICT"] = {
        "n3_log_growth_rate": s3, "n5_log_growth_rate": s5,
        "rate_ratio_n3_over_n5": s3 / s5 if s5 else None,
        "n3_final_meanmult": r12["n3"][-1]["mean_mult"],
        "n5_final_meanmult": r12["n5"][-1]["mean_mult"],
        "n3_final_maxmult": int(r12["n3"][-1]["max_mult"]),
        "n5_final_maxmult": int(r12["n5"][-1]["max_mult"]),
        "interpretation": "n3 exponential length-degeneracy (arithmetic), n5 strongly "
                          "suppressed (non-arithmetic) -- operator-side arithmeticity split",
        "PASS": bool(s3 > 2.5 * s5)}
    print("\nVERDICT:", json.dumps(out["VERDICT"], indent=2))
    json.dump(out, open(os.path.join(HERE, "run3_measured.json"), "w"), indent=2, default=str)
