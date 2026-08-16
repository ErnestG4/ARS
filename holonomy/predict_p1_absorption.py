"""P1 prediction upgrade — the FLUCTUATION-ABSORPTION term (holonomy seal
addendum ADD-7).  COMMITTED GENERATOR of holonomy/p1_absorption.json.

The sealed P1 prediction (predict_p1.py) captured only the TREND-TRACKING
term: the deterministic misfit of the smooth density by a degree-d
polynomial, computed on the exact continuum density with no point noise.
The seal registered, in advance, that a second term was KNOWN-OMITTED —
absorption of genuine FLUCTUATION by the fit — and pre-registered its
signature: a positive residual concentrated at cells where the trend term is
near zero.  The measurement showed exactly that (dial 2.0 / L=10: measured
+0.211 against a predicted -0.013).  This file derives the omitted term.

── Derivation (parameter-free; no constant is fitted to any residual) ───────
Write the counting fluctuation of the unit-density process as
    eta(u) = N(u) - u ,     Cov(eta(u), eta(u')) = C(u, u') .
For a stationary point process with number variance Sigma2(s), and anchoring
eta(0) = 0,
    C(u, u') = 0.5 * [ Sigma2(u) + Sigma2(u') - Sigma2(|u - u'|) ] .
The unfolding fit is a least-squares degree-d polynomial fit to the counting
staircase over the ordering's OWN estimation domain D_O (ordering A: the
full set; ordering B: the analysis window).  Least squares is a linear
projection Pi_O onto the polynomial subspace, so the fit absorbs the
component Pi_O eta and the unfolded coordinate carries only eta - Pi_O eta.

The number in a window [v, v+L] of the unfolded coordinate therefore loses
the increment of the absorbed part, and the sliding-window variance is
reduced by
    A_O(L) = Var_v[ (Pi_O eta)(v + L) - (Pi_O eta)(v) ] ,
averaged over exactly the window positions the estimator uses
(sigma2_direct_1d: step = max(0.1 L, 1)).  Because Pi_O eta is a linear
functional of eta, this is exact linear algebra:
    (Pi_O eta)(v) = a_v^T eta ,  A_O(L) = mean_v [ (a_{v+L} - a_v)^T C
                                                   (a_{v+L} - a_v) ] .
Since Sigma2_O = Sigma2_true - A_O, the absorption contribution to the
commutator is
    Delta_absorb(L) = Sigma2_A - Sigma2_B = A_B(L) - A_A(L) .
Ordering B fits d+1 parameters to the window alone and therefore absorbs
MORE of that window's own fluctuation than ordering A, whose fit is
constrained by the whole domain: A_B > A_A, so Delta_absorb > 0.  The SIGN
is a prediction of the derivation, not an observation.

Stated approximations (both first-order, declared):
  * the absorption is computed in the unit-density (truth) coordinate; the
    trend's effect on the absorption itself is second order (it enters as a
    reparametrisation of the design matrix, whose leading effect is already
    carried by the trend term);
  * Sigma2 for the GUE substrate uses the Mehta asymptotic form, valid for
    the sealed L >= 10.
"""

import json
import sys

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, f"{ROOT}/holonomy")

SEAL = json.load(open(f"{ROOT}/holonomy/prereg_sealed.json"))
P1 = SEAL["p1"]
GAMMA = 0.5772156649015329
NGRID = 1201            # grid over the full domain


def sigma2_gue(s):
    s = np.asarray(s, float)
    out = np.where(s > 0.5,
                   (np.log(2.0 * np.pi * np.maximum(s, 1e-9)) + GAMMA + 1.0)
                   / np.pi ** 2, 0.0)
    return np.maximum(out, 0.0)


def covariance(u):
    S = sigma2_gue(u)
    return 0.5 * (S[:, None] + S[None, :]
                  - sigma2_gue(np.abs(u[:, None] - u[None, :])))


def projector_rows(u_grid, domain_mask, deg):
    """Rows a_v of the LS projection: (Pi eta)(v) = a_v^T eta, with the fit
    taken over `domain_mask` and evaluated at every grid point."""
    ud = u_grid[domain_mask]
    xd = (ud - ud[0]) / (ud[-1] - ud[0])          # conditioning, as in code
    V = np.vander(xd, deg + 1, increasing=True)
    G = np.linalg.pinv(V.T @ V) @ V.T             # (deg+1) x n_domain
    xa = (u_grid - ud[0]) / (ud[-1] - ud[0])
    Va = np.vander(xa, deg + 1, increasing=True)  # evaluate everywhere
    A = np.zeros((u_grid.size, u_grid.size))
    A[:, domain_mask] = Va @ G
    return A


def absorption(u_grid, C, A_rows, L, win_lo, win_hi):
    """A_O(L) = mean over the estimator's own window positions."""
    step = max(0.1 * L, 1.0)
    pos = np.arange(win_lo, win_hi - L, step)
    if pos.size < 5:
        return np.nan
    i0 = np.searchsorted(u_grid, pos)
    i1 = np.searchsorted(u_grid, pos + L)
    i0 = np.clip(i0, 0, u_grid.size - 1)
    i1 = np.clip(i1, 0, u_grid.size - 1)
    D = A_rows[i1] - A_rows[i0]                   # n_pos x n_grid
    return float(np.mean(np.einsum("ij,jk,ik->i", D, C, D)))


def main():
    n_full, n_W, deg = P1["n_full"], P1["n_W"], P1["deg"]
    u = np.linspace(0.0, float(n_full), NGRID)
    C = covariance(u)
    lo, hi = (n_full - n_W) / 2.0, (n_full + n_W) / 2.0
    full_mask = np.ones(u.size, bool)
    win_mask = (u >= lo) & (u <= hi)
    A_full = projector_rows(u, full_mask, deg)
    A_win = projector_rows(u, win_mask, deg)
    rows = {}
    for f in P1["L_fracs"]:
        L = f * n_W
        aA = absorption(u, C, A_full, L, lo, hi)
        aB = absorption(u, C, A_win, L, lo, hi)
        rows[f"L{L:.1f}"] = dict(A_full=aA, A_window=aB,
                                 delta_absorb=float(aB - aA))
        print(f"  L={L:5.1f}: A_A={aA:.4f} A_B={aB:.4f} "
              f"-> delta_absorb={aB - aA:+.4f}")
    out = dict(derivation="fluctuation absorption by the LS polynomial "
                          "unfolding fit; parameter-free",
               constants=dict(n_full=n_full, n_W=n_W, deg=deg,
                              n_grid=NGRID),
               sign_prediction="delta_absorb > 0 at every L (ordering B "
                               "fits d+1 parameters to the window alone and "
                               "absorbs more of its fluctuation)",
               dial_independent=True,
               note="the absorption term depends on (n_full, n_W, deg, L) "
                    "only — NOT on the trend amplitude or scale — so it is "
                    "a CONSTANT offset across the dial ladder at fixed L. "
                    "That is itself a falsifiable claim: the residuals of "
                    "the sealed trend-only prediction must be flat in dial "
                    "at each L.",
               rows=rows)
    json.dump(out, open(f"{ROOT}/holonomy/p1_absorption.json", "w"), indent=1)


if __name__ == "__main__":
    main()
