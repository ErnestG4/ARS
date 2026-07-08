"""Run 1 (KEYSTONE) — n=3 Mayer cross-check.

Extend the validated 2a GKW discretization to the s-parametrized Mayer-Ruelle
operator L_s on the critical line s=1/2+i r, and find its parity-resolved
eigenvalue-1 crossings:
    Mayer:  Z_Selberg(s) = det(1 - L_s) * det(1 + L_s)
    det(1 - L_s)=0  <=>  L_s has eigenvalue +1   (one Maass parity)
    det(1 + L_s)=0  <=>  L_s has eigenvalue -1   (the other parity)
On Re(s)=1/2 both determinants are real; their sign changes bracket the Maass
spectral parameters r_n. Match the first N per parity to LMFDB r_n -> (a) mechanism
receipt for CP1, (b) weld to CP2's operator, (c) CALIBRATION of the L_s pipeline
for Run 3, (d) settle the LMFDB even/odd label convention.

Tail of sum_n (n+x)^{-2s} f(1/(n+x)) is only conditionally convergent at Re(s)=1/2;
accelerated via 2-term Taylor + complex Hurwitz zeta (mpmath).
"""
import json, math, os
import numpy as np
import mpmath as mp

HERE = os.path.dirname(os.path.abspath(__file__))
mp.mp.dps = 15

def cheb_lobatto(N):
    k = np.arange(N + 1)
    x = (1.0 - np.cos(np.pi * k / N)) / 2.0
    w = np.ones(N + 1); w[1:-1:2] = -1.0; w[0] *= 0.5; w[-1] *= 0.5
    return x, w

def bary_row(nodes, w, y):
    diff = y - nodes
    if np.any(np.abs(diff) < 1e-14):
        r = np.zeros(len(nodes)); r[np.argmin(np.abs(diff))] = 1.0; return r
    t = w / diff
    return t / t.sum()

def hurwitz(a, q):
    return complex(mp.zeta(a, q))

def bary_matrix(nodes, w, Y):
    """Vectorized barycentric interpolation rows for query points Y (1D)."""
    Y = np.asarray(Y, float)
    diff = Y[:, None] - nodes[None, :]
    exact = np.abs(diff) < 1e-14
    t = np.where(exact, 0.0, w[None, :] / diff)
    B = t / t.sum(axis=1, keepdims=True)
    rows = np.where(exact.any(axis=1))[0]
    for i in rows:
        B[i, :] = 0.0; B[i, np.argmax(exact[i])] = 1.0
    return B

def mayer_matrix(N, s, Ne=400):
    """Discretized L_s at complex s; explicit n<=Ne (vectorized) + Hurwitz tail."""
    nodes, w = cheb_lobatto(N)
    dim = N + 1
    n = np.arange(1, Ne + 1)[None, :]                 # (1,Ne)
    xj = nodes[:, None]                                # (dim,1)
    wgt = (n + xj) ** (-2.0 * s)                        # (dim,Ne)
    Y = (1.0 / (n + xj)).ravel()                        # (dim*Ne,)
    B = bary_matrix(nodes, w, Y).reshape(dim, Ne, dim)  # (dim,Ne,dim)
    M = np.einsum("jk,jkd->jd", wgt, B)                 # (dim,dim)
    # tail n>Ne via 2-term Taylor of f around 0 + complex Hurwitz zeta
    h = 1e-3
    B0 = bary_matrix(nodes, w, [0.0])[0]
    B1 = (bary_matrix(nodes, w, [h])[0] - bary_matrix(nodes, w, [-h])[0]) / (2 * h)
    for j in range(dim):
        t0 = hurwitz(2 * s, Ne + 1 + nodes[j])
        t1 = hurwitz(2 * s + 1, Ne + 1 + nodes[j])
        M[j, :] += t0 * B0 + t1 * B1
    return M

def gaps_to_pm1(N, r, Ne=400):
    """min|lambda-1| (even/sym0 crossing) and min|lambda+1| (odd/sym1 crossing)."""
    ev = np.linalg.eigvals(mayer_matrix(N, 0.5 + 1j * r, Ne))
    return float(np.min(np.abs(ev - 1.0))), float(np.min(np.abs(ev + 1.0)))

def find_zeros(N, r_lo, r_hi, dr=0.02, Ne=400):
    """Scan; local minima of the two gap functions = parity-resolved Maass r_n."""
    rs = np.arange(r_lo, r_hi + 1e-9, dr)
    gp = np.empty(len(rs)); gm = np.empty(len(rs))
    for i, r in enumerate(rs):
        gp[i], gm[i] = gaps_to_pm1(N, r, Ne)
    def minima(g):
        out = []
        for i in range(1, len(g) - 1):
            if g[i] < g[i - 1] and g[i] < g[i + 1] and g[i] < 0.15:
                # parabolic refine
                a, b, c = g[i - 1], g[i], g[i + 1]
                denom = (a - 2 * b + c)
                shift = 0.5 * (a - c) / denom if denom != 0 else 0.0
                out.append(rs[i] + shift * dr)
        return out
    return {"even_sym0": minima(gp), "odd_sym1": minima(gm)}

def validate_s1(N=40):
    M = mayer_matrix(N, 1.0 + 0j)
    ev = np.linalg.eigvals(M)
    ev = ev[np.argsort(-np.abs(ev))]
    return {"lambda0": complex(ev[0]), "lambda1": complex(ev[1])}

def det_pm(N, r, Ne=600):
    M = mayer_matrix(N, 0.5 + 1j * r, Ne)
    I = np.eye(M.shape[0])
    d_minus = np.linalg.det(I - M)       # zero <=> eigenvalue +1
    d_plus = np.linalg.det(I + M)        # zero <=> eigenvalue -1
    return d_minus, d_plus

def match_to_lmfdb():
    d = np.genfromtxt(os.path.join(HERE, "maass_level1_partial.csv"),
                      delimiter=",", names=True)
    r, sym = d["r"], d["symmetry"].astype(int)
    return {"sym0": np.sort(r[sym == 0]), "sym1": np.sort(r[sym == 1])}

if __name__ == "__main__":
    import sys
    print("=== s=1 reduction sanity (should match 2a: lam0=1, lam1=-0.30366) ===")
    print(validate_s1())
    r_hi = float(sys.argv[1]) if len(sys.argv) > 1 else 20.0
    print(f"\n=== scanning critical line r in [9, {r_hi}] for eigenvalue +/-1 crossings ===")
    N = 48
    zeros = find_zeros(N, 9.0, r_hi, dr=0.02)
    lm = match_to_lmfdb()
    out = {"s1_sanity": {k: str(v) for k, v in validate_s1().items()},
           "found": {k: [round(x, 4) for x in v] for k, v in zeros.items()},
           "parity_convention": "eigenvalue+1 (det(1-L)=0) = EVEN = LMFDB sym0; "
                                "eigenvalue-1 (det(1+L)=0) = ODD = LMFDB sym1"}
    # match found even (sym0) and odd (sym1) to LMFDB
    match = {}
    for parity, key in [("even_sym0", "sym0"), ("odd_sym1", "sym1")]:
        found = np.array(sorted(zeros[parity])); ref = lm[key][: len(found) + 3]
        rows = []
        for f in found:
            j = int(np.argmin(np.abs(ref - f)))
            rows.append({"found": round(f, 4), "lmfdb": round(float(ref[j]), 4),
                         "err": round(abs(f - ref[j]), 4)})
        match[parity] = rows
    out["match"] = match
    for parity in ("even_sym0", "odd_sym1"):
        errs = [m["err"] for m in match[parity]]
        print(f"\n  {parity}: {len(match[parity])} found; max_err={max(errs):.4f}, "
              f"median_err={np.median(errs):.4f}")
        for m in match[parity][:12]:
            print(f"     found {m['found']:8.4f}  lmfdb {m['lmfdb']:8.4f}  err {m['err']:.4f}")
    json.dump(out, open(os.path.join(HERE, "mayer_run1_measured.json"), "w"), indent=2, default=str)
    print("\nwrote mayer_run1_measured.json")
