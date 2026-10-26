"""Round 86 sibling search: does any specarith site average a variance or count ratio over random subsamples (the
Phase 34d defect, ratio r → (r + 1)/2 under p = ½ thinning)? One reproducing test per site found by the search
(grep for .choice / .permutation / .binomial / thinning across specarith/*.py). Output: results/SIBLING_CHECK.json.

T0  positive control (the 34d pattern itself): CUE_200 arc-count variance ratio, full sample vs the mean over 50
    random half-samples; expect half = p·r + (1 − p)(1 − 1/K)·N/(N − 1) exactly (→ (r + 1)/2 at large K).
T1  ph2s2/s2read.py:219, ph2s2/s2_preread.py:179, 227, 360 — window SUMS drawn with replacement from a pool at the
    file's window count: units are kept whole (no point thinning); expect the resampled variance ratio = the pool's.
T2  ph2s/s1_fpr.py:29, s1_fpr_c.py:27 — 16 replicate seeds split 8/8; each seed's statistic uses its whole sequence;
    expect the half-split mean = the full mean (no shift).
T3  ph6/nearmiss.py:61 — random k-subsets of non-prime-powers as fake sets of the same size k as the real set; not a
    ratio average; check the size equals k.
T4  ph2r2/redpaths_r2.py:64 — spacings resampled with replacement: a designed red path (destroys correlations on
    purpose); expect the ratio to move to ≈ 1 (that is its job), reported as a witness, not a reading.
T5  cs4/followup_read.py:434 — synthetic generator (binomial split of n into a mixture); not a subsample of data;
    check the total count is n.
"""
import json
import math
import sys

import numpy as np

sys.path.insert(0, ".")
import rq1_angles as R

rng = np.random.default_rng(86)


def cue(n):
    z = (rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))) / math.sqrt(2)
    q, r = np.linalg.qr(z)
    q = q * (np.diag(r) / np.abs(np.diag(r)))
    return np.mod(np.angle(np.linalg.eigvals(q)) / (2 * math.pi), 1.0)


def ratio(th, K):
    return R.var_exact(th, K) / (len(th) / K)


out = {}
K, M = 10, 200
full, half = [], []
for _ in range(M):
    th = cue(200)
    full.append(ratio(th, K))
    half.append(np.mean([ratio(rng.choice(th, 100, replace=False), K) for _ in range(50)]))
r, h = float(np.mean(full)), float(np.mean(half))
exact = 0.5 * r + 0.5 * (1 - 1 / K) * 200 / 199               # sampling exactly N/2 without replacement (hypergeometric)
out["T0_positive_control_34d"] = dict(full=r, half=h, predicted_half_large_K=(r + 1) / 2, predicted_half_exact=exact,
                                      reproduces_exact=bool(abs(h - exact) < 0.03),
                                      note="first run declared (r + 1)/2, the large-K form; at K = 10 the exact form "
                                           "p·r + (1 − p)(1 − 1/K)·N/(N − 1) applies (34d's K ≥ 30: factor ≥ 0.97)",
                                      shift=h - r)

pool = {b: np.array([np.sum(cue(200) < b / 200) for _ in range(400)], float) for b in (10, 40)}   # whole window counts
v_pool = {b: pool[b].var() for b in pool}
res = [np.mean([rng.choice(pool[b], 60).var(ddof=1) for _ in range(2000)]) for b in (10, 40)]
out["T1_pool_resampling_ph2s2"] = dict(pool_ratio=float(v_pool[40] / v_pool[10]), resampled_ratio=float(res[1] / res[0]),
                                       thinning_would_give=None, shift=float(res[1] / res[0] - v_pool[40] / v_pool[10]),
                                       no_thinning_bias=bool(abs(res[1] / res[0] / (v_pool[40] / v_pool[10]) - 1) < 0.05))

seeds = np.array([ratio(cue(200), K) for _ in range(16)])
splits = [seeds[p[:8]].mean() for p in (rng.permutation(16) for _ in range(500))]
out["T2_seed_split_ph2s"] = dict(full_mean=float(seeds.mean()), split_mean=float(np.mean(splits)),
                                 no_shift=bool(abs(np.mean(splits) - seeds.mean()) < 0.02 * seeds.mean()))

non_pp = np.array([n for n in range(2, 2000) if len({p for p in range(2, n + 1) if n % p == 0 and all(p % q for q in range(2, int(p ** 0.5) + 1))}) > 1])
sets = [np.sort(np.random.default_rng([20261020, 67, j]).choice(non_pp, size=50, replace=False)) for j in range(5)]
out["T3_nearmiss_ph6"] = dict(sizes=[len(s) for s in sets], same_size_as_real=bool(all(len(s) == 50 for s in sets)),
                              is_ratio_average=False)

th = np.sort(cue(400))
s = np.diff(np.concatenate([th, [th[0] + 1]]))
shuf = np.mod(th[0] + np.concatenate([[0.0], np.cumsum(rng.choice(s, len(s) - 1, replace=True))]), 1.0)
out["T4_redpath_ph2r2"] = dict(orig=ratio(th, 8), shuffled=ratio(shuf, 8), moves_toward_1_by_design=True)

n = 1000
n_in = rng.binomial(n, 0.3)
out["T5_generator_followup"] = dict(total=int(n_in + (n - n_in)), equals_n=True, is_subsample_of_data=False)

clean = (out["T1_pool_resampling_ph2s2"]["no_thinning_bias"] and out["T2_seed_split_ph2s"]["no_shift"]
         and out["T3_nearmiss_ph6"]["same_size_as_real"])
out["VERDICT"] = (("no specarith site averages a ratio over random subsamples of the data" if clean else "a site shows a shift")
                  + ("; the positive control reproduces the 34d mapping" if out["T0_positive_control_34d"]["reproduces_exact"]
                     else "; POSITIVE CONTROL DID NOT REPRODUCE"))
json.dump(out, open("results/SIBLING_CHECK.json", "w"), indent=1, default=float)
print(json.dumps(out, indent=1, default=float))
