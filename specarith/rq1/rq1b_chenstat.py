"""RQ1-b, POST HOC (round 94): Chen et al.'s statistic exactly as their Appendix A computes it, for ℤ[i] and ℤ[√2].

  weights log N𝔭: log p for each of the two split ideals above p (θ and 1 − θ); inert primes q ≤ √X at θ = 0 with weight
  2 log q (ℤ[i]: q ≡ 3 mod 4; ℤ[√2]: q ≡ ±3 mod 8), generated fresh here; ramified primes and prime powers omitted (as
  Chen omits (1 + i) and prime powers); Φ = 1_(0,1] (N𝔭 ≤ X); K = round(X^λ) equal bins on θ ∈ [0, 1) (their
  HistogramList on [0, π/2)); value = Variance(bin weights, ddof 1) / (X^{1−λ} log X); λ = 0.100, 0.125, …, 0.700.
Split primes come from the 10¹¹ archives (segments with hi ≤ X; segment sha256 checked against the manifest). Both
fields at the same X, as Chen's formula is stated (not matched N). Nothing at 10¹² is touched.

  python rq1b_chenstat.py ZS2_DIR ZI_DIR OUT_JSON X [X ...]
"""
import hashlib
import json
import math
import os
import sys
import time

import numpy as np

import rq1_read as Q
import rq1_angles as R

LAMS = [round(0.1 + 0.025 * i, 3) for i in range(25)]
INERT = {"zi": lambda q: q % 4 == 3, "zs2": lambda q: q % 8 in (3, 5)}


def segments(d, Xmax):
    man = json.load(open(os.path.join(d, "MANIFEST.json")))
    for s in man["segments"]:
        if s["hi"] > Xmax:
            break
        path = os.path.join(d, f"seg_{s['k']:04d}.npy")
        assert hashlib.sha256(open(path, "rb").read()).hexdigest() == s["sha256"], path
        yield s, np.load(path)


def theta_p(ab, field):
    if field == "zs2":
        th, p = R.thetas_from_ab(ab)
        return th, p
    a, b = ab[:, 0].astype(np.int64), ab[:, 1].astype(np.int64)
    return Q.field_thetas(ab, "zi"), a * a + b * b


def run_field(d, field, Xs):
    Ks = {X: [int(round(X ** l)) for l in LAMS] for X in Xs}
    bins = {X: [np.zeros(K) for K in Ks[X]] for X in Xs}
    Xmax = max(Xs)
    t0 = time.time()
    for s, ab in segments(d, Xmax):
        th, p = theta_p(ab, field)
        w = np.log(p.astype(np.float64))
        th2 = np.concatenate([th, np.mod(1.0 - th, 1.0)])
        w2 = np.concatenate([w, w])
        for X in Xs:
            if s["hi"] > X:
                continue
            for i, K in enumerate(Ks[X]):
                idx = np.minimum((th2 * K).astype(np.int64), K - 1)
                bins[X][i] += np.bincount(idx, weights=w2, minlength=K)
    out = {}
    for X in Xs:
        r = math.isqrt(int(X))
        qs = R.primes_in(2, r + 1)
        qs = qs[[INERT[field](int(q)) for q in qs]]
        w_inert = float(np.sum(2 * np.log(qs.astype(np.float64))))
        rows = []
        for i, (lam, K) in enumerate(zip(LAMS, Ks[X])):
            b = bins[X][i].copy()
            b[0] += w_inert
            val = float(np.var(b, ddof=1)) / (X ** (1 - lam) * math.log(X))
            rows.append(dict(lam=lam, K=K, value=val))
        out[str(X)] = dict(n_inert=int(len(qs)), inert_weight=w_inert, total_weight=float(sum(bins[X][0]) + w_inert),
                           rows=rows)
    return out, time.time() - t0


def main(zs2, zi, out, Xs):
    res = dict(label="RQ1-b POST HOC: Chen et al.'s Appendix-A statistic on the RQ1 archives (round 94)", lams=LAMS,
               fields={})
    for field, d in (("zi", zi), ("zs2", zs2)):
        r, dt = run_field(d, field, Xs)
        res["fields"][field] = dict(results=r, wall_s=dt)
        print(field, f"{dt:.0f} s", {X: v["rows"][::6] for X, v in r.items()}, flush=True)
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], [int(float(x)) for x in sys.argv[4:]])
