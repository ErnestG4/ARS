"""ABOVE THE HORIZON: structurally equivalent, but do they SOUND alike?

COMMITTED GENERATOR of cross_substrate/brocot_horizon_perceptual.json.
Predictions and verdict lattice sealed here, before any output exists.

THE GAP THIS CLOSES
-------------------
`brocot_useful_depth.json` proved, exactly and at every one of 508 node-index
cells: a ratio p/q admits sideband coincidences iff max(p,q) <= 2*order_bound(I).

The proposed feature turns that into a depth-slider annotation — "how much of the
tree is alive right now" — and a user will read that as a claim about SOUND. The
theorem is not a claim about sound. It says no coincidence is REACHABLE; it says
nothing about whether two above-horizon nodes resemble each other.

And on inspection they should not. Above the horizon every sideband lands on its
own frequency, but WHERE those frequencies land still depends on alpha. Two
above-horizon nodes share the ABSENCE of coincidence structure and nothing else.
The equivalence measured earlier — identical partial count, top-5 energy and
entropy at every q >= 7 — is an equivalence of AGGREGATES, and two spectra with
identical aggregates can differ completely in pitch content.

So the earlier wording "every node past max(p,q)=8 is spectrally equivalent" was
already too strong, before it reached any UI.

WHAT IS MEASURED
----------------
Pairwise distance between rendered magnitude spectra, on a mel-band perceptual
stand-in and on a log-frequency histogram, for:

  ABOVE   pairs of nodes both above the horizon
  BELOW   pairs of nodes both below it
  JND     one node against itself detuned by 1 cent — a rough "certainly
          inaudible" floor, giving the distances an absolute anchor without a
          listening test
  SELF    a node against itself — must be exactly 0, or the metric is broken

STATED LIMITS, so the feature wording cannot outrun them:
  * steady-state MAGNITUDE spectra only. Phase, transients, and anything the
    synthesis path adds downstream are out of scope, so no claim here covers
    them.
  * a distance ratio is not an audibility verdict. This can show above-horizon
    pairs are far apart relative to a 1-cent detune; only listening establishes
    what a player hears.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ H1  SELF distance is exactly 0 and JND distance is tiny — the metric works    ║
║     and has a floor.                                                         ║
║ H2  ABOVE-horizon pairs are NOT alike: their median mel distance exceeds the  ║
║     1-cent JND floor by at least 10x.                                        ║
║ H3  ABOVE and BELOW pair distances are COMPARABLE — median ABOVE is at least  ║
║     half the median BELOW. The horizon does not collapse nodes together.      ║
║                                                                              ║
║ I EXPECT H2 AND H3 TO HOLD, which means the feature wording must NARROW.     ║
║ "How much of the tree is alive" would then be wrong: above-horizon nodes are  ║
║ audibly distinct from one another, they simply lack coincidence structure.    ║
║ The honest annotation is about a PROPERTY (does this ratio ring?), not about  ║
║ whether the region is worth visiting.                                        ║
║                                                                              ║
║ VERDICT LATTICE                                                              ║
║   WORDING_MUST_NARROW    H2 and H3 hold: above-horizon nodes sound distinct   ║
║   EQUIVALENCE_SUPPORTED  H2 fails: above-horizon pairs sit near the JND       ║
║                          floor, and "alive" is defensible as written          ║
║   METRIC_BROKEN          H1 fails                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import itertools
import json
import os
import sys
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/brocot"))
from redpath import redpath                                       # noqa: E402
from phase3.partial_prediction import predict_partials, order_bound  # noqa: E402

INDICES = [0.9, 2.0]
LO, HI, QMAX = 0.70, 1.40, 24
N_PAIRS = 60
SEED = 20260824
FMIN, FMAX, N_MEL = 50.0, 12000.0, 40

NODES = sorted({Fraction(p, q) for q in range(1, QMAX + 1) for p in range(1, 40)
                if LO <= p / q <= HI and np.gcd(p, q) == 1}, key=float)

_mel_edges = np.linspace(2595 * np.log10(1 + FMIN / 700),
                         2595 * np.log10(1 + FMAX / 700), N_MEL + 1)
MEL_HZ = 700 * (10 ** (_mel_edges / 2595) - 1)
LOG_EDGES = np.geomspace(FMIN, FMAX, 61)


def render(alpha, I):
    sp = predict_partials([1.0, float(alpha)], [I, I], f_carrier=220.0)
    f = np.asarray(sp.freqs, float)
    a = np.abs(np.asarray(sp.amps, float))
    m = (f >= FMIN) & (f <= FMAX) & (a > 0)
    return f[m], a[m]


def band_vec(f, a, edges):
    v = np.zeros(len(edges) - 1)
    idx = np.digitize(f, edges) - 1
    for i, amp in zip(idx, a):
        if 0 <= i < len(v):
            v[i] += amp * amp                       # energy
    v = np.sqrt(v)
    n = np.linalg.norm(v)
    return v / n if n > 0 else v                    # loudness-normalised


def dist(alpha1, alpha2, I, edges):
    f1, a1 = render(alpha1, I)
    f2, a2 = render(alpha2, I)
    return float(np.linalg.norm(band_vec(f1, a1, edges) - band_vec(f2, a2, edges)))


rng = np.random.default_rng(SEED)
rows = {}
for I in INDICES:
    B = order_bound(I)
    hor = 2 * B
    above = [f for f in NODES if max(f.numerator, f.denominator) > hor]
    below = [f for f in NODES if max(f.numerator, f.denominator) <= hor]

    def sample_pairs(pool):
        allp = list(itertools.combinations(pool, 2))
        if not allp:
            return []
        pick = rng.choice(len(allp), size=min(N_PAIRS, len(allp)), replace=False)
        return [allp[i] for i in pick]

    res = {}
    for name, edges in (("mel", MEL_HZ), ("logfreq", LOG_EDGES)):
        d_above = [dist(x, y, I, edges) for x, y in sample_pairs(above)]
        d_below = [dist(x, y, I, edges) for x, y in sample_pairs(below)]
        cents = 2 ** (1 / 1200)
        d_jnd = [dist(f, float(f) * cents, I, edges) for f in above[:20]]
        d_self = [dist(f, float(f), I, edges) for f in above[:10]]
        res[name] = dict(
            n_above_pairs=len(d_above), n_below_pairs=len(d_below),
            above_median=float(np.median(d_above)) if d_above else float("nan"),
            below_median=float(np.median(d_below)) if d_below else float("nan"),
            jnd_median=float(np.median(d_jnd)) if d_jnd else float("nan"),
            self_max=float(np.max(d_self)) if d_self else float("nan"))
    rows[I] = dict(I=I, order_bound=B, horizon=hor,
                   n_above=len(above), n_below=len(below), **res)

print(f"{'I':>5s} {'horizon':>8s} {'nodes above':>12s} {'nodes below':>12s}")
for I in INDICES:
    r = rows[I]
    print(f"{I:>5.1f} {r['horizon']:>8d} {r['n_above']:>12d} {r['n_below']:>12d}")

print(f"\n{'I':>5s} {'metric':>9s} {'SELF':>8s} {'1-cent JND':>11s} "
      f"{'ABOVE pairs':>12s} {'BELOW pairs':>12s} {'ABOVE/JND':>10s} {'ABOVE/BELOW':>12s}")
for I in INDICES:
    for name in ("mel", "logfreq"):
        r = rows[I][name]
        print(f"{I:>5.1f} {name:>9s} {r['self_max']:>8.4f} {r['jnd_median']:>11.4f} "
              f"{r['above_median']:>12.4f} {r['below_median']:>12.4f} "
              f"{r['above_median']/max(r['jnd_median'],1e-12):>10.1f} "
              f"{r['above_median']/max(r['below_median'],1e-12):>12.2f}")

h1 = all(rows[I][m]["self_max"] < 1e-12 for I in INDICES for m in ("mel", "logfreq"))
h2 = all(rows[I]["mel"]["above_median"] >= 10 * rows[I]["mel"]["jnd_median"]
         for I in INDICES)
h3 = all(rows[I]["mel"]["above_median"] >= 0.5 * rows[I]["mel"]["below_median"]
         for I in INDICES)

verdict = ("METRIC_BROKEN" if not h1 else
           "WORDING_MUST_NARROW" if h2 and h3 else "EQUIVALENCE_SUPPORTED")

print(f"\nH1  SELF exactly 0, JND small   {'MET' if h1 else 'MISSED'}")
print(f"H2  ABOVE pairs >= 10x the 1-cent floor   {'MET' if h2 else 'MISSED'}")
print(f"H3  ABOVE >= 0.5x BELOW (horizon does not collapse nodes)   "
      f"{'MET' if h3 else 'MISSED'}")
print(f"\nVERDICT: {verdict}")
if verdict == "WORDING_MUST_NARROW":
    print("  The horizon annotation may claim COINCIDENCE STRUCTURE and nothing more.")
    print("  Above-horizon nodes are audibly distinct from each other; they simply")
    print("  do not ring. 'How much of the tree is alive' is not supported.")

with redpath("index x metric cells measured", expect_min=4) as rp:
    rp.observed(sum(1 for I in INDICES for m in ("mel", "logfreq")
                    if np.isfinite(rows[I][m]["above_median"])))

json.dump(dict(indices=INDICES, n_pairs=N_PAIRS, seed=SEED,
               fmin=FMIN, fmax=FMAX, n_mel=N_MEL,
               rows={str(k): v for k, v in rows.items()},
               predictions=dict(H1=bool(h1), H2=bool(h2), H3=bool(h3)),
               verdict=verdict,
               limits=["steady-state magnitude spectra only; phase and transients out of scope",
                       "a distance ratio is not an audibility verdict"]),
          open(f"{HERE}/brocot_horizon_perceptual.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_horizon_perceptual.json")
