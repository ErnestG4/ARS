"""Corrected (B), the data-free L rule (CORRECTED_B_DESIGN.md §2, f014f447). Data-free: CUE_1000 draws and predictions.

  python b2_rule.py samp REP0 REP1 OUT_DIR    (char GPU) R CUE_1000 replicates per F3 file at its pre-data size; per
                                              replicate, file, L and offset u_k = kL/32: the number of windows and the
                                              sums of d, d², d³ of the counts (d = count − round(L)), windows inside each
                                              matrix's [0, N) (matrices concatenated); seeds [20261018, 57, i, rep]
  python b2_rule.py rule OUT_DIR              k̄₃ per (rep, file, L) → μ̂ with the F3 predictions → SD_f(L), SE_pool(L),
                                              M(L) = 1/SE_pool(L), eligibility, L* → results/b2_rule.json
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import route_a_read as RR  # noqa: E402

N_MAT, CHUNK, NU = 1000, 2000, 32
LGRID = (1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0)
QUAD_TOL = 0.01


def accumulate(th, acc):
    x = np.sort(np.mod(th, 2 * np.pi), axis=1) * N_MAT / (2 * np.pi)
    k_mat = x.shape[0]
    rows = np.broadcast_to(np.arange(k_mat)[:, None], x.shape)
    for L in LGRID:
        c0 = int(round(L))
        for k in range(NU):
            u = k * L / NU
            nw = int((N_MAT - u) // L)
            j = np.floor((x - u) / L).astype(np.int64)
            ok = (x >= u) & (j < nw)
            cnt = np.bincount((rows[ok] * nw + j[ok]), minlength=k_mat * nw).astype(float)
            d = cnt - c0
            a = acc[str(L)]
            a["W"][k] += cnt.size
            a["S1"][k] += float(d.sum())
            a["S2"][k] += float((d * d).sum())
            a["S3"][k] += float((d ** 3).sum())


def samp(r0, r1, out_dir):
    import cbe
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"b2samp_{r0:03d}_{r1:03d}.jsonl")
    done = {(r["rep"], r["file"]) for r in map(json.loads, open(path))} if os.path.exists(path) else set()
    _, nf = RR.weights()
    for rep in range(r0, r1):
        for i, f in enumerate(RR.F3):
            if (rep, f) in done:
                continue
            t = time.time()
            n = int(round(nf[f]))
            rng = np.random.default_rng([20261018, 57, i, rep])
            need = -(-n // N_MAT)
            acc = {str(L): dict(W=[0] * NU, S1=[0.0] * NU, S2=[0.0] * NU, S3=[0.0] * NU) for L in LGRID}
            while need > 0:
                k = min(CHUNK, need)
                th, _ = cbe.sample(rng, k, N_MAT, 2.0, gpu=True)
                accumulate(np.asarray(th), acc)
                need -= k
            row = dict(rep=rep, file=f, i=i, n=n, n_mat=-(-n // N_MAT), acc=acc, t=round(time.time() - t, 1))
            with open(path, "a") as fh:
                fh.write(json.dumps(row) + "\n")
                fh.flush()
                os.fsync(fh.fileno())
            print(f"rep {rep} {f}: {row['n_mat']} matrices ({row['t']} s)", flush=True)


def kbar3(a):
    v = []
    for k in range(NU):
        W, s1, s2, s3 = a["W"][k], a["S1"][k], a["S2"][k], a["S3"][k]
        m1, m2, m3 = s1 / W, s2 / W, s3 / W
        v.append(W * W * (m3 - 3 * m1 * m2 + 2 * m1 ** 3) / ((W - 1) * (W - 2)))
    return float(np.mean(v)), v


def rule(out_dir):
    k3a = json.load(open(os.path.join(HERE, "results", "followup_k3.json")))["files"]
    k3b = json.load(open(os.path.join(HERE, "results", "followup_k3_r57.json")))["files"]
    pred = {f: {**k3a[f], **k3b[f]} for f in RR.F3}
    w, _ = RR.weights()
    rows = {}
    for fn in sorted(os.listdir(out_dir)):
        if fn.startswith("b2samp_"):
            for r in map(json.loads, open(os.path.join(out_dir, fn))):
                rows[(r["rep"], r["file"])] = r
    reps = sorted({rep for rep, _ in rows})
    assert all((rep, f) in rows for rep in reps for f in RR.F3) and len(reps) == 100, len(reps)
    out = dict(rule="CORRECTED_B_DESIGN.md section 2 (f014f447)", R=len(reps), L={})
    for L in LGRID:
        key = str(L)
        sd, mean_mu, k3s, qerr = {}, {}, {}, {}
        for f in RR.F3:
            p = pred[f][key]
            mus = np.array([(kbar3(rows[(rep, f)]["acc"][key])[0] - p["kappa3_sine"]) / p["dkappa3"] for rep in reps])
            sd[f], mean_mu[f] = float(mus.std(ddof=1)), float(mus.mean())
            k3s[f] = p["dkappa3"]
            qerr[f] = p["quad_err_dF3"] / abs(p["dkappa3"])
        se = float(np.sqrt(sum(w[f] ** 2 * sd[f] ** 2 for f in RR.F3)))
        elig = all(q <= QUAD_TOL for q in qerr.values())
        out["L"][key] = dict(SD=sd, SE_pool=se, M=1 / se, eligible=elig, dkappa3=k3s, quad_rel_err=qerr,
                             mean_mu_cue=mean_mu, kappa3_sine=pred[next(iter(RR.F3))][key]["kappa3_sine"])
        print(f"L = {L}: SE_pool {se:.5f}  M {1 / se:7.2f}  eligible {elig}  Δκ₃ "
              + ", ".join(f"{v:+.4e}" for v in k3s.values()) + f"  max quad rel err {max(qerr.values()):.1e}  "
              f"CUE mean μ̂ {np.mean(list(mean_mu.values())):+.4f}", flush=True)
    el = [L for L in LGRID if out["L"][str(L)]["eligible"]]
    Ls = max(el, key=lambda L: (out["L"][str(L)]["M"], -L))
    out["L_star"] = Ls
    json.dump(out, open(os.path.join(HERE, "results", "b2_rule.json"), "w"), indent=1)
    print(f"L* = {Ls}", flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "samp":
        samp(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    elif sys.argv[1] == "rule":
        rule(sys.argv[2])
