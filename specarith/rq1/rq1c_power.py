"""RQ1-c (round 95): power of P1, P3 and P4 at 10¹², from the 10¹⁰ / 10¹¹ results only (nothing at 10¹² is read).
P1: the B2 T rule at the 10¹² cells (β 0.40, 0.45) with D(10¹²) from each P2 law (results/RQ1C_P2.json), SE from the
    sealed model at n₁₂ ≈ 1.880·10¹⁰, null T SD from the witnesses' within-X correlation (0.786), t = 2·SD(T_null).
P3: the collapse residual's sign change in β ∈ [0.45, 0.65] (results/collapse/COLLAPSE.json): location by linear
    interpolation, resolution SE_res / |slope| at the crossing; scaled to 10¹² by the model SE (∝ K^{−1/2}).
P4: ℤ[ω] separations from D_ωi = 0.283·D_√2i (log a_ω / log a_√2 = log √(27/16) / log 2.5204) and D_√2ω = 0.717·D_√2i,
    per cell and X, in units of the model SE (same N and K as ℤ[√2]; ℤ[ω]'s R taken between the other two).

  python rq1c_power.py OUT_JSON
"""
import json
import math
import sys

from scipy.stats import norm

C_SE = 0.6271633049515984
N12 = 2 * 1.880e10
FRAC = math.log(math.sqrt(27 / 16)) / math.log(math.pi / (math.sqrt(2) * math.log(1 + math.sqrt(2))))


def se_model(K, r1, r2):
    return math.sqrt(2 / (C_SE * K)) * math.hypot(r1, r2)


def main(out):
    read = json.load(open("results/read/read1.json"))["rows"]
    p2 = json.load(open("results/RQ1C_P2.json"))["cells"]
    col = json.load(open("results/collapse/COLLAPSE.json"))["rows"]
    res = dict(label="RQ1-c power of P1, P3, P4 (from 1e10 / 1e11 only)", frac_omega=FRAC)
    # P1
    rho = 0.786
    sdT = math.sqrt(2 + 2 * rho)
    t = 2 * sdT
    p1 = {}
    for law in ("1/logX", "1/log2X", "X^-delta"):
        T = sum(p2[f"beta={b}"]["laws"][law]["pred"] / p2[f"beta={b}"]["SE_1e12"] for b in (0.40, 0.45))
        p1[law] = dict(T_mean=T, t=t, power=float(1 - norm.cdf((t - T) / sdT)))
    res["P1"] = p1
    # P3
    p3 = {}
    for Xs, v in col.items():
        rr = [x for x in v["rows"] if 0.45 <= x["beta"] <= 0.65]
        for a, b in zip(rr, rr[1:]):
            if a["residual"] <= 0 < b["residual"]:
                slope = (b["residual"] - a["residual"]) / (b["beta"] - a["beta"])
                loc = a["beta"] - a["residual"] / slope
                se = 0.5 * (a["SE_residual"] + b["SE_residual"])
                K = a["K"]
                se12 = se * math.sqrt(K / round(N12 ** a["beta"]))
                p3[Xs] = dict(location=loc, slope_per_beta=slope, SE_residual=se, resolution=se / slope,
                              resolution_at_1e12_same_slope=se12 / slope)
    res["P3"] = p3
    # P4
    p4 = {}
    for Xs, X in (("10000000000", 1e10), ("100000000000", 1e11), ("1e12", 1e12)):
        for b in (0.40, 0.45, 0.55):
            if Xs == "1e12":
                D = p2[f"beta={b}"]["laws"]["1/logX"]["pred"] if f"beta={b}" in p2 else None
                if D is None:
                    D = p2["beta=0.55"]["laws"]["1/logX"]["pred"]
                se = p2[f"beta={b}"]["SE_1e12"] if f"beta={b}" in p2 else None
            else:
                x = {r["beta"]: r for r in read[Xs]["rows"]}[b]
                D, se = x["D"], x["SE_diff"]
            p4[f"{Xs} beta={b}"] = dict(D_sqrt2_i=D, SE=se, D_omega_i=FRAC * D, z_omega_i=FRAC * D / se,
                                         D_sqrt2_omega=(1 - FRAC) * D, z_sqrt2_omega=(1 - FRAC) * D / se)
    res["P4"] = p4
    json.dump(res, open(out, "w"), indent=1)
    print("P1:", {k: (round(v["T_mean"], 2), round(v["power"], 2)) for k, v in p1.items()}, "t", round(t, 2))
    print("P3:", {k: (round(v["location"], 4), round(v["resolution"], 4), round(v["resolution_at_1e12_same_slope"], 4)) for k, v in p3.items()})
    for k, v in p4.items():
        print("P4", k, f"D_wi {v['D_omega_i']:.4f} ({v['z_omega_i']:.2f} SE)  D_s2w {v['D_sqrt2_omega']:.4f} ({v['z_sqrt2_omega']:.2f} SE)")


if __name__ == "__main__":
    main(sys.argv[1])
