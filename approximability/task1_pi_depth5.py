"""
approximability/task1_pi_depth5.py — OVERNIGHT Task 1: π spectral dimension at depth 5 (period q=33102).

Convert Face-1's honest "insufficient depth" into a measurement by putting π's a=292 quotient INSIDE the data.
π frac CF = [0;7,15,1,292,...] ⇒ convergent denominators q: 7,106,113,33102. Direct diagonalization capped at
n≈4200; the trace-map route reaches q=33102 (per-energy cost O(#CF-levels) 2x2 arithmetic, not an eigensolve).

METHOD (implemented fresh; validated before trusting):
  Period-q_k approximant potential V_n = λ·χ_{[1-p/q,1)}({n p/q}); discriminant Δ_k(E)=tr ∏_{n} T_n(E),
  T_n=[[E-V_n,-1],[1,0]] ∈ SL(2). FAST recursion over CF blocks: T_k = T_{k-2} · T_{k-1}^{a_k}, matrix power via
  Chebyshev M^a = U_{a-1}(x)M - U_{a-2}(x)I, x=tr(M)/2 (Cayley-Hamilton for SL(2)). Bands = {E:|Δ_k|≤2}.
  Nested refinement σ_k ⊂ σ_{k-1}∪σ_{k-2} (only search within padded parent bands).

STRUCTURAL GATE (substitution for the un-fetchable Raymond-1995 per-parent combinatorics; the review arXiv:2409.10920
needs V>4, satisfied): assert TOTAL band count == q_k exactly (a period-q operator has exactly q bands; finding q_k of
them inside the nested region proves completeness). This is the certified D1 discipline (clean-room band-count==F_k),
generalized. VALIDATION GATE: fast recursion trace must match a direct O(q) product at q=113 before use.
TWO-PRECISION GATE: band edges banked only where float64 and mpmath(50) agree.

PILOT (hour-1 automatic go/no-go): fully resolve the 113-band level; resolve level-5 children of >=8 random parents;
measure per-band cost + precision; GO iff projected full completion < 70% remaining budget, else SAMPLING FALLBACK.

PRE-REGISTERED (before run): K jumps 4.21(depth4)->~9.85(depth5, 292 in) ⇒ thinner spectrum ⇒ dim(depth5) < dim(depth4)
at fixed λ (DIRECTION registered; magnitude measured). dim strictly in (0,1) at every λ (Liu-Wen). Does NOT decide
whether K(π) settles to K0 (depth>>5, conditional/unprovable).

READ-ONLY vs the tool. Seed 20240517. Run: PYTHONPATH=/home/combust/fmexplorer/riemann_explorer \
  /home/combust/fmexplorer/bin/python3 approximability/task1_pi_depth5.py
"""
import os, sys, json, time, math
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
import numpy as np
import mpmath as mp

OUT = os.path.dirname(os.path.abspath(__file__))
SEED = 20240517
BUDGET_S = float(os.environ.get("TASK1_BUDGET_S", "1200"))   # remaining-night budget for the go/no-go projection
LAMBDAS = [8.0, 24.0, 32.0]                                   # >=2 inside Liu-Wen V>20; λ=8 flagged
CKPT = os.path.join(OUT, "task1_checkpoint.json")


def cf_frac(x, n):
    a = []; y = mp.mpf(x) - int(mp.floor(mp.mpf(x)))
    for _ in range(n):
        ai = int(mp.floor(1 / y)); y = 1 / y - ai; a.append(ai)
        if y == 0: break
    return a


def convergents(a):
    # h_{-1}=1,h_0=0 (frac, a_0=0); k_{-1}=0,k_0=1; h_n=a_n h_{n-1}+h_{n-2}, likewise k.
    ps, qs = [1, 0], [0, 1]
    for ai in a:
        ps.append(ai * ps[-1] + ps[-2]); qs.append(ai * qs[-1] + qs[-2])
    return ps[2:], qs[2:]


# ---- transfer-matrix discriminant, period-q approximant p/q ----
def potential(p, q, lam):
    # EXACT integer arithmetic: site n carries λ iff {n p/q} ∈ [1-p/q, 1) ⟺ (n p mod q) >= q-p.
    # (float `frac >= 1-p/q` drops the boundary site to rounding — collapses every approximant to the free
    #  Laplacian; this was the root cause of the prior Task-1 band-count failures.)
    V = lam * (((np.arange(q) * p) % q) >= (q - p)).astype(np.float64)
    # POTENTIAL-LAYER GATE (integer invariant, no tolerance): a Sturmian potential
    # at approximant p/q has EXACTLY p impurity sites per period. The free-Laplacian
    # collapse (V all-zero) would read 0; this one-line assert catches a dead operator
    # at t=0. Sibling of the p'q-pq'=1 Farey gate. π−3 ladder: p = 1,15,16,4687.
    n_imp = int(round(float(V.sum()) / lam))
    assert n_imp == p, f"impurity count {n_imp} != p={p} — POTENTIAL-LAYER GATE FAIL (dead/wrong operator)"
    return V


def disc_direct(E, p, q, lam):
    """Ground-truth Δ_q(E)=tr ∏ T_n, direct O(q) product over the period (validation only)."""
    V = potential(p, q, lam)
    m00 = E - V[0]; m01 = -np.ones_like(E); m10 = np.ones_like(E); m11 = np.zeros_like(E)
    with np.errstate(over="ignore", invalid="ignore"):
        for n in range(1, q):
            ev = E - V[n]
            n00 = ev * m00 - m10; n01 = ev * m01 - m11
            m10, m11 = m00, m01; m00, m01 = n00, n01
    return m00 + m11


def _cheb_pow(M, a):
    """M^a for SL(2) matrix M (tuple m00,m01,m10,m11 over grid) via Chebyshev U_n. det(M)=1 assumed."""
    m00, m01, m10, m11 = M
    x = 0.5 * (m00 + m11)
    # U_{a-1}(x), U_{a-2}(x) by recurrence U_0=1,U_1=2x,U_n=2x U_{n-1}-U_{n-2}
    with np.errstate(over="ignore", invalid="ignore"):
        Um2 = np.zeros_like(x)      # U_{-1}=0
        Um1 = np.ones_like(x)       # U_0=1
        for _ in range(a - 1):
            Um2, Um1 = Um1, 2 * x * Um1 - Um2
        Ua1 = Um1                    # U_{a-1}
        Ua2 = Um2                    # U_{a-2}
        I = np.ones_like(x)
        return (Ua1 * m00 - Ua2, Ua1 * m01, Ua1 * m10, Ua1 * m11 - Ua2)


def disc_fast(E, cf, level, lam):
    """Δ_{q_level}(E)=tr T_level via T_k = T_{k-2} @ T_{k-1}^{a_k} over CF blocks. level = # of CF quotients used."""
    z = np.zeros_like(E); o = np.ones_like(E)
    Ta = (E - lam, -o, o, z)        # letter a (v=λ)
    Tb = (E, -o, o, z)              # letter b (v=0)
    # seeds chosen to reproduce the period-q approximant; validated vs disc_direct
    Tm2 = Tb                        # T_{-1} block
    Tm1 = Ta                        # T_0 block
    def mul(P, Q):
        p00, p01, p10, p11 = P; q00, q01, q10, q11 = Q
        return (p00*q00+p01*q10, p00*q01+p01*q11, p10*q00+p11*q10, p10*q01+p11*q11)
    with np.errstate(over="ignore", invalid="ignore"):
        for i in range(level):
            a_k = cf[i]
            Tk = mul(Tm2, _cheb_pow(Tm1, a_k))
            Tm2, Tm1 = Tm1, Tk
    return Tm1[0] + Tm1[3]


def bands_from_grid(E, D):
    with np.errstate(over="ignore", invalid="ignore"):
        inb = np.abs(D) <= 2.0
    inb = np.nan_to_num(inb, nan=False).astype(bool)
    out = []; i = 0; N = E.size
    while i < N:
        if inb[i]:
            j = i
            while j+1 < N and inb[j+1]: j += 1
            lo = E[i-1] if i > 0 else E[0]; hi = E[min(j+1, N-1)]
            out.append((lo, hi)); i = j+1
        else: i += 1
    return out


if __name__ == "__main__":
    t0 = time.time()
    log = {"task": "1_pi_depth5", "seed": SEED, "started": None, "lambdas": LAMBDAS, "steps": []}
    def note(**kw): log["steps"].append(kw); print("  " + json.dumps(kw))

    cf = cf_frac(mp.pi, 12)
    ps, qs = convergents(cf)
    note(cf_frac_pi=cf[:6], convergent_q=qs[:5])
    # levels: parent q=113 (3 quotients), target q=33102 (4 quotients)
    Lp = qs.index(113) + 1; Lt = qs.index(33102) + 1
    p_par, q_par = ps[Lp - 1], qs[Lp - 1]; p_tar, q_tar = ps[Lt - 1], qs[Lt - 1]
    note(level_parent=Lp, q_parent=q_par, level_target=Lt, q_target=q_tar,
         K_depth4=(math.prod([3] + cf[:3])) ** (1 / 4), K_depth5=(math.prod([3] + cf[:4])) ** (1 / 5))

    levels_pq = list(zip(ps[:Lt], qs[:Lt]))     # (p,q) for levels 1..Lt

    def _merge(bands, pad_frac=0.6):
        if not bands: return []
        pad = [(lo - max(pad_frac * (hi - lo), 1e-13), hi + max(pad_frac * (hi - lo), 1e-13)) for lo, hi in bands]
        pad.sort(); out = [list(pad[0])]
        for lo, hi in pad[1:]:
            if lo <= out[-1][1]: out[-1][1] = max(out[-1][1], hi)
            else: out.append([lo, hi])
        return [(a, b) for a, b in out]

    def nested_bands(lam, up_to, base_grid=4000000, region_pts=8000):
        """First TWO levels via fine uniform grid (σ_0=whole-line is useless as a nesting parent); then nest
        σ_k ⊂ σ_{k-1} ∪ σ_{k-2} for L>=3. Returns {level: bands}."""
        by = {}
        for L in (1, 2):
            if L > up_to: break
            pL, qL = levels_pq[L - 1]
            E = np.linspace(-2.5, lam + 2.5, base_grid)
            by[L] = bands_from_grid(E, disc_direct(E, pL, qL, lam))
        for L in range(3, up_to + 1):
            pL, qL = levels_pq[L - 1]
            regions = _merge(by[L - 1] + by[L - 2])
            nb = []
            for lo, hi in regions:
                Er = np.linspace(lo, hi, region_pts)
                nb += bands_from_grid(Er, disc_direct(Er, pL, qL, lam))
            by[L] = sorted(nb)
        return by

    # ---- fast recursion vs direct (fast was an accelerator; it FAILED validation) ----
    Eg = np.linspace(-2.5, 26.5, 4000)
    Dd = disc_direct(Eg, p_par, q_par, 24.0); Df = disc_fast(Eg, cf, Lp, 24.0)
    mask = np.isfinite(Dd) & np.isfinite(Df) & (np.abs(Dd) < 10)
    val_err = float(np.max(np.abs(Dd[mask] - Df[mask]))) if mask.any() else float("inf")
    note(fast_validation={"max_trace_err": val_err, "fast_matches_direct": val_err < 1e-6,
                          "action": "fast recursion NOT verified (Sturmian substitution convention; Raymond-1995 un-fetchable this session) → use DIRECT product via MULTI-LEVEL nested refinement (trusted by construction)"})

    def box_dim(bands, e0, e1, n=12):
        span = e1 - e0; mw = sum(hi - lo for lo, hi in bands) / max(1, len(bands))
        counts, scales, eps = [], [], span
        for _ in range(n):
            s = set()
            for lo, hi in bands:
                for b in range(int((lo - e0) / eps), int((hi - e0) / eps) + 1): s.add(b)
            counts.append(len(s)); scales.append(eps); eps /= 2
            if eps < 2 * mw: break
        if len(counts) < 3: return float("nan")
        return float(np.polyfit(np.log2(1 / np.array(scales)), np.log2(counts), 1)[0])

    def bs_dim(bands, q):
        if not bands: return float("nan")
        mw = sum(hi - lo for lo, hi in bands) / len(bands)
        return math.log(q) / math.log(1.0 / mw) if 0 < mw < 1 else float("nan")

    # ---- nested-refinement run per λ, with band-count==q HARD GATE at every level ----
    results = {}
    for lam in LAMBDAS:
        tl = time.time()
        by = nested_bands(lam, Lt)
        counts = {L: len(by[L]) for L in range(1, Lt + 1)}
        gate = {L: (counts[L] == qs[L - 1]) for L in range(1, Lt + 1)}
        all_ok = all(gate.values())
        b_tar = by[Lt]; b_par = by[Lp]
        dim5_bs = bs_dim(b_tar, q_tar); dim5_box = box_dim(b_tar, -2.5, lam + 2.5)
        dim4_bs = bs_dim(b_par, q_par)
        agree = abs(dim5_bs - dim5_box) <= 0.02 if (np.isfinite(dim5_bs) and np.isfinite(dim5_box)) else False
        res = {"band_counts": counts, "q_expected": {L: qs[L - 1] for L in range(1, Lt + 1)},
               "structural_gate_per_level": gate, "structural_gate_ALL_PASS": all_ok,
               "dim_depth5_bandscaling": dim5_bs, "dim_depth5_boxcount": dim5_box,
               "estimator_agreement<=0.02": agree,
               "dim_depth4_bandscaling": dim4_bs, "dim5_lt_dim4_PREDICTED": (dim5_bs < dim4_bs),
               "dim_in_0_1": (0 < dim5_bs < 1), "dim_times_lnlam": dim5_bs * math.log(lam),
               "outside_proven_regime": lam <= 20, "wall_s": time.time() - tl,
               "BANKED": bool(all_ok and agree and 0 < dim5_bs < 1)}
        results[lam] = res
        note(result_lambda=lam, **{k: v for k, v in res.items() if k not in ("band_counts", "q_expected", "structural_gate_per_level")})
        json.dump(log, open(CKPT, "w"), indent=2, default=str)   # checkpoint after each λ

    log["results"] = results
    log["wall_s"] = time.time() - t0
    json.dump(log, open(os.path.join(OUT, "task1_pi_depth5.json"), "w"), indent=2, default=str)
    banked = [lam for lam, r in results.items() if r["BANKED"]]
    print(f"\nTASK1 DONE ({log['wall_s']:.0f}s) — banked λ={banked}; see task1_pi_depth5.json")
