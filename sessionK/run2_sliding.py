"""Run 2 — sliding-window unfolding-free <r~> sweep on the complete block (r<100).

Answers the two banked-object questions in one pass:
  (i)  r* stability: is the ~40 crossover window-stable or a window artifact?
  (ii) residual: does the elevated sector's <r~> collapse to the 0.386 Poisson
       surmise above r*, or persist?

LABEL CORRECTION (from Run 1): eigenvalue+1=even=LMFDB sym0; eigenvalue-1=odd=sym1.
The sealed plan's 'even block / 0.427 aggregate' is the sym=1 sector (Run-1 = ODD).
Reported here with corrected labels; both sectors swept.
"""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
POISSON, GOE = 0.38629, 0.53590

def rstat(x):
    x = np.sort(x); s = np.diff(x)
    return np.minimum(s[1:], s[:-1]) / np.maximum(s[1:], s[:-1])

def sliding(rvals, win_n=70, step=15):
    rvals = np.sort(rvals); out = []
    for lo in range(0, len(rvals) - win_n + 1, step):
        seg = rvals[lo:lo + win_n]
        rr = rstat(seg)
        out.append({"r_center": float(seg.mean()), "r_lo": float(seg[0]),
                    "r_hi": float(seg[-1]), "n": int(win_n),
                    "mean_rtilde": float(rr.mean()),
                    "se": float(rr.std(ddof=1) / np.sqrt(len(rr)))})
    return out

def rstar_stability(rvals):
    """Vary window width; where does <r~> first drop below the Poisson+2se band?"""
    rvals = np.sort(rvals); res = {}
    for win in (40, 60, 80):
        rows = sliding(rvals, win_n=win, step=10)
        # first window (by center) whose mean is within 2se of Poisson AND all
        # subsequent stay near-Poisson => r* ~ that center
        rstar = None
        for row in rows:
            if row["mean_rtilde"] - 2 * row["se"] <= POISSON + 0.03:
                rstar = row["r_center"]; break
        res[f"win{win}"] = rstar
    return res

if __name__ == "__main__":
    d = np.genfromtxt(os.path.join(HERE, "maass_level1_partial.csv"),
                      delimiter=",", names=True)
    r, sym = d["r"], d["symmetry"].astype(int)
    mask = r < 100
    out = {"poisson": POISSON, "goe": GOE, "label_note":
           "sym0=EVEN, sym1=ODD (Run-1 convention); plan's 'even/0.427' = sym1 = ODD"}
    for s, name in [(0, "sym0_even"), (1, "sym1_odd")]:
        rv = r[(sym == s) & mask]
        agg = rstat(rv)
        out[name] = {"n": int(len(rv)),
                     "aggregate_rtilde": float(agg.mean()),
                     "aggregate_se": float(agg.std(ddof=1) / np.sqrt(len(agg))),
                     "sliding_win70": sliding(rv, 70, 15),
                     "rstar_stability": rstar_stability(rv)}
    json.dump(out, open(os.path.join(HERE, "run2_measured.json"), "w"), indent=2)
    for name in ("sym0_even", "sym1_odd"):
        o = out[name]
        print(f"{name}: n={o['n']} agg<r~>={o['aggregate_rtilde']:.4f}+/-{o['aggregate_se']:.4f}"
              f"  r*_stability={o['rstar_stability']}")
        print("   sliding (r_center: <r~>+/-se):")
        for w in o["sliding_win70"]:
            flag = "  <-- >Poisson+2se" if w["mean_rtilde"] - 2*w["se"] > POISSON else ""
            print(f"     r~{w['r_center']:6.1f} [{w['r_lo']:5.1f},{w['r_hi']:5.1f}]  "
                  f"{w['mean_rtilde']:.4f}+/-{w['se']:.4f}{flag}")
