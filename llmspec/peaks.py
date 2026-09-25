"""Spectra (GPU, fp64) + KDE peak counting (Stage 1 criterion)."""
import numpy as np
import torch
from scipy.signal import find_peaks

DEV = "cuda" if torch.cuda.is_available() else "cpu"


def singvals(W):
    """Singular values of a batch of matrices, fp64, DIRECT SVD on GPU (v2). Ascending, (batch, min(p,n)).
    v1 used Gram eigvalsh, which cannot resolve sigma below ~1e-8 sigma_max (OLMo has heads whose
    rows decayed to ~1e-28): retired 2026-09-25."""
    W = (W if torch.is_tensor(W) else torch.as_tensor(np.asarray(W))).to(DEV, torch.float64)
    if W.ndim == 2:
        W = W[None]
    return torch.linalg.svdvals(W).flip(-1).cpu().numpy()


def silverman(x):
    x = np.asarray(x)
    sd = x.std(ddof=1, axis=-1)
    q75, q25 = np.percentile(x, [75, 25], axis=-1)
    return 0.9 * np.minimum(sd, (q75 - q25) / 1.34) * x.shape[-1] ** (-0.2)


SPARSE_PAD = 8.0   # in units of h; verify_kde_sparse.py --redpath shrinks it to show the check can fail


def kde(x, h, dense=False):
    """One normalised spectrum x (n,), fixed scalar bandwidth h. Grid step is FIXED in x units
    (h/8), anchored at min-4h, so a far outlier cannot coarsen the grid under narrow peaks.
    Sparse form (default, v2): only grid points within 8h of some data point are kept -- an exact
    subset of the dense grid; dropped points carry density < exp(-32) of a single kernel's peak.
    Needed because heads with decayed rows give sigma/median spans of 1e8+. Equivalence to the
    dense grid is checked in verify_kde_sparse.py."""
    x = np.asarray(x, dtype=np.float64)
    step = h / 8
    g0 = x.min() - 4 * h
    if dense:
        k = np.arange(0, int(np.ceil((x.max() + 4 * h - g0) / step)) + 1)
    else:
        xs = np.sort(x)
        lo = np.floor((xs - SPARSE_PAD * h - g0) / step).astype(np.int64).clip(0)
        hi = np.ceil((xs + SPARSE_PAD * h - g0) / step).astype(np.int64)
        kmax = int(np.ceil((x.max() + 4 * h - g0) / step))
        hi = np.minimum(hi, kmax)
        # merge intervals
        segs = []
        cl, ch = lo[0], hi[0]
        for l_, h_ in zip(lo[1:], hi[1:]):
            if l_ <= ch + 1:
                ch = max(ch, h_)
            else:
                segs.append((cl, ch)); cl, ch = l_, h_
        segs.append((cl, ch))
        k = np.concatenate([np.arange(u, v + 1) for u, v in segs])
    g = g0 + k * step
    d = np.zeros_like(g)
    for i in range(0, len(x), 256):
        z = (g[:, None] - x[None, i:i + 256]) / h
        d += np.exp(-0.5 * z * z).sum(1)
    return g, d / (len(x) * h * np.sqrt(2 * np.pi))


def modes(grid, dens, x, prom_frac, m_min):
    """Peaks with prominence >= prom_frac * max density. Basin = between the adjacent
    density minima; mass = number of spectrum points in the basin.
    Returns (n_modes_all, n_modes_massive, list of (loc, prom, mass))."""
    pk, pr = find_peaks(dens, prominence=prom_frac * dens.max())
    if len(pk) == 0:
        return 0, 0, []
    # basin edges: argmin of density between consecutive peaks
    edges = [grid[0]]
    for a, b in zip(pk[:-1], pk[1:]):
        edges.append(grid[a + np.argmin(dens[a:b + 1])])
    edges.append(grid[-1] + 1)
    info = []
    for j, p in enumerate(pk):
        mass = int(((x >= edges[j]) & (x < edges[j + 1])).sum())
        info.append((float(grid[p]), float(pr["prominences"][j] / dens.max()), mass))
    return len(pk), sum(1 for _, _, m in info if m >= m_min), info


def normalise(sig):
    """x = sigma / median(sigma), per spectrum."""
    sig = np.asarray(sig, dtype=np.float64)
    return sig / np.median(sig, axis=-1, keepdims=True)


def count_batch(xs, h, prom_frac, m_min, keep_info=False):
    res = []
    for x in xs:
        g, d = kde(x, h)
        res.append(modes(g, d, x, prom_frac, m_min))
    a = np.array([r[0] for r in res])
    m = np.array([r[1] for r in res])
    return (a, m, [r[2] for r in res]) if keep_info else (a, m)
