#!/usr/bin/env python3
"""Track-0 §6.iii — iid-seed unfolding residual vs the free-convolution reference, n-scaling gate.

Gate design (Will, 2026-08-10): no quantitative finite-n rate is on the filed rail
(Hoskins–Kabluchko gives convergence, not an error bound), so a fixed residual threshold would be
arbitrary or silently tuned. The gate's authority is EMPIRICAL: run n in {1024, 2048, 4096} and
require the residual to SHRINK WITH n AT EVERY SAMPLED s — monotone n-scaling, logged as the
artifact. A fixed number rides along as a sanity ceiling only. If the adversarial lit pull later
surfaces a quantitative theorem, the measured scaling gets compared against it, not replaced.

Reference: EMPIRICAL seed measure (scope §4 v1.2) — mu_s = D_{1-s}(mu_emp^boxplus 1/(1-s)) via
Belinschi–Bercovici subordination (free_conv.py, closed-form-gated). The population-law
(Uniform[-1,1], G = (1/2)log((z+1)/(z-1))) reference rides along as a logged DIAGNOSTIC, not a gate.

Wiring notes (Will): eps is tied to the FLOWED local spacing per s (support shrinks by (1-s); a
seed-calibrated eps would be relatively fine late exactly where the readout matters) — the
eps-doubling check still runs but shouldn't be spent on a bad eps choice. Subordination iteration
counts are logged per (s, n): if the empirical measure drives the subordinator materially slower
than the smooth gates did, the jitter-floor run needs to know before inheriting the cost.
"""
import json, time
import numpy as np
from track0_harness import diff_step, bulk_idx, rtilde, sigma2, GateFail, \
    BULK_FRACTION, MIN_WINDOWED_SPACINGS, SIGMA2_LS
from free_conv import F_empirical, flow_density

# ---- declared constants ----
NS = [1024, 2048, 4096]
S_SAMPLES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]   # first point >> 1/n (atoms gone)
RNG_SEED = 0
EPS_FRAC = 0.5             # eps = EPS_FRAC * (flowed support width)/m  — flowed local spacing
GRID_PTS = 4001
GRID_PAD = 0.05            # grid extends 5% of width beyond the flowed roots
SANITY_CEILING = 0.05      # KS at n=4096 must sit below this (rides along; NOT the gate)


def F_uniform(w):
    """F = 1/G for Uniform[-1,1]: G(z) = (1/2) log((z+1)/(z-1)) (principal log, Im w > 0)."""
    return 2.0 / np.log((w + 1.0) / (w - 1.0))


def reference_cdf(F_seed, roots_flowed, s, m):
    """Reference CDF of mu_s on a grid spanning the flowed roots; returns (cdf at roots, diag)."""
    lo, hi = roots_flowed[0], roots_flowed[-1]
    w = hi - lo
    xg = np.linspace(lo - GRID_PAD * w, hi + GRID_PAD * w, GRID_PTS)
    eps = EPS_FRAC * w / m
    rho1, res1, it1 = flow_density(F_seed, xg, s, eps)
    rho2, _, _ = flow_density(F_seed, xg, s, 2.0 * eps)
    eps_dev = float(np.max(np.abs(rho1 - rho2)))
    rho = np.maximum(rho1, 0.0)
    cdf = np.concatenate([[0.0], np.cumsum(0.5 * (rho[1:] + rho[:-1]) * np.diff(xg))])
    mass = float(cdf[-1])
    cdf /= mass                                   # normalized; defect logged, not hidden
    F_at = np.interp(roots_flowed, xg, cdf)
    return F_at, {"eps": eps, "eps_double_dev": eps_dev, "mass_defect": abs(1.0 - mass),
                  "sub_residual": res1, "sub_iters": it1}


def ks_stat(F_at):
    m = len(F_at)
    i = np.arange(1, m + 1)
    return float(np.max(np.maximum(np.abs(i / m - F_at), np.abs(F_at - (i - 1) / m))))


def run():
    t0 = time.time()
    rng = np.random.default_rng(RNG_SEED)
    out = {"constants": {"NS": NS, "S_SAMPLES": S_SAMPLES, "RNG_SEED": RNG_SEED,
                         "EPS_FRAC": EPS_FRAC, "GRID_PTS": GRID_PTS, "GRID_PAD": GRID_PAD,
                         "SANITY_CEILING": SANITY_CEILING, "BULK_FRACTION": BULK_FRACTION},
           "runs": {}, "verdict": "PASS", "failures": []}
    for n in NS:
        seed = np.sort(rng.uniform(-1.0, 1.0, n))
        F_seed = F_empirical(seed)
        targets = {int(round(s * n)): s for s in S_SAMPLES}
        r = seed.copy()
        recs = []
        t_n = time.time()
        for k in range(1, max(targets) + 1):
            r = diff_step(r)
            if k not in targets:
                continue
            s = targets[k]
            m = n - k
            F_at, diag = reference_cdf(F_seed, r, s, m)
            d_emp = ks_stat(F_at)
            F_at_pop, diag_pop = reference_cdf(F_uniform, r, s, m)
            d_pop = ks_stat(F_at_pop)
            u = F_at * m
            bi = bulk_idx(m)
            du = np.diff(u[bi])
            rt = rtilde(du) if len(du) > 2 else None
            recs.append({"s": s, "k": k, "m": m, "ks_empirical_ref": d_emp,
                         "ks_population_ref_DIAGNOSTIC": d_pop,
                         "bulk_mean_spacing_dev": abs(float(np.mean(du)) - 1.0),
                         "windowed_spacings": len(du),
                         "readout_powered": len(du) >= MIN_WINDOWED_SPACINGS,
                         "rtilde_bulk": rt, "one_minus_rtilde": (1.0 - rt) if rt else None,
                         "sigma2": {str(L): sigma2(u[bi], L) for L in SIGMA2_LS},
                         **{k2: v for k2, v in diag.items()}})
            print(f"n={n} s={s:.1f} m={m}: KS_emp={d_emp:.5f} KS_pop={d_pop:.5f} "
                  f"iters={diag['sub_iters']} eps_dbl={diag['eps_double_dev']:.2e}", flush=True)
        out["runs"][str(n)] = {"flow_runtime_s": round(time.time() - t_n, 1), "steps": recs}
    # ---- the gate: monotone n-scaling of the empirical-reference residual at every sampled s ----
    for s in S_SAMPLES:
        ds = [next(x["ks_empirical_ref"] for x in out["runs"][str(n)]["steps"] if x["s"] == s)
              for n in NS]
        if not all(ds[i] > ds[i + 1] for i in range(len(ds) - 1)):
            out["verdict"] = "FAIL"
            out["failures"].append(f"s={s}: KS not monotone in n: {[f'{d:.5f}' for d in ds]}")
        if ds[-1] > SANITY_CEILING:
            out["verdict"] = "FAIL"
            out["failures"].append(f"s={s}: KS at n={NS[-1]} = {ds[-1]:.4f} > ceiling")
    out["runtime_s"] = round(time.time() - t0, 1)
    with open("derivflow/track0_iid_scaling.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"\nVERDICT: {out['verdict']}  (runtime {out['runtime_s']}s)")
    for s in S_SAMPLES:
        ds = [next(x["ks_empirical_ref"] for x in out["runs"][str(n)]["steps"] if x["s"] == s)
              for n in NS]
        dp = next(x["ks_population_ref_DIAGNOSTIC"] for x in out["runs"][str(NS[-1])]["steps"]
                  if x["s"] == s)
        print(f"s={s:.1f}: KS_emp " + " -> ".join(f"{d:.5f}" for d in ds) +
              f"   (pop-ref diag at n={NS[-1]}: {dp:.5f})")
    for msg in out["failures"]:
        print("  FAIL:", msg)
    return out["verdict"]


if __name__ == "__main__":
    import sys, os
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, "derivflow")
    sys.exit(0 if run() == "PASS" else 1)
