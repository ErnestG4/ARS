"""RQ1 POST-HOC conductor-scaling collapse (round 92; descriptive, no verdict). Runs on the already-read archives.

The heuristic's field dependence enters only through 2 log k + C_F, so in the continuum R_ℤ[√2](K) = R_ℤ[i](a·K) with
a = e^{ΔC/2} = π/(√2·log(1 + √2)) ≈ 2.5204 (checked on the heuristic formula: |R_ℤ[√2](K) − R_ℤ[i](aK)| ≤ 1.2·10⁻³ at
β = 0.20 and ≤ 2.3·10⁻⁵ for β ≥ 0.40, against offsets of 0.003–0.09). Here, per X ∈ {10¹⁰, 10¹¹} at the read's matched N:
  R_ℤ[√2](K) and R_ℤ[i](K), K = round(N^β), and R_ℤ[i](a·K) (window 1/(aK), not rounded), β = 0.20, 0.21, …, 0.70.
  residual(β) = R_ℤ[√2](K) − R_ℤ[i](aK), SE from the sealed model (c = 0.627, each term at its own K; independent fields).
  D(β) = R_ℤ[√2](K) − R_ℤ[i](K) against R′_ℤ[i](β)·log a / log N (R′ = dR/dβ by central differences on the grid; first
  order) and against R_ℤ[i](aK) − R_ℤ[i](K) (the same shift without the linearisation).
The read's own loader (rq1_read.load_field: each loaded segment's sha256 against the manifest) and estimator
(rq1_read.var_stream) are used; the read's cells (β 0.20, 0.30, 0.40, 0.45, 0.50, …, 0.70) must reproduce read1.json.
Passes run in a thread pool (var_stream is nogil) over one shared sorted array; one field in memory at a time.

Cost model (round 84; N6-2_PLAN §10 form): a pass costs 1.6·10⁻⁸ s per point locally × 2.3 on spot; a field load
(hash, angles, sort) 204 s × N/N₁₁ (measured on spot). 153 passes per X: ≈ 0.71 spot core-h at 10¹⁰ and 6.4 at 10¹¹,
≈ 7.4 with loads. After every stage the cumulative CPU is compared with the cumulative model; above 1.25× the run
writes STOPPED and exits 3 before the next stage (first-wave rule, and the round-88 mid-run check).

  python rq1_collapse.py ZS2_DIR ZI_DIR OUT_DIR
"""
import json
import math
import os
import platform
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np

import rq1_read as Q

A = math.pi / (math.sqrt(2) * math.log(1 + math.sqrt(2)))
BETAS = [round(0.20 + 0.01 * i, 2) for i in range(51)]
NT = int(os.environ.get("COLLAPSE_THREADS", "16"))
PASS_S, SPOT, LOAD_S11, N11 = 1.6e-8, 2.3, 204.0, 4118052228
LIMIT = 1.25


def se_rel(K):
    return math.sqrt(2 / (Q.C_SE * K))


def passes(th, Ks, pool):
    N = len(th)
    return list(pool.map(lambda K: Q.var_stream(th, K) / (N / K), Ks))


def main(zs2, zi, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    res = dict(label="RQ1 POST-HOC conductor-scaling collapse (round 92); descriptive, no verdict", a=A, betas=BETAS,
               threads=NT, kernel=platform.release(), cost=[], rows={})
    model = 0.0
    with ThreadPoolExecutor(NT) as pool:
        for X in Q.XS:
            n = Q.n_below(zs2, X)
            N = 2 * n
            K = [int(round(N ** b)) for b in BETAS]
            aK = [A * k for k in K]
            t0 = time.time()
            got = {}
            for f, d, Ks in (("zs2", zs2, K), ("zi", zi, K + aK)):
                th = Q.load_field(d, f, n)
                got[f] = passes(th, Ks, pool)
                del th
                model += len(Ks) * PASS_S * N * SPOT + LOAD_S11 * N / N11
                cpu = time.process_time()
                res["cost"].append(dict(stage=f"{X:.0e} {f}", cpu_s=cpu, model_cpu_s=model, ratio=cpu / model,
                                        wall_s=time.time() - t0))
                print(res["cost"][-1], flush=True)
                if cpu > LIMIT * model:
                    json.dump(res, open(os.path.join(out_dir, "COLLAPSE_PARTIAL.json"), "w"), indent=1)
                    open(os.path.join(out_dir, "STOPPED"), "w").write(f"cost {cpu / model:.2f}x the model at {f} {X:.0e}\n")
                    return 3
            r2, riK, riaK = got["zs2"], got["zi"][:len(K)], got["zi"][len(K):]
            dRi = np.gradient(np.array(riK), np.array(BETAS))
            rows = []
            for i, b in enumerate(BETAS):
                se_res = math.hypot(r2[i] * se_rel(K[i]), riaK[i] * se_rel(aK[i]))
                rows.append(dict(beta=b, K=K[i], aK=aK[i], R_zs2=r2[i], R_zi=riK[i], R_zi_aK=riaK[i],
                                 residual=r2[i] - riaK[i], SE_residual=se_res, residual_over_SE=(r2[i] - riaK[i]) / se_res,
                                 D=r2[i] - riK[i], SE_D=Q.se_diff(r2[i], riK[i], K[i]), dR_zi_dbeta=float(dRi[i]),
                                 D_pred_first_order=float(dRi[i]) * math.log(A) / math.log(N),
                                 D_pred_shift=riaK[i] - riK[i]))
            res["rows"][str(X)] = dict(n_split=n, N=N, log_a_over_log_N=math.log(A) / math.log(N), rows=rows)
    res["cpu_core_h"] = time.process_time() / 3600
    json.dump(res, open(os.path.join(out_dir, "COLLAPSE.json"), "w"), indent=1)
    print("done", res["cpu_core_h"], "core-h")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
