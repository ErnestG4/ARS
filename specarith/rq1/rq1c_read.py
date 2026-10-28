"""RQ1-c read (RQ1C_SEAL.md §2), its reproduction checks, and the ℤ[ω] pipeline check against Phase 34d (Will,
2026-10-27). Criteria are declared here and committed before any mode runs.

Archives: the 10¹² archives only (spot /mnt/data/rq1/archive_1e12_{zs2,zi,zw}). Their segments below 10¹¹ (ℤ[√2]) and
1.01·10¹¹ (ℤ[i]) are hash-identical to the sealed read's archives (all 1,000 and 1,010), so 10¹⁰ / 10¹¹ use the same
bytes as the sealed read. Every loaded segment's sha256 is checked against its manifest (a mismatch raises: VOID).
Matched N at each X: n = # ℤ[√2] split primes ≤ X; each other field contributes its first n split primes; N = 2n.

Estimators.
  exact:  rq1_read.var_stream on the sorted full set (rq1_read.load_field; ℤ[ω] via load_zw, same construction).
  binned: rq1c_binned.var_binned on the half-set histogram of width δ = 2^−B, built segment by segment (hist_stream:
          per prime the half value min(θ, 1 − θ), with a second copy where θ = 1 − θ, i.e. exactly rq1c_binned.half_set's
          multiset, so the histogram equals hist_half(half_set(...))). 10¹² uses B = 36 (seal §3).
  SE: the sealed model (rq1_read.se_diff, c = 0.627); P3 residual SE as rq1_collapse (each term at its own K).

MODE zw34d OUT_JSON  (ℤ[ω] pipeline against Phase 34d, on the seen range X ≤ 10⁸; runs before anything else in the
  ℤ[ω] archive is read). 34d set: phase34d/eisenstein_primes.eisenstein_prime_angles(10⁸, include_ramified=False,
  both_factors=True) (radians, [0, π/3)). New set: rq1_zw.gen_segment_zw(0, 10⁸) regenerated, θ = thetas_zw and the
  mirror 1 − θ, × π/3, sorted. Reported: counts, max |Δθ| (radians and in units of the sector), and, if ARCHIVE_DIR is
  given, whether the regenerated segment's .npy bytes hash to the archive's seg_0000.npy. CRITERIA: equal counts and
  max |Δθ| ≤ 1e−12 of the sector (float rounding only); the archive hash, if given, equal.

MODE repro ZS2_DIR ZI_DIR OUT_JSON  (post hoc on the sealed read's data, X = 10¹⁰ and 10¹¹). CRITERIA:
  (a) exact path, the sealed RQ1 cells (β 0.20 … 0.90): R_zs2, R_zi, D and SE_diff equal results/read/read1.json
      bit-for-bit (==), and B2_T equal.
  (b) exact path, the P3 grid (β 0.45 … 0.65): R_zs2(K) and R_zi(aK) equal results/collapse/COLLAPSE.json bit-for-bit;
      the P3 location (rq1c_witness.p3_locate, the witness's rule) rounds to 0.525 (10¹⁰) and 0.529 (10¹¹).
  (c) binned path, at the B2 cells (β 0.40, 0.45) and the P3 grid, B per cell as rq1c_binned.validate (the coarsest B with
      N·δ²·K at least the 10¹² value at 2⁻³⁶, so the stress is the read's): |R_binned − R_exact| ≤ N·δ²·K (the
      validated bound) at every cell; the binned P3 location also rounds to 0.525 / 0.529.
  (d) hist_stream equals hist_half(half_set) bit-for-bit at 10¹⁰ (both fields, the finest B used there).
  PASS iff (a)–(d) all hold.

MODE read ZS2_DIR ZI_DIR ZW_DIR SELECTION_JSON CONFIRM_JSON OUT_JSON  (the sealed read; only after the seal is stamped,
  Bitcoin-attested and verified on two explorers, and `sha256sum -c` passes on spot).
  10¹² (binned, B = 36): ℤ[√2] at K for β ∈ {0.40, 0.45, 0.55, 0.60} ∪ the P3 grid; ℤ[i] at K for {0.40, 0.45, 0.55,
  0.60} and at a·K on the P3 grid; ℤ[ω] at K for {0.40, 0.45, 0.55}.
  10¹⁰, 10¹¹ (exact): ℤ[ω] at K for {0.40, 0.45, 0.55}; ℤ[√2] and ℤ[i] recomputed at the same cells and asserted equal to
  read1.json (the repro mode proved the path).
  P1: the round-90 T rule and guard (rq1_read.b2_T, b2_guard) at (10¹², 0.40), (10¹², 0.45) with the frozen t and scales
      from SELECTION_JSON (rq1c_witness p1sel summary), which CONFIRM_JSON (p1conf, fresh seeds) must confirm at the
      same t (else P1 UNPOWERED). PASS iff T > t and the guard holds; FAIL otherwise.
  P2: D(10¹²) at β 0.40, 0.45, 0.55, 0.60 against each law's consistency window (results/RQ1C_P2.json). Descriptive.
  P3: residual R_zs2(K) − R_zi(aK) on the grid; location by p3_locate; resolution = mean SE of the bracketing points /
      slope. PASS iff the location lies in [0.51, 0.54]; FAIL if outside or no crossing.
  P4: R_zs2 > R_zw > R_zi at β 0.55 at 10¹⁰, 10¹¹ and 10¹². PASS iff both inequalities hold at all three; FAIL
      otherwise. Descriptive: the ordering at β 0.40 and 0.45, and D_ωi / D_√2i at β 0.55 against 0.283.
  Cost: after each stage the cumulative CPU is compared with the cumulative model; above 1.25× the run writes STOPPED
  and exits 3. Passes run in a thread pool (nogil kernels); each pass is single-threaded and deterministic, and the
  output is written with sorted keys, so the double read compares byte-identical.

  python rq1c_read.py zw34d OUT_JSON [ARCHIVE_DIR]
  python rq1c_read.py repro ZS2_DIR ZI_DIR OUT_JSON
  python rq1c_read.py read ZS2_DIR ZI_DIR ZW_DIR SELECTION_JSON CONFIRM_JSON OUT_JSON
"""
import hashlib
import io
import json
import math
import os
import platform
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np

import rq1_read as Q
import rq1c_binned as BN
import rq1c_witness as W
import rq1_zw as Z

HERE = os.path.dirname(os.path.abspath(__file__))
A = BN.A
B12 = 36
P3_GRID = W.P3_GRID
P2_BETAS = [0.40, 0.45, 0.55, 0.60]
P4_BETAS = [0.40, 0.45, 0.55]
P1_BETAS = [0.40, 0.45]
NT = int(os.environ.get("READ_THREADS", "16"))
LIMIT = 1.25
# cost model (spot core-s): exact pass 1.6e-8·N·2.3 (rq1_collapse); exact load 204 s × N/N₁₁; binned pass 14 ns per
# bin step × 2^(B+1) (rq1c_binned validation, ≈ 1,900 s at B = 36); histogram build 120 s × N/N₁₁ per field.
N11 = 4118052228


def m_exact_pass(N):
    return 1.6e-8 * N * 2.3


def m_load(N):
    return 204.0 * N / N11


def m_binned_pass(B):
    return 14e-9 * 2 ** (B + 1)


def m_hist(N):
    return 120.0 * N / N11


def K_of(N, b):
    return int(round(N ** b))


def se_rel(K):
    return math.sqrt(2 / (Q.C_SE * K))


def thetas(rows, field):
    return Z.thetas_zw(rows) if field == "zw" else Q.field_thetas(rows, field)


def load_zw(d, n):
    """rq1_read.load_field for the ℤ[ω] archive: θ ∈ [0, 1) per row and the mirror 1 − θ, sorted (hash-checked)."""
    man = json.load(open(os.path.join(d, "MANIFEST.json")))
    th = np.empty(2 * n, np.float64)
    got = 0
    for s in man["segments"]:
        if got >= n:
            break
        path = os.path.join(d, f"seg_{s['k']:04d}.npy")
        assert hashlib.sha256(open(path, "rb").read()).hexdigest() == s["sha256"], path
        uv = np.load(path)[: n - got]
        t1 = Z.thetas_zw(uv)
        th[got:got + len(uv)] = t1
        th[n + got:n + got + len(uv)] = np.mod(1.0 - t1, 1.0)
        got += len(uv)
    assert got == n
    th.sort()
    return th


def load(d, field, n):
    return load_zw(d, n) if field == "zw" else Q.load_field(d, field, n)


def hist_add(h, t_sorted, nb):
    """Add the sorted half values t_sorted into h (2^(B−1) bins of width 1/(2nb)), by run lengths."""
    top = np.iinfo(h.dtype).max
    if len(t_sorted) == 0:
        return
    idx = np.minimum((t_sorted * (2 * nb)).astype(np.int64), nb - 1)
    cut = np.flatnonzero(np.diff(idx)) + 1
    starts = np.concatenate([[0], cut])
    counts = np.diff(np.concatenate([starts, [len(idx)]]))
    u = idx[starts]
    new = h[u].astype(np.int64) + counts
    assert new.max() <= top
    h[u] = new


def hist_stream(d, field, n, B, dtype=np.uint8):
    """Half-set histogram (as rq1c_binned.hist_half(half_set(...))) of the first n rows, segment by segment."""
    man = json.load(open(os.path.join(d, "MANIFEST.json")))
    nb = 2 ** (B - 1)
    h = np.zeros(nb, dtype)
    got = 0
    for s in man["segments"]:
        if got >= n:
            break
        path = os.path.join(d, f"seg_{s['k']:04d}.npy")
        assert hashlib.sha256(open(path, "rb").read()).hexdigest() == s["sha256"], path
        rows = np.load(path)[: n - got]
        t = thetas(rows, field)
        m = np.mod(1.0 - t, 1.0)
        half = np.concatenate([t[t <= 0.5], m[m <= 0.5]])     # the multiset of half_set: every θ ≤ ½ of the full set
        half.sort()
        hist_add(h, half, nb)
        got += len(rows)
    assert got == n
    return h


def B_matched(N, K, beta, N12):
    """rq1c_binned.validate's rule: the coarsest B with N·δ²·K ≥ the 10¹² value at 2⁻³⁶ (same β), here with the actual
    10¹² matched N."""
    bias12 = N12 * 2.0 ** (-2 * B12) * N12 ** beta
    return math.floor(0.5 * math.log2(N * K / bias12))


class Cost:
    def __init__(self, out_dir, res):
        self.model, self.out_dir, self.res = 0.0, out_dir, res
        res.setdefault("cost", [])

    def add(self, stage, model_s):
        self.model += model_s
        cpu = time.process_time()
        self.res["cost"].append(dict(stage=stage, cpu_s=cpu, model_s=self.model, ratio=cpu / self.model))
        print(self.res["cost"][-1], flush=True)
        if cpu > LIMIT * self.model:
            open(os.path.join(self.out_dir, "STOPPED"), "w").write(f"cost {cpu / self.model:.2f}x the model at {stage}\n")
            sys.exit(3)


# ---------------- zw34d ----------------
def zw34d(out, archive=None):
    sys.path.insert(0, os.path.join(HERE, "..", "..", "phase34d"))
    import eisenstein_primes as E
    t0 = time.time()
    old = E.eisenstein_prime_angles(10 ** 8, include_ramified=False, both_factors=True)
    uv = Z.gen_segment_zw(0, 10 ** 8)
    t = Z.thetas_zw(uv)
    new = np.sort(np.concatenate([t, np.mod(1.0 - t, 1.0)])) * (math.pi / 3)
    res = dict(label="RQ1-c Z[omega] pipeline against Phase 34d at X <= 1e8 (seen range)", n_34d=int(len(old)),
               n_new=int(len(new)), n_split_primes=int(len(uv)))
    res["counts_equal"] = bool(len(old) == len(new))
    if res["counts_equal"]:
        d = np.abs(old - new)
        res["max_abs_dtheta_rad"] = float(d.max())
        res["max_abs_dtheta_sector_units"] = float(d.max() / (math.pi / 3))
        res["argmax"] = int(d.argmax())
    res["ok_dtheta"] = bool(res["counts_equal"] and res["max_abs_dtheta_sector_units"] <= 1e-12)
    if archive:
        buf = io.BytesIO()
        np.save(buf, uv)
        res["regen_sha256"] = hashlib.sha256(buf.getvalue()).hexdigest()
        res["archive_seg0_sha256"] = hashlib.sha256(open(os.path.join(archive, "seg_0000.npy"), "rb").read()).hexdigest()
        res["archive_hash_equal"] = res["regen_sha256"] == res["archive_seg0_sha256"]
    res["PASS"] = bool(res["ok_dtheta"] and res.get("archive_hash_equal", True))
    res["wall_s"] = time.time() - t0
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    print(json.dumps(res, sort_keys=True))
    return 0


# ---------------- repro ----------------
def repro(zs2, zi, out):
    out_dir = os.path.dirname(os.path.abspath(out))
    res = dict(label="RQ1-c read-code reproduction on the sealed read's data (post hoc)", kernel=platform.release(), X={})
    cost = Cost(out_dir, res)
    read1 = json.load(open(os.path.join(HERE, "results/read/read1.json")))
    col = json.load(open(os.path.join(HERE, "results/collapse/COLLAPSE.json")))["rows"]
    N12 = 2 * Q.n_below(zs2, 10 ** 12)
    ok_all = True
    with ThreadPoolExecutor(NT) as pool:
        for X in Q.XS:
            n = Q.n_below(zs2, X)
            N = 2 * n
            Kr = [K_of(N, b) for b in Q.BETAS]
            Kg = [K_of(N, b) for b in P3_GRID]
            ex = {}
            for f, Ks in (("zs2", sorted(set(Kr + Kg))), ("zi", Kr + [A * k for k in Kg])):
                th = load(zs2 if f == "zs2" else zi, f, n)
                vals = list(pool.map(lambda K: Q.var_stream(th, K) / (N / K), Ks))
                ex[f] = dict(zip(Ks, vals))
                del th
                cost.add(f"{X:.0e} exact {f}", m_load(N) + len(Ks) * m_exact_pass(N))
            # (a)
            rr = {r["beta"]: r for r in read1["rows"][str(X)]["rows"]}
            a_ok, rows_a = True, []
            for b, K in zip(Q.BETAS, Kr):
                r2, ri = ex["zs2"][K], ex["zi"][K]
                same = (r2 == rr[b]["R_zs2"] and ri == rr[b]["R_zi"] and r2 - ri == rr[b]["D"]
                        and Q.se_diff(r2, ri, K) == rr[b]["SE_diff"] and K == rr[b]["K"])
                a_ok &= same
                rows_a.append(dict(beta=b, K=K, R_zs2=r2, R_zi=ri, identical=bool(same)))
            # (b)
            cr = {r["beta"]: r for r in col[str(X)]["rows"]}
            b_ok = all(ex["zs2"][K] == cr[b]["R_zs2"] and ex["zi"][A * K] == cr[b]["R_zi_aK"] for b, K in zip(P3_GRID, Kg))
            resid = [ex["zs2"][K] - ex["zi"][A * K] for K in Kg]
            loc = W.p3_locate(resid)
            target = {10 ** 10: 0.525, 10 ** 11: 0.529}[X]
            b_ok &= loc is not None and round(loc, 3) == target
            # (c) binned at matched stress
            cells = [("zs2", b, K, K) for b, K in zip(P1_BETAS, [K_of(N, b) for b in P1_BETAS])]
            cells += [("zi", b, K, K) for b, K in zip(P1_BETAS, [K_of(N, b) for b in P1_BETAS])]
            cells += [("zs2", b, K, K) for b, K in zip(P3_GRID, Kg)] + [("zi", b, K, A * K) for b, K in zip(P3_GRID, Kg)]
            cells = [(f, b, K, KK, B_matched(N, K, b, N12)) for f, b, K, KK in cells]
            rows_c, binned = [], {}
            for f, d in (("zs2", zs2), ("zi", zi)):
                mine = [c for c in cells if c[0] == f]
                Bmax = max(c[4] for c in mine)
                h = hist_stream(d, f, n, Bmax)
                if X == 10 ** 10:                                            # (d)
                    ref = BN.hist_half(BN.half_set(d, f, n), Bmax, dtype=np.uint8)
                    res.setdefault("hist_stream_equals_hist_half", {})[f] = bool(np.array_equal(h, ref))
                    del ref
                hs = {B: BN.coarsen(h, Bmax - B) for B in set(c[4] for c in mine)}
                vals = list(pool.map(lambda c: BN.var_binned(hs[c[4]], float(c[3]))[0] / (N / c[3]), mine))
                for (ff, b, K, KK, B), v in zip(mine, vals):
                    e = ex[ff][KK]
                    bound = N * 2.0 ** (-2 * B) * KK
                    binned[(ff, KK)] = v
                    rows_c.append(dict(field=ff, beta=b, K=KK, B=B, R_binned=v, R_exact=e, diff=v - e, bound=bound,
                                       diff_over_bound=(v - e) / bound, diff_over_SE=(v - e) / (se_rel(KK) * e),
                                       within=bool(abs(v - e) <= bound)))
                del h, hs
                cost.add(f"{X:.0e} binned {f}", m_hist(N) + (m_hist(N) if X == 10 ** 10 else 0)
                         + sum(m_binned_pass(c[4]) for c in mine))
            resid_b = [binned[("zs2", K)] - binned[("zi", A * K)] for K in Kg]
            loc_b = W.p3_locate(resid_b)
            c_ok = all(r["within"] for r in rows_c) and loc_b is not None and round(loc_b, 3) == target
            res["X"][str(X)] = dict(n=n, N=N, a_read_cells_bit_identical=bool(a_ok), rows_a=rows_a,
                                    b_collapse_bit_identical_and_location=bool(b_ok), P3_location_exact=loc,
                                    P3_location_binned=loc_b, P3_target=target, c_binned_within_bound=bool(c_ok),
                                    rows_c=rows_c, max_diff_over_bound=max(abs(r["diff_over_bound"]) for r in rows_c),
                                    max_diff_over_SE=max(abs(r["diff_over_SE"]) for r in rows_c))
            ok_all &= a_ok and b_ok and c_ok
            print(X, "a", a_ok, "b", b_ok, loc, "c", c_ok, loc_b, flush=True)
    d_ok = all(res.get("hist_stream_equals_hist_half", {}).values()) and len(res.get("hist_stream_equals_hist_half", {})) == 2
    res["PASS"] = bool(ok_all and d_ok)
    res["cpu_core_h"] = time.process_time() / 3600
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    print("PASS", res["PASS"], "hist", res.get("hist_stream_equals_hist_half"))
    return 0


# ---------------- read ----------------
def load_rule_c(sel_path, conf_path):
    sel, conf = json.load(open(sel_path)), json.load(open(conf_path))
    if not (sel["OK"] and conf["OK"] and conf["t"] == sel["t"] and conf["scale"] == sel["scale"]):
        return None
    return dict(t=float(sel["t"]), scale={float(k): float(v) for k, v in sel["scale"].items()})


def read(zs2, zi, zw, sel, conf, out):
    for d in (zs2, zi, zw):
        if os.path.abspath(d).startswith("/mnt/data"):
            assert os.path.ismount("/mnt/data"), "/mnt/data is not mounted"
    out_dir = os.path.dirname(os.path.abspath(out))
    res = dict(label="RQ1-c read (sealed)", kernel=platform.release(), B=B12,
               selection_sha256=hashlib.sha256(open(sel, "rb").read()).hexdigest(),
               confirm_sha256=hashlib.sha256(open(conf, "rb").read()).hexdigest())
    cost = Cost(out_dir, res)
    rule = load_rule_c(sel, conf)
    res["rule"] = rule
    read1 = json.load(open(os.path.join(HERE, "results/read/read1.json")))
    p2 = json.load(open(os.path.join(HERE, "results/RQ1C_P2.json")))["cells"]
    R = {}                                   # R[(X, field, K)]
    with ThreadPoolExecutor(NT) as pool:
        # 10¹⁰, 10¹¹ exact
        for X in Q.XS:
            n = Q.n_below(zs2, X)
            N = 2 * n
            Ks = [K_of(N, b) for b in P4_BETAS]
            for f, d in (("zs2", zs2), ("zi", zi), ("zw", zw)):
                th = load(d, f, n)
                for K, v in zip(Ks, pool.map(lambda K: Q.var_stream(th, K) / (N / K), Ks)):
                    R[(X, f, K)] = v
                del th
                cost.add(f"{X:.0e} exact {f}", m_load(N) + len(Ks) * m_exact_pass(N))
            rr = {r["beta"]: r for r in read1["rows"][str(X)]["rows"]}
            for b, K in zip(P4_BETAS, Ks):
                assert R[(X, "zs2", K)] == rr[b]["R_zs2"] and R[(X, "zi", K)] == rr[b]["R_zi"], (X, b)
        # 10¹² binned
        X = 10 ** 12
        n = Q.n_below(zs2, X)
        N = 2 * n
        K = {b: K_of(N, b) for b in sorted(set(P2_BETAS + P3_GRID + P4_BETAS))}
        want = {"zs2": sorted(set(K[b] for b in P2_BETAS + P3_GRID)),
                "zi": [K[b] for b in P2_BETAS] + [A * K[b] for b in P3_GRID],
                "zw": [K[b] for b in P4_BETAS]}
        for f, d in (("zs2", zs2), ("zi", zi), ("zw", zw)):
            h = hist_stream(d, f, n, B12)
            for KK, v in zip(want[f], pool.map(lambda KK: BN.var_binned(h, float(KK))[0] / (N / KK), want[f])):
                R[(X, f, KK)] = v
            del h
            cost.add(f"1e12 binned {f}", m_hist(N) + len(want[f]) * m_binned_pass(B12))
    res["n_1e12"], res["N_1e12"], res["K_1e12"] = n, N, {str(b): k for b, k in K.items()}
    res["R"] = {f"{X:.0e} {f} {KK}": v for (X, f, KK), v in sorted(R.items(), key=lambda x: (x[0][0], x[0][1], x[0][2]))}
    # P1
    D = {(X, b): R[(X, "zs2", K[b])] - R[(X, "zi", K[b])] for b in P2_BETAS}
    SE = {(X, b): Q.se_diff(R[(X, "zs2", K[b])], R[(X, "zi", K[b])], K[b]) for b in P2_BETAS}
    if rule is None:
        res["P1"] = dict(verdict="UNPOWERED (witness selection or confirmation failed)")
    else:
        cells = [(X, b) for b in P1_BETAS]
        scale = {(X, b): rule["scale"][b] for b in P1_BETAS}
        T, g = Q.b2_T(D, SE, cells, scale), Q.b2_guard(D, SE, cells, scale)
        res["P1"] = dict(T=T, t=rule["t"], guard=bool(g), cells={str(b): dict(D=D[(X, b)], SE_diff=SE[(X, b)])
                                                                  for b in P1_BETAS},
                         verdict="PASS" if (T > rule["t"] and g) else "FAIL")
    # P2
    res["P2"] = {str(b): dict(D=D[(X, b)], SE_diff=SE[(X, b)], laws={
        law: dict(pred=v["pred"], window=v["consistent_window"],
                  inside=bool(v["consistent_window"][0] <= D[(X, b)] <= v["consistent_window"][1]))
        for law, v in p2[f"beta={b}"]["laws"].items()}) for b in P2_BETAS}
    # P3
    resid, ser = [], []
    for b in P3_GRID:
        r2, ra = R[(X, "zs2", K[b])], R[(X, "zi", A * K[b])]
        resid.append(r2 - ra)
        ser.append(math.hypot(r2 * se_rel(K[b]), ra * se_rel(A * K[b])))
    loc = W.p3_locate(resid)
    resol = None
    if loc is not None:
        i = max(j for j in range(len(P3_GRID) - 1) if P3_GRID[j] <= loc)
        slope = (resid[i + 1] - resid[i]) / (P3_GRID[i + 1] - P3_GRID[i])
        resol = 0.5 * (ser[i] + ser[i + 1]) / slope
    res["P3"] = dict(grid=P3_GRID, residual=resid, SE_residual=ser, location=loc, resolution=resol,
                     verdict="PASS" if (loc is not None and 0.51 <= loc <= 0.54) else "FAIL")
    # P4
    p4 = {}
    for XX in Q.XS + [10 ** 12]:
        NN = 2 * Q.n_below(zs2, XX)
        cell = {}
        for b in P4_BETAS:
            KK = K_of(NN, b)
            a, w, i = R[(XX, "zs2", KK)], R[(XX, "zw", KK)], R[(XX, "zi", KK)]
            cell[str(b)] = dict(K=KK, R_zs2=a, R_zw=w, R_zi=i, ordered=bool(a > w > i),
                                D_wi_over_D_s2i=(w - i) / (a - i) if a != i else None)
        p4[f"{XX:.0e}"] = cell
    res["P4"] = dict(cells=p4, verdict="PASS" if all(p4[x]["0.55"]["ordered"] for x in p4) else "FAIL",
                     ratio_reference=0.283)
    res["cpu_core_h"] = time.process_time() / 3600
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    print("P1", res["P1"].get("verdict"), "P3", res["P3"]["verdict"], "P4", res["P4"]["verdict"])
    return 0


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "zw34d":
        sys.exit(zw34d(sys.argv[2], *(sys.argv[3:4])))
    if c == "repro":
        sys.exit(repro(sys.argv[2], sys.argv[3], sys.argv[4]))
    sys.exit(read(*sys.argv[2:8]))
