"""Holonomy pilot: registered transitions + pair machinery (brief §1).

Provenance discipline (R2): survey/ and bridge/ frozen code is exercised
through public surfaces where possible.  Two exceptions, both banked:
  * unfold_poly mirrors fix_gue_generator.unfold_empirical (that module
    imports cupy at top level; mirrored body is 4 lines, equivalence
    asserted in kag_holonomy.py against the source text's algebra:
    polyfit(positions, 1..n, deg) -> polyval).
  * thin_pre is the u-threading variant of survey/mask_kag.thin_to_data
    (frozen, internally-drawn RNG).  Its diff is banked in the seal and
    equivalence_thin() proves bit-identical keep-masks when u is drawn
    the way the frozen function draws it.  Tested transfer surface.
"""

import sys

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
for p in (ROOT, f"{ROOT}/bridge", f"{ROOT}/survey"):
    if p not in sys.path:
        sys.path.insert(0, p)

from observer_b import sigma2_direct_1d                     # noqa: E402


# ── P1: 1-D unfold / window ──────────────────────────────────────────────────

def semicircle_cdf_unit(x):
    """Mirror of fix_gue_generator.semicircle_cdf_unit (cupy-free)."""
    x = np.clip(x, -1.0, 1.0)
    return 0.5 + (x * np.sqrt(1.0 - x * x) + np.arcsin(x)) / np.pi


def gen_gue_unfolded(N, seed):
    """GUE eigenvalues (fix_gue_generator.gen_gue_eigenvalues construction),
    truth-unfolded by the analytic semicircle CDF * N."""
    rng = np.random.default_rng(seed)
    A = (rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))) / np.sqrt(2)
    H = (A + A.conj().T) / np.sqrt(2 * N)
    ev = np.sort(np.linalg.eigvalsh(H).real)
    return semicircle_cdf_unit(ev / 2.0) * N


def make_trend_maps(a, ell, u_hi, n_grid=200_001):
    """Truth warp for density rho(x) = 1 + a sin(2 pi x / ell) in RAW x:
    U_true(x) = x + (a ell / 2 pi)(1 - cos(2 pi x / ell)).  Returns
    (x_of_u, u_of_x) interpolators on a dense monotone grid covering
    u in [0, u_hi]."""
    x_grid = np.linspace(0.0, 1.25 * u_hi / (1.0), n_grid)  # rho>=1-a; margin
    u_grid = x_grid + (a * ell / (2 * np.pi)) * (1.0 - np.cos(2 * np.pi * x_grid / ell))
    x_of_u = lambda u: np.interp(u, u_grid, x_grid)          # noqa: E731
    u_of_x = lambda x: np.interp(x, x_grid, u_grid)          # noqa: E731
    return x_of_u, u_of_x


def gen_trended_set(seed, N, n_keep, a, ell):
    """Trended-GUE substrate: truth coords u (central n_keep, re-zeroed),
    raw x = U_true^{-1}(u).  Returns dict(x, u_true)."""
    u_all = gen_gue_unfolded(N, seed)
    lo = (len(u_all) - n_keep) // 2
    u = u_all[lo:lo + n_keep]
    u = u - u[0]
    x_of_u, _ = make_trend_maps(a, ell, u_hi=float(u[-1]))
    return dict(x=x_of_u(u), u_true=u)


def unfold_poly(x, deg):
    """Mirror of fix_gue_generator.unfold_empirical: poly fit to the
    cumulative count at each point."""
    x = np.asarray(x, float)
    counts = np.arange(1, x.size + 1, dtype=float)
    coefs = np.polyfit(x, counts, deg=deg)
    return np.polyval(coefs, x)


def central_ranks(n_total, n_W):
    lo = (n_total - n_W) // 2
    return slice(lo, lo + n_W)


def p1_apply(x, order, deg, n_W):
    """Both P1 orderings.  Sealed window rule: central n_W RANKS in both
    orderings (rank is invariant under monotone maps) — isolates the
    estimation-domain mechanism; selection-coordinate effects are a
    different pair, not sealed here (brief §1)."""
    x = np.sort(np.asarray(x, float))
    sl = central_ranks(x.size, n_W)
    if order == "unfold_then_window":       # A: fit on FULL set
        u_hat = unfold_poly(x, deg)
        return np.sort(u_hat)[sl]
    elif order == "window_then_unfold":     # B: fit on the TRUNCATED set
        xw = x[sl]
        return np.sort(unfold_poly(xw, deg))
    raise ValueError(order)


def sigma2_at(events, L_list):
    return sigma2_direct_1d(np.asarray(events, float), list(L_list))


def rtilde(events):
    """<r~> adjacent-gap ratio (unfold-free control)."""
    s = np.diff(np.sort(np.asarray(events, float)))
    r = s[1:] / s[:-1]
    return float(np.mean(np.minimum(r, 1.0 / r)))


def nns_ks_gue(events):
    """Home-dialect NNS-KS to GUE via universality.compute_nns — including
    its census-C1 internal renormalisation (part of the measured stack)."""
    from universality import compute_nns
    return float(compute_nns(np.asarray(events, float)).ks_gue)


# ── P2: 2-D reweight / edge ──────────────────────────────────────────────────

def sample_inhom_poisson(seed, beta, n_target, Lx=10.0, Ly=10.0):
    """Inhomogeneous Poisson, lambda(x) = lam0 exp(beta x), E[n] = n_target.
    Sampled by thinning a homogeneous proposal at max intensity."""
    rng = np.random.default_rng(seed)
    if abs(beta) < 1e-12:
        lam0 = n_target / (Lx * Ly)
    else:
        lam0 = n_target * beta / (Ly * (np.exp(beta * Lx) - 1.0))
    lam_max = lam0 * np.exp(max(beta * Lx, 0.0))
    n_prop = rng.poisson(lam_max * Lx * Ly)
    pts = rng.uniform(0, 1, size=(n_prop, 2)) * np.array([Lx, Ly])
    keep = rng.uniform(size=n_prop) < lam0 * np.exp(beta * pts[:, 0]) / lam_max
    return pts[keep], dict(lam0=lam0, beta=beta, Lx=Lx, Ly=Ly)


def fit_lambda_strips(pts, domain, n_strips=10):
    """Sealed lambda-hat: strip counts in x -> linear LS fit, floor-clamped.
    Deliberately finite-flexibility (the realistic mechanism carrier);
    fit domain = the STATE's domain (the estimation-domain mechanism)."""
    x0, x1, y0, y1 = domain
    edges = np.linspace(x0, x1, n_strips + 1)
    cnt, _ = np.histogram(pts[:, 0], bins=edges)
    dens = cnt / ((edges[1] - edges[0]) * (y1 - y0))
    mid = 0.5 * (edges[:-1] + edges[1:])
    c1, c0 = np.polyfit(mid, dens, 1)
    floor = max(0.05 * dens.mean(), 1e-9)
    return lambda x: np.maximum(c0 + c1 * np.asarray(x, float), floor)


def erode(pts, domain, rmax):
    x0, x1, y0, y1 = domain
    d2 = (x0 + rmax, x1 - rmax, y0 + rmax, y1 - rmax)
    m = ((pts[:, 0] >= d2[0]) & (pts[:, 0] <= d2[1])
         & (pts[:, 1] >= d2[2]) & (pts[:, 1] <= d2[3]))
    return pts[m], d2


def p2_apply(pts, domain, order, rmax, n_strips=10):
    """Both P2 orderings.  Returns (pts_state, marks, state_domain)."""
    if order == "reweight_then_edge":       # A: fit on full domain
        lam_hat = fit_lambda_strips(pts, domain, n_strips)
        marks = lam_hat(pts[:, 0])
        pe, d2 = erode(pts, domain, rmax)
        me = marks[((pts[:, 0] >= d2[0]) & (pts[:, 0] <= d2[1])
                    & (pts[:, 1] >= d2[2]) & (pts[:, 1] <= d2[3]))]
        return pe, me, d2
    elif order == "edge_then_reweight":     # B: fit on eroded domain
        pe, d2 = erode(pts, domain, rmax)
        lam_hat = fit_lambda_strips(pe, d2, n_strips)
        return pe, lam_hat(pe[:, 0]), d2
    raise ValueError(order)


def k_inhom_marks(pts, marks, domain, r_list):
    """BMW-form inhomogeneous K with per-point marks as lambda, border-
    corrected within the state's domain (observer_b.k_inhom:254 form:
    K = [sum_core (1/m_i) sum_{j in ball} 1/m_j] / sum_core (1/m_i),
    self-pair removed).  Vectorised via query_pairs."""
    from scipy.spatial import cKDTree
    x0, x1, y0, y1 = domain
    tree = cKDTree(pts)
    inv = 1.0 / marks
    out = {}
    for r in r_list:
        core = ((pts[:, 0] >= x0 + r) & (pts[:, 0] <= x1 - r)
                & (pts[:, 1] >= y0 + r) & (pts[:, 1] <= y1 - r))
        pairs = tree.query_pairs(r, output_type="ndarray")
        if len(pairs):
            i, j = pairs[:, 0], pairs[:, 1]
            w = inv[i] * inv[j]
            num = (np.sum(w[core[i]]) + np.sum(w[core[j]]))
        else:
            num = 0.0
        out[float(r)] = float(num / np.sum(inv[core]))
    return out


# ── P3: survey weight / thin (u-threading variant of the frozen path) ────────

def thin_pre(cat, p, u):
    """u-threading variant of survey/mask_kag.thin_to_data:49 (frozen).
    Differences vs frozen, in full (the banked diff, R2):
      frozen: p = w_target / kag['w'].sum(); keep = rng.uniform(n) < p
      here:   p given by CALLER (the ordering decides its normalisation);
              keep = u < p with u PRE-DRAWN (brief §0).
    Same keep rule, same dict comprehension."""
    keep = u < p
    return {k: v[keep] for k, v in cat.items()}


def equivalence_thin(kag_cat, w_target, seed):
    """R2 equivalence test: thin_pre driven with internally-drawn u at the
    frozen seed path must reproduce frozen thin_to_data bit-identically."""
    from mask_kag import thin_to_data
    frozen = thin_to_data(kag_cat, w_target, seed)
    u = np.random.default_rng(seed).uniform(size=len(kag_cat["w"]))
    p = w_target / kag_cat["w"].sum()
    ours = thin_pre(kag_cat, p, u)
    same = all(np.array_equal(frozen[k], ours[k]) for k in frozen)
    return bool(same), int(len(frozen["w"]))


def p3_keep_probs(cat_data, cat_kag):
    """The two orderings' scalar thinning rates (brief §1 mechanism):
    weight-then-thin normalises by WEIGHTED totals (frozen semantics);
    thin-then-weight normalises by COUNTS."""
    p_wt = cat_data["w"].sum() / cat_kag["w"].sum()      # A: weight -> thin
    p_tw = len(cat_data["w"]) / len(cat_kag["w"])        # B: thin -> weight
    return float(p_wt), float(p_tw)
