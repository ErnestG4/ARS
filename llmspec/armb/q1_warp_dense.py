"""Q1 E4 licence re-run for A2 on its amended DENSE grid (B1a-A8: every 10 steps over 1000-2200), Will 09-28. Synthetic
only; runs on spot. Identical to q1_warp.main (same shapes, noise, draws = 500, r* grid, SEALED criteria incl. the HALFWAY
clause) except that A2's grid and comparison window come from grids.arm_grid("A2"). Output:
results/armb_q1_warp_licence_A2dense.json. Also reports, per cell, the licence verdict WITHOUT the HALFWAY clause as a
DESCRIPTIVE diagnostic (the HALFWAY confuser coincides with the LR_INT map after both warmups end; see the 09-28 report)
-- that diagnostic changes nothing sealed."""
import json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import q1_warp as W  # noqa: E402
import q1_licence as QL  # noqa: E402
from grids import arm_grid  # noqa: E402

OUT = ROOT / "results" / "armb_q1_warp_licence_A2dense.json"
GA2 = np.array(arm_grid("A2"), float)


def window_dense(X):
    g = GA2; ok = (g >= 300) & (g <= W.STOP[X])
    for m in W.MODELS:
        tm = W.tau(g, X, m); ok &= (tm >= 0) & (tm <= W.STOP["A0"])
    return g[ok]


W.window = window_dense                                            # decide() looks the window up through W.window


def main():
    rng = np.random.default_rng(W.SEED + 1); res = {"doc": __doc__, "grid_A2_n": len(GA2), "window_A2_n": len(window_dense("A2")), "cells": {}}
    g0 = QL.grid(W.STOP["A0"]); names = [n for n, _ in W.base_curves(g0)]; X, gX = "A2", GA2
    for s in (0.005, 0.01, 0.02, 0.05):
        for ar in (False, True):
            recs = []
            for d in range(W.DRAWS):
                name = names[rng.integers(len(names))]; mstar = ["STEP", "WARMUP", "LR_INT", "HALFWAY"][d % 4]
                b = [0.8, 1.0, 1.25][rng.integers(3)]; a = rng.normal(0, 5)
                y0 = W.gen_curve(name, g0) * (1 + QL.noise(rng, len(g0), 1, s, ar)[0])
                clean = a + b * W.gen_curve(name, np.clip(W.tau(gX, X, mstar), 0, None))
                yX = clean * (1 + QL.noise(rng, len(gX), 1, s, ar)[0])
                _, sse, fr = W.decide(g0, y0, gX, yX, X, 1.0, None); recs.append((mstar, sse, fr))
            c_fit = float(np.quantile([fr for m, _, fr in recs if m != "HALFWAY"], 0.99)); table = {}
            for r in W.R_GRID:
                conf = {m: {} for m in W.MODELS + ["HALFWAY"]}
                for mstar, sse, fr in recs:
                    o = sorted(sse, key=sse.get)
                    dec = "NO_SIMPLE_ANCHOR" if fr > c_fit else (o[0] if sse[o[1]] / max(sse[o[0]], 1e-300) >= r else "INCONCLUSIVE")
                    conf[mstar][dec] = conf[mstar].get(dec, 0) + 1
                conf = {m: {k: v / sum(cc.values()) for k, v in cc.items()} for m, cc in conf.items()}
                table[str(r)] = {"confusion": conf, "max_offdiag": max(conf[m].get(o, 0) for m in W.MODELS for o in W.MODELS if o != m),
                                 "halfway_to_single_model": max(conf["HALFWAY"].get(o, 0) for o in W.MODELS),
                                 "min_diag": min(conf[m].get(m, 0) for m in W.MODELS)}
            ok = [r for r in W.R_GRID if table[str(r)]["max_offdiag"] <= 0.05 and table[str(r)]["halfway_to_single_model"] <= 0.20]
            rs = ok[0] if ok else None
            ok_nh = [r for r in W.R_GRID if table[str(r)]["max_offdiag"] <= 0.05]
            rs_nh = ok_nh[0] if ok_nh else None
            key = f"A2_s{s}_{'ar' if ar else 'iid'}"
            res["cells"][key] = {"c_fit": c_fit, "table": table, "r_star": rs,
                                 "LICENSED": bool(rs is not None and table[str(rs)]["min_diag"] >= 0.80),
                                 "DESCRIPTIVE_without_halfway_clause": {"r_star": rs_nh,
                                     "would_license": bool(rs_nh is not None and table[str(rs_nh)]["min_diag"] >= 0.80)}}
            t = table[str(rs or 1.0)]
            print(key, "LICENSED", res["cells"][key]["LICENSED"], f"diag {t['min_diag']:.2f} offdiag {t['max_offdiag']:.3f} halfway {t['halfway_to_single_model']:.2f}",
                  "| w/o HALFWAY clause:", res["cells"][key]["DESCRIPTIVE_without_halfway_clause"], flush=True)
    OUT.write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
