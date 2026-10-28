"""GEO-TOT2 (Will, 2026-10-28; GEOTOT2_SEAL.md): prime powers in (10⁶, 10⁷] against size-matched primes.

Value per q and N (as GEO-TOT1): v_N(q) = c_N(q)·(q/φ(q)) / q^(2δ_N − 1), c_N(q) = #{a coprime to q, 0 < a < q, a/q ∈ E_N}
(canonical CF, last quotient ≥ 2). Excess at a target q: v_N(q) − mean of v_N over its 4 matched primes (the 4 primes
nearest q; ties to the smaller). Fold count at a square q = p²: F_N(q) = the number of distinct canonical E_N keys of p²
given by Niederreiter's folding of the keys of p (a/p = [b₁…b_s] ↦ [b₁, …, b_{s−1}, b_s + 1, b_s − 1, b_{s−1}, …, b₁],
denominator p²), on the same scale: f_N(q) = F_N(q)·(q/φ(q)) / q^(2δ_N − 1).

(A) Odd prime powers p^k, k odd ≥ 3, p ≥ 7 (non-foldable for N ≤ 5: q = p·r² with p > N + 1), 10⁶ < q ≤ 10⁷: mean excess.
(B) Prime squares p², 10⁶ < q ≤ 10⁷: R_N = mean excess / mean f_N over the squares; pooled R = inverse-variance-weighted
    mean of R_3, R_4, R_5 (weights from their bootstrap SEs). SEs by a bootstrap over targets (10,000 resamples).

  python geotot2.py plan PERQ_PARQUET OUT_JSON [HI] seen range (HI = 1e7 default) + deterministic arithmetic only (no q > 10⁶ counted)
  python geotot2.py enum PLAN_JSON OUT_NPZ          the fresh q (targets and matched primes), counts for N = 2 … 6
  python geotot2.py read PLAN_JSON NPZ OUT_JSON     sealed read
"""
import hashlib
import json
import math
import os
import sys
import time

import numpy as np
from numba import njit, prange

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "geotot1"))
from geotot1 import one_q, LH, SH                          # noqa: E402  (the GEO-TOT1 per-q kernel, pinned)
from geotot1_analyze import DELTA                         # noqa: E402

NS = (3, 4, 5)
LO, HI = 10 ** 6, 10 ** 7
SEED = 20261028
NBOOT = 10000
MU = 12 * math.log(2) / math.pi ** 2


def sieve(n):
    s = np.ones(n + 1, bool)
    s[:2] = False
    for p in range(2, math.isqrt(n) + 1):
        if s[p]:
            s[p * p::p] = False
    return np.flatnonzero(s)


def matched(q, primes):
    i = int(np.searchsorted(primes, q))
    cand = primes[max(0, i - 6):i + 6]
    order = sorted(cand.tolist(), key=lambda x: (abs(x - q), x))
    return order[:4], order[4]                            # the 4 matched primes, and the 5th (witness base)


def cf(a, r):
    out = []
    while a:
        k = r // a
        out.append(k)
        r, a = a, r - k * a
    return out


def canon(w):
    w = list(w)
    if len(w) > 1 and w[-1] == 1:
        w = w[:-2] + [w[-2] + 1]
    return w


def value(w):
    """(numerator, denominator) of [0; w] by the convergent recurrence."""
    p0, q0 = 0, 1
    for b in reversed(w):
        p0, q0 = q0, b * q0 + p0
    return p0, q0


def fold_keys(p):
    """{N: sorted list of distinct numerators of canonical E_N keys of p² obtained by folding the keys of p}."""
    out = {N: set() for N in NS}
    for a in range(1, p):
        if math.gcd(a, p) != 1:
            continue
        b = cf(a, p)
        w = canon(b[:-1] + [b[-1] + 1, b[-1] - 1] + b[:-1][::-1])
        num, den = value(w)
        assert den == p * p and math.gcd(num, den) == 1 and value(cf(num, den)) == (num, den)
        m = max(w)
        for N in NS:
            if m <= N:
                out[N].add(num)
    return {N: sorted(v) for N, v in out.items()}


def scale(q, phi, N):
    return (q / phi) / q ** (2 * DELTA[N] - 1)


def boot_R(ex, fo, rng):
    """R per N (ratio of means), bootstrap SEs, pooled inverse-variance mean and its bootstrap SE. ex, fo: {N: array}."""
    n = len(ex[NS[0]])
    idx = rng.integers(0, n, size=(NBOOT, n))
    R = {N: float(ex[N].mean() / fo[N].mean()) for N in NS}
    Rb = {N: ex[N][idx].mean(1) / fo[N][idx].mean(1) for N in NS}
    se = {N: float(Rb[N].std(ddof=1)) for N in NS}
    w = {N: 1 / se[N] ** 2 for N in NS}
    W = sum(w.values())
    pool = sum(w[N] * R[N] for N in NS) / W
    poolb = sum(w[N] * Rb[N] for N in NS) / W
    return dict(R={str(N): R[N] for N in NS}, SE={str(N): se[N] for N in NS}, pooled=float(pool),
                pooled_SE=float(poolb.std(ddof=1)), weights={str(N): w[N] / W for N in NS},
                mean_excess={str(N): float(ex[N].mean()) for N in NS}, mean_fold={str(N): float(fo[N].mean()) for N in NS})


def reading(R, se, R_seen, se_seen):
    cf_ = abs(R - 1) <= 2 * se
    cs = abs(R - R_seen) <= 2 * math.hypot(se, se_seen)
    v = "pure folding" if cf_ and not cs else ("displacement" if cs and not cf_ else "unpowered/unexplained")
    return dict(R=R, SE=se, consistent_H_fold=bool(cf_), consistent_H_seen=bool(cs), reading=v)


def targets(primes, HI):
    sq = [int(p) * int(p) for p in primes if LO < int(p) * int(p) <= HI]
    odd, even = [], []
    for p in primes:
        p = int(p)
        if p ** 3 > HI:
            continue
        for k in range(3, 64):
            if p ** k > HI:
                break
            if p ** k > LO and k % 2 == 1 and p >= 7:
                odd.append((p ** k, p, k))
            if p ** k > LO and k % 2 == 0:
                even.append((p ** k, p, k))       # r² with r = p^(k/2): descriptive only
    return sq, sorted(odd), sorted(even)


def plan(perq, out, HI=HI):
    import pyarrow.parquet as pq_
    t = pq_.read_table(perq, columns=["q", "phi", "type", "E3_canon", "E4_canon", "E5_canon"]).to_pandas()
    q1, phi1, typ = t.q.values, t.phi.values, t.type.astype(str).values
    vseen = {N: t[f"E{N}_canon"].values * scale(q1.astype(float), phi1, N) for N in NS}
    P = sieve(HI + 2000)
    sq, odd, even = targets(P, HI)
    res = dict(label="GEO-TOT2 plan: seen range (q ≤ 10⁶) and deterministic arithmetic only", seed=SEED, nboot=NBOOT,
               range=[LO, HI])
    # fresh targets and their matched primes
    fresh = []
    for q in sq:
        m, fifth = matched(q, P)
        fresh.append(dict(q=q, kind="square", p=math.isqrt(q), matched=m))
    for q, p, k in odd:
        m, fifth = matched(q, P)
        fresh.append(dict(q=q, kind="odd_pp", p=p, k=k, matched=m))
    for q, p, k in even:
        m, fifth = matched(q, P)
        fresh.append(dict(q=q, kind="even_pp", p=p, k=k, r=p ** (k // 2), matched=m))
    allq = sorted({x["q"] for x in fresh} | {m for x in fresh for m in x["matched"]})
    assert all(q > LO for q in allq)
    res["fresh"] = fresh
    res["fresh_q_list"] = allq
    res["n_squares"], res["n_odd_pp"], res["n_even_pp"] = len(sq), len(odd), len(even)
    # fold counts for the fresh squares (keys of p ≤ 3162: seen range)
    t0 = time.time()
    fk = {}
    for x in fresh:
        if x["kind"] in ("square", "even_pp"):
            f = fold_keys(x.get("r", x["p"]))
            x["F"] = {str(N): len(f[N]) for N in NS}
            fk[x["q"]] = f
    res["fold_seconds"] = time.time() - t0
    # seen squares (p ≤ 997, q ≤ 10⁶): H_seen, noise and the witness
    seen_p = [int(p) for p in P if 317 <= p <= 997]
    rng = np.random.default_rng(SEED)
    ex, fo = {N: [] for N in NS}, {N: [] for N in NS}
    wit_base = {N: [] for N in NS}
    seen_fold = {}
    for p in seen_p:
        q = p * p
        m, fifth = matched(q, P)
        f = fold_keys(p)
        seen_fold[p] = f
        for N in NS:
            vm = np.mean([vseen[N][x - 2] for x in m])
            ex[N].append(vseen[N][q - 2] - vm)
            fo[N].append(len(f[N]) * scale(q, phi1[q - 2], N))
            wit_base[N].append((vseen[N][fifth - 2] - vm, scale(q, phi1[q - 2], N), len(f[N])))
    ex = {N: np.array(v) for N, v in ex.items()}
    fo = {N: np.array(v) for N, v in fo.items()}
    res["H_seen"] = boot_R(ex, fo, rng)
    res["H_seen"]["n"] = len(seen_p)
    # witness: H_fold made true by construction on the seen squares. Each square's count is replaced by its 5th-nearest
    # prime's value (real noise, not among the 4 matched) plus a seeded subset of (1 − x) of its fold keys.
    wit = {}
    for x in (0.0, 0.25, 0.5):
        exw, fow = {}, {}
        for N in NS:
            e, f_ = [], []
            for (b, s, F) in wit_base[N]:
                keep = F - int(round(x * F))
                e.append(b + keep * s)
                f_.append(F * s)
            exw[N], fow[N] = np.array(e), np.array(f_)
        r = boot_R(exw, fow, rng)
        r["pass"] = {str(N): abs(r["R"][str(N)] - (1 - x)) <= 2 * r["SE"][str(N)] for N in NS}
        r["pass"]["pooled"] = abs(r["pooled"] - (1 - x)) <= 2 * r["pooled_SE"]
        wit[str(x)] = r
    res["witness"] = wit
    res["witness_PASS"] = all(all(wit[x]["pass"].values()) for x in ("0.25", "0.5"))
    # literal reading of the witness (remove x of the fold keys from the real seen counts): R = R_seen − x exactly
    res["witness_literal_note"] = "on the real seen counts, removing x of the fold keys gives R = R_seen − x by construction"
    # noise model: prime 'null excess' v(q') − mean of its 4 nearest other primes, SD per decade-tenth bin, power-law fit
    pr = q1[typ == "prime"]
    sd_x, sd_y = [], []
    for j in range(40, 60):
        lo, hi = 10 ** (j / 10), 10 ** ((j + 1) / 10)
        sel = pr[(pr >= lo) & (pr < hi)]
        sel = rng.choice(sel, min(400, len(sel)), replace=False)
        d = {N: [] for N in NS}
        for x in sel:
            i = int(np.searchsorted(pr, x))
            nb = sorted([y for y in pr[max(0, i - 5):i + 6] if y != x], key=lambda y: (abs(y - x), y))[:4]
            for N in NS:
                d[N].append(vseen[N][x - 2] - np.mean([vseen[N][y - 2] for y in nb]))
        sd_x.append(math.log(np.sqrt(lo * hi)))
        sd_y.append({N: math.log(np.std(d[N], ddof=1)) for N in NS})
    fit = {N: np.polyfit(sd_x, [y[N] for y in sd_y], 1) for N in NS}
    res["noise_model"] = {str(N): dict(slope=float(fit[N][0]), intercept=float(fit[N][1]),
                                       sd_at_1e6=float(math.exp(np.polyval(fit[N], math.log(1e6))))) for N in NS}
    # predicted fresh SEs and power (normal approximation, 200,000 draws)
    sqs = [x for x in fresh if x["kind"] == "square"]
    pw = {}
    phi_sq = lambda x: x["q"] * (1 - 1 / x["p"])
    for N in NS:
        sds = np.array([math.exp(np.polyval(fit[N], math.log(x["q"]))) for x in sqs])
        f_mean = np.mean([x["F"][str(N)] * scale(x["q"], phi_sq(x), N) for x in sqs])
        se_R = math.sqrt((sds ** 2).sum()) / len(sqs) / f_mean
        Rs, ss = res["H_seen"]["R"][str(N)], res["H_seen"]["SE"][str(N)]
        z = np.random.default_rng(SEED + N).standard_normal(200000)
        fold_ok = np.mean([reading(1 + se_R * v, se_R, Rs, ss)["reading"] == "pure folding" for v in z[:20000]])
        seen_ok = np.mean([reading(Rs + se_R * v, se_R, Rs, ss)["reading"] == "displacement" for v in z[20000:40000]])
        pw[str(N)] = dict(mean_fold_fresh=float(f_mean), pred_SE_R=float(se_R), R_seen=Rs, SE_seen=ss,
                          separation_sd=float(abs(1 - Rs) / math.hypot(se_R, ss)),
                          P_pure_folding_given_H_fold=float(fold_ok), P_displacement_given_H_seen=float(seen_ok))
    # pooled: inverse-variance weights from the predicted SEs; the predicted pooled SE is the independent-N value
    # inflated by the seen ratio (bootstrap pooled SE / independent-N value), since the three N share their q
    hsS = res["H_seen"]["SE"]
    infl = res["H_seen"]["pooled_SE"] * math.sqrt(sum(1 / hsS[str(N)] ** 2 for N in NS))
    wN = {N: 1 / pw[str(N)]["pred_SE_R"] ** 2 for N in NS}
    se_pool = infl / math.sqrt(sum(wN.values()))
    Rs, ss = res["H_seen"]["pooled"], res["H_seen"]["pooled_SE"]
    z = np.random.default_rng(SEED + 9).standard_normal(40000)
    pw["pooled"] = dict(pred_SE_R=float(se_pool), correlation_inflation=float(infl), R_seen=Rs, SE_seen=ss,
                        separation_sd=float(abs(1 - Rs) / math.hypot(se_pool, ss)),
                        P_pure_folding_given_H_fold=float(np.mean([reading(1 + se_pool * v, se_pool, Rs, ss)["reading"]
                                                                   == "pure folding" for v in z[:20000]])),
                        P_displacement_given_H_seen=float(np.mean([reading(Rs + se_pool * v, se_pool, Rs, ss)["reading"]
                                                                   == "displacement" for v in z[20000:]])))
    res["power"] = pw
    # (A) predicted SE against fold-size/2 (fold size = mean f_N over the fresh squares)
    pa = {}
    for N in NS:
        sds = np.array([math.exp(np.polyval(fit[N], math.log(x["q"]))) for x in fresh if x["kind"] == "odd_pp"])
        se_A = math.sqrt((sds ** 2).sum()) / len(sds)
        pa[str(N)] = dict(pred_SE=float(se_A), fold_size=pw[str(N)]["mean_fold_fresh"],
                          powered=bool(se_A <= pw[str(N)]["mean_fold_fresh"] / 2))
    res["power_A"] = pa
    # cost model (GEO-TOT1: 6.06 ns per Euclid step locally, × 2.3 on spot; measured 0.86× of this model)
    res["cost_spot_core_h"] = sum((q - 1) * (MU * math.log(q) + 1.0) for q in allq) * 6.06e-9 * 2.3 / 3600
    json.dump(res, open(out, "w"), indent=1)
    print("squares", len(sq), "odd pp", len(odd), "fresh q", len(allq), f"cost {res['cost_spot_core_h']:.2f} spot core-h")
    print("H_seen", json.dumps({k: res['H_seen'][k] for k in ('R', 'SE', 'pooled', 'pooled_SE')}))
    print("witness PASS", res["witness_PASS"], json.dumps({x: (wit[x]["R"], wit[x]["pooled"]) for x in wit}))
    print("power", json.dumps(pw))
    print("power A", json.dumps(pa))
    return 0


@njit(cache=False, parallel=True)
def enum_list(qs):
    n = len(qs)
    phi = np.zeros(n, np.int64)
    cc = np.zeros((n, 5), np.int64)
    ca = np.zeros((n, 5), np.int64)
    for i in prange(n):
        Lh = np.zeros(LH, np.int64)
        Sh = np.zeros(SH, np.int64)
        Mh = np.zeros(SH, np.int64)
        p, s, l1, l2 = one_q(qs[i], cc[i], ca[i], Lh, Sh, Mh)
        phi[i] = p
    return phi, cc, ca


def enum(plan_json, out):
    """20 chunks of the seeded permutation of the q list (balances the threads); cost checks against the GEO-TOT1 model
    (6.06 ns per Euclid step × 2.3 on spot) after the first chunk and at 25 / 50 / 75%: above 1.25× → STOPPED, exit 3."""
    pl = json.load(open(plan_json))
    qs = np.array(pl["fresh_q_list"], np.int64)
    order = np.random.default_rng(SEED).permutation(len(qs))
    model = lambda v: float(sum((int(q) - 1) * (MU * math.log(int(q)) + 1.0) for q in v)) * 6.06e-9 * 2.3
    enum_list(np.array([5, 7], np.int64))                        # compile outside the cost measurement
    t0 = time.process_time()
    phi = np.zeros(len(qs), np.int64)
    cc = np.zeros((len(qs), 5), np.int64)
    ca = np.zeros((len(qs), 5), np.int64)
    chunks = np.array_split(order, 20)
    checks = {0: "first", 5: "25%", 10: "50%", 15: "75%"}
    done = []
    for c, idx in enumerate(chunks):
        if c in checks and c > 0 or c == 1:
            r = (time.process_time() - t0) / model(qs[np.concatenate(done)])
            lab = checks.get(c, "first")
            print(f"{lab}: {c} chunks, cpu/model = {r:.3f}", flush=True)
            if r > 1.25:
                open(out + ".STOPPED", "w").write(f"cost above 1.25x at {lab}: {r:.3f}\n")
                return 3
        p_, c_, a_ = enum_list(qs[idx])
        phi[idx], cc[idx], ca[idx] = p_, c_, a_
        done.append(idx)
    cpu = time.process_time() - t0
    np.savez(out, q=qs, phi=phi, cnt_canon=cc, cnt_alt=ca)
    open(out + ".cpu", "w").write(f"{cpu:.3f} {cpu / model(qs):.4f}\n")
    print(f"done: cpu {cpu / 3600:.2f} core-h = {cpu / model(qs):.3f}x model", flush=True)
    return 0


def read(plan_json, npz, out):
    pl = json.load(open(plan_json))
    d = np.load(npz)
    pos = {int(q): i for i, q in enumerate(d["q"])}
    assert set(pos) == set(pl["fresh_q_list"])
    v = lambda q, N: d["cnt_canon"][pos[q], N - 2] * scale(q, d["phi"][pos[q]], N)
    rng = np.random.default_rng(SEED + 1)
    res = dict(label="GEO-TOT2 sealed read")
    # (A)
    odd = [x for x in pl["fresh"] if x["kind"] == "odd_pp"]
    A = {}
    for N in NS:
        e = np.array([v(x["q"], N) - np.mean([v(m, N) for m in x["matched"]]) for x in odd])
        se = float(e.std(ddof=1) / math.sqrt(len(e)))
        fs = pl["power"][str(N)]["mean_fold_fresh"]
        verdict = "UNPOWERED" if se > fs / 2 else ("PASS (zero excess)" if abs(e.mean()) <= 2 * se else "FAIL (nonzero excess)")
        A[str(N)] = dict(n=len(e), mean_excess=float(e.mean()), SE=se, fold_size=fs, verdict=verdict)
    res["A"] = A
    # (B)
    sqs = [x for x in pl["fresh"] if x["kind"] == "square"]
    ex, fo = {}, {}
    for N in NS:
        ex[N] = np.array([v(x["q"], N) - np.mean([v(m, N) for m in x["matched"]]) for x in sqs])
        fo[N] = np.array([x["F"][str(N)] * scale(x["q"], d["phi"][pos[x["q"]]], N) for x in sqs])
    b = boot_R(ex, fo, rng)
    hs = pl["H_seen"]
    B = {str(N): reading(b["R"][str(N)], b["SE"][str(N)], hs["R"][str(N)], hs["SE"][str(N)]) for N in NS}
    B["pooled"] = reading(b["pooled"], b["pooled_SE"], hs["pooled"], hs["pooled_SE"])
    res["B"] = dict(per_N=B, detail=b, n=len(sqs))
    ev = [x for x in pl["fresh"] if x["kind"] == "even_pp"]
    res["even_pp_descriptive"] = [dict(q=x["q"], p=x["p"], k=x["k"], **{
        f"N{N}": dict(excess=float(v(x["q"], N) - np.mean([v(m, N) for m in x["matched"]])),
                      fold=float(x["F"][str(N)] * scale(x["q"], d["phi"][pos[x["q"]]], N))) for N in NS}) for x in ev]
    res["phi_check"] = all(int(d["phi"][pos[x["q"]]]) == x["q"] - x["q"] // x["p"] for x in pl["fresh"])
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    print(json.dumps({"A": {N: A[N]["verdict"] for N in A}, "B": {k: B[k]["reading"] for k in B}}))
    return 0


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "plan":
        sys.exit(plan(sys.argv[2], sys.argv[3], *([int(float(sys.argv[4]))] if len(sys.argv) > 4 else [])))
    if c == "enum":
        sys.exit(enum(sys.argv[2], sys.argv[3]))
    sys.exit(read(sys.argv[2], sys.argv[3], sys.argv[4]))
