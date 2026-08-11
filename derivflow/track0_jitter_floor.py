#!/usr/bin/env python3
"""Track-0 §6.iv-a — numerical jitter floor. A GATE (scope v1.4; §6.iv-b, the error bar, is
a separate instrument and is NOT run here).

Design: iid position jitter delta * (local spacing) on the seed, replicated flows, spread of
unfolded readouts per k on the small-k grid — the action window per §6.iii's ceiling finding,
and the cheap window (kappa ~ 1). Downstream extension is theorem-side: the derivative-root map
is globally ell-infinity non-expansive (dx*/dr_j are positive convex weights summing to 1 along
any segment of sorted root vectors => Lipschitz-1 per step), so the floor measured here
upper-bounds every later k. That lemma is itself GATED below (transfer ratio), not assumed.

Declared gates (scope §6.iv-a, filed before this run):
  (i)  position transfer ratio ||dx(k)||_inf / ||dx(0)||_inf <= 1.02 at every k,
       for delta in {1e-10, 1e-8} (theorem-exact <= 1; slack = solver noise; at delta = 1e-12
       the ratio is LOGGED ONLY — solver accuracy 1.35e-13 is a nontrivial fraction of delta).
  (ii) readout floor-vs-signal at delta = 1e-12: for every k with unperturbed 1 - rtilde > 1e-3,
       replicate spread < 1% of signal; at-ceiling k rows require spread < 1e-7 absolute.
  (iii) no super-linear amplification: log-log slope of spread vs delta over the top two
       decades <= 1.3.
"""
import json, time
import numpy as np
from track0_harness import diff_step, bulk_idx, rtilde, sigma2, SIGMA2_LS
from free_conv import F_empirical, flow_density
from track0_iid_scaling import reference_cdf, RNG_SEED

# ---- declared constants ----
N_SEED = 4096
K_GRID = [1, 2, 4, 8, 16, 32, 64]
DELTAS = [1e-12, 1e-10, 1e-8]
R_REP = 6
TRANSFER_TOL = 1.02
TRANSFER_GATE_DELTAS = [1e-10, 1e-8]
FLOOR_SIGNAL_MIN = 1e-3      # k counts as "in the fit window" when unperturbed 1-rtilde exceeds this
FLOOR_RATIO_TOL = 0.01
CEILING_ABS_TOL = 1e-7
AMP_SLOPE_TOL = 1.3
JITTER_RNG_SEED = 1          # independent of the seed-draw RNG


def flow_readouts(seed_roots, label):
    """Run the flow to max(K_GRID); return per-k readouts and flowed positions at each k."""
    F_seed = F_empirical(seed_roots)
    r = seed_roots.copy()
    out = {}
    for k in range(1, K_GRID[-1] + 1):
        r = diff_step(r)
        if k not in K_GRID:
            continue
        m = N_SEED - k
        s = k / N_SEED
        F_at, diag = reference_cdf(F_seed, r, s, m)
        u = F_at * m
        bi = bulk_idx(m)
        du = np.diff(u[bi])
        out[k] = {"positions": r.copy(), "one_minus_rtilde": 1.0 - rtilde(du),
                  "sigma2_8": sigma2(u[bi], 8), "sub_iters": diag["sub_iters"]}
    print(f"  flow {label} done", flush=True)
    return out


def run():
    t0 = time.time()
    rng_seed_draw = np.random.default_rng(RNG_SEED)
    base_seed = np.sort(rng_seed_draw.uniform(-1.0, 1.0, N_SEED))
    local = np.empty(N_SEED)
    gaps = np.diff(base_seed)
    local[1:-1] = 0.5 * (gaps[:-1] + gaps[1:]); local[0] = gaps[0]; local[-1] = gaps[-1]

    base = flow_readouts(base_seed, "base")
    jr = np.random.default_rng(JITTER_RNG_SEED)
    reps = {d: [] for d in DELTAS}
    for d in DELTAS:
        for i in range(R_REP):
            pert = np.sort(base_seed + d * local * jr.standard_normal(N_SEED))
            delta0 = float(np.max(np.abs(pert - base_seed)))
            rr = flow_readouts(pert, f"delta={d:.0e} rep={i}")
            for k in K_GRID:
                rr[k]["transfer"] = float(np.max(np.abs(rr[k]["positions"] - base[k]["positions"]))) / delta0
            reps[d].append(rr)

    verdict, failures, rows = "PASS", [], []
    for k in K_GRID:
        sig = base[k]["one_minus_rtilde"]
        row = {"k": k, "s": k / N_SEED, "unpert_one_minus_rtilde": sig,
               "unpert_sigma2_8": base[k]["sigma2_8"], "sub_iters": base[k]["sub_iters"]}
        for d in DELTAS:
            vals = [r[k]["one_minus_rtilde"] for r in reps[d]]
            tr = max(r[k]["transfer"] for r in reps[d])
            row[f"spread_{d:.0e}"] = float(np.std(vals, ddof=1))
            row[f"transfer_max_{d:.0e}"] = tr
            if d in TRANSFER_GATE_DELTAS and tr > TRANSFER_TOL:
                verdict = "FAIL"; failures.append(f"k={k} delta={d:.0e}: transfer {tr:.4f} > {TRANSFER_TOL}")
        sp12 = row["spread_1e-12"]
        row["in_fit_window"] = sig > FLOOR_SIGNAL_MIN
        if row["in_fit_window"]:
            row["floor_ratio"] = sp12 / sig
            if sp12 > FLOOR_RATIO_TOL * sig:
                verdict = "FAIL"; failures.append(f"k={k}: spread@1e-12 {sp12:.3g} > 1% of signal {sig:.3g}")
        else:
            if sp12 > CEILING_ABS_TOL:
                verdict = "FAIL"; failures.append(f"k={k} (at-ceiling): spread@1e-12 {sp12:.3g} > {CEILING_ABS_TOL}")
        ampl = np.log10(row["spread_1e-08"] / row["spread_1e-10"]) / 2.0 if row["spread_1e-10"] > 0 else None
        row["amp_slope_top2dec"] = ampl
        if ampl is not None and ampl > AMP_SLOPE_TOL:
            verdict = "FAIL"; failures.append(f"k={k}: amplification slope {ampl:.2f} > {AMP_SLOPE_TOL}")
        rows.append(row)

    out = {"gate": "6iv-a numerical jitter floor", "scope": "TRACK0_SCOPE.md v1.4",
           "constants": {"N_SEED": N_SEED, "K_GRID": K_GRID, "DELTAS": DELTAS, "R_REP": R_REP,
                         "TRANSFER_TOL": TRANSFER_TOL, "TRANSFER_GATE_DELTAS": TRANSFER_GATE_DELTAS,
                         "FLOOR_SIGNAL_MIN": FLOOR_SIGNAL_MIN, "FLOOR_RATIO_TOL": FLOOR_RATIO_TOL,
                         "CEILING_ABS_TOL": CEILING_ABS_TOL, "AMP_SLOPE_TOL": AMP_SLOPE_TOL,
                         "RNG_SEED": RNG_SEED, "JITTER_RNG_SEED": JITTER_RNG_SEED},
           "verdict": verdict, "failures": failures, "rows": rows,
           "runtime_s": round(time.time() - t0, 1)}
    with open("derivflow/track0_jitter_floor.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"\nVERDICT: {verdict}  (runtime {out['runtime_s']}s)")
    for row in rows:
        print(f"k={row['k']:3d}: 1-rt={row['unpert_one_minus_rtilde']:.3e} "
              f"spread@1e-12={row['spread_1e-12']:.2e} @1e-10={row['spread_1e-10']:.2e} "
              f"@1e-08={row['spread_1e-08']:.2e} transfer_max={row['transfer_max_1e-08']:.4f} "
              f"amp={row['amp_slope_top2dec'] if row['amp_slope_top2dec'] is None else round(row['amp_slope_top2dec'],2)} "
              f"{'FIT' if row['in_fit_window'] else 'ceiling'}")
    for msg in failures:
        print("  FAIL:", msg)
    return verdict


if __name__ == "__main__":
    import sys
    sys.exit(0 if run() == "PASS" else 1)
