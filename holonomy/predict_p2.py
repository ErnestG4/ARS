"""P2 sealed prediction — COMMITTED CONTINUUM DERIVATION (brief §2).

lambda(x) = lam0 exp(beta x) on [0,Lx]x[0,Ly]; the sealed lambda-hat is a
linear LS fit to 10 strip densities over the ESTIMATION DOMAIN (full for
ordering A, eroded for ordering B) — the finite-flexibility misfit is the
mechanism carrier.  For BMW-form K with marks m(x) = lambda_hat(x),

  E K_hat(r) = [ Int_core q(x) kappa(x,r) dx ] / [ Int_core q(x) dx ],
  q(x) = lambda(x)/lambda_hat(x),
  kappa(x,r) = Int_{-r}^{r} q(x+h) 2 sqrt(r^2-h^2) dh,

core_x = [rmax+r, Lx-rmax-r] (state domain = eroded rect, further border r).
Truth: K = pi r^2.  Delta_pred(r,G) = K_A - K_B; per-ordering
|K_O - pi r^2| is the predicted correctness separation.
"""

import json

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"

# sealed P2 constants
LX = LY = 10.0
RMAX = 1.0
N_TARGET = 3000
N_STRIPS = 10
R_LIST = [0.5, 1.0]
LADDER = [1.2 ** 2, 1.2 ** 4, 1.2 ** 6, 1.2 ** 8]   # gradient max/min ratios


def lam_params(G):
    beta = np.log(G) / LX
    lam0 = N_TARGET * beta / (LY * (np.exp(beta * LX) - 1.0))
    return lam0, beta


def strip_fit_continuum(lam0, beta, x0, x1):
    """Continuum mirror of transitions.fit_lambda_strips."""
    edges = np.linspace(x0, x1, N_STRIPS + 1)
    w = edges[1] - edges[0]
    dens = lam0 * (np.exp(beta * edges[1:]) - np.exp(beta * edges[:-1])) / (beta * w)
    mid = 0.5 * (edges[:-1] + edges[1:])
    c1, c0 = np.polyfit(mid, dens, 1)
    floor = max(0.05 * dens.mean(), 1e-9)
    return lambda x: np.maximum(c0 + c1 * np.asarray(x, float), floor)


def expected_K(lam0, beta, lam_hat, r):
    lam = lambda x: lam0 * np.exp(beta * np.asarray(x, float))  # noqa: E731
    q = lambda x: lam(x) / lam_hat(x)                           # noqa: E731
    cx0, cx1 = RMAX + r, LX - RMAX - r
    xg = np.linspace(cx0, cx1, 2001)
    hg = np.linspace(-r, r, 801)
    kern = 2.0 * np.sqrt(np.maximum(r * r - hg * hg, 0.0))
    Q = q(xg[:, None] + hg[None, :])
    kappa = np.trapezoid(Q * kern[None, :], hg, axis=1)
    qc = q(xg)
    return float(np.trapezoid(qc * kappa, xg) / np.trapezoid(qc, xg))


def main():
    out = {}
    for G in LADDER:
        lam0, beta = lam_params(G)
        hat_A = strip_fit_continuum(lam0, beta, 0.0, LX)          # full
        hat_B = strip_fit_continuum(lam0, beta, RMAX, LX - RMAX)  # eroded
        row = {}
        for r in R_LIST:
            KA = expected_K(lam0, beta, hat_A, r)
            KB = expected_K(lam0, beta, hat_B, r)
            true = np.pi * r * r
            row[f"r{r}"] = dict(K_A=KA, K_B=KB, K_true=true,
                                delta_pred=KA - KB,
                                bias_A=KA - true, bias_B=KB - true)
        out[f"G{G:.3f}"] = row
    res = dict(constants=dict(Lx=LX, Ly=LY, rmax=RMAX, n_target=N_TARGET,
                              n_strips=N_STRIPS, r_list=R_LIST,
                              ladder=LADDER),
               prediction=out)
    json.dump(res, open(f"{ROOT}/holonomy/p2_prediction.json", "w"), indent=1)
    print("P2 prediction (delta_pred = K_A - K_B; bias vs pi r^2):")
    for G, row in out.items():
        for rk, v in row.items():
            print(f"  {G} {rk}: dK={v['delta_pred']:+.5f} "
                  f"biasA={v['bias_A']:+.5f} biasB={v['bias_B']:+.5f}")


if __name__ == "__main__":
    main()
