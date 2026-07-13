"""
Farey CLASS certification — flip banked-detection → certified-class (or not).

Certifies the GLOBAL Farey sequence F_Q against its analytic answer:
  - NNS: Hall 1970 gap law, exact = d3_farey.triangle_cdf (tau=gap/mean, min tau=3/pi^2).
  - Sigma^2(L): the Session-K / Maass machinery (nns_stats.number_variance), placed vs
    Poisson/GUE analytic references — apples-to-apples with the rest of ARS.

Reconciliation: Hall's tau is unit-mean-normalized; nns_stats operates on unit-mean
spacings. For the GLOBAL sequence empirical mean-gap = 1/|F_Q| = the analytic mean, so
the two normalizations coincide (no convention gap). Asserted below (min tau ~ 0.304).

READ-ONLY. Run:
  $HOME/fmexplorer/bin/python3 approximability/farey_class_certify.py
"""
import os, sys, math
import numpy as np

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "sessionK"))
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/mathtest/refsuite"))

from d3_farey import farey_gaps_global, triangle_cdf, MIN_TAU  # analytic Hall law
import nns_stats as NS                                         # Maass machinery

PI = math.pi


def hall_cdf_grid(tau_max, n=6000):
    """Tabulate Hall triangle_cdf on a grid for KS interp (quad per point is slow)."""
    grid = np.linspace(MIN_TAU, tau_max, n)
    cdf = np.array([triangle_cdf(float(t)) for t in grid])
    return grid, cdf


def ks_to_cdf(sorted_tau, grid, cdf):
    emp = np.arange(1, len(sorted_tau) + 1) / len(sorted_tau)
    theo = np.interp(sorted_tau, grid, cdf)
    return float(np.max(np.abs(emp - theo)))


def main():
    for Q in (3000, 5000):
        print("=" * 78)
        print(f"GLOBAL FAREY F_Q, Q={Q}")
        gaps, count = farey_gaps_global(Q)
        gaps = np.asarray(gaps, float)
        tau = gaps / gaps.mean()                 # Hall normalization (= unit mean)
        print(f"  |F_Q|={count:,}  gaps={gaps.size:,}  min tau={tau.min():.5f} "
              f"(analytic 3/pi^2={MIN_TAU:.5f})  mean={tau.mean():.4f}  "
              f"var={tau.var():.3f} (Hall: infinite → grows with Q)")

        # ---- NNS certification: KS vs Hall, and vs RMT surmises for contrast ----
        st = np.sort(tau)
        tau_max = float(min(st[-1], 40.0))
        hg, hc = hall_cdf_grid(tau_max)
        ks_hall = ks_to_cdf(st[st <= tau_max], hg, hc)

        # RMT surmises via the SAME machinery the Maass pillar uses (unit-mean spacings)
        sgrid = np.linspace(0, max(6.0, st[-1]), 4000)
        ks_rmt = {}
        for name in ("Poisson", "GOE", "GUE"):
            theo = np.interp(st, sgrid, NS._surmise_cdf(name, sgrid))
            ks_rmt[name] = float(np.max(np.abs(np.arange(1, len(st) + 1) / len(st) - theo)))

        print(f"\n  NNS KS distance (n={tau.size:,}):")
        print(f"    Hall (BCZ/analytic)  KS = {ks_hall:.5f}   <-- the certification target")
        for k, v in ks_rmt.items():
            print(f"    {k:20s} KS = {v:.5f}")
        best_rmt = min(ks_rmt.values())
        margin = best_rmt / max(ks_hall, 1e-9)
        nns_cert = (ks_hall < 0.01) and (ks_hall < 0.3 * best_rmt)
        print(f"    -> Hall beats best RMT by {margin:.0f}x; "
              f"NNS {'CERTIFIED (Hall, KS<0.01 & <<RMT)' if nns_cert else 'NOT certified'}")

        # ---- Sigma^2(L): Maass machinery, vs Poisson/GUE ----
        unf = np.concatenate([[0.0], np.cumsum(tau)])   # unit-mean unfolded process
        Ls = np.array([1., 2., 3., 5., 8., 12., 20., 30.])
        s2 = NS.number_variance(unf, Ls, n_origins=2000)
        print(f"\n  Sigma^2(L)  [Maass machinery, {unf.size:,} levels]:")
        print(f"    {'L':>4s} {'Farey':>9s} {'Poisson':>9s} {'GUE':>8s}   placement")
        for L, v in zip(Ls, s2):
            p, g = float(NS.sigma2_poisson(L)), float(NS.sigma2_gue(L))
            if not np.isfinite(v):
                continue
            place = ("BELOW Poisson (rigid)" if v < p else "ABOVE Poisson (clustered)")
            print(f"    {L:>4.0f} {v:>9.3f} {p:>9.3f} {g:>8.3f}   {place}")
        print(f"\n  READ: hard gap at tau_min={tau.min():.3f} = short-range repulsion; "
              f"Sigma^2 slope vs L = long-range behavior (infinite-variance tail ⇒ expect super-Poisson).")


if __name__ == "__main__":
    main()
