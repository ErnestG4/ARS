"""
PHASE 9 — settle cumulative-vs-local from inside. No literature.

Reviewer's two corrections, both taken:
  (i) The "local reading" C(lnln+K) + C/lnX was obtained by DIFFERENTIATING an asymptotic with an
      o(T) error. d/dT of o(T) is NOT o(1) -- it is unbounded. So that row is not entailed by the
      cited theorem and is STRUCK as a comparison. The algebra was right; the object does not inherit
      the theorem's grade.
  (ii) The question is decidable from the data: compute the CUMULATIVE integral directly with the
      same exact O(W) machinery and compare it to the LOCAL block values at the same heights.

And a THIRD form difference neither of us listed, which may be the whole story:
    Goldston's int_0^T S^2 dt is an UNCENTERED second moment.
    My Var[S] is CENTERED (block mean removed).
    They differ by <S>^2, which is NOT obviously negligible over a block.
So three axes, not one: cumulative-vs-local, t-average-vs-u-average, centered-vs-uncentered.

Stub, flagged by the reviewer: cumulative from gamma_1 is not cumulative from 0. Computed explicitly.
"""
from __future__ import annotations
import json, math, os
import numpy as np
from scipy.special import loggamma
from scipy.integrate import quad

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
p = lambda *a: print(*a, flush=True)
C = 1.0 / (2 * math.pi ** 2)
K = 1.400967852459


def exact_N(t):
    t = np.asarray(t, float)
    return (np.imag(loggamma(0.25 + 0.5j * t)) - 0.5 * t * math.log(math.pi)) / math.pi + 1.0


def rho(t):
    return np.log(np.asarray(t, float) / (2 * math.pi)) / (2 * math.pi)


z = np.sort(np.loadtxt(os.path.join(ROOT, "data", "odlyzko_zeros6.txt")))
u_all = exact_N(z)

# ---------------------------------------------------------------- the stub [0, gamma_1]
stub = quad(lambda t: (exact_N(np.array([t]))[0]) ** 2, 0.0, float(z[0]), limit=200)[0]
p(f"[stub] int_0^gamma_1 S^2 dt = {stub:.4f}  (S = -N_smooth below the first zero)")
p(f"       at T=1e6 this is {stub/(1e6*C):.5f} in units of the bracket -- {100*stub/(1e6*C)/K:.3f}% of K\n")

# ---------------------------------------------------------------- per-gap exact pieces
# On (gamma_j, gamma_{j+1}): S(u) = j - u linear in u; dt = du/rho, rho ~ constant over one gap.
s = np.arange(1, len(z) + 1, dtype=float) - u_all
a = s[:-1]; b = s[1:] - 1.0
Lu = a - b                                              # gap length in u
rmid = rho(0.5 * (z[:-1] + z[1:]))                      # rho at gap midpoint
I2_u = (a ** 3 - b ** 3) / 3.0                          # int S^2 du per gap
I1_u = (a ** 2 - b ** 2) / 2.0                          # int S   du per gap
I2_t = I2_u / rmid                                      # int S^2 dt per gap
I1_t = I1_u / rmid
Lt = Lu / rmid

p("[A] CUMULATIVE — does int_0^T S^2 dt match Goldston's form?")
p(f"  G(T) = (2 pi^2 / T) int_0^T S^2 dt - lnln(T/2pi);  Goldston: G -> K = {K:.6f}")
p(f"  {'T':>12s} {'lnln':>8s} {'G(T)':>10s} {'G-K':>9s}")
cum2 = np.concatenate([[stub], stub + np.cumsum(I2_t)])
rows = []
for frac in (0.05, 0.15, 0.35, 0.6, 0.85, 1.0):
    i = int(frac * (len(z) - 1))
    T = float(z[i]); ll = math.log(math.log(T / (2 * math.pi)))
    G = cum2[i] / (T * C) - ll
    rows.append((T, ll, G))
    p(f"  {T:>12.4g} {ll:>8.4f} {G:>10.5f} {G-K:>+9.5f}")
p(f"  -> cumulative {'MATCHES Goldston' if abs(rows[-1][2]-K) < 0.02 else 'does NOT match Goldston'}"
  f" at the top (|G-K| = {abs(rows[-1][2]-K):.5f})\n")

# ---------------------------------------------------------------- local, three ways
p("[B] LOCAL — the same blocks, under all three form conventions")
W, ANCH = 20000, [40000, 300000, 900000, 1900000]
p(f"  {'lnln':>8s} {'V centred(u)':>13s} {'M2 uncent(u)':>13s} {'M2 uncent(t)':>13s} {'<S>':>9s} {'<S>^2':>9s}")
out = []
for a0 in ANCH:
    for k in range(3):
        i0 = a0 + k * W
        if i0 + W >= len(z) - 1:
            continue
        sl_ = slice(i0, i0 + W - 1)
        Uu = float(Lu[sl_].sum()); Ut = float(Lt[sl_].sum())
        m1u = float(I1_u[sl_].sum()) / Uu
        m2u = float(I2_u[sl_].sum()) / Uu
        m2t = float(I2_t[sl_].sum()) / Ut
        gm = float(z[i0 + W // 2]); ll = math.log(math.log(gm / (2 * math.pi)))
        out.append((ll, m2u - m1u ** 2, m2u, m2t, m1u))
        if k == 0:
            p(f"  {ll:>8.4f} {m2u-m1u**2:>13.6f} {m2u:>13.6f} {m2t:>13.6f} {m1u:>9.5f} {m1u**2:>9.6f}")
o = np.array(out)
p(f"\n  mean <S>^2 across blocks = {np.mean(o[:,4]**2):.6f}  "
  f"({100*np.mean(o[:,4]**2)/np.mean(o[:,1]):.2f}% of V)")
p(f"  -> centred vs uncentred differ by {'MORE' if np.mean(o[:,4]**2) > 0.001 else 'less'} than 0.001;")
p(f"     u-average vs t-average differ by {abs(np.mean(o[:,3]-o[:,2])):.6f}")

p("\n[C] which local form does the cumulative's derivative actually pick out?")
p("  dI/dT computed as a finite difference of the measured cumulative, vs the measured local M2(t):")
for a0 in ANCH:
    i0 = a0 + W
    if i0 + W >= len(z) - 1:
        continue
    T0, T1 = float(z[i0]), float(z[i0 + W - 1])
    dIdT = (cum2[i0 + W - 1] - cum2[i0]) / (T1 - T0)
    sl_ = slice(i0, i0 + W - 1)
    m2t = float(I2_t[sl_].sum()) / float(Lt[sl_].sum())
    ll = math.log(math.log(float(z[i0 + W // 2]) / (2 * math.pi)))
    p(f"  lnln {ll:.4f}:  dI/dT = {dIdT:.6f}   M2(t) local = {m2t:.6f}   diff {dIdT-m2t:+.2e}")
p("  (these must agree by construction -- it is a check on the machinery, not on zeta)")

json.dump({"stub": stub, "cumulative_G": [[r[0], r[1], r[2]] for r in rows], "K": K,
           "local": o.tolist(),
           "mean_S_squared": float(np.mean(o[:, 4] ** 2))},
          open(os.path.join(HERE, "phase9_form_measured.json"), "w"), indent=2)
p("\nwrote phase9_form_measured.json")
