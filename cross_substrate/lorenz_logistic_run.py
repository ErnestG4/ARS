"""
cross_substrate/lorenz_logistic_run.py — Lorenz + logistic substrates (breadth).

Two more dynamical anchors with trajectories:
  - Lorenz (3D continuous flow): ρ-sweep stable→chaotic; lobe-transition events;
    Family V via Rosenstein λ₁ + GP D₂ on x(t). Known truth: ρ=28 → λ₁≈0.906, D₂≈2.06.
  - Logistic (1D map): r-sweep period-doubling route; IEI events. Family V λ is
    ANALYTIC (λ=⟨ln|r(1−2x)|⟩, exact for a map — the right tool, and a crisp
    known-truth check: r=4→ln2; the period-3 window at r=3.83 has λ<0 inside chaos).

Out: coordinates/lorenz.jsonl + coordinates/logistic.jsonl, with Family V validation.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from transition_calibrators_dynamical import (   # noqa: E402
    lorenz_integrate, lorenz_lobe_transition_events,
    logistic_iterate, logistic_to_events, LOGISTIC_REGIMES)
from cross_substrate.axes import (                # noqa: E402
    canonical_spacings, compute_family_I, compute_family_II,
    I1_w1_clock, V1_lyapunov, V2_correlation_dim)

COORD = os.path.join(_HERE, "coordinates")
LORENZ_RHO = [(20.0, "stable"), (28.0, "classic_chaos"), (35.0, "chaos"), (40.0, "chaos_hi")]


def lorenz_lyapunov_benettin(rho, sigma=10.0, beta=8.0 / 3.0, dt=0.01,
                             n_steps=200_000, discard=20_000):
    """Largest Lyapunov via tangent-space (Benettin) on the Lorenz ODE —
    correct sign + magnitude (validated ρ=28→0.909 vs known 0.906; stable→<0)."""
    s = np.array([1.0, 1.0, 1.0]); d = np.array([1e-8, 0.0, 0.0]); d0 = np.linalg.norm(d)

    def f(s):
        x, y, z = s
        return np.array([sigma * (y - x), x * (rho - z) - y, x * y - beta * z])

    def J(s):
        x, y, z = s
        return np.array([[-sigma, sigma, 0.0], [rho - z, -1.0, -x], [y, x, -beta]])

    for _ in range(discard):
        k1 = f(s); k2 = f(s + .5 * dt * k1); k3 = f(s + .5 * dt * k2); k4 = f(s + dt * k3)
        s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    lsum = 0.0
    for _ in range(n_steps):
        def fd(s, d):
            return f(s), J(s) @ d
        a1, b1 = fd(s, d); a2, b2 = fd(s + .5 * dt * a1, d + .5 * dt * b1)
        a3, b3 = fd(s + .5 * dt * a2, d + .5 * dt * b2); a4, b4 = fd(s + dt * a3, d + dt * b3)
        s = s + dt / 6 * (a1 + 2 * a2 + 2 * a3 + a4)
        d = d + dt / 6 * (b1 + 2 * b2 + 2 * b3 + b4)
        nd = np.linalg.norm(d); lsum += np.log(nd / d0); d = d * (d0 / nd)
    return lsum / (n_steps * dt)


def logistic_lyapunov(r, x0=0.5, n=200_000, discard=2000):
    """Analytic Lyapunov of the logistic map: λ = ⟨ln|f'(x)|⟩, f'=r(1−2x). Exact."""
    x = x0
    for _ in range(discard):
        x = r * x * (1.0 - x)
    s = 0.0
    for _ in range(n):
        s += np.log(abs(r * (1.0 - 2.0 * x)) + 1e-300)
        x = r * x * (1.0 - x)
    return s / n


def _rec(substrate, cell_id, axes, method, audit):
    return {"substrate": substrate, "cell_id": cell_id, "axes_computed": axes,
            "non_applicable_axes": ["III.1_p2"], "extraction_method": method,
            "extraction_audit": audit,
            "source_artifact": "transition_calibrators_dynamical (regenerable)",
            "computed_date": date.today().isoformat()}


def run_lorenz():
    recs = []
    print("LORENZ (ρ-sweep) — known: ρ=28 λ₁≈0.906, D₂≈2.06")
    for rho, desc in LORENZ_RHO:
        traj = lorenz_integrate(rho, 100_000, dt=0.01)
        xc = traj[:, 0]
        ev = lorenz_lobe_transition_events(traj)
        fI = compute_family_I(ev) if ev.size >= 20 else {}
        fII = compute_family_II(ev) if ev.size >= 200 else {}
        lam = lorenz_lyapunov_benettin(rho)        # tangent-space (known equations)
        d2 = V2_correlation_dim(xc)
        axes = {**fI, **fII, "V.1_lyapunov": lam, "V.2_correlation_dim": d2}
        recs.append(_rec("lorenz", f"rho{rho:g}_{desc}", axes,
                         "RK4 dt=0.01; events=lobe-transitions(x sign); unit-mean",
                         {"rho": rho, "regime": desc, "sigma": 10.0, "beta": 8 / 3,
                          "n_events": int(ev.size)}))
        w1 = fI.get("I.1_w1_clock")
        print(f"  ρ={rho:>4g} {desc:14s} n_ev={ev.size:>5d} "
              f"W1δ={w1:.3f}" if isinstance(w1, float) else
              f"  ρ={rho:>4g} {desc:14s} n_ev={ev.size:>5d} W1δ=NA",
              f"λ₁={lam:+.3f}" if isinstance(lam, float) else "λ₁=NA",
              f"D₂={d2:.2f}" if isinstance(d2, float) else "D₂=NA")
    _write("lorenz", recs)


def run_logistic():
    recs = []
    print("\nLOGISTIC (r-sweep) — analytic λ: periodic<0, chaos(3.7)>0, period-3-window(3.83)<0")
    for name, r, desc in LOGISTIC_REGIMES:
        x = logistic_iterate(r, 0.5, 200_000)
        ev = logistic_to_events(x, "iei")
        fI = compute_family_I(ev) if ev.size >= 20 else {}
        fII = compute_family_II(ev) if ev.size >= 200 else {}
        lam = logistic_lyapunov(r)                  # analytic (exact for the map)
        d2 = V2_correlation_dim(x, emb_dim=4)       # GP on the map series (low-D)
        # VI.3 cross-extraction across the 3 logistic event modes
        w1s = [I1_w1_clock(canonical_spacings(logistic_to_events(x, m)))
               for m in ("iei", "cumsum", "index")]
        w1s = [v for v in w1s if v is not None]
        vi3 = float(np.var(w1s)) if len(w1s) >= 2 else None
        axes = {**fI, **fII, "V.1_lyapunov": float(lam),
                "V.2_correlation_dim": d2, "VI.3_cross_extraction_var": vi3}
        recs.append(_rec("logistic", f"r{r:g}_{name}", axes,
                         "1D map; events=IEI; V.1 ANALYTIC λ=⟨ln|r(1-2x)|⟩",
                         {"r": r, "regime": desc, "n_events": int(ev.size),
                          "lyapunov_method": "analytic"}))
        w1 = fI.get("I.1_w1_clock")
        print(f"  r={r:>5g} {name:11s} n_ev={ev.size:>5d} "
              f"W1δ={w1:.3f}" if isinstance(w1, float) else
              f"  r={r:>5g} {name:11s} n_ev={ev.size:>5d} W1δ=NA",
              f"λ(analytic)={lam:+.4f} D₂={d2:.2f}" if isinstance(d2, float)
              else f"λ(analytic)={lam:+.4f} D₂=NA")
    _write("logistic", recs)


def _write(sub, recs):
    with open(os.path.join(COORD, f"{sub}.jsonl"), "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    print(f"  → wrote coordinates/{sub}.jsonl ({len(recs)} cells)")


if __name__ == "__main__":
    run_lorenz()
    run_logistic()
