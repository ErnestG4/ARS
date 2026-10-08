"""Phase 2, low heights (N_eff < 2): DESCRIPTIVE ONLY, outside the expansion's validity (seal §3; Will, tenth round).
No verdicts, no gates. zeros6 (sha256 checked) in bins of unit width in log(E/2π) below 8.69; exact-θ unfolding; both
families fitted with the sealed estimator (window s ≤ 2.0); moving-block bootstrap SD (block 10·⌈N_eff⌉); fit flags and
the model's positivity c-range reported, because the first-order family barely remains a density this low.
Writes results/lowheight/lowheight.json and LOWHEIGHT.md."""
import json
import math
import os

import numpy as np

import ph2lib as P
import preread as R
import run

L_EDGES = [3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.69]
OUT = os.path.join(R.RES, "lowheight")


def main():
    import mpmath as mp
    path = run.SOURCES["zeros6"]
    if run._hash(path, "sha256") != json.load(open(run.SEAL))["data"]["sha256"]["zeros6"]:
        raise SystemExit("REFUSED: zeros6 hash mismatch")
    lo_all, hi_all = R.TWO_PI * math.exp(L_EDGES[0]), R.TWO_PI * math.exp(L_EDGES[-1])
    with mp.workdps(run.DPS):
        g = [mp.mpf(line.strip()) for line in open(path) if lo_all <= float(line) < hi_all]
    gf = np.array([float(x) for x in g])
    Mp, Ms = P.Model(), P.Model(abar_grid=P.SECONDARY_ABAR_GRID)
    Wp, Ws = P.WindowFit(Mp), P.WindowFit(Ms)
    rng = np.random.default_rng(20261008)
    rows = []
    for L0, L1 in zip(L_EDGES[:-1], L_EDGES[1:]):
        idx = np.nonzero((gf >= R.TWO_PI * math.exp(L0)) & (gf < R.TWO_PI * math.exp(L1)))[0]
        gb = [g[i] for i in idx]
        s = P.unfolded_spacings(gb, dps=run.DPS)
        mid = 0.5 * (gf[idx][1:] + gf[idx][:-1])
        Lk = np.log(mid / R.TWO_PI)
        Neff, ab = R.neff_of_L(Lk), R.abar_of_L(Lk)
        Lb = 10 * int(math.ceil(float(np.median(Neff))))
        r = dict(L=[L0, L1], n=len(s), N_eff=[float(Neff.min()), float(np.median(Neff)), float(Neff.max())],
                 abar_median=float(np.median(ab)), mean_spacing=float(s.mean()), block=Lb)
        for arm, W, abar in (("prim", Wp, None), ("sec", Ws, ab)):
            prep = W.prepare(s, Neff, abar)
            c, flag = W.fit(prep)
            bs, _ = P.block_bootstrap_c_series(W, prep, c, Lb, 200, rng)
            sd_c = float(np.std(bs, ddof=1))
            cr = W.c_range(float(Neff.min()), abars=None if abar is None else (float(ab.min()), float(ab.max())))
            r[arm] = dict(c=c, flag=flag, kappa=P.kappa_from_c(c), boot_sd_c=sd_c,
                          c_interval=[c - R.Z95 * sd_c, c + R.Z95 * sd_c], c_range=list(cr))
        rows.append(r)
        print(json.dumps(r, default=float), flush=True)
    os.makedirs(OUT, exist_ok=True)
    json.dump(dict(note="DESCRIPTIVE ONLY: N_eff < 2, outside the expansion's validity; no verdicts", rows=rows),
              open(os.path.join(OUT, "lowheight.json"), "w"), indent=1, default=float)
    kfmt = lambda c: "∞" if c <= 0 else f"{1 / math.sqrt(c):.3f}"
    md = ["# Phase 2 low heights — DESCRIPTIVE ONLY (N_eff < 2: outside the expansion's validity; no verdicts)", "",
          "κ̂ = N̂/N_eff from the sealed estimator (window s ≤ 2.0). 'at_hi' = the fit sits on the model's positivity "
          "bound (the first-order family stops being a density for larger c), so κ̂ there is a bound, not an estimate.", "",
          "| log(E/2π) | zeros | N_eff (median) | PRIMARY κ̂ (95% from c ± 1.96·SD) | flag | SECONDARY κ̂ (95%) | flag | positivity c-range prim / sec |",
          "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        p, q = r["prim"], r["sec"]
        md.append(f"| {r['L'][0]}–{r['L'][1]} | {r['n']:,} | {r['N_eff'][1]:.3f} |"
                  f" {p['kappa']:.3f} [{kfmt(p['c_interval'][1])}, {kfmt(p['c_interval'][0])}] | {p['flag']} |"
                  f" {q['kappa']:.3f} [{kfmt(q['c_interval'][1])}, {kfmt(q['c_interval'][0])}] | {q['flag']} |"
                  f" ≤ {p['c_range'][1]:.2f} / ≤ {q['c_range'][1]:.2f} |")
    open(os.path.join(OUT, "LOWHEIGHT.md"), "w").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
