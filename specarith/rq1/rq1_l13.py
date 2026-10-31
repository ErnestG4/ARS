"""L13 (OPEN_LEADS; Will, 2026-10-31): does RQ1's sealed SE model overstate the noise on the arithmetic angle sets?
Descriptive; the already-read 10¹⁰ / 10¹¹ data only, sliced from the pinned 10¹² ℤ[√2] and ℤ[i] archives as in REPRO;
no seal.

Cells: X ∈ {10¹⁰, 10¹¹} × β ∈ {0.40, 0.45} (B2) and {0.55, 0.60} (crossover) × field ∈ {ℤ[√2], ℤ[i]}. Matched N = 2n
and K = round(N^β), as in the sealed read.

Model: SE_model = R·√(2/(cK)), c = C_SE = 0.6272 (rq1_read.se_diff, per field).

Method A (block arcs, the round-97 estimator of rq1c_blockse).
  - The variance integral is split over M equal arcs; mirror pairs are the blocks; SE_A = √(M/2·var(P_b))/(N/K).
  - M = 1000 (the validated setting) where its block/window ratio K·10⁻³ is ≥ 10, else M = 250 (block/window
    K·4·10⁻³ ≥ 10 at every cell here).
  - Declared now: M = 250 at 10¹⁰ β 0.40 (2.9 → 11.6), 10¹⁰ β 0.45 (7.9 → 31) and 10¹¹ β 0.40 (7.0 → 28).
  - Both M are reported at every cell.
  - 90% interval of model/SE_A: ratio·(1 ± 1.645/√(2(B − 1))), B = M/2 blocks.

Method B (residue-class subsets).
  - For m ∈ {5, 7, 13}, the split primes p ≢ 0 (mod m) fall into q = 4, 6 and 12 classes of p mod m.
  - Each class is cut to its first n_min rows, n_min being the smallest class, so N_sub = 2·n_min is matched across the
    classes.
  - R_j is computed at K_sub = round(N_sub^β); relSD_m = SD(R_j, ddof 1)/mean(R_j).
  - Scaled to the full N by the model's own 1/√K law: relSD_full,m = relSD_m·√(K_sub/K).
  - Pooled over m with weights q_m − 1 (19 degrees of freedom).
  - Ratio_B = √(2/(cK))/relSD_full,pooled, with a 90% interval from χ²₁₉.
  - Per-m ratios are reported; their agreement checks the scaling.

Reading (declared before running).
  - For each method and cell: "below" (empirical noise below the model) if the 90% interval of model/empirical lies
    above 1; "above" if it lies below 1; else "consistent".
  - The two methods agree at a cell iff their 90% intervals overlap.
  - Will's reading:
    - both methods below at a cell: RQ1's PASS is conservative there, by the factor model/empirical;
    - above: P1's T is recomputed with the empirical SE (descriptive);
    - the methods disagree: report it and draw no conclusion.
  - Always reported (descriptive):
    - the B2 T at 10¹⁰ / 10¹¹, recomputed with each method's SE;
    - P1's T at 10¹², with each method's 10¹¹ model/empirical ratio carried to 10¹² (an extrapolation, so labelled).

Guard: the exact R from rq1_read.var_stream must equal the sealed read's R (results/read/read1.json) at every cell, bit
for bit, else stop (the data or the code differ).

Cost model (spot core-s; the rq1c_read constants): per field and X, load 1.0·m_load(N); full set 12 passes (4 exact,
8 block); subsets 3 × (0.5·m_load(N) sorts + 4 passes). Total ≈ 2.6 core-h; stop above 1.25× after any stage. Timings go
to a sidecar; L13.json has none.

Calibration (§9.G; synthetic, before the run): mirror-symmetrised i.i.d. (Poisson) sets of n = 10⁶ half-points, 60
replicates (seeds [9900, rep]), K = 2,000 and 20,000. Per K: the replicate relSD of R (the truth), the model's relSD,
the mean method-A relSE (M = 1000 and 250), and method B's relSD from 12 random-label classes (m = 13 analogue,
pooled over replicates). Reported only; it shows whether each method recovers the truth on a set whose truth is known.

  python rq1_l13.py selftest
  python rq1_l13.py calib OUT_JSON
  python rq1_l13.py run ZS2_DIR ZI_DIR OUT_JSON
"""
import hashlib
import json
import math
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from numba import njit
from scipy.stats import chi2

import rq1_read as Q
import rq1_angles as RA

HERE = os.path.dirname(os.path.abspath(__file__))
BETAS = [0.40, 0.45, 0.55, 0.60]
B2 = [0.40, 0.45]
MS_SUB = [5, 7, 13]
MODS = 455                                       # 5·7·13
NT = int(os.environ.get("READ_THREADS", "16"))
LIMIT = 1.25
N11 = 4118052228


def m_pass(N):
    return 1.6e-8 * N * 2.3


def m_load(N):
    return 204.0 * N / N11


@njit(cache=False, nogil=True)
def _add(blocks, a, b, v, M):
    i = int(a * M)
    while a < b and i < M:
        e = min(b, (i + 1) / M)
        blocks[i] += (e - a) * v
        a = e
        i += 1


@njit(cache=False, nogil=True)
def var_stream_blocks(th, K, M):
    """rq1c_blockse.var_stream_blocks with the arc count M as an argument."""
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
        _add(blocks, pos, nxt, dv * dv, M)
        pos = nxt
        cnt += d
    dv = cnt - mean
    _add(blocks, pos, 1.0, dv * dv, M)
    return blocks


def r_se(blocks, N, K):
    M = len(blocks)
    P = blocks[:M // 2] + blocks[::-1][:M // 2]
    nk = N / K
    return float(P.sum() / nk), float(math.sqrt((M // 2) * P.var(ddof=1)) / nk)


def model_rel(K):
    return math.sqrt(2 / (Q.C_SE * K))


def m_primary(K):
    return 1000 if K * 1e-3 >= 10 else 250


def load_half(d, field, n):
    """θ ∈ [0, ½] per row (first n rows, segment sha256 checked as rq1_read.load_field) and p mod 455 (int16)."""
    man = json.load(open(os.path.join(d, "MANIFEST.json")))
    th = np.empty(n, np.float64)
    md = np.empty(n, np.int16)
    got = 0
    for s in man["segments"]:
        if got >= n:
            break
        path = os.path.join(d, f"seg_{s['k']:04d}.npy")
        assert hashlib.sha256(open(path, "rb").read()).hexdigest() == s["sha256"], path
        ab = np.load(path)[: n - got]
        th[got:got + len(ab)] = Q.field_thetas(ab, field)
        if field == "zs2":
            p = RA.thetas_from_ab(ab)[1]
        else:
            u, v = ab[:, 0].astype(np.int64), ab[:, 1].astype(np.int64)
            p = u * u + v * v
        md[got:got + len(ab)] = (p % MODS).astype(np.int16)
        got += len(ab)
    assert got == n
    return th, md


def full_sorted(t):
    th = np.concatenate([t, np.mod(1.0 - t, 1.0)])
    th.sort()
    return th


class Cost:
    def __init__(self):
        self.model, self.rows = 0.0, []

    def add(self, stage, model_s, side):
        self.model += model_s
        cpu = time.process_time()
        self.rows.append(dict(stage=stage, cpu_s=cpu, model_s=self.model, ratio=cpu / self.model))
        json.dump(self.rows, open(side, "w"), indent=1)
        print(self.rows[-1], flush=True)
        if cpu > LIMIT * self.model:
            open(side + ".STOPPED", "w").write(f"cost {cpu / self.model:.2f}x the model at {stage}\n")
            sys.exit(3)


def one_field(d, field, n, X, pool, cost, side, sealed):
    N = 2 * n
    Ks = [int(round(N ** b)) for b in BETAS]
    t, md = load_half(d, field, n)
    th = full_sorted(t)
    cost.add(f"{X:.0e} {field} load", m_load(N), side)
    ex = list(pool.map(lambda K: Q.var_stream(th, K) / (N / K), Ks))
    key = "R_zs2" if field == "zs2" else "R_zi"
    for b, K, r in zip(BETAS, Ks, ex):
        s = sealed[b]
        assert s["K"] == K and s[key] == r, ("sealed R differs", X, field, b)
    tasks = [(K, M) for K in Ks for M in (1000, 250)]
    bl = list(pool.map(lambda km: var_stream_blocks(th, float(km[0]), km[1]), tasks))
    blk = {km: r_se(b, N, km[0]) for km, b in zip(tasks, bl)}
    del th
    cost.add(f"{X:.0e} {field} full", 12 * m_pass(N), side)
    cells = {}
    for b, K, r in zip(BETAS, Ks, ex):
        mr = model_rel(K)
        c = dict(beta=b, K=K, R=r, R_equals_sealed=True, SE_model=r * mr, block={})
        for M in (1000, 250):
            Rb, se = blk[(K, M)]
            B = M // 2
            ratio = r * mr / se
            hw = 1.645 / math.sqrt(2 * (B - 1))
            c["block"][str(M)] = dict(block_over_window=K * 0.5 / B, R_blocks=Rb, SE=se, ratio_model_over_emp=ratio,
                                      ci90=[ratio * (1 - hw), ratio * (1 + hw)])
        c["block_primary_M"] = m_primary(K)
        c["subsets"] = {}
        cells[b] = c
    for m in MS_SUB:
        lab = md % m
        cnt = np.bincount(lab, minlength=m)
        cls = [r for r in range(1, m) if math.gcd(r, m) == 1]
        nmin = int(min(cnt[r] for r in cls))
        Nsub = 2 * nmin
        Ksub = [int(round(Nsub ** b)) for b in BETAS]
        Rj = []
        for r in cls:
            idx = np.flatnonzero(lab == r)[:nmin]
            ths = full_sorted(t[idx])
            del idx
            Rj.append(list(pool.map(lambda K: Q.var_stream(ths, K) / (Nsub / K), Ksub)))
            del ths
        Rj = np.array(Rj)                                       # class × β
        for i, (b, K) in enumerate(zip(BETAS, Ks)):
            col = Rj[:, i]
            rel = float(col.std(ddof=1) / col.mean())
            relf = rel * math.sqrt(Ksub[i] / K)
            cells[b]["subsets"][str(m)] = dict(q=len(cls), n_min=nmin, class_counts=[int(cnt[r]) for r in cls],
                                               K_sub=Ksub[i], R_j=col.tolist(), relSD_sub=rel, relSD_full=relf,
                                               ratio_model_over_emp=model_rel(K) / relf)
        del lab
        cost.add(f"{X:.0e} {field} subsets m={m}", 0.5 * m_load(N) + 4 * m_pass(N), side)
    for b, K in zip(BETAS, Ks):
        c = cells[b]
        sub = c["subsets"]
        dof = sum(sub[str(m)]["q"] - 1 for m in MS_SUB)
        var = sum((sub[str(m)]["q"] - 1) * sub[str(m)]["relSD_full"] ** 2 for m in MS_SUB) / dof
        ratio = model_rel(K) / math.sqrt(var)
        lo = ratio * math.sqrt(chi2.ppf(0.05, dof) / dof)
        hi = ratio * math.sqrt(chi2.ppf(0.95, dof) / dof)
        c["subset_pooled"] = dict(dof=dof, relSD_full=math.sqrt(var), SE=c["R"] * math.sqrt(var),
                                  ratio_model_over_emp=ratio, ci90=[lo, hi])
    del t, md
    return cells


def cls_(ci):
    return "below" if ci[0] > 1 else "above" if ci[1] < 1 else "consistent"


def run(zs2, zi, out):
    side = out + ".cost"
    read1 = json.load(open(os.path.join(HERE, "results/read/read1.json")))
    p1 = json.load(open(os.path.join(HERE, "results/rq1c_read_ruling/read1.stripped.json")))["P1"]
    cost = Cost()
    res = dict(label="L13: RQ1 SE model against empirical SEs (descriptive; already-read 1e10/1e11 data)",
               C_SE=Q.C_SE, betas=BETAS, B2_cells=B2, m_subsets=MS_SUB, X={})
    with ThreadPoolExecutor(NT) as pool:
        for X in Q.XS:
            n = Q.n_below(zs2, X)
            sealed = {r["beta"]: r for r in read1["rows"][str(X)]["rows"]}
            F = {f: one_field(zs2 if f == "zs2" else zi, f, n, X, pool, cost, side, sealed) for f in ("zs2", "zi")}
            rows = {}
            for b in BETAS:
                a, c = F["zs2"][b], F["zi"][b]
                Mp = a["block_primary_M"]
                seA = math.hypot(a["block"][str(Mp)]["SE"], c["block"][str(Mp)]["SE"])
                seB = math.hypot(a["subset_pooled"]["SE"], c["subset_pooled"]["SE"])
                seM = Q.se_diff(a["R"], c["R"], a["K"])
                per = {}
                for f, cc in (("zs2", a), ("zi", c)):
                    ciA = cc["block"][str(Mp)]["ci90"]
                    ciB = cc["subset_pooled"]["ci90"]
                    per[f] = dict(A=cls_(ciA), B=cls_(ciB), agree=bool(ciA[0] <= ciB[1] and ciB[0] <= ciA[1]))
                rows[str(b)] = dict(D=a["R"] - c["R"], SE_diff_model=seM, SE_diff_A=seA, SE_diff_B=seB,
                                    ratio_diff_A=seM / seA, ratio_diff_B=seM / seB, classification=per)
            res["X"][str(X)] = dict(n=n, N=2 * n, fields=F, diff=rows)
    # T with empirical SEs (descriptive)
    rule_t = read1["rule"]["t"]
    T = {}
    for lab in ("model", "A", "B"):
        T[lab] = sum(res["X"][str(X)]["diff"][str(b)]["D"] / res["X"][str(X)]["diff"][str(b)][
            "SE_diff_model" if lab == "model" else f"SE_diff_{lab}"] for X in Q.XS for b in B2)
    res["B2_T_1e10_1e11"] = dict(t=rule_t, T_model=T["model"], T_A=T["A"], T_B=T["B"], T_sealed=read1["B2_T"])
    p1T = {}
    for lab in ("A", "B"):
        p1T[lab] = sum(p1["cells"][str(b)]["D"] / p1["cells"][str(b)]["SE_diff"]
                       * res["X"][str(10 ** 11)]["diff"][str(b)][f"ratio_diff_{lab}"] for b in B2)
    res["P1_T_1e12_extrapolated"] = dict(t=p1["t"], T_sealed=p1["T"], T_A=p1T["A"], T_B=p1T["B"],
                                         note="the 1e11 model/empirical ratio of SE_diff carried to 1e12 (extrapolation)")
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    for X in Q.XS:
        for b in BETAS:
            for f in ("zs2", "zi"):
                c = res["X"][str(X)]["fields"][f][b]
                Mp = c["block_primary_M"]
                print(f"{X:.0e} β {b} {f}: R {c['R']:.5f} model/A(M={Mp}) {c['block'][str(Mp)]['ratio_model_over_emp']:.2f} "
                      f"model/B {c['subset_pooled']['ratio_model_over_emp']:.2f} "
                      f"[{c['subset_pooled']['ci90'][0]:.2f}, {c['subset_pooled']['ci90'][1]:.2f}] per m "
                      + " ".join(f"{c['subsets'][str(m)]['ratio_model_over_emp']:.2f}" for m in MS_SUB), flush=True)
    print(json.dumps(res["B2_T_1e10_1e11"]), json.dumps(res["P1_T_1e12_extrapolated"]))
    return 0


def selftest():
    import rq1c_blockse as BS
    rng = np.random.default_rng(1)
    th = BS.gen_mix(300_000, rng)
    for K in (100.0, 3000.0):
        a = var_stream_blocks(th, K, 1000)
        b = BS.var_stream_blocks(th, K)
        v = Q.var_stream(th, K)
        print("K", K, "M=1000 identical to rq1c_blockse:", bool(np.array_equal(a, b)),
              "| M=250 sum vs var_stream rel", abs(var_stream_blocks(th, K, 250).sum() - v) / v)
    # subsets plumbing on i.i.d. points with fake labels: model/B should be ≈ 1 for Poisson (c is Poisson's)
    n = 2_000_000
    t = rng.random(n) * 0.5                      # archive order (by p), not sorted by θ
    lab = rng.integers(0, 4, n)
    Rj = []
    for r in range(4):
        tt = t[lab == r][: int(np.bincount(lab).min())]
        ths = full_sorted(tt)
        Rj.append(Q.var_stream(ths, 2000.0) / (len(ths) / 2000.0))
    print("iid subsets: R_j", np.round(Rj, 4), "relSD", np.std(Rj, ddof=1) / np.mean(Rj), "model", model_rel(2000),
          "(4 classes: the ratio scatters about 1 with ~40% spread)")
    return 0


def calib(out):
    n, reps, Ks = 10 ** 6, 60, [2000.0, 20000.0]
    rows = {K: dict(R=[], A1000=[], A250=[], Bvar=[]) for K in Ks}
    for rep in range(reps):
        rng = np.random.default_rng([9900, rep])
        t = rng.random(n) * 0.5
        th = full_sorted(t)
        for K in Ks:
            N = len(th)
            R = Q.var_stream(th, K) / (N / K)
            rows[K]["R"].append(R)
            for M in (1000, 250):
                rows[K][f"A{M}"].append(r_se(var_stream_blocks(th, K, M), N, K)[1] / R)
        lab = rng.integers(0, 12, n)
        nmin = int(np.bincount(lab, minlength=12).min())
        for K in Ks:
            Ksub = round((2 * nmin) ** (math.log(K) / math.log(2 * n)))
            Rj = [Q.var_stream(full_sorted(t[lab == r][:nmin]), float(Ksub)) / (2 * nmin / Ksub) for r in range(12)]
            rows[K]["Bvar"].append((np.std(Rj, ddof=1) / np.mean(Rj)) ** 2 * Ksub / K)
    res = {}
    for K in Ks:
        r = rows[K]
        truth = float(np.std(r["R"], ddof=1) / np.mean(r["R"]))
        res[str(int(K))] = dict(truth_relSD=truth, model_relSD=model_rel(K),
                                A1000_relSE=float(np.mean(r["A1000"])), A250_relSE=float(np.mean(r["A250"])),
                                B_relSD=float(math.sqrt(np.mean(r["Bvar"]))),
                                model_over_truth=model_rel(K) / truth,
                                A1000_over_truth=float(np.mean(r["A1000"])) / truth,
                                A250_over_truth=float(np.mean(r["A250"])) / truth,
                                B_over_truth=float(math.sqrt(np.mean(r["Bvar"]))) / truth)
        print(K, {k: round(v, 3) for k, v in res[str(int(K))].items()})
    json.dump(dict(label="L13 calibration on Poisson (synthetic)", n=n, reps=reps, rows=res), open(out, "w"), indent=1)
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "selftest":
        sys.exit(selftest())
    if sys.argv[1] == "calib":
        sys.exit(calib(sys.argv[2]))
    sys.exit(run(*sys.argv[2:5]))
