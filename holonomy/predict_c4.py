"""C4 sealed prediction — COMMITTED CONTINUUM DERIVATION, written and run
BEFORE the C4 measurement (prediction-first).

Pair C4 (census-found, brief-registered, unmeasured until now):
    window -> project   (deployed: survey/tiling.tile_points cuts in
                         (ra, dec) THEN gnomonic-projects)
  vs
    project -> window   (project the whole footprint, then cut the same
                         nominal box in PLANE coordinates)

Mechanism: a rectangle in (ra, dec) does not map to a rectangle under the
gnomonic projection.  Cutting first selects the sky-rectangle; cutting after
selects the plane-rectangle.  The two regions agree near the tile centre and
disagree near the corners, so a point set's membership differs on the
symmetric difference of the two regions.

Continuum prediction (deterministic, no point noise): the ORDER-SENSITIVE
FRACTION is the symmetric-difference area over the tile area,

    q(TILE) = |A_sky XOR A_plane| / |A_sky| ,

computed by exact numerical quadrature on the sphere (uniform-in-solid-angle
measure) for each sealed tile size.  For a uniform process the expected
membership difference is q * n_tile, and the leading small-angle behaviour is
q = O(theta^2) with theta the tile half-angle in radians (the gnomonic radial
scale factor is sec^2(c) = 1 + c^2 + O(c^4), so the boundary displacement is
second order and the corner-region area follows).
"""

import json
import sys

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, f"{ROOT}/survey")
from tiling import gnomonic                                    # noqa: E402

TILES = [5.0, 10.0, 20.0, 30.0]          # sealed dial ladder (degrees)
DEC0 = 0.0                                # tile centre declination
NQ = 3000                                 # quadrature resolution per axis


def q_symmetric_difference(tile, dec0=DEC0, nq=NQ):
    """|A_sky XOR A_plane| / |A_sky| by solid-angle quadrature.

    A_sky   : |ra - ra0| <= tile/2 / cos(dec)  and  |dec - dec0| <= tile/2
              (the deployed tiling's box: RA spacing tile/cos(dec_centre))
    A_plane : |x| <= tile/2 and |y| <= tile/2 in gnomonic plane degrees
    """
    half = tile / 2.0
    dra = tile / np.cos(np.radians(dec0))
    # sample generously beyond both boxes so the XOR is fully covered
    ra = np.linspace(-0.9 * dra, 0.9 * dra, nq)
    dec = np.linspace(dec0 - 0.9 * tile, dec0 + 0.9 * tile, nq)
    RA, DEC = np.meshgrid(ra, dec, indexing="ij")
    w = np.cos(np.radians(DEC))                      # solid-angle weight
    in_sky = (np.abs(RA) <= dra / 2.0) & (np.abs(DEC - dec0) <= half)
    x, y = gnomonic(RA, DEC, 0.0, dec0)
    in_plane = (np.abs(x) <= half) & (np.abs(y) <= half)
    a_sky = float((w * in_sky).sum())
    a_xor = float((w * (in_sky ^ in_plane)).sum())
    return a_xor / a_sky, a_sky, a_xor


def main():
    rows = {}
    for t in TILES:
        q, a_sky, a_xor = q_symmetric_difference(t)
        theta = np.radians(t / 2.0)
        rows[f"tile{t:g}"] = dict(tile_deg=t, q_pred=q,
                                  theta_half_rad=float(theta),
                                  q_over_theta2=float(q / theta ** 2))
        print(f"  TILE={t:5.1f} deg: q = {q:.5f}  "
              f"(q/theta^2 = {q / theta ** 2:.3f})")
    out = dict(pair="C4 window<->project", tiles=TILES, dec0=DEC0, nq=NQ,
               prediction=rows,
               note="q = expected fraction of points whose tile membership "
                    "differs between the two orderings, for a uniform "
                    "process; leading order O(theta^2).")
    json.dump(out, open(f"{ROOT}/holonomy/c4_prediction.json", "w"), indent=1)


if __name__ == "__main__":
    main()
