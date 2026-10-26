"""RQ1 angle precision (round 88). Primes in a window just above 1.01·10¹¹, outside both archives (ℤ[√2] < 10¹¹,
ℤ[i] < 1.01·10¹¹); nothing is read from the archives.

For each field, the float θ the read uses (rq1_read.field_thetas, and its mirror np.mod(1 − θ, 1)) is compared
against mpmath at 50 digits:
  ℤ[√2]: θ = log((a + b√2)/|a − b√2|)/(2 log ε), ε = 1 + √2, for the generator rq1_angles.gen_segment stores;
  ℤ[i]:  θ = atan(u/v)·2/π for the stored pair 0 < u < v.
Unit shift: multiplying by a unit shifts θ by exactly 1 (in the unreduced angle).
  ℤ[√2]: π·εᵏ = (a, b)·(1 + √2)ᵏ, k = 1, 2, 3 (both coordinates stay positive), through the read's float formula
         (rq1_angles.thetas_from_ab); the deviation is |θ(πεᵏ) − θ(π) − k|; mpmath checks the identity exactly.
  ℤ[i]:  iᵏ·(v + iu), k = 1, 2, 3, through θ = atan2(Im, Re)/(π/2); the deviation is the distance of
         θ(iᵏz) − θ(z) − k from 4ℤ; mpmath likewise.
Reported against the smallest window, 1/K_max, K_max = round(N^0.90) at the X = 10¹¹ matched N.

  python rq1_precision.py OUT_JSON
"""
import json
import math
import sys

import mpmath as mp
import numpy as np

import rq1_angles as R
import rq1_read as Q

LO, W = 101 * 10 ** 9, 2 * 10 ** 6
N11 = 2 * 2059026114
mp.mp.dps = 50


def zs2():
    ab = R.gen_segment(LO, LO + W).astype(np.int64)
    th = Q.field_thetas(ab, "zs2")
    mir = np.mod(1.0 - th, 1.0)
    s2, le = mp.sqrt(2), mp.log(1 + mp.sqrt(2))
    d_th = d_mir = d_unit_f = d_unit_mp = 0.0
    for (a, b), t, m in zip(ab.tolist(), th.tolist(), mir.tolist()):
        tm = mp.log((a + b * s2) / abs(a - b * s2)) / (2 * le)
        d_th = max(d_th, abs(float(tm - t)))
        d_mir = max(d_mir, abs(float((1 - tm) - m)))
        aa, bb = a, b
        for k in (1, 2, 3):
            aa, bb = aa + 2 * bb, aa + bb                          # × ε
            tk = Q.field_thetas(np.array([[aa, bb]], np.int64), "zs2")[0]
            d_unit_f = max(d_unit_f, abs(tk - t - k))
            tkm = mp.log((aa + bb * s2) / abs(aa - bb * s2)) / (2 * le)
            d_unit_mp = max(d_unit_mp, abs(float(tkm - tm - k)))
    return dict(primes=len(ab), max_abs_dtheta=d_th, max_abs_dmirror=d_mir, unit_shift_float_max_dev=d_unit_f,
                unit_shift_mpmath_max_dev=d_unit_mp)


def zi():
    uv = R.gen_segment_zi(LO, LO + W).astype(np.int64)
    th = Q.field_thetas(uv, "zi")
    mir = np.mod(1.0 - th, 1.0)
    d_th = d_mir = d_unit_f = d_unit_mp = 0.0

    def dist4(x):
        return abs(x - 4 * round(x / 4))
    for (u, v), t, m in zip(uv.tolist(), th.tolist(), mir.tolist()):
        tm = mp.atan(mp.mpf(u) / v) * 2 / mp.pi
        d_th = max(d_th, abs(float(tm - t)))
        d_mir = max(d_mir, abs(float((1 - tm) - m)))
        x, y = v, u                                                 # z = v + iu: θ(z) = atan(u/v)/(π/2), the stored θ
        t0 = math.atan2(y, x) / (math.pi / 2)
        t0m = mp.atan2(y, x) * 2 / mp.pi
        for k in (1, 2, 3):
            x, y = -y, x                                            # × i
            d_unit_f = max(d_unit_f, dist4(math.atan2(y, x) / (math.pi / 2) - t0 - k))
            d_unit_mp = max(d_unit_mp, dist4(float(mp.atan2(y, x) * 2 / mp.pi - t0m - k)))
        d_th = max(d_th, abs(t0 - t))                               # the general formula agrees with the read's map
    return dict(primes=len(uv), max_abs_dtheta=d_th, max_abs_dmirror=d_mir, unit_shift_float_max_dev=d_unit_f,
                unit_shift_mpmath_max_dev=d_unit_mp)


def main(out):
    kmax = int(round(N11 ** 0.90))
    res = dict(window=[LO, LO + W], mpmath_dps=50, K_max=kmax, min_window=1.0 / kmax, zs2=zs2(), zi=zi())
    worst = max(res[f][k] for f in ("zs2", "zi") for k in ("max_abs_dtheta", "max_abs_dmirror",
                                                             "unit_shift_float_max_dev"))
    res["worst_float_dev"] = worst
    res["worst_over_min_window"] = worst * kmax
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
