"""R₂ pre-read machinery (PH2R2_SEAL 1.0 §2): fresh-bin geometry, the declared test-function family, the CS07 prediction
split into RMT_f + LOT_f for within-file pairs, and the pair statistic S_f. Theory only — nothing here reads a zero.

Declared here (seal R3/R4; values fixed before any fresh zero is read):
  test functions   f_{u,w}(x) = exp(−(x − u δ)²/2(wδ)²) + exp(−(x + u δ)²/2(wδ)²), δ = the bin's central mean spacing
                   2π/log(t_c/2π) (raw γ units, fixed per bin); family u ∈ {0.5, 1.0, 1.5, 2.0}, w ∈ {0.15, 0.3}
  u_max            separations |γ − γ′| ≤ U_MAX·δ, U_MAX = 3.0 (covers every family member to ≥ 3.3 w beyond its centre)
  pairs            ordered pairs γ ≠ γ′ with BOTH members inside the file (R4); the prediction applies the same restriction
"""
import math

import numpy as np

import r2lib as R

TWO_PI = 2 * math.pi
U_MAX = 3.0
FAMILY = [(u, w) for u in (0.5, 1.0, 1.5, 2.0) for w in (0.15, 0.3)]
# fresh bins (FRESH_PLATT_PINS.md): [t0, t1) of each pinned Platt file
BINS = {
    "R1": (6_746_000.0, 8_846_000.0),
    "R2": (55_046_000.0, 57_146_000.0),
    "R3": (412_046_000.0, 414_146_000.0),
    "R4": (3_047_546_000.0, 3_049_646_000.0),
    "R5": (22_522_946_000.0, 22_525_046_000.0),
}


def nbar(t):
    t = np.asarray(t, dtype=float)
    th = t / 2 * np.log(t / TWO_PI) - t / 2 - math.pi / 8 + 1 / (48 * t) + 7 / (5760 * t ** 3)
    return th / math.pi + 1


def geometry(name):
    t0, t1 = BINS[name]
    tc = 0.5 * (t0 + t1)
    delta = TWO_PI / math.log(tc / TWO_PI)
    return dict(t0=t0, t1=t1, tc=tc, L_c=math.log(tc / TWO_PI), delta=delta,
                n_zeros=float(nbar(t1) - nbar(t0)))


def f_raw(x, u, w, delta):
    a, s = u * delta, w * delta
    return np.exp(-(x - a) ** 2 / (2 * s * s)) + np.exp(-(x + a) ** 2 / (2 * s * s))


class Prediction:
    """∫∫ f(r) R(t, r) 1[t ∈ bin] 1[t + r ∈ bin] dr dt, split into RMT and LOT parts (CS07 Theorem 4.1)."""

    def __init__(self, name, n_r=1201, n_t=24):
        g = geometry(name)
        self.g = g
        rmax = U_MAX * g["delta"]
        # r grid on (0, rmax] (densities are even in r; f even) — Gauss–Legendre
        x, wr = np.polynomial.legendre.leggauss(n_r)
        self.r = 0.5 * rmax * (x + 1)
        self.wr = 0.5 * rmax * wr
        self.K = R.Kernel(self.r)
        xt, wt = np.polynomial.legendre.leggauss(n_t)
        self.t = 0.5 * (g["t1"] - g["t0"]) * (xt + 1) + g["t0"]
        self.wt = 0.5 * (g["t1"] - g["t0"]) * wt
        self.Rmt = np.array([self.K.RMT(t) for t in self.t])          # (n_t, n_r)
        self.Lot = np.array([self.K.LOT(t) for t in self.t])
        self.Rt = self.Rmt + self.Lot

    def parts(self, u, w):
        """(RMT_f, LOT_f) for ordered pairs within the file, both signs of r (factor 2 for r < 0 by evenness).
        Edge restriction: a pair at separation r loses the length |r| of t-range at the file's edges (density ≈ the
        edge's; the loss is computed with R at each edge)."""
        g = self.g
        f = f_raw(self.r, u, w, g["delta"])
        bulk_rmt = 2 * np.sum(self.wt[:, None] * self.Rmt * (f * self.wr)[None, :])
        bulk_lot = 2 * np.sum(self.wt[:, None] * self.Lot * (f * self.wr)[None, :])
        e_rmt = sum(np.sum(self.K.RMT(t) * f * self.r * self.wr) for t in (g["t0"], g["t1"]))
        e_lot = sum(np.sum(self.K.LOT(t) * f * self.r * self.wr) for t in (g["t0"], g["t1"]))
        return bulk_rmt - e_rmt, bulk_lot - e_lot


def pair_sum(levels, u, w, delta):
    """S_f over ordered pairs γ ≠ γ′ of a sorted level list (all inside the file by construction), |γ − γ′| ≤ U_MAX δ."""
    t = np.asarray(levels, dtype=float)
    rmax = U_MAX * delta
    s = 0.0
    k = 1
    while True:
        d = t[k:] - t[:-k]
        m = d <= rmax
        if not m.any():
            break
        s += 2 * np.sum(f_raw(d[m], u, w, delta))
        k += 1
    return float(s)
