"""
approximability/panel_B_cleanroom.py — Panel B clean-room GATE (must pass before any π number is banked).

B's headline probe is long-range Σ²(L). The tool's Σ² path has an OPEN bug (FIX-2: under-unfold → residual density
trend → σ²≫Poisson — a MAGNITUDE failure that can leave ORDERING intact). So the gate is on MAGNITUDE vs closed forms,
with ordering as an additional hard-fail:

  Σ²_Poisson(L) = L
  Σ²_GUE(L)     = (1/π²)[ ln(2πL) + γ + 1 ]        (Mehta, β=2 bulk; γ=Euler–Mascheroni)
  Σ²_picket(L)  = bounded / oscillating (rigid)     (catches spurious growth the other two can't)

GATE (across the SAME L grid B will use):
  HARD-FAIL if not Σ²_GUE(L) < Σ²_Poisson(L)  →  FIX-2 lands, then retry.
  BANK-GATE: |Σ²_obs − Σ²_closed| ≤ max(3·SE, 3%·closed)  for GUE & Poisson; picket stays bounded.

Validates the estimator B uses (axes.II1_sigma2_at_L) + the unfold (longrange_discriminator.unfold_empirical), and
sweeps the unfold degree so we deploy a degree that actually recovers the closed forms (Phase-5 showed deg-6
under-unfolds semicircle GUE). No signal_gen import (FIX-1 moot). READ-ONLY.
Run: PYTHONPATH=$HOME/fmexplorer/riemann_explorer $HOME/fmexplorer/bin/python3 \
       approximability/panel_B_cleanroom.py
"""
import os, sys, json
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT); sys.path.insert(0, os.path.join(_ROOT, "cross_substrate"))
import numpy as np
from cross_substrate.axes import II1_sigma2_at_L
from cross_substrate.longrange_discriminator import unfold_empirical

GAMMA = 0.5772156649015329
OUT = os.path.dirname(os.path.abspath(__file__))
L_GRID = [2.0, 3.0, 5.0, 8.0, 12.0, 20.0, 30.0, 50.0]


def sigma2_poisson(L): return L
def sigma2_gue(L):     return (1.0 / np.pi**2) * (np.log(2 * np.pi * L) + GAMMA + 1.0)


def gue_eigs(N, seed):
    rng = np.random.default_rng(seed)
    A = (rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))) / np.sqrt(2.0)
    H = (A + A.conj().T) / np.sqrt(2.0)
    return np.sort(np.linalg.eigvalsh(H).real)


def poisson_proc(N, seed):
    rng = np.random.default_rng(seed)
    return np.cumsum(rng.exponential(1.0, N))          # unit mean spacing already


def picket(N):
    return np.arange(N, dtype=float) + 1.0              # perfectly rigid, unit spacing


def sigma2_curve(positions, unfold_deg=None):
    p = np.asarray(positions, float)
    if unfold_deg is not None:
        p = np.sort(unfold_empirical(p, unfold_deg))    # smooth-poly flatten to unit density
    return [II1_sigma2_at_L(p, L) for L in L_GRID]


def bulk_trim(e, frac=0.15):
    n = len(e); lo = int(n * frac); return e[lo:n - lo]


if __name__ == "__main__":
    print("=" * 84)
    print("PANEL B CLEAN-ROOM GATE — Σ²(L) magnitude vs closed forms (ordering = hard-fail)")
    print("=" * 84)
    NSEED = 8
    print(f"\nclosed forms:  Σ²_Poisson(L)=L   Σ²_GUE(L)=(1/π²)[ln(2πL)+γ+1]   (L grid {L_GRID})")

    # ---- Poisson (no unfold needed; already unit density) ----
    N_P = 24000
    P = np.array([sigma2_curve(poisson_proc(N_P, s)) for s in range(NSEED)], float)
    P_mean, P_se = P.mean(0), P.std(0) / np.sqrt(NSEED)

    # ---- picket-fence (rigid control) ----
    pk = np.array(sigma2_curve(picket(24000)), float)

    # ---- GUE: sweep unfold degree to find one that recovers the closed form ----
    N_G = 2600
    print(f"\n[GUE unfold-degree sweep] which poly degree recovers Σ²_GUE? (Phase-5: deg-6 under-unfolds semicircle)")
    print(f"  {'deg':>4s} " + " ".join(f"L={int(L)}".rjust(7) for L in L_GRID))
    print(f"  {'GUE*':>4s} " + " ".join(f"{sigma2_gue(L):.3f}".rjust(7) for L in L_GRID) + "   <- closed form")
    gue_by_deg = {}
    for deg in (6, 10, 14, 20):
        G = np.array([sigma2_curve(bulk_trim(gue_eigs(N_G, s)), unfold_deg=deg) for s in range(NSEED)], float)
        gue_by_deg[deg] = (G.mean(0), G.std(0) / np.sqrt(NSEED))
        print(f"  {deg:>4d} " + " ".join(f"{v:.3f}".rjust(7) for v in G.mean(0)))

    # pick the degree whose GUE curve is closest to the closed form (median relative error)
    gue_star = np.array([sigma2_gue(L) for L in L_GRID])
    best_deg = min(gue_by_deg, key=lambda d: np.median(np.abs(gue_by_deg[d][0] - gue_star) / gue_star))
    G_mean, G_se = gue_by_deg[best_deg]
    print(f"\n  → best unfold degree = {best_deg} (deploy this for B's spectra)")

    # ---- the gate table ----
    print(f"\n{'L':>5s} {'Σ²_Pois obs':>12s} {'(L)':>6s} {'Σ²_GUE obs':>11s} {'GUE*':>7s} {'picket':>7s} {'order?':>7s} {'mag?':>6s}")
    def tol_ok(obs, se, closed):
        return abs(obs - closed) <= max(3 * se, 0.03 * closed)
    ordering_ok = True; poisson_mag_ok = True; gue_mag_ok = True; picket_ok = True
    for i, L in enumerate(L_GRID):
        po, pse = P_mean[i], P_se[i]; go, gse = G_mean[i], G_se[i]; pk_i = pk[i]
        o_ok = go < po; m_p = tol_ok(po, pse, sigma2_poisson(L)); m_g = tol_ok(go, gse, sigma2_gue(L))
        ordering_ok &= o_ok; poisson_mag_ok &= m_p; gue_mag_ok &= m_g
        if abs(pk_i) > 0.5: picket_ok = False
        print(f"{L:>5g} {po:>12.3f} {sigma2_poisson(L):>6.1f} {go:>11.3f} {sigma2_gue(L):>7.3f} "
              f"{pk_i:>7.3f} {'✓' if o_ok else '✗FAIL':>7s} {('P' if m_p else 'p')+('G' if m_g else 'g'):>6s}")

    print("\n" + "-" * 60)
    print(f"  ORDERING (Σ²_GUE < Σ²_Poisson, hard-fail):     {'PASS ✓' if ordering_ok else 'FAIL ✗ → land FIX-2, retry'}")
    print(f"  MAGNITUDE Poisson (≤max(3SE,3%)):              {'PASS ✓' if poisson_mag_ok else 'FAIL ✗'}")
    print(f"  MAGNITUDE GUE (≤max(3SE,3%), deg={best_deg}):         {'PASS ✓' if gue_mag_ok else 'FAIL ✗'}")
    print(f"  PICKET bounded (|Σ²|<0.5, rigidity detected):  {'PASS ✓' if picket_ok else 'FAIL ✗'}")
    gate = ordering_ok and poisson_mag_ok and gue_mag_ok and picket_ok
    print(f"\n  === CLEAN-ROOM GATE: {'PASS — B may bank Σ² numbers (deploy deg=%d)' % best_deg if gate else 'FAIL — do NOT bank π; fix first'} ===")

    with open(os.path.join(OUT, "panel_B_cleanroom.json"), "w") as fh:
        json.dump({"L_grid": L_GRID, "best_unfold_deg": int(best_deg),
                   "poisson_obs": P_mean.tolist(), "poisson_se": P_se.tolist(),
                   "gue_obs": G_mean.tolist(), "gue_se": G_se.tolist(),
                   "gue_closed": gue_star.tolist(), "picket_obs": pk.tolist(),
                   "gate_pass": bool(gate), "ordering_ok": bool(ordering_ok),
                   "poisson_mag_ok": bool(poisson_mag_ok), "gue_mag_ok": bool(gue_mag_ok)}, fh, indent=2)
    print("  wrote approximability/panel_B_cleanroom.json")
