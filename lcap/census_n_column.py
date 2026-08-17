"""Census n-column (ruling, 2026-08-16) — closes the flank the
n-dependence opened.  COMMITTED GENERATOR of lcap/census_n.json.

The single-L census established WHICH call sites judge at one L.  The
n-dependence finding means that was only half the question: a call site is
exposed if its judging L exceeds discrimination_L AT ITS OWN n, and that cap
ranges 5 -> 40 across n = 343 -> 2000.  Brocot was the one row that happened
to be checked; the other five sites were audited against a cap that did not
exist.

The sharpest form of the question: the repo's DEFAULT scale policy is
matched_L(n) = clip(0.02*n, 5, 50), which grows LINEARLY in n, while the
discrimination cap does not.  If the two curves cross, the default policy is
out-of-window over a whole range of n — which would make this a property of
the scale policy itself rather than of any one call site.
"""

import json
import sys

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
for p in (f"{ROOT}/rigidgate", f"{ROOT}/lcap", f"{ROOT}/cross_substrate"):
    if p not in sys.path:
        sys.path.insert(0, p)
import gate_probe as G                                          # noqa: E402
from policy import goe_positions, Z_SEP                         # noqa: E402

N_GRID = [343, 700, 1200, 1600, 2000]
L_SCAN = [3.0, 5.0, 8.0, 12.0, 20.0, 30.0, 40.0, 50.0]
SEEDS, DRAWS, DEG = 12, 5, 6


def matched_L(n):
    return float(np.clip(0.02 * n, 5.0, 50.0))


def discrimination_L_at(n):
    rows, best = {}, None
    for L in L_SCAN:
        gue, _ = G.bands(n, L, SEEDS, DEG)
        gm, gs = gue["sigma2"]["mean"], gue["sigma2"]["sd"]
        vals = [G.sigma2(goe_positions(n, np.random.default_rng(81_000 + k)),
                         L, DEG) for k in range(DRAWS)]
        z = (float(np.mean(vals)) - gm) / gs
        rows[str(L)] = dict(z_goe=float(z), separated=bool(z >= Z_SEP))
    for L in L_SCAN:
        if rows[str(L)]["separated"]:
            best = L
        else:
            break
    return best, rows


def main():
    out = dict(Z_SEP=Z_SEP, seeds=SEEDS, draws=DRAWS,
               default_policy="matched_L(n) = clip(0.02n, 5, 50)", by_n={})
    print("n-column: does the DEFAULT scale policy stay inside the "
          "discrimination window?", flush=True)
    print(f"{'n':>6} {'matched_L':>10} {'discrim_L':>10} {'verdict':>14}",
          flush=True)
    crossings = []
    for n in N_GRID:
        Ld, rows = discrimination_L_at(n)
        mL = matched_L(n)
        inside = bool(Ld is not None and mL <= Ld)
        out["by_n"][str(n)] = dict(matched_L=mL, discrimination_L=Ld,
                                   default_inside_window=inside, scan=rows)
        if not inside:
            crossings.append(n)
        print(f"{n:6d} {mL:10.2f} {str(Ld):>10} "
              f"{'INSIDE' if inside else 'OUTSIDE':>14}", flush=True)

    out["default_policy_outside_at"] = crossings
    out["finding"] = (
        "matched_L grows linearly in n while the discrimination cap does "
        "not, so the DEFAULT scale policy is out-of-window over the range "
        f"{crossings} of the n values tested. This is a property of the "
        "scale policy itself, not of any individual call site."
        if crossings else
        "the default policy stays inside the discrimination window at every "
        "n tested")

    # per-call-site exposure, from the single-L census + the n each runs at
    out["call_sites"] = {
        "longrange_audit.py:36": dict(
            L="fixed 50.0", n="per row (zeta n=2000; others vary)",
            exposure="zeta n=2000: 50 > discrimination_L(2000)=40 -> OUTSIDE. "
                     "Other arithmetic rows depend on their own n and are "
                     "unaudited here (their point sets are not held by this "
                     "arc)."),
        "longrange_allen_audit.py:73": dict(
            L="fixed 50.0", n="per cell (spike counts, >= MIN_N=200)",
            exposure="fixed L=50 exceeds discrimination_L at every n tested "
                     "below 2000 -> OUTSIDE for any cell with n < ~2000. "
                     "Direction note: these rows are the NEGATIVE result "
                     "0/100 RIGID_GUE, and a discrimination failure cannot "
                     "manufacture a rigid reading — it can only fail to "
                     "separate GUE from GOE, both of which are non-results "
                     "here."),
        "longrange_allen_psth_audit.py:78": dict(
            L="fixed 50.0", n="per cell", exposure="as above"),
        "trial_psth_unfold.py:124": dict(
            L="caller-supplied", n="per cell",
            exposure="depends on the caller; the policy helper l_judge() is "
                     "now available to bound it"),
        "threadE_universality_diff.py:36": dict(
            L="matched_L default", n="per input",
            exposure="follows the default-policy row above"),
        "threadE_figure.py:12": dict(
            L="matched_L default", n="per input",
            exposure="descriptive figure; follows the default-policy row"),
    }
    json.dump(out, open(f"{ROOT}/lcap/census_n.json", "w"), indent=1)
    print(f"\nFINDING: {out['finding']}", flush=True)


if __name__ == "__main__":
    main()
