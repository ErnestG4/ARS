"""Phase 6 detection floor (DESCRIPTIVE, post-seal; Will 2026-10-07). Not a gate; changes no sealed verdict.

The red paths show gross errors fire. This asks how SMALL an error the exact identity bar catches: perturb one term or
weight family of the sealed RHS by a relative amount eps (or shift one prime's line by delta in tau) and find, by
bisection on |eps|, the smallest perturbation for which max_tau |LHS - RHS'| / eps_tol(tau) > 1 (the gate would FAIL).
Both signs are tried; the smaller magnitude is reported.

LHS: the sealed statistic recomputed exactly (compensated sums) on the sealed inputs; RHS and tolerance: the sealed
pre-read (results/preread_proposed). Usage: python detection_floor.py ZEROS1 MAASS_CSV CHI4_ZEROS OUT.json
"""
import json
import math
import os
import sys

import numpy as np

import classes
import ph6lib as L
from preread import load_maass

HERE = os.path.dirname(os.path.abspath(__file__))
PRE = os.path.join(HERE, "results", "preread_proposed")


def floor(res, eps_tol, delta_rhs_of):
    """Smallest |x| with max |res - delta_rhs_of(x)| / eps_tol > 1, over both signs (log-bisection on [1e-14, 1])."""
    best = None
    for sgn in (1.0, -1.0):
        f = lambda x: float(np.max(np.abs(res - delta_rhs_of(sgn * x)) / eps_tol))
        lo, hi = 1e-14, 1.0
        if f(hi) <= 1:
            continue
        if f(lo) > 1:
            return lo
        for _ in range(60):
            mid = math.sqrt(lo * hi)
            lo, hi = (mid, hi) if f(mid) <= 1 else (lo, mid)
        best = hi if best is None else min(best, hi)
    return best


def dirichlet_rows(name, cfg, levels, q, chi, a):
    pre = np.load(os.path.join(PRE, f"rhs_{name}.npz"))
    taus, rhs, tol = pre["taus"], pre["rhs"], pre["eps"]
    import time
    cache = os.path.join(HERE, "results", f"_lhs_cache_{name}.npy")
    t0 = time.time()
    if os.path.exists(cache):
        lhs = np.load(cache)
    else:
        S, M = L.zero_sums(cfg, levels, taus, exact=True)
        lhs = S + M
        np.save(cache, lhs)
    print(name, "LHS", round(time.time() - t0, 1), "s", flush=True)
    res = lhs - rhs
    lam = L.mangoldt_upto(10000)
    w = lambda n: lam[n] / math.sqrt(n) * (1.0 if chi is None else float(chi(np.array([n]))[0]))
    line = lambda n, x=0.0: w(n) * (L.g_zero_line(cfg, taus, math.log(n) + x) + L.g_zero_line(cfg, taus, -math.log(n) - x))
    R = L.rhs_dirichlet(cfg, taus, q, chi, a)
    P_all = R["prime"]
    def nonprime(n):                   # prime powers p^k with k >= 2 (its own Lambda table: the tail reaches n_tail)
        lam_n = L.mangoldt_upto(int(np.max(n)))
        return np.array([1.0 if (lam_n[k] > 0 and round(math.exp(lam_n[k])) != k) else 0.0 for k in np.asarray(n)])
    P_k2 = L.prime_sum_dirichlet(cfg, taus, chi=(lambda n: nonprime(n) * (1.0 if chi is None else chi(n))))[0]
    rows = {"base_max_ratio": float(np.max(np.abs(res) / tol)),
            "all prime-power weights x(1+eps)": floor(res, tol, lambda e: -e * P_all),
            "k>=2 harmonics x(1+eps)": floor(res, tol, lambda e: -e * P_k2)}
    for p in (2, 3, 89):
        if w(p) != 0:
            rows[f"weight of p={p} x(1+eps)"] = floor(res, tol, lambda e, p=p: -e * line(p))
            rows[f"line of p={p} shifted by delta (tau units)"] = floor(res, tol, lambda d, p=p: -(line(p, d) - line(p)))
    if name.startswith(("G0s", "G2s")):
        rows["Gamma term x(1+eps)"] = floor(res, tol, lambda e: e * R["gamma"])
        if q == 1:
            rows["pole term x(1+eps)"] = floor(res, tol, lambda e: e * R["pole"])
    rows["line width 1/sigma (tau units)"] = 1 / cfg.sigma
    return rows


def maass_rows(name, cfg, r_even, r_odd, ch, cg):
    out = {}
    for sector, rl in (("even", r_even), ("odd", r_odd)):
        pre = np.load(os.path.join(PRE, f"rhs_{name}_{sector}.npz"))
        taus, rhs, tol = pre["taus"], pre["rhs"], pre["eps"]
        res = L.maass_sector_sum(cfg, rl, taus, sector == "even") - rhs
        Rs = L.rhs_selberg(cfg, taus, sector, ch, cg)
        rows = {"base_max_ratio": float(np.max(np.abs(res) / tol))}
        for term in ("elliptic", "glide", "hyperbolic", "ident", "prime"):
            if term in Rs and np.max(np.abs(Rs[term])) > 0:
                rows[f"{term} term x(1+eps)"] = floor(res, tol, lambda e, t=term: e * Rs[t])
        out[sector] = rows
    return out


def main(zeros1, maass, chi4, out_path):
    tab = json.load(open(os.path.join(PRE, "preread_tables.json")))
    C = {k: L.Config(**v) for k, v in tab["configs"].items()}
    z = np.loadtxt(zeros1)
    zc = np.array([float(x) for x in open(chi4).read().split()])
    rE, rO = load_maass(maass)
    _, ls = classes.pari_counts(30, 30)
    ch = {t: ls[("h", t)] / 2 for (k, t) in ls if k == "h"}
    cg = {t: ls[("g", t)] for (k, t) in ls if k == "g"}
    res = {}
    for name, levels, q, chi, a in (("G0", z, 1, None, 0), ("G0s_a", z, 1, None, 0), ("G0c", z[:30000], 1, None, 0),
                                    ("G2", zc, 4, L.chi4, 1), ("G2s_a", zc, 4, L.chi4, 1)):
        res[name] = dirichlet_rows(name, C[name], levels, q, chi, a)
        print(name, json.dumps(res[name]), flush=True)
    for name in ("G1", "G1s_a", "G1s_b"):
        res[name] = maass_rows(name, C[name], rE, rO, ch, cg)
        print(name, json.dumps(res[name]), flush=True)
    with open(out_path, "w") as f:
        json.dump(res, f, indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:5])
