"""n = 6 stage (b), session 1 (l6/N6_STAGE_B.md; gates in l6/N6_STAGE_B_GATE.md): the long-range non-oscillating part of the
cross-connected correlation for two clusters, from the ratios construction (ratios_t5.Model, general in n).

The extraction is a phase filter. In the ratios formula every term of J(A; B) carries e^{−L(ΣS + ΣT)}, a linear phase
Φ = i·Σ_k c_k x_k with c_k = +1 for the points of P in S, −1 for the points of M in T, and 0 otherwise. Shifting the
second cluster by r multiplies a term by e^{−iL·r_t·Σ_{k∈B} c_k}. So a term is non-oscillating in r iff
Σ_{k ∈ cluster B} c_k = 0. This is the rule cs4fastc.connected uses for 2 + 2, applied term by term (no asymptotics).
The derivative jets preserve each term's phase, so the selection is exact at every order.

  K_ab(x_A, x_B) = ρ_{a+b}^{non-osc}(x_A ∪ x_B) − ρ_a(x_A)·ρ_b(x_B)      (unit-spacing densities, R/L^n)

  python n6b_extract.py gb2 OUT.json [PMAX]     G-b2: K_22 by this extraction vs cs4fastc.connected(nonosc_only=True)
"""
import itertools
import json
import math
import os
import sys
import time

import numpy as np

import ratios_t5 as T5


class FilteredModel(T5.Model):
    """ratios_t5.Model with the (S, T) terms filtered by their phase over a set of point indices (cluster B)."""

    def ratio_jet_f(self, J, A, B, Aidx, Bidx, clusterB, keep, only=None):
        nA = len(A)
        Cc, D = list(A), list(B)
        zero = np.zeros(np.shape(np.asarray(A[0])), complex)
        out = J.const(zero)
        for k in range(0, min(len(A), len(B)) + 1):
            for S in itertools.combinations(range(nA), k):
                for T in itertools.combinations(range(len(B)), k):
                    if only is not None:
                        if (S, T) != only:
                            continue
                    else:
                        cB = sum(1 for i in S if Aidx[i] in clusterB) - sum(1 for j in T if Bidx[j] in clusterB)
                        if not keep(cB):
                            continue
                    Sbar = [(A[i], i, 1) for i in range(nA) if i not in S]
                    Tm = [(-B[j], nA + j, -1) for j in T]
                    Tbar = [(B[j], nA + j, 1) for j in range(len(B)) if j not in T]
                    Sm = [(-A[i], i, -1) for i in S]
                    AA, BB = Sbar + Tm, Tbar + Sm
                    jet = lambda el: J.var(el[0], el[1], el[2])            # noqa: E731
                    lin = J.const(zero)
                    for i in S:
                        lin = lin + J.var(A[i], i, 1)
                    for j in T:
                        lin = lin + J.var(B[j], nA + j, 1)
                    term = J.exp(-self.L * lin)
                    for a in AA:
                        for b in BB:
                            term = J.mul(term, self.zfac(J, jet(a) + jet(b), False))
                    for c in Cc:
                        for d in D:
                            term = J.mul(term, self.zfac(J, J.const(c + d), False))
                    for a in AA:
                        for d in D:
                            term = J.mul(term, self.zfac(J, jet(a) + J.const(d), True))
                    for b in BB:
                        for c in Cc:
                            term = J.mul(term, self.zfac(J, jet(b) + J.const(c), True))
                    if self.kind == "zeta":
                        term = J.mul(term, J.exp(self.arith(J, AA, BB, Cc, D)))
                    out = out + term
        return out

    def ratio_jet_cls(self, J, A, B, Aidx, Bidx, clusterB):
        """As ratio_jet_f, but every (S, T) term kept and accumulated by its phase class cB (one pass)."""
        out = {}
        nA = len(A)
        for k in range(0, min(len(A), len(B)) + 1):
            for S in itertools.combinations(range(nA), k):
                for T in itertools.combinations(range(len(B)), k):
                    cB = sum(1 for i in S if Aidx[i] in clusterB) - sum(1 for j in T if Bidx[j] in clusterB)
                    term = self.ratio_jet_f(J, A, B, Aidx, Bidx, clusterB, None, only=(S, T))
                    out[cB] = out[cB] + term if cB in out else term
        return out

    def R_f(self, xs, clusterB, keep):
        n = len(xs)
        tot = self.L ** n                                                  # the constant piece: phase 0
        idx = range(n)
        for kp in range(1, n + 1):
            for P in itertools.combinations(idx, kp):
                rest = [i for i in idx if i not in P]
                for km in range(1, len(rest) + 1):
                    for M in itertools.combinations(rest, km):
                        Jt = T5.Jets(kp + km)
                        v = self.ratio_jet_f(Jt, [1j * xs[p] for p in P], [-1j * xs[m] for m in M], list(P), list(M),
                                             clusterB, keep)[Jt.K - 1]
                        tot = tot + self.L ** (n - kp - km) * v
        return tot

    def R_cls(self, xs, clusterB):
        """{cB: R_n's class-cB part}; the constant L^n sits in class 0."""
        n = len(xs)
        out = {0: self.L ** n + 0j}
        idx = range(n)
        for kp in range(1, n + 1):
            for P in itertools.combinations(idx, kp):
                rest = [i for i in idx if i not in P]
                for km in range(1, len(rest) + 1):
                    for M in itertools.combinations(rest, km):
                        Jt = T5.Jets(kp + km)
                        cls = self.ratio_jet_cls(Jt, [1j * xs[p] for p in P], [-1j * xs[m] for m in M], list(P), list(M),
                                                 clusterB)
                        for cB, jet in cls.items():
                            out[cB] = out.get(cB, 0) + self.L ** (n - kp - km) * jet[Jt.K - 1]
        return out

    def rho_cls(self, ds, clusterB):
        n = len(ds)
        return {k: v / self.L ** n for k, v in self.R_cls([2 * math.pi * d / self.L for d in ds], clusterB).items()}

    def rho_f(self, ds, clusterB, keep):
        return self.R_f([2 * math.pi * d / self.L for d in ds], clusterB, keep) / self.L ** len(ds)


NONOSC = lambda cB: cB == 0                                                 # noqa: E731
OSC = lambda cB: cB != 0                                                    # noqa: E731
ALL = lambda cB: True                                                       # noqa: E731


def K_ab(model, dsA, dsB):
    """Cross-connected non-oscillating K_ab at points dsA (cluster A) and dsB (cluster B, already shifted by r)."""
    a, b = len(dsA), len(dsB)
    nonosc = model.rho_f(list(dsA) + list(dsB), set(range(a, a + b)), NONOSC)
    return nonosc - model.rho(list(dsA)) * model.rho(list(dsB))


def gb2(out, pmax=1000):
    """G-b2 (N6_STAGE_B_GATE.md): the extraction's own (2, 2) instance against cs4fastc's (pointwise) and cs4lr's (grid)
    validated 2 + 2 non-oscillating
    ρ₄ᶜ at the same pmax, heights ℓ ≈ 15.75 and 21.75, r ∈ {20, 50, 100, 300, 1000}, in-pair offsets (0.5, 0.8) and
    (1.1, 0.3). Wrong variants: the sign-reversed extraction, and the (1, 1) reduction in its place, must fail."""
    import cs4fastc as FC
    rows = []
    for t in (2 * math.pi * math.exp(15.75), 2 * math.pi * math.exp(21.75)):
        ell = math.log(t / (2 * math.pi))
        M = FilteredModel("zeta", ell, pmax=pmax)
        ref = FC.FastZetaCached(t, pmax=pmax)
        for d1, d2 in ((0.5, 0.8), (1.1, 0.3)):
            r = np.array([20.0, 50.0, 100.0, 300.0, 1000.0])
            tt = time.time()
            _, non = ref.connected(d1, d2, r, nonosc_only=True)
            # cs4lr itself (the Stage 2 long-range evaluator) on its uniform grid; r values picked from it. cs4lr needs
            # primes above its split (1000) for its Fourier groups, so at pmax ≤ 1000 only cs4fastc is compared.
            if pmax > 1000:
                import cs4lr as LR
                lr = LR.LongRangeZeta(t, pmax=pmax)
                grid = 20.0 + 0.5 * np.arange(1962)                        # 20 … 1000.5, even length, uniform
                lr.set_grid(grid)
                _, nl = lr.connected(d1, d2, grid, nonosc_only=True)
                lr_at = nl[np.searchsorted(grid, r)]
            else:
                lr_at = non
            mine = K_ab(M, [np.full(5, -d1 / 2), np.full(5, d1 / 2)], [r - d2 / 2, r + d2 / 2])
            k11 = K_ab(M, [np.zeros(5)], [r])
            # precision (N6_STAGE_B_GATE.md G-b2): the larger of cs4lr's validated agreement with cs4fastc, 1.1e-9 ABSOLUTE
            # (cs4lr_check.py: max |Δ| per grid; GS_ZETA_RESULTS §2), and the 3e5 → 1e6 cutoff change. Only 1.1e-9 is
            # used, which is the stricter choice. (The first run applied 1.1e-9 as a relative tolerance by mistake.)
            prec = np.full(len(r), 1.1e-9)
            rows.append(dict(ell=ell, d1=d1, d2=d2, r=r.tolist(), ref=np.real(non).tolist(), ext=np.real(mine).tolist(),
                             cs4lr=np.real(lr_at).tolist(), abs_diff_cs4lr=np.abs(mine - lr_at).tolist(),
                             ok_cs4lr=bool(np.all(np.abs(mine - lr_at) <= prec)), cs4lr_compared=bool(pmax > 1000),
                             abs_diff=np.abs(mine - non).tolist(), prec=prec.tolist(),
                             ok=bool(np.all(np.abs(mine - non) <= prec)),
                             wrong_sign_fails=bool(np.any(np.abs(-mine - non) > prec)),
                             wrong_k11_fails=bool(np.any(np.abs(k11 - non) > prec)), wall_s=round(time.time() - tt, 1)))
            print({k: v for k, v in rows[-1].items() if k not in ("prec",)}, flush=True)
    res = dict(pmax=pmax, rows=rows, PASS=all(x["ok"] and x["ok_cs4lr"] for x in rows),
               wrong_variants_fail=all(x["wrong_sign_fails"] and x["wrong_k11_fails"] for x in rows))
    json.dump(res, open(out, "w"), indent=1)
    print("G-b2:", "PASS" if res["PASS"] else "FAIL", "| wrong variants fail:", res["wrong_variants_fail"], flush=True)
    return 0 if res["PASS"] and res["wrong_variants_fail"] else 1


# ---------------------------------------------------------------- G-b1 (i): algebra check, not G-b1 (round 76)
def _det_rho(P, N):
    X = P[..., :, None] - P[..., None, :]
    K = np.ones_like(X)
    nz = np.abs(X) > 1e-15
    K[nz] = np.sin(np.pi * X[nz]) / (N * np.sin(np.pi * X[nz] / N))
    return np.linalg.det(K)


def _tuples(nq, a):
    x, w = np.polynomial.legendre.leggauss(nq)
    x, w = 2 * (x + 1), 2 * w                                              # [0, 4]
    T = list(itertools.combinations(range(nq), a))
    return np.array([[x[i] for i in t] for t in T]), np.array([math.factorial(a) * np.prod([w[i] for i in t]) for t in T])


TRI = [(j / 8, (8 - abs(j)) / 64) for j in range(-7, 8)]                     # triangular weights over two periods


def algebra_check(out, rs=(20.0, 50.0, 100.0, 300.0), nq=4, N=100_000):
    """ALGEBRA CHECK, NOT G-b1 (round 76 (i)). At identical in-window Gauss–Legendre nodes (nq per coordinate, distinct
    sorted tuples × a!), for every (a, b) in {1, 2, 3}²:
      extraction  I_ab^ext(r) = Σ W·[ρ_{a+b}^{non-osc} − ρ_a ρ_b]   (FilteredModel, U(N), double; nodes ≥ 1 apart)
      determinant I_ab^det(r) = Σ_j t_j Σ W·[ρ_{a+b}(r + j/8) − ρ_a ρ_b]   (exact det, triangular two-period average)
    The triangular average removes the e^{2πikr} carriers (k ≠ 0 mod 8) together with their linear drift in r. The
    quadrature is common to both sides, so its error cancels. Declared criterion: every piece agrees to
    1e-13 + 1e-4·max(|ext|, |det|), at every r. The total C(r) = Σ c_a c_b I_ab is reported beside stage (a)'s exact
    value. This tests the phase filter at 3 + 3; it is not the comparison with the exact Fredholm answer (G-b1)."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "l6"))
    import n6a_trace as A
    cp = A.psi_coeffs(A.single_moments())
    M = FilteredModel("U", N)
    rows = []
    for r in rs:
        pieces, Cx, Cd = {}, 0.0, 0.0
        for a in (1, 2, 3):
            XA, WA = _tuples(nq, a)
            for b in (1, 2, 3):
                XB, WB = _tuples(nq, b)
                PA = np.repeat(XA, len(XB), 0)
                PB = np.tile(XB, (len(XA), 1))
                W = np.repeat(WA, len(XB)) * np.tile(WB, len(XA))
                t = time.time()
                prod = _det_rho(PA, N) * _det_rho(PB, N)
                ds = [PA[:, k] for k in range(a)] + [PB[:, k] + r for k in range(b)]
                from ratios_t6 import guard
                guard(ds)
                nonosc = np.real(M.rho_f(ds, set(range(a, a + b)), NONOSC))
                ext = float(np.sum(W * (nonosc - np.real(M.rho([PA[:, k] for k in range(a)]))
                                        * np.real(M.rho([PB[:, k] for k in range(b)])))))
                det = sum(tj * float(np.sum(W * (_det_rho(np.concatenate([PA, PB + r + sj], 1), N) - prod)))
                          for sj, tj in TRI)
                ok = abs(ext - det) <= 1e-13 + 1e-4 * max(abs(ext), abs(det))
                pieces[f"{a}{b}"] = dict(ext=ext, det=det, abs_diff=abs(ext - det), ok=bool(ok), wall_s=round(time.time() - t, 1))
                Cx += cp[a] * cp[b] * ext
                Cd += cp[a] * cp[b] * det
        exact = A.cov_r(r, A.single_moments(), cp)[0]
        rows.append(dict(r=r, pieces=pieces, C_ext=Cx, C_det_avg=Cd, C_exact_stage_a=exact, ok=all(v["ok"] for v in pieces.values())))
        print(r, {k: (f"{v['ext']:.4e}", f"{v['det']:.4e}", v["ok"]) for k, v in pieces.items()},
              f"C ext {Cx:.4e} det-avg {Cd:.4e} exact(a) {exact:.4e}", flush=True)
    res = dict(label="ALGEBRA CHECK, NOT G-b1 (round 76 (i))", nq=nq, N=N, rows=rows, PASS=all(x["ok"] for x in rows))
    json.dump(res, open(out, "w"), indent=1)
    print("algebra check (not G-b1):", "PASS" if res["PASS"] else "FAIL", flush=True)
    return 0 if res["PASS"] else 1


# ---------------------------------------------------------------- shared: one (a, b) piece at one shift, both sides
def _piece_task(job):
    """job = (kind, L, pmax, side, a, b, r, nq): Σ W·[ρ_{a+b}^{side} − ρ_a ρ_b] at separation r with identical in-window
    nodes; side 'ext' (phase-filtered, non-oscillating), 'full' (the unfiltered construction) or 'det' (U(N) only)."""
    kind, L, pmax, side, a, b, r, nq = job
    XA, WA = _tuples(nq, a)
    XB, WB = _tuples(nq, b)
    PA = np.repeat(XA, len(XB), 0)
    PB = np.tile(XB, (len(XA), 1))
    W = np.repeat(WA, len(XB)) * np.tile(WB, len(XA))
    if side == "det":
        N = int(L)
        return float(np.sum(W * (_det_rho(np.concatenate([PA, PB + r], 1), N) - _det_rho(PA, N) * _det_rho(PB, N))))
    from ratios_t6 import guard
    M = FilteredModel(kind, L, pmax=pmax)
    ds = [PA[:, k] for k in range(a)] + [PB[:, k] + r for k in range(b)]
    guard(ds)
    rho_full = M.rho_f(ds, set(range(a, a + b)), NONOSC if side == "ext" else ALL)
    prod = M.rho([PA[:, k] for k in range(a)]) * M.rho([PB[:, k] for k in range(b)])
    return float(np.sum(W * np.real(rho_full - prod)))


def _tri_avg(fn_of_shift):
    return sum(tj * fn_of_shift(sj) for sj, tj in TRI)


def algebra_check2(out, rs=(20.0, 50.0, 100.0, 300.0), nq=4, N=100_000, procs=28):
    """ALGEBRA CHECK, NOT G-b1: post-hoc rerun of round 76 (i) with IDENTICAL averaging on both sides. The first run
    (2c22dd0b) compared the triangular-averaged determinant with the UNAVERAGED extraction; the average multiplies a
    non-oscillating 1/r² term by 1 + 3σ²/r² (σ² = 0.164), which predicted its failures at r = 20 and 50 to 6% and 0.1%
    of the effect. Here both sides are averaged over the same 15 shifts; same nodes, same criterion
    (1e-13 + 1e-4·max per piece)."""
    from multiprocessing import Pool
    jobs = [("U", N, None, side, a, b, r + sj, nq) for r in rs for sj, _ in TRI for a in (1, 2, 3) for b in (1, 2, 3)
            for side in ("ext", "det")]
    with Pool(procs) as pool:
        vals = dict(zip(jobs, pool.map(_piece_task, jobs, chunksize=1)))
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "l6"))
    import n6a_trace as A
    cp = A.psi_coeffs(A.single_moments())
    rows = []
    for r in rs:
        pieces, Cx, Cd = {}, 0.0, 0.0
        for a in (1, 2, 3):
            for b in (1, 2, 3):
                ext = sum(tj * vals[("U", N, None, "ext", a, b, r + sj, nq)] for sj, tj in TRI)
                det = sum(tj * vals[("U", N, None, "det", a, b, r + sj, nq)] for sj, tj in TRI)
                ok = abs(ext - det) <= 1e-13 + 1e-4 * max(abs(ext), abs(det))
                pieces[f"{a}{b}"] = dict(ext=ext, det=det, rel_diff=abs(ext - det) / max(abs(ext), abs(det)), ok=bool(ok))
                Cx += cp[a] * cp[b] * ext
                Cd += cp[a] * cp[b] * det
        rows.append(dict(r=r, pieces=pieces, C_ext=Cx, C_det=Cd, ok=all(v["ok"] for v in pieces.values())))
        print(r, {k: f"{v['rel_diff']:.1e}" for k, v in pieces.items()}, f"C ext {Cx:.6e} det {Cd:.6e}", flush=True)
    res = dict(label="ALGEBRA CHECK, NOT G-b1 (round 76 (i)); post-hoc rerun with identical averaging on both sides",
               nq=nq, N=N, rows=rows, PASS=all(x["ok"] for x in rows))
    json.dump(res, open(out, "w"), indent=1)
    print("algebra check, both sides averaged (not G-b1):", "PASS" if res["PASS"] else "FAIL", flush=True)
    return 0 if res["PASS"] else 1


# ---------------------------------------------------------------- G-b3 (N6_STAGE_B_GATE.md, round 75; declared 2026-10-23)
GB3_CASES = [(15.75, 100.0), (15.75, 173.0), (15.75, 300.0), (15.75, 500.0), (21.75, 173.0), (21.75, 500.0)]


def gb3(out, pmax=1000, nq=4, procs=28):
    """G-b3: brute force against the extraction for the (3, 3) cross-connected term, ζ at PMAX 10³, at the six declared
    (ℓ, r). Both sides at identical in-window nodes (nq = 4; distinct sorted tuples × 3!) and both averaged over the
    same 15 shifts with the triangular two-period weights (the lesson of the first algebra check: average both sides
    identically). brute = the unfiltered construction's ρ₆ − ρ₃ρ₃; extraction = its phase-filtered non-oscillating
    part − ρ₃ρ₃. Tolerance: 1% of |brute| (the declared tolerance is the larger of the 4-vs-6-node quadrature error and
    1%; 1% alone is the stricter choice, and the quadrature cancels at identical nodes). Wrong variants: the
    sign-reversed extraction, and the (1, 1) piece in place of (3, 3), must fail."""
    from multiprocessing import Pool
    jobs = []
    for ell, r in GB3_CASES:
        for sj, _ in TRI:
            for side, a, b in (("full", 3, 3), ("ext", 3, 3), ("ext", 1, 1)):
                jobs.append(("zeta", ell, pmax, side, a, b, r + sj, nq))
    t = time.time()
    with Pool(procs) as pool:
        vals = dict(zip(jobs, pool.map(_piece_task, jobs, chunksize=1)))
    rows = []
    for ell, r in GB3_CASES:
        brute = sum(tj * vals[("zeta", ell, pmax, "full", 3, 3, r + sj, nq)] for sj, tj in TRI)
        ext = sum(tj * vals[("zeta", ell, pmax, "ext", 3, 3, r + sj, nq)] for sj, tj in TRI)
        k11 = sum(tj * vals[("zeta", ell, pmax, "ext", 1, 1, r + sj, nq)] for sj, tj in TRI)
        tol = 0.01 * abs(brute)
        rows.append(dict(ell=ell, r=r, brute=brute, ext=ext, rel_diff=abs(ext - brute) / abs(brute), ok=bool(abs(ext - brute) <= tol),
                         wrong_sign_fails=bool(abs(-ext - brute) > tol), wrong_k11_fails=bool(abs(k11 - brute) > tol)))
        print(rows[-1], flush=True)
    res = dict(pmax=pmax, nq=nq, rows=rows, wall_s=round(time.time() - t, 1), PASS=all(x["ok"] for x in rows),
               wrong_variants_fail=all(x["wrong_sign_fails"] and x["wrong_k11_fails"] for x in rows))
    json.dump(res, open(out, "w"), indent=1)
    print("G-b3:", "PASS" if res["PASS"] else "FAIL", "| wrong variants fail:", res["wrong_variants_fail"], flush=True)
    return 0 if res["PASS"] and res["wrong_variants_fail"] else 1


if __name__ == "__main__":
    if sys.argv[1] == "algebra":
        sys.exit(algebra_check(sys.argv[2]))
    if sys.argv[1] == "algebra2":
        sys.exit(algebra_check2(sys.argv[2], procs=int(sys.argv[3]) if len(sys.argv) > 3 else 28))
    if sys.argv[1] == "gb3":
        sys.exit(gb3(sys.argv[2], procs=int(sys.argv[3]) if len(sys.argv) > 3 else 28))
    if sys.argv[1] == "gb2":
        sys.exit(gb2(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1000))
