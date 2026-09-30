"""POST-RESULT, DESCRIPTIVE ONLY (2026-09-30, after Will's review of ARMB_FINDINGS.md). Not sealed; no verdict changes.
Generator for the descriptive numbers added to ARMB_FINDINGS.md in response to that review:
  (a) Q2 wave leave-layer-0-out: the sealed statistic S = rho_Q + rho_K and its exact permutation null, over layers 1-5
      (120^2), from the banked t_half in results/armb_b4_q2.json;
  (b) Q/K layer-mean stable rank at steps 0/512/1000/3000 for A0, M0s1, M0s2 (cache, via b4_analyze);
  (c) bulk VIOLATED count vs the per-cell null exceedance 2*Phi(-2.487), binomial (cells treated as independent,
      which they are not -- adjacent checkpoints are correlated);
  (d) the A1 licence cells and A0's TP_O calibration margin behind "why A1 gives no verdict".
Output: results/armb_b4_post_descriptive.json.
"""
import itertools, json, sys
from pathlib import Path
import numpy as np
from scipy.stats import binom, norm, rankdata

HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
RES = ROOT / "results"


def rho(tv):
    r1 = rankdata(tv); r0 = np.arange(1, len(tv) + 1)
    return float(np.corrcoef(r0, r1)[0, 1]) if np.std(r1) > 0 else 0.0


def wave_sub(th, layers):
    sub = {M: np.array(th[M], float)[layers] for M in ("Q", "K")}
    obs = {M: rho(sub[M]) for M in sub}; S = obs["Q"] + obs["K"]
    perms = list(itertools.permutations(range(len(layers))))
    nq = np.array([rho(sub["Q"][list(p)]) for p in perms]); nk = np.array([rho(sub["K"][list(p)]) for p in perms])
    null = (nq[:, None] + nk[None, :]).ravel()
    return {"rho": obs, "S": S, "p_lower": float((null <= S + 1e-12).mean()), "p_upper": float((null >= S - 1e-12).mean())}


def main():
    import b4_analyze as A
    out = {"doc": __doc__, "wave": {}, "qk_sr": {}, "bulk": {}, "q1_a1": {}}
    q2 = json.loads((RES / "armb_b4_q2.json").read_text())
    for arm in ("A0", "M0s1", "M0s2"):
        th = {M: [np.inf if v is None else v for v in q2[arm]["wave"]["t_half"][M]] for M in ("Q", "K")}
        full = wave_sub(th, list(range(6)))
        assert abs(full["S"] - q2[arm]["wave"]["S"]) < 1e-9, "6-layer S does not reproduce the sealed value"
        out["wave"][arm] = {"layers_1_5": wave_sub(th, [1, 2, 3, 4, 5]), "sealed_S_reproduced": full["S"]}
    for arm in ("A0", "M0s1", "M0s2"):
        out["qk_sr"][arm] = {M: {t: A.layer_mean(arm, t, M, A.sr) for t in (0, 512, 1000, 3000)} for M in ("Q", "K")}
    b = json.loads((RES / "armb_b4_bulk.json").read_text()); p = float(2 * norm.sf(2.487)); N = K = 0
    for arm, v in b.items():
        if arm == "provenance":
            continue
        n = sum(v["counts"].values()); k = v["counts"]["VIOLATED"]; N += n; K += k
        out["bulk"][arm] = {"cells": n, "violated": k, "expected": n * p, "P_ge_k": float(binom.sf(k - 1, n, p))}
    out["bulk"]["all"] = {"cells": N, "violated": K, "expected": N * p, "null_rate": p,
                          "z_binomial": float((N * p - K) / np.sqrt(N * p * (1 - p))), "P_le_k": float(binom.cdf(K, N, p))}
    w = json.loads((RES / "armb_q1_warp_licence_v2.json").read_text())["cells"]
    cal = json.loads((RES / "armb_noise_calibration.json").read_text())["q1"]["A0"]
    q1 = json.loads((RES / "armb_b4_q1.json").read_text())
    out["q1_a1"] = {"licence": {k: {x: w[k][x] for x in ("LICENSED", "NSA_LICENSED", "r_star", "c_fit")}
                                for k in ("A1_s0.005_iid", "A1_s0.005_ar", "A1_s0.01_iid", "A1_s0.01_ar")},
                    "A0_TP_O_measured": q1["TP_O"]["A0"]["noise_measured"], "row_0.005_ar_q05": cal["0.005_ar"]["q05"],
                    "row_0.005_iid_q05": cal["0.005_iid"]["q05"]}
    (RES / "armb_b4_post_descriptive.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: out[k] for k in ("wave", "bulk")}, indent=1, default=float)[:1500])


if __name__ == "__main__":
    main()
