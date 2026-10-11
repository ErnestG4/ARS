"""Quadrature sizing for the ζ predictor, on the sine kernel (known answer = ND 40): v(b) at b = 100, 300 with ND
Gauss–Legendre nodes per in-pair offset on [0, DMAX], DMAX ∈ {2.8, 2.4}."""
import importlib

import numpy as np

import gs_unitary as G

ref = None
for dmax, nd in ((2.8, 40), (2.8, 24), (2.8, 20), (2.8, 16), (2.4, 20), (2.4, 16), (2.8, 12)):
    G.DMAX, G.ND = dmax, nd
    G.DN, G.DW = G.gl(0.0, dmax, nd)
    G.FD = G.F(G.DN)
    G.WD = 4 * np.outer(G.DW * G.FD, G.DW * G.FD)
    vals = [G.v_direct(b)[0] for b in (100, 300)]
    if ref is None:
        ref = vals
    print("DMAX %.1f ND %2d  v(100) %.10f  v(300) %.10f  rel diff vs ND40: %.1e %.1e"
          % (dmax, nd, vals[0], vals[1], vals[0] / ref[0] - 1, vals[1] / ref[1] - 1), flush=True)
