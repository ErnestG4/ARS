"""Survey arc D1: tiling scheme — tangent-plane (gnomonic) sub-patches as
replicates (brief §3 D1).

Tile grid: dec rows of height TILE deg; within a row, RA spacing TILE/cos(dec)
so every tile subtends ~TILE x TILE true degrees.  Gnomonic projection about
each tile centre maps (ra, dec) -> plane coordinates in degrees.

Distortion budget (sealed): the gnomonic radial scale factor is sec^2(c) at
angular distance c from the tile centre; at a corner of a 10x10 tile,
c ~= 7.07 deg -> sec^2 = 1.0154, i.e. +1.5% at the extreme corner.  Sealed
budget: max scale distortion <= 2.0% (all 10x10 tiles pass by construction;
the budget exists so a larger tile choice CANNOT silently exceed it).
Because BOTH data and randoms are projected identically, metric distortion
cancels in every DD/RR ratio at fixed plane separation — the budget bounds
tile-to-tile comparability, not estimator bias (ratio-form virtue, brief §1).

Acceptance rules (sealed, applied BEFORE measurement, tripwire 3):
  * effective area (from randoms mass) >= MIN_EFF_AREA of nominal;
  * distortion budget as above;
  * weight-variation budget applied in D2.
"""

import numpy as np

TILE = 10.0                 # deg
MAX_SCALE_DISTORTION = 0.02
MIN_EFF_FRACTION = 0.60     # effective/nominal area to accept a tile


def gnomonic(ra, dec, ra0, dec0):
    """Gnomonic projection (degrees in, plane degrees out)."""
    ra, dec = np.radians(ra), np.radians(dec)
    ra0, dec0 = np.radians(ra0), np.radians(dec0)
    cosc = (np.sin(dec0) * np.sin(dec)
            + np.cos(dec0) * np.cos(dec) * np.cos(ra - ra0))
    x = np.cos(dec) * np.sin(ra - ra0) / cosc
    y = (np.cos(dec0) * np.sin(dec)
         - np.sin(dec0) * np.cos(dec) * np.cos(ra - ra0)) / cosc
    return np.degrees(x), np.degrees(y)


def corner_distortion():
    """Max gnomonic scale error for a TILE x TILE tile (at the corner)."""
    c = np.radians(np.hypot(TILE / 2, TILE / 2))
    return 1.0 / np.cos(c) ** 2 - 1.0


def build_tiles(ran_ra, ran_dec, ran_w, randoms_per_deg2):
    """Tile centres from dec rows x RA columns covering the randoms footprint;
    acceptance by sealed rules.  Returns list of dicts."""
    assert corner_distortion() <= MAX_SCALE_DISTORTION, "distortion budget"
    tiles = []
    dec_lo = np.floor(ran_dec.min() / TILE) * TILE
    dec_hi = np.ceil(ran_dec.max() / TILE) * TILE
    for d0 in np.arange(dec_lo, dec_hi, TILE):
        dc = d0 + TILE / 2
        if abs(dc) > 80:                      # RA compression blowup guard
            continue
        dra = TILE / np.cos(np.radians(dc))
        row = (ran_dec >= d0) & (ran_dec < d0 + TILE)
        if not row.any():
            continue
        ra_lo = np.floor(ran_ra[row].min() / dra) * dra
        ra_hi = np.ceil(ran_ra[row].max() / dra) * dra
        for r0 in np.arange(ra_lo, ra_hi, dra):
            rc = r0 + dra / 2
            m = row & (ran_ra >= r0) & (ran_ra < r0 + dra)
            eff_area = ran_w[m].sum() / randoms_per_deg2
            nominal = TILE * TILE
            if eff_area / nominal < MIN_EFF_FRACTION:
                continue
            tiles.append(dict(ra0=float(rc), dec0=float(dc),
                              ra_range=(float(r0), float(r0 + dra)),
                              dec_range=(float(d0), float(d0 + TILE)),
                              eff_area=float(eff_area)))
    return tiles


def tile_points(cat, tile):
    """Select catalog points in a tile and project them; returns (xy, w)."""
    r0, r1 = tile["ra_range"]
    d0, d1 = tile["dec_range"]
    m = ((cat["ra"] >= r0) & (cat["ra"] < r1)
         & (cat["dec"] >= d0) & (cat["dec"] < d1))
    x, y = gnomonic(cat["ra"][m], cat["dec"][m], tile["ra0"], tile["dec0"])
    return np.column_stack([x, y]), cat["w"][m]
