"""Certify the Spacings provenance guard — and prove it refuses the real cases.

A guard that has never been shown to refuse is not a guard. The two refusals
below are not hypothetical: each reproduces, in miniature, a collision that cost
this repo a measurement.

  1. ANALYTIC vs EMPIRICAL reference. recert_finite_seed (2026-09-13) measured
     an additive 2.6e-03 contribution to 1-<r~> from swapping one for the other
     -- larger than every science reading past k=16.
  2. RAW vs RICHARDSON arm. A Gate D construction placed by inverting the raw
     CDF and read back through the Richardson pair read +8.92% against a known
     answer, identically at two grid densities, so it was not interpolation.

It also checks the boundaries that make the guard usable rather than merely
strict: identical provenance must combine freely, float() must always work (the
tag is not a rail), and scalars must combine without a tag.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "derivflow"))

from spacings import (Unfolding, Spacings, Tagged, ProvenanceMismatch)  # noqa: E402
from track0_harness import rtilde as _instrument_rtilde                 # noqa: E402

bad = []
rng = np.random.default_rng(20260914)
pos = np.concatenate(([0.0], np.cumsum(1.0 + 1e-3 * rng.standard_normal(4031))))

ANALYTIC = Unfolding("analytic-semicircle", "richardson", 0.704, "bulk-0.20")
EMPIRICAL = Unfolding("empirical-n4096", "richardson", 0.704, "bulk-0.20")
RAW = Unfolding("analytic-semicircle", "raw-eps", 0.704, "bulk-0.20")
WIDE = Unfolding("analytic-semicircle", "richardson", 2.0, "bulk-0.20")
EDGE = Unfolding("analytic-semicircle", "richardson", 0.704, "section-0.95-0.05")

sa = Spacings.from_positions(pos, ANALYTIC, "gate-D")
se = Spacings.from_positions(pos, EMPIRICAL, "science")
sr = Spacings.from_positions(pos, RAW, "gate-D")
sw = Spacings.from_positions(pos, WIDE, "gate-D")
sx = Spacings.from_positions(pos, EDGE, "gate-D")

# ---- 1. the statistic agrees with the instrument --------------------------
t = sa.rtilde_distance()
inst = 1.0 - _instrument_rtilde(np.diff(pos))
print(f"  statistic vs track0_harness.rtilde: {float(t):.17g} vs {inst:.17g}")
if float(t) != inst:
    bad.append(f"Spacings.rtilde_distance disagrees with the instrument by "
               f"{abs(float(t) - inst):.2e}")

# ---- 2. the four refusals that each cost a measurement --------------------
CASES = [
    ("analytic vs empirical reference", sa, se, "reference"),
    ("raw vs Richardson arm", sa, sr, "arm"),
    ("bandwidth 0.704 vs 2.0", sa, sw, "eps_over_delta"),
    ("bulk window vs edge section", sa, sx, "window"),
]
print("\n  REFUSALS (each reproduces a collision that cost a measurement):")
for label, A, B, field in CASES:
    fired, msg = False, ""
    try:
        A.rtilde_distance() - B.rtilde_distance()
    except ProvenanceMismatch as e:
        fired, msg = True, str(e)
    print(f"    {label:<34} {'REFUSED' if fired else 'ALLOWED  <-- BAD'}")
    if not fired:
        bad.append(f"combining across {field} was ALLOWED — the guard does not "
                   "cover the field it exists for")
    elif field not in msg:
        bad.append(f"refusal for {label} does not name the differing field "
                   f"{field!r}; the message must say what differs")

# ---- 3. it must NOT over-refuse -------------------------------------------
print("\n  PERMITTED (identical provenance, and scalars):")
ok = True
try:
    d = sa.rtilde_distance() - Spacings.from_positions(
        pos, ANALYTIC, "gate-D").rtilde_distance()
    print(f"    same provenance subtract              -> {float(d):.3e}")
except ProvenanceMismatch as e:
    ok = False
    bad.append(f"identical provenance was REFUSED: {e}")
try:
    scaled = sa.rtilde_distance() * 2.0
    print(f"    scalar multiply                       -> {float(scaled):.6f}")
except Exception as e:
    ok = False
    bad.append(f"scalar arithmetic was refused: {e}")
try:
    print(f"    float() on a tagged value             -> {float(t):.6f}")
except Exception as e:
    ok = False
    bad.append(f"float() on a Tagged raised: {e} — the tag is not a rail and "
               "must not block reading the value")
try:
    r = sa.rtilde_distance().ratio_to(sa.rtilde_distance())
    print(f"    ratio_to with matching provenance     -> {r:.6f}")
except ProvenanceMismatch as e:
    ok = False
    bad.append(f"ratio_to refused matching provenance: {e}")

# ---- 4. construction refuses a non-monotone unfolding ---------------------
nm = pos.copy()
nm[2000] = nm[2001] + 0.5
fired = False
try:
    Spacings.from_positions(nm, ANALYTIC, "gate-D")
except ValueError:
    fired = True
allowed = Spacings.from_positions(nm, ANALYTIC, "gate-D", allow_nonpositive=True)
print(f"\n  non-monotone construction: {'REFUSED' if fired else 'ALLOWED <-- BAD'}; "
      f"with allow_nonpositive it yields {len(allowed)} gaps")
if not fired:
    bad.append("Spacings.from_positions accepted a non-monotone unfolding "
               "silently — the same defect as the filter removed from "
               "knownanswer.py on 2026-09-14")

# ---- 5. Unfolding has no defaults ----------------------------------------
try:
    Unfolding()                                   # type: ignore[call-arg]
    bad.append("Unfolding() constructed with no arguments — a default lets a "
               "caller omit the field that distinguishes their case")
except TypeError:
    print("  Unfolding requires every field (no defaults to omit)")

if bad:
    print("\nVERIFY_SPACINGS: FAIL")
    for b in bad:
        print("  *", b)
    sys.exit(1)
print("\nVERIFY_SPACINGS: PASS — the statistic matches the instrument, all four "
      "estimator differences are refused by name, matching provenance and "
      "scalars combine freely, and a non-monotone unfolding cannot be built "
      "by accident")
