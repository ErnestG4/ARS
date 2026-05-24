"""
cross_substrate/calibration_anchors.py — explicit GOE/GUE/GSE/Poisson/clock landscape anchors.

The program has used GUE / GOE / Poisson as *theoretical* reference classes throughout but never
banked them as explicit landscape POINTS with computed fingerprint coordinates. This generates the
canonical classes (calibrator zoo: β-ensemble eigenvalues, Poisson, near-clock, uniform-jitter) and
fingerprints them on the SAME instrument every substrate uses — I.5q (ars_classify), Family I
(W1δ / I.5 / Brody q / BR ρ via unfold_unit_mean), Family II (Σ²/Δ₃/K) — averaged over seeds.

These are the landscape "corners": GUE (q≈1, ρ≈1, I.5 low), Poisson (q≈0, far-from-GUE), clock
(W1δ≈0), GOE/GSE intermediate. A clean comparison baseline for every measured substrate, and a
re-validation of the instrument (do the canonical classes land where theory says?).

Out: coordinates/calibration-anchors.jsonl.  Run: --run.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import sys
from datetime import date

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_ROOT, os.path.join(_ROOT, "phase22a")):
    if p not in sys.path:
        sys.path.insert(0, p)

from ars_classify import classify, unfold_unit_mean                  # noqa: E402
from cross_substrate.axes import (canonical_spacings, FAMILY_I,      # noqa: E402
                                   compute_family_II)
from signal_gen import make_beta_ensemble_eigenvalues, make_uniform_jitter  # noqa: E402
from extractor_distinctness import _gen_poisson                      # noqa: E402

COORD = os.path.join(_HERE, "coordinates")
N = 3000
N_SEEDS = 6

# (name, expected, generator(seed) -> event/eigenvalue sequence)
CLASSES = [
    ("clock",   "W1δ→0, rigid", lambda s: np.arange(N) + 1.0 + 0.0),
    ("GUE_b2",  "q≈1 ρ≈1 (GUE)", lambda s: make_beta_ensemble_eigenvalues(N, 2, s)),
    ("GOE_b1",  "intermediate-Wigner", lambda s: make_beta_ensemble_eigenvalues(N, 1, s)),
    ("GSE_b4",  "strong-repulsion", lambda s: make_beta_ensemble_eigenvalues(N, 4, s)),
    ("uniform_jitter", "BR-regime", lambda s: make_uniform_jitter(N, 0.10, s)),
    ("poisson", "q≈0, far-from-GUE", lambda s: _gen_poisson(s, n=N)),
]


def _f(v):
    return None if v is None or not np.isfinite(v) else float(v)


def _fingerprint(events):
    cl = classify(events)
    i5q = cl.get("ks_gue_med") if isinstance(cl, dict) else None
    pos = unfold_unit_mean(events)
    s = canonical_spacings(pos)
    fI = {k: _f(fn(s) if k != "_" else None) for k, fn in FAMILY_I.items()}
    fII = {k: _f(v) if isinstance(v, (int, float)) else None
           for k, v in compute_family_II(pos).items()}
    return {"I.5q_ks_gue_med": _f(i5q), **fI, **fII}


def run():
    print(f"CALIBRATION ANCHORS — canonical classes, N={N}, {N_SEEDS} seeds, same instrument as substrates")
    print(f"{'class':16s} {'I.5q':>6s} {'I.5':>6s} {'W1δ':>6s} {'Brody q':>8s} {'BR ρ':>6s} {'Σ²':>8s}")
    recs = []
    for name, expected, gen in CLASSES:
        seeds = [_fingerprint(np.asarray(gen(s), float)) for s in range(N_SEEDS)]
        keys = seeds[0].keys()
        mean = {k: (float(np.mean([d[k] for d in seeds if d[k] is not None]))
                    if any(d[k] is not None for d in seeds) else None) for k in keys}
        std = {k: (float(np.std([d[k] for d in seeds if d[k] is not None]))
                   if any(d[k] is not None for d in seeds) else None) for k in keys}
        recs.append({"substrate": "calibration-anchor", "cell_id": name,
                     "axes_computed": mean,
                     "extraction_method": f"canonical {name} (calibrator zoo), N={N}, {N_SEEDS}-seed mean; "
                                          f"ars_classify I.5q + unfold_unit_mean Family I/II — same instrument as substrates",
                     "extraction_audit": {"expected": expected, "N": N, "n_seeds": N_SEEDS,
                                          "axes_std": std},
                     "source_artifact": "generated (calibrator zoo)",
                     "computed_date": date.today().isoformat()})
        def g(k):
            v = mean.get(k)
            return f"{v:.3f}" if isinstance(v, float) else "  -"
        print(f"{name:16s} {g('I.5q_ks_gue_med'):>6s} {g('I.5_ks_gue'):>6s} {g('I.1_w1_clock'):>6s} "
              f"{g('I.8_brody_q'):>8s} {g('I.9_berry_robnik_rho'):>6s} {g('II.1_sigma2_L'):>8s}")

    with open(os.path.join(COORD, "calibration-anchors.jsonl"), "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    print(f"\n→ {len(recs)} anchors banked. (Instrument re-validation: do GUE→q≈1, Poisson→q≈0, clock→W1δ≈0?)")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args()
    if a.run:
        run()
    else:
        ap.error("need --run")


if __name__ == "__main__":
    main()
