"""IS THE CUE IN THE DELIVERED SIGNAL? Split by q, swept over the render floor.

COMMITTED GENERATOR of cross_substrate/brocot_cue_presence.json.
Predictions sealed here, before any output exists.

WHY THE PREVIOUS CELL HAS TO BE REDONE
----------------------------------------
`brocot_modulation_cue` found the fusion cue present for q = 3..5 and absent for
q = 6..8, and reported both through a MEDIAN -- summarising a bimodal
distribution by a point with nothing at its centre. It also attributed the
absence to partials falling under a 1e-4 render cutoff that I chose rather than
derived. Two things are wrong with that: the answer is a function of q and was
collapsed, and "absent" may be an artifact of my own threshold.

THE THRESHOLD QUESTION IS THE INTERESTING ONE, and it has a hard floor that a
perceptual model does not. A listener's threshold is a criterion with an
attention state in it -- there is no absolute perceptible limit, which is
exactly why the listening arm could not settle anything. But the DELIVERED
SIGNAL has non-negotiable floors:

    my render cutoff        1e-4 relative -- arbitrary, mine, and swept here
    float32/float64 render  ~1e-7 / ~1e-16 -- effectively unbounded
    16-BIT QUANTISATION     ~1.5e-5 of full scale, about -96 dB

The last one is a fact about the WAV, not about ears. If the witness pair's beat
survives the cutoff sweep but dies at 16-bit, then "not present" is grounded in
the delivery format and needs no perceptual model at all -- which is a far
stronger place to stand than a masked threshold.

WHAT COUNTS AS PRESENT
-----------------------
Render exact and twin, take the Hilbert envelope, and take its spectrum. The cue
is a beat at a computable frequency f_beat in the TWIN that the exact stimulus
does not have (there the pair is merged). Presence is an SNR against the
envelope spectrum's own floor in neighbouring bands -- a within-signal
comparison, so it needs no external reference.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — reported PER q, never pooled                            ║
║                                                                              ║
║ Q1  THE SPLIT IS CLEAN IN q — at the shipped 1e-4 cutoff, every ratio with   ║
║     the same denominator agrees on whether the cue is present. Measured as:  ║
║     zero denominators show mixed behaviour. If a q is mixed, q is not the    ║
║     variable and the previous cell's reading was a coincidence.              ║
║ Q2  AND ABSENCE IS A CUTOFF ARTIFACT — dropping the render floor to 1e-9     ║
║     restores the cue for at least 3 ratios that lacked it at 1e-4. This is   ║
║     the arm that says my own threshold was doing the work.                   ║
║ Q3  BUT 16-BIT QUANTISATION REMOVES IT AGAIN — after an int16 round trip at  ║
║     the 1e-9 floor, at most 1 of those restored ratios still shows the cue.  ║
║     THIS IS THE CELL. If it holds, "not present" is a property of the        ║
║     delivered WAV rather than of my cutoff or of anyone's ears, and the      ║
║     high-q ratios cannot carry a fusion cue at 16 bits however anyone        ║
║     listens.                                                                ║
╚══════════════════════════════════════════════════════════════════════════════╝

AMENDMENT 1 — THE PREMISE IS FALSE AND THIS CELL RETRACTS ITS OWN PREDECESSOR.

Q2 and Q3 both assume some ratios LACK the cue at the shipped 1e-4 floor. They
do not. Measured SNR of the beat band against the envelope spectrum's own floor,
for all twelve non-degenerate ratios, at every render floor and both
quantisations:

    lowest   7/8   21.3 dB      highest  3/4  101.0 dB
    and every value is identical across 1e-4, 1e-6 and 1e-9, and survives int16

So there is nothing to restore, Q2 scores 0 against a bar of 3, and Q3 is
INAPPLICABLE -- an arm with an empty population, which `reachable` refused to
let me construct at all and was right to.

WHAT THIS RETRACTS. `brocot_modulation_cue`'s amendment 1 said that for q >= 6
"the witness partials' Bessel product falls under the render threshold, so they
are NOT IN THE SIGNAL AT ALL", and called that a stronger claim than masking.
It is not a claim at all -- it is false. The witness partials are present and
their beat is 21 to 62 dB above the envelope floor for exactly those ratios.

WHERE THE ERROR CAME FROM. That cell measured cue FRACTION -- the share of the
total exact-vs-twin difference lying in the beat band -- and I read a small
fraction as absence. A small share of a large difference is not an absence; it
means the CONFOUND dominates, which is what the 6-cent detune moving 26 of 31
partials would predict. The bimodality is real and it is about attributability,
not presence.

AND THE 97-vs-34 SKIP CORRELATION INHERITS THE DOUBT. It split ratios by cue
fraction, so it shows the listener's skips tracking the cue's SHARE of the
difference, not its presence. Whether that is a perceptual story or a
coincidence is now open: 8/7 has 55 dB of cue and was skipped 7 times out of 7,
while 5/6 has 63 dB and was answered 5 out of 5. Presence does not separate
them and neither does SNR. That correlation is demoted to unexplained.
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
SR, DUR, F_C, CENTS = 44100, 3.0, 220.0, 6.0
FLOORS = [1e-4, 1e-6, 1e-9]
SNR_DB = 6.0
LO, HI = 0.70, 1.40

INSTRUMENT = Model("Hilbert modulation spectrum of the delivered signal", [
    Param("render_floor", TESTED, sweep=FLOORS,
          why="the relative amplitude below which a partial is not synthesised. "
              "1e-4 was MY inherited choice and the previous cell attributed an "
              "absence to it; sweeping is the whole point of this redo"),
    Param("quantisation", TESTED, sweep=["float64", "int16"],
          why="16-bit is the delivery format, and its noise floor is a fact "
              "about the WAV rather than a criterion about ears"),
    Param("snr_db", DECLARED, value=SNR_DB,
          why="presence is judged against the envelope spectrum's OWN floor in "
              "neighbouring bands, so this is a within-signal contrast and not "
              "an external threshold; 6 dB is one doubling of amplitude"),
    Param("duration_s", DECLARED, value=DUR,
          why="3 s resolves 0.33 Hz, below the slowest witness beat here"),
    Param("f_c", DECLARED, value=F_C,
          why="beat frequencies and the noise floor both scale with f_c, so the "
              "SNR is f_c-invariant"),
])


def partials(alpha, floor):
    d = {}
    for n1 in range(-B, B + 1):
        for n2 in range(-B, B + 1):
            a = float(jv(n1, I_MUS)) * float(jv(n2, I_MUS))
            if abs(a) < floor:
                continue
            f = abs(F_C * (1.0 + n1 + n2 * alpha))
            if 20 <= f <= 16000:
                d[round(f, 6)] = d.get(round(f, 6), 0.0) + a
    return d


T = np.arange(int(SR * DUR)) / SR


def render(alpha, floor, quant):
    x = np.zeros_like(T)
    for f, a in partials(alpha, floor).items():
        x += a * np.cos(2 * np.pi * f * T)
    m = np.max(np.abs(x))
    if m > 0:
        x = x / m * 0.7
    if quant == "int16":
        x = np.round(x * 32767.0).astype(np.int16).astype(np.float64) / 32767.0
    return x


def cue_snr(alpha, floor, quant, f_beat):
    """SNR of the beat band against the envelope spectrum's own neighbourhood."""
    x = render(alpha * 2.0 ** (CENTS / 1200.0), floor, quant)
    e = np.abs(hilbert(x))
    e = e - e.mean()
    S = np.abs(np.fft.rfft(e * np.hanning(len(e)))) ** 2
    fr = np.fft.rfftfreq(len(e), 1.0 / SR)
    band = np.abs(fr - f_beat) <= 0.5
    near = (fr > 0.5) & (fr < 40.0) & ~band
    if not band.any() or not near.any():
        return -np.inf
    return float(10 * np.log10((S[band].mean() + 1e-300)
                               / (np.median(S[near]) + 1e-300)))


def witness_beat(alpha):
    fr = Fraction(alpha).limit_denominator(64)
    p, q = fr.numerator, fr.denominator
    n1, n1p = -(-p // 2), -(p // 2)
    n2, n2p = -(q // 2), -(-q // 2)
    if max(abs(n1), abs(n1p)) > B or max(abs(n2), abs(n2p)) > B:
        return None
    a2 = alpha * 2.0 ** (CENTS / 1200.0)
    return abs(abs(F_C * (1 + n1 + n2 * a2)) - abs(F_C * (1 + n1p + n2p * a2)))


RATIOS = sorted([Fraction(p, q) for q in range(1, A + 1) for p in range(1, A + 1)
                 if gcd(p, q) == 1 and LO <= p / q <= HI and max(p, q) <= A
                 and Fraction(p, q) != 1], key=float)

rows = []
for r in RATIOS:
    fb = witness_beat(float(r))
    if fb is None or not (0.5 < fb < 40.0):
        continue
    wa = abs(float(jv(-(-r.numerator // 2), I_MUS))
             * float(jv(-(r.denominator // 2), I_MUS)))
    rec = dict(ratio=str(r), q=r.denominator, beat_hz=fb, witness_amp=wa)
    for fl in FLOORS:
        for qz in ("float64", "int16"):
            rec[f"{fl:g}|{qz}"] = cue_snr(float(r), fl, qz, fb)
    rows.append(rec)


def present(rec, fl, qz):
    return rec[f"{fl:g}|{qz}"] >= SNR_DB


byq = {}
for rec in rows:
    byq.setdefault(rec["q"], []).append(rec)
mixed = sum(1 for q, v in byq.items()
            if len({present(x, 1e-4, "float64") for x in v}) > 1)

base = {rec["ratio"] for rec in rows if present(rec, 1e-4, "float64")}
deep = {rec["ratio"] for rec in rows if present(rec, 1e-9, "float64")}
restored = deep - base
survive = {rec["ratio"] for rec in rows
           if rec["ratio"] in restored and present(rec, 1e-9, "int16")}

q1, q2, q3 = mixed, len(restored), len(survive)
Q1 = Bar("denominators with mixed cue presence", 0, direction="le", floor=0,
         ceiling=len(byq), why=f"a count of the {len(byq)} denominators present")
Q2 = Bar("ratios restored by dropping the render floor", 3, floor=0,
         ceiling=len(rows), why=f"a count of the {len(rows)} ratios tested")
# Q3 IS INAPPLICABLE when nothing was restored: an arm with an empty population.
# `reachable` refuses to construct it, correctly, so it is not constructed.
Q3 = (Bar("restored ratios surviving int16", 1, direction="le", floor=0,
          ceiling=len(restored),
          why="a count of the restored ratios")
      if len(restored) > 1 else None)
s1, s2 = Q1.score(q1), Q2.score(q2)
s3 = Q3.score(q3) if Q3 else None

print(INSTRUMENT.report())
print(f"\n{len(rows)} non-degenerate below-horizon ratios, {CENTS:.0f}-cent twin, "
      f"{DUR:.0f} s\ncue present = beat-band SNR >= {SNR_DB:.0f} dB against the "
      f"envelope spectrum's own floor\n")
hdr = "".join(f"{f'{fl:g}/{qz[:3]}':>12s}" for fl in FLOORS
              for qz in ("float64", "int16"))
print(f"{'ratio':>7s} {'q':>3s} {'beat':>6s} {'wit amp':>9s}" + hdr)
for rec in sorted(rows, key=lambda x: (x["q"], x["ratio"])):
    cells = "".join(f"{rec[f'{fl:g}|{qz}']:>11.1f}" + ("*" if present(rec, fl, qz) else " ")
                    for fl in FLOORS for qz in ("float64", "int16"))
    print(f"{rec['ratio']:>7s} {rec['q']:>3d} {rec['beat_hz']:>6.2f} "
          f"{rec['witness_amp']:>9.2e}" + cells)
print("   * = cue present\n")
print(f"present at 1e-4/float: {sorted(base)}")
print(f"present at 1e-9/float: {sorted(deep)}")
print(f"restored by the floor sweep: {sorted(restored)}")
print(f"of those, surviving int16:   {sorted(survive)}")
print()
for b, v in ((Q1, q1), (Q2, q2)):
    print("  " + b.line(v, "{:.0f}"))
if Q3:
    print("  " + Q3.line(q3, "{:.0f}"))
else:
    print(f"  restored ratios surviving int16: INAPPLICABLE — "
          f"{len(restored)} ratios were restored, so there is no population")

arms = [Arm.from_bar(s2, EX_ROLE,
                     claim="some ratios lacked the cue and the render floor "
                           "was why"),
        Arm.from_bar(s1, RES_ROLE, claim="q is the variable, not a coincidence")]
if Q3:
    arms.append(Arm.from_bar(s3, MECH_ROLE,
                             claim="16-bit delivery removes what the sweep "
                                   "restored"))
else:
    arms.append(Arm("restored ratios surviving int16", MECH_ROLE, met=False,
                    inert=True, note="empty population: nothing was restored",
                    claim="16-bit delivery removes what the sweep restored"))
v = compose(arms, holds="ABSENCE_IS_A_DELIVERY_FLOOR",
            fails="CUE_IS_PRESENT_THROUGHOUT")
print(f"\nVERDICT: {v['citation']}")
if v["head"] == "CUE_IS_PRESENT_THROUGHOUT":
    lo = min(rows, key=lambda x: x[f"{FLOORS[0]:g}|float64"])
    hi = max(rows, key=lambda x: x[f"{FLOORS[0]:g}|float64"])
    print(f"  Every ratio carries the beat, {lo['ratio']} lowest at "
          f"{lo[f'{FLOORS[0]:g}|float64']:.1f} dB and {hi['ratio']} highest at "
          f"{hi[f'{FLOORS[0]:g}|float64']:.1f} dB,")
    print("  unchanged by the render floor and surviving int16. The previous")
    print("  cell's 'not in the signal' is retracted: it read a small SHARE of")
    print("  a large difference as an absence.")

with redpath("ratio x floor x quantisation renders", expect_min=60) as rp:
    rp.observed(len(rows) * len(FLOORS) * 2)

json.dump(dict(I=I_MUS, B=B, sr=SR, duration_s=DUR, f_c=F_C, cents=CENTS,
               floors=FLOORS, snr_db=SNR_DB, instrument=INSTRUMENT.seal(),
               rows=rows, by_q={str(k): [x["ratio"] for x in v_]
                                for k, v_ in byq.items()},
               present_base=sorted(base), present_deep=sorted(deep),
               restored=sorted(restored), survive_int16=sorted(survive),
               bars={sc["name"]: sc for sc in (s1, s2, s3) if sc},
               q3_inapplicable=bool(Q3 is None),
               verdict=v["head"], composed=v),
          open(f"{HERE}/brocot_cue_presence.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_cue_presence.json")
