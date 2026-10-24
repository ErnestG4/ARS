"""n = 6 stage (c), round 78: the arithmetic part (ζ − U) of the fully connected 6-point term only (l6/N6_STAGE_C.md,
round 78 section, committed before running). Pilot first: r = 6 at 8 and 10 nodes, ζ and the U(N)-for-ζ null.

T₆ is the Ursell (truncated) function, from the ρ_m of all 63 nonempty subsets of the 3 + 3 points by Möbius inversion
over the 203 set partitions: T₆ = Σ_π (−1)^{|π|−1}(|π| − 1)! Π_{b∈π} ρ_{|b|}(x_b). Every other partition term of ρ₆ is a
product of T_m with m ≤ 5, i.e. through ρ₅, and stays out of scope. T₆ enters C(r) only through the (3, 3) piece, with
coefficient c₃c₃ = 1: ΔC₆(r) = ∫_{A³×B³} (T₆^ζ − T₆^U).

Phase classes: ρ_m of a subset is split by n6b_extract.FilteredModel.rho_cls into classes cB (net cluster-B count);
phases multiply under products, so classes add (Laurent convolution). The envelope E(r) = Σ_k |ΔT₆,k| keeps the round-77
phase-robust bound.

U(N)-for-ζ null: the ζ slot gets U(N) at N = 10⁵ by the exact determinant det[K(x_i, x_j)] for every subset (an
independent route); the U slot is the ratios construction as in the real comparison. A planted witness (ρ₆ of the
determinant slot × (1 + 10⁻⁸), pushed through the same Möbius sum) must be detected at its known size.

  python n6c_conn.py task KIND ELL PMAX R NQ CHUNK OUT_DIR
  python n6c_conn.py jobs                    the declared pilot task list
  python n6c_conn.py summary_pilot OUT_DIR   → OUT_DIR/N6C_PILOT.json
  python n6c_conn.py selftest                Möbius vs the determinantal cycle formula (local; not a gate)
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

CHUNK = 16
N_U = 100_000
KMAX = 3
PILOT = [("zeta", 15.75, 100, 6.0, 8), ("zeta", 15.75, 100, 6.0, 10), ("U", 0.0, 0, 6.0, 8), ("U", 0.0, 0, 6.0, 10)]
PLANT = 1e-8             # ρ₆ ≈ 7·10² integrated ⇒ planted ≈ 7·10⁻⁶, about the per-r allowance
NULL_TOL = 4e-7            # 10% of the per-r allowance 4.1e-6 = 3.3e-4 / (2·40)
CONV_REL, CONV_ABS = 0.2, 4e-7


def set_partitions(items):
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for p in set_partitions(rest):
        yield [[first]] + p
        for i in range(len(p)):
            yield p[:i] + [[first] + p[i]] + p[i + 1:]


PARTS = [(sorted(tuple(b) for b in p), (-1) ** (len(p) - 1) * math.factorial(len(p) - 1)) for p in set_partitions(list(range(6)))]
SUBSETS = [s for m in range(1, 7) for s in itertools.combinations(range(6), m)]


def _multisets(nq):
    """The product Gauss–Legendre rule on [0, 4]³ folded by symmetry: sorted node multisets i ≤ j ≤ k, weight
    (3!/Π mult!)·Π w. Unlike E._tuples (distinct nodes only), it keeps the in-cluster diagonal, where T₆ ≠ 0."""
    x, w = np.polynomial.legendre.leggauss(nq)
    x, w = 2 * (x + 1), 2 * w
    T = list(itertools.combinations_with_replacement(range(nq), 3))
    I = np.array(T)
    W = np.array([math.factorial(3) / np.prod([math.factorial(t.count(v)) for v in set(t)]) * np.prod(w[list(t)]) for t in T])
    return x[I], I, W


def configs(nq):
    XA, IA, WA = _multisets(nq)
    m = len(WA)
    PA, PB = np.repeat(XA, m, 0), np.tile(XA, (m, 1))
    IAx, IBx = np.repeat(IA, m, 0), np.tile(IA, (m, 1))
    W = np.repeat(WA, m) * np.tile(WA, m)
    return PA, PB, W, IAx, IBx


def valid(s, IA, IB):
    """Rows where the subset s has no repeated node within a cluster (else its ρ is exactly 0: ρ_m ∝ d² at coincidence)."""
    ok = np.ones(len(IA), bool)
    for a, b in itertools.combinations(s, 2):
        if (a < 3) == (b < 3):
            Ia, Ib = (IA[:, a], IA[:, b]) if a < 3 else (IB[:, a - 3], IB[:, b - 3])
            ok &= Ia != Ib
    return ok


def mobius_cls(rho):
    """rho: {subset: array (n, 2·KMAX + 1) of class parts, class k at index k + KMAX} → T₆ by class, same shape."""
    n = next(iter(rho.values())).shape[0]
    out = np.zeros((n, 2 * KMAX + 1), complex)
    for blocks, mu in PARTS:
        acc = None
        for b in blocks:
            f = rho[b]
            if acc is None:
                acc = f.copy()
                continue
            new = np.zeros_like(acc)
            for i in range(2 * KMAX + 1):
                for j in range(2 * KMAX + 1):
                    k = i + j - KMAX
                    if 0 <= k <= 2 * KMAX and np.any(f[:, j]):
                        new[:, k] += acc[:, i] * f[:, j]
            acc = new
        out += mu * acc
    return out


def mobius(rho):
    """rho: {subset: array (n,)} → T₆ (n,)."""
    out = 0.0
    for blocks, mu in PARTS:
        out = out + mu * np.prod([rho[b] for b in blocks], axis=0)
    return out


def _cls_array(d, n):
    a = np.zeros((n, 2 * KMAX + 1), complex)
    for k, v in d.items():
        a[:, k + KMAX] = np.broadcast_to(v, (n,))
    return a


def tname(kind, ell, pmax, r, nq, c):
    return f"t_{kind}_{ell}_{pmax}_{r}_{nq}_{c:04d}.json"


def task(kind, ell, pmax, r, nq, c, out_dir):
    path = os.path.join(out_dir, tname(kind, ell, pmax, r, nq, c))
    if os.path.exists(path):
        return 0
    PA, PB, W, IA, IB = configs(nq)
    sl = slice(c * CHUNK, (c + 1) * CHUNK)
    PA, PB, W, IA, IB = PA[sl], PB[sl], W[sl], IA[sl], IB[sl]
    n = len(W)
    pts = [PA[:, k] for k in range(3)] + [PB[:, k] + r for k in range(3)]
    from ratios_t6 import guard
    M = E.FilteredModel(kind, N_U if kind == "U" else ell, pmax=pmax if kind == "zeta" else None)
    t = time.time()
    rho = {}
    for s in SUBSETS:
        ok = valid(s, IA, IB)
        rho[s] = np.zeros((n, 2 * KMAX + 1), complex)
        if ok.any():
            ds = [pts[i][ok] for i in s]
            if len(s) > 1:
                guard(ds)
            cl = {j for j, i in enumerate(s) if i >= 3}
            rho[s][ok] = _cls_array(M.rho_cls(ds, cl), int(ok.sum()))
    T6 = mobius_cls(rho)
    g = {str(k - KMAX): [float(np.sum(W * T6[:, k].real)), float(np.sum(W * T6[:, k].imag))] for k in range(2 * KMAX + 1)}
    rec = dict(kind=kind, ell=ell, pmax=pmax, r=r, nq=nq, chunk=c, n=n, g=g,
               rho6=float(np.sum(W * rho[SUBSETS[-1]].sum(1).real)))
    if kind == "U":
        rd = {s: E._det_rho(np.stack([pts[i] for i in s], -1), N_U) for s in SUBSETS}
        rec["det_T6"] = float(np.sum(W * mobius(rd)))
        rec["det_rho6"] = float(np.sum(W * rd[SUBSETS[-1]]))
        rd[SUBSETS[-1]] = rd[SUBSETS[-1]] * (1 + PLANT)
        rec["det_T6_planted"] = float(np.sum(W * mobius(rd)))
    rec["wall_s"] = round(time.time() - t, 1)
    tmp = path + ".part"
    json.dump(rec, open(tmp, "w"))
    os.replace(tmp, path)
    print(kind, ell, pmax, r, nq, c, rec["wall_s"], flush=True)
    return 0


def jobs():
    out = []
    for kind, ell, pmax, r, nq in PILOT:
        nc = (len(configs(nq)[2]) + CHUNK - 1) // CHUNK
        out += [(kind, ell, pmax, r, nq, c) for c in range(nc)]
    return sorted(out, key=lambda j: (j[0] != "zeta", -j[4]))       # the slow ζ 10-node chunks first


def _collect(out_dir):
    acc = {}
    for p in glob.glob(os.path.join(out_dir, "t_*.json")):
        d = json.load(open(p))
        a = acc.setdefault((d["kind"], d["ell"], d["pmax"], d["r"], d["nq"]), {"n": 0, "g": {}, "s": {}})
        a["n"] += d["n"]
        for k, (re_, im_) in d["g"].items():
            a["g"][k] = a["g"].get(k, 0j) + complex(re_, im_)
        for f in ("rho6", "det_T6", "det_rho6", "det_T6_planted"):
            if f in d:
                a["s"][f] = a["s"].get(f, 0.0) + d[f]
    return acc


def summary_pilot(out_dir):
    acc = _collect(out_dir)
    for kind, ell, pmax, r, nq in PILOT:
        got = acc.get((kind, ell, pmax, r, nq), {"n": 0})["n"]
        assert got == len(configs(nq)[2]), f"incomplete: {(kind, ell, pmax, r, nq)} {got}"
    res = dict(label="round 78 stage (c) pilot: arithmetic part of the connected T6 (N6_STAGE_C.md, round 78)", nodes={})
    for nq in (8, 10):
        z, u = acc[("zeta", 15.75, 100, 6.0, nq)], acc[("U", 0.0, 0, 6.0, nq)]
        dg = {k: z["g"][k] - u["g"][k] for k in z["g"]}
        I_rat = sum(u["g"].values()).real
        null_res = u["s"]["det_T6"] - I_rat
        plant_res = u["s"]["det_T6_planted"] - I_rat
        plant_exp = PLANT * u["s"]["det_rho6"]
        res["nodes"][str(nq)] = dict(
            E=float(sum(abs(v) for v in dg.values())), dI=float(sum(dg.values()).real),
            dg={k: [v.real, v.imag] for k, v in dg.items()},
            T6_zeta=float(sum(z["g"].values()).real), T6_U=I_rat, rho6_zeta=z["s"]["rho6"], rho6_U=u["s"]["rho6"],
            null=dict(T6_det=u["s"]["det_T6"], residual=null_res, tol=NULL_TOL, PASS=bool(abs(null_res) <= NULL_TOL)),
            witness=dict(planted_expected=plant_exp, planted_measured=plant_res - null_res,
                         fires=bool(abs(plant_res) > NULL_TOL),
                         size_ok=bool(abs((plant_res - null_res) - plant_exp) <= 0.1 * abs(plant_exp))))
    n8, n10 = res["nodes"]["8"], res["nodes"]["10"]
    conv = {q: dict(v8=n8[q], v10=n10[q], ok=bool(abs(n8[q] - n10[q]) <= CONV_REL * abs(n10[q]) + CONV_ABS))
            for q in ("E", "dI")}
    res["convergence"] = conv
    res["CONVERGES"] = bool(all(c["ok"] for c in conv.values()))
    res["NULL_PASSES"] = bool(all(res["nodes"][q]["null"]["PASS"] and res["nodes"][q]["witness"]["fires"]
                                  and res["nodes"][q]["witness"]["size_ok"] for q in ("8", "10")))
    res["FULL_RUN_ALLOWED"] = bool(res["CONVERGES"] and res["NULL_PASSES"])
    res["B6_from_r6_only"] = 2.0 * 40.0 * n10["E"]          # descriptive: as if r = 6 were the maximum; not a bound
    json.dump(res, open(os.path.join(out_dir, "N6C_PILOT.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "nodes"}, indent=1))
    for q in ("8", "10"):
        v = res["nodes"][q]
        print(q, "E", f"{v['E']:.4e}", "dI", f"{v['dI']:+.4e}", "null", v["null"], "witness", v["witness"])
    return 0


def selftest():
    """Möbius over 203 partitions against the determinantal cycle formula T₆ = −Σ_{6-cycles} Π K (U(N), N = 10⁵)."""
    rng = np.random.default_rng(78)
    P = np.sort(rng.uniform(0, 3, (5, 6)), 1)
    X = P[:, :, None] - P[:, None, :]
    K = np.ones_like(X)
    nz = np.abs(X) > 1e-15
    K[nz] = np.sin(np.pi * X[nz]) / (N_U * np.sin(np.pi * X[nz] / N_U))
    cyc = np.zeros(len(P))
    for perm in itertools.permutations(range(1, 6)):
        seq = (0,) + perm
        cyc += np.prod([K[:, seq[i], seq[(i + 1) % 6]] for i in range(6)], axis=0)
    T_cycle = (-1) ** 5 * cyc
    rd = {s: E._det_rho(P[:, list(s)], N_U) for s in SUBSETS}
    T_mob = mobius(rd)
    print("partitions", len(PARTS), "Σμ·(1)", sum(mu for _, mu in PARTS))
    print("T6 cycle", T_cycle, "\nT6 mobius", T_mob, "\nmax abs diff", np.abs(T_cycle - T_mob).max())
    # class bookkeeping: the class-summed Möbius equals the plain Möbius on the summed classes
    M = E.FilteredModel("U", N_U)
    pts = [P[:2, i] for i in range(3)] + [P[:2, i + 3] + 6.0 for i in range(3)]
    rho = {s: _cls_array(M.rho_cls([pts[i] for i in s], {j for j, i in enumerate(s) if i >= 3}), 2) for s in SUBSETS}
    a = mobius_cls(rho).sum(1)
    b = mobius({s: v.sum(1) for s, v in rho.items()})
    dd = {s: E._det_rho(np.stack([pts[i] for i in s], -1), N_U) for s in SUBSETS}
    print("class-summed vs plain Möbius", np.abs(a - b).max(), " construction vs det T6", a.real, mobius(dd))
    return 0


def _K(x, y):
    X = x[:, None] - y[None, :]
    out = np.ones_like(X)
    nz = np.abs(X) > 1e-15
    out[nz] = np.sin(np.pi * X[nz]) / (N_U * np.sin(np.pi * X[nz] / N_U))
    return out


def T_trace(i, j, r, nq):
    """∫_{A^i×B^j} T_{i+j} for U(N) by the full product GL rule and the determinantal cycle formula (cyclic traces)."""
    x, w = np.polynomial.legendre.leggauss(nq)
    xa, wa = 2 * (x + 1), 2 * w
    xb, wb = xa + r, wa
    sq = {"A": np.sqrt(wa), "B": np.sqrt(wb)}
    pt = {"A": xa, "B": xb}
    blk = {(u, v): sq[u][:, None] * _K(pt[u], pt[v]) * sq[v][None, :] for u in "AB" for v in "AB"}
    m, tot = i + j, 0.0
    for pos in itertools.combinations(range(m), i):
        wd = ["A" if t in pos else "B" for t in range(m)]
        P = np.eye(nq)
        for t in range(m):
            P = P @ blk[(wd[t], wd[(t + 1) % m])]
        tot += np.trace(P)
    return (-1) ** (m - 1) * math.factorial(i) * math.factorial(j) / m * tot


def quadtest(r=6.0):
    """The folded multiset rule (Möbius on determinant ρ's) against the product-rule trace formula; and the converged
    reference (24 nodes). Local, not a gate."""
    for nq in (6, 8, 10):
        PA, PB, W = configs(nq)[:3]
        pts = [PA[:, k] for k in range(3)] + [PB[:, k] + r for k in range(3)]
        rd = {s: E._det_rho(np.stack([pts[i] for i in s], -1), N_U) for s in SUBSETS}
        print(nq, "multiset", float(np.sum(W * mobius(rd))), "trace", T_trace(3, 3, r, nq), flush=True)
    print("reference (24 nodes, trace)", T_trace(3, 3, r, 24))
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "task":
        sys.exit(task(sys.argv[2], float(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]), int(sys.argv[6]),
                      int(sys.argv[7]), sys.argv[8]))
    if sys.argv[1] == "jobs":
        for j in jobs():
            print(*j)
        sys.exit(0)
    if sys.argv[1] == "summary_pilot":
        sys.exit(summary_pilot(sys.argv[2]))
    if sys.argv[1] == "quadtest":
        sys.exit(quadtest())
    if sys.argv[1] == "selftest":
        sys.exit(selftest())
