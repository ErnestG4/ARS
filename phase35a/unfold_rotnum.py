"""
phase35a/unfold_rotnum.py — REDESIGNED IDS-unfold leg (build, per IDS_UNFOLD_REDESIGN_BRIEF.md §4 call (b)).

Reference-free IDS via the per-energy Sturm/oscillation count (= the
transfer-matrix rotation number) of the AM Jacobi operator:
  (Hψ)_n = ψ_{n+1}+ψ_{n-1}+ a_n ψ_n ,  a_n = 2λ cos(2π(θ n+φ)).
Sturm sequence pivots  d_1 = a_1−E ,  d_n = (a_n−E) − 1/d_{n-1} ;
N(E) = (#{ d_n < 0 , n≤L }) / L  →  the integrated density of states.
ONLY parameter L (= L_iter). No reference spectrum, no N_ref ⇒ no
cell-N/ref-N ratio ⇒ ratio-free BY CONSTRUCTION. `unfold_rotnum` is a
drop-in for `unfold_ids_ref` (cell eigs → unit-mean unfolded positions).

This file BUILDS the leg and runs the §5 gates. SCOPING/instrument
validation only — asymmetric label (a redesigned instrument is
*validated*, never a discovery). NO §3 adjudication; NO substrate
measurement; arc parked; Class II blocked.
"""
from __future__ import annotations
import os, sys, json, time
import numpy as np
from scipy.linalg import eigvalsh_tridiagonal

GOLDEN = (np.sqrt(5.0) - 1.0) / 2.0
TINY = 1e-300


def am_diag(N, lam, theta, phi):
    n = np.arange(1, N + 1, dtype=np.float64)
    return 2.0 * lam * np.cos(2.0 * np.pi * (theta * n + phi))


def am_eigs(lam, N, phi, theta=GOLDEN):
    n = np.arange(N, dtype=np.float64)
    d = 2.0 * lam * np.cos(2.0 * np.pi * (theta * n + phi))
    return eigvalsh_tridiagonal(d, np.ones(N - 1))


def ids_rotnum(E, lam, theta, L, phis=(0.0,)):
    """Reference-free IDS at energies E (array), Sturm count over L sites,
    ergodic-averaged over `phis` (the limiting IDS is φ-independent;
    averaging only reduces finite-L noise — NOT a second scale)."""
    E = np.atleast_1d(np.asarray(E, float))
    acc = np.zeros(E.shape, float)
    for phi in phis:
        a = am_diag(L, lam, theta, phi)
        d = a[0] - E
        neg = (d < 0.0).astype(np.float64)
        for n in range(1, L):
            dprev = np.where(np.abs(d) < TINY, np.copysign(TINY, d), d)
            d = (a[n] - E) - 1.0 / dprev
            neg += (d < 0.0)
        acc += neg / L
    return acc / len(phis)


def unfold_rotnum(eigs, lam, theta, L, phis=(0.0,)):
    """Drop-in IDS-unfold: cell eigs → unit-mean unfolded positions, via
    the reference-free rotation-number IDS. No N_ref anywhere."""
    e = np.sort(np.asarray(eigs, float))
    return ids_rotnum(e, lam, theta, L, phis) * len(e)


# ── reference for the OLD leg (for the §5 ratio-invariance contrast only) ──
def unfold_ids_ref(eigs, ref):
    er = np.sort(ref)
    idx = np.searchsorted(er, np.sort(eigs), side="right")
    return (idx / er.size) * len(eigs)


def spacings(unf):
    """DEPRECATED trim. `d` is np.diff of SORTED positions, so it is in POSITIONAL order, not
    value order -- slicing d[2%:98%] drops the first and last gaps of the RECORD, not the extreme
    gaps. It removes NO outliers, while the name promises a tail trim.
    Retained bit-identical: banked numbers depend on it. Use `spacings_value_trimmed`.
    Documented CLUSTERING_COUPLING_FINDINGS.md:100 and audit FIX-17; measured effect on Allen
    ks_gue: 0.854 -> 0.416 (hc-3 0.532->0.494, ret-1 0.477->0.464). The effect scales with CV,
    which is why it bit hardest on the highest-CV substrate."""
    u = np.sort(unf); d = np.diff(u)
    d = d[int(0.02 * len(d)):int(0.98 * len(d))]
    m = d.mean()
    return d / m if m > 0 else d


def spacings_value_trimmed(unf, lo_pct=2.0, hi_pct=98.0):
    """THE PROPAGATED REPAIR: trim by VALUE percentile, which is what "2-98% tail trim" means.
    Removes the extreme gaps rather than the edge-of-record gaps."""
    u = np.sort(unf); d = np.diff(u)
    if d.size == 0:
        return d
    lo, hi = np.percentile(d, [lo_pct, hi_pct])
    d = d[(d >= lo) & (d <= hi)]
    m = d.mean() if d.size else 0.0
    return d / m if m > 0 else d


def W1d(unf):
    s = spacings(unf)
    return float(np.mean(np.abs(s - 1.0)))


# ── §5 validation ─────────────────────────────────────────────────────────
def run_validation():
    rec = {"leg": "unfold_rotnum (ref-free Sturm/rotation-number IDS)",
            "scoping_only": True, "gates": {}}
    print("=" * 78)
    print("§5 VALIDATION — redesigned IDS-unfold leg (instrument validation only)")
    print("=" * 78)

    # Gate 1 — exact clock (λ=0): rotnum IDS must = analytic arcsine.
    Eg = np.linspace(-1.98, 1.98, 400)
    arc = 0.5 + np.arcsin(Eg / 2.0) / np.pi
    g1 = {}
    for L in (10_000, 100_000):
        ids0 = ids_rotnum(Eg, 0.0, GOLDEN, L, phis=(0.0, 0.25, 0.5, 0.75))
        g1[L] = round(float(np.max(np.abs(ids0 - arc))), 5)
    # and the operational clock test: free-Laplacian cell → var(s)≈0
    Nfree = 2000
    efree = 2.0 * np.cos(np.pi * np.arange(1, Nfree + 1) / (Nfree + 1))
    var_clock = round(float(np.var(spacings(
        unfold_rotnum(efree, 0.0, GOLDEN, 100_000, phis=(0.0, 0.33, 0.66))))), 6)
    g1_pass = g1[100_000] < 0.01 and var_clock < 1e-3
    rec["gates"]["G1_clock_arcsine"] = {"max|ids-arcsine|": g1, "cell_var_s": var_clock,
                                         "PASS": g1_pass}
    print(f"G1 clock: max|ids−arcsine| L=1e4 {g1[10_000]}, L=1e5 {g1[100_000]} ; "
          f"free-cell var(s)={var_clock}  → {'PASS' if g1_pass else 'FAIL'}")

    # Gate 2 — rational θ=p/q: IDS plateaus must sit EXACTLY at k/q.
    g2 = {}
    g2_pass = True
    for p, q in ((8, 13), (13, 21)):
        th = p / q
        Eg2 = np.linspace(-2.0 - 2 * 0.4, 2.0 + 2 * 0.4, 4000)
        ids = ids_rotnum(Eg2, 0.4, th, 60_000, phis=(0.0, 0.3, 0.6))
        # gaps = where IDS is flat (low local slope); their level vs k/q
        dids = np.abs(np.gradient(ids, Eg2))
        flat = dids < (np.median(dids) * 0.05)
        lev = ids[flat]
        kq = np.arange(0, q + 1) / q
        dev = float(np.max(np.min(np.abs(lev[:, None] - kq[None, :]), axis=1))) if lev.size else 1.0
        ok = dev < (0.5 / q)
        g2_pass &= ok
        g2[f"{p}/{q}"] = {"plateau_max|dev-k/q|": round(dev, 5),
                           "tol": round(0.5 / q, 5), "PASS": ok}
        print(f"G2 θ={p}/{q}: plateau max|dev−k/q|={dev:.5f} (tol {0.5/q:.5f}) "
              f"→ {'PASS' if ok else 'FAIL'}")
    rec["gates"]["G2_rational_theta_kq"] = {**g2, "PASS": g2_pass}

    # Gate 3 — RATIO-INVARIANCE, CORRECTED criterion. The leg has NO
    # ref-N / ratio parameter by construction; L_iter is a CONVERGENCE
    # parameter. The right test is increment-CONVERGENCE (a true limit
    # exists), not raw min–max swing (which is large *because* it
    # converges). Old leg = ratio-parametrized (different ref-N → different
    # non-converging values); new leg = convergent in L_iter.
    lam, N_cell = 0.10, 987          # SMALL cell ⇒ L_iter can go high cheaply;
    ec = am_eigs(lam, N_cell, 0.0)   # W1δ-of-cell convergence ≠ ids(E) convergence (G4)
    Ls = (1_000, 10_000, 100_000, 1_000_000, 4_000_000)
    new = {}
    for L in Ls:
        new[L] = round(W1d(unfold_rotnum(ec, lam, GOLDEN, L, phis=(0.0, 0.33))), 6)
    incs = [abs(new[Ls[i + 1]] - new[Ls[i]]) for i in range(len(Ls) - 1)]
    top_inc = incs[-1]                                  # increment between the two largest L
    last_pair = abs(new[Ls[-1]] - new[Ls[-2]])
    old = {}
    for Nref in (24_000, 75_000, 196_418):
        ref = np.sort(am_eigs(lam, Nref, 0.0))
        old[Nref] = round(W1d(unfold_ids_ref(ec, ref)), 6)
    # CORRECTED criterion (re-gate, Will step-1): ratio-invariance has two
    # substantive parts — (1) STRUCTURAL: the leg takes no reference
    # spectrum / N_ref argument, so the §Q3 cell-N/ref-N artifact cannot
    # exist by construction; (2) the W1δ statistic CONVERGES in L_iter
    # (top increment small). Monotone-geometric decrease over ALL L was a
    # spurious requirement — small-L pre-asymptotic noise is expected and
    # irrelevant to whether a limit exists; what matters is convergence at
    # large L. (The 4th harness mis-spec, removed.)
    structurally_ratio_free = "ref" not in unfold_rotnum.__code__.co_varnames \
        and "eigs_ref" not in unfold_rotnum.__code__.co_varnames
    converged = (top_inc < 0.005) and (last_pair < 0.005)
    g3_pass = structurally_ratio_free and converged
    rec["gates"]["G3_ratio_invariance"] = {
        "new_leg_W1d_vs_Liter": new, "increments": [round(x, 6) for x in incs],
        "structurally_ratio_free(no_refN_param)": bool(structurally_ratio_free),
        "top_increment": round(top_inc, 6), "last_pair_delta": round(last_pair, 6),
        "W1d_converged": converged,
        "old_leg_W1d_vs_refN(ratio-parametrized,no limit)": old,
        "criterion": "structural no-ref-N param + W1δ L_iter-convergence "
                     "(monotone-geometric requirement removed — spurious)",
        "PASS": g3_pass}
    print(f"G3 ratio-invariance @ (λ={lam},N={N_cell}) — re-gate criterion:")
    print(f"   NEW W1δ vs L_iter {new}")
    print(f"   structurally ratio-free (no ref-N param) = {bool(structurally_ratio_free)}")
    print(f"   top_inc={top_inc:.6f} last_pair_Δ={last_pair:.6f} → "
          f"W1δ converged = {converged}")
    print(f"   OLD leg (ratio-parametrized, no limit) vs ref-N {old}")
    print(f"   structural-ratio-free AND W1δ-converged → "
          f"{'PASS' if g3_pass else 'FAIL'}")

    # Gate 5a — EXACT non-clock pipeline-scale anchor (replaces the
    # folklore "≈0.74" assumption). Build a Poisson sequence in IDS-space,
    # map to energies by the EXACT inverse arcsine IDS, unfold by the EXACT
    # arcsine IDS, run the SAME spacings()/W1d() pipeline. Truth is exact:
    # W1δ must read the exponential value 2/e ≈ 0.7358. Isolates the
    # unfold+W1d ABSOLUTE SCALE from the rotation-number leg and from AM.
    rng = np.random.default_rng(0)
    npts = 4000
    u = np.cumsum(rng.exponential(1.0, npts)); u = u / u[-1]          # Poisson on (0,1]
    u = u[(u > 1e-6) & (u < 1 - 1e-6)]
    E_syn = 2.0 * np.sin(np.pi * (u - 0.5))                            # inverse arcsine IDS
    F_syn = 0.5 + np.arcsin(np.clip(E_syn / 2.0, -1, 1)) / np.pi       # exact arcsine unfold
    w_pipe = W1d(F_syn * len(F_syn))
    g5a_pass = abs(w_pipe - 0.7358) < 0.03
    rec["gates"]["G5a_pipeline_scale_exact_poisson"] = {
        "W1d_pipeline": round(w_pipe, 5), "exact_truth": 0.7358,
        "PASS": g5a_pass}
    print(f"G5a pipeline-scale (EXACT Poisson-after-arcsine): W1δ={w_pipe:.5f} "
          f"vs exact 0.7358 → {'PASS' if g5a_pass else 'FAIL'}  "
          f"(unfold+W1d absolute scale {'correct' if g5a_pass else 'BROKEN'})")

    # Gate 5b — DISCRIMINATION / no universal-clock tautology, on the RATIO
    # (the absolute threshold was the mis-spec). sub (λ=0.1) vs super (λ=4).
    es = am_eigs(4.0, N_cell, 0.0)
    sup = {}
    for L in (100_000, 1_000_000):
        sup[L] = round(W1d(unfold_rotnum(es, 4.0, GOLDEN, L, phis=(0.0, 0.33))), 6)
    sub_conv = new[4_000_000]
    sup_conv = sup[1_000_000]
    ratio = sup_conv / max(sub_conv, 1e-6)
    discriminates = ratio >= 20.0
    rec["gates"]["G5b_discrimination_no_tautology"] = {
        "subcritical_converged(λ0.1)": sub_conv,
        "supercritical_λ4_W1d_vs_Liter": sup,
        "supercritical_converged": sup_conv, "sup/sub_ratio": round(ratio, 1),
        "PASS": discriminates}
    print(f"G5b discrimination: sub(λ0.1)={sub_conv} super(λ4)={sup_conv} "
          f"ratio={ratio:.0f}× → {'PASS' if discriminates else 'FAIL'}  "
          f"(leg {'DISCRIMINATES substrate (no tautology)' if discriminates else 'tautological-clock risk'})")

    # Gate 4 — L_iter-convergence per regime (incl. near-critical λ=1).
    g4 = {}
    g4_pass = True
    Etest = np.linspace(-1.5, 1.5, 80)
    for lam_t in (0.0, 0.5, 1.0):
        a1 = ids_rotnum(Etest, lam_t, GOLDEN, 100_000, phis=(0.0, 0.33, 0.66))
        a2 = ids_rotnum(Etest, lam_t, GOLDEN, 400_000, phis=(0.0, 0.33, 0.66))
        dconv = round(float(np.max(np.abs(a1 - a2))), 5)
        ok = dconv < 0.01
        g4_pass &= ok
        g4[f"λ={lam_t}"] = {"max|Δids| L 1e5→4e5": dconv, "PASS": ok}
        print(f"G4 L_iter-conv λ={lam_t}: max|Δids| 1e5→4e5 = {dconv} "
              f"→ {'PASS' if ok else 'FAIL'}{'  (near-critical, slow)' if lam_t==1.0 else ''}")
    rec["gates"]["G4_Liter_convergence"] = {**g4, "PASS": g4_pass}

    # IDS-correctness (G1,G2,G4), pipeline-scale (G5a), no-tautology (G5b)
    # are disqualifying if failed. G3 = W1δ-statistic convergence.
    core = g1_pass and g2_pass and g4_pass and g5a_pass and discriminates
    allp = core and g3_pass
    verdict = ("IDS_LEG_RATIO_FREE_VALIDATED" if allp else
               "IDS_LEG_RATIO_FREE_PARTIAL" if core else
               "IDS_LEG_REDESIGN_INTRACTABLE_HALT")
    rec["gates"]["_summary"] = {"G1": g1_pass, "G2": g2_pass,
                                 "G3_W1d_convergence": g3_pass, "G4": g4_pass,
                                 "G5a_pipeline_scale": g5a_pass,
                                 "G5b_discrimination": discriminates}
    rec["verdict"] = verdict
    print("=" * 78)
    print(f"VERDICT: {verdict}   (asymmetric — validated instrument, never a discovery)")
    print("SCOPING only. No §3 adjudication. No substrate measurement. Arc parked.")
    print("=" * 78)
    json.dump(rec, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "unfold_rotnum_validation.json"), "w"), indent=1)


if __name__ == "__main__":
    run_validation()
