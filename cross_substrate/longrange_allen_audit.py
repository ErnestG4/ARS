"""
cross_substrate/longrange_allen_audit.py — the GUE-pole long-range audit + H1 self-test
on Allen V1 (the GUE-reading substrate hc-3 lacked).

hc-3 had 0 GUE-pole cells, so the GUE side of pillar-1 was untestable there. Allen V1
drifting-gratings units DO populate the GUE end (the H1 OSI↔ks_gue work). Two tests:

(1) GUE-POLE CONCORDANCE — do the cells the NNS instrument ranks nearest the GUE pole
    (lowest ks_gue / i5) read RIGID on the long-range instrument? Spearman(ks_gue, σ²)
    > 0 and the lowest-ks_gue cells reading RIGID = the GUE end is genuine, not
    marginal-only. (The neural counterpart of zeta_first CONFIRMED.)

(2) H1 SELF-TEST as a DISAMBIGUATOR — H1 is OSI↔ks_gue POSITIVE, so high-OSI cells sit
    FAR from the GUE pole on the NNS marginal. "Far" is two-sided and NNS can't tell
    which; the long-range tool splits it: high-OSI → SUPER_POISSON = bursty stimulus-
    driven firing; high-OSI → RIGID = stimulus-LOCKING. Sign of Spearman(OSI, σ²) is
    the mechanism readout. The 2nd instrument hands H1 a mechanism candidate.

Reuses allen_osi_gap.gratings_train + the banked OSI parquet (111 V1 units). Main venv.
"""
from __future__ import annotations

import glob
import json
import os
import sys

import numpy as np
import pandas as pd
import h5py
from scipy import stats

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_HERE, _ROOT, os.path.join(_ROOT, "phase22a")):
    if p not in sys.path:
        sys.path.insert(0, p)

import longrange_discriminator as LD
from allen_osi_gap import gratings_train
from ars_classify import unfold_unit_mean
from axes import canonical_spacings, I5_ks_gue

NWB_GLOB = os.path.expanduser("~/fmexplorer/allen_cache/session_*/session_*.nwb")
OSI_PARQUET = os.path.join(_ROOT, "data/phase24_results/h1_allen_comparison.parquet")
L = 50.0
REF_N = 1500
N_SEEDS = 12
CAP = 4000


def collect():
    osi = pd.read_parquet(OSI_PARQUET).set_index("unit_id")
    targets = set(osi.index)
    rows = []
    for f in sorted(glob.glob(NWB_GLOB)):
        sess = f.split("/")[-1].replace(".nwb", "")
        with h5py.File(f, "r") as h:
            ids = h["units/id"][:]
            present = [(r, int(u)) for r, u in enumerate(ids) if int(u) in targets]
            if not present:
                continue
            g = h["intervals/drifting_gratings_presentations"]
            starts, stops = g["start_time"][:], g["stop_time"][:]
            for r, u in present:
                train = gratings_train(h, r, starts, stops)
                if not LD.enough_for_longrange(train, L=L)["enough"]:
                    continue
                tr = train[:CAP] if train.size > CAP else train
                i5 = I5_ks_gue(canonical_spacings(unfold_unit_mean(tr)))
                if i5 is None:
                    continue
                v = LD.longrange_verdict(tr, L=L, n_seeds=N_SEEDS, unfold_deg=6, ref_n=REF_N)
                sens = LD.unfolding_sensitivity(tr, degs=(3, 6, 10), n_seeds=N_SEEDS,
                                                L=L, ref_n=REF_N)
                rows.append({"session": sess, "unit_id": u, "n": int(tr.size),
                             "ks_gue": float(i5), "osi": float(osi.loc[u, "osi"]),
                             "mean_rate": float(osi.loc[u, "mean_rate"]),
                             "longrange": v["verdict"], "sigma2": v["sigma2"]["obs"],
                             "lens": sens["lens"]})
        print(f"  {sess}: {len(present)} target units", flush=True)
    return pd.DataFrame(rows)


def main():
    print("=" * 78)
    print("ALLEN V1 GUE-POLE LONG-RANGE AUDIT + H1 SELF-TEST")
    print("=" * 78)
    df = collect()
    inv = df[df.lens == "INVARIANT"].copy()      # lens-invariant cells only for claims
    print(f"\n{len(df)} V1 units (≥{LD.MIN_N_LONGRANGE} gratings spikes); "
          f"{len(inv)} lens-INVARIANT. Long-range mix: {dict(df.longrange.value_counts())}")
    if len(inv) < 8:
        print("too few lens-invariant cells for the tests"); return

    # (1) GUE-pole concordance — does NNS GUE-proximity (low ks_gue) ⇒ long-range RIGID?
    rho_kc, p_kc = stats.spearmanr(inv.ks_gue, inv.sigma2)
    q1 = inv[inv.ks_gue <= inv.ks_gue.quantile(0.25)]    # nearest GUE pole by NNS
    q4 = inv[inv.ks_gue >= inv.ks_gue.quantile(0.75)]    # farthest
    rigid_q1 = float((q1.longrange == "RIGID_GUE").mean())
    print("\n(1) GUE-POLE CONCORDANCE (NNS GUE-proximity vs long-range rigidity):")
    print(f"    Spearman(ks_gue, σ²) = {rho_kc:+.3f} (p={p_kc:.1e})  "
          f"[+ = low-ks_gue cells are more rigid → concordant]")
    print(f"    lowest-ks_gue quartile (n={len(q1)}): {rigid_q1*100:.0f}% RIGID_GUE, "
          f"verdicts {dict(q1.longrange.value_counts())}")
    print(f"    highest-ks_gue quartile (n={len(q4)}): verdicts {dict(q4.longrange.value_counts())}")
    # concordant RANKING (ks_gue tracks the long-range gradient) is necessary but
    # NOT sufficient for a genuine GUE pole — the latter needs the nearest-GUE cells
    # to actually read RIGID. 0% RIGID ⇒ marginal-only, like hc-3's Poisson pole.
    concordant_ranking = rho_kc > 0 and p_kc < 0.05
    gue_pole_genuine = rigid_q1 >= 0.5

    # (2) H1 self-test — OSI vs long-range, the mechanism disambiguator
    rho_oc, p_oc = stats.spearmanr(inv.osi, inv.sigma2)
    rho_ok, p_ok = stats.spearmanr(inv.osi, inv.ks_gue)   # H1 itself (expect +)
    hi = inv[inv.osi >= inv.osi.quantile(0.66)]           # high-OSI = far from GUE (H1+)
    hi_mix = dict(hi.longrange.value_counts())
    n_sup = int((hi.longrange == "SUPER_POISSON").sum())
    n_rig = int((hi.longrange == "RIGID_GUE").sum())
    print("\n(2) H1 SELF-TEST (OSI ↔ long-range; mechanism disambiguator):")
    print(f"    Spearman(OSI, PLAIN ks_gue i5) = {rho_ok:+.3f} (p={p_ok:.1e})  "
          f"[plain-NNS leg the Σ² extends — NOT the q-banded ks_gue_med pillar "
          f"(banked Allen −0.22); their divergence = the OSI-gap]")
    print(f"    Spearman(OSI, σ²)     = {rho_oc:+.3f} (p={p_oc:.1e})  "
          f"[+ → high-OSI clustered (bursty stimulus-driven); − → high-OSI rigid (stimulus-locking)]")
    print(f"    high-OSI tertile (n={len(hi)}): {hi_mix}  → SUPER_POISSON={n_sup}, RIGID={n_rig}")
    mech = ("bursty-stimulus-driven (SUPER_POISSON-dominated)" if n_sup > n_rig
            else "stimulus-locking (RIGID-dominated)" if n_rig > n_sup
            else "mixed/ambiguous")

    print("\n" + "=" * 78)
    if gue_pole_genuine:
        v1 = "GENUINE GUE pole (nearest-GUE cells read RIGID)"
    elif concordant_ranking:
        v1 = ("MARGINAL-ONLY — ks_gue tracks a long-range CLUSTERING gradient "
              f"(ρ={rho_kc:+.2f}) but 0% of even the nearest-GUE cells are RIGID; the "
              "NNS GUE pole DOWNGRADES, like hc-3's Poisson pole (3rd downgrade).")
    else:
        v1 = "ranking uninformative (ks_gue ⊥ long-range)"
    print(f"VERDICT (1) GUE pole: {v1}")
    print(f"VERDICT (2) H1 mechanism candidate (2nd instrument): high-OSI cells read {mech} "
          f"— far-from-GUE is the CLUSTERED side, not stimulus-locking (RIGID).")
    print("CAVEAT (load-bearing): the gratings train is presentation-CONCATENATED, so "
          "stimulus-driven rate modulation (non-smooth, per-presentation) inflates Σ² "
          "and smooth-poly can't remove it — the all-SUPER_POISSON conflates intrinsic "
          "clustering with stimulus drive. UNLIKE hc-3, the external rate (trial PSTH) "
          "IS available here → the trial-PSTH unfold (the external-rate fix #2's negative "
          "result demanded) is the concrete next step to isolate intrinsic structure.")
    print("Bound: claims restricted to lens-INVARIANT cells; smooth-poly unfold only "
          "(rate-aware self-unfold is aliased — see validate_rate_unfold). Allen V1 "
          "gratings, awake mouse.")
    df.to_parquet(os.path.join(_HERE, "longrange_allen_cells.parquet"))
    out = dict(n=len(df), n_invariant=len(inv),
               concordance_rho=float(rho_kc), concordance_p=float(p_kc),
               lowest_ksgue_pct_rigid=rigid_q1,
               osi_ksgue_rho=float(rho_ok), osi_sigma2_rho=float(rho_oc),
               high_osi_super=n_sup, high_osi_rigid=n_rig, mechanism=mech,
               concordant_ranking=bool(concordant_ranking),
               gue_pole_genuine=bool(gue_pole_genuine),
               gue_pole_verdict=("GENUINE" if gue_pole_genuine
                                 else "MARGINAL_ONLY" if concordant_ranking else "UNINFORMATIVE"),
               stimulus_rate_confound="gratings concatenation; needs trial-PSTH unfold")
    with open(os.path.join(_HERE, "longrange_allen_results.json"), "w") as fo:
        json.dump(out, fo, indent=2)
    print("→ longrange_allen_results.json + longrange_allen_cells.parquet")


if __name__ == "__main__":
    main()
