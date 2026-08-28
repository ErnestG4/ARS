"""WHAT IS ACTUALLY IN THE SIGNAL: the phasing cue, measured instead of listened to.

COMMITTED GENERATOR of cross_substrate/brocot_modulation_cue.json.
Predictions sealed here, before any output exists.

WHY THIS SHOULD HAVE COME FIRST
---------------------------------
Stage B sent a listener at 180 trials. It should not have. What a listener
reports as "phasing" is amplitude modulation at a difference frequency -- a
PHYSICAL property of the rendered waveform, present whether or not anyone is
listening, and computable exactly. Two failures followed from skipping it:

  1. brocot_masked_horizon's criterion runs over the PREDICTED PARTIAL LIST, an
     abstraction, while a listener hears the RENDERED SIGNAL. A threshold model
     over one thing was used to make claims about the other.
  2. The stimulus does not isolate what it claims to. A 6-cent detune of alpha
     moves every partial with n2 != 0: at alpha = 5/4, 26 of 31 partials move
     more than a cent and five move more than six, the largest by 30.3 cents.
     The twin is a DIFFERENT SPECTRUM, so discriminating it demonstrates
     nothing about fusion. A signal-level check would have shown this in
     minutes.

    COMPUTE WHAT IS COMPUTABLE BEFORE SPENDING A LISTENER.

Human-in-the-loop belongs on the residual, after the signal-level questions are
exhausted -- not on the first pass.

WHAT IS MEASURED
----------------
For each non-degenerate below-horizon ratio, render the exact stimulus and its
6-cent twin, take the Hilbert envelope of each, and take the envelope's spectrum
over 0.5-40 Hz. That modulation spectrum IS the phasing.

The fusion cue has a predicted frequency. At the exact ratio the witness pair is
merged and contributes no beat; in the twin it splits by a computable amount, so
the cue should appear at

    f_beat = |partial_i - partial_j|  for the witness pair, in the twin

The confound has a different signature: every OTHER pair of partials also moves,
producing modulation across the whole band. So the question is not "is there a
difference" -- there obviously is -- but WHAT FRACTION OF THE DIFFERENCE SITS AT
THE FUSION CUE'S OWN FREQUENCY. That is the number that says whether the
stimulus can attribute anything, and it needs no ears.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — bars edge-probed                                        ║
║                                                                              ║
║ P1  THE CUE IS REALLY THERE — in the twin, modulation energy within 1 Hz of  ║
║     the predicted beat frequency exceeds the exact stimulus's energy in the  ║
║     same band by at least 6 dB, on the median ratio. If it misses, splitting ║
║     the witness pair produces no measurable beat and the whole fusion story  ║
║     has no signal-level correlate.                                          ║
║ P2  AND THE STIMULUS CANNOT ATTRIBUTE IT — the fraction of the TOTAL         ║
║     modulation-spectrum difference lying in that 1 Hz band is at most 0.25.  ║
║     This quantifies the design flaw: most of what changes is not the cue.    ║
║ P3  THE CONFOUND IS BROADBAND — the exact-vs-twin difference is spread over  ║
║     at least 8 distinct 1 Hz bands above a common floor, so it is not one    ║
║     stray component that could be filtered out.                             ║
║                                                                              ║
║ P1 WITH P2 IS THE FINDING. A real cue that the stimulus cannot isolate is a  ║
║ different situation from no cue at all, and it says the redesign must change ║
║ the CONTRAST, not the threshold.                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

AMENDMENT 1 — THE RESULT IS BIMODAL AND A MEDIAN WAS THE WRONG STATISTIC, which
is this repo's oldest recorded defect appearing in a new cell.

    cue fraction ~1.0:  3/4, 4/5, 5/4, 6/5, 7/5, 4/3     q = 3..5
    cue fraction ~0.0:  5/7, 5/6, 6/7, 7/8, 8/7, 7/6     q = 6..8

The split is by DENOMINATOR.

    *** THE MECHANISM STATED HERE WAS WRONG. RETRACTED 2026-08-28. ***

This paragraph read: "For q >= 6 the witness partials carry Bessel orders whose
product falls under the render threshold, so those partials are NOT IN THE
SIGNAL AT ALL. There is no cue to bury." That is false.
`brocot_cue_presence` measured the beat-band SNR directly, per ratio, over a
render-floor sweep and through int16: every ratio carries the cue, 7/8 lowest at
21.3 dB and 3/4 highest at 101.0 dB, unchanged from 1e-4 down to 1e-9 and
surviving quantisation.

The error was reading a small cue FRACTION as an absence. Fraction is the beat
band's SHARE of the total exact-vs-twin difference; a small share of a large
difference means the CONFOUND dominates, which is what a 6-cent detune moving 26
of 31 partials predicts. The bimodality below is real and it is about
ATTRIBUTABILITY, not presence.

P2's median of 0.274 and P3's median of 2 both summarise a distribution with
nothing at its centre. The verdict head STIMULUS_CONTRAST_IS_CLEAN is therefore
not readable as sealed: the contrast is clean for low q, absent for high q, and
a single number for both is the wrong shape of answer.

AMENDMENT 2 — A LISTENER'S SKIPS CONFIRMED IT, WHICH IS THE ONLY THING THE
LISTENING SESSION SHOULD EVER HAVE BEEN ASKED FOR.

90 trials were run before this cell existed, with an ill-designed task (a
forced-choice paradigm that offered a skip button, so the answered set is
selected on discriminability). The answers cannot give a rate. But the SKIP
PATTERN can, because it is a report of "these sounded the same", and it lines up
with the signal measurement:

    low cue FRACTION  (< 0.1):  answered 10/29 = 34%
    high cue FRACTION (> 0.5):  answered 29/30 = 97%

    *** DEMOTED TO UNEXPLAINED, same retraction. ***

This was reported as "the listener answered where the beat exists and skipped
where it does not", validating the measurement against a human. It does not show
that: the beat exists everywhere. What it shows is skips tracking the cue's
SHARE of the difference, and neither presence nor SNR separates the cases --
8/7 carries 55 dB of cue and was skipped 7 times out of 7, while 5/6 carries
63 dB and was answered 5 out of 5. The correlation is real and its cause is
open. It is not a validation.

AMENDMENT 3 — P1's CEILING WAS WRONG, flagged by out_of_range at 118 dB against
a declared 60. The framing was the error, not just the bound: at the exact ratio
the witness pair is MERGED and contributes no beat, so the band holds numerical
noise and the "gain" is presence-versus-absence, limited by float precision
rather than by anything physical. A dB ratio was the wrong statistic for a
presence question.
"""
import json
import os
import sys
from fractions import Fraction
from math import gcd

import numpy as np
from scipy.signal import hilbert
from scipy.special import jv

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/brocot"))
from redpath import redpath                                       # noqa: E402
from reachable import Bar                                         # noqa: E402
from modelparams import Model, Param, TESTED, DECLARED            # noqa: E402
from verdictlattice import (Arm, compose, EXISTENCE as EX_ROLE,   # noqa: E402
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from phase3.partial_prediction import order_bound                 # noqa: E402

I_MUS = 0.9
B = order_bound(I_MUS)
A = 2 * B
SR, DUR, F_C = 44100, 4.0, 220.0
CENTS = 6.0
MOD_LO, MOD_HI, BW = 0.5, 40.0, 1.0
LO, HI = 0.70, 1.40

INSTRUMENT = Model("Hilbert envelope modulation spectrum of the rendered signal", [
    Param("detune_cents", TESTED, sweep=[3.0, 6.0, 12.0],
          why="the twin's offset; the confound scales with it and the cue "
              "frequency does too, so both must be swept together"),
    Param("mod_band_hz", TESTED, sweep=[0.5, 1.0, 2.0],
          why="the width around the predicted beat used to collect cue energy; "
              "P2 must not be an artifact of a narrow window"),
    Param("duration_s", DECLARED, value=DUR,
          why="4 s resolves a 0.25 Hz modulation, comfortably below the "
              "slowest beat any witness pair produces here"),
    Param("f_c", DECLARED, value=F_C,
          why="beat frequencies scale with f_c, so the cue and confound move "
              "together and the FRACTION in P2 is f_c-invariant"),
    Param("envelope", DECLARED, value="Hilbert magnitude, full-band",
          why="a full-band envelope is the crudest and most conservative "
              "reading; a per-critical-band envelope would only ADD cue "
              "visibility, so this cannot inflate P1"),
])


def partials(alpha):
    d = {}
    for n1 in range(-B, B + 1):
        for n2 in range(-B, B + 1):
            a = float(jv(n1, I_MUS)) * float(jv(n2, I_MUS))
            if abs(a) < 1e-4:
                continue
            f = abs(F_C * (1.0 + n1 + n2 * alpha))
            if 20 <= f <= 16000:
                d[round(f, 6)] = d.get(round(f, 6), 0.0) + a
    return d


def render(alpha):
    t = np.arange(int(SR * DUR)) / SR
    x = np.zeros_like(t)
    for f, a in partials(alpha).items():
        x += a * np.cos(2 * np.pi * f * t)
    return x


def modspec(x):
    e = np.abs(hilbert(x))
    e = e - e.mean()
    w = np.hanning(len(e))
    S = np.abs(np.fft.rfft(e * w))
    fr = np.fft.rfftfreq(len(e), 1.0 / SR)
    m = (fr >= MOD_LO) & (fr <= MOD_HI)
    return fr[m], S[m]


def witness_beat(alpha, cents):
    """Frequency split of the coinciding pair once the twin detunes it."""
    p, q = Fraction(alpha).limit_denominator(64).numerator, \
        Fraction(alpha).limit_denominator(64).denominator
    n1, n1p = -(-p // 2), -(p // 2)
    n2, n2p = -(q // 2), -(-q // 2)
    if max(abs(n1), abs(n1p)) > B or max(abs(n2), abs(n2p)) > B:
        return None
    a2 = alpha * (2.0 ** (cents / 1200.0))
    f1 = abs(F_C * (1.0 + n1 + n2 * a2))
    f2 = abs(F_C * (1.0 + n1p + n2p * a2))
    return abs(f1 - f2)


RATIOS = [Fraction(p, q) for q in range(1, A + 1) for p in range(1, A + 1)
          if gcd(p, q) == 1 and LO <= p / q <= HI and max(p, q) <= A
          and Fraction(p, q) != 1]
RATIOS.sort(key=float)

rows = []
for r in RATIOS:
    fb = witness_beat(float(r), CENTS)
    if fb is None or not (MOD_LO < fb < MOD_HI):
        continue
    fr, Se = modspec(render(float(r)))
    _, St = modspec(render(float(r) * 2.0 ** (CENTS / 1200.0)))
    band = np.abs(fr - fb) <= BW / 2
    cue_e = float(np.sum(Se[band] ** 2))
    cue_t = float(np.sum(St[band] ** 2))
    gain = 10 * np.log10((cue_t + 1e-30) / (cue_e + 1e-30))
    diff = (St - Se) ** 2
    frac = float(np.sum(diff[band]) / (np.sum(diff) + 1e-30))
    edges = np.arange(MOD_LO, MOD_HI, BW)
    bandsum = np.array([np.sum(diff[(fr >= a_) & (fr < a_ + BW)]) for a_ in edges])
    live = int((bandsum > 0.02 * bandsum.max()).sum())
    rows.append(dict(ratio=str(r), beat_hz=fb, cue_gain_db=gain,
                     cue_fraction=frac, live_bands=live))

g = np.array([x["cue_gain_db"] for x in rows])
fr_ = np.array([x["cue_fraction"] for x in rows])
lb = np.array([x["live_bands"] for x in rows])
p1, p2, p3 = float(np.median(g)), float(np.median(fr_)), int(np.median(lb))

P1 = Bar("median cue gain, twin over exact, dB", 6.0, floor=-60.0, ceiling=60.0,
         why="a ratio of band energies in dB; bounded by the dynamic range of "
             "the rendered signals")
P2 = Bar("median fraction of the difference at the cue frequency", 0.25,
         direction="le", floor=0.0, ceiling=1.0,
         why="a fraction of total spectral difference: 0 to 1")
P3 = Bar("median live 1 Hz bands in the difference", 8, floor=1,
         ceiling=int((MOD_HI - MOD_LO) / BW),
         why=f"the number of 1 Hz bands between {MOD_LO} and {MOD_HI} Hz")
s1, s2, s3 = P1.score(p1), P2.score(p2), P3.score(p3)

print(INSTRUMENT.report())
print(f"\n{len(rows)} non-degenerate below-horizon ratios, "
      f"{CENTS:.0f}-cent twin, {DUR:.0f} s at {SR} Hz\n")
print(f"{'ratio':>7s} {'beat Hz':>9s} {'cue gain dB':>12s} "
      f"{'cue frac':>9s} {'live bands':>11s}")
for x in rows:
    print(f"{x['ratio']:>7s} {x['beat_hz']:>9.2f} {x['cue_gain_db']:>12.1f} "
          f"{x['cue_fraction']:>9.3f} {x['live_bands']:>11d}")
print()
for b, v, f in ((P1, p1, "{:.1f}"), (P2, p2, "{:.3f}"), (P3, p3, "{:.0f}")):
    print("  " + b.line(v, f))

v = compose([Arm.from_bar(s1, EX_ROLE,
                          claim="splitting the witness pair produces a real "
                                "measurable beat in the rendered signal"),
             Arm.from_bar(s2, EX_ROLE,
                          claim="but most of what changes is NOT that beat, so "
                                "the stimulus cannot attribute a discrimination"),
             Arm.from_bar(s3, MECH_ROLE,
                          claim="the confound is broadband, not one filterable "
                                "component")],
            holds="CUE_REAL_BUT_NOT_ISOLATED",
            fails="STIMULUS_CONTRAST_IS_CLEAN")
print(f"\nVERDICT: {v['citation']}")

with redpath("ratios rendered and analysed", expect_min=5) as rp:
    rp.observed(len(rows))

json.dump(dict(I=I_MUS, B=B, sr=SR, duration_s=DUR, f_c=F_C, cents=CENTS,
               mod_band=[MOD_LO, MOD_HI], bandwidth=BW,
               instrument=INSTRUMENT.seal(), rows=rows,
               median_cue_gain_db=p1, median_cue_fraction=p2,
               median_live_bands=p3,
               bars={s["name"]: s for s in (s1, s2, s3)},
               verdict=v["head"], composed=v),
          open(f"{HERE}/brocot_modulation_cue.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_modulation_cue.json")
