"""
cross_substrate/mackey_glass_run.py — Mackey-Glass substrate (breadth).

Known-chaos anchor with a τ-sweep trajectory (substrate-as-trajectory, like
Kuramoto). Gives the landscape its first Family V (dynamical) coordinates.

Per regime τ: integrate the DDE → extract events (local-maxima primary) →
unfold to unit-mean → Family I/II; Family V (Lyapunov λ₁, corr-dim D₂) on the
trajectory; VI.3 cross-extraction variance across the 3 extractors. The τ-sweep
spans stable → periodic → period-doubled → chaotic → deeper-chaos.

Reuses the existing integrator + extractors in transition_calibrators_dynamical.
Out: coordinates/mackey-glass.jsonl + console (with Family V validation: λ₁
should be ≤0 for stable/periodic, >0 for chaotic — known-truth check).
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
    mackey_glass, mackey_glass_to_events, MACKEY_GLASS_REGIMES)
from cross_substrate.axes import (                # noqa: E402
    canonical_spacings, compute_family_I, compute_family_II,
    I1_w1_clock, V1_lyapunov, V2_correlation_dim)

DT = 0.1
N_STEPS = 300_000
EXTRACTORS = ["local_maxima_prominence", "running_mean_upcrossings",
              "envelope_upcrossings"]
COORD = os.path.join(_HERE, "coordinates")


def run():
    recs = []
    for name, tau, desc in MACKEY_GLASS_REGIMES:
        x = mackey_glass(tau, N_STEPS, dt=DT)
        # primary extractor → event times → Family I/II
        ev = mackey_glass_to_events(x, "local_maxima_prominence")
        times = np.sort(ev) * DT
        s = canonical_spacings(times) if times.size >= 20 else np.zeros(0)
        fI = compute_family_I(times) if times.size >= 20 else {}
        fII = compute_family_II(times) if times.size >= 200 else {}
        # Family V on the trajectory (the dynamical axes)
        lam = V1_lyapunov(x, dt=DT)
        d2 = V2_correlation_dim(x)
        # VI.3 cross-extraction variance: W1δ across the 3 extractors
        w1s = []
        for ex in EXTRACTORS:
            e2 = np.sort(mackey_glass_to_events(x, ex)) * DT
            v = I1_w1_clock(canonical_spacings(e2)) if e2.size >= 20 else None
            if v is not None:
                w1s.append(v)
        vi3 = float(np.var(w1s)) if len(w1s) >= 2 else None

        axes = {**fI, **fII, "V.1_lyapunov": lam, "V.2_correlation_dim": d2,
                "VI.3_cross_extraction_var": vi3}
        recs.append({
            "substrate": "mackey-glass", "cell_id": f"tau{tau:g}_{name}",
            "axes_computed": axes,
            "non_applicable_axes": ["III.1_p2"],  # no arithmetic index
            "extraction_method": "DDE Euler dt=0.1; events=local-maxima(prominence); "
                                 "unit-mean unfold",
            "extraction_audit": {"tau": tau, "regime": desc, "n_steps": N_STEPS,
                                 "n_events": int(times.size),
                                 "beta": 0.2, "gamma": 0.1, "n_pow": 10.0,
                                 "extractors_for_VI3": EXTRACTORS},
            "source_artifact": "transition_calibrators_dynamical.mackey_glass (regenerable)",
            "computed_date": date.today().isoformat()})
        w1 = fI.get("I.1_w1_clock")
        print(f"  τ={tau:>4g} {name:14s} n_ev={times.size:>5d}  "
              f"W1δ={w1:.3f}" if isinstance(w1, float) else
              f"  τ={tau:>4g} {name:14s} n_ev={times.size:>5d}  W1δ=NA",
              f" λ₁={lam:+.4f}" if isinstance(lam, float) else " λ₁=NA",
              f" D₂={d2:.2f}" if isinstance(d2, float) else " D₂=NA",
              f" VI.3={vi3:.4f}" if isinstance(vi3, float) else " VI.3=NA")

    # Family V known-truth validation (sign/ordering)
    lams = {r["cell_id"]: r["axes_computed"].get("V.1_lyapunov") for r in recs}
    print("\n[Family V validation] λ₁ should be ≤~0 for stable/periodic, >0 chaotic:")
    for cid, l in lams.items():
        print(f"   {cid:22s} λ₁ = {l}")

    with open(os.path.join(COORD, "mackey-glass.jsonl"), "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    print(f"\n→ wrote coordinates/mackey-glass.jsonl ({len(recs)} cells)")


if __name__ == "__main__":
    run()
