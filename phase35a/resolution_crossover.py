"""
phase35a/resolution_crossover.py — SCOPING CALCULATION ONLY (not 35a execution).
CORRECTED (v2). Supersedes the broken g_max/s̄ diagnostic, which tracked
the principal AM gap (~2λ, present for every λ≠0) and so labelled every
λ "Cantor-resolved" — an artifact, not the crossover (caught 2026-05-16).

Fork (Will): is class I on 35b's critical path — i.e. does the EXISTING
zoo mis-fit the finite-N AM spectrum at 35b-relevant (λ, N=F_k) cells —
or does the zoo handle them (⇒ class I descopes, rev-3 = P3 only)?

Two faithful instruments, both reusing validated toolkit machinery:

  (A) ZOO-CLASSIFIER (operational truth — Will's own criterion):
      AM eigenvalues → unfold_empirical (the toolkit's own RMT-calibrator
      unfolding, deg=11) → the unfolded levels as the point process →
      joint_q_profile → joint_quadrant_diagnostic. Report per-cell
      quadrant occupancy. BL ⇒ zoo handles (Poisson/localized). BR/TR
      clean ⇒ zoo handles (would-be class-II / clock corner).
      BR_artifact-dominated ⇒ the zoo's nearest-Wigner rule fits a
      non-Wigner shape it has no class for ⇒ class I needed there.

  (B) SPECTRAL multi-scale cross-check (the corrected metric): in
      UNFOLDED coords (mean spacing = 1), drop the single largest gap
      (the principal gap — the v1 confound) and ask whether the REST is
      a multi-decade hierarchy whose resolved-gap count grows along the
      F_k ladder (Cantor) vs a single-scale ~unit-spacing bulk (clock).

Plus a programmatic "eyeball": top unfolded gaps at representative cells.

Unfolding caveat (flagged, load-bearing): deg-11 polynomial unfolding
smooths over the devil's-staircase IDS — it cannot represent the
gap-labelling staircase. That is correct for THIS question (the zoo
uses exactly this unfolding for its calibrators, so we ask whether the
zoo-as-built mis-fits AM); the rigorous IDS/gap-labelling unfolding is
a §3 post-fork concern, not this scoping pass.

NO calibrator built; NO NNS derived; NO DGY/f(α) work. Bounded.
"""
from __future__ import annotations
import os, sys, warnings
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS_DIR))          # criticality_tool/

from fix_gue_generator import unfold_empirical          # toolkit's own
from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic

GOLDEN = (np.sqrt(5.0) - 1.0) / 2.0
Q_MAX, MIN_EV = 30, 30                                   # extractor_distinctness defaults


def am_eigs(lam: float, N: int, phi: float) -> np.ndarray:
    from scipy.linalg import eigvalsh_tridiagonal
    n = np.arange(N, dtype=np.float64)
    diag = 2.0 * lam * np.cos(2.0 * np.pi * (GOLDEN * n + phi))
    return eigvalsh_tridiagonal(diag, np.ones(N - 1))


def unfolded_levels(lam: float, N: int, phi: float) -> np.ndarray:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")                  # polyfit conditioning
        u = unfold_empirical(am_eigs(lam, N, phi), deg=11)
    return np.sort(u)


def fib(kmin, kmax):
    F = [1, 1]
    while len(F) <= kmax:
        F.append(F[-1] + F[-2])
    return [F[k] for k in range(kmin, kmax + 1)]


# ── (A) zoo classifier ────────────────────────────────────────────────────
def zoo_verdict(lam, N, phis):
    """Per-q quadrant occupancy fractions, averaged over phases."""
    from collections import Counter
    agg = Counter()
    tot = 0
    for p in phis:
        ev = unfolded_levels(lam, N, p)
        j = joint_q_profile(ev, q_max=Q_MAX, min_events_per_q=MIN_EV)
        qd = joint_quadrant_diagnostic(j)
        for q in qd['quadrant']:
            agg[q] += 1
            tot += 1
    return {k: agg[k] / tot for k in agg}, tot


def dom(frac):
    return max(frac, key=frac.get) if frac else "none"


# ── (B) spectral multi-scale cross-check (principal-gap excluded) ──────────
def hierarchy(lam, N, phis, big=3.0):
    """In unfolded coords: drop the largest gap (principal), count
    'resolved' gaps (> big × unit spacing) among the rest, and their
    decade spread."""
    ncnt, spreads = [], []
    for p in phis:
        u = unfolded_levels(lam, N, p)
        d = np.diff(u)
        d = d[int(0.02 * len(d)):int(0.98 * len(d))]      # edge-trim
        d = np.sort(d)[:-1]                                # drop principal
        res = d[d > big]
        ncnt.append(len(res))
        spreads.append(np.log10(res.max() / res.min()) if len(res) > 1 else 0.0)
    return float(np.mean(ncnt)), float(np.mean(spreads))


def run():
    phis = [0.0, 0.2, 0.4]
    Ns_full = fib(12, 20)                                  # 144 … 6765 (cheap)
    Ns_zoo = [377, 2584, 6765]                             # F_14, F_18, F_20

    sup = [1.05, 1.10, 1.25, 1.50, 2.00, 4.00]             # λ→1⁺ (35b side)
    sub = [0.10, 0.30, 0.50, 0.80, 0.95]                   # class-II / P3 side

    print("=" * 78)
    print("(A) ZOO CLASSIFIER — dominant quadrant + occupancy, avg over phases")
    print("=" * 78)
    for tag, lams in [("SUPERCRITICAL λ→1⁺", sup), ("SUBCRITICAL small-λ", sub)]:
        print(f"\n{tag}")
        print(f"{'λ':>6} {'N':>6} | dom        BL    TR   BRart BRnov  TL   amb")
        for lam in lams:
            for N in Ns_zoo:
                fr, _ = zoo_verdict(lam, N, phis)
                g = lambda k: fr.get(k, 0.0)
                print(f"{lam:>6.2f} {N:>6d} | {dom(fr):<10s} "
                      f"{g('BL'):4.2f} {g('TR'):4.2f} {g('BR_artifact'):5.2f} "
                      f"{g('BR_novel'):4.2f} {g('TL'):4.2f} {g('ambiguous'):4.2f}")

    print("\n" + "=" * 78)
    print("(B) SPECTRAL multi-scale (principal-gap EXCLUDED) — #resolved(>3·unit),")
    print("    decade-spread; along the F_k ladder.  Cantor ⇒ count grows + spread≫0")
    print("=" * 78)
    for tag, lams in [("SUPERCRITICAL λ→1⁺", sup), ("SUBCRITICAL small-λ", sub)]:
        print(f"\n{tag} :  N = {Ns_full}")
        for lam in lams:
            ns = [hierarchy(lam, N, phis)[0] for N in Ns_full]
            sp = hierarchy(lam, Ns_full[-1], phis)[1]
            sl = np.polyfit(np.log(Ns_full), np.log(np.maximum(ns, 0.5)), 1)[0]
            tag2 = ("Cantor-hier" if (sl > 0.25 and sp > 1.0) else
                    "single-scale" if max(ns) < 2 else "marginal")
            print(f"  λ={lam:>5.2f} | #res " +
                  " ".join(f"{x:5.0f}" for x in ns) +
                  f" | slope {sl:5.2f} spread {sp:4.1f}  → {tag2}")

    print("\n" + "=" * 78)
    print("EYEBALL — top 12 unfolded gaps (unit spacing = 1)")
    print("=" * 78)
    for lam, N in [(1.10, 2584), (0.30, 2584), (4.00, 2584), (0.10, 6765)]:
        u = unfolded_levels(lam, N, 0.0)
        d = np.sort(np.diff(u))[::-1][:12]
        print(f"  λ={lam:>5.2f} N={N:5d} : " + " ".join(f"{x:6.1f}" for x in d))

    print("\n" + "=" * 78)
    print("FORK READ: class I on 35b's path  ⇔  35b's near-1 cells are")
    print("BR_artifact-dominated in (A) AND Cantor-hier in (B). Inspect above;")
    print("no auto-verdict this run (v1's auto-verdict was the artifact).")
    print("=" * 78)


if __name__ == "__main__":
    run()
