"""
phase37/reaudit_summary.py — Set 1 summary. Read every coordinate file, and for cells that now carry the
clustering axis (I.10_cv + I.11_mass03), assign a two-axis label (CV-PRIMARY: REPULSIVE CV<0.9 / POISSON
CV≈1 / CLUSTERED CV>1.1; mass<τ reported as a secondary SHAPE diagnostic, not label-gating — Phase-37 Set 4)
and aggregate per substrate. Flag
AXIS-INCOMPLETE substrates: those whose repulsion-axis read is null/Poisson-pole (low rep, near-Poisson on
ks_gue) but where a material fraction of cells are CLUSTERED (super-Poisson) — i.e. the clustering axis
carries signal the original repulsion-only read missed. Distinguishes a genuine null (clean Poisson on BOTH
axes) from axis-incomplete (super-Poisson on the clustering axis).

Interface-readout framing; the flag is a re-audit pointer, not a substrate-level claim.
"""
from __future__ import annotations
import os, json, glob, collections
import numpy as np

COORD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "cross_substrate", "coordinates")

# Label coordinate. PRIMARY = I.12_cv2 (CV2, parameter-free LOCAL irregularity, rate-robust): it isolates
# FAST burst-clustering from the SLOW rate-nonstationarity / epoch-gap concatenation that inflates global CV
# (validated: epoch-concat Poisson → global CV 10.9 but CV2 1.0; bursty → CV2 1.3). The global CV (I.10) and
# mass<τ (I.11) are reported as the SLOW/TOTAL-dispersion secondary — a cell with global CV≫CV2 is
# rate-nonstationary/epoch-gappy, NOT fast-clustered. Phase 37 CV-16-artifact fix.
CV2_REG, CV2_SUP = 0.90, 1.10        # locally regular / Poisson-like / locally clustered (Poisson CV2=1)


def label(cv2):
    if cv2 is None:
        return None
    if cv2 < CV2_REG:
        return "REGULAR"             # locally regular/refractory (CV2<1)
    if cv2 > CV2_SUP:
        return "CLUSTERED"           # genuine FAST burst-clustering (CV2>1, rate-robust)
    return "POISSON"                 # locally Poisson-like


def main():
    rows = []
    for f in sorted(glob.glob(os.path.join(COORD, "*.jsonl"))):
        sub = os.path.basename(f)[:-6]
        cells = []
        try:
            with open(f) as fh:
                for ln in fh:
                    d = json.loads(ln)
                    ax = d.get("axes_computed")
                    if isinstance(ax, dict) and "I.12_cv2" in ax:
                        cells.append(dict(cv2=ax.get("I.12_cv2"), lv=ax.get("I.13_lv"),
                                          cv=ax.get("I.10_cv"), mass=ax.get("I.11_mass03")))
        except Exception:
            continue
        cells = [c for c in cells if c["cv2"] is not None]
        if len(cells) < 5:
            continue
        labs = [label(c["cv2"]) for c in cells]
        cnt = collections.Counter(labs)
        n = len(cells)
        cv2 = np.array([c["cv2"] for c in cells])
        cv = np.array([c["cv"] for c in cells if c["cv"] is not None])
        mass = np.array([c["mass"] for c in cells if c["mass"] is not None])
        frac_clust = cnt["CLUSTERED"] / n        # CV2>1.1 = GENUINE fast burst-clustering
        frac_reg = cnt["REGULAR"] / n
        # fraction where global CV is high but CV2 is ~Poisson → slow rate-drift / epoch-gap (NOT fast clust)
        frac_slow = float(np.mean([(c["cv"] is not None and c["cv"] > 1.5 and c["cv2"] <= 1.1) for c in cells]))
        # axis-incomplete (clustering-type) keys on GENUINE fast clustering, not slow-structure-inflated CV
        axis_incomplete = (frac_clust >= 0.20) and (frac_reg < 0.20)
        rows.append(dict(sub=sub, n=n, cv2_med=float(np.median(cv2)),
                         cv_med=float(np.median(cv)) if cv.size else None,
                         mass_med=float(np.median(mass)) if mass.size else None,
                         frac_reg=frac_reg, frac_pois=cnt["POISSON"] / n, frac_clust=frac_clust,
                         frac_slow_drift=frac_slow, axis_incomplete=axis_incomplete))

    rows.sort(key=lambda r: (-r["frac_clust"], r["sub"]))
    print(f"{'substrate':30s} {'n':>6} {'CV2med':>6} {'gCVmed':>7} {'%reg':>5} {'%pois':>6} {'%clust':>6} {'%slowdrift':>10}  flag")
    for r in rows:
        flag = "FAST-CLUSTERED (axis-incomplete)" if r["axis_incomplete"] else \
               ("SLOW-STRUCTURE (gCV≫CV2)" if r["frac_slow_drift"] >= 0.5 else "")
        gcv = f"{r['cv_med']:7.2f}" if r['cv_med'] is not None else "   None"
        print(f"{r['sub']:30s} {r['n']:6d} {r['cv2_med']:6.3f} {gcv} "
              f"{100*r['frac_reg']:5.0f} {100*r['frac_pois']:6.0f} {100*r['frac_clust']:6.0f} "
              f"{100*r['frac_slow_drift']:10.0f}  {flag}")

    flagged = [r["sub"] for r in rows if r["axis_incomplete"]]
    print(f"\n{len(rows)} substrates with the rate-robust axis (CV2) computed.")
    print(f"GENUINE FAST-CLUSTERED (CV2>1.1, repulsion/regular-quiet) = clustering-type: {flagged or 'none'}")
    print("Contrast: %slowdrift = cells with global CV≫1 but CV2≈1 (rate-nonstationary/epoch-gap, NOT fast")
    print("clustering — the CV-16 artifact). Interface-readout framing: flags are re-audit POINTERS.")
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reaudit_twoaxis_summary.json")
    json.dump(rows, open(out, "w"), indent=1)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
