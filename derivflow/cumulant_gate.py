#!/usr/bin/env python3
"""Finite-free-probability invariant gate — an independent check on the root flow.

SOURCE.  Arizmendi, Fujie, Perales, Ueda, "S-transform in Finite Free Probability",
arXiv:2408.09337, Lemma 3.2:

    with  d_{k|d} p := p^(d-k) / (d)_{d-k}   (monic, degree k),
          e~_j^{(k)}( d_{k|d} p )  =  e~_j^{(d)}( p )     for 1 <= j <= k <= d,

where the normalized coefficients are defined by writing
    p(x) = sum_k (-1)^k C(d,k) e~_k^{(d)}(p) x^{d-k},
i.e.  e~_j = e_j(roots) / C(d,j)  with e_j the elementary symmetric polynomial.

So along OUR flow, at every step, with m = n - k remaining roots:

    e_j(roots_k) / C(m,j)   ==   e_j(seed) / C(n,j)      EXACTLY, for all j <= m.

Why this is worth having.  Every gate the project already owns tests the readout
(Hermite self-map, lattice, free-convolution evaluator).  This one tests the FLOW
itself against machinery built by other people for other reasons, and it is exact
rather than asymptotic: no unfolding, no reference density, no tolerance chosen by
us.  Normalization is a constant multiple, so it does not move roots; the invariant
is a statement about the root set alone.

It certifies the GLOBAL layer only.  Two configurations with identical normalized
coefficients can have completely different local spacing, which is exactly why this
gate cannot be turned into a local result — see the derivability memo.

Reached via a reference supplied by A. Campbell (corr. 2026-08-17).
Exploratory, unsealed; no RNG of its own beyond the seeds it builds.
"""
import json
import os
import sys
import time

import numpy as np
from scipy.special import roots_hermite

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from track0_harness import diff_step                    # noqa: E402

JMAX = 4                 # e~_1..e~_4; higher j loses conditioning at these degrees
KS = [1, 2, 4, 8, 16, 32, 64]
NS = [1024, 4096]


def e_tilde(roots, jmax=JMAX):
    """e~_j = e_j(roots)/C(d,j) for j=1..jmax, via Newton's identities on power
    sums.  Returned already normalized, so the values stay O(1)-ish instead of
    overflowing through the binomial."""
    d = len(roots)
    p = [None] + [float(np.sum(roots ** k)) for k in range(1, jmax + 1)]
    e = [1.0]
    for j in range(1, jmax + 1):
        acc = 0.0
        for i in range(1, j + 1):
            acc += (-1) ** (i - 1) * e[j - i] * p[i]
        e.append(acc / j)
    out, binom = [], 1.0
    for j in range(1, jmax + 1):
        binom *= (d - j + 1) / j          # C(d,j) built incrementally
        out.append(e[j] / binom)
    return np.array(out)


def run():
    out = {"gate": "finite free coefficient invariance (AFPU 2408.09337 Lemma 3.2)",
           "jmax": JMAX, "ks": KS, "ns": NS, "rows": [], "verdict": None}
    t0 = time.time()
    worst = 0.0
    rng = np.random.default_rng(20260818)

    for n in NS:
        seeds = {
            "iid":      np.sort(rng.uniform(-1.0, 1.0, n)),
            "hermite":  roots_hermite(n)[0],
            "lattice":  np.linspace(-1.0, 1.0, n),
        }
        for name, seed in seeds.items():
            ref = e_tilde(seed)
            r = seed.copy()
            for k in range(1, max(KS) + 1):
                r = diff_step(r)
                if k not in KS:
                    continue
                cur = e_tilde(r)
                # scale-free residual: |difference| against the size of the invariant
                scale = np.maximum(np.abs(ref), np.max(np.abs(ref)) * 1e-3)
                rel = np.abs(cur - ref) / scale
                worst = max(worst, float(np.max(rel)))
                out["rows"].append({"n": n, "seed": name, "k": k,
                                    "e_tilde_seed": ref.tolist(),
                                    "e_tilde_flowed": cur.tolist(),
                                    "rel_residual": rel.tolist(),
                                    "worst_rel": float(np.max(rel))})
                print(f"  n={n:<5d} {name:8s} k={k:<3d} worst rel residual "
                      f"{np.max(rel):.3e}", flush=True)

    out["worst_rel_residual"] = worst
    out["verdict"] = "PASS" if worst < 1e-9 else "FAIL"
    out["runtime_s"] = round(time.time() - t0, 1)
    with open(os.path.join(_HERE, "cumulant_gate.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"\nVERDICT: {out['verdict']}  worst relative residual "
          f"{worst:.3e}  ({out['runtime_s']:.0f}s)")
    return out


if __name__ == "__main__":
    sys.exit(0 if run()["verdict"] == "PASS" else 1)
