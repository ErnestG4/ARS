"""
cross_substrate/longrange_neural_audit.py — point the marginal-vs-class falsification
loop at the NEURAL pillar-1 verdicts. Every pillar-1 GUE/Poisson-pole call is an NNS
(marginal) statement; does it survive a long-range statistic?

Both poles, because NNS under-certifies BOTH (point 4): exponential NNS is necessary-
NOT-sufficient for Poisson (a correlated process can wear an exponential marginal),
so Σ²(L) must certify rigidity for a GUE-pole cell AND Σ²(L)≈L for a Poisson-pole
cell. Pre-check the ≥200-event floor per cell (below it Σ²/Δ₃ are underpowered →
folds into the pass-2 resolution floor on fast low-yield units). Each cell keeps its
OWN verdict — never pool spike trains across cells/sessions.

Run: longrange_neural_audit.py [--max-cells N]
"""
from __future__ import annotations

import argparse
import glob
import os
import sys
from collections import Counter

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import longrange_discriminator as LD
from axes import compute_family_I
from hc3_instrument_pass import parse_units, load_cellmap

# ALL cached hc-3 sessions (widen the pool so the exponential-NNS / Poisson-pole
# filter yields more than a thin handful of cells — n=7 on 4 sessions was too few).
def _discover_sessions():
    root = os.path.expanduser("~/fmexplorer/crcns_cache/sessions")
    out = []
    for sdir in sorted(glob.glob(os.path.join(root, "*", "*"))):
        if os.path.isdir(sdir) and glob.glob(os.path.join(sdir, "*.res.*")):
            out.append("/".join(sdir.split("/")[-2:]))
    return out


SESSIONS = _discover_sessions()
CAP = 3000           # contiguous segment per cell (preserve structure; enough for Σ²)
REF_N = 1200         # fixed reference n → one cached ensemble set shared by all cells
L = 50.0
N_SEEDS = 12
POLE_KS = 0.10       # NNS within this of a pole's reference CDF counts as that pole


def nns_pole(spk):
    """Which pole does the NNS (marginal) claim? GUE if ks_gue is small & < ks_poisson;
    Poisson if ks_poisson small & < ks_gue; else clustered/neither."""
    ax = compute_family_I(spk)
    kg, kp = ax.get("I.5_ks_gue"), ax.get("I.7_ks_poisson")
    if kg is None or kp is None:
        return "n/a", kg, kp
    if kg < kp and kg < POLE_KS:
        return "GUE-pole", kg, kp
    if kp < kg and kp < POLE_KS:
        return "Poisson-pole", kg, kp
    return "clustered/neither", kg, kp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-cells", type=int, default=0)
    a = ap.parse_args()
    cm = load_cellmap()
    cells = []
    for s in SESSIONS:
        sdir = os.path.expanduser(f"~/fmexplorer/crcns_cache/sessions/{s}")
        if not os.path.isdir(sdir):
            continue
        topdir, session = s.split("/")
        units, tmax, sr = parse_units(sdir, topdir, session, cm)
        for u in units:
            if u["region"] in ("EC", "CA1", "CA3", "DG") and u["spk"].size >= 200:
                cells.append((session, u))
    if a.max_cells:
        cells = cells[:a.max_cells]
    print(f"hc-3 cells with ≥200 events: {len(cells)} across {len(SESSIONS)} sessions")

    rows = []
    for session, u in cells:
        spk = np.sort(u["spk"])
        spk = spk[:CAP] if spk.size > CAP else spk
        floor = LD.enough_for_longrange(spk, L=L)
        if not floor["enough"]:
            continue
        pole, kg, kp = nns_pole(spk)
        v = LD.longrange_verdict(spk, L=L, n_seeds=N_SEEDS, unfold_deg=6, ref_n=REF_N)
        sens = LD.unfolding_sensitivity(spk, degs=(3, 6, 10), n_seeds=N_SEEDS,
                                        L=L, ref_n=REF_N)
        rows.append(dict(session=session, region=u["region"], ct=u["celltype"],
                         ele=u["ele"], clu=u["clu"], n=int(spk.size),
                         ks_gue=kg, ks_poisson=kp, nns_pole=pole,
                         longrange=v["verdict"], sigma2=v["sigma2"]["obs"],
                         lens=sens["lens"]))
    print(f"certified {len(rows)} cells (cleared the ≥{LD.MIN_N_LONGRANGE}-event floor)\n")

    # ── verdict: does each NNS pole survive the long-range statistic? ──
    def _certify(pole, want):
        sub = [r for r in rows if r["nns_pole"] == pole]
        if not sub:
            print(f"  {pole}: 0 cells"); return
        lr = Counter(r["longrange"] for r in sub)
        lens = Counter(r["lens"] for r in sub)
        confirm = sum(1 for r in sub if r["longrange"] == want and r["lens"] == "INVARIANT")
        print(f"  {pole} (n={len(sub)}): long-range {dict(lr)}  |  lens {dict(lens)}")
        print(f"      CONFIRMED ({want} & lens-invariant): {confirm}/{len(sub)}  "
              f"→ {100*confirm/len(sub):.0f}% of the NNS-{pole} verdicts survive")

    print("PILLAR-1 LONG-RANGE CERTIFICATION (per pole, each cell its own verdict):")
    _certify("GUE-pole", "RIGID_GUE")
    _certify("Poisson-pole", "POISSON_INDEP")
    cl = [r for r in rows if r["nns_pole"] == "clustered/neither"]
    if cl:
        print(f"  clustered/neither (n={len(cl)}): long-range "
              f"{dict(Counter(r['longrange'] for r in cl))} (not a pole claim)")

    # rate-nonstationarity guard: neural σ² conflates genuine long-range clustering
    # with slow rate drift; the smooth-poly unfold removes only smooth trends. How
    # much of SUPER_POISSON is lens-COVARIANT (unfolding/rate-suspect) vs INVARIANT?
    sup = [r for r in rows if r["longrange"] == "SUPER_POISSON"]
    print(f"\nrate-nonstationarity guard — SUPER_POISSON cells (n={len(sup)}): "
          f"lens {dict(Counter(r['lens'] for r in sup))}")
    print(f"  overall lens across all certified cells: {dict(Counter(r['lens'] for r in rows))}")
    inv_sup = sum(1 for r in sup if r["lens"] == "INVARIANT")
    print(f"  SUPER_POISSON & lens-INVARIANT (clustering robust to the unfold lens): "
          f"{inv_sup}/{len(sup)}; the rest are unfolding/rate-suspect")

    # by region/celltype
    print("\nby region × celltype (NNS-pole → long-range, lens):")
    seen = sorted({(r["region"], r["ct"]) for r in rows})
    for reg, ct in seen:
        sub = [r for r in rows if r["region"] == reg and r["ct"] == ct]
        poles = Counter(r["nns_pole"] for r in sub)
        lr = Counter(r["longrange"] for r in sub)
        print(f"  {reg:3s} {ct:11s} n={len(sub):>3d}  NNS-pole={dict(poles)}  longrange={dict(lr)}")

    print("\nBound: a Poisson-pole cell is genuinely independent only if Σ²(L)≈L "
          "(POISSON_INDEP); INTERMEDIATE/RIGID there = correlated structure under an "
          "exponential marginal — NNS under-certified it. Same for the GUE pole "
          "(RIGID required). Lens-COVARIANT verdicts are unfolding-dependent, not promoted.")


if __name__ == "__main__":
    main()
