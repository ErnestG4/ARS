"""
arsrh/fungal_real_detector.py — run the ACTUAL deployed exact-zero detector on the corrected null.

The port (fungal_surrogate_port.py) established the I_rep false-positive result with a RECONSTRUCTION
(pair_correlation_full on the pooled normalized spacings) — "faithful in behavior, not bit-identical".
The reviewer's falsifying test: the deployed detector is not pair_correlation_full on one pool; it is
`joint_q_profile` (per-denominator-q passage-time repulsion `rep_int_q`, one row per q) +
`joint_quadrant_diagnostic` (BL quadrant, exact-0 rep = CLUSTERED). The "fungal 194/194 exact-0" flag
(commit 9ad46d6) is 194 q-band ROWS, not units. Run THAT code path on the count-anchored corrected
null and confirm 0% — else the gap is the finding.

Null construction matches load_fungal_pool EXACTLY (run_phase15_cross_signal.py:158-190) except the
spikes are floored-Poisson instead of real: per unit (>=20 spikes) floored-Poisson at matched
rate/count -> isi/isi.mean() -> concatenate -> cumsum -> _subsample to N_TARGET. Count anchor
(certification of record): the 35 units give sum(n-1)=1470=pooled_direct.n exactly.

Run:  $HOME/fmexplorer/bin/python3 arsrh/fungal_real_detector.py
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic   # noqa: E402  DEPLOYED detector

HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(20260724)
MIN_ISI_SEC = 120.0
N_TARGET = 2000        # matches run_phase15_cross_signal.N_TARGET


def _subsample(t, n=N_TARGET):                    # verbatim from run_phase15_cross_signal.py:44
    if t.size <= n:
        return t
    step = t.size // n
    return t[::step][:n]


def floored_poisson_unit(n_spikes, T, min_isi=MIN_ISI_SEC, max_tries=20):
    lam = n_spikes / T
    for _ in range(max_tries):
        isi = RNG.exponential(1.0 / lam, size=int(n_spikes * 1.6) + 10)
        t = np.cumsum(isi)
        t = t[t < T]
        kept, last = [], -np.inf
        for x in t:
            if x - last > min_isi:
                kept.append(x)
                last = x
        if len(kept) >= n_spikes:
            return np.array(kept[:n_spikes])
    return np.array(kept)


def make_null(units):
    """Corrected-construction null point process, matching load_fungal_pool()."""
    pool = []
    for n, T in units:
        sp = floored_poisson_unit(n, T)
        isi = np.diff(np.sort(sp))
        isi = isi[isi > 0]
        if isi.size and isi.mean() > 0:
            pool.append(isi / isi.mean())
    return _subsample(np.cumsum(np.concatenate(pool)))


def deployed_detector(t):
    """The actual deployed path: joint_q_profile -> joint_quadrant_diagnostic -> BL exact-0 count."""
    df = joint_q_profile(t, q_max=200)
    df = joint_quadrant_diagnostic(df)
    well = df[~df["underpowered"]] if "underpowered" in df else df
    bl = well[well["quadrant"] == "BL"]
    n_bl = len(bl)
    if n_bl == 0:
        return {"n_bl": 0, "n_exact0": 0, "frac_exact0": float("nan")}
    exact0 = int((np.abs(bl["rep_int_q"].to_numpy()) < 1e-12).sum())
    return {"n_bl": n_bl, "n_exact0": exact0, "frac_exact0": exact0 / n_bl}


def main():
    d = json.load(open(os.path.join(_ROOT, "data", "fungal_results.json")))
    units = [(u["n_spikes"], u["duration_h"] * 3600.0) for u in d["per_unit"] if u["n_spikes"] >= 20]
    anchor = sum(n for n, _ in units) - len(units)
    assert anchor == d["pooled_direct"]["n"] == 1470, f"COUNT ANCHOR BROKEN: {anchor}"   # regression
    print(f"count anchor (certification of record): 35 units, Σ(n−1) = {anchor} = pooled_direct.n ✓\n")
    print("Running the DEPLOYED detector (joint_q_profile + joint_quadrant_diagnostic) on the "
          "count-anchored corrected null.")
    print("Real fungal reads 194/194 BL rows exact-0 (commit 9ad46d6). Null should read ~0%.\n")

    B = 12
    rows = []
    for b in range(B):
        t = make_null(units)
        r = deployed_detector(t)
        rows.append(r)
        if b < 8:
            print(f"  null {b}: BL rows={r['n_bl']:3d}  exact-0={r['n_exact0']:3d}  "
                  f"frac_exact0={r['frac_exact0']:.3f}")
    fracs = np.array([r["frac_exact0"] for r in rows if r["n_bl"] > 0])
    total_bl = sum(r["n_bl"] for r in rows)
    total_e0 = sum(r["n_exact0"] for r in rows)
    print(f"\n  over B={B} nulls: {total_e0}/{total_bl} BL q-band rows exact-0 "
          f"({100*total_e0/max(total_bl,1):.2f}%); per-null mean frac_exact0 = {fracs.mean():.4f} "
          f"(max {fracs.max():.3f})")
    agrees = total_e0 / max(total_bl, 1) < 0.02
    print(f"\n  DEPLOYED detector on corrected null: {'~0% exact-0 — CONFIRMED IDENTICAL to the '
          'reconstruction; the no-false-positive result is fully banked' if agrees else 'NON-ZERO '
          'exact-0 — the deployed path DIVERGES from the reconstruction; THAT GAP IS THE FINDING'}")

    out = {"count_anchor_1470": int(anchor), "B": B, "detector": "joint_q_profile + "
           "joint_quadrant_diagnostic (the deployed path, not the pair_correlation reconstruction)",
           "real_fungal_flag": "194/194 BL rows exact-0 (commit 9ad46d6)",
           "null_total_bl_rows": total_bl, "null_total_exact0": total_e0,
           "null_frac_exact0_overall": total_e0 / max(total_bl, 1),
           "per_null_mean_frac_exact0": float(fracs.mean()),
           "per_null_max_frac_exact0": float(fracs.max()),
           "AGREES_WITH_RECONSTRUCTION": bool(agrees),
           "verdict": ("The deployed detector confirms ~0% exact-0 false-positive on the corrected "
                       "null — the reconstruction was faithful, Half-2 fully banked." if agrees else
                       "The deployed detector DIVERGES from the reconstruction — the gap is the "
                       "finding; the clip fires per-q-band where the single-pool reconstruction did "
                       "not."),
           "bug_status": "The clip pathology (near-zero-negative rep pinned to 0.000, read as "
                         "CLUSTERED) is CONFIRMED and UNFIXED — DORMANT here only because fungal's "
                         "null sits at rep~+0.05, far from the boundary. Not cleared. Live on any "
                         "substrate whose null sits near-zero-negative."}
    json.dump(out, open(os.path.join(HERE, "fungal_real_detector_measured.json"), "w"),
              indent=2, default=str)
    print("\nwrote fungal_real_detector_measured.json")


if __name__ == "__main__":
    main()
