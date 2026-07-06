"""
cross_substrate/sturmian_run.py — Sturmian-word substrate (Lagrange-class θ-sweep).

The bridge substrate (PROGRESS_REPORT §4 number-theoretic frame). The Sturmian word
of slope α — c_n = ⌊(n+1)α+φ⌋ − ⌊nα+φ⌋ ∈ {0,1} — has its 1-positions (a Beatty
sequence) as the canonical event-train: parameter-side α ↔ spectral-side event-train,
made explicit. Sweep α across Lagrange classes and ask whether the spacing-statistics
fingerprint CLUSTERS by continued-fraction class (the prediction):

  rational (terminating CF, control) · quadratic irrational (eventually-periodic CF —
  metallic means golden/silver/bronze, + √3−1) · transcendental (Liouville: unbounded
  partial quotients; e−2: transcendental but Diophantine/bounded-measure).

Two legs per α: ARS-classify (q-banded I.5q + RF Family III + rep) and matched object-(a)
Family I/II. Flag clustering, don't interpret. Out: coordinates/sturmian.jsonl.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_ROOT, os.path.join(_ROOT, "phase22a")):
    if p not in sys.path:
        sys.path.insert(0, p)

from ars_classify import classify, per_q_columns    # noqa: E402  (q-banded + RF)
from cross_substrate.axes import (                 # noqa: E402
    canonical_spacings, compute_family_I, compute_family_II,
    compute_family_III_from_rf, I1_w1_clock)

N = 400_000          # Sturmian word length; ~Nα events
PHI = np.sqrt(2) / 2  # fixed offset (NNS is φ-invariant for the gap structure)
COORD = os.path.join(_HERE, "coordinates")

# α set with Lagrange / continued-fraction class
_ALPHAS = [
    ("golden", (np.sqrt(5) - 1) / 2, "quadratic", "[0;1,1,1,…] hardest-to-approximate"),
    ("silver", np.sqrt(2) - 1, "quadratic", "[0;2,2,2,…]"),
    ("bronze", (np.sqrt(13) - 3) / 2, "quadratic", "[0;3,3,3,…]"),
    ("sqrt3m1", np.sqrt(3) - 1, "quadratic", "[0;1,2,1,2,…] period-2"),
    ("e_minus_2", np.e - 2, "transcendental_diophantine", "e−2, bounded irrationality measure 2"),
    ("liouville", sum(10.0 ** -e for e in (1, 2, 6, 24, 120, 720)), "transcendental_liouville",
     "Σ10^−k!, unbounded quotients"),
    ("liouville2", sum(2.0 ** -e for e in (1, 2, 6, 24, 120)), "transcendental_liouville",
     "Σ2^−k!, unbounded quotients"),
    ("rational_3_5", 0.6, "rational", "3/5 terminating CF (control; periodic word)"),
]


def sturmian_events(alpha, n, phi=PHI):
    """1-positions of the characteristic Sturmian word of slope α (Beatty seq)."""
    k = np.arange(n + 1, dtype=np.float64)
    fl = np.floor(k * alpha + phi)
    w = np.diff(fl)                       # c_n ∈ {0,1}
    return np.where(w >= 0.5)[0].astype(np.float64)


def circle_crossings(alpha, n, phi=PHI, level=0.5):
    """2nd extraction (for VI.3): upcrossings of `level` by the rotation {nα+φ}."""
    x = (np.arange(n) * alpha + phi) % 1.0
    up = np.where((x[:-1] < level) & (x[1:] >= level))[0]
    return up.astype(np.float64)


def run():
    recs = []
    print(f"STURMIAN θ-sweep (N={N}) — Lagrange-class cluster test")
    print(f"{'α-name':12s} {'class':26s} {'n_ev':>7s} {'I.5q':>6s} {'W1δ':>6s} "
          f"{'q':>5s} {'ρ':>5s} {'VI.3':>7s}")
    for name, alpha, klass, desc in _ALPHAS:
        ev = sturmian_events(alpha, N)
        # leg 1: ARS-classify (q-banded I.5q + RF Family III + rep)
        cl = classify(ev)
        i5q = cl.get("ks_gue_med")
        rf = per_q_columns(cl["per_q"]).get("rf_amp_per_q") if cl.get("per_q") is not None else None
        fIII = compute_family_III_from_rf(rf) if rf is not None and len(rf) >= 7 else {}
        # leg 2: matched object-(a) Family I/II
        fI = compute_family_I(ev) if ev.size >= 20 else {}
        fII = compute_family_II(ev) if ev.size >= 200 else {}
        # VI.3 cross-extraction: W1δ across the 2 extractions
        w1s = [I1_w1_clock(canonical_spacings(ev))]
        cc = circle_crossings(alpha, N)
        if cc.size >= 20:
            w1s.append(I1_w1_clock(canonical_spacings(cc)))
        w1s = [v for v in w1s if v is not None]
        vi3 = float(np.var(w1s)) if len(w1s) >= 2 else None

        axes = {**fI, **fII, **fIII,
                "I.5q_ks_gue_med": float(i5q) if i5q is not None and np.isfinite(i5q) else None,
                "ARS.rep_med": float(cl["rep_med"]) if np.isfinite(cl.get("rep_med", np.nan)) else None,
                "VI.3_cross_extraction_var": vi3}
        recs.append({"substrate": "sturmian", "cell_id": f"{name}_{klass}",
                     "axes_computed": axes,
                     "non_applicable_axes": ["V.1_lyapunov", "V.2_correlation_dim"],
                     "extraction_method": "Sturmian word 1-positions (Beatty); "
                                          "leg1 ARS-classify q-banded+RF, leg2 matched NNS",
                     "extraction_audit": {"alpha": float(alpha), "lagrange_class": klass,
                                          "cf": desc, "N_word": N, "n_events": int(ev.size)},
                     "source_artifact": "generated (deterministic)",
                     "computed_date": date.today().isoformat()})
        def f(v):
            return f"{v:.3f}" if isinstance(v, float) else " - "
        print(f"{name:12s} {klass:26s} {ev.size:>7d} {f(axes['I.5q_ks_gue_med']):>6s} "
              f"{f(fI.get('I.1_w1_clock')):>6s} {f(fI.get('I.8_brody_q')):>5s} "
              f"{f(fI.get('I.9_berry_robnik_rho')):>5s} {f(vi3):>7s}")

    with open(os.path.join(COORD, "sturmian.jsonl"), "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    print(f"\n→ wrote coordinates/sturmian.jsonl ({len(recs)} cells)")
    print("[cluster test] do quadratics (golden/silver/bronze/√3−1) group, and "
          "Liouville separate? flag, don't interpret.")


if __name__ == "__main__":
    run()
