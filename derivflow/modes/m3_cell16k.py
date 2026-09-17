#!/usr/bin/env python3
"""M3 at n=16384 — the same cell as m3_cell.py, restructured for the box: flows on the certified
GPU solver (sequential), then every (replicate, k) reference evaluation in a CPU pool.
    usage: m3_cell16k.py <iid|gue>
COMMITTED GENERATOR of derivflow/modes/m3_<class>_16384.json and roots/<class>_16384.npz.
Identical arms, tags, reproduction bars (vs step3_scale_law.json data.<class>) and banking as
m3_cell.py. TIS.CHUNK = 1024 as in step3_scale_law.py (memory guard; reference unchanged).
Declared in MANIFEST_M0 as NOT RUN on the CPU projection; run because the GPU solver and the
measured reference cost make it fit the window. Nothing else changes.
"""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modes_common as M                                              # noqa: E402
from modelparams import Model, Param, DECLARED                        # noqa: E402
from lineage import Lineage                                           # noqa: E402

CLASS = sys.argv[1]
N = 16384
CHILD0 = M.SEAL_CHILDREN[(CLASS, N)]
R = M.R_SEAL
KS = M.K_DENSE
WORKERS = int(os.environ.get("M3_WORKERS", "6"))
OUT_JSON = os.path.join(HERE, f"m3_{CLASS}_{N}.json")
OUT_NPZ = os.path.join(HERE, "roots", f"{CLASS}_{N}.npz")
LOG = os.path.join(HERE, f"m3_{CLASS}_{N}.progress.log")
POPREF_TAG = "analytic-uniform" if CLASS == "iid" else "analytic-semicircle"

INSTRUMENT = Model("derivflow production instrument, consumed verbatim (M0.2/M0.3/M0.5)", [
    Param("KSTAR_LEVEL", DECLARED, value=M.KSTAR_LEVEL, why="science_rate_question.py:28"),
    Param("FIT_WINDOW_MIN", DECLARED, value=M.FIT_WINDOW_MIN, why="science_rate_question.py:27"),
    Param("BULK_FRACTION", DECLARED, value=M.BULK_FRACTION, why="track0_harness.py:32; by root index"),
    Param("k_grid", DECLARED, value="dense {1..16} u {24,32,48,64} (c986573)", why="the sealed grid"),
    Param("replicates", DECLARED, value=R, why=f"SCALE_LAW_SEAL children {CHILD0}..{CHILD0+R-1}"),
    Param("solver", DECLARED, value="modes_common.diff_step_gpu (GPU_SOLVER_CERTIFIED)", why="gpu_solver_gate.json"),
    Param("popref_transform", DECLARED,
          value=("Uniform[-1,1]: F(w) = 2/log((w+1)/(w-1))" if CLASS == "iid" else "semicircle sc(sigma=1)"),
          why="the analytic seed law of the class"),
])


def log(msg):
    with open(LOG, "a") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")


def seed_of(i):
    child = M.seal_children()[CHILD0 + i]
    return M.seed_iid_uniform(child, N) if CLASS == "iid" else M.seed_gue_de(child, N)


def _task(args):
    i, k = args
    M.TIS.CHUNK = 1024
    seed = seed_of(i)
    r = np.load(OUT_NPZ)[f"rep{i}_k{k}"]
    t0 = time.time()
    F_pop = M.F_uniform if CLASS == "iid" else M.F_semicircle(M.GUE_DE_SEMICIRCLE_SIGMA)
    pos, diag = M.prod_positions(M.F_empirical(seed), r, N, k)
    o = {arm: M.omr(u, N, k, arm, substrate=f"{CLASS}-{N}")[0] for arm, u in pos.items()}
    o["NOUNFOLD"] = M.omr(r, N, k, "NOUNFOLD", substrate=f"{CLASS}-{N}")[0]
    up, dpop = M.popref_positions(F_pop, r, N, k)
    o["POPREF"] = M.omr(up, N, k, "POPREF", reference=POPREF_TAG, substrate=f"{CLASS}-{N}")[0]
    D = M.interlacing_D(seed, r)
    log(f"rep {i} k={k} prim={o['PROD_PRIMARY']:.4e} nounf={o['NOUNFOLD']:.4e} pop={o['POPREF']:.4e} D*n/k={D*N/k:.4f} ({time.time()-t0:.0f}s)")
    return i, k, o, {"prod": diag, "popref": dpop}, D


if __name__ == "__main__":
    t_all = time.time()
    open(LOG, "a").close()
    # ---- phase 1: flows on the GPU, bank roots ----
    arrays = {}
    for i in range(R):
        seed = seed_of(i); arrays[f"rep{i}_k0"] = seed
        M.flow_gpu(seed, KS, lambda k, r, i=i: arrays.__setitem__(f"rep{i}_k{k}", r.copy()))
        log(f"rep {i} flowed ({time.time()-t_all:.0f}s)")
    os.makedirs(os.path.dirname(OUT_NPZ), exist_ok=True)
    np.savez(OUT_NPZ, **arrays)
    # ---- phase 2: references in a pool ----
    with Pool(WORKERS) as p:
        res = p.map(_task, [(i, k) for i in range(R) for k in KS])
    omr = {a: {i: {} for i in range(R)} for a in ("PROD_PRIMARY", "PROD_BW1", "PROD_BW2", "NOUNFOLD", "POPREF")}
    diag, D = {i: {} for i in range(R)}, {i: {} for i in range(R)}
    for i, k, o, d, dd in res:
        for a in omr:
            omr[a][i][k] = o[a]
        diag[i][k] = d; D[i][k] = dd
    # ---- reproduction vs step3_scale_law.json ----
    bank = json.load(open(os.path.join(M.DF, "step3_scale_law.json")))
    cell = bank["data"][CLASS]
    mism = {"primary": 0, "eps": 0, "2eps": 0}; worst = 0.0
    for arm, band, mk, sk in (("PROD_PRIMARY", "primary", "mean", "sigma_mean"),
                              ("PROD_BW1", "eps", "mean_epsraw", "sigma_mean_epsraw"),
                              ("PROD_BW2", "2eps", "mean_2eps", "sigma_mean_2eps")):
        for k in KS:
            col = np.array([omr[arm][i][k] for i in range(R)])
            for got, want in ((float(col.mean()), cell[str(k)][mk]),
                              (float(col.std(ddof=1) / np.sqrt(R)), cell[str(k)][sk])):
                rel = abs(got - want) / max(abs(want), 1e-300); worst = max(worst, rel)
                if rel > 1e-12:
                    mism[band] += 1
    curves = {a: np.array([[omr[a][i][k] for k in KS] for i in range(R)]) for a in omr}
    rng = np.random.default_rng(12345)
    summ = {a: M.curve_summary(curves[a], KS, rng) for a in curves}
    kb = bank["adjudication"][CLASS]["kstar_16384"]
    k_rep = summ["PROD_PRIMARY"]["kstar_fit"]["value"]; k_rel = abs(k_rep - kb) / kb
    Dmax_sharp = max(D[i][k] * N / k for i in range(R) for k in KS)
    Dmax_brief = max(D[i][k] * (N - k) / (2 * k) for i in range(R) for k in KS)
    reproduced = (sum(mism.values()) == 0) and (k_rel <= 1e-9)
    lineage = Lineage(cell=f"m3 {CLASS} n={N}",
                      construction=f"sealed SeedSequence(20260811) children {CHILD0}..{CHILD0+R-1}, diff_step_gpu, reference_cdf v1.5.1",
                      data=f"scale-law seal {CLASS} n={N} replicates (regenerated roots, banked here)",
                      protocol="rtilde over bulk_idx; F3 ladder + kstar(); interp; OLS tail")
    out = {"cell": f"M3 {CLASS} n={N}", "class": CLASS, "n": N, "k_grid": KS, "replicates": R,
           "children": list(range(CHILD0, CHILD0 + R)), "instrument": INSTRUMENT.seal(),
           "lineage": lineage.record(), "arms_share_roots": True,
           "reproduction": {"tolerance_rel": 1e-12, "mismatches": mism, "n_compared": 120, "worst_rel": worst,
                            "kstar_banked": {"kstar": kb, "source": "step3_scale_law.json adjudication"},
                            "kstar_reproduced": k_rep, "kstar_rel_dev": k_rel, "kstar_tol_rel": 1e-9,
                            "REPRODUCED": bool(reproduced),
                            "note": "the sealed flows used the CPU solver; this cell's flows used the certified GPU twin "
                                    "(agreement 1.4e-12 of a spacing), so 1e-12-relative equality of omr is NOT expected "
                                    "a priori — the count of mismatches is the measurement of the solver swap's effect"},
           "arms": summ,
           "interlacing": {"bound_checked": "sharp k/n", "max_D_n_over_k": Dmax_sharp,
                           "max_D_times_(n-k)_over_2k": Dmax_brief, "holds": bool(Dmax_sharp <= 1.0 + 1e-12)},
           "reference_diag": {str(k): {"prod_sub_iters": max(diag[i][k]["prod"]["sub_iters"] for i in range(R)),
                                       "prod_mass_defect_max": max(diag[i][k]["prod"]["mass_defect"] for i in range(R))}
                              for k in KS},
           "roots_npz": os.path.relpath(OUT_NPZ, M.ROOT), "roots_npz_sha256": M.sha256_of(OUT_NPZ),
           "runtime_s": time.time() - t_all}
    json.dump(out, open(OUT_JSON, "w"), indent=1)
    print(f"REPRODUCTION: mismatches {mism} of 120 at 1e-12 rel (worst {worst:.2e}); k* {k_rep:.6f} vs banked {kb:.6f} "
          f"(rel {k_rel:.2e}) -> {'REPRODUCED' if reproduced else 'NOT REPRODUCED AT 1e-12 (see note)'}")
    for a in summ:
        s = summ[a]
        print(f"  {a:13s} k*_fit {s['kstar_fit']['value']} +- {s['kstar_fit']['err_covariance']} (boot {s['kstar_fit']['err_bootstrap']}) "
              f"[{s['kstar_fit']['selected']}]  k*_interp {s['kstar_interp']['value']} +- {s['kstar_interp']['err_bootstrap']}  "
              f"p_tail {s['p_tail']['value']} +- {s['p_tail']['err_bootstrap']}")
    print(f"  interlacing max D n/k {Dmax_sharp:.4f}; runtime {out['runtime_s']:.0f}s")
    sys.exit(0 if out["interlacing"]["holds"] else 1)
