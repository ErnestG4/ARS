"""JUMP DISPLAY: where the coincidence events sit on a morph path, in closed form.

COMMITTED GENERATOR of cross_substrate/brocot_jump_display.json.
Predictions and verdict lattice sealed here, before any output exists.

WHY A DISPLAY AND NOT A SMOOTHER
---------------------------------
Three attempts to linearise a ratio morph failed (`brocot_linear_morph.json`,
`brocot_waypoint_scorer.json`, `brocot_horizon_resolution.json`): 1.6x, 1.31x,
1.74x against a 3x bar, with the last ruling out granularity by demonstrably
admitting more nodes and changing nothing. The punctuation is scale-free within
the instrument's range, so a smooth wormhole is not available by any waypoint
policy.

The honest feature is therefore to MARK the jumps rather than pretend to
interpolate through them — and the horizon gives their positions in closed form
before a note is played.

WHAT THE MARKERS ARE
--------------------
For a path [a0, a1] at modulation index I, with B = order_bound(I):

  DIRECT events   p/q in range, gcd(p,q)=1, max(p,q) <= 2B
                  (the theorem's horizon; these are where sidebands fuse)
  REFLECTED events  p/q with q <= 2B and p <= 2B+2 that carry an m != 0
                  reflected coincidence — the same horizon shifted by +2 in p

Both sets are finite Farey enumerations bounded by 2B. No search, no sampling,
nothing on the audio thread.

WEIGHT. Each event carries a weight = the number of coinciding index pairs at
that ratio, also closed-form. A display can size markers by it.

THE VALIDATION IS THE POINT
---------------------------
A display that marks positions with no measurable correlate is decoration. So
this run checks the markers against the measured roughness of u(alpha):

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ J1  COVERAGE — every large measured jump lands near a predicted event:        ║
║     at least 80% of the top-decile |du| steps fall within delta of one.       ║
║ J2  CONTRAST — median gradient near an event is at least 3x the median        ║
║     gradient away from every event.                                          ║
║ J3  WEIGHT IS INFORMATIVE — the closed-form coincidence count correlates      ║
║     positively with measured local jump magnitude (Spearman > 0, CI clear     ║
║     of zero).                                                                ║
║                                                                              ║
║ J3 IS THE ONE THAT CAN FAIL HONESTLY, and it is the one that decides whether  ║
║ markers may be SIZED. Coincidence count is a lattice quantity; the audible    ║
║ jump depends on the AMPLITUDES landing on the coinciding bins, which the      ║
║ count ignores entirely. If J3 misses, the display shows positions only and    ║
║ every marker is the same size — a weaker feature, honestly scoped, and the    ║
║ follow-up would be to weight by summed Bessel amplitude instead of by count.  ║
║                                                                              ║
║ VERDICT LATTICE                                                              ║
║   MARKERS_VALIDATED     J1 and J2 hold; J3 decides sizing                     ║
║   POSITIONS_ONLY        J1 and J2 hold, J3 misses — show unsized markers      ║
║   NOT_VALIDATED         J1 or J2 misses: the events are not the jumps         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import json
import os
import sys
from fractions import Fraction

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/brocot"))
from redpath import redpath                                       # noqa: E402
from existence import summarise, EXISTENCE                        # noqa: E402
from phase3.partial_prediction import predict_partials, order_bound  # noqa: E402
from cross_substrate.axes import canonical_spacings, I8_brody_q_unbounded  # noqa: E402

I_MUS = 0.9
A0, A1 = 0.70, 1.40
GRID = 1401
DELTA = 0.005            # "near an event", a few grid steps
SEED, BOOT = 20260824, 2000


# ── the closed-form marker set ──────────────────────────────────────────────
def coincidence_profile(fr, B):
    """(direct pairs, reflected m!=0 pairs) at this ratio. Exact arithmetic."""
    vals = {}
    for n1 in range(-B, B + 1):
        for n2 in range(-B, B + 1):
            vals[(n1, n2)] = Fraction(1) + Fraction(n1) + Fraction(n2) * fr
    seen, direct = set(), 0
    for v in vals.values():
        if v in seen:
            direct += 1
        else:
            seen.add(v)
    keys, refl = list(vals), 0
    for i, k1 in enumerate(keys):
        v1 = vals[k1]
        if v1 <= 0:
            continue
        for k2 in keys[i + 1:]:
            if vals[k2] != -v1:
                continue
            if not (2 + k1[0] + k2[0] == 0 and k1[1] + k2[1] == 0):
                refl += 1
    return direct, refl


def markers(a0, a1, I):
    """Every coincidence event on [a0, a1] at index I. Closed form."""
    B = order_bound(I)
    hor = 2 * B
    out = []
    for q in range(1, hor + 1):
        for p in range(1, hor + 3):
            if np.gcd(p, q) != 1:
                continue
            x = p / q
            if not (a0 <= x <= a1):
                continue
            fr = Fraction(p, q)
            d, r = coincidence_profile(fr, B)
            if d == 0 and r == 0:
                continue
            out.append(dict(ratio=str(fr), value=float(x),
                            maxpq=max(p, q), direct=d, reflected=r,
                            weight=d + r,
                            kind=("direct" if d else "reflected-only")))
    return sorted(out, key=lambda m: m["value"]), B, hor


MARK, B, HOR = markers(A0, A1, I_MUS)


# ── the measured roughness ──────────────────────────────────────────────────
def u_of(a):
    sp = predict_partials([1.0, float(a)], [I_MUS, I_MUS], f_carrier=220.0)
    if sp.freqs.size < 20:
        return np.nan
    v = I8_brody_q_unbounded(canonical_spacings(np.sort(sp.freqs)))
    return np.nan if v is None else float(v)


grid = np.linspace(A0, A1, GRID)
u = np.array([u_of(a) for a in grid])
ok = np.isfinite(u)
step_mid = (grid[:-1] + grid[1:]) / 2
step_mag = np.abs(np.diff(u))
valid = np.isfinite(step_mag)

pos = np.array([m["value"] for m in MARK])
near = np.array([np.any(np.abs(x - pos) <= DELTA) for x in step_mid])

top_dec = valid & (step_mag >= np.nanpercentile(step_mag[valid], 90))
covered = float(near[top_dec].mean())
g_near = float(np.median(step_mag[valid & near]))
g_far = float(np.median(step_mag[valid & ~near]))
contrast = g_near / g_far if g_far > 0 else float("inf")

# J3: does the closed-form weight predict the measured jump size?
wm, jm = [], []
for m in MARK:
    sel = valid & (np.abs(step_mid - m["value"]) <= DELTA)
    if sel.any():
        wm.append(m["weight"]); jm.append(float(np.max(step_mag[sel])))
rho = float(stats.spearmanr(wm, jm)[0]) if len(wm) > 4 else float("nan")
rng = np.random.default_rng(SEED)
bs = []
for _ in range(BOOT):
    i = rng.integers(0, len(wm), len(wm))
    if len(set(i.tolist())) < 4:
        continue
    r = stats.spearmanr(np.array(wm)[i], np.array(jm)[i])[0]
    if np.isfinite(r):
        bs.append(r)
lo, hi = np.percentile(bs, [2.5, 97.5]) if bs else (np.nan, np.nan)

j1 = covered >= 0.80
j2 = contrast >= 3.0
j3 = np.isfinite(rho) and rho > 0 and lo > 0
verdict = ("MARKERS_VALIDATED" if j1 and j2 and j3 else
           "POSITIONS_ONLY" if j1 and j2 else "NOT_VALIDATED")

print(f"path [{A0}, {A1}] at I={I_MUS}   B={B}   horizon max(p,q)<={HOR}")
print(f"markers: {len(MARK)} events "
      f"({sum(1 for m in MARK if m['kind'] == 'direct')} direct, "
      f"{sum(1 for m in MARK if m['kind'] == 'reflected-only')} reflected-only)\n")
print(f"{'ratio':>8s} {'value':>8s} {'max(p,q)':>9s} {'direct':>7s} {'refl':>5s} {'weight':>7s}")
for m in MARK[:12]:
    print(f"{m['ratio']:>8s} {m['value']:>8.4f} {m['maxpq']:>9d} "
          f"{m['direct']:>7d} {m['reflected']:>5d} {m['weight']:>7d}")
if len(MARK) > 12:
    print(f"      ... {len(MARK) - 12} more")

print(f"\nJ1  top-decile jumps within {DELTA} of an event: {covered:.1%}   "
      f"(>= 80% ?)  {'MET' if j1 else 'MISSED'}")
print(f"J2  median |du| near {g_near:.4f} vs far {g_far:.4f} = {contrast:.2f}x   "
      f"(>= 3 ?)  {'MET' if j2 else 'MISSED'}")
print(f"J3  weight vs measured jump: rho={rho:+.3f} CI [{lo:+.3f}, {hi:+.3f}]   "
      f"{'MET' if j3 else 'MISSED'}")
print(f"\nVERDICT: {verdict}")
if verdict == "POSITIONS_ONLY":
    print("  Show markers at the event positions, all the same size. The")
    print("  closed-form coincidence COUNT does not predict jump magnitude --")
    print("  it ignores the Bessel amplitudes landing on the coinciding bins,")
    print("  which is the sealed follow-up: weight by summed amplitude instead.")

# existence, not central tendency: are there events at all, and reflected ones?
ev = summarise("n_events", [m["weight"] for m in MARK], EXISTENCE)
with redpath("coincidence events on the path", expect_min=5) as rp:
    rp.observed(ev["n_nonzero"])

json.dump(dict(I=I_MUS, a0=A0, a1=A1, B=B, horizon=HOR, delta=DELTA,
               n_markers=len(MARK), markers=MARK,
               coverage_top_decile=covered, grad_near=g_near, grad_far=g_far,
               contrast=contrast, weight_vs_jump_rho=rho, weight_ci=[lo, hi],
               predictions=dict(J1=bool(j1), J2=bool(j2), J3=bool(j3)),
               verdict=verdict),
          open(f"{HERE}/brocot_jump_display.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_jump_display.json")
