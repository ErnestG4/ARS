#!/usr/bin/env python3
"""M3 — no-reference vs production on one sealed science cell (BRIEF §3 M3).
    usage: m3_cell.py <iid|gue> <n>
COMMITTED GENERATOR of derivflow/modes/m3_<class>_<n>.json and roots/<class>_<n>.npz.
Generalises m0_smoke.py (the iid n=4096 cell) to every (class, n) of the sealed grid; identical
arms, identical reproduction bars, identical banking. POPREF transform: iid -> analytic Uniform;
gue -> analytic semicircle sc(sigma=1) (the production GUE_DE normalisation, MANIFEST_M0).

1. Reproduce the banked PROD arms (science_dense_grid.json, data.iid.4096: mean and
   sigma_mean per k for primary / eps / 2eps) at 1e-12 relative — the tolerance the repo's own
   precedent uses for "the same instrument" (seed_roster_beta P1, 0 of 40). Reproduce the banked
   k* (kstar_table.iid.4096) point value at 1e-9 relative.
2. On the IDENTICAL roots compute NOUNFOLD and POPREF (analytic Uniform[-1,1] transform
   F = 2/log((w+1)/(w-1)) through the production reference, same eps_k rule, same Richardson).
3. M6 interlacing witness at every banked k (sharp bound k/n; BRIEF's 2k/(n-k) reported).
4. Timing: one diff_step and one reference evaluation at n in {1024, 4096, 16384}.

Roots are NOT banked by the sealed runs (M0.9); they are regenerated from the sealed
SeedSequence here and banked as .npz with sha256 so every later arm shares them.
Nothing in this file is tuned after output: the tolerances above are the repo's precedents.
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

N = int(sys.argv[2])
CLASS = sys.argv[1]
CHILD0 = M.SEAL_CHILDREN[(CLASS, N)]
R = M.R_SEAL
KS = M.K_DENSE
WORKERS = 8
OUT_JSON = os.path.join(HERE, f"m3_{CLASS}_{N}.json")
OUT_NPZ = os.path.join(HERE, "roots", f"{CLASS}_{N}.npz")
LOG = os.path.join(HERE, f"m3_{CLASS}_{N}.progress.log")

INSTRUMENT = Model("derivflow production instrument, consumed verbatim (M0.2/M0.3/M0.5)", [
    Param("KSTAR_LEVEL", DECLARED, value=M.KSTAR_LEVEL,
          why="science_rate_question.py:28; the level whose crossing defines k*"),
    Param("FIT_WINDOW_MIN", DECLARED, value=M.FIT_WINDOW_MIN,
          why="science_rate_question.py:27; the sealed fit-window rule (mean > 1e-3)"),
    Param("BULK_FRACTION", DECLARED, value=M.BULK_FRACTION,
          why="track0_harness.py:32; central window selected BY ROOT INDEX (bulk_idx)"),
    Param("k_grid", DECLARED, value="dense {1..16} u {24,32,48,64} (c986573)",
          why="the sealed grid; reproduction is only meaningful on it"),
    Param("replicates", DECLARED, value=R, why=f"the seal's 16; children {CHILD0}..{CHILD0+R-1}"),
    Param("popref_transform", DECLARED,
          value=("Uniform[-1,1]: F(w) = 2/log((w+1)/(w-1))" if CLASS == "iid"
                 else "semicircle sc(sigma=1): F(w) = (w + sqrt(w^2-4))/2"),
          why="the analytic seed law of the class; same eps_k rule and Richardson pairing "
              "as PROD_PRIMARY so only the seed transform differs"),
])


def log(msg):
    with open(LOG, "a") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")


def one_rep(i):
    child = M.seal_children()[CHILD0 + i]
    seed = M.seed_iid_uniform(child, N) if CLASS == "iid" else M.seed_gue_de(child, N)
    F_emp = M.F_empirical(seed)
    F_pop = M.F_uniform if CLASS == "iid" else M.F_semicircle(M.GUE_DE_SEMICIRCLE_SIGMA)
    POPREF_TAG = "analytic-uniform" if CLASS == "iid" else "analytic-semicircle"
    rec = {"roots": {0: seed}, "omr": {a: {} for a in ("PROD_PRIMARY", "PROD_BW1", "PROD_BW2",
                                                       "NOUNFOLD", "POPREF")},
           "diag": {}, "D": {}}
    t0 = time.time()

    def on_k(k, r):
        rec["roots"][k] = r.copy()
        pos, diag = M.prod_positions(F_emp, r, N, k)
        for arm, u in pos.items():
            rec["omr"][arm][k] = M.omr(u, N, k, arm, substrate=f"{CLASS}-{N}")[0]
        rec["omr"]["NOUNFOLD"][k] = M.omr(r, N, k, "NOUNFOLD", substrate=f"{CLASS}-{N}")[0]
        up, dpop = M.popref_positions(F_pop, r, N, k)
        rec["omr"]["POPREF"][k] = M.omr(up, N, k, "POPREF", reference=POPREF_TAG,
                                        substrate=f"{CLASS}-{N}")[0]
        rec["diag"][k] = {"prod": diag, "popref": dpop}
        rec["D"][k] = M.interlacing_D(seed, r)
        log(f"rep {i} k={k} omr prim={rec['omr']['PROD_PRIMARY'][k]:.4e} "
            f"nounf={rec['omr']['NOUNFOLD'][k]:.4e} pop={rec['omr']['POPREF'][k]:.4e} "
            f"D*n/k={rec['D'][k]*N/k:.4f} ({time.time()-t0:.0f}s)")

    M.flow(seed, KS, on_k)
    rec["runtime_s"] = time.time() - t0
    return i, rec


def timing():
    out = {}
    for n in (1024, 4096, 16384):
        seed = M.seed_iid_uniform(M.seal_children()[0], n)
        t = time.time(); r = M.diff_step(seed); t_step = time.time() - t
        F_emp = M.F_empirical(seed)
        if n == 16384:
            M.TIS.CHUNK = 1024      # step3_scale_law.py memory guard; definition unchanged
        t = time.time(); _p, d = M.prod_positions(F_emp, r, n, 1); t_ref = time.time() - t
        t = time.time(); M.popref_positions(M.F_uniform, r, n, 1); t_pop = time.time() - t
        out[str(n)] = {"diff_step_s": t_step, "prod_reference_pair_s": t_ref,
                       "popref_pair_s": t_pop, "sub_iters_k1": d["sub_iters"]}
        log(f"timing n={n}: step {t_step:.2f}s, prod ref {t_ref:.1f}s, popref {t_pop:.1f}s")
        M.TIS.CHUNK = 2048
    return out


if __name__ == "__main__":
    t_all = time.time()
    open(LOG, "w").close()
    tim = {"note": "timing measured in m0_smoke.json"}
    with Pool(WORKERS) as p:
        res = dict(p.map(one_rep, range(R)))
    log("flows done")

    # ---- bank roots ----
    os.makedirs(os.path.dirname(OUT_NPZ), exist_ok=True)
    arrays = {f"rep{i}_k{k}": res[i]["roots"][k] for i in range(R) for k in [0] + KS}
    np.savez(OUT_NPZ, **arrays)
    root_hashes = {key: M.sha256_array(a) for key, a in arrays.items()}

    # ---- reproduction against the banked artifact ----
    bank = json.load(open(os.path.join(M.DF, "science_dense_grid.json")))
    cell = bank["data"][CLASS][str(N)]
    mism = {"primary": 0, "eps": 0, "2eps": 0}
    worst = 0.0
    for arm, band, mk, sk in (("PROD_PRIMARY", "primary", "mean", "sigma_mean"),
                              ("PROD_BW1", "eps", "mean_epsraw", "sigma_mean_epsraw"),
                              ("PROD_BW2", "2eps", "mean_2eps", "sigma_mean_2eps")):
        for k in KS:
            col = np.array([res[i]["omr"][arm][k] for i in range(R)])
            for got, want in ((float(col.mean()), cell[str(k)][mk]),
                              (float(col.std(ddof=1) / np.sqrt(R)), cell[str(k)][sk])):
                rel = abs(got - want) / max(abs(want), 1e-300)
                worst = max(worst, rel)
                if rel > 1e-12:
                    mism[band] += 1
    curves = {arm: np.array([[res[i]["omr"][arm][k] for k in KS] for i in range(R)])
              for arm in res[0]["omr"]}
    rng = np.random.default_rng(12345)
    summ = {arm: M.curve_summary(curves[arm], KS, rng) for arm in curves}
    kb = bank["kstar_table"][CLASS][str(N)]
    k_rep = summ["PROD_PRIMARY"]["kstar_fit"]["value"]
    k_rel = abs(k_rep - kb["kstar"]) / kb["kstar"]

    Dmax_sharp = max(res[i]["D"][k] * N / k for i in range(R) for k in KS)
    Dmax_brief = max(res[i]["D"][k] * (N - k) / (2 * k) for i in range(R) for k in KS)

    reproduced = (sum(mism.values()) == 0) and (k_rel <= 1e-9)
    lineage = Lineage(cell=f"m3 {CLASS} n={N}",
                      construction=f"sealed SeedSequence(20260811) children {CHILD0}..{CHILD0+R-1}, diff_step, "
                                   "reference_cdf v1.5.1",
                      data=f"science seal {CLASS} n={N} replicates (regenerated roots, banked here)",
                      protocol="rtilde over bulk_idx; F3 ladder + kstar(); interp; OLS tail")
    out = {"cell": f"M3 {CLASS} n={N}", "class": CLASS, "n": N, "k_grid": KS, "replicates": R,
           "children": list(range(CHILD0, CHILD0 + R)),
           "instrument": INSTRUMENT.seal(), "lineage": lineage.record(),
           "arms_share_roots": True,
           "reproduction": {"tolerance_rel": 1e-12, "mismatches": mism,
                            "n_compared": 120, "worst_rel": worst,
                            "kstar_banked": kb, "kstar_reproduced": k_rep,
                            "kstar_rel_dev": k_rel, "kstar_tol_rel": 1e-9,
                            "REPRODUCED": bool(reproduced)},
           "arms": summ,
           "interlacing": {"bound_checked": "sharp k/n", "max_D_n_over_k": Dmax_sharp,
                           "max_D_times_(n-k)_over_2k": Dmax_brief,
                           "holds": bool(Dmax_sharp <= 1.0 + 1e-12),
                           "per_replicate_max_ratio": [max(res[i]["D"][k] * N / k for k in KS)
                                                       for i in range(R)]},
           "reference_diag": {str(k): {"prod_eps": res[0]["diag"][k]["prod"]["eps"],
                                       "prod_sub_iters": max(res[i]["diag"][k]["prod"]["sub_iters"] for i in range(R)),
                                       "prod_mass_defect_max": max(res[i]["diag"][k]["prod"]["mass_defect"] for i in range(R)),
                                       "popref_sub_iters": max(res[i]["diag"][k]["popref"]["sub_iters"] for i in range(R)),
                                       "popref_mass_defect_max": max(res[i]["diag"][k]["popref"]["mass_defect"] for i in range(R))}
                              for k in KS},
           "roots_npz": os.path.relpath(OUT_NPZ, M.ROOT), "roots_sha256": root_hashes,
           "roots_npz_sha256": M.sha256_of(OUT_NPZ),
           "timing": tim, "per_rep_runtime_s": [res[i]["runtime_s"] for i in range(R)],
           "runtime_s": time.time() - t_all}
    json.dump(out, open(OUT_JSON, "w"), indent=1)
    print(INSTRUMENT.report())
    print(f"\nREPRODUCTION: mismatches {mism} of 120 at 1e-12 rel (worst {worst:.2e}); "
          f"k* {k_rep:.6f} vs banked {kb['kstar']:.6f} (rel {k_rel:.2e}) -> "
          f"{'REPRODUCED' if reproduced else 'NOT REPRODUCED'}")
    for arm in summ:
        s = summ[arm]
        print(f"  {arm:13s} k*_fit {s['kstar_fit']['value']} +- {s['kstar_fit']['err_covariance']} "
              f"(boot {s['kstar_fit']['err_bootstrap']}) [{s['kstar_fit']['selected']}]  "
              f"k*_interp {s['kstar_interp']['value']} +- {s['kstar_interp']['err_bootstrap']}  "
              f"p_tail {s['p_tail']['value']} +- {s['p_tail']['err_bootstrap']}")
    print(f"  interlacing: max D*n/k = {Dmax_sharp:.4f} (sharp bound 1), "
          f"max D*(n-k)/2k = {Dmax_brief:.4f}; holds={out['interlacing']['holds']}")
    print(f"  timing: {json.dumps(tim)}")
    print(f"  runtime {out['runtime_s']:.0f}s -> {os.path.relpath(OUT_JSON, M.ROOT)}")
    sys.exit(0 if (reproduced and out["interlacing"]["holds"]) else 1)
