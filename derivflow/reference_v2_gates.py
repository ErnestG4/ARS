#!/usr/bin/env python3
"""v1.5 reference known-answer gates (scope §4 v1.5) — run green BEFORE anything consumes the
corrected instrument; re-run on any future reference change.

Gate L (maximally rippled input): picket-fence k = 1 through the FULL corrected path must read
1 - <rtilde> <= 1e-7 at n in {1024, 2048, 4096} (true value <= 1e-8, Step 1 standalone).

Gate H (maximally smooth input): Hermite seed k in {1, 2} at n = 4096 through the full corrected
EMPIRICAL-reference path, gated against the exact H_{n-k} truth (exact roots, exact semicircle
unfolding, same window) at |diff| <= 1e-5. Certifies the reference on smooth density at exactly
the k's under review — the original Hermite gate never exercised reference_cdf.
"""
import json
import numpy as np
from scipy.special import roots_hermite
from track0_harness import diff_step, bulk_idx, rtilde, unfold_semicircle
from free_conv import F_empirical
from track0_iid_scaling import reference_cdf

LATTICE_NS = [1024, 2048, 4096]
LATTICE_TOL = 1e-7
HERMITE_N = 4096
HERMITE_KS = [1, 2]
HERMITE_TOL = 1e-5


def pipeline_rt(seed, r, k, n):
    m = n - k
    F_at, diag = reference_cdf(F_empirical(seed), r, k / n, m)
    u = F_at * m
    return 1.0 - rtilde(np.diff(u[bulk_idx(m)])), diag


def run():
    out = {"gate": "reference v1.5 known-answers", "verdict": "PASS", "rows": [], "failures": []}

    for n in LATTICE_NS:
        seed = np.linspace(-1.0, 1.0, n)
        r = diff_step(seed)
        val, diag = pipeline_rt(seed, r, 1, n)
        row = {"gate": "L", "n": n, "k": 1, "value": val, "tol": LATTICE_TOL,
               "eps": diag["eps"], "sub_iters": diag["sub_iters"]}
        out["rows"].append(row)
        print(f"L n={n}: 1-rt={val:.3e} (tol {LATTICE_TOL:.0e})", flush=True)
        if val > LATTICE_TOL:
            out["verdict"] = "FAIL"
            out["failures"].append(f"lattice n={n}: {val:.3e} > {LATTICE_TOL}")

    n = HERMITE_N
    seed = roots_hermite(n)[0]
    r = seed.copy()
    for k in range(1, max(HERMITE_KS) + 1):
        r = diff_step(r)
        if k not in HERMITE_KS:
            continue
        m = n - k
        val, diag = pipeline_rt(seed, r, k, n)
        exact_roots = roots_hermite(m)[0]
        u_exact = unfold_semicircle(exact_roots, m)
        truth = 1.0 - rtilde(np.diff(u_exact[bulk_idx(m)]))
        diff = abs(val - truth)
        row = {"gate": "H", "n": n, "k": k, "pipeline": val, "exact_truth": truth,
               "abs_diff": diff, "tol": HERMITE_TOL, "sub_iters": diag["sub_iters"]}
        out["rows"].append(row)
        print(f"H k={k}: pipeline={val:.3e} truth={truth:.3e} |diff|={diff:.3e} (tol {HERMITE_TOL:.0e})",
              flush=True)
        if diff > HERMITE_TOL:
            out["verdict"] = "FAIL"
            out["failures"].append(f"hermite k={k}: |diff| {diff:.3e} > {HERMITE_TOL}")

    with open("derivflow/reference_v2_gates.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"VERDICT: {out['verdict']}")
    for msg in out["failures"]:
        print("  FAIL:", msg)
    return out["verdict"]


if __name__ == "__main__":
    import sys
    sys.exit(0 if run() == "PASS" else 1)
