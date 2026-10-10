"""Diagnostic (not a gate): precision of the fast evaluator's full connected ρ₄c near coincident points, where the
CS08 pieces have poles that cancel in the sum. Two pairs d = (0.5, 0.7); r = (d₂ − d₁)/2 + δ puts x₃ within δ of x₁.
Fast (cs4fast, double with long-double phases) against the 50-digit reference (cs4ref), δ = 1e-1 … 1e-5.
Also one exact-coincidence-adjacent diagonal node (d₁ = d₂ = 0.5, r = δ).

  python diag_coinc.py OUT
"""
import json
import math
import os
import sys

import mpmath as mp
import numpy as np

import cs4fast as F
import cs4ref as RF
import cs4split as S

T = 2 * math.pi * math.exp(16.5)


def main(out):
    ref = RF.ZetaRef(2 * mp.pi * mp.exp(16.5))
    fast = F.FastZeta(T, pmax=100_000)
    rows = []
    for (d1, d2, r0) in ((0.5, 0.7, 0.1), (0.5, 0.5, 0.0)):
        for dl in (1e-1, 1e-2, 1e-3, 1e-4, 1e-5):
            r = r0 + dl
            o, n_, tot = S.connected_split(ref, d1, d2, r)
            fo, fn = fast.connected(d1, d2, np.array([r]))
            ft = complex(fo[0] + fn[0])
            err = abs(ft - complex(tot))
            rows.append(dict(d1=d1, d2=d2, r=r, delta=dl, ref=str(tot), fast=str(ft), err=err))
            print("d=(%.1f,%.1f) δ=%.0e  ref %.6e  fast %.6e  err %.2e" % (d1, d2, dl, float(mp.re(tot)), ft.real, err), flush=True)
    os.makedirs(out, exist_ok=True)
    json.dump(rows, open(os.path.join(out, "diag_coinc.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
