"""Spectra (GPU, fp64) + KDE peak counting (Stage 1 criterion)."""
import numpy as np
import torch
from scipy.signal import find_peaks

DEV = "cuda" if torch.cuda.is_available() else "cpu"


def singvals(W):
    """Singular values of a batch of p x n matrices (p <= n), fp64, via Gram eigvalsh on GPU.
    Returns ascending sigma, shape (batch, p)."""
    W = (W if torch.is_tensor(W) else torch.as_tensor(np.asarray(W))).to(DEV, torch.float64)
    if W.ndim == 2:
        W = W[None]
    if W.shape[-2] > W.shape[-1]:
        W = W.transpose(-1, -2)
    G = W @ W.transpose(-1, -2)
    ev = torch.linalg.eigvalsh(G).clamp_min(0)
    return ev.sqrt().cpu().numpy()


def silverman(x):
    x = np.asarray(x)
    sd = x.std(ddof=1, axis=-1)
    q75, q25 = np.percentile(x, [75, 25], axis=-1)
    return 0.9 * np.minimum(sd, (q75 - q25) / 1.34) * x.shape[-1] ** (-0.2)


def kde(x, h):
    """One normalised spectrum x (n,), fixed scalar bandwidth h. Grid step is FIXED in x units
    (h/8) over [min-4h, max+4h], so a far outlier cannot coarsen the grid under narrow peaks."""
    x = np.asarray(x, dtype=np.float64)
    step = h / 8
    g = np.arange(x.min() - 4 * h, x.max() + 4 * h + step, step)
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
