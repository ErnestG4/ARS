"""P1 sealed prediction — COMMITTED CONTINUUM DERIVATION (brief §2).

Deterministic functional calculation, no point noise: both orderings are
applied to the exact continuum density.  In truth coordinate u the process
has unit density; the raw coordinate is x(u) = U_true^{-1}(u) for the sealed
trend rho(x) = 1 + a sin(2 pi x / ell).

phi_O(u) := P_O(x(u)) is the ESTIMATED unfolded coordinate as a function of
the true one, where P_O is the deg-d polynomial CDF fit (unfold_empirical
algebra) over ordering O's estimation domain: A = full set, B = central
window.  The expected count in the estimated window [v, v+L] is
m_O(v) = phi_O^{-1}(v+L) - phi_O^{-1}(v); the misunfolding contribution to
the sliding-window number variance is Var_v[m_O(v)] with the exact
sigma2_direct_1d window positions (step = max(0.1 L, 1)).  Intrinsic GUE
Sigma^2 is ordering-independent at leading order and cancels in
Delta = Sigma2_A - Sigma2_B, so

    Delta_pred(dial, L) = Var_v[m_A] - Var_v[m_B].

The same functional also yields the predicted CORRECTNESS separation: the
per-ordering spurious variance Var_v[m_O] is that ordering's predicted
|Sigma2 - Sigma2_true| excess, so sign(Var_A - Var_B) predicts which
ordering the leg should rule toward (negative => A less biased).
"""

import json

import numpy as np

from transitions import make_trend_maps

ROOT = "/home/combust/fmexplorer/criticality_tool"

# sealed P1 constants (mirrored into the seal by seal_prereg.py)
A_TREND = 0.25
DEG = 5
N_FULL = 1200
N_W = 600
DIALS = [0.25, 0.5, 1.0, 2.0, 4.0]         # window-length / trend-scale
L_FRACS = [1.0 / 60, 1.0 / 30, 1.0 / 15]   # L as fraction of window (R5)
JITTER_DEGS = [4, 6]                        # bandwidth envelope, not a dial


def spurious_var(phi_u, u_grid, L):
    """Var over sliding positions of expected counts in phi-windows."""
    v0, v1 = phi_u[0], phi_u[-1]
    step = max(0.1 * L, 1.0)
    pos = np.arange(v0, v1 - L, step)
    if pos.size < 5:
        return np.nan
    inv_lo = np.interp(pos, phi_u, u_grid)
    inv_hi = np.interp(pos + L, phi_u, u_grid)
    m = inv_hi - inv_lo
    return float(m.var(ddof=1))


def predict(deg=DEG):
    out = {}
    for dial in DIALS:
        ell = N_W / dial
        x_of_u, _ = make_trend_maps(A_TREND, ell, u_hi=N_FULL)
        u_full = np.linspace(0.0, N_FULL, 48001)
        x_full = x_of_u(u_full)
        lo, hi = (N_FULL - N_W) / 2.0, (N_FULL + N_W) / 2.0
        win = (u_full >= lo) & (u_full <= hi)
        u_win, x_win = u_full[win], x_full[win]
        # ordering A: fit on full domain; B: fit on window (within-set ranks)
        cA = np.polyfit(x_full, u_full, deg)
        cB = np.polyfit(x_win, u_win - lo, deg)
        phi_A = np.polyval(cA, x_win)
        phi_B = np.polyval(cB, x_win)
        row = {}
        for f in L_FRACS:
            L = f * N_W
            vA = spurious_var(phi_A, u_win, L)
            vB = spurious_var(phi_B, u_win, L)
            row[f"L{L:.1f}"] = dict(delta_pred=vA - vB, var_A=vA, var_B=vB)
        out[f"dial{dial}"] = row
    return out


def main():
    res = dict(constants=dict(a=A_TREND, deg=DEG, n_full=N_FULL, n_W=N_W,
                              dials=DIALS, L_fracs=L_FRACS,
                              jitter_degs=JITTER_DEGS),
               prediction=predict(DEG),
               bandwidth_envelope={f"deg{d}": predict(d)
                                   for d in JITTER_DEGS})
    json.dump(res, open(f"{ROOT}/holonomy/p1_prediction.json", "w"), indent=1)
    print("P1 prediction (delta_pred = Var_A - Var_B, negative => "
          "unfold-then-window less biased):")
    for dial, row in res["prediction"].items():
        print(f"  {dial}: " + "  ".join(
            f"{k}: {v['delta_pred']:+.4f}" for k, v in row.items()))


if __name__ == "__main__":
    main()
