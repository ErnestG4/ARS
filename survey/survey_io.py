"""Survey arc: catalog IO.  Loads (RA, DEC, Z, WEIGHT) from DESI DR1 LSS
clustering FITS files and applies the sealed redshift slice.

Sealed conventions (brief §2, D0):
  * Data weight = WEIGHT (the released combined completeness x systematics x
    zfail clustering weight).  WEIGHT_FKP is NOT used — FKP optimizes P(k)
    estimation and is not part of the window/selection definition.
  * Randoms weight = WEIGHT from the matched clustering randoms.
  * One transition per path: slicing here; all downstream code receives
    already-sliced arrays and never re-cuts.
"""

import numpy as np
from astropy.io import fits

SV = "/home/combust/fmexplorer/criticality_tool/survey"


def load_cat(filename, zlo=None, zhi=None):
    """Returns dict(ra, dec, z, w) as float64 arrays, sliced if bounds given."""
    with fits.open(f"{SV}/{filename}", memmap=True) as hdul:
        d = hdul[1].data
        ra = np.asarray(d["RA"], dtype=np.float64)
        dec = np.asarray(d["DEC"], dtype=np.float64)
        z = np.asarray(d["Z"], dtype=np.float64)
        w = np.asarray(d["WEIGHT"], dtype=np.float64)
    if zlo is not None:
        m = (z >= zlo) & (z < zhi)
        ra, dec, z, w = ra[m], dec[m], z[m], w[m]
    return dict(ra=ra, dec=dec, z=z, w=w)


def load_randoms_split(half, zlo, zhi, manifest):
    """Concatenate the sealed 4-file randoms half ('kag_half'|'null_half'),
    sliced.  Tripwire 2: the two halves are disjoint by file index."""
    idx = manifest["randoms_split"][half]
    parts = [load_cat(f"LRG_NGC_{i}_clustering.ran.fits", zlo, zhi) for i in idx]
    return {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
