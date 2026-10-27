"""RQ1-b, POST HOC (round 93): Chen et al.'s Conjecture 1.2 (generalised per RQ1B_STEP0.md; constants from
results/RQ1B_CONSTANTS.json) against data. Zero parameters.

  Var/(⟨ψ⟩ log X) = 2λ − K_F/(C_Φ log X)   (λ < ½),     1 + Δ_Φ/(C_Φ log X)   (½ < λ < 1),     λ = log K / log X.

(a) Check of the constants on Chen's own statistic: ℤ[i] at X = 10⁹, their Appendix-A statistic computed on our ℤ[i]
    angles (results/CHEN_TRANSCRIPTION_X1e9.json; its Figure-1 check passed in round 86).
(b) Against the read data (our statistic: unweighted counts of split ideals, not Chen's Λ-weighted ψ with inert primes),
    on the fine β grid of results/collapse/COLLAPSE.json at 10¹⁰ and 10¹¹: R_F(β) and D(β) = R_ℤ[√2] − R_ℤ[i], with the
    sealed-model SE. λ is taken as log K / log X. The statistic mismatch is a known difference, reported, not removed.

  python rq1b_compare.py OUT_JSON
"""
import json
import math
import sys

import rq1_read as Q


def pred(lam, X, K_F, CPhi, Delta):
    L = math.log(X)
    return 2 * lam - K_F / (CPhi * L) if lam < 0.5 else 1 + Delta / (CPhi * L)


def main(out):
    c = json.load(open("results/RQ1B_CONSTANTS.json"))
    CPhi, Delta = c["C_Phi"], c["Delta_Phi"]
    K = {f: v["K_Phi"] for f, v in c["fields"].items()}
    res = dict(label="RQ1-b POST HOC: Chen Conjecture 1.2 (generalised) against data; zero parameters", K_Phi=K,
               K_over_CPhi={f: k / CPhi for f, k in K.items()}, Delta_over_CPhi=Delta / CPhi)
    t = json.load(open("results/CHEN_TRANSCRIPTION_X1e9.json"))
    res["zi_chen_statistic_1e9"] = [dict(lam=r["lam"], value=r["value"], pred=pred(r["lam"], 1e9, K["zi"], CPhi, Delta),
                                         resid=r["value"] - pred(r["lam"], 1e9, K["zi"], CPhi, Delta)) for r in t["rows"]]
    col = json.load(open("results/collapse/COLLAPSE.json"))
    res["read"] = {}
    for Xs, X in (("10000000000", 1e10), ("100000000000", 1e11)):
        rows = []
        for x in col["rows"][Xs]["rows"]:
            lam = math.log(x["K"]) / math.log(X)
            s = math.sqrt(2 / (Q.C_SE * x["K"]))
            p2, pi = pred(lam, X, K["zs2"], CPhi, Delta), pred(lam, X, K["zi"], CPhi, Delta)
            rows.append(dict(beta=x["beta"], lam=lam, R_zs2=x["R_zs2"], R_zi=x["R_zi"], pred_zs2=p2, pred_zi=pi,
                             resid_zs2_over_SE=(x["R_zs2"] - p2) / (x["R_zs2"] * s),
                             resid_zi_over_SE=(x["R_zi"] - pi) / (x["R_zi"] * s),
                             D=x["D"], SE_D=x["SE_D"], D_pred=p2 - pi, D_resid_over_SE=(x["D"] - (p2 - pi)) / x["SE_D"]))
        res["read"][Xs] = rows
    json.dump(res, open(out, "w"), indent=1)
    print("K/CPhi", res["K_over_CPhi"], "Delta/CPhi", res["Delta_over_CPhi"])
    for r in res["zi_chen_statistic_1e9"][::2]:
        print(f"  Z[i] 1e9 Chen statistic lam={r['lam']:.3f} data {r['value']:.4f} pred {r['pred']:.4f} resid {r['resid']:+.4f}")
    for Xs, rows in res["read"].items():
        print(Xs)
        for r in rows[::5]:
            print(f"  b={r['beta']:.2f} lam={r['lam']:.3f}  R_zs2 {r['R_zs2']:.3f} pred {r['pred_zs2']:.3f} ({r['resid_zs2_over_SE']:+.1f} SE)"
                  f"  R_zi {r['R_zi']:.3f} pred {r['pred_zi']:.3f} ({r['resid_zi_over_SE']:+.1f} SE)"
                  f"  D {r['D']:+.4f} pred {r['D_pred']:+.4f} ({r['D_resid_over_SE']:+.1f} SE)")


if __name__ == "__main__":
    main(sys.argv[1])
