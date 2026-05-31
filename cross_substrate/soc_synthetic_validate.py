"""
cross_substrate/soc_synthetic_validate.py — calibrate the local-rate-unfold discriminator on ground truth.

The new discriminator (fact #3): clustering that SURVIVES local-rate unfolding = genuine triggering
memory; clustering that COLLAPSES to the inhomogeneous-Poisson floor (mass<0.3~0.26, CV~1) = rate
envelope only. Before banking it as a discriminator, validate it on synthetic processes with KNOWN
memory and KNOWN rate envelope (synthetic-validate-fitters discipline — a new discriminator needs its
own calibrator).

Three ground-truth processes, all with the SAME sinusoidal rate envelope (mimicking the ~11yr solar
cycle / ~20x flare-rate modulation):
  A. inhomogeneous Poisson, NO memory      -> unfold MUST collapse to floor (CV->1). If not, false +.
  B. Hawkes, memory + envelope (branch 0.5) -> unfold MUST keep CV>1 (memory survives). If not, false -.
  C. Hawkes, strong memory (branch 0.8)     -> unfold keeps even more.
Plus a duplicate-contamination control:
  D. process A with each event duplicated at +/- a few seconds (FRM-style) -> shows duplicates create
     fake surviving-clustering that unfold CANNOT remove (coincident -> same local rate). This is why
     the GOES FRM dedup had to happen BEFORE the unfold, not be fixed by it.

Pass criteria: the unfolded readout separates A (->floor) from B,C (stay above floor) across bandwidths,
AND D exposes that duplicate contamination masquerades as surviving memory (motivating the dedup gate).
"""
from __future__ import annotations

import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
for p in (_HERE, os.path.dirname(_HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import comcat_port as CP                                                    # noqa: E402

T = 29 * 365.25 * 86400.0          # 29-yr span, matched to GOES
CYCLE = 11 * 365.25 * 86400.0      # solar-cycle period
DAY = 86400.0


def envelope(t, base, amp):
    """Sinusoidal rate envelope λ(t) = base*(1 + amp*(1+sin)/2-ish), >=0, ~20x peak/trough like solar."""
    s = 0.5 * (1 + np.sin(2 * np.pi * t / CYCLE))
    return base * (0.05 + s)        # trough ~0.05*base, peak ~1.05*base => ~20x modulation


def inhomogeneous_poisson(base, amp, rng):
    """Thinning: homogeneous at λmax, keep with prob λ(t)/λmax. NO memory."""
    lam_max = base * 1.05
    n_prop = rng.poisson(lam_max * T)
    tp = np.sort(rng.uniform(0, T, n_prop))
    keep = rng.uniform(size=tp.size) < (envelope(tp, base, amp) / lam_max)
    return tp[keep]


def hawkes(base, amp, branch, decay_s, rng, max_events=2_000_000):
    """Inhomogeneous-background Hawkes via thinning. Background = envelope() ; each event adds an
    exponential self-excitation kernel branch*decay*exp(-decay*dt). branch = branching ratio (memory
    strength, <1 for stability); decay_s = memory timescale. Returns sorted event times."""
    decay = 1.0 / decay_s
    lam_bg_max = base * 1.05
    events = []
    t = 0.0
    # upper bound on intensity for thinning: bg_max + branch*decay*(current active sum). We track the
    # decaying excitation sum S(t) and use lam_max = bg_max + branch*decay*S as a local bound.
    S = 0.0
    last = 0.0
    while t < T and len(events) < max_events:
        S *= np.exp(-decay * (t - last)); last = t
        lam_max = lam_bg_max + branch * decay * S + branch * decay  # +slack for the next possible event
        dt = rng.exponential(1.0 / lam_max)
        t += dt
        if t >= T:
            break
        S *= np.exp(-decay * (t - last)); last = t
        lam = envelope(t, base, amp) + branch * decay * S
        if rng.uniform() < lam / lam_max:
            events.append(t)
            S += 1.0                     # new event contributes one unit to the excitation sum
    return np.array(events)


def readout(times, label, Ws=(5, 7, 11, 21, 51, 101)):
    # NB: include small W (5,7). The unfold estimator's floor is BELOW CV=1 at small W even for the
    # no-memory process A — short windows over-fit fluctuation as rate. A small-W CV<1 is therefore NOT
    # evidence of regularity; it must be read against process A's small-W floor, not against CV=1.
    times = np.sort(np.asarray(times, float))
    n = times.size
    homo = CP.clustering_readout(times)
    line = f"  {label:28s} n={n:7d}  HOMO mass<.3={homo['mass_lt_0p3']:.3f} CV={homo['cv']:5.2f}  | unfolded:"
    unf = {}
    for W in Ws:
        su = CP.local_rate_unfold(times, W)
        c = CP.clustering_from_spacings(su) if su is not None else None
        unf[W] = c
        if c:
            line += f" W{W}:CV={c['cv']:.2f}"
    print(line)
    return homo, unf


def duplicate_contaminate(times, frac=0.8, jitter_s=3.0, rng=None):
    """FRM-style: re-detect a fraction of flares at peaktime +/- a few seconds (near-coincident dup)."""
    rng = rng or np.random.default_rng(0)
    mask = rng.uniform(size=times.size) < frac
    dups = times[mask] + rng.uniform(-jitter_s, jitter_s, mask.sum())
    return np.sort(np.concatenate([times, dups]))


def main():
    rng = np.random.default_rng(7)
    base = 200_000 / T            # ~GOES-clean rate scale (tune so n is comparable)
    amp = 1.0
    print("SYNTHETIC VALIDATION of the local-rate-unfold memory discriminator")
    print("(floor: inhom-Poisson -> unfolded CV~1.0, mass<.3~0.26; memory -> CV stays >1)\n")

    A = inhomogeneous_poisson(base, amp, rng)
    readout(A, "A. inhom-Poisson (NO mem)")

    B = hawkes(base * 0.5, amp, branch=0.5, decay_s=3600.0, rng=rng)
    readout(B, "B. Hawkes branch=0.5 (mem)")

    C = hawkes(base * 0.3, amp, branch=0.8, decay_s=3600.0, rng=rng)
    readout(C, "C. Hawkes branch=0.8 (strong)")

    D = duplicate_contaminate(A, frac=0.4, jitter_s=3.0, rng=rng)
    readout(D, "D. A + FRM duplicates")

    print("\nPASS if: A unfolded CV ~1.0 (floor, no false-positive memory);")
    print("         B,C unfolded CV >1 (memory survives, no false-negative);")
    print("         D unfolded CV >1 despite NO real memory => duplicates fake surviving-memory,")
    print("         which the unfold cannot remove (coincident events share local rate) => dedup")
    print("         MUST precede unfold. This is exactly the GOES FRM-contamination lesson.")


if __name__ == "__main__":
    main()
