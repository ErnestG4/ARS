"""P3 shared machinery: load-once survey objects + the F path.

Tripwire 7 (brief §5): survey/ frozen files are exercised through public
surfaces only (load_cat, load_randoms_split, build_tiles, tile_points,
cells_F); null_half is loaded READ-ONLY via the frozen loader as the fixed
reference (Q2 ruling) and never enters a manipulated path; nothing under
survey/ is written.  The LRG catalog contributes exactly two scalars
(W_data, N_data — the thinning targets, same role as in the D1 KAG); no
catalog row enters any measured point set.
"""

import json
import sys

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
SV = f"{ROOT}/survey"
for p in (ROOT, f"{ROOT}/holonomy", SV):
    if p not in sys.path:
        sys.path.insert(0, p)

from survey_io import load_cat, load_randoms_split          # noqa: E402
from tiling import build_tiles, tile_points                 # noqa: E402
from estimators import cells_F                              # noqa: E402

ZLO, ZHI = 0.6, 0.8            # the survey arc's sealed primary slice
FOOTPRINT_DEG2 = 3464.9234532477117   # run_d3_measure.py:60 (frozen)


def load_all():
    """Data scalars + kag_half (manipulated object) + null_half (fixed
    reference) + the sealed tiling built from the null half (D3 semantics)."""
    manifest = json.load(open(f"{SV}/MANIFEST.json"))
    data = load_cat("LRG_NGC_clustering.dat.fits", ZLO, ZHI)
    scal = dict(W_data=float(data["w"].sum()), N_data=int(len(data["w"])),
                wbar_data=float(data["w"].mean()))
    del data                                   # rows leave scope immediately
    kag = load_randoms_split("kag_half", ZLO, ZHI, manifest)
    nulls = load_randoms_split("null_half", ZLO, ZHI, manifest)
    null_per_deg2 = nulls["w"].sum() / FOOTPRINT_DEG2
    tiles = build_tiles(nulls["ra"], nulls["dec"], nulls["w"], null_per_deg2)
    scal["wbar_kag"] = float(kag["w"].mean())
    scal["N_kag"] = int(len(kag["w"]))
    scal["W_kag"] = float(kag["w"].sum())
    return scal, kag, nulls, tiles


def pooled_F(thinned, nulls_by_tile, tiles, L_list):
    """Mean F over accepted tiles per L for a thinned point set, through the
    frozen tile_points/cells_F path.  nulls_by_tile: precomputed per-tile
    (xy_r, w_r, extent) — the fixed reference, computed once."""
    acc = {L: [] for L in L_list}
    for t, (xy_r, w_r, ext) in zip(tiles, nulls_by_tile):
        xy_d, w_d = tile_points(thinned, t)
        if len(xy_d) < 500:
            continue
        for L in L_list:
            out = cells_F(xy_d, w_d, xy_r, w_r, L, ext)
            if out is not None:
                acc[L].append(out["F"])
    return {L: float(np.mean(v)) for L, v in acc.items()}, \
           {L: len(v) for L, v in acc.items()}


def prep_null_tiles(nulls, tiles):
    out = []
    for t in tiles:
        xy_r, w_r = tile_points(nulls, t)
        ext = (xy_r[:, 0].min(), xy_r[:, 0].max(),
               xy_r[:, 1].min(), xy_r[:, 1].max())
        out.append((xy_r, w_r, ext))
    return out
