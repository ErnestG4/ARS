"""RQ1-c (round 96, prerequisite 2): the binned estimator for 10¹², and its validation.

Histogram: counts of θ ∈ [0, ½] (the stored half-set) in nb = 2^(B−1) bins of width δ = 2^−B; the full circle is the
mirror (bin j and bin 2nb − 1 − j hold the same count), applied in the kernel, so only the half is stored (2⁻³⁶ at 10¹²:
34 GB as uint8). var_binned is rq1_read.var_stream's exact two-pointer merge with every point moved to its bin centre:
events at centre ± w/2 with weight = the bin's count. On the rounded point set it equals var_stream to rounding (checked
in `selftest`). Rounding biases R upward by at most about N·δ²·K (round 92: measured 0.08–0.25 of that on synthetic
mirror-symmetric sets).

Validation (`validate`; post hoc, on the already-read 10¹⁰ / 10¹¹ archives): at each gated β (P1 0.40, 0.45; P4 0.55;
P3 0.45–0.65 step 0.01, with ℤ[i] at a·K), B is chosen so that N·δ²·K is at least as large as at 10¹² with δ = 2⁻³⁶
(the stress the 10¹² read will see), and |R_binned − R_exact| is reported against N·δ²·K. R_exact is the read's and the
round-92 collapse run's (results/collapse/COLLAPSE.json, which reproduced the read bit-exactly).

  python rq1c_binned.py selftest
  python rq1c_binned.py validate ZS2_DIR ZI_DIR OUT_JSON
"""
import json
import math
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from numba import njit

import rq1_read as Q

N12 = 2 * 1.880e10
B12 = 36
A = math.pi / (math.sqrt(2) * math.log(1 + math.sqrt(2)))


@njit(cache=False, nogil=True)
def var_binned(c, K):
    """Exact ∫₀¹ (N(x) − N w)² dx for the mirror-symmetric point set with c[j] points at ((j + ½)/(2nb)) for j < nb and
    the mirror image, windows of width w = 1/K (circular)."""
    nb = c.shape[0]
    NB = 2 * nb
    d = 1.0 / NB
    w = 1.0 / K
    h = w / 2.0
    tot = 0.0
    for j in range(nb):
        tot += c[j]
    tot *= 2.0
    mean = tot * w
    # count at x = 0
    c0 = 0.0
    for j in range(NB):
        x = (j + 0.5) * d
        if x < h or x > 1.0 - h:
            c0 += c[j] if j < nb else c[NB - 1 - j]
    # starts: x − h for x ≥ h ascending, then x − h + 1 for x < h; ends: x + h − 1 for x ≥ 1 − h, then x + h
    i0 = 0
    while i0 < NB and (i0 + 0.5) * d < h:
        i0 += 1
    j0 = 0
    while j0 < NB and (j0 + 0.5) * d < 1.0 - h:
        j0 += 1
    si, ei = 0, 0
    cnt = c0
    pos = 0.0
    acc, comp = 0.0, 0.0
    for _ in range(2 * NB):
        if si < NB:
            k = i0 + si
            kk = k if k < NB else k - NB
            s = (kk + 0.5) * d - h + (0.0 if k < NB else 1.0)
            ws = c[kk] if kk < nb else c[NB - 1 - kk]
        else:
            s = 2.0
            ws = 0
        if ei < NB:
            k = j0 + ei
            kk = k if k < NB else k - NB
            e = (kk + 0.5) * d + h - (1.0 if k < NB else 0.0)
            we = c[kk] if kk < nb else c[NB - 1 - kk]
        else:
            e = 2.0
            we = 0
        if s <= e:
            nxt, dl = s, ws
            si += 1
        else:
            nxt, dl = e, -we
            ei += 1
        dv = cnt - mean
        y = (nxt - pos) * dv * dv - comp
        t = acc + y
        comp = (t - acc) - y
        acc = t
        pos = nxt
        cnt += dl
    dv = cnt - mean
    acc += (1.0 - pos) * dv * dv - comp
    return acc, tot


def hist_half(th_half, B, dtype=np.uint16, chunk=1 << 26):
    """Counts of the sorted half-set in 2^(B−1) bins, built chunk by chunk from run lengths (no int64 array of
    length nb)."""
    nb = 2 ** (B - 1)
    h = np.zeros(nb, dtype)
    top = np.iinfo(dtype).max
    for i in range(0, len(th_half), chunk):
        idx = np.minimum((th_half[i:i + chunk] * (2 * nb)).astype(np.int64), nb - 1)
        cut = np.flatnonzero(np.diff(idx)) + 1
        starts = np.concatenate([[0], cut])
        counts = np.diff(np.concatenate([starts, [len(idx)]]))
        u = idx[starts]
        new = h[u].astype(np.int64) + counts
        assert new.max() <= top
        h[u] = new
    return h


def coarsen(h, steps):
    return h.reshape(-1, 2 ** steps).sum(1, dtype=np.int64).astype(h.dtype) if steps else h


def selftest():
    rng = np.random.default_rng(96)
    n = 200_000
    t = np.sort(rng.random(n) * 0.5)
    for B in (12, 16, 20):
        h = hist_half(t, B)
        nb = len(h)
        cen = (np.repeat(np.arange(nb), h) + 0.5) / (2 * nb)
        full = np.sort(np.concatenate([cen, 1 - cen]))
        for K in (7, 100, 3000, 50000):
            vb, tot = var_binned(h, float(K))
            vs = Q.var_stream(full, float(K))
            print(f"B={B} K={K}: binned {vb:.10e} stream-on-rounded {vs:.10e} rel {abs(vb - vs) / vs:.1e}")
    return 0


def half_set(d, field, n):
    th = Q.load_field(d, field, n)
    return np.ascontiguousarray(th[th <= 0.5])


def validate(zs2, zi, out):
    col = json.load(open("results/collapse/COLLAPSE.json"))["rows"]
    res = dict(label="RQ1-c binned estimator validation (round 96; post hoc on the read archives)", B12=B12, rows={})
    t0 = time.time()
    with ThreadPoolExecutor(16) as pool:
        for X in Q.XS:
            n = Q.n_below(zs2, X)
            N = 2 * n
            ex = {r["beta"]: r for r in col[str(X)]["rows"]}
            betas = sorted(set([0.40, 0.45, 0.55] + ([round(0.45 + 0.01 * i, 2) for i in range(21)] if X == 10 ** 11 else [])))
            jobs = []
            for b in betas:
                K = ex[b]["K"]
                bias12 = N12 * 2.0 ** (-2 * B12) * N12 ** b
                B = math.floor(0.5 * math.log2(N * K / bias12))                 # coarsest B with N δ² K ≥ the 10¹² value
                jobs.append((b, K, B, "zs2", K))
                jobs.append((b, K, B, "zi", K))
                if X == 10 ** 11:
                    jobs.append((b, K, B, "zi_aK", A * K))
            Bmax = max(j[2] for j in jobs)
            rows = []
            for field, d in (("zs2", zs2), ("zi", zi)):
                h = hist_half(half_set(d, field, n), Bmax)
                hs = {B: coarsen(h, Bmax - B) for B in set(j[2] for j in jobs)}
                mine = [j for j in jobs if j[3].startswith(field)]
                vals = list(pool.map(lambda j: var_binned(hs[j[2]], float(j[4]))[0] / (N / j[4]), mine))
                for (b, K, B, f, KK), v in zip(mine, vals):
                    key = {"zs2": "R_zs2", "zi": "R_zi", "zi_aK": "R_zi_aK"}[f]
                    exact = ex[b][key]
                    bound = N * 2.0 ** (-2 * B) * KK
                    se = math.sqrt(2 / (Q.C_SE * KK)) * exact
                    rows.append(dict(beta=b, field=f, K=KK, B=B, R_binned=v, R_exact=exact, diff=v - exact,
                                     bound_NdeltaK=bound, diff_over_bound=(v - exact) / bound, diff_over_SE=(v - exact) / se))
                del h, hs
            res["rows"][str(X)] = rows
            print(X, f"{time.time() - t0:.0f} s", max(abs(r["diff_over_bound"]) for r in rows),
                  max(abs(r["diff_over_SE"]) for r in rows), flush=True)
    res["max_abs_diff_over_bound"] = max(abs(r["diff_over_bound"]) for v in res["rows"].values() for r in v)
    res["max_abs_diff_over_SE"] = max(abs(r["diff_over_SE"]) for v in res["rows"].values() for r in v)
    res["wall_s"] = time.time() - t0
    json.dump(res, open(out, "w"), indent=1)
    print("max |diff|/bound", res["max_abs_diff_over_bound"], "max |diff|/SE", res["max_abs_diff_over_SE"])
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "selftest":
        sys.exit(selftest())
    sys.exit(validate(sys.argv[2], sys.argv[3], sys.argv[4]))
