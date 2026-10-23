"""n = 6 stage (c): the bound on the arithmetic n = 6 short-range correction to corrected (B)'s block variance (round 77:
6 nodes plus an 8-node convergence check; l6/N6_STAGE_C_BOUND.md, amended in l6/N6_STAGE_C.md before running).

The (3, 3) piece I₃₃(r) = ∫_{A³×B³} [ρ₆ − ρ₃ρ₃] (A = [0, 4), B = [r, r + 4); the only place ρ₆ enters C(r)) is computed
by phase class k (cB = −3 … 3; n6b_extract.FilteredModel.rho_cls) for ζ and for U(N) (N = 10⁵, the sine-kernel
stand-in) at identical in-window Gauss–Legendre nodes (6 per coordinate; distinct sorted tuples × 3!²). The arithmetic
correction per class is Δg_k = g_k^ζ − g_k^U, and the envelope E(r) = Σ_k |Δg_k(r)| bounds |ΔI₃₃| at every phase of
the carrier. Then ΔW₆ ≤ Δ·(1 + 2·(R₀/Δ − 1))·max_r E ≈ 40·max_r E (R₀ = 20, Δ = 1/8).

  python n6c_bound.py task KIND ELL PMAX R NQ CHUNK OUT_DIR     one chunk of 16 configurations → OUT_DIR/t_*.json
  python n6c_bound.py jobs                                       print the declared task list
  python n6c_bound.py summary OUT_DIR                            → OUT_DIR/N6C_BOUND.json
"""
import glob
import itertools
import json
import math
import os
import sys
import time

import numpy as np

import n6b_extract as E

R_GRID = [0.27, 1.17, 2.07, 3.46, 4.0, 6.0, 10.0, 20.0]      # small r chosen so 6-node grids stay ≥ 0.22 apart
CHUNK = 16
N_U = 100_000
# (kind, ℓ, pmax, r-list, nq), declared before running (l6/N6_STAGE_C.md, round 77)
CASES = ([("zeta", 15.75, 100, R_GRID, 6), ("zeta", 15.75, 300, R_GRID, 6), ("zeta", 21.75, 100, R_GRID, 6),
          ("zeta", 15.75, 1000, [2.07, 10.0], 6), ("U", 0.0, 0, R_GRID, 6),
          ("zeta", 15.75, 100, [6.0], 8), ("U", 0.0, 0, [6.0], 8)])
W_CUE = 0.211089                                            # stage (a), κ₃ units, G = 10⁴ (flat to 0.05%)
R_ZETA = {300: 0.315, 1000: 0.209, 3000: 0.183, 10000: 0.157}


def configs(nq):
    XA, WA = E._tuples(nq, 3)
    PA = np.repeat(XA, len(XA), 0)
    PB = np.tile(XA, (len(XA), 1))
    W = np.repeat(WA, len(XA)) * np.tile(WA, len(XA))
    return PA, PB, W


def jobs():
    out = []
    for kind, ell, pmax, rs, nq in CASES:
        n = len(configs(nq)[2])
        for r in rs:
            for c in range((n + CHUNK - 1) // CHUNK):
                out.append((kind, ell, pmax, r, nq, c))
    return out


def tname(kind, ell, pmax, r, nq, c):
    return f"t_{kind}_{ell}_{pmax}_{r}_{nq}_{c:04d}.json"


def task(kind, ell, pmax, r, nq, c, out_dir):
    path = os.path.join(out_dir, tname(kind, ell, pmax, r, nq, c))
    if os.path.exists(path):
        return 0
    PA, PB, W = configs(nq)
    sl = slice(c * CHUNK, (c + 1) * CHUNK)
    PA, PB, W = PA[sl], PB[sl], W[sl]
    L = N_U if kind == "U" else ell
    M = E.FilteredModel(kind, L, pmax=pmax if kind == "zeta" else None)
    ds = [PA[:, k] for k in range(3)] + [PB[:, k] + r for k in range(3)]
    from ratios_t6 import guard
    guard(ds)
    t = time.time()
    cls = M.rho_cls(ds, {3, 4, 5})
    prod = np.real(M.rho([PA[:, k] for k in range(3)]) * M.rho([PB[:, k] for k in range(3)]))
    g = {str(k): [float(np.sum(W * np.real(v))), float(np.sum(W * np.imag(v)))] for k, v in cls.items()}
    g["0"][0] -= float(np.sum(W * prod))
    rec = dict(kind=kind, ell=ell, pmax=pmax, r=r, nq=nq, chunk=c, n=int(len(W)), g=g, wall_s=round(time.time() - t, 1))
    tmp = path + ".part"
    json.dump(rec, open(tmp, "w"))
    os.replace(tmp, path)
    print(rec["kind"], ell, pmax, r, nq, c, rec["wall_s"], flush=True)
    return 0


def _collect(out_dir):
    acc = {}
    for p in glob.glob(os.path.join(out_dir, "t_*.json")):
        d = json.load(open(p))
        key = (d["kind"], d["ell"], d["pmax"], d["r"], d["nq"])
        a = acc.setdefault(key, {"n": 0})
        a["n"] += d["n"]
        for k, (re_, im_) in d["g"].items():
            a.setdefault(k, 0j)
            a[k] += complex(re_, im_)
    return acc


def summary(out_dir):
    acc = _collect(out_dir)
    for kind, ell, pmax, rs, nq in CASES:
        need = len(configs(nq)[2])
        for r in rs:
            got = acc.get((kind, ell, pmax, r, nq), {"n": 0})["n"]
            assert got == need, f"incomplete: {(kind, ell, pmax, r, nq)} {got}/{need}"

    def env(ell, pmax, r, nq):
        z = acc[("zeta", ell, pmax, r, nq)]
        u = acc[("U", 0.0, 0, r, nq)]
        ks = sorted({k for k in z if k != "n"} | {k for k in u if k != "n"}, key=int)
        dg = {k: z.get(k, 0j) - u.get(k, 0j) for k in ks}
        return float(sum(abs(v) for v in dg.values())), {k: [v.real, v.imag] for k, v in dg.items()}

    rows = {}
    for ell, pmax in ((15.75, 100), (15.75, 300), (21.75, 100)):
        rows[f"{ell}_{pmax}"] = {str(r): env(ell, pmax, r, 6)[0] for r in R_GRID}
    trend = {str(r): dict(E300=env(15.75, 300, r, 6)[0], E1000=env(15.75, 1000, r, 6)[0]) for r in (2.07, 10.0)}
    for v in trend.values():
        v["rel_change"] = abs(v["E1000"] - v["E300"]) / max(v["E300"], 1e-300)
    E6, E8 = env(15.75, 100, 6.0, 6)[0], env(15.75, 100, 6.0, 8)[0]
    conv = dict(E6=E6, E8=E8, ratio=E8 / E6)
    maxE = max(max(v.values()) for v in rows.values())
    maxE = max(maxE, max(v["E1000"] for v in trend.values()))
    established = (0.5 <= conv["ratio"] <= 2.0) and all(v["rel_change"] <= 0.30 for v in trend.values())
    B6 = 2.0 * max(1.0, conv["ratio"]) * 40.0 * maxE
    thr = {str(G): 0.01 * R * W_CUE for G, R in R_ZETA.items()}
    res = dict(R_GRID=R_GRID, envelope=rows, cutoff_trend=trend, convergence=conv, max_envelope=maxE, B6=B6,
               threshold=thr, established=bool(established),
               negligible=bool(established and all(B6 <= t for t in thr.values())),
               label="round 77 stage (c) bound (6 nodes + 8-node check); envelope over phase classes")
    json.dump(res, open(os.path.join(out_dir, "N6C_BOUND.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "envelope"}, indent=1))
    for k, v in rows.items():
        print(k, {r: f"{e:.3e}" for r, e in v.items()})
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "task":
        sys.exit(task(sys.argv[2], float(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]), int(sys.argv[6]),
                      int(sys.argv[7]), sys.argv[8]))
    if sys.argv[1] == "jobs":
        for j in jobs():
            print(*j)
        sys.exit(0)
    if sys.argv[1] == "summary":
        sys.exit(summary(sys.argv[2]))
