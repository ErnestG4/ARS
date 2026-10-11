"""In-pair quadrature v2: Gauss–Jacobi with weight d² on [0, DMAX] (ρ₄c ∝ d² as d → 0, so the integrand / d² is smooth;
the nodes move away from d = 0, where the ζ pieces cancel catastrophically: d = 0.008 gave 5% imaginary residue).
Sine kernel, v(b = 100, 300), against the ND 40 GL reference on [0, 2.8]."""
import numpy as np
from scipy.special import roots_jacobi

import gs_unitary as G

REF = {100: 0.1199557972, 300: 0.1137197623}


def gj(dmax, n):
    x, w = roots_jacobi(n, 0.0, 2.0)                 # weight (1 + x)² on [−1, 1]
    d = 0.5 * dmax * (1 + x)
    return d, 0.5 * dmax * w / (1 + x) ** 2


for dmax, nd in ((2.4, 20), (2.4, 16), (2.4, 24), (2.6, 20)):
    G.DN, G.DW = gj(dmax, nd)
    G.FD = G.F(G.DN)
    G.WD = 4 * np.outer(G.DW * G.FD, G.DW * G.FD)
    vals = [G.v_direct(b)[0] for b in (100, 300)]
    print("GJ DMAX %.1f ND %2d  min node %.4f  v(100) %.10f  v(300) %.10f  rel %.1e %.1e"
          % (dmax, nd, G.DN.min(), vals[0], vals[1], vals[0] / REF[100] - 1, vals[1] / REF[300] - 1), flush=True)
