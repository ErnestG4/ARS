"""Checker for the detune-impossibility cell (2026-09-02). Nonzero exit on failure.

Pins what a reader would ACT on, and each pin names the input that flips it red:

  1. CONTROL-FIRED   -- the freeze detector still finds the freeze in the
                        lattice built to contain one. Red if the detector goes
                        blind, which would make pin 2's zero meaningless.
  2. EXACT-IMPOSSIBLE -- no ratio admits a delta != 0 returning the bystander
                        spectrum to itself while splitting the witnesses, over
                        the complete candidate set. RED IS A FINDING here, not
                        a regression: a counterexample retires the theorem and
                        unblocks `heard-as-listening` with a ratio detune.
  3. CANDIDATES-REAL -- the candidate set is large. Red if it collapses, because
                        "zero freezes found" over zero candidates is vacuous and
                        is exactly how pin 2 would go inert.
  4. LOCAL-COSTS     -- every ratio's local isolation ratio is < 1: separating
                        the witness pair always costs MORE bystander movement
                        than it buys. Red if any ratio turns favourable, which
                        would make a ratio-detune stimulus viable after all.
  5. LINEARITY       -- usable split per unit tolerance is stable across the
                        50x tau sweep. Red if the local regime stops being
                        linear, because then one cost factor is not a valid
                        summary of it and pin 4 is reporting the wrong shape.
  6. CORNERS-COUNTED -- lattice corners (a = 0 exactly) are still counted, and
                        the direction check is still measured OFF them at small
                        deviation. Red if the instrument goes back to scoring a
                        derivative that does not exist.
  7. NO-VACUOUS-ZERO -- no ratio reports margin exactly 0.0 while having moving
                        bystanders. THIS IS THE RETRACTION'S TEST: the first run
                        scored 3/4 and 4/3 at margin 0.0 -- not a measurement but
                        log(x/0) falling through to an initialiser -- and counted
                        both as PASSES of the headline arm. Red if that returns.

NOT INERT: pin 2 asserts a count is ZERO while pin 3 asserts a related count is
LARGE, so a degenerate run that computed nothing fails pin 3 rather than
sailing through pin 2. Pin 4 asserts every ratio is BELOW 1 while pin 1 requires
the machinery to be able to report a positive, so an all-zero instrument fails
pin 1. Pins 6 and 7 both fire on the specific defects the first run contained,
and both were observed red before they were observed green.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "brocot_detune_impossibility.json")

if not os.path.exists(SRC):
    print(f"SKIP — {os.path.basename(SRC)} absent; run "
          "brocot_detune_impossibility.py")
    sys.exit(0)

d = json.load(open(SRC))
rows = d["rows"]
fail = []

ctl = d["positive_control"]
if not ctl.get("fired"):
    fail.append(f"pin1 CONTROL: the freeze detector did not find the "
                f"constructed freeze {ctl.get('expected')} — every 'no freeze "
                "exists' below is then unsupported")

iso = sum(r["n_isolating"] for r in rows)
if iso != 0:
    who = [r["ratio"] for r in rows if r["n_isolating"]]
    fail.append(f"pin2 EXACT-IMPOSSIBLE: {iso} isolating detune(s) now exist at "
                f"{who}. This is a FINDING, not a bug — a ratio detune can split "
                "the witness pair after all, and heard-as-listening unblocks "
                "without the resynthesis apparatus. Re-adjudicate before editing "
                "this checker.")

cands = sum(r["n_freeze_candidates"] for r in rows)
if cands < 2000:
    fail.append(f"pin3 CANDIDATES-REAL: only {cands} candidate deltas across "
                f"{len(rows)} ratios (was 2306). Pin 2's zero is vacuous below "
                "a real candidate set")

bad = [(r["ratio"], r["local_isolation_ratio"]) for r in rows
       if r["local_isolation_ratio"] >= 1.0]
if bad:
    fail.append(f"pin4 LOCAL-COSTS: {bad} now separate the witnesses faster "
                "than they disturb the bystanders. A ratio-detune stimulus "
                "becomes viable at those ratios and the arc's blocking premise "
                "is gone")

sw = d["usable_split"]
if sw.get("unstable"):
    fail.append(f"pin5 LINEARITY: usable split per unit tolerance swings "
                f"{sw['swing']:.3f} across the tau sweep, so the local regime is "
                "not linear and a single cost factor no longer summarises it")

if d.get("n_lattice_corners", 0) < 1:
    fail.append("pin6 CORNERS-COUNTED: no lattice corners recorded. This "
                "lattice has them (2,-4 at 3/4; 3,-3 at 4/3); a zero means they "
                "are being dropped silently again rather than counted")
if d.get("direction_max_rel_dev", 1.0) > 1e-6:
    fail.append(f"pin6b: off-corner direction deviation "
                f"{d['direction_max_rel_dev']:.3e} > 1e-6 — the shift is no "
                "longer the lattice-fixed direction, so the mechanism claim "
                "fails on its own terms")

vac = [r["ratio"] for r in rows
       if r["margin"] == 0.0 and r["n_moving"] > 0]
if vac:
    fail.append(f"pin7 NO-VACUOUS-ZERO: {vac} report margin exactly 0.0 while "
                "having moving bystanders — the log(x/0) fall-through is back, "
                "and those ratios are being counted as passes of the headline "
                "arm on a division by zero")

if fail:
    print("FAIL — detune impossibility")
    for f in fail:
        print("  *", f)
    sys.exit(1)

lr = [r["local_isolation_ratio"] for r in rows]
loc = d["local_isolation"]
print(f"PASS — detune impossibility, {len(rows)} ratios at I={d['I']}, "
      f"horizon A={d['A']}")
print(f"       EXACT: 0 isolating detunes over {cands} candidates at unbounded "
      "magnitude, folds and permutations included — the theorem holds")
print(f"       LOCAL: isolation ratio {min(lr):.3f}..{max(lr):.3f}, so splitting "
      f"the pair by 1 cent costs {loc['cost_min']:.1f}x-{loc['cost_max']:.1f}x "
      "that in bystander movement")
print(f"       the margin>1 that E3 found lives at "
      f"{loc['margin_at_cents_min']:.0f}-{loc['margin_at_cents_max']:.0f} cents "
      "— a different ratio, not a detune")
print(f"       control fired, {d['n_lattice_corners']} corners counted, "
      f"direction dev {d['direction_max_rel_dev']:.1e}, "
      f"linearity swing {sw['swing']:.4f}")
