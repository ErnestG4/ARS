"""Survey arc D1/D3: randoms-backed ratio estimators on tile tangent planes.

Sealed estimator forms (brief §1 null implementation):
  pcf:   g_hat(r-bin) = [DD(bin)/W_D^2] / [RR(bin)/W_R^2]   (natural
         DD/RR estimator; weighted pair counts, unordered, canonical no
         self-pairs).  The window — every hole and edge — cancels in the
         ratio; this is the identity the mask KAG certifies (DD/RR == 1 on
         thinned randoms).
  K:     K_hat(r) = cumulative version of the same ratio times pi r^2's
         reference — reported as the cumulative ratio; Poisson reference 1.
  Sigma^2 (carries the class): counts-in-cells on a non-overlapping square
         grid of side L: F_hat(L) = Var_c[N_c - E_c] / (w2bar * mean_c E_c),
         E_c = (W_D/W_R) * RR_mass(cell), w2bar = sum(w^2)/sum(w) of data
         weights.  Weighted-Poisson reference: F == 1.  Cells with
         E_c < CELL_FLOOR * median(E_c) excluded by sealed rule (mask holes).

DIM=2 plane degrees throughout.  No analytic window anywhere (tripwire 6).
"""

import numpy as np
from scipy.spatial import cKDTree

CELL_FLOOR = 0.2


def pair_counts(xy_a, w_a, xy_b, w_b, bins, same=False):
    """Weighted pair counts binned by plane separation, via the dual-tree
    C-speed cKDTree.count_neighbors (a python pair loop cannot survive RR at
    ~4e5 randoms/tile).  Cumulative ordered counts are differenced per bin;
    self-pair weight (distance 0, included in every cumulative value when
    bins[0] > 0) cancels in the differences.  same=True halves ordered to
    unordered."""
    ta, tb = cKDTree(xy_a), cKDTree(xy_b)
    cum = ta.count_neighbors(tb, np.asarray(bins, float),
                             weights=(w_a, w_b), cumulative=True)
    per_bin = np.diff(cum)
    if same:
        per_bin = per_bin / 2.0
    return per_bin


def g_ratio(xy_d, w_d, xy_r, w_r, bins):
    """Natural DD/RR estimator per bin + cumulative-ratio K analog."""
    WD, WR = w_d.sum(), w_r.sum()
    DD = pair_counts(xy_d, w_d, xy_d, w_d, bins, same=True)
    RR = pair_counts(xy_r, w_r, xy_r, w_r, bins, same=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        g = (DD / WD**2) / (RR / WR**2)
        Kratio = (np.cumsum(DD) / WD**2) / (np.cumsum(RR) / WR**2)
    return dict(centers=0.5 * (bins[:-1] + bins[1:]), g=g, K_ratio=Kratio,
                DD=DD, RR=RR, WD=float(WD), WR=float(WR))


def cells_F(xy_d, w_d, xy_r, w_r, L, extent):
    """Counts-in-cells F_hat(L) on a non-overlapping grid over [x0,x1]x[y0,y1].
    Returns F, n_cells, plus per-cell arrays for diagnostics."""
    x0, x1, y0, y1 = extent
    nx = max(int((x1 - x0) / L), 1)
    ny = max(int((y1 - y0) / L), 1)
    if nx < 2 or ny < 2:
        return None

    def grid_mass(xy, w):
        ix = np.floor((xy[:, 0] - x0) / L).astype(int)
        iy = np.floor((xy[:, 1] - y0) / L).astype(int)
        m = (ix >= 0) & (ix < nx) & (iy >= 0) & (iy < ny)
        H = np.zeros((nx, ny))
        np.add.at(H, (ix[m], iy[m]), w[m])
        return H

    Nd = grid_mass(xy_d, w_d)
    Rr = grid_mass(xy_r, w_r)
    scale = w_d.sum() / w_r.sum()
    E = Rr * scale
    keep = E >= CELL_FLOOR * np.median(E[E > 0])
    if keep.sum() < 8:
        return None
    resid = (Nd - E)[keep]
    w2bar = float((w_d**2).sum() / w_d.sum())
    F = float(resid.var(ddof=1) / (w2bar * E[keep].mean()))
    return dict(L=float(L), F=F, n_cells=int(keep.sum()),
                mean_E=float(E[keep].mean()))
