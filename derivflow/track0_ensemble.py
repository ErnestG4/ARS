#!/usr/bin/env python3
"""Track-0 §6.iv-b — realization ensemble. NOT A GATE: the error bar (scope v1.4;
seals/RATE_QUESTION_SEAL.json design.sigma_source).

16 fresh Uniform[-1,1] draws per n, same pipeline as everything else. The per-k sigma this file
banks is the ONLY sigma the sealed fits and the universality verdict may consume; the §6.iv-a
numerical floor sits ~11 orders below it and must never be quoted in its place.

RNG protocol is the SEAL's, not this file's: SeedSequence(20260811).spawn(96), children 0-47 =
iid replicates, 16 per n ascending. Enumerable in advance; replicate selection impossible.
"""
import json, time
import numpy as np
from track0_harness import diff_step, bulk_idx, rtilde, sigma2
from free_conv import F_empirical
from track0_iid_scaling import reference_cdf

MASTER_SEED = 20260811          # pinned in the seal; do not change here
N_SCIENCE = [1024, 2048, 4096]
K_GRID_FIT = [1, 2, 4, 8, 16, 32, 64]
R = 16


def one_flow(seed_roots, n, label):
    F_seed = F_empirical(seed_roots)
    r = seed_roots.copy()
    rec = {}
    for k in range(1, K_GRID_FIT[-1] + 1):
        r = diff_step(r)
        if k not in K_GRID_FIT:
            continue
        m = n - k
        F_at, diag = reference_cdf(F_seed, r, k / n, m)
        u = F_at * m
        du = np.diff(u[bulk_idx(m)])
        rec[k] = {"one_minus_rtilde": 1.0 - rtilde(du), "sigma2_8": sigma2(u[bulk_idx(m)], 8)}
    print(f"  {label} done", flush=True)
    return rec


def run():
    t0 = time.time()
    children = np.random.SeedSequence(MASTER_SEED).spawn(96)
    out = {"role": "6.iv-b realization ensemble — error bar, NOT a gate; no verdict field by design",
           "seal_ref": "seals/RATE_QUESTION_SEAL.json (rng_protocol, sigma_source)",
           "constants": {"MASTER_SEED": MASTER_SEED, "N_SCIENCE": N_SCIENCE,
                         "K_GRID_FIT": K_GRID_FIT, "R": R},
           "ensembles": {}}
    for ni, n in enumerate(N_SCIENCE):
        reps = []
        for i in range(R):
            child = children[ni * R + i]           # children 0-47: iid, 16 per n ascending
            rng = np.random.default_rng(child)
            seed = np.sort(rng.uniform(-1.0, 1.0, n))
            reps.append(one_flow(seed, n, f"n={n} rep={i}"))
        per_k = {}
        for k in K_GRID_FIT:
            vals = np.array([r[k]["one_minus_rtilde"] for r in reps])
            s2 = np.array([r[k]["sigma2_8"] for r in reps], dtype=float)
            per_k[str(k)] = {"one_minus_rtilde_values": vals.tolist(),
                             "mean": float(np.mean(vals)),
                             "std": float(np.std(vals, ddof=1)),
                             "sigma_mean": float(np.std(vals, ddof=1) / np.sqrt(R)),
                             "sigma2_8_mean": float(np.mean(s2)),
                             "sigma2_8_std": float(np.std(s2, ddof=1))}
        out["ensembles"][str(n)] = per_k
        print(f"n={n}: " + "  ".join(
            f"k={k}:{per_k[str(k)]['mean']:.3e}±{per_k[str(k)]['std']:.1e}" for k in K_GRID_FIT),
            flush=True)
    out["runtime_s"] = round(time.time() - t0, 1)
    with open("derivflow/track0_ensemble.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"done in {out['runtime_s']}s -> derivflow/track0_ensemble.json")


if __name__ == "__main__":
    run()
