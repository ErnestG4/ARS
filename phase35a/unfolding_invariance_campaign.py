"""
phase35a/unfolding_invariance_campaign.py — SCOPING CAMPAIGN (not 35a execution).

Resolves rev-3's structure (Will, 2026-05-16). Supersedes the
single-unfolding disambiguator: KS-vs-exponential is passable by the
artifact (Reading-2's gaps→large-spacing-tail marginal is itself
exponential-ish). The DECISIVE split is unfolding-INVARIANCE — genuine
localization-Poisson is unfolding-stable (levels truly decoupled); a
deg-11 polynomial artifact (cannot follow a devil-staircase IDS ⇒ leaves
gap mass as residual large-spacing → low rep_int → BL) is
unfolding-dependent by construction.

STAGE 0 (GATE — §7.ter.55/57, validate on known truth before the unknown):
  λ=0 free Laplacian, eigenvalues 2cos(kπ/(N+1)), exact truth
  P(s)=δ(s−1) (clock). Run through the identical pipeline under
  exact-arcsine-IDS / deg-11 / neutral. Answers: (1) where does exact
  clock land (does TR bin clock? — makes "subcritical reads TR"
  consistent with the Class-II premise or threatens it); (2) does deg-11
  reproduce clock on a SMOOTH IDS (if not, deg-11 is implicated for every
  λ≠0 cell ⇒ Reading-2 pre-confirmed). Gates the whole campaign.

STAGE 1: direct P(s) characterization across the 35b (λ,N=F_k) grid,
  under THREE unfoldings — deg-11 polynomial (the suspect),
  gap-labelling-IDS proxy (high-N-reference IDS — follows the staircase
  where deg-11 cannot; the principled one), neutral low-order (deg-3) —
  KS vs {clock δ(s−1), Wigner-GUE, Poisson/exponential} judged on the
  §7.ter.59 floor (KS / (0.8687/√n)), plus the zoo quadrant. Per cell:
  is the nearest-class verdict INVARIANT across the three unfoldings?

Records EVERYTHING (the horizon, not just the fork): full per-cell
P(s)/KS/floor/quadrant under every unfolding → JSON + readable log.
NO auto-adjudication (v1's auto-verdict was the artifact). NO calibrator
built, NO NNS derived, NO DGY/f(α) work. Bounded.

Unfolding caveat (flagged): the "gap-labelling-IDS" leg is a
high-resolution-reference-IDS proxy for the exact ℤ+θℤ construction —
sufficient for an invariance audit (it DOES follow the staircase, which
is the only property the test needs); the rigorous construction is a §3
post-fork concern.
"""
from __future__ import annotations
import os, sys, json, warnings
import numpy as np
from scipy.linalg import eigvalsh_tridiagonal

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS_DIR))            # criticality_tool/
from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic  # SAFE (no side-effect import)

GOLDEN = (np.sqrt(5.0) - 1.0) / 2.0
Q_MAX, MIN_EV = 30, 30


# ── operator ──────────────────────────────────────────────────────────────
def am_eigs(lam, N, phi):
    n = np.arange(N, dtype=np.float64)
    diag = 2.0 * lam * np.cos(2.0 * np.pi * (GOLDEN * n + phi))
    return eigvalsh_tridiagonal(diag, np.ones(N - 1))     # λ=0 ⇒ free Laplacian


# ── unfoldings (all inline; NO side-effecting imports) ────────────────────
def unfold_poly(eigs, deg):
    """Smooth polynomial fit to the cumulative count (toolkit's
    `unfold_empirical` procedure, inlined). deg=11 = the suspect;
    deg=3 = neutral low-order. Cannot follow a devil-staircase IDS."""
    e = np.asarray(eigs, float)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        c = np.polyfit(e, np.arange(1, e.size + 1, dtype=float), deg)
    return np.polyval(c, e)


def unfold_ids_ref(eigs, eigs_ref):
    """Gap-labelling-IDS proxy: unfold by a high-N reference spectrum's
    empirical IDS (monotone step interpolation). FOLLOWS the staircase —
    the IDS is flat across gaps, so gap-induced large-spacing mass is
    absorbed, not left as residual. This is the leg deg-11 cannot do."""
    er = np.sort(np.asarray(eigs_ref, float))
    # IDS(E) = (#ref ≤ E)/Nref ; evaluate at eigs, scale to the cell's N
    idx = np.searchsorted(er, np.asarray(eigs, float), side="right")
    return (idx / er.size) * len(eigs)


def unfold_arcsine(eigs, N):
    """EXACT free-Laplacian IDS on [−2,2]: F(E)=1/2+arcsin(E/2)/π.
    The analytic truth-unfolding for λ=0 (Stage-0 only)."""
    e = np.clip(np.asarray(eigs, float) / 2.0, -1.0, 1.0)
    return (0.5 + np.arcsin(e) / np.pi) * N


# ── spacings + KS on the §7.ter.59 floor ──────────────────────────────────
def spacings(unfolded):
    u = np.sort(unfolded)
    d = np.diff(u)
    d = d[int(0.02 * len(d)):int(0.98 * len(d))]          # edge-trim, comparable
    m = d.mean()
    return d / m if m > 0 else d                            # unit mean


def _cdf_wigner(s):
    g = np.linspace(0, max(s.max(), 6.0), 6001)
    pdf = (32 / np.pi**2) * g * g * np.exp(-4 * g * g / np.pi)
    cdf = np.concatenate([[0], np.cumsum(0.5 * (pdf[:-1] + pdf[1:]) * np.diff(g))])
    return np.interp(s, g, cdf)


def ks_floor(d):
    """KS to clock δ(s−1), Wigner-GUE, Poisson(exp); each as raw KS and
    as the §7.ter.59 floor ratio KS/(0.8687/√n)."""
    s = np.sort(d)
    n = s.size
    floor = 0.8687 / np.sqrt(max(n, 1))
    F = (np.arange(1, n + 1)) / n
    ks_clock = float(np.max(np.abs(F - (s >= 1.0).astype(float))))
    ks_wig = float(np.max(np.abs(F - _cdf_wigner(s))))
    ks_poi = float(np.max(np.abs(F - (1.0 - np.exp(-s)))))
    out = {}
    for nm, k in (("clock", ks_clock), ("wigner", ks_wig), ("poisson", ks_poi)):
        out[nm] = round(k, 4)
        out[nm + "_fl"] = round(k / floor, 2)
    out["n"], out["floor"] = n, round(floor, 5)
    out["var_s"] = round(float(np.var(d)), 4)
    out["nearest"] = min(("clock", "wigner", "poisson"), key=lambda c: out[c])
    return out


def quadrant_occ(unfolded):
    ev = np.sort(unfolded)
    j = joint_q_profile(ev, q_max=Q_MAX, min_events_per_q=MIN_EV)
    qd = joint_quadrant_diagnostic(j)
    vc = qd['quadrant'].value_counts(normalize=True)
    return {k: round(float(v), 3) for k, v in vc.items()}, max(vc.index, key=lambda k: vc[k])


def fib(kmin, kmax):
    F = [1, 1]
    while len(F) <= kmax:
        F.append(F[-1] + F[-2])
    return [F[k] for k in range(kmin, kmax + 1)]


# ── campaign ──────────────────────────────────────────────────────────────
def run():
    phis = [0.0, 0.2, 0.4]
    rec = {"stage0_anchor": [], "stage1_grid": []}

    print("=" * 80)
    print("STAGE 0 — GATE: λ=0 exact clock (P(s)=δ(s−1)) through the pipeline")
    print("  truth=arcsine-IDS ; suspect=deg-11 ; neutral=deg-3 ; (no IDS-ref: λ=0 has no gaps)")
    print("=" * 80)
    print(f"{'N':>6} {'unfold':>9} | {'var(s)':>7} {'KS_clk(fl)':>11} "
          f"{'KS_wig(fl)':>11} {'KS_poi(fl)':>11} | near   quad")
    for N in [377, 2584, 6765]:
        eig = am_eigs(0.0, N, 0.0)                          # free Laplacian (φ irrelevant)
        for nm, uf in (("arcsine", unfold_arcsine(eig, N)),
                       ("deg11",   unfold_poly(eig, 11)),
                       ("deg3",    unfold_poly(eig, 3))):
            d = spacings(uf)
            k = ks_floor(d)
            occ, dq = quadrant_occ(uf)
            rec["stage0_anchor"].append({"N": N, "unfold": nm, **k,
                                          "quad": dq, "occ": occ})
            print(f"{N:>6} {nm:>9} | {k['var_s']:>7.4f} "
                  f"{k['clock']:.3f}({k['clock_fl']:>5.1f}) "
                  f"{k['wigner']:.3f}({k['wigner_fl']:>5.1f}) "
                  f"{k['poisson']:.3f}({k['poisson_fl']:>5.1f}) | "
                  f"{k['nearest']:<6s} {dq}")

    print("\n" + "=" * 80)
    print("STAGE 1 — (λ,N) grid × 3 unfoldings ; nearest-class INVARIANCE is")
    print("  the decisive split. KS(floor-ratio); quad. avg over phases.")
    print("=" * 80)
    sup = [1.05, 1.10, 1.25, 1.50, 2.00, 4.00]
    sub = [0.10, 0.30, 0.50, 0.80, 0.95]
    Ns = [377, 987, 2584, 6765]
    NREF = 24000                                            # high-N IDS reference

    for tag, lams in (("SUPERCRITICAL λ→1⁺", sup), ("SUBCRITICAL small-λ", sub)):
        print(f"\n{tag}")
        print(f"{'λ':>5} {'N':>5} | {'unfold':>7}  near  KS(fl) clk/wig/poi   "
              f"var(s)  quad  | INVARIANT?")
        for lam in lams:
            ref = np.concatenate([am_eigs(lam, NREF, p) for p in (0.0, 0.33)])
            for N in Ns:
                nears = {}
                line_rows = []
                for nm in ("deg11", "ids", "deg3"):
                    ks_acc, occ_acc, near_acc = [], {}, []
                    for p in phis:
                        eig = am_eigs(lam, N, p)
                        if nm == "deg11":
                            uf = unfold_poly(eig, 11)
                        elif nm == "deg3":
                            uf = unfold_poly(eig, 3)
                        else:
                            uf = unfold_ids_ref(eig, ref)
                        d = spacings(uf)
                        k = ks_floor(d)
                        near_acc.append(k["nearest"])
                        ks_acc.append((k["clock_fl"], k["wigner_fl"], k["poisson_fl"]))
                        o, _ = quadrant_occ(uf)
                        for kk, vv in o.items():
                            occ_acc[kk] = occ_acc.get(kk, 0.0) + vv / len(phis)
                    ks_m = np.mean(ks_acc, axis=0)
                    var_m = round(float(np.mean([ks_floor(spacings(
                        (unfold_poly(am_eigs(lam, N, p), 11) if nm == "deg11" else
                         unfold_poly(am_eigs(lam, N, p), 3) if nm == "deg3" else
                         unfold_ids_ref(am_eigs(lam, N, p), ref))))["var_s"]
                        for p in phis])), 4)
                    near = max(set(near_acc), key=near_acc.count)
                    dq = max(occ_acc, key=occ_acc.get) if occ_acc else "—"
                    nears[nm] = near
                    rec["stage1_grid"].append(
                        {"lam": lam, "N": N, "unfold": nm, "nearest": near,
                         "ks_floor_clk_wig_poi": [round(x, 2) for x in ks_m],
                         "var_s": var_m, "quad": dq, "occ": {k: round(v, 3) for k, v in occ_acc.items()}})
                    line_rows.append(
                        f"{lam:>5.2f} {N:>5} | {nm:>7}  {near:<5s} "
                        f"{ks_m[0]:5.1f}/{ks_m[1]:5.1f}/{ks_m[2]:5.1f}  "
                        f"{var_m:6.3f}  {dq}")
                inv = "YES" if len(set(nears.values())) == 1 else \
                      f"NO {nears}"
                for i, r in enumerate(line_rows):
                    print(r + (f"  | {inv}" if i == len(line_rows) - 1 else ""))

    out = os.path.join(THIS_DIR, "unfolding_invariance_results.json")
    with open(out, "w") as f:
        json.dump(rec, f, indent=1)
    print(f"\nfull record (the horizon, not just the fork) → {out}")
    print("\nNO auto-verdict. Read STAGE 0 gate first, then STAGE 1 invariance.")


if __name__ == "__main__":
    run()
