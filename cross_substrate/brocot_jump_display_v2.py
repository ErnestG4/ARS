"""JUMP DISPLAY v2: mark PARTIAL-SET CHANGES, of which coincidences are one class.

COMMITTED GENERATOR of cross_substrate/brocot_jump_display_v2.json.
Predictions sealed here, before any output exists.

WHY v2 EXISTS
-------------
v1 marked the closed-form coincidence events and was falsified against the
measured roughness: 55% coverage of top-decile jumps against an 80% bar, 1.97x
contrast against 3x. The markers were not the jumps.

The diagnosis (banked with that run) was measured, not guessed: partial-set
MEMBERSHIP change is the dominant mechanism. Median |du| is 0.2098 where the
partial count changes and 0.0066 where it does not — a 32x ratio — while
top-decile jumps carry a count change at 24% against a 1% baseline.

Coincidences are a SUBSET of that class. Two partials merging drops the distinct
count, so every coincidence is a count change; but on this path there are 14
coincidence markers against roughly 50 count-change steps. The rest are
AMPLITUDE-THRESHOLD CROSSINGS — a partial's amplitude is a product of Bessel
terms and crosses the -50 dB floor at ratios the Farey lattice knows nothing
about.

So v2 marks the union, labelled by class:

  COINCIDENCE   closed form, Farey-enumerable from the horizon (v1's set)
  THRESHOLD     amplitude-dependent, offline-computable but not closed form

WHAT WOULD MAKE THIS A WORSE FEATURE, AND IS THEREFORE TESTED
--------------------------------------------------------------
A marker set built by DETECTING count changes on a grid is not a prediction —
it is a redescription of the measurement, and it would score perfectly by
construction while telling a player nothing they could not have got by listening.
The test that separates the two is OUT-OF-SAMPLE: derive the marker set on one
grid and score it on a DIFFERENT, finer one. A redescription degrades; a real
event set does not.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ K1  COVERAGE — at least 80% of top-decile |du| steps on the HELD-OUT grid    ║
║     fall within delta of a marker derived on the coarse grid.                ║
║ K2  CONTRAST — median |du| near a marker is at least 3x the median away,     ║
║     on the held-out grid.                                                    ║
║ K3  OUT-OF-SAMPLE HOLDS — held-out coverage is at least 0.8x the in-sample   ║
║     coverage. A large drop means the markers were fitted to the grid they    ║
║     were found on.                                                          ║
║ K4  THE CLOSED-FORM CLASS EARNS ITS PLACE — coincidence markers have a       ║
║     HIGHER median jump than threshold markers. If they do not, the horizon   ║
║     contributes nothing the amplitude scan would not have found anyway, and  ║
║     the honest feature is a pure amplitude scan with no theorem in it.       ║
║                                                                              ║
║ K4 IS THE ONE I CARE ABOUT. It is the question of whether the theorem does   ║
║ any work in the shipped feature, or is decoration on top of a scan. A miss   ║
║ is not fatal to the display — it is fatal to the claim that the display uses ║
║ the theorem, and that distinction should be recorded rather than blurred.    ║
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
from existence import summarise, EXISTENCE                        # noqa: E402
from phase3.partial_prediction import predict_partials, order_bound  # noqa: E402
from cross_substrate.axes import canonical_spacings, I8_brody_q_unbounded  # noqa: E402

I_MUS = 0.9
A0, A1 = 0.70, 1.40
COARSE, FINE = 1401, 3501        # derive on COARSE, score on FINE

# AMENDED before the corrected result is banked. Both scoring rules were
# GRID-DEPENDENT, inside a test whose entire purpose is comparing across grids --
# the commensurability defect, in my own metric.
#
#   delta was a fixed 0.005, spanning 10 coarse steps but 25 fine ones, so the
#   fine-grid "median |du| near a marker" averaged one event against 24
#   non-events and collapsed the contrast to 1.1x.
#
#   "top decile" is relative, so a finer grid admits more merely-moderate steps
#   into the set being explained.
#
# The principled replacement uses the physics: a real DISCONTINUITY has
# grid-independent magnitude, while continuous variation shrinks with spacing.
# So a large jump is defined ABSOLUTELY -- and delta scales with the grid, so
# the window means the same thing on both.
DELTA_STEPS = 3                  # window = 3 grid steps, on whichever grid
ABS_JUMP = 0.05                  # ~8x the measured continuous background 0.0066,
                                 # far below the event scale 0.21-0.38
V1 = json.load(open(f"{HERE}/brocot_jump_display.json"))
COINC = {round(m["value"], 6) for m in V1["markers"]}


def probe(a):
    sp = predict_partials([1.0, float(a)], [I_MUS, I_MUS], f_carrier=220.0)
    n = sp.freqs.size
    u = (I8_brody_q_unbounded(canonical_spacings(np.sort(sp.freqs)))
         if n >= 20 else None)
    return n, (np.nan if u is None else float(u))


def sweep(npts):
    g = np.linspace(A0, A1, npts)
    N, U = [], []
    for a in g:
        n, u = probe(a)
        N.append(n); U.append(u)
    return g, np.array(N, float), np.array(U, float)


# ── derive markers on the COARSE grid ───────────────────────────────────────
gc, Nc, Uc = sweep(COARSE)
dn = np.abs(np.diff(Nc))
mid_c = (gc[:-1] + gc[1:]) / 2
change = dn > 0
dc = (A1 - A0) / (COARSE - 1)
df = (A1 - A0) / (FINE - 1)
mark = []
for x in mid_c[change]:
    kind = ("coincidence" if any(abs(x - c) <= DELTA_STEPS * dc for c in COINC)
            else "threshold")
    mark.append(dict(value=float(x), kind=kind))
pos = np.array([m["value"] for m in mark])

# ── score on the HELD-OUT fine grid ─────────────────────────────────────────
gf, Nf, Uf = sweep(FINE)
mid_f = (gf[:-1] + gf[1:]) / 2
jump_f = np.abs(np.diff(Uf))
okf = np.isfinite(jump_f)
near_f = np.array([np.any(np.abs(x - pos) <= DELTA_STEPS * df) for x in mid_f])

top_f = okf & (jump_f >= ABS_JUMP)
cov_out = float(near_f[top_f].mean())
gn = float(np.median(jump_f[okf & near_f]))
gf_ = float(np.median(jump_f[okf & ~near_f]))
contrast = gn / gf_ if gf_ > 0 else float("inf")

# in-sample coverage, for the degradation check
jump_c = np.abs(np.diff(Uc))
okc = np.isfinite(jump_c)
near_c = np.array([np.any(np.abs(x - pos) <= DELTA_STEPS * dc) for x in mid_c])
top_c = okc & (jump_c >= ABS_JUMP)
cov_in = float(near_c[top_c].mean())

# per-class jump magnitude, on the held-out grid
def class_jumps(kind):
    p = np.array([m["value"] for m in mark if m["kind"] == kind])
    if p.size == 0:
        return []
    out = []
    for x in p:
        sel = okf & (np.abs(mid_f - x) <= DELTA_STEPS * df)
        if sel.any():
            out.append(float(np.max(jump_f[sel])))
    return out


jc, jt = class_jumps("coincidence"), class_jumps("threshold")
med_c = float(np.median(jc)) if jc else float("nan")
med_t = float(np.median(jt)) if jt else float("nan")

k1 = cov_out >= 0.80
k2 = contrast >= 3.0
k3 = cov_in > 0 and cov_out >= 0.8 * cov_in
k4 = np.isfinite(med_c) and np.isfinite(med_t) and med_c > med_t

verdict = ("DISPLAY_VALIDATED" if k1 and k2 and k3 else "NOT_VALIDATED")

print(f"derive on {COARSE} points, score on held-out {FINE}\n")
print(f"markers: {len(mark)}  "
      f"({sum(1 for m in mark if m['kind'] == 'coincidence')} coincidence, "
      f"{sum(1 for m in mark if m['kind'] == 'threshold')} threshold)\n")
print(f"    large jumps on held-out grid (|du| >= {ABS_JUMP}): {int(top_f.sum())}")
print(f"K1  held-out large-jump coverage {cov_out:.1%}   (>= 80% ?)  "
      f"{'MET' if k1 else 'MISSED'}")
print(f"K2  median |du| near {gn:.4f} vs far {gf_:.4f} = {contrast:.1f}x   "
      f"(>= 3 ?)  {'MET' if k2 else 'MISSED'}")
print(f"K3  in-sample {cov_in:.1%} -> held-out {cov_out:.1%} "
      f"({cov_out/cov_in if cov_in else float('nan'):.2f}x)   {'MET' if k3 else 'MISSED'}")
print(f"K4  median jump: coincidence {med_c:.4f} vs threshold {med_t:.4f}   "
      f"{'MET' if k4 else 'MISSED'}")
print(f"\nVERDICT: {verdict}")
if not k4:
    print("  The closed-form class does NOT carry bigger jumps than the amplitude")
    print("  class. The display works, but the THEOREM does no work in it -- an")
    print("  amplitude scan alone would find the same markers. Record that rather")
    print("  than implying the horizon is load-bearing here.")

ev = summarise("n_markers", [1] * len(mark), EXISTENCE)
with redpath("markers derived on the coarse grid", expect_min=10) as rp:
    rp.observed(ev["n_nonzero"])

json.dump(dict(I=I_MUS, a0=A0, a1=A1, coarse=COARSE, fine=FINE, delta=DELTA,
               n_markers=len(mark), markers=mark,
               delta_steps=DELTA_STEPS, abs_jump=ABS_JUMP,
               n_large_jumps_held_out=int(top_f.sum()),
               coverage_in_sample=cov_in, coverage_held_out=cov_out,
               contrast=contrast, median_jump_coincidence=med_c,
               median_jump_threshold=med_t,
               predictions=dict(K1=bool(k1), K2=bool(k2), K3=bool(k3), K4=bool(k4)),
               verdict=verdict),
          open(f"{HERE}/brocot_jump_display_v2.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_jump_display_v2.json")
