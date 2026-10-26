"""RQ1 Step 3 read (RQ1_SEAL.md §5; runs only after the seal is approved, stamped and Bitcoin-attested).

For each X ∈ {1e10, 1e11}:
  n = # ℤ[√2] split primes ≤ X (manifest rows); the ℤ[i] set is its first n split primes (matched N = 2n ideals).
  θ arrays (both ideals) for each field, sorted; R_F(β) = Var/(N/K), K = round(N^β), β on the grid.
  D(β) = R_ℤ[√2] − R_ℤ[i]; SE_diff from the sealed model (c = 1.4); B2 = sign at the gated (β, X).
Witness: 20 seeded replicates of two independent uniform sets at each matched N, through the same B2 rule.

Estimator: RW eq. 1.2 on θ ∈ [0, 1), window 1/K, exact. Streaming over the sorted θ: the breakpoints θ ± w/2 are the
sorted array shifted, merged by two pointers; Σ len·(count − Nw)² accumulated centred with Kahan summation;
single-threaded and deterministic (the double read must be byte-identical).

  python rq1_read.py ZS2_DIR ZI_DIR OUT_JSON
"""
import hashlib
import json
import math
import os
import sys

import numpy as np
from numba import njit

import rq1_angles as R

BETAS = [0.20, 0.30, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70, 0.80, 0.90]
XS = [10 ** 10, 10 ** 11]
GATED = {10 ** 10: [0.40, 0.45], 10 ** 11: [0.30, 0.40, 0.45]}
C_SE = 1.4
N_WIT = 20
LOGEPS2 = 2.0 * math.log(1 + math.sqrt(2.0))


@njit(cache=False)
def var_stream(th, K):
    """Exact ∫₀¹ (N(c) − Nw)² dc for sorted th in [0, 1), window w = 1/K (circular)."""
    N = th.shape[0]
    w = 1.0 / K
    h = w / 2.0
    mean = N * w
    # count at c = 0: points within h of 0 on the circle
    c0 = 0
    for i in range(N):
        if th[i] < h:
            c0 += 1
        else:
            break
    for i in range(N - 1, -1, -1):
        if th[i] > 1.0 - h:
            c0 += 1
        else:
            break
    # events: starts at (θ − h) mod 1 (+1), ends at (θ + h) mod 1 (−1); each list is the sorted θ rotated
    # starts: θ ≥ h give θ − h (ascending), then θ < h give θ − h + 1 (ascending)
    i0 = 0
    while i0 < N and th[i0] < h:
        i0 += 1
    j0 = 0
    while j0 < N and th[j0] < 1.0 - h:
        j0 += 1
    # ends: θ ≥ 1 − h give θ + h − 1 (ascending), then θ < 1 − h give θ + h
    si, ei = 0, 0
    cnt = c0
    pos = 0.0
    acc, comp = 0.0, 0.0
    for _ in range(2 * N):
        if si < N:
            k = i0 + si
            s = th[k] - h if k < N else th[k - N] - h + 1.0
        else:
            s = 2.0
        if ei < N:
            k = j0 + ei
            e = th[k] + h - 1.0 if k < N else th[k - N] + h
        else:
            e = 2.0
        if s <= e:
            nxt, d = s, 1
            si += 1
        else:
            nxt, d = e, -1
            ei += 1
        dv = cnt - mean
        y = (nxt - pos) * dv * dv - comp
        t = acc + y
        comp = (t - acc) - y
        acc = t
        pos = nxt
        cnt += d
    dv = cnt - mean
    y = (1.0 - pos) * dv * dv - comp
    acc += y
    return acc


def load_field(d, field, n):
    """θ (both ideals) for the first n split primes of the archive in d, sorted; built segment by segment
    (each segment's sha256 checked against the manifest) to bound peak memory."""
    man = json.load(open(os.path.join(d, "MANIFEST.json")))
    th = np.empty(2 * n, np.float64)
    got = 0
    for s in man["segments"]:
        if got >= n:
            break
        path = os.path.join(d, f"seg_{s['k']:04d}.npy")
        assert hashlib.sha256(open(path, "rb").read()).hexdigest() == s["sha256"], path
        ab = np.load(path)[: n - got]
        if field == "zs2":
            t1, _ = R.thetas_from_ab(ab)
        else:
            t1 = np.arctan(ab[:, 0].astype(np.float64) / ab[:, 1].astype(np.float64)) / (math.pi / 2)
        th[got:got + len(ab)] = t1
        th[n + got:n + got + len(ab)] = np.mod(1.0 - t1, 1.0)
        got += len(ab)
    assert got == n
    th.sort()
    return th


def sorted_uniform(N, rng, chunk=1 << 26):
    """N sorted i.i.d. uniforms on [0, 1) without a sort: normalised cumulative sums of N + 1 exponential spacings."""
    out = np.empty(N, np.float64)
    tot, i = 0.0, 0
    while i < N:
        m = min(chunk, N - i)
        e = rng.standard_exponential(m)
        np.cumsum(e, out=out[i:i + m])
        out[i:i + m] += tot
        tot = out[i + m - 1]
        i += m
    tot += rng.standard_exponential()
    out /= tot
    return out


def n_below(d, X):
    man = json.load(open(os.path.join(d, "MANIFEST.json")))
    return int(sum(s["rows"] for s in man["segments"] if s["hi"] <= X))


def ratios(th, Ks):
    N = len(th)
    return [var_stream(th, K) / (N / K) for K in Ks]


def main(zs2, zi, out):
    res = dict(label="RQ1 read (sealed reading B)", rows={})
    b2_all = True
    for X in XS:
        n = n_below(zs2, X)
        N = 2 * n
        Ks = [int(round(N ** b)) for b in BETAS]
        r_s2 = ratios(load_field(zs2, "zs2", n), Ks)
        r_zi = ratios(load_field(zi, "zi", n), Ks)
        rows = []
        for b, K, a, c in zip(BETAS, Ks, r_s2, r_zi):
            se = math.sqrt((a * math.sqrt(2 / (C_SE * K))) ** 2 + (c * math.sqrt(2 / (C_SE * K))) ** 2)
            gated = b in GATED[X]
            ok = (a - c) > 0
            if gated:
                b2_all &= ok
            rows.append(dict(beta=b, K=K, R_zs2=a, R_zi=c, D=a - c, SE_diff=se, heuristic_logX=1.8489 / math.log(X),
                             heuristic_logN=1.8489 / math.log(N), B2_gated=gated, B2_sign_positive=bool(ok)))
            print(X, b, K, f"{a:.6f} {c:.6f} D {a - c:+.6f} SE {se:.4f}", "gated" if gated else "", flush=True)
        res["rows"][str(X)] = dict(n_split=n, N=N, rows=rows)
    res["B2"] = "PASS" if b2_all else "FAIL"
    # witness: two independent uniform sets at each matched N, the same B2 rule
    passes = 0
    for rep in range(N_WIT):
        rng = np.random.default_rng([8787, rep])
        ok_all = True
        for X in XS:
            N = res["rows"][str(X)]["N"]
            Ks = {b: int(round(N ** b)) for b in GATED[X]}
            u1 = sorted_uniform(N, rng)
            a = ratios(u1, list(Ks.values()))
            del u1
            u2 = sorted_uniform(N, rng)
            c = ratios(u2, list(Ks.values()))
            del u2
            ok_all &= all(x - y > 0 for x, y in zip(a, c))
        passes += int(ok_all)
    res["witness"] = dict(replicates=N_WIT, B2_pass_count=passes, OK=bool(passes <= 5))
    res["READING"] = res["B2"] if res["witness"]["OK"] else "VOID (witness)"
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    print("B2", res["B2"], "witness passes", passes, "READING", res["READING"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
