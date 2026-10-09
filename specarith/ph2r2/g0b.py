"""R₂ pre-read G0b/G0c (PH2R2_SEAL 1.0 §4): the μ estimator on full-size surrogates at each fresh bin's density.

Surrogate: consecutive CUE_250 eigenphase blocks (Haar, Mezzadri), each unfolded to unit density exactly
(x = 250·θ/2π) and mapped onto ζ's smooth count by t = N̄⁻¹(x₀ + offset + x), tiling the bin's height range; each block
is its own "file" (pairs counted only within a block, as R4 counts pairs only within a Platt file). Truth: the sine
kernel (CUE_250 O(N⁻²) correction ≈ 1.6·10⁻⁵ of RMT_f, negligible), so the known answer is μ* = 0 for every test function, and
the ~3·10⁴ block edges per surrogate test the within-file edge correction far harder than the data's two edges.

Per surrogate and family member: S_f (within-block pairs), the prediction RMT_f, LOT_f for the same tiling, μ̂ =
(S_f − RMT_f)/LOT_f, and moving-block bootstrap SDs of μ̂ over the per-level pair contributions, blocks of
BOOT_LEVELS levels (declared sweep), the widest used.

  python g0b.py kernel BIN OUT             cache the bin's CS07 kernel on its r grid (mpmath ζ; ~2 min)
  python g0b.py run BIN REP0 REP1 OUT      surrogates REP0 … REP1−1 -> OUT/g0b_BIN_r<REP0>.json
  python g0b.py merge OUT                  per-bin bias, SD, bootstrap/surrogate SD ratios, coverage; primary-f choice
"""
import glob
import json
import math
import os
import sys

import numpy as np

import r2lib as R
import r2prep as P

BLOCK = 250               # CUE_250: O(N⁻²) pair-density correction ≈ 1.6e-5 of RMT_f (μ* shift ~1e-3); 8× cheaper eig per block
BOOT_LEVELS = (100, 1000, 10000)      # declared bootstrap sweep (levels per moving block), widest used (R5)
BOOT_B = 400
SEED0 = 20261009


class CachedKernel(R.Kernel):
    def __init__(self, path):                                           # noqa: super().__init__ deliberately skipped
        z = np.load(path)
        self.r, self.d1, self.zz, self.A, self.B = z["r"], z["d1"], z["zz"], z["A"], z["B"]


def kernel_path(out, name):
    return os.path.join(out, f"kernel_{name}.npz")


def make_kernel(name, out):
    g = P.geometry(name)
    x, wr = np.polynomial.legendre.leggauss(801)
    rmax = P.U_MAX * g["delta"]
    r = 0.5 * rmax * (x + 1)
    K = R.Kernel(r)
    os.makedirs(out, exist_ok=True)
    np.savez(kernel_path(out, name), r=r, wr=0.5 * rmax * wr, d1=K.d1, zz=K.zz, A=K.A, B=K.B)


def nbar_inv(x, t_guess):
    t = np.full(np.shape(x), float(t_guess))
    for _ in range(60):
        t = t - (P.nbar(t) - x) / (np.log(t / P.TWO_PI) / P.TWO_PI)
    return t


def cue_block(rng):
    Z = (rng.standard_normal((BLOCK, BLOCK)) + 1j * rng.standard_normal((BLOCK, BLOCK))) / math.sqrt(2)
    Q, Rm = np.linalg.qr(Z)
    Q = Q * (np.diagonal(Rm) / np.abs(np.diagonal(Rm)))[None, :]
    th = np.sort(np.mod(np.angle(np.linalg.eigvals(Q)), 2 * math.pi))
    return BLOCK * th / (2 * math.pi)


def predict_tiling(K, wr, edges, u, w, delta):
    """RMT_f, LOT_f for within-window pairs over windows [edges[k], edges[k+1]): bulk over the covered range (Gauss–
    Legendre in t per window), minus the loss ∫₀ f r R dr at both edges of every window."""
    f = P.f_raw(K.r, u, w, delta)
    fw = f * wr
    xt, wt = np.polynomial.legendre.leggauss(6)
    rmt = lot = 0.0
    for a, b in zip(edges[:-1], edges[1:]):
        tt = 0.5 * (b - a) * (xt + 1) + a
        ww = 0.5 * (b - a) * wt
        for t_, w_ in zip(tt, ww):
            Rm = K.RMT(t_)
            Lo = K.R(t_) - Rm
            rmt += 2 * w_ * np.sum(Rm * fw)
            lot += 2 * w_ * np.sum(Lo * fw)
        for te in (a, b):
            Rm = K.RMT(te)
            Lo = K.R(te) - Rm
            rmt -= np.sum(Rm * fw * K.r)
            lot -= np.sum(Lo * fw * K.r)
    return rmt, lot


def contributions(t, u, w, delta):
    """Per-level ordered-pair contribution c_i = Σ_{j≠i, |t_j − t_i| ≤ U_MAX δ} f(t_j − t_i) within one window."""
    rmax = P.U_MAX * delta
    c = np.zeros(len(t))
    k = 1
    while k < len(t):
        d = t[k:] - t[:-k]
        m = d <= rmax
        if not m.any():
            break
        v = np.where(m, P.f_raw(d, u, w, delta), 0.0)
        c[:-k] += v
        c[k:] += v
        k += 1
    return c


def boot_sd_sum(c, block, rng, B=BOOT_B):
    n = len(c)
    nb = int(math.ceil(n / block))
    cs = np.concatenate([[0.0], np.cumsum(c)])
    starts = rng.integers(0, n - block + 1, (B, nb))
    sums = (cs[starts + block] - cs[starts]).sum(axis=1) * (n / (nb * block))
    return float(np.std(sums, ddof=1))


def run(name, rep0, rep1, out):
    g = P.geometry(name)
    K = CachedKernel(kernel_path(out, name))
    wr = np.load(kernel_path(out, name))["wr"]
    x0 = float(P.nbar(g["t0"]))
    x_end = float(P.nbar(g["t1"]))
    nblocks = int((x_end - x0) // BLOCK)
    nblocks = min(nblocks, int(os.environ.get("G0B_MAXBLOCKS", nblocks)))      # smoke tests only
    res = []
    for rep in range(rep0, rep1):
        rng = np.random.default_rng(SEED0 * 100_000 + int(name[1:]) * 1000 + rep)   # reproducible (no hash())
        windows, edges = [], [g["t0"]]
        cs = {fm: [] for fm in P.FAMILY}
        for b in range(nblocks):
            xb = x0 + b * BLOCK
            t = nbar_inv(xb + cue_block(rng), g["tc"])
            edges.append(float(nbar_inv(np.array([xb + BLOCK]), g["tc"])[0]))
            for fm in P.FAMILY:
                cs[fm].append(contributions(t, *fm, g["delta"]))
        rec = dict(rep=rep, nblocks=nblocks)
        for fm in P.FAMILY:
            c = np.concatenate(cs[fm])
            S = float(c.sum())                 # Σ_i Σ_{j≠i} f = the ordered-pair sum (each unordered pair counted twice)
            rmt, lot = predict_tiling(K, wr, edges, *fm, g["delta"])
            mu = (S - rmt) / lot
            bsd = {str(bl): boot_sd_sum(c, bl, rng) / abs(lot) for bl in BOOT_LEVELS}
            rec[f"{fm[0]}_{fm[1]}"] = dict(S=S, RMT=rmt, LOT=lot, mu=mu, boot_sd_mu=bsd)
        res.append(rec)
        print(name, rep, {k: round(v["mu"], 4) for k, v in rec.items() if isinstance(v, dict)}, flush=True)
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, f"g0b_{name}_r{rep0:03d}.json"), "w"), indent=1)


def merge(out):
    summary = {}
    for name in P.BINS:
        recs = [r for f in sorted(glob.glob(os.path.join(out, f"g0b_{name}_r*.json"))) for r in json.load(open(f))]
        if not recs:
            continue
        s = dict(n_rep=len(recs))
        for fm in P.FAMILY:
            k = f"{fm[0]}_{fm[1]}"
            mu = np.array([r[k]["mu"] for r in recs])
            sd = float(mu.std(ddof=1))
            bsd = {bl: np.array([r[k]["boot_sd_mu"][str(bl)] for r in recs]) for bl in BOOT_LEVELS}
            widest = np.max(np.stack([bsd[bl] for bl in BOOT_LEVELS]), axis=0)
            cover_boot = float(np.mean(np.abs(mu) <= 1.959964 * widest))
            cover_wider = float(np.mean(np.abs(mu) <= 1.959964 * np.maximum(widest, sd)))
            s[k] = dict(mean_mu=float(mu.mean()), sd_mu=sd, bias_in_sd=float(mu.mean() / sd),
                        boot_sd_over_sd={str(bl): float(bsd[bl].mean() / sd) for bl in BOOT_LEVELS},
                        cover_boot_widest=cover_boot, cover_wider=cover_wider,
                        power_reject_mu0=float(0.5 * math.erfc((1 / max(sd, float(widest.mean())) - 1.959964) / math.sqrt(2))))
        summary[name] = s
    # primary f (R3): maximise the median over bins of 1/SD(μ̂) (= |LOT_f| / SD(S_f)), theory + surrogates only
    score = {}
    for fm in P.FAMILY:
        k = f"{fm[0]}_{fm[1]}"
        vals = [1 / max(summary[n][k]["sd_mu"], np.mean([v for v in summary[n][k]["boot_sd_over_sd"].values()])
                        * summary[n][k]["sd_mu"]) for n in summary]
        score[k] = float(np.median(vals))
    summary["primary_choice"] = dict(score_median_inverse_sd=score, primary=max(score, key=score.get))
    json.dump(summary, open(os.path.join(out, "g0b_summary.json"), "w"), indent=1)
    print(json.dumps(summary["primary_choice"], indent=1))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "kernel":
        make_kernel(sys.argv[2], sys.argv[3])
    elif cmd == "run":
        run(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    elif cmd == "merge":
        merge(sys.argv[2])
