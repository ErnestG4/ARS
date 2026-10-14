"""Route (a) data-free sensitivity split (forty-third round, Will, 2026-10-14): how much of the declared statistic's
prediction comes from the n ≥ 3 correlations. No F3 file is decoded; no zero data is read.

The tagged prediction (route_a_zeta.json, n ≤ 5) is Δp = Δ₂ − Δ₃ + Δ₄ + Δ₅ at the Chebyshev nodes, Δ_n = T_n^ζ − T_n^sine
(route_a_zeta's terms, stored per node in results/route_a_raw/route_a_zeta/; Δ₅ as included, check_c.delta5_included).
Models, as truths for the read's own estimator (route_a_read.MuFit on the tagged Δp, i.e. μ = 1 is the n ≤ 5 law):
    (i)   n = 2 only, higher orders from the sine kernel:  p = p_sine + Δ₂
    (ii)  full n ≤ 5:                                       p = p_sine + Δp        (gate: μ* = the committed
          route_a_equiv.json "prediction (μ = 1 check)" value to 1e-9 — the same code path — and |μ* − 1| ≤ 1e-4; that
          integrator's own offset is 3–5e-5, from its trapezoid score against the window grid's φ)
    (and for information the cumulative n ≤ 3, n ≤ 4 truncations)
μ-equivalent μ* = the estimator's infinite-sample limit (route_a_equiv.expected_mu), per file and pooled with the read's
weights w_f. Reported against the PASS band half-width 2·SE_pool + δμ_sys with SE_f at its floor SD_f·(1 + 1/R)^{1/2}
from the declared calibration (the read's bootstrap can only widen it), and against the ±0.015 quoted in the round.
Round 43's reading: if |μ*_pool(i) − 1| < 0.25 × band, the seal records that route (a) tests two-point structure only.

  python route_a_split.py [OUT.json]
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import route_a_equiv as EQ  # noqa: E402
import route_a_read as RR  # noqa: E402
import route_a_zeta as RZ  # noqa: E402

RAW = os.path.join(HERE, "results", "route_a_raw", "route_a_zeta")
BAND_QUOTED = 0.015
FRACTION = 0.25


def term_deltas(f):
    """Δ₂, −Δ₃, +Δ₄ at the nodes (s = 0 prepended as 0), from the stored rows exactly as route_a_zeta.merge reads them."""
    uniq = {}
    for fn in sorted(os.listdir(RAW)):
        if fn.startswith("terms_c") and fn.endswith(".jsonl"):
            for line in open(os.path.join(RAW, fn)):
                r = json.loads(line)
                uniq.setdefault((r["file"], r["which"], r["pmax"], r["m"], r["s"]), r)
    by_s = {k[4]: RZ.apply_skip(r) for k, r in uniq.items() if k[:4] == (f, "mean", RZ.PMAX_MAIN, RZ.M_QUAD)}
    out = {k: [0.0] for k in ("T2", "T3", "T4")}
    for s in RZ.NODES[1:]:
        r = by_s[float(s)]
        for k, sign in (("T2", 1), ("T3", -1), ("T4", 1)):
            out[k].append(sign * (r["zeta"][k] - r["sine"][k]))
    return {k: np.array(v) for k, v in out.items()}


def main(out=None):
    pred = json.load(open(RR.PRED))
    cal = RR.calib()
    w, _ = RR.weights()
    eqv = json.load(open(os.path.join(HERE, "results", "route_a_equiv.json")))["files"]
    res = dict(round="forty-third", files={}, definition=__doc__.split("\n\n")[1])
    eq_err = 0.0
    gate_err = 0.0
    se2 = 0.0
    for f in RR.F3:
        v = pred["files"][f]
        D = term_deltas(f)
        d5 = np.array(v["check_c"]["delta5_included"])
        full = np.array(v["dp_nodes"])
        recon = D["T2"] + D["T3"] + D["T4"] + d5
        err = float(np.max(np.abs(recon - full)))
        gate_err = max(gate_err, err)
        models = {"n2_sine_higher": D["T2"], "n_le_3": D["T2"] + D["T3"], "n_le_4": D["T2"] + D["T3"] + D["T4"],
                  "n_le_5_full": full}
        fit = RR.MuFit(full)
        _, nf = RR.weights()
        row = dict(reconstruction_max_abs=err, mu_star={}, gof_noncentrality={},
                   max_abs_node={k: float(np.max(np.abs(m))) for k, m in models.items()})
        for k, m in models.items():
            p = (lambda dn: (lambda s: RR.p_sine()(np.maximum(np.asarray(s, float), RR.S_TINY))
                             + RR.cheb_interp(dn, np.maximum(np.asarray(s, float), RR.S_TINY))))(m)
            mu = EQ.expected_mu(fit, p)
            row["mu_star"][k] = mu
            row["gof_noncentrality"][k] = EQ.noncentrality(fit, p, mu, nf[f])
        eq_err = max(eq_err, abs(row["mu_star"]["n_le_5_full"] - eqv[f]["mu"]["prediction (μ = 1 check)"]))
        c = cal["files"][f]
        se_f = c["sd"] * math.sqrt(1 + 1 / c["R"])
        se2 += w[f] ** 2 * se_f ** 2
        row["se_floor"] = se_f
        res["files"][f] = row
        print(f"{f}: recon {err:.1e}  μ* n=2 {row['mu_star']['n2_sine_higher']:.5f}  n≤3 {row['mu_star']['n_le_3']:.5f}  "
              f"n≤4 {row['mu_star']['n_le_4']:.5f}  n≤5 {row['mu_star']['n_le_5_full']:.6f}  "
              f"GoF nc(n=2) {row['gof_noncentrality']['n2_sine_higher']:.2f}", flush=True)
    se_pool = math.sqrt(se2)
    band = 2 * se_pool + RR.DMU_SYS
    pool = {k: float(sum(w[f] * res["files"][f]["mu_star"][k] for f in RR.F3)) for k in res["files"][f]["mu_star"]}
    shift = pool["n_le_5_full"] - pool["n2_sine_higher"]
    gate_ok = bool(gate_err <= 1e-12 and eq_err <= 1e-9 and abs(pool["n_le_5_full"] - 1) <= 1e-4)
    res.update(weights=w, gate=dict(reconstruction_max_abs=gate_err, full_vs_committed_equiv=eq_err,
                                    full_mu_star_pool=pool["n_le_5_full"], PASS=gate_ok),
               mu_star_pool=pool, se_pool_floor=se_pool, band_half_width=band, band_quoted=BAND_QUOTED,
               shift_n_ge_3=shift, shift_over_band=abs(shift) / band, shift_over_band_quoted=abs(shift) / BAND_QUOTED,
               fraction=FRACTION,
               two_point_only=bool(gate_ok and abs(shift) < FRACTION * band and abs(shift) < FRACTION * BAND_QUOTED))
    print(f"gate (Δp reconstruction ≤ 1e-12; full μ* = committed equiv check ≤ 1e-9; |μ*_pool − 1| ≤ 1e-4): "
          f"{'PASS' if gate_ok else 'FAIL'} (recon {gate_err:.1e}, vs equiv {eq_err:.1e}, μ*_pool {pool['n_le_5_full']:.8f})")
    print(f"pooled μ*: " + "  ".join(f"{k} {x:.5f}" for k, x in pool.items()))
    print(f"band half-width 2·SE_pool + δμ_sys = {band:.5f} (SE_pool floor {se_pool:.5f}); quoted ±{BAND_QUOTED}")
    print(f"n ≥ 3 shift {shift:+.5f} = {abs(shift) / band:.3f} band ({abs(shift) / BAND_QUOTED:.3f} of ±0.015); "
          f"threshold {FRACTION} → two-point only: {res['two_point_only']}")
    if out:
        json.dump(res, open(out, "w"), indent=1)
    return 0 if gate_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
