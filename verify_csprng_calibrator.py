"""Checker for the CSPRNG calibrator (2026-09-05). Nonzero exit on failure.

This pins a calibrator whose whole value is ONE-SIDEDNESS, plus a measured
witness for the battery's blind spot. Each pin names what flips it red.

  1. BATTERY-CAN-REJECT -- the periodic control is still rejected as Poisson at
                    every seed. Red if it stops: the three NULL results below
                    are non-evidence from a battery that rejects nothing, and
                    this is the pin that keeps them honest.
  2. CSPRNG-READS-POISSON -- still Poisson at every seed. RED HERE IS A FINDING
                    ABOUT THE INSTRUMENT, not about the stream: exponential
                    gaps from uniform variates IS a homogeneous Poisson process
                    by construction, so a departure is either an instrument bug
                    or a distinguisher against ChaCha20 — and the second would
                    be a much larger result than anything this repo tests.
  3. BLIND-SPOT-STANDS -- RANDU still reads Poisson at every seed. Red if the
                    battery starts catching it: that would mean its reach is
                    WIDER than claimed and the "there is always structure we
                    cannot see" citation must be re-derived, not deleted.
  4. LATTICE-IS-REALLY-THERE -- RANDU's mean distance to its own 15 planes is
                    still ~0 while the CSPRNG's is ~1/60. THIS IS WHAT MAKES
                    PIN 3 MEAN SOMETHING. Without it, "RANDU reads Poisson" is
                    compatible with there being no defect to find; with it, the
                    defect is present, measured, and invisible to the battery.
  5. ARM-DISCRIMINATES -- the lattice arm must still separate RANDU from the
                    CSPRNG. Red if the rival also meets the bar, which would
                    make the arm inert and pin 4 decorative.

NOT INERT: pin 1 requires a REJECTION while pins 2 and 3 require ACCEPTANCES
from the same battery on the same statistic, so no degenerate instrument
satisfies both — one that accepts everything fails pin 1, one that rejects
everything fails pins 2 and 3. Pin 4 requires one value near zero and another
near 1/60, so a probe returning a constant fails it whichever constant it picks.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "csprng_calibrator.json")

if not os.path.exists(SRC):
    print("SKIP — csprng_calibrator.json absent; run run_csprng_calibrator.py")
    sys.exit(0)

d = json.load(open(SRC))
n = len(d["seeds"])
fail = []

if d["periodic_rejected"] != n:
    fail.append(f"pin1 BATTERY-CAN-REJECT: the periodic control is rejected at "
                f"only {d['periodic_rejected']}/{n} seeds. A battery that "
                "cannot reject makes every null below non-evidence")
if d["csprng_poisson"] != n:
    fail.append(f"pin2 CSPRNG: reads Poisson at only {d['csprng_poisson']}/{n} "
                "seeds. Exponential gaps from uniforms IS a Poisson process by "
                "construction, so this is an instrument bug — or a "
                "distinguisher against ChaCha20, which would be the larger "
                "result and should be checked before it is believed")
if d["randu_poisson"] != n:
    fail.append(f"pin3 BLIND-SPOT: RANDU now reads non-Poisson at "
                f"{n - d['randu_poisson']}/{n} seeds. The battery's reach is "
                "wider than this cell claimed; re-derive the incompleteness "
                "citation rather than dropping it")
if d["lattice_randu"] > 1e-6:
    fail.append(f"pin4 LATTICE: RANDU's mean distance to its 15 planes is now "
                f"{d['lattice_randu']:.3g} > 1e-6. If the lattice is not there, "
                "pin 3 is 'nothing to find' rather than 'invisible to this "
                "instrument', and the blind-spot claim collapses")
if not (0.010 < d["lattice_csprng"] < 0.025):
    fail.append(f"pin4b CONTROL: the CSPRNG's lattice distance is "
                f"{d['lattice_csprng']:.5f}, outside [0.010, 0.025]. A uniform "
                "residual PREDICTS 1/60 = 0.01667; a value away from it means "
                "the probe is measuring something other than what it claims")
arm = (d.get("bars") or {}).get(
    "RANDU mean distance to its own 15 lattice planes", {})
if arm.get("discriminating") is not True:
    fail.append(f"pin5 ARM-DISCRIMINATES: the lattice arm reports "
                f"discriminating={arm.get('discriminating')!r}. If the CSPRNG "
                "also meets the bar the arm separates nothing and pin 4 is "
                "decorative")

if fail:
    print("FAIL — CSPRNG calibrator")
    for f in fail:
        print("  *", f)
    sys.exit(1)

print(f"PASS — CSPRNG calibrator, {n} seeds x {d['n_points']} points")
print(f"       ONE-SIDED: CSPRNG reads Poisson {d['csprng_poisson']}/{n}; a "
      "reading here would be an instrument bug, since the ideal calibrator (a "
      "Martin-Lof random sequence) is UNCOMPUTABLE and this substitutes "
      "cryptographic one-sidedness for it")
print(f"       POWERED: the periodic control is rejected {d['periodic_rejected']}"
      f"/{n}, so the nulls are not the nulls of a battery that rejects nothing")
print(f"       BLIND SPOT EXHIBITED: RANDU reads Poisson {d['randu_poisson']}/{n} "
      f"and MT19937 {d['mt_poisson']}/{n} — indistinguishable from ChaCha20 on "
      "this battery")
print(f"       AND THE DEFECT IS REALLY THERE: RANDU's distance to its own 15 "
      f"planes is {d['lattice_randu']:.6f} against the CSPRNG's "
      f"{d['lattice_csprng']:.6f} (uniform predicts 1/60 = 0.01667). The "
      "structure is present, measured, and invisible to a 1-D marginal test")
