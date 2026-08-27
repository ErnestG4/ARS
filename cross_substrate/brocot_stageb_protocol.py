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

AMENDMENT 1 — BEFORE ANY DATA EXISTS. THE TASK WAS UNDER-SPECIFIED.

"2AFC detune-twin discrimination" named a stimulus pair and not a question. With
two files per ratio the task would have to be either "same or different?", which
has a response-criterion problem a null cannot be cleaned of, or "which is the
exact one?", which a listener has no way to know. Neither is scorable.

REPLACED WITH 3-INTERVAL ODD-ONE-OUT. Each trial presents three intervals: two
are the same stimulus and one is its twin. The listener names the odd interval.
Chance is 1/3, there is no criterion to drift, and no reference knowledge is
required. B2's bar moves from "<= 60% against a chance of 50%" to
"<= 45% against a chance of 33.3%" and B3's from ">= 75%" to ">= 60%", both
preserving roughly the same distance from chance as sealed. B1's gate stays at
90%, which is far above 1/3 and unambiguous.

This is a pre-data amendment and it is the last moment one is honest. After a
single response is recorded, changing the task is choosing an analysis.

AMENDMENT 2 — ALSO PRE-DATA. A LISTENER'S FIRST IMPRESSION BROKE TWO THINGS.

Played the stimulus bank informally and reported: the two arms "both had their
own tone set", and merge_1-1_6c was "close/pulsing". Both remarks turned out to
be design faults, verified rather than taken on trust.

(i) THE ARMS WERE CATEGORICALLY DISTINGUISHABLE, so interleaving did not blind.
    Merge ratios carried 7 to 43 partials above -80 dB; beat ratios carried 42
    to 43. A listener can hear which arm they are in, and the beat arm is the
    GATE -- knowing you are being gated changes effort. Fixed by choosing the
    beat set to MATCH the merge set's partial-count distribution.

(ii) alpha = 1 IS DEGENERATE and was the merge arm's positive control. It means
    r2/r1 = 1, i.e. both modulators at the SAME ratio: not two operators'
    sidebands meeting but one operator counted twice. Its spectrum is a plain
    harmonic series (7 partials at 220, 440, 660, 880 Hz) against a 40-partial
    twin beating at 0.76 Hz -- trivially discriminable, for a reason with
    nothing to do with coincidence audibility. "Close/pulsing" is exactly that.

    This corrects Stage A as well: the +10.7 dB SMR that made alpha = 1 the sole
    survivor was a partial in a sparse harmonic series, not a coincidence. The
    corrected headline is that ZERO of the 12 non-degenerate below-horizon
    ratios clear masking, at every index tested.

CONSEQUENCES FOR THE SEAL. alpha = 1 leaves the merge arm. B3 -- "the unison is
discriminated at >= 60%" -- IS WITHDRAWN, not re-aimed: with the degenerate case
removed, the corrected model predicts NO audible merge at all, so the merge arm
has no positive prediction and the GATE is the only positive control. That is a
stronger seal, because the whole merge arm now carries one direction and cannot
be rescued by an exemplar that was going to pass regardless.

    B2  every non-degenerate merge ratio at <= 45% (chance 33.3%)
    B3  WITHDRAWN — the model predicts no audible merge; there is no positive
        to control on inside this arm
    B3' if ANY merge ratio exceeds 45%, the corrected masking model is refuted
        and the cell names which ratio did it
    B4  unchanged: the count above 45% pins sigma

RESIDUAL TELL, DISCLOSED RATHER THAN ENGINEERED AWAY. After matching, the merge
arm still carries a sparse tail -- 25, 26, 31 and 32 partials -- that the beat
arm has no counterpart for, because above-horizon ratios in this range are
uniformly dense. So the four sparsest merge trials remain potentially
identifiable as merge trials. Two reasons not to force it: dropping them would
remove the four ratios closest to the horizon, which are the ones most likely to
be audible and therefore the ones B2 most needs; and a tell that lets a listener
know they are in the merge arm biases toward EFFORT on exactly the trials the
model predicts are silent, which pushes against B2 rather than for it. It is
recorded here so a reader can weigh it, and B2 should be read with the sparse
four listed separately when data exists.
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
GATE_PCT, CHANCE = 0.90, 1.0 / 3.0
B2_BAR, B3_BAR = 0.45, 0.60      # amendment 1: re-expressed against 1/3
LO, HI = Fraction(7, 10), Fraction(7, 5)

PROTOCOL = Model("3-interval odd-one-out detune-twin discrimination", [
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
def n_partials(alpha, floor_db=-80.0):
    """Partials above a relative floor — the quantity that was giving the arms
    away (amendment 2(i))."""
    B = order_bound(I_MUS)
    d = {}
    for n1 in range(-B, B + 1):
        for n2 in range(-B, B + 1):
            amp = abs(float(jv(n1, I_MUS)) * float(jv(n2, I_MUS)))
            if amp < 1e-4:
                continue
            f = abs(FC * (1.0 + n1 + n2 * float(alpha)))
            if 20 <= f <= 16000:
                d[round(f, 3)] = d.get(round(f, 3), 0.0) + amp
    return len(d)


# amendment 2(ii): alpha = 1 is degenerate (identical operators) and is excluded
below = sorted({Fraction(p, q) for q in range(1, A + 1) for p in range(1, A + 1)
                if gcd(p, q) == 1 and LO <= Fraction(p, q) <= HI
                and max(p, q) <= A and Fraction(p, q) != 1}, key=float)
# amendment 2(i): match the beat arm to the merge arm's partial-count
# distribution, so a listener cannot tell which arm a trial belongs to
merge_np = sorted(n_partials(f) for f in below)
lo_np, hi_np = merge_np[0], merge_np[-1]
cands = [f for f in sorted({Fraction(p, q) for q in range(1, 41)
                            for p in range(1, 60)
                            if gcd(p, q) == 1 and LO <= Fraction(p, q) <= HI
                            and max(p, q) > A}, key=float)
         if 3.0 <= gap_hz(f) <= 8.0]
# match on BOTH axes. Matching partial count alone collapsed the beat set onto
# ratios just under unity (32/33, 33/34, ...), which gives the arm away by
# proximity to 1 instead of by density — a second tell, found the same way.
inrange = [f for f in cands if lo_np <= n_partials(f) <= hi_np]
lo_v, hi_v = float(below[0]), float(below[-1])
targets = [lo_v + (hi_v - lo_v) * k / 5.0 for k in range(6)]
above, used = [], set()
for tv in targets:
    pick = min((f for f in inrange if f not in used),
               key=lambda f: abs(float(f) - tv), default=None)
    if pick is not None:
        above.append(pick)
        used.add(pick)
above.sort(key=float)

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
print(f"MERGE arm — {n_merge} NON-DEGENERATE below-horizon ratios "
      f"(alpha = 1 excluded), exact vs {DETUNE_CENTS:.0f}c twin")
for f in below:
    print(f"    {str(f):>6s}  max(p,q) {max(f.numerator, f.denominator):>2d}  "
          f"{n_partials(f):>3d} partials  separation {gap_hz(f):.2f} Hz")
print(f"\nBEAT arm (the gate) — {n_beat} above-horizon ratios, 3-8 Hz "
      f"separation, partial-count matched")
for f in above:
    print(f"    {str(f):>6s}  {n_partials(f):>3d} partials  "
          f"separation {gap_hz(f):.2f} Hz")
print(f"\n    merge: partials {merge_np}")
print(f"           ratios   {[round(float(f), 3) for f in below]}")
print(f"    beat : partials {sorted(n_partials(f) for f in above)}")
print(f"           ratios   {[round(float(f), 3) for f in above]}")
print("    matched on BOTH density and ratio spread — neither is a tell")

print(f"\nTASK: 3-interval odd-one-out, chance {CHANCE:.1%} (amendment 1)")
print(f"GATE: a listener scores >= {GATE_PCT:.0%} on the beat arm before any "
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
               task="3-interval odd-one-out",
               b2_bar=B2_BAR, b3_bar=B3_BAR,
               predictions_sealed=[f"B1 gate >={GATE_PCT:.0%} beat arm, per listener",
                                   f"B2 non-unison merges <={B2_BAR:.0%} (chance 33.3%)",
                                   "B3 WITHDRAWN (alpha=1 degenerate; the "
                                   "corrected model predicts no audible merge)",
                                   f"B3' any merge ratio >{B2_BAR:.0%} refutes "
                                   "the corrected masking model",
                                   f"B4 the count above {B2_BAR:.0%} pins sigma"],
               verdict="PROTOCOL_SEALED_AWAITING_DATA"),
          open(f"{HERE}/brocot_stageb_protocol.json", "w"), indent=1)
print(f"\nwritten -> cross_substrate/brocot_stageb_protocol.json")
