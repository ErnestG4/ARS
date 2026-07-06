"""Panel C — turtle-path / tessellation / V7-triangle re-drawn three ways.

Reconstruction of spec Panel C §6.2 (exact wording was conversational, not on disk; RECON.md is the only
trace: "Panel C §6.2 re-draws V7's polyline three ways"). V7 = gold_silver_ladder.py's C-vs-Lagrange scatter
over the gold->silver Markov ladder. The scientific content: is the DEGT dimension C controlled by
approximability (Lagrange Λ), by Panel A's liminf-geomean order parameter K (Liu-Wen), or by the digit-content
functional (Thread-1's a>=2 story)? Re-draw the polyline against all three; whichever linearizes C is the real
controlling functional, the others are the "zigzag".

Clean-C fix (Thread-1 enabled): the banked ladder C (2026-05-25) ran dim_growth over FIBONACCI q-targets, which
don't align with non-golden members' convergents -> few levels -> noisy C (mixed-ladder Spearman not significant,
n=8). Here each member runs over ITS OWN convergent ladder via exact Floquet band widths -> more levels ->
tighter C. Moderate lambda in {2,4,8,16} (fully resolved by Floquet); C = intercept of dim*ln(lambda) vs 1/ln(lambda).
"""
import os, sys, json, math
sys.path.insert(0, ".")
import numpy as np
_ROOT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, os.path.join(_ROOT, "cross_substrate"))
from trace_map_dimension import band_widths, dim_pressure  # Floquet band widths + Bowen pressure
from task1_pi_depth5 import potential, convergents  # EXACT integer potential + fractional convergents (p<q)

LAMS = [2.0, 4.0, 8.0, 16.0, 32.0]
QMIN, QMAX = 30, 6000

# ---- ladder: 8 gold->silver members (V7) + anchors + extra mixed CFs for statistical power ----
MEMBERS = [
    ("[1] gold",   [1]),
    ("[1,1,1,2]",  [1, 1, 1, 2]),
    ("[1,1,2]",    [1, 1, 2]),
    ("[1,2]",      [1, 2]),
    ("[2,2,1,1]M", [2, 2, 1, 1]),
    ("[1,2,2]",    [1, 2, 2]),
    ("[1,2,2,2]",  [1, 2, 2, 2]),
    ("[2] silver", [2]),
    ("[3] bronze", [3]),
    ("[4] metal4", [4]),
    ("[1,1,1,1,2]",[1, 1, 1, 1, 2]),
    ("[1,3]",      [1, 3]),
    ("[2,3]",      [2, 3]),
    ("[1,1,3]",    [1, 1, 3]),
    ("[1,2,3]",    [1, 2, 3]),
    ("[2,2,3]",    [2, 2, 3]),
]
REPS = 200


def cf_value(digits):
    x = 0.0
    for d in reversed(digits):
        x = 1.0 / (d + x)
    return x


def periodic_alpha(period):
    return cf_value(period * REPS)


def lagrange_const(period):
    p = len(period); best = 0.0
    for i in range(p):
        fwd = (period[i:] + period[:i]) * REPS
        f = fwd[0] + cf_value(fwd[1:])
        back = ((period[:i][::-1]) + (period[::-1]) * REPS)
        b = cf_value(back)
        best = max(best, f + b)
    return best


def convergent_qs(period, qmax):
    """Fractional CF convergents (p,q), p<q, of alpha=[0;period,period,...] up to q<=qmax.
    Uses the proven task1 convergents() (a_0=0 fractional convention; matches potential())."""
    ps, qs = convergents(period * REPS)
    out = []
    for p, q in zip(ps, qs):
        if q < 1 or q > qmax:
            if q > qmax:
                break
            continue
        if math.gcd(p, q) == 1 and 0 < p < q:
            out.append((p, q))
    return out


def dim_growth_own(period, lam):
    """Bowen-pressure spectral dim via slope-zero of log Σ|band|^d vs log q, over the member's OWN
    convergent levels (Floquet band widths). Returns (d_star, nlevels)."""
    levels = []
    for p, q in convergent_qs(period, QMAX):
        if q < QMIN:
            continue
        w = band_widths(potential(p, q, lam))
        if w.size > 2 and w.size >= 0.9 * q:     # require most bands resolved
            levels.append((q, w))
    seen = {}
    for q, w in levels:
        seen[q] = w
    levels = sorted(seen.items())
    if len(levels) < 3:
        return None, len(levels)
    logq = np.array([math.log(q) for q, _ in levels])
    dgrid = np.linspace(0.02, 0.999, 300)
    P = np.array([np.polyfit(logq, np.array([math.log(np.sum(w ** d)) for _, w in levels]), 1)[0]
                  for d in dgrid])
    sign = np.sign(P); cross = np.where(np.diff(sign) != 0)[0]
    if cross.size == 0:
        return None, len(levels)
    i = cross[0]
    d_star = dgrid[i] - P[i] * (dgrid[i + 1] - dgrid[i]) / (P[i + 1] - P[i])
    return float(d_star), len(levels)


def degt_C(period):
    """C = intercept of dim*ln(lambda) vs 1/ln(lambda), extrapolated 1/ln(lambda)->0, over resolved lambdas."""
    pts = []
    for lam in LAMS:
        d, nlv = dim_growth_own(period, lam)
        if d is not None:
            pts.append((1.0 / math.log(lam), d * math.log(lam), lam, nlv))
    if len(pts) < 3:
        return None, pts
    x = np.array([p[0] for p in pts]); y = np.array([p[1] for p in pts])
    C = float(np.polyfit(x, y, 1)[1])
    return C, pts


def main():
    rows = []
    for name, period in MEMBERS:
        C, pts = degt_C(period)
        a = np.array(period, float)
        rows.append({
            "name": name, "period": period,
            "alpha": periodic_alpha(period),
            "lagrange": lagrange_const(period),
            "K": float(np.prod(a) ** (1.0 / len(a))),     # liminf-geomean (periodic => period geomean)
            "meandig": float(np.mean(a)), "maxdig": float(max(period)),
            "mdens": float(np.mean([1.0 if d >= 2 else 0.0 for d in period])),
            "C": C, "nlam_conv": len(pts),
            "dimlnlam_pts": [(round(1/math.log(l), 4), round(v, 4), l, nlv) for _, v, l, nlv in pts],
        })
        cs = f"{C:.4f}" if C else "None"
        print(f"{name:12s} C={cs:>7s} Λ={rows[-1]['lagrange']:.3f} K={rows[-1]['K']:.3f} "
              f"meandig={rows[-1]['meandig']:.3f} nλ={len(pts)}")
    json.dump(rows, open("panel_C.json", "w"), indent=1)

    # ---- three-ways correlations ----
    from scipy.stats import spearmanr, pearsonr
    ok = [r for r in rows if r["C"] is not None]
    C = np.array([r["C"] for r in ok])
    print(f"\nn={len(ok)} members with clean C. Three-ways (C vs each functional):")
    print(f"{'axis':10s} {'spearman':>9s} {'pearson':>8s} {'p(spear)':>9s}")
    for ax in ("lagrange", "K", "meandig", "maxdig", "mdens"):
        x = np.array([r[ax] for r in ok])
        sr = spearmanr(x, C); pe = pearsonr(x, C)[0]
        print(f"{ax:10s} {sr.correlation:>9.3f} {pe:>8.3f} {sr.pvalue:>9.3f}")
    print("\nwrote panel_C.json")


if __name__ == "__main__":
    main()
