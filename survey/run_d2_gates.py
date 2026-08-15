"""Survey arc D2 runner: the FIX-2 weights gate, red-and-green.  COMMITTED
GENERATOR of survey/d2_gates_measured.json.  Runs only against the seal.

Three arms (seal d2_fix2_gates):
  RIGHT lens      — weighted expectations; must stay within the D1 arms.
  WRONG-real      — unweighted expectations at real DESI weight amplitude;
                    REGISTERED EXPECTATION near-inert (mean weight 1.005);
                    filed as the amplitude observation either way (the B2
                    thin-window observation's analog).
  WRONG-powered   — synthetic weight gradient injected (w *= 1 + 0.5*(x/5));
                    right lens (gradient known to expectations) within arms;
                    wrong lens (gradient ignored) must push F above right by
                    >= 5 sigma at some sealed L in EVERY test tile -> FIRED.
"""

import json
import sys

import numpy as np

SV = "/home/combust/fmexplorer/criticality_tool/survey"
sys.path.insert(0, SV)
from survey_io import load_cat, load_randoms_split          # noqa: E402
from tiling import build_tiles, tile_points                 # noqa: E402
from estimators import cells_F                              # noqa: E402
from mask_kag import thin_to_data, ZLO, ZHI                 # noqa: E402

SEAL = json.load(open(f"{SV}/prereg_sealed.json"))
L_LIST = SEAL["scale_ranges"]["sigma2_L_deg"]
manifest = json.load(open(f"{SV}/MANIFEST.json"))

nulls = load_randoms_split("null_half", ZLO, ZHI, manifest)
kagr = load_randoms_split("kag_half", ZLO, ZHI, manifest)
data = load_cat("LRG_NGC_clustering.dat.fits", ZLO, ZHI)
null_per_deg2 = nulls["w"].sum() / 3464.9234532477117
tiles = build_tiles(nulls["ra"], nulls["dec"], nulls["w"], null_per_deg2)
tiles_sorted = sorted(tiles, key=lambda t: t["dec0"])
sel = {0, 1, len(tiles) - 2, len(tiles) - 1,
       len(tiles) // 4, len(tiles) // 2, 3 * len(tiles) // 4}
test_tiles = [tiles_sorted[i] for i in sorted(sel)]
thinned = thin_to_data(kagr, float(data["w"].sum()), seed=20260815)

res = dict(seal_cited=f"{SV}/prereg_sealed.json", arms={})


def run_arm(tag, wd_fn, wr_fn):
    rows = []
    for t in test_tiles:
        xy_d, w_d = tile_points(thinned, t)
        xy_r, w_r = tile_points(nulls, t)
        w_d, w_r = wd_fn(xy_d, w_d), wr_fn(xy_r, w_r)
        ext = (xy_r[:, 0].min(), xy_r[:, 0].max(),
               xy_r[:, 1].min(), xy_r[:, 1].max())
        Fs = []
        for L in L_LIST:
            out = cells_F(xy_d, w_d, xy_r, w_r, L, ext)
            Fs.append(dict(L=L, F=out["F"], sigma=out["sigma_F"],
                           z=(out["F"] - 1.0) / out["sigma_F"]))
        rows.append(dict(dec0=t["dec0"], ra0=t["ra0"], F=Fs,
                         worst_z=float(max(abs(f["z"]) for f in Fs))))
        print(f"  [{tag}] tile ({t['ra0']:.0f},{t['dec0']:.0f}) "
              f"F={['%.3f' % f['F'] for f in Fs]}", flush=True)
    return rows


ident = lambda xy, w: w
grad = lambda xy, w: w * (1.0 + 0.5 * (xy[:, 0] / 5.0))

print("RIGHT lens (weighted expectations):", flush=True)
right = run_arm("right", ident, ident)
res["arms"]["right"] = right
right_ok = all(r["worst_z"] <= 4.5 for r in right)

print("WRONG-real (unweighted expectations, real amplitude):", flush=True)
wrong_real = run_arm("wrong_real", ident, lambda xy, w: np.ones_like(w))
res["arms"]["wrong_real"] = wrong_real
dz_real = [max(abs(a["F"][i]["F"] - b["F"][i]["F"]) /
               np.hypot(a["F"][i]["sigma"], b["F"][i]["sigma"])
               for i in range(len(L_LIST)))
           for a, b in zip(wrong_real, right)]
res["wrong_real_max_dz"] = float(max(dz_real))

print("POWERED: right lens (gradient known):", flush=True)
p_right = run_arm("p_right", grad, grad)
print("POWERED: wrong lens (gradient ignored in expectations):", flush=True)
p_wrong = run_arm("p_wrong", grad, ident)
res["arms"]["powered_right"] = p_right
res["arms"]["powered_wrong"] = p_wrong
p_right_ok = all(r["worst_z"] <= 4.5 for r in p_right)
fired_per_tile = []
for a, b in zip(p_wrong, p_right):
    dz = max((a["F"][i]["F"] - b["F"][i]["F"]) /
             np.hypot(a["F"][i]["sigma"], b["F"][i]["sigma"])
             for i in range(len(L_LIST)))
    fired_per_tile.append(dz >= 5.0)
fired = all(fired_per_tile)

res.update(right_ok=bool(right_ok), powered_right_ok=bool(p_right_ok),
           powered_fired=bool(fired),
           PASS=bool(right_ok and p_right_ok and fired))
json.dump(res, open(f"{SV}/d2_gates_measured.json", "w"), indent=1)
print(f"D2: right_ok={right_ok} wrong_real max dz={res['wrong_real_max_dz']:.2f} "
      f"powered_right_ok={p_right_ok} powered FIRED={fired} "
      f"PASS={res['PASS']}", flush=True)
