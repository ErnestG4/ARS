"""Follow-up candidate (A), FOLLOWUP_SELECTION_RULE.md + amendment 1 (rounds 48–49): the next-nearest-neighbour spacing
law. Data-free.

With T_n(s) = (1/(n−2)!)∫_{[0,s]^{n−2}} ρ_n(0, y…, s) dy (route (a)'s terms; p⁽¹⁾ = ρ₂ − T₃ + T₄ − T₅ + T₆ − …), the
density of x_{i+2} − x_i is
    p⁽²⁾(s) = Σ_{m ≥ 1} (−1)^{m−1} m T_{m+2}(s) = T₃ − 2T₄ + 3T₅ − 4T₆ + …,
so CS08's n ≤ 5 arithmetic part is Δp⁽²⁾ = ΔT₃ − 2ΔT₄ + 3ΔT₅ (Δ = ζ − sine; no ρ₂ term, so the block-cut n ≥ 3 share
is 1), and the n = 6 term is −4T₆ (truncation bound 4·T6_CAP·|T₆^sine|, route_a_zeta check (c)).
- **p⁽²⁾_sine** = d²/ds² [2E(0; s) + E(1; s)], with E(0) = Π(1 − λ_i) and E(1) = E(0)·Σ λ_i/(1 − λ_i) from the
  eigenvalues of the sine kernel on [0, s] (Gauss–Legendre m = 40), Chebyshev–Lobatto M = 160 on [0, 6]. Checks:
  ∫p⁽²⁾ = 1, mean 2, and d²E(0)/ds² = route (a)'s p_sine.
- **ζ's terms** at each F3 file's zero-weighted mean height, on Chebyshev–Lobatto nodes of [0, 3.0] (M = 32):
  - T₃ and T₄ from FastZeta at primes ≤ 3·10⁵ (route (a)'s quadratures, orders M_QUAD and M_QUAD + 4 for the error);
  - T₅ from ratios_t5.Model at primes ≤ 1000 (t5_points at M_T5, and M_T5 + 2 at the four largest nodes for the error).
- route (a)'s skip rule (|T_n^sine| < RZ.SKIP → no ζ change) is applied in the merge, as the prediction did.

  python followup_nnn.py selftest                       (p⁽²⁾_sine checks)
  python followup_nnn.py run CHUNK NCHUNKS OUT_DIR      (spot)
  python followup_nnn.py merge OUT_DIR                  → results/followup_nnn.json
"""
import json
import math
import os
import sys

import numpy as np
from numpy.polynomial import chebyshev as Cb

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "ph2"))
import route_a_zeta as RZ  # noqa: E402

SN, M_NN = 3.0, 32
NODES = 0.5 * SN * (1 - np.cos(np.pi * np.arange(M_NN + 1) / M_NN))


def nn_interp(vals, s):
    """Barycentric interpolation through NODES (Chebyshev–Lobatto on [0, SN])."""
    w = (-1.0) ** np.arange(len(NODES))
    w[0] *= 0.5
    w[-1] *= 0.5
    s = np.atleast_1d(np.asarray(s, float))
    D = s[:, None] - NODES[None, :]
    hit = np.isclose(D, 0, atol=1e-14)
    D[hit] = 1.0
    K = w / D
    out = (K @ np.asarray(vals)) / K.sum(1)
    r, c = np.nonzero(hit)
    out[r] = np.asarray(vals)[c]
    return out


def e01(s, m=40):
    x, w = np.polynomial.legendre.leggauss(m)
    t, ws = 0.5 * s * (x + 1), 0.5 * s * w
    D = t[:, None] - t[None, :]
    K = np.sinc(D)
    sq = np.sqrt(ws)
    lam = np.clip(np.linalg.eigvalsh(sq[:, None] * K * sq[None, :]), 0.0, 1.0 - 1e-300)
    e0 = float(np.prod(1 - lam))
    return e0, e0 * float(np.sum(lam / (1 - lam)))


_P = None


def p2_sine():
    """(p⁽²⁾_sine, p⁽¹⁾_sine) callables on [0, 6]."""
    global _P
    if _P is None:
        S, M = 6.0, 160
        nodes = 0.5 * S * (1 - np.cos(np.pi * np.arange(M + 1) / M))
        E = np.array([e01(s) if s > 0 else (1.0, 0.0) for s in nodes])
        xs = 2 * nodes / S - 1
        c2 = Cb.chebder(Cb.chebfit(xs, 2 * E[:, 0] + E[:, 1], M), 2) * (2 / S) ** 2
        c1 = Cb.chebder(Cb.chebfit(xs, E[:, 0], M), 2) * (2 / S) ** 2
        _P = (lambda s: Cb.chebval(2 * np.asarray(s, float) / S - 1, c2),
              lambda s: Cb.chebval(2 * np.asarray(s, float) / S - 1, c1))
    return _P


def selftest():
    import route_a_read as RR
    p2, p1 = p2_sine()
    g = np.linspace(0, 6, 60001)
    norm = float(np.trapezoid(p2(g), g))
    mean = float(np.trapezoid(g * p2(g), g))
    gg = np.linspace(RR.S_TINY, 1.8, 400)
    d1 = float(np.max(np.abs(p1(gg) - RR.p_sine()(gg))))
    ok = abs(norm - 1) < 1e-6 and abs(mean - 2) < 1e-4 and d1 < 1e-8
    print(f"p⁽²⁾_sine: ∫ = {norm:.8f}, mean = {mean:.6f}; d²E(0)/ds² vs route (a)'s p_sine on [S_TINY, 1.8]: max |diff| "
          f"{d1:.1e} → {'PASS' if ok else 'FAIL'}")
    return ok


def jobs():
    J = []
    for f in RZ.F3:
        for i, s in enumerate(NODES[1:], start=1):
            s = float(s)
            J += [(f, "T3", s), (f, "T4", s), (f, "T3e", s), (f, "T4e", s), (f, "T5", s)]
            if i > M_NN - 4:
                J.append((f, "T5e", s))
    return J


def run_one(job):
    f, part, s = job
    t = RZ.height(f, "mean")
    out = dict(file=f, part=part, s=s)
    if part in ("T3", "T4", "T3e", "T4e"):
        import cs4fast as F
        Z = F.FastZeta(t, pmax=RZ.PMAX_MAIN)
        m = RZ.M_QUAD + (4 if part.endswith("e") else 0)
        ds, w, c = RZ.term_points(s, m)[part[:2]]
        rz, rs = np.real(RZ.rho(Z, ds)), RZ.sine_rho(ds)
        out.update(T_sine=float(c * np.sum(w * rs)), dT=float(c * np.sum(w * (rz - rs))))
    else:
        import ratios_t5 as T
        pts = T.t5_points(s, T.M_T5 + (2 if part == "T5e" else 0))
        ds = [np.array([p[0][i] for p in pts]) for i in range(5)]
        w = np.array([p[1] for p in pts])
        rz = np.real(T.Model("zeta", math.log(t / (2 * math.pi)), pmax=1000).rho(ds))
        rs = RZ.sine_rho(ds)
        out.update(T_sine=float(np.sum(w * rs) / 6), dT=float(np.sum(w * (rz - rs)) / 6))
    print(json.dumps(out), flush=True)
    return out


def run(chunk, nchunks, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"nnn_c{chunk:02d}.jsonl")
    done = set()
    if os.path.exists(path):
        done = {(r["file"], r["part"], r["s"]) for r in map(json.loads, open(path))}
    J = sorted(jobs(), key=lambda j: {"T5e": 0, "T5": 1, "T4e": 2, "T4": 3, "T3e": 4, "T3": 5}[j[1]])
    for i, j in enumerate(J):
        if i % nchunks != chunk or j in done:
            continue
        r = run_one(j)
        with open(path, "a") as fh:
            fh.write(json.dumps(r) + "\n")


def merge(out_dir):
    rows = {}
    for fn in sorted(os.listdir(out_dir)):
        if fn.startswith("nnn_c") and fn.endswith(".jsonl"):
            for r in map(json.loads, open(os.path.join(out_dir, fn))):
                rows.setdefault((r["file"], r["part"], r["s"]), r)
    missing = set(jobs()) - set(rows)
    if missing:
        raise SystemExit(f"merge: {len(missing)} jobs missing")
    T6 = [0.0] + [abs(RZ.T6_det(float(s))) for s in NODES[1:]]
    res = dict(round="forty-ninth", candidate="A", definition=__doc__.split("\n\n")[0], nodes=NODES.tolist(),
               T6_sine_abs=T6, trunc6_bound=[4 * RZ.T6_CAP * v for v in T6], files={})
    for f in RZ.F3:
        out = {}
        for skip in (True, False):
            dp, err = [0.0], [0.0]
            for s in NODES[1:]:
                s = float(s)
                g = {p: rows[(f, p, s)] for p in ("T3", "T4", "T3e", "T4e", "T5")}
                d3 = 0.0 if (skip and abs(g["T3"]["T_sine"]) < RZ.SKIP) else g["T3"]["dT"]
                d4 = 0.0 if (skip and abs(g["T4"]["T_sine"]) < RZ.SKIP) else g["T4"]["dT"]
                dp.append(d3 - 2 * d4 + 3 * g["T5"]["dT"])
                e = abs(g["T3e"]["dT"] - g["T3"]["dT"]) + 2 * abs(g["T4e"]["dT"] - g["T4"]["dT"])
                if (f, "T5e", s) in rows:
                    e += 3 * abs(rows[(f, "T5e", s)]["dT"] - g["T5"]["dT"])
                err.append(e)
            out["skip" if skip else "every_node"] = dict(dp_nodes=dp, quad_err_nodes=err)
        res["files"][f] = out
        d = np.array(out["skip"]["dp_nodes"])
        print(f"{f}: max|Δp⁽²⁾| {np.max(np.abs(d)):.4e} at s = {NODES[int(np.argmax(np.abs(d)))]:.3f}; max quad err "
              f"{max(out['skip']['quad_err_nodes']):.1e}", flush=True)
    json.dump(res, open(os.path.join(HERE, "results", "followup_nnn.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "selftest":
        sys.exit(0 if selftest() else 1)
    elif cmd == "run":
        run(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    elif cmd == "merge":
        sys.exit(merge(sys.argv[2]))
