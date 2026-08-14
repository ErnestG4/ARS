"""Observer-B (spatial-statistics dialect) estimators, implemented in-house.

Bridge arc discipline (bridge/ brief §0, §3):
  * Every function carries an explicit DIM tag (tripwire 2: dimension slot errors).
  * Border (minus-sampling) correction throughout — bias-transparent, mandated for
    known-answer-gate runs by TOOLKIT.md §11.1.  spatstat cross-checks use its own
    corrections; comparisons are made on the border-corrected column.
  * One transition per data path (tripwire 1): 1-D inputs here are ALREADY in
    unit-mean (unfolded) coordinates when they came through the home dialect;
    2-D inputs are raw coordinates with an explicit intensity argument.
    No function in this module both unfolds and reweights.

References: Baddeley, Rubak & Turner, "Spatial Point Patterns" (2015) for the
K/L/pcf estimator forms; Torquato (2018) for the Σ²/hyperuniformity dictionary.
"""

import numpy as np
from scipy.spatial import cKDTree


# ── DIM=1 estimators (stationary, on an interval; intensity lam) ─────────────

def k_1d(points, r_grid, lam=None):
    """DIM=1. Ripley K, stationary 1-D form, border-corrected.
    K(r) = (1/lam) E[# further points within distance r of a typical point].
    Poisson reference: K(r) = 2r."""
    e = np.sort(np.asarray(points, float))
    lo, hi = e[0], e[-1]
    if lam is None:
        lam = (e.size - 1) / (hi - lo)
    rmax = float(r_grid[-1])
    core = e[(e >= lo + rmax) & (e <= hi - rmax)]          # border erosion
    if core.size == 0:
        raise ValueError("border erosion left no core points")
    idx = np.searchsorted(e, core)
    K = np.empty(len(r_grid))
    for j, r in enumerate(r_grid):
        left = np.searchsorted(e, core - r, side="left")
        right = np.searchsorted(e, core + r, side="right")
        K[j] = (right - left - 1).mean() / lam             # −1 removes the point itself
    return K


def pcf_1d(points, bins, lam=None):
    """DIM=1. Pair-correlation g(r) by pair-distance histogram, border-corrected.
    Poisson: g = 1.  GUE (unfolded, unit-mean): g(s) = 1 − (sin πs/πs)²
    (analytic-form owner: universality.py pair_correlation docstring)."""
    e = np.sort(np.asarray(points, float))
    lo, hi = e[0], e[-1]
    if lam is None:
        lam = (e.size - 1) / (hi - lo)
    rmax = float(bins[-1])
    core_mask = (e >= lo + rmax) & (e <= hi - rmax)
    core_idx = np.nonzero(core_mask)[0]
    counts = np.zeros(len(bins) - 1)
    # sorted-window scan: O(n · k) with k = points per rmax window, not O(n²)
    left = np.searchsorted(e, e[core_idx] - rmax, side="left")
    right = np.searchsorted(e, e[core_idx] + rmax, side="right")
    for i, lo_j, hi_j in zip(core_idx, left, right):
        d = np.abs(e[lo_j:hi_j] - e[i])
        d = d[d > 0]
        counts += np.histogram(d, bins=bins)[0]
    core = e[core_mask]
    dr = np.diff(bins)
    # expected pairs per core point per bin, Poisson at rate lam: lam * 2 dr
    g = counts / (core.size * lam * 2.0 * dr)
    centers = 0.5 * (bins[:-1] + bins[1:])
    return centers, g


def sigma2_from_g_1d(g_centers, g_vals, L, lam=1.0):
    """DIM=1 gluing identity (gate G-A3, 1-D form):
    Var N[0,L] = lam L + 2 lam² ∫₀ᴸ (L−s)(g(s)−1) ds   (stationary).
    Trapezoid on the empirical g grid; grid must reach s=L."""
    if g_centers[-1] < L:
        raise ValueError(f"g grid reaches {g_centers[-1]:.2f} < L={L}")
    m = g_centers <= L
    s, gv = g_centers[m], g_vals[m]
    integrand = (L - s) * (gv - 1.0)
    return lam * L + 2.0 * lam**2 * np.trapezoid(integrand, s)


# ── DIM=2 estimators (windowed planar patterns; intensity lam) ───────────────

class DiskWindow:
    """DIM=2 observation window: disk of radius R centred at origin."""
    def __init__(self, R): self.R = float(R)
    def area(self): return np.pi * self.R**2
    def dist_to_boundary(self, pts): return self.R - np.hypot(pts[:, 0], pts[:, 1])
    def contains(self, pts): return self.dist_to_boundary(pts) >= 0


class RectWindow:
    """DIM=2 observation window: [0,Lx]×[0,Ly]."""
    def __init__(self, Lx, Ly): self.Lx, self.Ly = float(Lx), float(Ly)
    def area(self): return self.Lx * self.Ly
    def dist_to_boundary(self, pts):
        return np.minimum.reduce([pts[:, 0], self.Lx - pts[:, 0],
                                  pts[:, 1], self.Ly - pts[:, 1]])
    def contains(self, pts): return self.dist_to_boundary(pts) >= 0


class WedgeWindow:
    """DIM=2 observation window: annular sector r∈[R1,R2], θ∈[t1,t2]."""
    def __init__(self, R1, R2, t1, t2):
        self.R1, self.R2, self.t1, self.t2 = map(float, (R1, R2, t1, t2))
    def area(self):
        return 0.5 * (self.t2 - self.t1) * (self.R2**2 - self.R1**2)
    def dist_to_boundary(self, pts):
        r = np.hypot(pts[:, 0], pts[:, 1])
        th = np.arctan2(pts[:, 1], pts[:, 0])
        radial = np.minimum(r - self.R1, self.R2 - r)
        angular = np.minimum(th - self.t1, self.t2 - th) * r   # arc-length distance
        return np.minimum(radial, angular)
    def contains(self, pts): return self.dist_to_boundary(pts) >= 0


def k_2d(points, window, r_grid, lam=None):
    """DIM=2. Ripley K, border-corrected (minus-sampling).
    Poisson reference: K(r) = π r²;  L(r) = sqrt(K/π) = r."""
    pts = np.asarray(points, float)
    if lam is None:
        lam = len(pts) / window.area()
    rmax = float(r_grid[-1])
    core = pts[window.dist_to_boundary(pts) >= rmax]
    if len(core) == 0:
        raise ValueError("border erosion left no core points")
    tree = cKDTree(pts)
    K = np.empty(len(r_grid))
    for j, r in enumerate(r_grid):
        cnt = tree.query_ball_point(core, r, return_length=True)
        K[j] = (cnt.mean() - 1.0) / lam
    return K


def pcf_2d(points, window, bins, lam=None):
    """DIM=2. Pair-correlation g(r), pair-distance histogram, border-corrected.
    Poisson: g = 1.  Ginibre (intensity 1/π units): g(r) = 1 − exp(−r²)."""
    pts = np.asarray(points, float)
    if lam is None:
        lam = len(pts) / window.area()
    rmax = float(bins[-1])
    core = pts[window.dist_to_boundary(pts) >= rmax]
    tree = cKDTree(pts)
    counts = np.zeros(len(bins) - 1)
    for x in core:
        idx = tree.query_ball_point(x, rmax)
        d = np.linalg.norm(pts[idx] - x, axis=1)
        d = d[d > 0]
        counts += np.histogram(d, bins=bins)[0]
    ann = np.pi * (bins[1:]**2 - bins[:-1]**2)   # DIM=2 annulus area (1-D twin: 2·dr)
    g = counts / (len(core) * lam * ann)
    centers = 0.5 * (bins[:-1] + bins[1:])
    return centers, g


def disk_set_covariance(r, R):
    """DIM=2. γ(r) = |b(0,R) ∩ b(x,R)|, |x|=r — lens area of two disks radius R."""
    r = np.asarray(r, float)
    out = np.zeros_like(r)
    m = r < 2 * R
    rm = r[m]
    out[m] = 2 * R**2 * np.arccos(rm / (2 * R)) - 0.5 * rm * np.sqrt(4 * R**2 - rm**2)
    return out


def sigma2_from_g_2d(g_centers, g_vals, R, lam):
    """DIM=2 gluing identity (gate G-A3, 2-D form), counting disk radius R:
    Var N(b(0,R)) = lam πR² + lam² ∫₀^{2R} (g(r)−1) γ_R(r) 2πr dr.
    Empirical-g grid must reach 2R."""
    if g_centers[-1] < 2 * R:
        raise ValueError(f"g grid reaches {g_centers[-1]:.2f} < 2R={2*R}")
    m = g_centers <= 2 * R
    r, gv = g_centers[m], g_vals[m]
    integrand = (gv - 1.0) * disk_set_covariance(r, R) * 2 * np.pi * r
    return lam * np.pi * R**2 + lam**2 * np.trapezoid(integrand, r)


def disk_counts_grid(points, window, R):
    """DIM=2. Counts in NON-OVERLAPPING disks of radius R placed on a square
    grid of spacing 2R inside the eroded window.  Non-overlap keeps the counts
    (nearly) independent so a pooled variance across seeds is a usable direct
    Σ²(R) — the overlapping-sampled version underestimates its own sampling
    error badly on clustered processes (pilot-2 finding)."""
    pts = np.asarray(points, float)
    tree = cKDTree(pts)
    if isinstance(window, DiskWindow):
        Reff = window.R - R
        xs = np.arange(-Reff, Reff + 1e-9, 2 * R)
        cx, cy = np.meshgrid(xs, xs)
        centers = np.column_stack([cx.ravel(), cy.ravel()])
        centers = centers[np.hypot(centers[:, 0], centers[:, 1]) <= Reff]
    elif isinstance(window, RectWindow):
        xs = np.arange(R, window.Lx - R + 1e-9, 2 * R)
        ys = np.arange(R, window.Ly - R + 1e-9, 2 * R)
        cx, cy = np.meshgrid(xs, ys)
        centers = np.column_stack([cx.ravel(), cy.ravel()])
    else:
        raise NotImplementedError("grid counts: DiskWindow / RectWindow only")
    return tree.query_ball_point(centers, R, return_length=True).astype(float)


def sigma2_disk_direct(points, window, R_list, n_disks=400, seed=0):
    """DIM=2. Direct Σ²(R): variance of counts in n_disks disks of radius R whose
    centres are uniform in the eroded window (disk fully inside).
    NOTE (pilot-2): overlapping sampled disks have few effective independent
    counts; prefer disk_counts_grid pooled across seeds for gate use."""
    pts = np.asarray(points, float)
    rng = np.random.default_rng(seed)
    tree = cKDTree(pts)
    out = {}
    for R in R_list:
        centers = []
        # rejection-sample centres in the eroded window
        if isinstance(window, DiskWindow):
            Reff = window.R - R
            while len(centers) < n_disks:
                xy = rng.uniform(-Reff, Reff, size=(4 * n_disks, 2))
                xy = xy[np.hypot(xy[:, 0], xy[:, 1]) <= Reff]
                centers.extend(xy.tolist())
            centers = np.array(centers[:n_disks])
        elif isinstance(window, RectWindow):
            centers = np.column_stack([
                rng.uniform(R, window.Lx - R, n_disks),
                rng.uniform(R, window.Ly - R, n_disks)])
        else:
            raise NotImplementedError("direct Σ²: DiskWindow / RectWindow only")
        cnt = tree.query_ball_point(centers, R, return_length=True).astype(float)
        out[float(R)] = dict(var=float(cnt.var(ddof=1)), mean=float(cnt.mean()),
                             n_disks=int(n_disks))
    return out


def sigma2_direct_1d(events, L_vals, slide_step=0.1):
    """DIM=1. Direct sliding-window Σ²(L) replicating the home-dialect
    semantics of universality.py number_variance:134 EXACTLY (same window
    positions arange(e0, e[-1]-L, step), step=max(L*slide_step, 1.0), same
    ddof=1), but via searchsorted so it scales to n~1e5.  Equality with the
    home implementation is asserted by bridge tests on small n."""
    e = np.sort(np.asarray(events, float))
    out = np.empty(len(L_vals))
    for i, L in enumerate(L_vals):
        step = max(L * slide_step, 1.0)
        pos = np.arange(e[0], e[-1] - L, step)
        if pos.size < 5:
            out[i] = np.nan
            continue
        counts = (np.searchsorted(e, pos + L, side="left")
                  - np.searchsorted(e, pos, side="left")).astype(float)
        out[i] = counts.var(ddof=1)
    return out


def k_inhom(pts, window, r_grid, lam_fn):
    """DIM=2. Inhomogeneous K (Baddeley–Møller–Waagepetersen form), border-
    corrected: pairs weighted 1/(λ(x)λ(y)), normalized by Σ_core 1/λ.
    lam_fn maps radius → intensity (radial-intensity substrates).
    Inhomogeneous-Poisson reference: K_inhom(r) = πr².
    ONE transition on this path (tripwire 1): raw coordinates + λ(x); never
    feed unfolded/reweighted data here."""
    pts = np.asarray(pts, float)
    tree = cKDTree(pts)
    rmax = float(r_grid[-1])
    core_m = window.dist_to_boundary(pts) >= rmax
    core = pts[core_m]
    lam_all = lam_fn(np.hypot(pts[:, 0], pts[:, 1]))
    lam_core = lam_all[core_m]
    K = np.empty(len(r_grid))
    for j, r in enumerate(r_grid):
        tot = 0.0
        for i, x in enumerate(core):
            idx = tree.query_ball_point(x, r)
            wsum = np.sum(1.0 / lam_all[idx]) - 1.0 / lam_core[i]
            tot += wsum / lam_core[i]
        K[j] = tot / np.sum(1.0 / lam_core)
    return K
