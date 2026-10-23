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
import sys
import time

import numpy as np

import ratios_t5 as T5


class FilteredModel(T5.Model):
    """ratios_t5.Model with the (S, T) terms filtered by their phase over a set of point indices (cluster B)."""

    def ratio_jet_f(self, J, A, B, Aidx, Bidx, clusterB, keep):
        nA = len(A)
        Cc, D = list(A), list(B)
        zero = np.zeros(np.shape(np.asarray(A[0])), complex)
        out = J.const(zero)
        for k in range(0, min(len(A), len(B)) + 1):
            for S in itertools.combinations(range(nA), k):
                for T in itertools.combinations(range(len(B)), k):
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
            # cs4lr itself (the Stage 2 long-range evaluator) on its uniform grid; r values picked from it
            import cs4lr as LR
            lr = LR.LongRangeZeta(t, pmax=pmax)
            grid = 20.0 + 0.5 * np.arange(1962)                            # 20 … 1000.5, even length, uniform
            lr.set_grid(grid)
            _, nl = lr.connected(d1, d2, grid, nonosc_only=True)
            lr_at = nl[np.searchsorted(grid, r)]
            mine = K_ab(M, [np.full(5, -d1 / 2), np.full(5, d1 / 2)], [r - d2 / 2, r + d2 / 2])
            k11 = K_ab(M, [np.zeros(5)], [r])
            # precision: cs4fastc's validated agreement (1.1e-9 relative, GS_ZETA_RESULTS §2), floor 1e-15 absolute
            prec = 1.1e-9 * np.abs(non) + 1e-15
            rows.append(dict(ell=ell, d1=d1, d2=d2, r=r.tolist(), ref=np.real(non).tolist(), ext=np.real(mine).tolist(),
                             cs4lr=np.real(lr_at).tolist(), abs_diff_cs4lr=np.abs(mine - lr_at).tolist(),
                             ok_cs4lr=bool(np.all(np.abs(mine - lr_at) <= prec + 1.1e-9 * np.abs(lr_at))),
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


if __name__ == "__main__":
    if sys.argv[1] == "gb2":
        sys.exit(gb2(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1000))
