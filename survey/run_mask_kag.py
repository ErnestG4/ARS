"""Survey arc D1 runner.  COMMITTED GENERATOR of survey/mask_kag_measured.json.

Sequence (all D1, no science measurement anywhere — the only touch of the
data catalog is its total slice weight, used as the thinning target):
  1. build the sealed tiling from the measurement-null randoms half;
  2. GREEN gate: thinned kag-half randoms as data vs null half — DD/RR == 1
     within the self-calibrated arms, on a KAG tile set that includes the
     declination extremes (the projection twin is thereby part of the gate,
     not an afterthought);
  3. RED path: same data vs the forbidden uniform-box analytic window —
     the gate MUST fire (witness-must-be-able-to-fail, demonstrated once);
  4. Q5 decision filed from the numbers.
"""

import json
import sys

import numpy as np

SV = "/home/combust/fmexplorer/criticality_tool/survey"
sys.path.insert(0, SV)
from survey_io import load_cat, load_randoms_split          # noqa: E402
from tiling import build_tiles, corner_distortion           # noqa: E402
from mask_kag import kag, thin_to_data, ZLO, ZHI            # noqa: E402

manifest = json.load(open(f"{SV}/MANIFEST.json"))
res = dict(slice=[ZLO, ZHI], corner_distortion=float(corner_distortion()))

print("loading randoms halves + data slice weight...", flush=True)
nulls = load_randoms_split("null_half", ZLO, ZHI, manifest)
kagr = load_randoms_split("kag_half", ZLO, ZHI, manifest)
data = load_cat("LRG_NGC_clustering.dat.fits", ZLO, ZHI)
W_target = float(data["w"].sum())
res["W_data_slice"] = W_target
res["n_null_randoms"] = int(len(nulls["w"]))
print(f"data slice W={W_target:.0f} n={len(data['w'])}; "
      f"null randoms n={len(nulls['w'])}; kag randoms n={len(kagr['w'])}",
      flush=True)

# randoms surface density of the null half, effective-area convention
# (area from the released nz-file header: effective 3464.92 deg^2)
null_per_deg2 = nulls["w"].sum() / 3464.9234532477117

tiles = build_tiles(nulls["ra"], nulls["dec"], nulls["w"], null_per_deg2)
res["n_tiles_accepted"] = len(tiles)
print(f"tiles accepted: {len(tiles)} (corner distortion "
      f"{res['corner_distortion']:.4f} <= 0.02)", flush=True)

# KAG tile set: declination extremes (projection twin) + spread of middles
tiles_sorted = sorted(tiles, key=lambda t: t["dec0"])
sel = {0, 1, len(tiles) - 2, len(tiles) - 1,
       len(tiles) // 4, len(tiles) // 2, 3 * len(tiles) // 4}
kag_tiles = [tiles_sorted[i] for i in sorted(sel) if 0 <= i < len(tiles)]
res["kag_tiles_dec"] = [t["dec0"] for t in kag_tiles]
print("KAG tile declinations:", res["kag_tiles_dec"], flush=True)

thinned = thin_to_data(kagr, W_target, seed=20260815)
res["n_thinned"] = int(len(thinned["w"]))

print("GREEN gate:", flush=True)
green = kag(kag_tiles, thinned, nulls, "green")
res["green"] = green
print(f"GREEN: worst|z|={green['worst_z']:.2f} grand mean z="
      f"{green['grand_mean_z']:+.3f} (thr {green['bias_threshold']:.3f}) "
      f"PASS={green['PASS']}", flush=True)

print("RED path (forbidden analytic window — must fire):", flush=True)
red = kag(kag_tiles[:3], thinned, None, "red", red_path=True)
res["red"] = dict(worst_z=red["worst_z"], fired=bool(red["worst_z"] > 4.5))
print(f"RED: worst|z|={red['worst_z']:.2f} fired={res['red']['fired']}",
      flush=True)

res["PASS"] = bool(green["PASS"] and res["red"]["fired"])
with open(f"{SV}/mask_kag_measured.json", "w") as f:
    json.dump(res, f, indent=1)
print("D1 MASK KAG:", "PASS" if res["PASS"] else "FAIL", flush=True)
