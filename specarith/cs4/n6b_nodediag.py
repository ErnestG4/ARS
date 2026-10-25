"""Round 83 node diagnostic on the settling pass (l6/N6-2_PLAN.md §10; a diagnostic, not a gate; asymmetric).

Points: at each r₀ ∈ {100, 300}, the 12 kernel points with the largest |kernel weight × ψ weight| (n6b_settle's frozen
local kernel; the (3, 3) piece's ψ weight is |c₃c₃| = 1, so the rule is the 12 largest kernel weights; the kernel's
(1 − r/G) slope breaks the k = ±6 tie towards k = −6). Computed: the (3, 3) piece by class at 6 in-window nodes
(distinct-node rule: 400 configurations per point, chunked), ℓ = 15.75, PMAX 10³, exactly as n6b_settle.task; the
4-node values are reused from the settling run (results/n6b/settle/tasks.tgz).

Reported per r₀: kernel-weighted partial sums over the 12 points of brute (Σ classes) and of the gap (brute − class 0)
at 4 and 6 nodes; their 4→6 changes; |ΔP_brute| as the sealed rule's 4-vs-6 quadrature-error estimate restricted to
these points. ARTIFACT iff |ΔP_gap| > 0.01·|P_brute(6)| at either r₀ (the settling pass is then recorded as a 4-node
artifact and N6-2 pauses); otherwise "no 4→6 movement at the dominant points" (no claim of convergence).

  python n6b_nodediag.py points                      the 24 selected (r₀, k)
  python n6b_nodediag.py jobs                        (r₀, k, chunk) task list
  python n6b_nodediag.py task R0 K C NQ OUT_DIR      one chunk → OUT_DIR/n_*.json
  python n6b_nodediag.py summary OUT_DIR SETTLE_TGZ  → OUT_DIR/NODEDIAG.json
"""
import glob
import json
import os
import sys
import tarfile
import time

import numpy as np

import n6b_extract as E
import n6b_settle as S

NQ6, NPTS, CH = 6, 12, 50                          # 400 configurations per point → 8 chunks of 50


def points():
    out = []
    for r0 in S.R0S:
        kk, r, w = S.local_weights(r0)
        top = np.argsort(-np.abs(w * 1.0), kind="stable")[:NPTS]       # ψ weight |c₃c₃| = 1 for the (3, 3) piece
        out += [(r0, int(kk[i])) for i in sorted(top)]
    return out


def _configs(nq):
    XA, WA = E._tuples(nq, 3)
    PA, PB = np.repeat(XA, len(XA), 0), np.tile(XA, (len(XA), 1))
    W = np.repeat(WA, len(XA)) * np.tile(WA, len(XA))
    return PA, PB, W


def jobs():
    n = len(_configs(NQ6)[2])
    return [(r0, k, c) for r0, k in points() for c in range((n + CH - 1) // CH)]


def task(r0, k, c, nq, out_dir):
    path = os.path.join(out_dir, f"n_{r0}_{k:+03d}_{nq}_{c:02d}.json")
    if os.path.exists(path):
        return 0
    r = r0 + k * S.DELTA
    PA, PB, W = _configs(nq)
    sl = slice(c * CH, (c + 1) * CH)
    PA, PB, W = PA[sl], PB[sl], W[sl]
    M = E.FilteredModel("zeta", S.ELL, pmax=S.PMAX)
    ds = [PA[:, j] for j in range(3)] + [PB[:, j] + r for j in range(3)]
    from ratios_t6 import guard
    guard(ds)
    t = time.time()
    cls = M.rho_cls(ds, {3, 4, 5})
    prod = np.real(M.rho([PA[:, j] for j in range(3)]) * M.rho([PB[:, j] for j in range(3)]))
    g = {str(q): [float(np.sum(W * np.real(v))), float(np.sum(W * np.imag(v)))] for q, v in cls.items()}
    g["0"][0] -= float(np.sum(W * prod))
    rec = dict(r0=r0, k=k, r=r, chunk=c, nq=nq, n=len(W), g=g, wall_s=round(time.time() - t, 1))
    tmp = f"{path}.{os.getpid()}.part"
    json.dump(rec, open(tmp, "w"))
    os.replace(tmp, path)
    print(r0, k, c, nq, rec["wall_s"], flush=True)
    return 0


def _bg(g):
    brute = sum(v[0] for v in g.values())
    return brute, brute - g["0"][0]


def summary(out_dir, settle_tgz):
    tf = tarfile.open(settle_tgz)
    s4 = {(d["r0"], d["k"]): d["g"] for d in (json.load(tf.extractfile(m)) for m in tf.getmembers())}
    n6 = len(_configs(NQ6)[2])
    res = dict(label="round 83 node diagnostic (not a gate; asymmetric)", points={})
    artifact = False
    for r0 in S.R0S:
        kk, r, w = S.local_weights(r0)
        wk = dict(zip(kk.tolist(), w.tolist()))
        sel = [k for rr, k in points() if rr == r0]
        P = {4: [0.0, 0.0], 6: [0.0, 0.0]}
        rows = []
        for k in sel:
            ch = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(out_dir, f"n_{r0}_{k:+03d}_6_*.json")))]
            assert sum(d["n"] for d in ch) == n6, (r0, k, "incomplete")
            g6 = {}
            for d in ch:
                for q, (a, b) in d["g"].items():
                    g6[q] = [g6.get(q, [0, 0])[0] + a, g6.get(q, [0, 0])[1] + b]
            b4, gap4 = _bg(s4[(r0, k)])
            b6, gap6 = _bg(g6)
            for n, (b, gp) in ((4, (b4, gap4)), (6, (b6, gap6))):
                P[n][0] += wk[k] * b
                P[n][1] += wk[k] * gp
            rows.append(dict(k=k, w=wk[k], brute4=b4, brute6=b6, gap4=gap4, gap6=gap6))
        d_b, d_g = P[6][0] - P[4][0], P[6][1] - P[4][1]
        hit = abs(d_g) > 0.01 * abs(P[6][0])
        artifact |= hit
        res["points"][str(r0)] = dict(selected_k=sel, weight_sum=float(sum(wk[k] for k in sel)), rows=rows,
                                      P_brute4=P[4][0], P_brute6=P[6][0], P_gap4=P[4][1], P_gap6=P[6][1],
                                      dP_brute=d_b, dP_gap=d_g, quad_err_4v6=abs(d_b),
                                      limit=0.01 * abs(P[6][0]), triggers=bool(hit))
        print(f"r0={r0}: P_brute 4/6 {P[4][0]:+.6f}/{P[6][0]:+.6f} (Δ {d_b:+.3e})  P_gap 4/6 {P[4][1]:+.3e}/{P[6][1]:+.3e} "
              f"(Δ {d_g:+.3e}; limit {0.01 * abs(P[6][0]):.3e})  {'TRIGGERS' if hit else 'no trigger'}")
    res["READING"] = "4-NODE ARTIFACT" if artifact else "no 4->6 movement at the dominant points"
    print("READING", res["READING"])
    json.dump(res, open(os.path.join(out_dir, "NODEDIAG.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "points":
        for p in points():
            print(*p)
        sys.exit(0)
    if sys.argv[1] == "jobs":
        for j in jobs():
            print(*j)
        sys.exit(0)
    if sys.argv[1] == "task":
        sys.exit(task(float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]))
    if sys.argv[1] == "summary":
        sys.exit(summary(sys.argv[2], sys.argv[3]))
