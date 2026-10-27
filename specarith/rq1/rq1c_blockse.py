"""RQ1-c SE check by block estimate (round 97). Synthetic data only; nothing from any archive.

Block estimate: the variance integral ∫₀¹ (N(x) − Nw)² dx is accumulated separately over M = 1000 equal arcs of the
circle; mirror symmetry makes arcs b and M − 1 − b identical, so the 500 pair sums P_b are the independent blocks on the
mirror half. R = Σ P_b / (N/K) and SE_block(R) = √(500 · var(P_b, ddof 1)) / (N/K). Block width (half circle) 10⁻³.
Windows at the gated cells (K = round(N₁₂^β), N₁₂ = 3.76·10¹⁰): β 0.40 → 1/K = 5.9·10⁻⁵ (block/window 17), β 0.45 →
1.74·10⁻⁵ (57), β 0.55 → 1.53·10⁻⁶ (655): ≥ 10× at every cell.

Families (mirror-symmetrised, n points on the half plus their mirrors):
  mix: the round-88 planted design, a lattice fraction ρ = 0.114 plus i.i.d. points (R ≈ 0.886);
  jit: a jittered lattice, (j + ½)/(2n) + σ·N(0, 1), σ = 9.3·10⁻⁶, folded into [0, ½] (R ≈ 2Kσ/√π for small Kσ: 0.18,
       0.60 and saturated at the three K).

CRITERIA (declared here, committed before running):
  VALIDATION (N = 10⁹, 100 replicates per family, seeds [9700, family, rep]): PASS iff for both families and each
  β ∈ {0.40, 0.45, 0.55}, |mean SE_block / SD(R over replicates) − 1| ≤ 0.15. On failure: report and stop.
  COMPARISON (only after VALIDATION passes; full N = 3.76·10¹⁰, binned at 2⁻³⁶, one set per family, seeds
  [9701, family]): PASS iff |SE_block(full) / mean SE_block(reduced) − 1| ≤ 0.20 for both families and each β.
  PASS → reduced-N witnesses; FAIL → report.

  python rq1c_blockse.py selftest
  python rq1c_blockse.py validate OUT_JSON [NPROC]
  python rq1c_blockse.py full OUT_JSON VALIDATION_JSON

Stated before the run: in a small-N plumbing test that broke the ≥ 10× rule (block/window 0.2, 1.25, 6), the block SE
underestimated the mixture family's replicate SD (ratios 0.36, 0.65, 0.81); the jittered family was within 0.87–1.07.
The production ratios are 17, 57 and 655.
"""
import json
import math
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

import numpy as np
from numba import njit

import rq1_read as Q
import rq1_witness as W

N12 = 3.76e10
BETAS = [0.40, 0.45, 0.55]
KS = [int(round(N12 ** b)) for b in BETAS]
M = 1000
RHO, SIGMA = 0.114, 9.3e-6
N_RED, NREP = 10 ** 9, 100


@njit(cache=False, nogil=True)
def _add(blocks, a, b, v):
    i = int(a * M)
    while a < b and i < M:
        e = min(b, (i + 1) / M)
        blocks[i] += (e - a) * v
        a = e
        i += 1


@njit(cache=False, nogil=True)
def var_stream_blocks(th, K):
    """rq1_read.var_stream with the integral split over M arcs."""
    N = th.shape[0]
    w = 1.0 / K
    h = w / 2.0
    mean = N * w
    blocks = np.zeros(M)
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
    i0 = 0
    while i0 < N and th[i0] < h:
        i0 += 1
    j0 = 0
    while j0 < N and th[j0] < 1.0 - h:
        j0 += 1
    si, ei, cnt, pos = 0, 0, c0, 0.0
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
        _add(blocks, pos, nxt, dv * dv)
        pos = nxt
        cnt += d
    dv = cnt - mean
    _add(blocks, pos, 1.0, dv * dv)
    return blocks


@njit(cache=False, nogil=True)
def var_binned_blocks(c, K):
    """rq1c_binned.var_binned with the integral split over M arcs."""
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
    blocks = np.zeros(M)
    c0 = 0.0
    for j in range(NB):
        x = (j + 0.5) * d
        if x < h or x > 1.0 - h:
            c0 += c[j] if j < nb else c[NB - 1 - j]
    i0 = 0
    while i0 < NB and (i0 + 0.5) * d < h:
        i0 += 1
    j0 = 0
    while j0 < NB and (j0 + 0.5) * d < 1.0 - h:
        j0 += 1
    si, ei, cnt, pos = 0, 0, c0, 0.0
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
        _add(blocks, pos, nxt, dv * dv)
        pos = nxt
        cnt += dl
    dv = cnt - mean
    _add(blocks, pos, 1.0, dv * dv)
    return blocks, tot


def r_se(blocks, N, K):
    P = blocks[:M // 2] + blocks[::-1][:M // 2]
    nk = N / K
    return float(P.sum() / nk), float(math.sqrt((M // 2) * P.var(ddof=1)) / nk)


def gen_mix(n, rng):
    m = int(round(RHO * n))
    buf = np.empty(2 * n)
    Q.sorted_uniform(n - m, rng, out=buf[n:2 * n - m], scale=0.5)
    W.merge_lattice(buf[n:2 * n - m], m, buf[:n])
    W.mirror_into(buf, n)
    return buf


def gen_jit(n, rng, sigma=None):
    sigma = SIGMA if sigma is None else sigma
    buf = np.empty(2 * n)
    x = buf[:n]
    x[:] = (np.arange(n) + 0.5) / (2 * n)
    x += sigma * rng.standard_normal(n)
    np.abs(x, out=x)                                  # fold into [0, ½] (σ ≪ ½, so one reflection at each end)
    np.minimum(x, 1.0 - x, out=x)
    x.sort()
    W.mirror_into(buf, n)
    return buf


GEN = {"mix": gen_mix, "jit": gen_jit}


def one_rep(args):
    fam, rep = args
    rng = np.random.default_rng([9700, 0 if fam == "mix" else 1, rep])
    th = GEN[fam](N_RED // 2, rng)
    with ThreadPoolExecutor(len(KS)) as pool:
        bl = list(pool.map(lambda K: var_stream_blocks(th, float(K)), KS))
    return fam, rep, [r_se(b, len(th), K) for b, K in zip(bl, KS)]


def selftest():
    rng = np.random.default_rng(1)
    for fam in ("mix", "jit"):
        th = GEN[fam](200_000, rng)
        for K in (50, 2000):
            b = var_stream_blocks(th, float(K))
            v = Q.var_stream(th, float(K))
            print(fam, K, "block sum vs var_stream rel", abs(b.sum() - v) / v, "R", b.sum() / (len(th) / K))
    return 0


def validate(out, nproc=6):
    t0 = time.time()
    res = {"mix": [], "jit": []}
    with ProcessPoolExecutor(nproc) as ex:
        for fam, rep, vals in ex.map(one_rep, [(f, r) for f in ("mix", "jit") for r in range(NREP)]):
            res[fam].append(vals)
    summ = dict(label="RQ1-c block-SE validation (round 97); synthetic, N = 1e9", N=N_RED, reps=NREP, betas=BETAS, K=KS,
                block_width_half=0.5 / (M // 2), window=[1 / K for K in KS], families={}, wall_s=time.time() - t0)
    ok = True
    for fam, rows in res.items():
        a = np.array(rows)                                # rep × β × (R, SE)
        cells = []
        for i, b in enumerate(BETAS):
            sd = float(a[:, i, 0].std(ddof=1))
            mse = float(a[:, i, 1].mean())
            ratio = mse / sd
            cells.append(dict(beta=b, K=KS[i], R_mean=float(a[:, i, 0].mean()), SD_reps=sd, SE_block_mean=mse,
                              ratio=ratio, model_SE=float(a[:, i, 0].mean() * math.sqrt(2 / (Q.C_SE * KS[i]))),
                              pass_=bool(abs(ratio - 1) <= 0.15)))
            ok &= abs(ratio - 1) <= 0.15
        summ["families"][fam] = cells
    summ["VALIDATION_PASS"] = bool(ok)
    json.dump(summ, open(out, "w"), indent=1)
    for fam, cells in summ["families"].items():
        for c in cells:
            print(fam, c["beta"], f"R {c['R_mean']:.4f} SD {c['SD_reps']:.3e} blockSE {c['SE_block_mean']:.3e} ratio {c['ratio']:.3f}")
    print("VALIDATION_PASS", ok)
    return 0


B_FULL = 36


def _add_sorted(h, x, nb):
    """Add the sorted positions x ∈ [0, ½] to the half-histogram h (nb bins) by run lengths."""
    idx = np.minimum((x * (2 * nb)).astype(np.int64), nb - 1)
    cut = np.flatnonzero(np.diff(idx)) + 1
    starts = np.concatenate([[0], cut])
    cnt = np.diff(np.concatenate([starts, [len(idx)]]))
    u = idx[starts]
    new = h[u].astype(np.int64) + cnt
    assert new.max() <= 255
    h[u] = new


def hist_full(fam, rng, chunk=1 << 27):
    """Half-histogram (2^(B−1) bins, uint8) of one full-N set of the family, generated in chunks; nothing is stored
    at point level."""
    nb = 2 ** (B_FULL - 1)
    n = int(N12 // 2)
    h = np.zeros(nb, np.uint8)
    if fam == "mix":
        m = int(round(RHO * n))
        lam = (n - m) / nb
        for i in range(0, nb, chunk):
            k = min(chunk, nb - i)
            h[i:i + k] += rng.poisson(lam, k).astype(np.uint8)
        for j in range(0, m, chunk):
            k = min(chunk, m - j)
            _add_sorted(h, (np.arange(j, j + k) + 0.5) / (2 * m), nb)
    else:
        for j in range(0, n, chunk):
            k = min(chunk, n - j)
            x = (np.arange(j, j + k) + 0.5) / (2 * n) + SIGMA * rng.standard_normal(k)
            np.abs(x, out=x)
            np.minimum(x, 1.0 - x, out=x)
            x.sort()
            _add_sorted(h, x, nb)
    return h


def full(out, val_path):
    val = json.load(open(val_path))
    assert val["VALIDATION_PASS"], "validation failed: stop (round 97)"
    t0 = time.time()
    res = dict(label="RQ1-c block-SE comparison, full N against reduced N (round 97); synthetic", N=N12, B=B_FULL,
               betas=BETAS, K=KS, families={})
    ok = True
    for fi, fam in enumerate(("mix", "jit")):
        h = hist_full(fam, np.random.default_rng([9701, fi]))
        with ThreadPoolExecutor(len(KS)) as pool:
            out_b = list(pool.map(lambda K: var_binned_blocks(h, float(K)), KS))
        cells = []
        for i, (b, K) in enumerate(zip(BETAS, KS)):
            bl, tot = out_b[i]
            R, se = r_se(bl, tot, K)
            red = val["families"][fam][i]["SE_block_mean"]
            ratio = se / red
            cells.append(dict(beta=b, K=K, R_full=R, SE_block_full=se, SE_block_reduced_mean=red, ratio=ratio,
                              pass_=bool(abs(ratio - 1) <= 0.20)))
            ok &= abs(ratio - 1) <= 0.20
            print(fam, b, f"R {R:.4f} SE_full {se:.3e} SE_reduced {red:.3e} ratio {ratio:.3f}", flush=True)
        res["families"][fam] = cells
        del h
    res["COMPARISON_PASS"] = bool(ok)
    res["wall_s"] = time.time() - t0
    json.dump(res, open(out, "w"), indent=1)
    print("COMPARISON_PASS", ok)
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "selftest":
        sys.exit(selftest())
    if sys.argv[1] == "validate":
        sys.exit(validate(sys.argv[2], *(int(x) for x in sys.argv[3:4])))
    if sys.argv[1] == "full":
        sys.exit(full(sys.argv[2], sys.argv[3]))
