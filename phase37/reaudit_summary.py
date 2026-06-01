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

# Two-axis cell label. CV is the PRIMARY magnitude coordinate (Phase-37 Set 4: the repulsion magnitude is a
# ~pure function of CV, and CV is the family-invariant signed Poisson-distance; for per-cell ISI it is NOT
# pooled, so no √N trap). mass<τ = CV + SHAPE, so it is reported as a SECONDARY shape diagnostic, NOT used to
# gate the label (a CV>1.1 cell is super-Poisson/clustered regardless of where its mass<τ quantile lands).
CV_SUB, CV_SUP = 0.90, 1.10          # repulsion side / clustering side of the Poisson pivot
MASS_POISSON = 0.259                 # Poisson baseline P(s<0.3)=1-e^-0.3 (shape reference only)


def label(cv, mass, ks_gue):
    if cv is None:
        return None
    if cv < CV_SUB:
        return "REPULSIVE"           # sub-Poisson / rigid (CV is the clean magnitude)
    if cv > CV_SUP:
        return "CLUSTERED"           # super-Poisson (CV alone — the dispersion magnitude)
    return "POISSON"                 # near the pivot


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
                    if isinstance(ax, dict) and "I.10_cv" in ax:
                        cells.append((ax.get("I.10_cv"), ax.get("I.11_mass03"),
                                      ax.get("I.5_ks_gue"), ax.get("I.7_ks_poisson")))
        except Exception:
            continue
        cells = [c for c in cells if c[0] is not None and c[1] is not None]
        if len(cells) < 5:
            continue
        labs = [label(*c[:3]) for c in cells]
        cnt = collections.Counter(labs)
        n = len(cells)
        cvs = np.array([c[0] for c in cells]); masses = np.array([c[1] for c in cells])
        frac_clust = cnt["CLUSTERED"] / n
        frac_rep = cnt["REPULSIVE"] / n
        # axis-incomplete: clustering axis carries signal (super-Poisson) in a substrate whose
        # repulsion read would be "near-Poisson/BL" (most cells not repulsive)
        axis_incomplete = (frac_clust >= 0.20) and (frac_rep < 0.20)
        rows.append(dict(sub=sub, n=n, cv_med=float(np.median(cvs)), mass_med=float(np.median(masses)),
                         frac_rep=frac_rep, frac_pois=cnt["POISSON"]/n, frac_clust=frac_clust,
                         axis_incomplete=axis_incomplete))

    rows.sort(key=lambda r: (-r["frac_clust"], r["sub"]))
    print(f"{'substrate':30s} {'n':>6} {'CVmed':>6} {'massMed':>7} {'%rep':>5} {'%pois':>6} {'%clust':>6}  flag")
    for r in rows:
        flag = "AXIS-INCOMPLETE?" if r["axis_incomplete"] else ""
        print(f"{r['sub']:30s} {r['n']:6d} {r['cv_med']:6.3f} {r['mass_med']:7.3f} "
              f"{100*r['frac_rep']:5.0f} {100*r['frac_pois']:6.0f} {100*r['frac_clust']:6.0f}  {flag}")

    flagged = [r["sub"] for r in rows if r["axis_incomplete"]]
    print(f"\n{len(rows)} substrates with the clustering axis computed.")
    print(f"AXIS-INCOMPLETE candidates (clustering-axis signal, repulsion-quiet): {flagged or 'none'}")
    print("Interface-readout framing: flags are re-audit POINTERS (which substrates want a closer two-axis")
    print("look), not substrate-level verdicts. A substrate clean-Poisson on BOTH axes is a genuine null.")
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reaudit_twoaxis_summary.json")
    json.dump(rows, open(out, "w"), indent=1)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
