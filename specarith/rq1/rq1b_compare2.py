"""RQ1-b, POST HOC (round 94): the generalised Chen formula against Chen's own statistic on the RQ1 archives. Zero
parameters. Criterion declared here, committed before the 1e10 / 1e11 values were seen:

  prediction (Conjecture 1.2 at finite X, constants from results/RQ1B_CONSTANTS.json; the two analogy substitutions,
  L(s, χ_F) and F's inert primes, are UNVERIFIED): 2λ − K_F/(C_Φ log X) for λ < ½, 1 + Δ_Φ/(C_Φ log X) for λ > ½.
  SE (model): value × 2/√K (sample variance of K bins, Gaussian, mirror pairs halving the independent bins); D's SE is
  the two fields' in quadrature. Reported alongside: the model's SE against the bin-to-bin scatter of the 1e9 ℤ[i]
  residuals (not used for the criterion).
  RIGIDITY RANGE: λ ∈ {0.200, 0.225, …, 0.400} ((1 − 2λ) log X ≥ 4.6 at 10¹⁰, so the λ ≶ ½ split is not at issue).
  COHERENT iff |residual| ≤ 2 SE for ℤ[√2], for ℤ[i] and for D at every λ of the rigidity range, at both 10¹⁰ and 10¹¹.
  Around λ = ½ (0.425–0.575) and above: reported only (bifurcation excluded from any gate, round 94).

  python rq1b_compare2.py CHENSTAT_JSON OUT_JSON
"""
import json
import math
import sys

RIG = [round(0.2 + 0.025 * i, 3) for i in range(9)]


def main(path, out):
    c = json.load(open("results/RQ1B_CONSTANTS.json"))
    CPhi, Delta = c["C_Phi"], c["Delta_Phi"]
    K = {f: v["K_Phi"] for f, v in c["fields"].items()}
    d = json.load(open(path))["fields"]
    res = dict(label="RQ1-b POST HOC: generalised Chen formula vs Chen's statistic", criterion="see docstring", X={})
    coherent = True
    for Xs in ("10000000000", "100000000000"):
        X = float(Xs)
        L = math.log(X)
        rows = []
        for a, b in zip(d["zs2"]["results"][Xs]["rows"], d["zi"]["results"][Xs]["rows"]):
            lam, Kb = a["lam"], a["K"]
            pr = {f: (2 * lam - K[f] / (CPhi * L) if lam < 0.5 else 1 + Delta / (CPhi * L)) for f in ("zs2", "zi")}
            v = {"zs2": a["value"], "zi": b["value"]}
            se = {f: abs(v[f]) * 2 / math.sqrt(Kb) for f in v}
            seD = math.hypot(se["zs2"], se["zi"])
            r = dict(lam=lam, K=Kb, value=v, pred=pr, SE=se,
                     resid_over_SE={f: (v[f] - pr[f]) / se[f] for f in v},
                     D=v["zs2"] - v["zi"], D_pred=pr["zs2"] - pr["zi"], SE_D=seD,
                     D_resid_over_SE=(v["zs2"] - v["zi"] - (pr["zs2"] - pr["zi"])) / seD)
            if lam in RIG:
                ok = all(abs(x) <= 2 for x in r["resid_over_SE"].values()) and abs(r["D_resid_over_SE"]) <= 2
                r["in_rigidity_range"], r["within_2SE"] = True, ok
                coherent &= ok
            rows.append(r)
        res["X"][Xs] = rows
    res["COHERENT_IN_RIGIDITY_RANGE"] = bool(coherent)
    json.dump(res, open(out, "w"), indent=1)
    for Xs, rows in res["X"].items():
        print(Xs)
        for r in rows:
            if r["lam"] >= 0.2:
                print(f"  lam={r['lam']:.3f} K={r['K']:>9}  zs2 {r['value']['zs2']:.4f} pred {r['pred']['zs2']:.4f} "
                      f"({r['resid_over_SE']['zs2']:+5.1f} SE)  zi {r['value']['zi']:.4f} pred {r['pred']['zi']:.4f} "
                      f"({r['resid_over_SE']['zi']:+5.1f} SE)  D {r['D']:+.4f} pred {r['D_pred']:+.4f} "
                      f"({r['D_resid_over_SE']:+5.1f} SE){'  *' if r.get('in_rigidity_range') else ''}")
    print("COHERENT_IN_RIGIDITY_RANGE", res["COHERENT_IN_RIGIDITY_RANGE"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
