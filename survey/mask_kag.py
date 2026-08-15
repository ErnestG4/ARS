"""Survey arc D1: the mask KAG — the witness that can fail (brief §3 D1).

Gate (ratio form, leading): thinned-randoms-as-data through the FULL
estimator stack against the disjoint measurement-null randoms half must
return DD/RR == 1 in expectation within tolerance; corollaries g == 1,
K_ratio == 1, F(L) == 1.

Construction:
  * "data"  = kag_half randoms (files 0,2,4,6), thinned to the LRG slice's
    effective weighted intensity (keep-prob p = W_data/W_kag), carrying
    their weights — Poisson-through-the-actual-window by construction.
  * null    = null_half randoms (files 1,3,5,7) — the SAME half measurement
    uses, so the KAG certifies the exact configuration that measures
    (tripwire 2: halves disjoint by file index).
  * Tiles   = the sealed tiling built from the null half.

Arms (comb-pattern, correlation-aware):
  (i)  per-tile worst |z| over g bins and F(L) values, multiplicity-aware;
  (ii) across-tile grand mean z, self-calibrated from tile scatter (tiles are
       the independent axis; within-tile bins are correlated).

RED PATH (witness-must-be-able-to-fail, demonstrated deliberately once):
the same thinned data evaluated against a UNIFORM-BOX pseudo-randoms set
over each tile's bounding box — the forbidden analytic window (tripwire 6).
The gate MUST fire red: mask holes enter DD but not the uniform RR, so the
ratio and F blow up.  A red path that does not fire fails the KAG itself.

PROJECTION TWIN (sealed dry-run, §6): the same green-path gate run on the
accepted tiles at the declination EXTREMES, confirming the gnomonic
distortion budget covers what it claims.
"""

import json
import sys

import numpy as np

SV = "/home/combust/fmexplorer/criticality_tool/survey"
sys.path.insert(0, SV)
from survey_io import load_cat, load_randoms_split          # noqa: E402
from tiling import build_tiles, tile_points, TILE           # noqa: E402
from estimators import g_ratio, cells_F                     # noqa: E402

ZLO, ZHI = 0.6, 0.8
BINS = np.arange(0.05, 1.001, 0.05)      # plane deg; r_min seal (0.05 deg)
L_LIST = [0.1, 0.2, 0.5, 1.0]


def thin_to_data(kag, w_target, seed):
    rng = np.random.default_rng(seed)
    p = w_target / kag["w"].sum()
    keep = rng.uniform(size=len(kag["w"])) < p
    return {k: v[keep] for k, v in kag.items()}


def run_tile(xy_d, w_d, xy_r, w_r, extent):
    res = g_ratio(xy_d, w_d, xy_r, w_r, BINS)
    zs = []
    # Poisson z per g bin: sigma_g ~ g/sqrt(DD_pairs) (weights ~1)
    for gval, dd in zip(res["g"], res["DD"]):
        if dd > 25:
            zs.append((gval - 1.0) * np.sqrt(dd))
    Fs = []
    for L in L_LIST:
        out = cells_F(xy_d, w_d, xy_r, w_r, L, extent)
        if out is not None:
            zF = (out["F"] - 1.0) / np.sqrt(2.0 / out["n_cells"])
            Fs.append(dict(L=L, F=out["F"], n_cells=out["n_cells"], z=zF))
            zs.append(zF)
    return res, Fs, zs


def kag(tiles, data_thinned, nulls, seed_tag, red_path=False, rng_seed=0):
    rows = []
    for t in tiles:
        xy_d, w_d = tile_points(data_thinned, t)
        if red_path:
            # forbidden analytic window: uniform box pseudo-randoms
            rng = np.random.default_rng(rng_seed + 1)
            n_fake = 20 * len(xy_d)
            r0, r1 = t["ra_range"]
            d0, d1 = t["dec_range"]
            ra = rng.uniform(r0, r1, n_fake)
            dec = np.degrees(np.arcsin(rng.uniform(
                np.sin(np.radians(d0)), np.sin(np.radians(d1)), n_fake)))
            from tiling import gnomonic
            x, y = gnomonic(ra, dec, t["ra0"], t["dec0"])
            xy_r, w_r = np.column_stack([x, y]), np.ones(n_fake)
        else:
            xy_r, w_r = tile_points(nulls, t)
        if len(xy_d) < 500:
            continue
        ext = (xy_r[:, 0].min(), xy_r[:, 0].max(),
               xy_r[:, 1].min(), xy_r[:, 1].max())
        res, Fs, zs = run_tile(xy_d, w_d, xy_r, w_r, ext)
        rows.append(dict(ra0=t["ra0"], dec0=t["dec0"], n_d=len(xy_d),
                         n_r=len(xy_r),
                         worst_z=float(max(abs(z) for z in zs)),
                         mean_z=float(np.mean(zs)),
                         F=[f["F"] for f in Fs],
                         g_max_dev=float(np.nanmax(np.abs(res["g"] - 1.0)))))
        print(f"  [{seed_tag}] tile ({t['ra0']:.0f},{t['dec0']:.0f}): "
              f"n_d={len(xy_d)} worst|z|={rows[-1]['worst_z']:.2f} "
              f"mean z={rows[-1]['mean_z']:+.2f} "
              f"F={['%.3f' % f['F'] for f in Fs]}", flush=True)
    worst = max(r["worst_z"] for r in rows)
    means = np.array([r["mean_z"] for r in rows])
    grand, sd = float(means.mean()), float(means.std(ddof=1))
    thresh = max(3.0 * sd / np.sqrt(len(rows)), 0.3)
    ok = worst <= 4.5 and abs(grand) <= thresh
    return dict(rows=rows, worst_z=float(worst), grand_mean_z=grand,
                bias_threshold=float(thresh), PASS=bool(ok))
