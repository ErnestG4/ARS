"""DOES THE DISPLAY MARK JUMPS THE PLAYER HEARS? The gate before it ships.

COMMITTED GENERATOR of cross_substrate/brocot_marker_erb_gate.json.
Predictions sealed here, before any output exists.

THE GAP
-------
`brocot_jump_display_v2.json` established that coincidence markers are enormous
where they land: median jump **1.3691** against threshold markers' 0.0081, a
169x separation. That was measured on **u**, the Brody statistic.

The display is PLAYER-FACING. Its claim must be validated in the player-facing
coordinate, and `brocot_axis_or_instrument.json` just measured that the two
coordinates agree jumps happen and disagree about WHERE — Spearman only +0.202,
CI [+0.122, +0.282].

Worse for this feature specifically: only **5.7%** of top-decile ERB jumps sit
at a partial-set change (baseline 1.9%). Coincidences are a subset of set
changes. So the events that dominate u's roughness are nearly absent from ERB's,
and whether they separate perceptually at all is genuinely open.

This is the "alive" defect in a new costume: a UI claim underwritten by the wrong
metric. The wording gate caught it once for the horizon annotation; the same gate
is owed to the marker.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ P1  The ERB metric is live here: median |dERB| away from markers is > 0, and  ║
║     a 1-cent detune is far below it. (Anchor liveness, folded into the        ║
║     metric check after an inert anchor slipped through once.)                 ║
║ P2  Coincidence markers separate in ERB by at least 3x: median |dERB| at a    ║
║     marker is >= 3x the median away from every marker.                       ║
║ P3  The separation is WEAKER in ERB than in u. u gave 169x against threshold  ║
║     markers; ERB will give far less, because Brody reads spacing structure    ║
║     directly while ERB reads a smeared amplitude pattern that a merge barely  ║
║     perturbs.                                                                ║
║                                                                              ║
║ I EXPECT P3 AND AM UNSURE OF P2, which is the point of running it.            ║
║                                                                              ║
║ CONSEQUENCE, COMMITTED IN ADVANCE so the caption cannot be chosen after the   ║
║ numbers:                                                                     ║
║   P2 MET  -> the display may say JUMP. Markers are where the timbre lurches,  ║
║              in the coordinate the player hears.                             ║
║   P2 MISS -> the display may say STRUCTURAL EVENT and NOT jump. "The partial  ║
║              count drops here; these sidebands fuse" is still true, still     ║
║              closed-form, still worth showing — and it is a different         ║
║              caption, not a weaker version of the same one.                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
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
from cross_substrate.axes import canonical_spacings, I8_brody_q_unbounded  # noqa: E402

I_MUS, A0, A1, GRID = 0.9, 0.70, 1.40, 2101
FMIN, FMAX = 50.0, 12000.0
ERB_C = np.geomspace(FMIN, FMAX, 400)
DELTA_STEPS = 3
V1 = json.load(open(f"{HERE}/brocot_jump_display.json"))
MARKERS = [m for m in V1["markers"] if m["kind"] == "direct"]


def erb_vec(a):
    sp = predict_partials([1.0, float(a)], [I_MUS, I_MUS], f_carrier=220.0)
    f = np.asarray(sp.freqs, float)
    am = np.abs(np.asarray(sp.amps, float))
    m = (f >= FMIN) & (f <= FMAX) & (am > 0)
    f, am = f[m], am[m]
    v = np.zeros(len(ERB_C))
    for fr, pa in zip(f, am):
        w = 24.7 * (4.37 * fr / 1000.0 + 1.0)
        v += (pa * pa) * np.exp(-0.5 * ((ERB_C - fr) / w) ** 2)
    v = np.sqrt(v)
    n = np.linalg.norm(v)
    return (v / n if n > 0 else v), int(sp.freqs.size)


def u_of(a):
    sp = predict_partials([1.0, float(a)], [I_MUS, I_MUS], f_carrier=220.0)
    if sp.freqs.size < 20:
        return np.nan
    v = I8_brody_q_unbounded(canonical_spacings(np.sort(sp.freqs)))
    return np.nan if v is None else float(v)


g = np.linspace(A0, A1, GRID)
step = (A1 - A0) / (GRID - 1)
V, N = [], []
for a in g:
    v, n = erb_vec(a)
    V.append(v); N.append(n)
de = np.array([float(np.linalg.norm(V[i + 1] - V[i])) for i in range(len(V) - 1)])
mid = (g[:-1] + g[1:]) / 2

pos = np.array([m["value"] for m in MARKERS])
near = np.array([np.any(np.abs(x - pos) <= DELTA_STEPS * step) for x in mid])

erb_near = float(np.median(de[near])) if near.any() else float("nan")
erb_far = float(np.median(de[~near]))
sep_erb = erb_near / erb_far if erb_far > 0 else float("inf")

# anchor: a 1-cent detune, same coordinate
cents = 2 ** (1 / 1200)
jnd = float(np.median([
    float(np.linalg.norm(erb_vec(float(m["value"]))[0]
                         - erb_vec(float(m["value"]) * cents)[0]))
    for m in MARKERS[:10]]))

# the same separation measured on u, for the P3 comparison
U = np.array([u_of(a) for a in g], float)
du = np.abs(np.diff(U))
oku = np.isfinite(du)
u_near = float(np.median(du[oku & near]))
u_far = float(np.median(du[oku & ~near]))
sep_u = u_near / u_far if u_far > 0 else float("inf")

p1 = erb_far > 0 and jnd > 0 and jnd < erb_far
p2 = sep_erb >= 3.0
p3 = sep_erb < sep_u

verdict = "MAY_SAY_JUMP" if p2 else "MAY_SAY_STRUCTURAL_EVENT_ONLY"

print(f"path [{A0},{A1}] at I={I_MUS}, {GRID} points, "
      f"{len(MARKERS)} direct coincidence markers\n")
print(f"{'coordinate':>12s} {'at marker':>11s} {'away':>11s} {'separation':>11s}")
print(f"{'ERB':>12s} {erb_near:>11.5f} {erb_far:>11.5f} {sep_erb:>10.2f}x")
print(f"{'Brody u':>12s} {u_near:>11.5f} {u_far:>11.5f} {sep_u:>10.2f}x")
print(f"\n  1-cent anchor in ERB: {jnd:.6f}  (must be > 0 and below the away-median)")

print(f"\nP1  ERB metric live, anchor below background   {'MET' if p1 else 'MISSED'}")
print(f"P2  markers separate in ERB by >= 3x ({sep_erb:.2f}x)   {'MET' if p2 else 'MISSED'}")
print(f"P3  separation weaker in ERB than in u ({sep_erb:.2f}x vs {sep_u:.2f}x)   "
      f"{'MET' if p3 else 'MISSED'}")
print(f"\nVERDICT: {verdict}")
if not p2:
    print("  Per the sealed consequence: the display may caption these STRUCTURAL")
    print("  EVENTS and may NOT call them jumps. 'The partial count drops here;")
    print("  these sidebands fuse' is true, closed-form and worth showing -- and")
    print("  it is a different caption, not a weaker version of the same one.")

with redpath("markers with a measurable ERB neighbourhood", expect_min=5) as rp:
    rp.observed(int(sum(1 for m in MARKERS
                        if np.any(np.abs(mid - m["value"]) <= DELTA_STEPS * step))))

json.dump(dict(I=I_MUS, a0=A0, a1=A1, grid=GRID, n_markers=len(MARKERS),
               delta_steps=DELTA_STEPS,
               erb_at_marker=erb_near, erb_away=erb_far, separation_erb=sep_erb,
               u_at_marker=u_near, u_away=u_far, separation_u=sep_u,
               erb_1cent_anchor=jnd,
               predictions=dict(P1=bool(p1), P2=bool(p2), P3=bool(p3)),
               verdict=verdict),
          open(f"{HERE}/brocot_marker_erb_gate.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_marker_erb_gate.json")
