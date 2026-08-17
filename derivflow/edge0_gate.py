#!/usr/bin/env python3
"""EDGE-0: can the instrument read the EDGE at all?  (exploratory, unsealed)

Prompted by A. Campbell (corr. 2026-08-17): "on a local level the roots should
crystalize (and pretty quickly) in the bulk and form a specific structure at the
edge."  Every number this project has banked is the central 20% bulk window.
Before measuring the edge we have to know the readout survives there, because the
edge is precisely where it is weakest: the unfolding divides by a predicted
density that vanishes at the spectrum edge, and BOTH permanent calibrators
(reference_v2_gates.py) were validated in the bulk only.

METHOD — the existing Gate H, with the window swapped.  Push a Hermite seed
through the FULL empirical-reference path and compare against exact H_{n-k}
truth (exact roots, exact semicircle unfolding, identical window).  Hermite is
the right probe because the answer is known at every k.  A lattice seed is run
as the second, maximally-rippled input for the same reason it is in Gate L.

ACCEPTANCE RULE, STATED BEFORE THE RUN.  Reporting a raw tolerance would be a
number invented after seeing the answer, so the rule is relative to signal, the
same floor-vs-signal logic as scope §6.iv-a:

    the edge readout is USABLE at a given k iff
        |pipeline - exact truth|  <  0.10 x (the exact-truth signal at that k)

i.e. the instrument's own distortion must be under 10% of the thing being
measured.  Anything above that is reported as NOT USABLE at that k and no edge
science is run there.  We expect degradation with k as the reference smooths;
the question is where it crosses.

CROSS-CHECK THAT NEEDS NO REFERENCE AT ALL.  <r~> is a ratio of ADJACENT gaps,
so a smooth density cancels to first order — this is why Oganesyan-Huse
introduced it.  We therefore also report the RAW (un-unfolded) gap ratio at the
edge.  If raw and unfolded agree, the density reference is not driving the
answer, which is the strongest statement available here.

Not part of the sealed protocol.  Its RNG is a separate master seed so it can
never collide with the sealed children (0-127 under SeedSequence(20260811)).
"""
import json
import os
import sys
import time

import numpy as np
from scipy.special import roots_hermite

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

from track0_harness import diff_step, bulk_idx, rtilde, unfold_semicircle  # noqa: E402
from free_conv import F_empirical                                          # noqa: E402
from track0_iid_scaling import reference_cdf                               # noqa: E402

N = 4096
KS = [1, 2, 4, 8, 16]
EDGE_FRACS = [0.05, 0.02]      # per side; 0.05 mirrors the bulk's 20% in count
USABLE_RATIO = 0.10            # pre-stated acceptance rule
MIN_SPACINGS = 64              # the harness's own readout power floor


def edge_idx(m, frac):
    """Outermost `frac` of the roots at EACH end, as one index array."""
    w = max(2, int(np.ceil(frac * m)))
    return np.concatenate([np.arange(0, w), np.arange(m - w, m)])


def _ratio_on(u, idx, m):
    """1 - <r~> computed on each end separately, then averaged, so the two ends
    are never joined across the middle (that gap is not a spacing)."""
    w = len(idx) // 2
    vals = []
    for half in (idx[:w], idx[w:]):
        d = np.diff(u[half])
        if len(d) >= 2:
            vals.append(1.0 - rtilde(d))
    return float(np.mean(vals)) if vals else None, 2 * (w - 1)


def run():
    out = {"gate": "EDGE-0 edge readability", "scope": __doc__.split("\n")[0],
           "n": N, "ks": KS, "edge_fracs": EDGE_FRACS,
           "usable_ratio": USABLE_RATIO, "rows": [], "verdict": None}
    t0 = time.time()

    for label, seed in (("hermite", roots_hermite(N)[0]),
                        ("lattice", np.linspace(-1.0, 1.0, N))):
        r = seed.copy()
        for k in range(1, max(KS) + 1):
            r = diff_step(r)
            if k not in KS:
                continue
            m = N - k
            F_at, diag = reference_cdf(F_empirical(seed), r, k / N, m)
            u_pipe = F_at * m

            exact = roots_hermite(m)[0] if label == "hermite" else None
            u_exact = unfold_semicircle(exact, m) if exact is not None else None

            for frac in EDGE_FRACS:
                idx = edge_idx(m, frac)
                pipe, nsp = _ratio_on(u_pipe, idx, m)
                raw, _ = _ratio_on(r, idx, m)            # NO unfolding at all
                row = {"seed": label, "k": k, "frac": frac, "n_spacings": nsp,
                       "powered": nsp >= MIN_SPACINGS,
                       "pipeline": pipe, "raw_unnormalised": raw,
                       "bulk_pipeline": 1.0 - rtilde(np.diff(u_pipe[bulk_idx(m)])),
                       "eps": diag["eps"]}
                if u_exact is not None:
                    truth, _ = _ratio_on(u_exact, idx, m)
                    row["exact_truth"] = truth
                    row["abs_diff"] = abs(pipe - truth)
                    row["usable"] = bool(row["abs_diff"] < USABLE_RATIO * abs(truth))
                out["rows"].append(row)
                msg = (f"{label:8s} k={k:<3d} edge{frac:.2f} "
                       f"pipe={pipe:.4e} raw={raw:.4e}")
                if u_exact is not None:
                    msg += (f" truth={row['exact_truth']:.4e} "
                            f"diff={row['abs_diff']:.2e} "
                            f"{'USABLE' if row['usable'] else 'NOT-USABLE'}")
                print(msg, flush=True)

    herm = [r for r in out["rows"] if r["seed"] == "hermite"]
    usable = [r for r in herm if r.get("usable")]
    out["verdict"] = ("EDGE_READABLE" if len(usable) == len(herm) else
                      "EDGE_PARTIALLY_READABLE" if usable else "EDGE_NOT_READABLE")
    out["usable_k"] = sorted({r["k"] for r in usable})
    out["runtime_s"] = round(time.time() - t0, 1)
    with open(os.path.join(_HERE, "edge0_gate.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"\nVERDICT: {out['verdict']}  usable k = {out['usable_k']}  "
          f"({out['runtime_s']:.0f}s)")
    return out


if __name__ == "__main__":
    run()
