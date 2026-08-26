"""STAGE B: the listening protocol, sealed and its stimuli generated.

COMMITTED GENERATOR of cross_substrate/brocot_stageb_protocol.json and of the
stimulus bank under cross_substrate/stageb_stimuli/.

THIS CELL PRODUCES NO VERDICT ABOUT AUDIBILITY. It cannot: the measurement needs
listeners. What it does is take Stage B as far as it can go without them --
generate the stimuli, seal the predictions, and declare the inclusion gate
BEFORE any data exists, which is the only moment those can honestly be fixed.
Its own verdict is PROTOCOL_SEALED_AWAITING_DATA and nothing else.

WHY IT IS ON THE CRITICAL PATH
--------------------------------
Two dispositions wait on one parameter. `brocot_masked_horizon` showed the
audible-horizon count is filter-width sensitive (1 at sigma = ERB, 2 at ERB/4 at
I = 0.9; 0 to 6 at I = 3.0), and `brocot_filter_worth_it` showed the reachability
filter's benefit flips on the same knob (+2.1% at ERB, +19.9% at ERB/2.5). When
one measurement blocks two decisions it runs next; that is the dependency graph,
not a preference.

THE TWO ARMS, AND WHY THE SPLIT IS FORCED BY THE STIMULUS
-----------------------------------------------------------
The detune-twin stimulus probes two different things at once, and they carry
OPPOSITE predictions, so they must be scored separately:

  MERGE ARM   ratios BELOW the horizon, where the exact ratio fuses two partials
              and the detuned twin does not. Masking predicts these are
              INDISCRIMINABLE at I = 0.9 except for 1/1.
  BEAT  ARM   ratios ABOVE the horizon with a separation in the 3-8 Hz band,
              where the exact ratio beats audibly and the twin beats at a
              different rate. Squarely discriminable; audibility was never in
              question here.

THE INCLUSION GATE, DECLARED HERE AND NOWHERE ELSE
----------------------------------------------------
A listener who fails the BEAT arm is not hearing the stimulus, so their merge
data says nothing about merges. The beat arm is therefore a PER-LISTENER
PASS-GATE: >= 90% correct on beat trials, evaluated before any merge trial from
that listener is counted.

This is declared now because a post-hoc listener exclusion is the oldest way to
manufacture a null, and the difference between an inclusion criterion and an
exclusion criterion is entirely when it was written down.

WHAT AN EMBARRASSMENT WOULD MEAN, stated in advance so it cannot be reframed
later: if listeners reliably discriminate merges the masking model says are
buried, that is a finding about the model's JURISDICTION -- most likely that
static relative masking is the wrong instrument for a fusion cue that has
temporal structure -- and not noise. It would be at least as informative as
confirmation, and it would invalidate the sigma-conditional dispositions rather
than resolve them.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — to be scored when listener data exists, not before      ║
║                                                                              ║
║ B1  GATE — every INCLUDED listener scores >= 90% on the beat arm. This is an ║
║     inclusion criterion, not a result.                                      ║
║ B2  MERGES ARE BURIED — among included listeners, pooled discrimination on   ║
║     below-horizon ratios OTHER than 1/1 is at most 60% (chance is 50%).     ║
║ B3  EXCEPT THE UNISON — 1/1 is discriminated at >= 75%. The masking model    ║
║     names it as the one coincidence that clears threshold, so it must be     ║
║     heard; a null here refutes the model as surely as B2 failing would.     ║
║ B4  THE COUNT PINS sigma — the number of below-horizon ratios discriminated  ║
║     above 60% is the measurement two dispositions wait on: 1 implies         ║
║     sigma ~ ERB, 3 implies sigma ~ ERB/2.5, and the audible-horizon and      ║
║     filter rows re-adjudicate against whichever lands.                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import json
import os
import sys
from fractions import Fraction
from math import gcd

import numpy as np
from scipy.io import wavfile
from scipy.special import jv

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/brocot"))
from redpath import redpath                                       # noqa: E402
from modelparams import Model, Param, TESTED, DECLARED            # noqa: E402
from phase3.partial_prediction import order_bound                 # noqa: E402

OUT = os.path.join(HERE, "stageb_stimuli")
SR, DUR, FC, I_MUS = 44100, 2.0, 220.0, 0.9
DETUNE_CENTS = 6.0
GATE_PCT, CHANCE = 0.90, 0.50
LO, HI = Fraction(7, 10), Fraction(7, 5)

PROTOCOL = Model("2AFC detune-twin discrimination", [
    Param("detune_cents", TESTED, sweep=[3.0, 6.0, 12.0],
          why="the twin's offset from the exact ratio; too small and the twin "
              "is the same stimulus, too large and it is a different ratio. "
              "Swept so the staircase has room and so a null cannot be blamed "
              "on one unlucky offset."),
    Param("sustain_s", DECLARED, value=DUR,
          why="separations of 1-24 Hz need 40 ms to 1 s to exist at all, so a "
              "staccato stimulus cannot carry the category. 2 s clears the "
              "slowest beat in the field by 2x."),
    Param("f_c", DECLARED, value=FC,
          why="the field is scale-invariant in f_c; 220 Hz places the whole "
              "partial set in the region where ERB is well characterised"),
    Param("I", DECLARED, value=I_MUS,
          why="BROCOT-SPEC's own typical index, and the index at which the "
              "masking prediction is sharpest (1 of 13)"),
    Param("gate_pct", DECLARED, value=GATE_PCT,
          why="a listener below 90% on a squarely-audible arm is not hearing "
              "the stimulus; declared before data so it is an inclusion "
              "criterion and not a post-hoc exclusion"),
])


def render(alpha, cents=0.0):
    t = np.arange(int(SR * DUR)) / SR
    a = float(alpha) * (2.0 ** (cents / 1200.0))
    B = order_bound(I_MUS)
    x = np.zeros_like(t)
    for n1 in range(-B, B + 1):
        for n2 in range(-B, B + 1):
            amp = float(jv(n1, I_MUS)) * float(jv(n2, I_MUS))
            if amp == 0.0:
                continue
            f = FC * (1.0 + n1 * 1.0 + n2 * a)
            if abs(f) < 20.0 or abs(f) > 16000.0:
                continue
            x += amp * np.cos(2 * np.pi * f * t)
    env = np.ones_like(t)
    k = int(0.02 * SR)
    env[:k] = np.linspace(0, 1, k)
    env[-k:] = np.linspace(1, 0, k)
    x *= env
    m = np.max(np.abs(x))
    return (x / m * 0.7 if m > 0 else x).astype(np.float32)


def gap_hz(alpha):
    B = order_bound(I_MUS)
    A = 2 * B
    p, q = alpha.numerator, alpha.denominator
    best = None
    for a1 in range(-A, A + 1):
        for a2 in range(-A, A + 1):
            if a1 == 0 and a2 == 0:
                continue
            v = abs(a1 * q + a2 * p)
            if best is None or v < best:
                best = v
    return best / q * FC


A = 2 * order_bound(I_MUS)
below = sorted({Fraction(p, q) for q in range(1, A + 1) for p in range(1, A + 1)
                if gcd(p, q) == 1 and LO <= Fraction(p, q) <= HI
                and max(p, q) <= A}, key=float)
above = [f for f in sorted({Fraction(p, q) for q in range(1, 41)
                            for p in range(1, 60)
                            if gcd(p, q) == 1 and LO <= Fraction(p, q) <= HI
                            and max(p, q) > A}, key=float)
         if 3.0 <= gap_hz(f) <= 8.0][:6]

os.makedirs(OUT, exist_ok=True)
manifest = []
for arm, ratios in (("merge", below), ("beat", above)):
    for f in ratios:
        for c in (0.0, DETUNE_CENTS):
            tag = f"{arm}_{f.numerator}-{f.denominator}_{int(c)}c"
            wavfile.write(os.path.join(OUT, tag + ".wav"), SR,
                          (render(f, c) * 32767).astype(np.int16))
            manifest.append(dict(arm=arm, ratio=str(f), cents=c, file=tag + ".wav",
                                 separation_hz=round(gap_hz(f), 3),
                                 fuses=bool(gap_hz(f) == 0.0)))

n_merge = sum(1 for m in manifest if m["arm"] == "merge") // 2
n_beat = sum(1 for m in manifest if m["arm"] == "beat") // 2

print(PROTOCOL.report())
print(f"\nstimuli written to {os.path.relpath(OUT, ROOT)}/  "
      f"({len(manifest)} files, {SR} Hz, {DUR:.0f} s)\n")
print(f"MERGE arm — {n_merge} below-horizon ratios, exact vs {DETUNE_CENTS:.0f}c twin")
for f in below:
    print(f"    {str(f):>6s}  max(p,q) {max(f.numerator, f.denominator):>2d}  "
          f"separation {gap_hz(f):.2f} Hz  "
          f"{'<- masking says THIS one is heard' if f == 1 else ''}")
print(f"\nBEAT arm (the gate) — {n_beat} above-horizon ratios, 3-8 Hz separation")
for f in above:
    print(f"    {str(f):>6s}  separation {gap_hz(f):.2f} Hz")

print(f"\nGATE: a listener scores >= {GATE_PCT:.0%} on the beat arm before any "
      f"of their merge\n      trials are counted. Declared here, before data.")
print("\nVERDICT: PROTOCOL_SEALED_AWAITING_DATA")
print("  No audibility claim is made or implied by this cell. It generates the")
print("  stimuli and fixes the predictions, the gate and the interpretation of")
print("  an embarrassment at the only moment those can honestly be fixed.")

with redpath("stimulus files written", expect_min=20) as rp:
    rp.observed(len(manifest))

json.dump(dict(sr=SR, duration_s=DUR, f_c=FC, I=I_MUS,
               detune_cents=DETUNE_CENTS, gate_pct=GATE_PCT, chance=CHANCE,
               protocol=PROTOCOL.seal(), manifest=manifest,
               n_merge_ratios=n_merge, n_beat_ratios=n_beat,
               predictions_sealed=["B1 gate >=90% beat arm, per listener",
                                   "B2 non-unison merges <=60%",
                                   "B3 unison >=75%",
                                   "B4 the count above 60% pins sigma"],
               verdict="PROTOCOL_SEALED_AWAITING_DATA"),
          open(f"{HERE}/brocot_stageb_protocol.json", "w"), indent=1)
print(f"\nwritten -> cross_substrate/brocot_stageb_protocol.json")
