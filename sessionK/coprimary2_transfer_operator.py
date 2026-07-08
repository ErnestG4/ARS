"""
Session K — Co-Primary 2: transfer-operator reproduction of the Session-J metallic bridge.

R4 split (see SESSION_K_COPRIMARY2_PREREG_SEALED.json):

  2a  OPERATOR SANITY (a.e. Gauss-map constants). Discretize the Gauss-Kuzmin-Wirsing
      (GKW) transfer operator  (L_s f)(x) = sum_{n>=1} (n+x)^{-2s} f(1/(n+x)).
      Confirm  lambda_0(s=1)=1,  subdominant lambda_1=-0.3036300...,  and the
      a.e. Lyapunov exponent  lambda_L = -d/ds log lambda_0(s)|_{s=1} = pi^2/(6 ln2),
      hence Levy exponent pi^2/(12 ln2) and Levy constant e^{pi^2/(12 ln2)}=3.27582.
      This validates the discretization; it is NOT the bridge numerator.

  2b  THE BRIDGE. The banked numerator L_a = log eps_a (metallic denominator growth)
      is a PERIODIC-ORBIT invariant of the same Gauss map: the CF [a;a,a,...] has
      transfer matrix M_a=[[a,1],[1,0]] whose top eigenvalue is eps_a=(a+sqrt(a^2+4))/2.
      Recover L_a = log(lambda_max(M_a)) by a SPECTRAL computation (numpy eig on M_a) --
      an independent code path from the sealed algebraic closed form -- then feed banked
      C_a and confirm the sealed theta_inf = L_a/C_a ladder within propagated C-bands.

Anti-laundering (R4): 2a passing does NOT imply 2b. Reported separately.
"""
import json, math, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREREG = json.load(open(os.path.join(ROOT, "SESSION_K_COPRIMARY2_PREREG_SEALED.json")))

# ----------------------------------------------------------------------------
# GKW operator via Chebyshev-Lobatto collocation + barycentric interpolation.
# ----------------------------------------------------------------------------
def cheb_lobatto(N):
    """N+1 Chebyshev-Lobatto nodes mapped to [0,1], plus barycentric weights."""
    k = np.arange(N + 1)
    x_cheb = np.cos(np.pi * k / N)            # in [-1,1], descending
    x = (1.0 - x_cheb) / 2.0                  # in [0,1], ascending
    w = np.ones(N + 1)
    w[1:-1:2] = -1.0                          # standard Lobatto barycentric weights
    w[0] *= 0.5
    w[-1] *= 0.5
    # sign pattern for descending->ascending remap is irrelevant up to global sign
    return x, w

def bary_matrix(nodes, w, xq):
    """Barycentric interpolation matrix B: f(xq) ~= B @ f(nodes)."""
    xq = np.asarray(xq, float)
    diff = xq[:, None] - nodes[None, :]       # (Q, N+1)
    B = np.zeros_like(diff)
    exact = np.isclose(diff, 0.0)
    rows_exact = np.any(exact, axis=1)
    tmp = w[None, :] / diff
    denom = tmp.sum(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        B = tmp / denom[:, None]
    # handle query points hitting a node exactly
    for i in np.where(rows_exact)[0]:
        B[i, :] = 0.0
        B[i, np.argmax(exact[i])] = 1.0
    return B

def gkw_matrix(N, s=1.0, nmax=20000):
    """Discretized (L_s f) at collocation nodes as a matrix acting on node values."""
    nodes, w = cheb_lobatto(N)
    n = np.arange(1, nmax + 1)[:, None]        # (nmax,1)
    xj = nodes[None, :]                        # (1,N+1)
    # For each node x_j: sum_n (n+x_j)^{-2s} f(1/(n+x_j))
    weights = (n + xj) ** (-2.0 * s)           # (nmax, N+1)
    ypts = 1.0 / (n + xj)                       # (nmax, N+1) image points in (0,1]
    M = np.zeros((N + 1, N + 1))
    # accumulate column j: weights[:,j] . B(ypts[:,j])
    for j in range(N + 1):
        B = bary_matrix(nodes, w, ypts[:, j])  # (nmax, N+1)
        M[j, :] = weights[:, j] @ B
    # Euler-Maclaurin tail correction n>nmax: sum (n+x)^{-2s} f(1/(n+x)) ~ f(0) * tail
    # tail of sum_{n>nmax}(n+x)^{-2s} ~ (nmax)^{1-2s}/(2s-1) ; f(0)=B(0)
    B0 = bary_matrix(nodes, w, np.array([0.0]))[0]   # f(0) row
    if s > 0.5:
        tail = (nmax ** (1.0 - 2.0 * s)) / (2.0 * s - 1.0)
        M += np.outer(np.ones(N + 1), B0) * tail
    return M

def lead_eigs(M, k=6):
    ev = np.linalg.eigvals(M)
    ev = ev[np.argsort(-np.abs(ev))]
    return ev[:k]

def run_2a():
    out = {}
    N = 48
    M = gkw_matrix(N, s=1.0)
    ev = lead_eigs(M, 6)
    lam0 = ev[0].real
    lam1 = ev[1].real
    out["lambda_0"] = float(lam0)
    out["lambda_1"] = float(lam1)
    out["top6_eigs"] = [complex(e).__repr__() for e in ev]
    # Lyapunov via pressure derivative:  lambda_L = -d/ds log lambda_0(s) |_{s=1}
    h = 1e-3
    def lead(s):
        return np.max(np.abs(np.linalg.eigvals(gkw_matrix(N, s=s)))).real
    l_p = lead(1.0 + h)
    l_m = lead(1.0 - h)
    dlog = (math.log(l_p) - math.log(l_m)) / (2 * h)
    lyap = -dlog
    out["lyapunov_operator"] = float(lyap)
    out["lyapunov_exact_pi2_6ln2"] = math.pi**2 / (6 * math.log(2))
    out["levy_exp_operator"] = float(lyap / 2)
    out["levy_exp_exact_pi2_12ln2"] = math.pi**2 / (12 * math.log(2))
    out["levy_const_operator"] = float(math.exp(lyap / 2))
    out["levy_const_exact"] = math.exp(math.pi**2 / (12 * math.log(2)))
    # checks
    ref = PREREG["sub_2a_operator_sanity"]
    out["check"] = {
        "lambda_0_err": abs(lam0 - 1.0),
        "lambda_1_err": abs(lam1 - ref["gkw_subdominant_eigenvalue_lambda1"]),
        "lyapunov_relerr": abs(lyap - ref["gauss_lyapunov_pi2_over_6ln2"]) / ref["gauss_lyapunov_pi2_over_6ln2"],
        "levy_const_relerr": abs(math.exp(lyap/2) - ref["levy_constant_exp"]) / ref["levy_constant_exp"],
    }
    c = out["check"]
    out["PASS_2a"] = bool(c["lambda_0_err"] < 1e-4 and c["lambda_1_err"] < 5e-3
                          and c["lyapunov_relerr"] < 5e-3)
    return out

def run_2b():
    """Recover L_a = log(lambda_max(M_a)) by spectral computation, reconstruct ladder."""
    ref = PREREG["sub_2b_bridge_reproduction"]
    L_exact = {int(k): v for k, v in ref["L_exact_sealed"].items()}
    C_a = {int(k): v for k, v in ref["C_a_panelA_measured"].items()}
    C_err = {int(k): v for k, v in ref["C_a_error"].items()}
    theta_sealed = ref["theta_inf_sealed_ladder"]
    rungs = {}
    max_L_err = 0.0
    for a in range(1, 6):
        M = np.array([[float(a), 1.0], [1.0, 0.0]])
        ev = np.linalg.eigvals(M)              # spectral: top eig = eps_a
        eps_a = float(np.max(ev))
        L_op = math.log(eps_a)
        L_err = abs(L_op - L_exact[a])
        max_L_err = max(max_L_err, L_err)
        theta = L_op / C_a[a]
        cerr = C_err.get(a)
        theta_band = (L_op * cerr / C_a[a]**2) if cerr else None
        rungs[a] = {
            "eps_a_spectral": eps_a,
            "L_a_operator": L_op,
            "L_a_sealed": L_exact[a],
            "L_a_err": L_err,
            "C_a": C_a[a],
            "theta_inf_operator": theta,
            "theta_inf_band": theta_band,
        }
    # golden closed-form self-check
    theta_gold_closed = math.log((1 + math.sqrt(5)) / 2) / math.log(1 + math.sqrt(2))
    rungs[1]["theta_inf_closed_form_check"] = theta_gold_closed
    # ladder match: compare theta_inf_operator to sealed
    match = {}
    for a in range(1, 6):
        sealed = theta_sealed["2"] if a == 2 else theta_sealed.get(str(a))
        if a == 1:
            sealed = theta_sealed["1_measC"]
        got = rungs[a]["theta_inf_operator"]
        band = rungs[a]["theta_inf_band"] or 0.002
        match[a] = {"sealed": sealed, "operator": got,
                    "diff": abs(got - sealed), "within_band": abs(got - sealed) <= max(band, 5e-4)}
    out = {"rungs": rungs, "ladder_match": match,
           "max_L_a_err": max_L_err,
           "theta_gold_closed_form": theta_gold_closed}
    out["PASS_2b"] = bool(max_L_err < 1e-9 and all(m["within_band"] for m in match.values()))
    return out

if __name__ == "__main__":
    result = {"2a_operator_sanity": run_2a(), "2b_bridge": run_2b()}
    print(json.dumps(result, indent=2, default=str))
    outp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coprimary2_measured.json")
    json.dump(result, open(outp, "w"), indent=2, default=str)
    print("\nwrote", outp)
    print("\n2a PASS:", result["2a_operator_sanity"]["PASS_2a"],
          "| 2b PASS:", result["2b_bridge"]["PASS_2b"])
