"""POST-HOC, DATA SEEN (round 56; descriptive, no verdict): (B)'s k₃ at L = 3 on F5, averaged over grid offsets.

For each F5 file (md5 against the pin before decoding; the sealed read's decode and exact-θ unfolding), windows
[u + jL, u + (j + 1)L), j ≥ 0, entirely inside [0, x_last], at NU = 32 offsets u_k = kL/NU. k̄₃ = mean over offsets of
the k-statistic k₃(u). SE from a joint block bootstrap over all offsets: the unfolded axis is cut into segments of
SEG = 300 units (a window belongs to the segment holding its start); each bootstrap replicate resamples segments with
replacement (the same draw for every offset) and recomputes k̄₃ from the resampled segment sums of d, d², d³
(d = count − 3). μ̃_f = (k̄₃ − κ₃^sine)/Δκ₃,f − b_f (sealed prediction and calibration bias), SE in μ from the bootstrap.
Pooled with the sealed weights; heterogeneity χ² about the pool. Offset u = 0 must reproduce the sealed read's k₃.

  python diag_d_phaseavg.py run FILE OUT_DIR      (spot; one process per file)
  python diag_d_phaseavg.py merge OUT_DIR         → OUT_DIR/PHASEAVG.json
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import followup_read as FR  # noqa: E402

L, NU, SEG, B = 3.0, 32, 300.0, 500
SEED = [20261018, 56]


def k3_from_sums(n, s1, s2, s3):
    m1, m2, m3 = s1 / n, s2 / n, s3 / n
    c3 = m3 - 3 * m1 * m2 + 2 * m1 ** 3
    return n * n * c3 / ((n - 1) * (n - 2))


def run(f, out_dir):
    import followup_sealread as SR
    i = list(FR.FILES["B"]).index(f)
    p = os.path.join(SR.FRESH, f)
    if SR.md5(p) != SR.MD5["B"][f]:
        raise SystemExit(f"REFUSED: {p} md5 differs from the pin")
    t0, t1 = FR.FILES["B"][f]
    g = SR.decode(p, t0, t1)
    _, x = FR.unfold(g, t0, dps=SR.DPS - 5)
    del g
    nseg = int(math.floor(x[-1] / SEG)) + 1
    S = np.zeros((NU, 3, nseg))                       # per offset, per moment, per segment
    N = np.zeros((NU, nseg))
    per = []
    for k in range(NU):
        u = k * L / NU
        W = int(math.floor((x[-1] - u) / L))
        j = np.floor((x[x >= u] - u) / L).astype(np.int64)
        c = np.bincount(j[j < W], minlength=W).astype(np.int64)
        d = (c - 3).astype(float)
        seg = np.floor((u + L * np.arange(W)) / SEG).astype(np.int64)
        for q in range(3):
            S[k, q] = np.bincount(seg, weights=d ** (q + 1), minlength=nseg)
        N[k] = np.bincount(seg, minlength=nseg)
        per.append(dict(u=u, W=W, k3=float(k3_from_sums(W, *(S[k, q].sum() for q in range(3)))),
                        k3_direct=FR.k3(c), k2=float(np.var(c, ddof=1))))
    k3bar = float(np.mean([r["k3"] for r in per]))
    rng = np.random.default_rng(SEED + [i])
    boots = np.empty(B)
    for b in range(B):
        idx = rng.integers(0, nseg, nseg)
        cnt = np.bincount(idx, minlength=nseg).astype(float)
        vals = [k3_from_sums((N[k] * cnt).sum(), *((S[k, q] * cnt).sum() for q in range(3))) for k in range(NU)]
        boots[b] = np.mean(vals)
    res = dict(file=f, NU=NU, SEG=SEG, B=B, nseg=nseg, per_offset=per, k3bar=k3bar,
               k3bar_se=float(np.std(boots, ddof=1)))
    os.makedirs(out_dir, exist_ok=True)
    json.dump(res, open(os.path.join(out_dir, f"phaseavg_{f}.json"), "w"), indent=1)
    print(f"{f}: k3(u=0) {per[0]['k3']:+.6f} (direct {per[0]['k3_direct']:+.6f}); k3bar {k3bar:+.6f} ± "
          f"{res['k3bar_se']:.6f}; k3(u) range [{min(r['k3'] for r in per):+.5f}, {max(r['k3'] for r in per):+.5f}]",
          flush=True)


def merge(out_dir):
    pred = json.load(open(FR.PRED["B"]))
    cal = json.load(open(FR.CALIB["B"]))
    sealed = json.load(open(os.path.join(HERE, "results", "followup_read", "B", "run1", "FOLLOWUP_READ.json")))
    w, _ = FR.weights("B")
    fs = list(FR.FILES["B"])
    rows = {}
    for f in fs:
        r = json.load(open(os.path.join(out_dir, f"phaseavg_{f}.json")))
        d, ks = pred["files"][f]["dkappa3"], pred["files"][f]["kappa3_sine"]
        rows[f] = dict(k3bar=r["k3bar"], k3bar_se=r["k3bar_se"],
                       mu=(r["k3bar"] - ks) / d - cal["files"][f]["bias"], mu_se=r["k3bar_se"] / abs(d),
                       k3_u0=r["per_offset"][0]["k3"], sealed_k3=sealed["records"][f]["k3"],
                       u0_reproduces_sealed=abs(r["per_offset"][0]["k3"] - sealed["records"][f]["k3"]) < 1e-10,
                       k3_u_min=min(x["k3"] for x in r["per_offset"]), k3_u_max=max(x["k3"] for x in r["per_offset"]))
    mu = np.array([rows[f]["mu"] for f in fs])
    se = np.array([rows[f]["mu_se"] for f in fs])
    W = np.array([w[f] for f in fs])
    pool = float(np.dot(W, mu))
    pool_se = float(math.sqrt(np.sum(W ** 2 * se ** 2)))
    chi = float(np.sum(((mu - pool) / se) ** 2))
    out = dict(label="post-hoc, data seen (round 56); descriptive, no verdict", files=rows, mu_pool=pool,
               mu_pool_se=pool_se, chi2_between=chi, dof=len(fs) - 1,
               note="SE is the joint block bootstrap only (no CUE floor); the sealed SE floor (CUE SD) is not applied")
    json.dump(out, open(os.path.join(out_dir, "PHASEAVG.json"), "w"), indent=1)
    for f in fs:
        r = rows[f]
        print(f"{f}: μ̃ {r['mu']:.4f} ± {r['mu_se']:.4f}  (k̄3 {r['k3bar']:+.6f} ± {r['k3bar_se']:.6f}; k3(u) "
              f"[{r['k3_u_min']:+.5f}, {r['k3_u_max']:+.5f}]; u=0 reproduces sealed: {r['u0_reproduces_sealed']})")
    print(f"pooled μ̃ {pool:.4f} ± {pool_se:.4f}; heterogeneity χ² {chi:.1f} on {len(fs) - 1}")


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "merge":
        merge(sys.argv[2])
