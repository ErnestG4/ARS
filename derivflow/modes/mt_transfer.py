#!/usr/bin/env python3
"""GATE MT — transfer function of the production unfolding reference on a planted wave
(BRIEF §3 MT). COMMITTED GENERATOR of derivflow/modes/mt_transfer.json and roots/mt_16384.npz.

    usage: mt_transfer.py flows      # GPU/CPU flows: LATTICE + LATTICE_WAVE(qw, 1e-5, 0.3), n=16384, bank roots
           mt_transfer.py refs       # CPU pool: every arm's unfolded positions at every k, T per arm

Executes seal_night1.json["MT"] verbatim. Each run is unfolded against ITS OWN reference
(F_empirical of its own seed), exactly as production; POPREF uses the analytic Uniform[-1,1]
transform; RM1 the local 3-gap running mean. T = P_c(u_wave - u_lat) / P_c((x_wave - x_lat)/h),
complex Hann-tapered projections on exp(-i theta), theta = qw (i + k/2) + phi, bulk window.
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
from ml_gain_gate import solver_choice, hann, local_spacing, PHI     # noqa: E402

SEAL = json.load(open(os.path.join(HERE, "seal_night1.json")))
MT = SEAL["MT"]
N = 16384
A = 1e-5
QW, KS = MT["qw_grid"], MT["k_grid"]
NPZ = os.path.join(HERE, "roots", f"mt_{N}.npz")
LOG = os.path.join(HERE, "mt_transfer.progress.log")
WORKERS = int(os.environ.get("MT_WORKERS", "6"))   # resource knob only
PASS_TOL = 0.1
QW_PASS = (0.1, 0.5)

INSTRUMENT = Model("gate MT measurement (declared in seal_night1.json)", [
    Param("KSTAR_LEVEL", DECLARED, value=M.KSTAR_LEVEL, why="imported constant; unused by MT but declared"),
    Param("FIT_WINDOW_MIN", DECLARED, value=M.FIT_WINDOW_MIN, why="imported constant; unused by MT but declared"),
    Param("BULK_FRACTION", DECLARED, value=M.BULK_FRACTION, why="the projection window (bulk_idx)"),
    Param("A", DECLARED, value=A, why="seal: planted amplitude 1e-5 spacings"),
    Param("pass_tol", DECLARED, value=PASS_TOL, why="seal: |T - T_pred| <= 0.1"),
    Param("qw_pass_range", DECLARED, value=list(QW_PASS), why="seal: adjudicated band 0.1..0.5"),
    Param("B_kernel", DECLARED, value="exp(-qw eps_sp) (Poisson kernel), B=1 on Richardson primary",
          why="seal mt_B_kernel"),
])


def log(msg):
    with open(LOG, "a") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")


def seeds():
    out = {"lattice": M.seed_lattice(N)}
    for qw in QW:
        out[f"qw{qw}"] = M.seed_lattice_wave(N, qw, A, PHI)
    return out


def flows():
    t0 = time.time()
    solver_name, flow = solver_choice()
    log(f"flows: solver {solver_name}")
    roots, D = {}, {}
    for name, seed in seeds().items():
        def on_k(k, r, name=name, seed=seed):
            roots[f"{name}_k{k}"] = r.copy()
            D[f"{name}_k{k}"] = M.interlacing_D(seed, r) * N / k
        flow(seed, KS, on_k)
        log(f"  {name} flowed ({time.time()-t0:.0f}s)")
    os.makedirs(os.path.dirname(NPZ), exist_ok=True)
    np.savez(NPZ, **roots)
    json.dump({"solver": solver_name, "D_n_over_k": D, "runtime_s": time.time() - t0,
               "npz_sha256": M.sha256_of(NPZ)},
              open(os.path.join(HERE, "mt_flows.json"), "w"), indent=1)
    print(f"flows done in {time.time()-t0:.0f}s; max D n/k {max(D.values()):.4f}")


def _task(args):
    name, k = args
    M.TIS.CHUNK = 1024
    sd = seeds()[name]
    r = np.load(NPZ)[f"{name}_k{k}"]
    t0 = time.time()
    pos, diag = M.prod_positions(M.F_empirical(sd), r, N, k)
    pos["POPREF"], dpop = M.popref_positions(M.F_uniform, r, N, k)
    pos["RM1"] = M.rm1_positions(r)
    log(f"  refs {name} k={k}: prod iters {diag['sub_iters']} pop iters {dpop['sub_iters']} ({time.time()-t0:.0f}s)")
    return name, k, {a: v for a, v in pos.items()}, {"prod": diag, "popref": dpop}


def proj(v, idx, k, qw):
    theta = qw * (idx + 0.5 * k) + PHI
    w = hann(len(idx))
    return 1j * 2.0 * np.sum(w * v * np.exp(-1j * theta)) / np.sum(w)


def refs():
    t0 = time.time()
    tasks = [(name, k) for name in ["lattice"] + [f"qw{qw}" for qw in QW] for k in KS]
    with Pool(WORKERS) as p:
        res = p.map(_task, tasks)
    pos = {(n_, k): P for n_, k, P, _ in res}
    diag = {f"{n_}_k{k}": d for n_, k, _, d in res}
    rows = []
    for qw in QW:
        for k in KS:
            m = N - k
            bi = M.bulk_idx(m); idx = np.arange(m)[bi]
            xl = np.load(NPZ)[f"lattice_k{k}"]; xw = np.load(NPZ)[f"qw{qw}_k{k}"]
            raw = proj(((xw - xl) / local_spacing(xl))[bi], idx, k, qw)
            row = {"qw": qw, "k": k, "raw_gain": float(raw.real), "raw_gain_im": float(raw.imag),
                   "raw_gain_pred": float((1 - qw / np.pi) ** k), "arms": {}}
            eps_sp = M.eps_over_delta(N, k)
            for arm in ("PROD_PRIMARY", "PROD_BW1", "PROD_BW2", "POPREF", "RM1"):
                num = proj((pos[(f"qw{qw}", k)][arm] - pos[("lattice", k)][arm])[bi], idx, k, qw)
                T = num / raw
                B = {"PROD_PRIMARY": 1.0, "PROD_BW1": np.exp(-qw * eps_sp), "PROD_BW2": np.exp(-qw * 2 * eps_sp)}.get(arm)
                Tp = (1.0 - B * np.exp(k * (-np.log(1 - qw / np.pi) - qw / np.pi))) if B is not None else None
                row["arms"][arm] = {"T_re": float(T.real), "T_im": float(T.imag), "abs_T": float(abs(T)),
                                    "T_pred": (float(Tp) if Tp is not None else None), "B": (float(B) if B is not None else None),
                                    "dev": (float(abs(T - Tp)) if Tp is not None else None)}
            rows.append(row)
    prod_dom = [(r, a) for r in rows if QW_PASS[0] <= r["qw"] <= QW_PASS[1]
                for a in ("PROD_PRIMARY", "PROD_BW1", "PROD_BW2")]
    fails = [{"qw": r["qw"], "k": r["k"], "arm": a, **r["arms"][a]} for r, a in prod_dom if r["arms"][a]["dev"] > PASS_TOL]
    pop = [abs(r["arms"]["POPREF"]["T_re"] - 1 + 1j * r["arms"]["POPREF"]["T_im"]) for r in rows]
    rm1 = [r["arms"]["RM1"]["abs_T"] for r in rows if r["qw"] <= 0.1]
    macro = all(abs(r["arms"][a]["T_pred"] - 1) <= PASS_TOL for r, a in prod_dom)
    out = {"cell": "gate MT", "n": N, "A": A, "instrument": INSTRUMENT.seal(), "rows": rows,
           "reference_diag": diag, "n_fail": len(fails), "failures": fails,
           "worst_dev_prod_in_band": max(r["arms"][a]["dev"] for r, a in prod_dom),
           "POPREF_worst_abs_T_minus_1": max(pop), "POPREF_expected_ok": bool(max(pop) <= 0.02),
           "RM1_worst_abs_T_qw_le_0.1": (max(rm1) if rm1 else None), "RM1_expected_ok": bool(rm1 and max(rm1) <= 0.05),
           "T_pred_within_0.1_of_1_in_band": bool(macro),
           "GATE_MT": ("PASS" if not fails else "FAIL"), "runtime_s": time.time() - t0}
    out["REFERENCE_TOKEN"] = ("REFERENCE_IS_MACROSCOPIC" if (out["GATE_MT"] == "PASS" and macro)
                              else "REFERENCE_ABSORBS_AND_INJECTS")
    json.dump(out, open(os.path.join(HERE, "mt_transfer.json"), "w"), indent=1)
    print(f"GATE MT: {out['GATE_MT']} ({len(fails)} fails of {len(prod_dom)} in band; worst dev "
          f"{out['worst_dev_prod_in_band']:.4f}); POPREF |T-1| max {max(pop):.4f}; RM1 max|T| (qw<=0.1) "
          f"{out['RM1_worst_abs_T_qw_le_0.1']}; token {out['REFERENCE_TOKEN']}; runtime {out['runtime_s']:.0f}s")
    return out["GATE_MT"] == "PASS"


if __name__ == "__main__":
    open(LOG, "a").close()
    if sys.argv[1] == "flows":
        flows(); sys.exit(0)
    sys.exit(0 if refs() else 1)
