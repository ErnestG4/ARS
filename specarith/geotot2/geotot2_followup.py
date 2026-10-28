"""GEO-TOT2 follow-up (Will, 2026-10-28; DESCRIPTIVE, POST HOC, no seal) on the sealed read's data.

  python geotot2_followup.py PLAN_1e8.json FRESH_NPZ PERQ_PARQUET OUT_JSON

1. R against q: the 1,061 fresh prime squares in 4 equal bins of log₁₀ q over (6, 8]; R_N per bin (bootstrap SE) and a
   weighted least-squares line R = a + b·log₁₀ q through the 4 bins (also with the seen point, 317 ≤ p ≤ 997, added).
2. Decomposition: for each prime square q = p², its E_N keys split into Niederreiter-fold keys (folds of the keys of p,
   each re-checked here by the canonical CF of num/q: denominator q, all quotients ≤ N) and the rest. Non-fold excess =
   (c_N − F_N)·s(q) − mean of v_N over the 4 matched primes, s(q) = (q/φ(q))/q^(2δ_N − 1). Seen (p 317 … 997) and fresh.
3. Squares of higher prime powers (26 fresh, plus 2^k): representations q = m·r², 1 ≤ m ≤ N + 1, r ≥ 2, against their
   excess and the m = 1 fold.
"""
import json
import math
import sys

import numpy as np

from geotot2 import NS, cf, canon, fold_keys, matched, scale, sieve, DELTA

SEED = 20261030
NB = 10000


def check_fold(nums, q, N):
    ok = 0
    for a in nums:
        w = canon(cf(a, q))
        num, den = 0, 1
        for b in reversed(w):
            num, den = den, b * den + num
        if den == q and num == a and max(w) <= N and math.gcd(a, q) == 1:
            ok += 1
    return ok


def boot(vals, rng, ratio_den=None):
    v = np.asarray(vals)
    idx = rng.integers(0, len(v), size=(NB, len(v)))
    if ratio_den is None:
        return float(v.mean()), float(v[idx].mean(1).std(ddof=1))
    d = np.asarray(ratio_den)
    return float(v.mean() / d.mean()), float((v[idx].mean(1) / d[idx].mean(1)).std(ddof=1))


def main(plan_json, npz, perq, out):
    import pyarrow.parquet as pq_
    pl = json.load(open(plan_json))
    d = np.load(npz)
    pos = {int(q): i for i, q in enumerate(d["q"])}
    vf = lambda q, N: d["cnt_canon"][pos[q], N - 2] * scale(q, d["phi"][pos[q]], N)
    cf_ = lambda q, N: int(d["cnt_canon"][pos[q], N - 2])
    t = pq_.read_table(perq, columns=["q", "phi", "E3_canon", "E4_canon", "E5_canon"]).to_pandas()
    vs = lambda q, N: t[f"E{N}_canon"].values[q - 2] * scale(q, t.phi.values[q - 2], N)
    cs = lambda q, N: int(t[f"E{N}_canon"].values[q - 2])
    rng = np.random.default_rng(SEED)
    res = dict(label="GEO-TOT2 follow-up: descriptive, post hoc, no seal (Will, 2026-10-28)")

    # per-square rows, fresh and seen
    rows = {"fresh": [], "seen": []}
    for x in pl["fresh"]:
        if x["kind"] != "square":
            continue
        q, p = x["q"], x["p"]
        fk = fold_keys(p)
        r = dict(q=q, p=p)
        for N in NS:
            F = len(fk[N])
            assert F == x["F"][str(N)] and check_fold(fk[N], q, N) == F and F <= cf_(q, N)
            s = scale(q, q - p, N)
            mm = np.mean([vf(m, N) for m in x["matched"]])
            r[N] = dict(ex=vf(q, N) - mm, fold=F * s, nonfold_ex=(cf_(q, N) - F) * s - mm)
        rows["fresh"].append(r)
    P = sieve(10 ** 6 + 2000)
    for p in [int(p) for p in P if 317 <= p <= 997]:
        q = p * p
        m, _ = matched(q, P)
        fk = fold_keys(p)
        r = dict(q=q, p=p)
        for N in NS:
            F = len(fk[N])
            assert check_fold(fk[N], q, N) == F and F <= cs(q, N)
            s = scale(q, q - p, N)
            mm = np.mean([vs(x, N) for x in m])
            r[N] = dict(ex=vs(q, N) - mm, fold=F * s, nonfold_ex=(cs(q, N) - F) * s - mm)
        rows["seen"].append(r)

    # 2. decomposition
    dec = {}
    for rng_name, rr in rows.items():
        dec[rng_name] = {"n": len(rr)}
        for N in NS:
            ex = [r[N]["ex"] for r in rr]
            fo = [r[N]["fold"] for r in rr]
            nf = [r[N]["nonfold_ex"] for r in rr]
            dec[rng_name][str(N)] = dict(excess=boot(ex, rng), fold=float(np.mean(fo)), nonfold_excess=boot(nf, rng),
                                         R=boot(ex, rng, fo))
    res["decomposition"] = dec

    # 1. R against q (fresh, 4 bins in log10 q)
    edges = [6.0, 6.5, 7.0, 7.5, 8.0]
    lq = np.array([math.log10(r["q"]) for r in rows["fresh"]])
    bins = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        sel = [r for r, l in zip(rows["fresh"], lq) if lo < l <= hi]
        b = dict(log10q=[lo, hi], n=len(sel), center=float(np.mean([math.log10(r["q"]) for r in sel])))
        for N in NS:
            b[str(N)] = boot([r[N]["ex"] for r in sel], rng, [r[N]["fold"] for r in sel])
        bins.append(b)
    seen_c = float(np.mean([math.log10(r["q"]) for r in rows["seen"]]))
    trend = {}
    for N in NS:
        x = np.array([b["center"] for b in bins])
        y = np.array([b[str(N)][0] for b in bins])
        w = 1 / np.array([b[str(N)][1] for b in bins]) ** 2

        def wls(x, y, w):
            X = np.vstack([np.ones_like(x), x]).T
            A = X.T @ (w[:, None] * X)
            c = np.linalg.solve(A, X.T @ (w * y))
            cov = np.linalg.inv(A)
            chi2 = float(np.sum(w * (y - X @ c) ** 2))
            return dict(intercept=float(c[0]), slope_per_decade=float(c[1]), slope_SE=float(math.sqrt(cov[1, 1])),
                        chi2=chi2, dof=len(x) - 2)
        sR, sS = dec["seen"][str(N)]["R"]
        trend[str(N)] = dict(fresh_4_bins=wls(x, y, w),
                             with_seen=wls(np.append(x, seen_c), np.append(y, sR), np.append(w, 1 / sS ** 2)),
                             constant_fit=dict(R=float(np.sum(w * y) / np.sum(w)), chi2=float(
                                 np.sum(w * (y - np.sum(w * y) / np.sum(w)) ** 2)), dof=3))
    res["R_vs_q"] = dict(bins=bins, seen_point=dict(center=seen_c, **{str(N): dec["seen"][str(N)]["R"] for N in NS}),
                         trend=trend)

    # 3. squares of higher prime powers: representations q = m·r², 1 ≤ m ≤ N + 1, r ≥ 2
    ev = []
    for x in pl["fresh"]:
        if x["kind"] != "even_pp":
            continue
        q = x["q"]
        reps = {}
        for N in NS:
            reps[str(N)] = [m for m in range(1, N + 2) if q % m == 0 and math.isqrt(q // m) ** 2 == q // m
                            and math.isqrt(q // m) >= 2]
        mm = {N: np.mean([vf(m, N) for m in x["matched"]]) for N in NS}
        s = {N: scale(q, d["phi"][pos[q]], N) for N in NS}
        ev.append(dict(q=q, p=x["p"], k=x["k"], **{f"N{N}": dict(
            reps=reps[str(N)], n_reps=len(reps[str(N)]), excess=float(vf(q, N) - mm[N]), fold_m1=float(x["F"][str(N)] * s[N]),
            excess_over_fold_m1=float((vf(q, N) - mm[N]) / (x["F"][str(N)] * s[N])) if x["F"][str(N)] else None)
            for N in NS}))
    res["even_pp"] = ev
    json.dump(res, open(out, "w"), indent=1)

    for k in ("seen", "fresh"):
        print(k, dec[k]["n"], " ".join(
            f"N{N}: ex {dec[k][str(N)]['excess'][0]:+.4f}±{dec[k][str(N)]['excess'][1]:.4f} fold {dec[k][str(N)]['fold']:.4f} "
            f"nonfold {dec[k][str(N)]['nonfold_excess'][0]:+.4f}±{dec[k][str(N)]['nonfold_excess'][1]:.4f} "
            f"R {dec[k][str(N)]['R'][0]:.3f}±{dec[k][str(N)]['R'][1]:.3f} |" for N in NS))
    for b in bins:
        print("bin", b["log10q"], b["n"], " ".join(f"N{N}: R {b[str(N)][0]:.3f}±{b[str(N)][1]:.3f}" for N in NS))
    for N in NS:
        tr = trend[str(N)]
        print(f"trend N{N}: fresh slope {tr['fresh_4_bins']['slope_per_decade']:+.3f}±{tr['fresh_4_bins']['slope_SE']:.3f} "
              f"(chi2 {tr['fresh_4_bins']['chi2']:.2f}/2); with seen {tr['with_seen']['slope_per_decade']:+.3f}±"
              f"{tr['with_seen']['slope_SE']:.3f} (chi2 {tr['with_seen']['chi2']:.2f}/3); constant chi2 "
              f"{tr['constant_fit']['chi2']:.2f}/3")
    for e in ev:
        print(e["q"], f"{e['p']}^{e['k']}", " ".join(
            f"N{N}: reps {e[f'N{N}']['reps']} ex {e[f'N{N}']['excess']:+.4f} fold1 {e[f'N{N}']['fold_m1']:.4f}" for N in NS))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:5]))
