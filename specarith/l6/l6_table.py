"""L6 descriptive pass (round 65): Var_zeros/Var_baseline of block statistics against block length, from outputs that
already exist. Reads only committed JSON; computes nothing new from zeros or matrices. DESCRIPTIVE: no verdict.

Rows:
  F3 route (a)      nearest-neighbour spacing law      zeros: results/read/run1 records[f].se[G]             (spacings)
  F4 (A)            next-nearest-neighbour law, s≤1.6  zeros: results/followup_read/A/run1 records[f].se[G]  (spacings)
  F6 corrected (B)  offset-averaged k3 at L* = 4       zeros: results/b2_read/run1 records[f].se[G]          (unfolded units)
     baseline for these three: the declared calibration's mean bootstrap SE at G over its 200 CUE_1000 replicates
     (se_boot_mean). The calibration's sequences are independent, randomly rotated 1,000-level matrices laid end to end,
     so a block of G ≥ ~1,000 levels sees no correlation beyond one matrix. Round 65 marked those cells
     "baseline invalid: stitched CUE_1000". Round 70 (L6_BASELINE_DESIGN.md §13): against the 50-sequence long CUE
     baseline, stitching does not change these statistics' block variance within ±14% at G = 1,000 and ±30% at
     G = 10,000, so they are marked "valid within stated sensitivity".
  R2 bins R1–R5     drift-removed pair-sum bootstrap SD   zeros: ph2r2/results/longbase_v2/zeros_R*_L1000000.json
     baseline: the 10⁶-level Dumitriu–Edelman GUE sequences of ph2r2/longbase.py v2 (PH2R2_FINDINGS §6), mapped onto
     each bin's heights and run through identical code. One long sequence per seed, so no block is stitched: every G is
     valid against this baseline.

ratio(G) = (SD_zeros(G) / SD_baseline(G))², i.e. Var_zeros/Var_baseline at block length G.
  cs4 rows: per file (the zeros' own bootstrap SE over the CUE replicates' mean bootstrap SE, same file geometry, same
  estimator, μ units); summary = geometric mean over files and the range.
  R2 rows: per bin, mean over zeros windows / mean over GUE sequences, with a delta-method SE from their spreads.

  python l6_table.py      → results/l6_table.json, results/L6_TABLE.md
"""
import glob
import json
import math
import os

import numpy as np

LONG_FLAG = "disjoint-block global-mean estimator (round 73; L6_BIAS_CORRECTION.md)"
VALID_FLAG = "valid within stated sensitivity (stitched/long within ±14% at G = 1,000, ±30% at G = 10,000; §13)"

HERE = os.path.dirname(os.path.abspath(__file__))
CS4 = os.path.join(HERE, "..", "cs4")
R2 = os.path.join(HERE, "..", "ph2r2")
STITCH = 1000            # CUE_1000: blocks of G ≥ this many levels see no long-range rigidity in the baseline
CS4_ROWS = [
    ("F3", "route (a)", "nearest-neighbour spacing law", "results/read/run1/ROUTE_A_READ.json",
     "results/calib/route_a_calib_declared.json", "spacings"),
    ("F4", "(A)", "next-nearest-neighbour spacing law, s ≤ 1.6", "results/followup_read/A/run1/FOLLOWUP_READ.json",
     "results/calib/followup_calib_A_declared.json", "spacings"),
    ("F6", "corrected (B)", "offset-averaged k3 of the count, L* = 4", "results/b2_read/run1/B2_READ.json",
     "results/calib/b2_calib_declared.json", "unfolded units"),
]


def sha(p):
    import hashlib
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def cs4_row(fs, test, obs, read_p, cal_p, unit):
    rd = json.load(open(os.path.join(CS4, read_p)))["records"]
    cal = json.load(open(os.path.join(CS4, cal_p)))["files"]
    Gs = sorted({int(g) for f in rd for g in rd[f]["se"]})
    per = {}
    for f in rd:
        per[f] = {str(G): (rd[f]["se"][str(G)] / cal[f]["se_boot_mean"][str(G)]) ** 2 for G in Gs}
    cells = {}
    for G in Gs:
        v = np.array([per[f][str(G)] for f in rd])
        cells[str(G)] = dict(geomean=float(np.exp(np.log(v).mean())), min=float(v.min()), max=float(v.max()),
                             n_files=len(v), valid=True,
                             flag=None if G < STITCH else VALID_FLAG)
    return dict(set=fs, test=test, observable=obs, unit=unit, baseline="CUE_1000 calibration (200 replicates), "
                "mean bootstrap SE", inputs={read_p: sha(os.path.join(CS4, read_p)), cal_p: sha(os.path.join(CS4, cal_p))},
                per_file=per, cells=cells)


def long_rows():
    """Round 73: zeros/long against the 50-sequence long CUE baseline (L6_BASELINE_DESIGN.md §13): G = 300 and 1,000 from
    the per-sequence moving-block bootstrap (compare.json; G/n <= 0.01), G = 3,000 and 10,000 from the disjoint-block
    global-mean estimator (L6_BIAS_CORRECTION.md, results/r73/R73_SUMMARY.json)."""
    cp = os.path.join(HERE, "results", "base", "compare.json")
    rp = os.path.join(HERE, "results", "r73", "R73_SUMMARY.json")
    cmp_, r73 = json.load(open(cp)), json.load(open(rp))
    out = []
    for (fs, test, obs, _, _, unit), key in zip(CS4_ROWS, ("route_a", "A", "B2")):
        files = list(cmp_["tests"][key])
        cells = {}
        for G in ("300", "1000", "3000", "10000"):
            if G in ("300", "1000"):
                v = np.array([cmp_["tests"][key][f][G]["zeros_over_long"] for f in files])
            else:
                v = np.array([r73["tests"][key][f][G]["zeros_over_long_revised"] for f in files])
            cells[G] = dict(geomean=float(np.exp(np.log(v).mean())), min=float(v.min()), max=float(v.max()),
                            n_files=len(v), valid=True, flag=None if G in ("300", "1000") else LONG_FLAG)
        out.append(dict(set=fs, test=test, observable=obs, unit=unit,
                        baseline="long CUE (50 x 10^5 CMV), zeros/long",
                        inputs={os.path.relpath(cp, HERE): sha(cp), os.path.relpath(rp, HERE): sha(rp)}, cells=cells))
    return out


def r2_rows():
    d = os.path.join(R2, "results", "longbase_v2")
    gue = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(d, "gue_L1000000_s*.json")))]
    out = []
    for b in ("R1", "R2", "R3", "R4", "R5"):
        zp = os.path.join(d, f"zeros_{b}_L1000000.json")
        z = json.load(open(zp))
        zw = z                                     # a list of per-window records
        cells = {}
        for G in ("100", "1000", "10000"):
            g = np.array([s["bins"][b]["boot_sd_drift_removed"][G] for s in gue])
            zz = np.array([w["boot_sd_drift_removed"][G] for w in zw])
            mz, mg = zz.mean(), g.mean()
            sez, seg = zz.std(ddof=1) / math.sqrt(len(zz)), g.std(ddof=1) / math.sqrt(len(g))
            r = (mz / mg) ** 2
            se = r * 2 * math.sqrt((sez / mz) ** 2 + (seg / mg) ** 2)
            cells[G] = dict(ratio=float(r), se=float(se), n_zeros_windows=len(zz), n_gue_seqs=len(g), valid=True,
                            flag=None)
        out.append(dict(set="R2 bins (seen)", test=f"R2 bin {b}", observable="drift-removed pair-sum bootstrap SD",
                        unit="levels", baseline="10^6-level DE GUE (longbase v2), one sequence per seed",
                        inputs={os.path.relpath(zp, HERE): sha(zp)}, cells=cells))
    return out


def main():
    rows = [cs4_row(*r) for r in CS4_ROWS] + long_rows() + r2_rows()
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(dict(round=65, revised_round=73, stitch_levels=STITCH, rows=rows), open(os.path.join(HERE, "results", "l6_table.json"), "w"),
              indent=1)
    L = ["| set / test | observable | baseline | " + " | ".join(f"G = {g}" for g in ("100", "300", "1000", "3000", "10000"))
         + " |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        c = []
        for G in ("100", "300", "1000", "3000", "10000"):
            x = r["cells"].get(G)
            if x is None:
                c.append("—")
            elif "geomean" in x:
                s = f"{x['geomean']:.2f} ({x['min']:.2f}–{x['max']:.2f})"
                c.append(s if not x.get("flag") else f"{s} {'‡' if x['flag'] == LONG_FLAG else '†'}")
            else:
                c.append(f"{x['ratio']:.2f} ± {x['se']:.2f}")
        L.append(f"| {r['set']} {r['test']} | {r['observable']} | {r['baseline'].split(',')[0]} | " + " | ".join(c) + " |")
    L += ["", "† valid within stated sensitivity: stitched CUE_1000 and the long CUE baseline agree within ±14% at "
          "G = 1,000 and ±30% at G = 10,000 for these three statistics (round 70; L6_BASELINE_DESIGN.md §13). "
          "Round 65 had marked these cells invalid.",
          "", "‡ revised (round 73): long-baseline variance from disjoint blocks about the global mean, free of the "
          "per-sequence bootstrap's mean-subtraction bias (L6_BIAS_CORRECTION.md). G = 300 and 1,000 in these rows are "
          "the per-sequence bootstrap (G/n ≤ 0.01)."]
    open(os.path.join(HERE, "results", "L6_TABLE.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
