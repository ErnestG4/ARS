"""IS THE ADDITIVE TWIN THE SAME SOUND, AND DOES IT COST LESS? The apparatus gate.

COMMITTED GENERATOR of cross_substrate/brocot_resynthesis_fidelity.json.
Predictions sealed here, before any output exists.

WHY THIS CELL EXISTS
--------------------
`brocot_detune_impossibility` closed the ratio-detune route. Exactly: over 2306
candidate detunes across 8 ratios, at unbounded magnitude, folds and permutations
included, none returns the bystander spectrum to itself while splitting the
witness pair. Locally it is worse than useless -- separating the pair by one cent
costs 2.4x to 7.4x that much bystander movement.

So the contrast has to be BUILT rather than dialled. Render the exact spectrum
additively from its own partial list, then make the twin by moving ONLY the
witness pair and leaving every other partial bit-identical. That is a
manipulation the FM synthesis path provably cannot express, which is the whole
point -- and it is also why the apparatus cannot be trusted on its own say-so.

THE OBLIGATION THIS CELL DISCHARGES
-----------------------------------
An additive resynthesis is a MODEL of the FM render. If the model is wrong, every
later listening result is a result about my model and not about the instrument
the seal is scoped to -- the model-ran-on-abstraction defect, one layer down from
where this arc already met it. So "the same sound" gets measured, not assumed.

GROUND TRUTH IS THE TIME-DOMAIN FM RENDER, NOT THE PARTIAL LIST. Comparing my
additive render against the partial list it was built from is circular and would
pass by construction. The honest reference is

    x(t) = cos(2*pi*f_c*t + I*sin(2*pi*f_c*t) + I*sin(2*pi*alpha*f_c*t))

whose true spectrum is the doubly-infinite Bessel lattice. My box is [-B,B]^2
above an amplitude floor. What the gate therefore measures is TRUNCATION ERROR,
which is a real quantity that can be too large.

WHY THE BAR IS A RATIO AND NOT A NUMBER I PICKED
------------------------------------------------
"ERB spectral distance <= X" would be a threshold invented by me, and the
one-sided-calibration lesson says an invented bar mostly measures its author. The
non-arbitrary calibration is against the contrast the apparatus has to CARRY:

    d(ADD_exact, FM_exact)   the resynthesis error
    d(FM_exact,  FM_twin)    the contrast that already exists

If the error is comparable to the difference the stimulus exists to isolate, the
apparatus cannot support the claim however good the absolute number looks. The
bar is the ratio, pre-registered at 0.10, and it can miss.

AND THE TWIN IS BUILT AT A MATCHED BEAT RATE. The FM twin (6 cents) splits the
witness pair by some amount and drags 26 of 31 partials along with it. The
additive twin splits the SAME pair to give the SAME beat frequency and moves
nothing else. Matched cue, different collateral -- which is the contrast this arc
has been missing since the beginning, and it is measurable as a ratio of the same
ERB distances.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                           ║
║                                                                              ║
║ P1  PREMISE — the ruler is live. d(FM_exact, FM_twin) exceeds the            ║
║     instrument's own noise floor (the same signal analysed over a shifted    ║
║     window) by at least 10x. If the contrast does not clear the floor, no    ║
║     ratio of distances below means anything.                                 ║
║                                                                              ║
║ E1  FIDELITY — d(ADD_exact, FM_exact) <= 0.10 * d(FM_exact, FM_twin).        ║
║     RIVAL, and the arm is scored against it: a deliberately truncated        ║
║     resynthesis at B = 2 must FAIL this same bar. An apparatus bar that a    ║
║     knowingly bad apparatus also clears is evidence for neither.             ║
║                                                                              ║
║ E2  SELECTIVITY — the apparatus earns its cost. At MATCHED witness beat      ║
║     rate, d(ADD_exact, ADD_twin) is at least 3x SMALLER than                 ║
║     d(FM_exact, FM_twin). Same cue, less collateral, by a factor worth the   ║
║     engineering. THIS IS THE CELL: if it fails, additive resynthesis buys    ║
║     nothing over the detune it replaces and the whole stage is off.          ║
║                                                                              ║
║ M1  MECHANISM — the residual really is truncation. d(ADD_exact, FM_exact)    ║
║     falls monotonically as B grows over the swept box sizes. If it does      ║
║     not, something other than truncation is driving the error and E1's       ║
║     pass would be for the wrong reason.                                      ║
║                                                                              ║
║ R1  RESOLUTION — E2 does not depend on a free parameter. The witness pair's  ║
║     phases at their moved frequencies are the one genuinely free choice in   ║
║     the construction, and beat salience is phase-sensitive, so they are      ║
║     TESTED and swept. Measured as: E2's verdict is unchanged at every        ║
║     swept phase configuration.                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

COMMENSURABILITY. The ERB instrument is taken from `brocot_marker_erb_gate`
UNCHANGED -- same 400-point geomspace grid over 50..12000 Hz, same Gaussian
smearing at w = 24.7*(4.37f/1000 + 1) evaluated at the source frequency, same
sqrt and same L2 normalisation. What differs is the INPUT: that cell fed it a
predicted partial list, this one feeds it a measured spectrum of a rendered
waveform, because the question here is about renders rather than about
predictions. Same ruler, different source, and the difference is stated because
an unstated one is how nine comparisons became one defect.

WHAT THIS CELL DOES NOT CLAIM. Nothing about audibility. Every quantity here is a
distance between spectra; whether any of it is heard is the question the
apparatus exists to make ASKABLE, and it still has a criterion in it.
"""
import json
import os
import sys
from fractions import Fraction
from math import gcd

import numpy as np
from scipy.special import jv

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/brocot"))
from redpath import redpath                                       # noqa: E402
from reachable import Bar                                         # noqa: E402
from modelparams import Model, Param, TESTED, DECLARED, swept     # noqa: E402
from verdictlattice import (Arm, compose, PREMISE as PRE_ROLE,    # noqa: E402
                            EXISTENCE as EX_ROLE,
                            MECHANISM as MECH_ROLE,
                            RESOLUTION as RES_ROLE)
from phase3.partial_prediction import order_bound                 # noqa: E402

I_MUS = 0.9
B = order_bound(I_MUS)
A = 2 * B
SR, DUR, F_C, CENTS = 44100, 3.0, 220.0, 6.0
FLOOR = 1e-4
LO, HI = 0.70, 1.40
FMIN, FMAX = 50.0, 12000.0
ERB_C = np.geomspace(FMIN, FMAX, 400)          # identical to brocot_marker_erb_gate
B_SWEEP = [2, 3, 4, 6, 8]
RIVAL_B = 2
PHASES = [0.0, 0.25, 0.5, 0.75]                # cycles, applied to the moved pair
PREREG_PHASE = "0"
FID_RATIO = 0.10
SEL_FACTOR = 3.0
FLOOR_MULT = 10.0

INSTRUMENT = Model("ERB excitation distance between rendered waveforms", [
    Param("box_halfwidth_B", TESTED, sweep=B_SWEEP,
          why="the truncation the fidelity gate exists to measure; M1 reads "
              "monotonicity across this sweep and B = 2 is also the RIVAL "
              "apparatus that must fail E1"),
    Param("witness_phase_cycles", TESTED, sweep=PHASES,
          why="the ONE genuinely free choice in the construction. The exact "
              "resynthesis has no phase freedom -- the FM identity gives "
              "all-cosine partials with signed amplitudes and cos is even, so "
              "the fold adds rather than flips. Freedom appears only where the "
              "witness pair is MOVED, and beat salience is phase-sensitive, so "
              "this is TESTED and not DECLARED"),
    Param("erb_grid", DECLARED, value=len(ERB_C),
          why="taken unchanged from brocot_marker_erb_gate so the distances "
              "here are commensurable with the ERB cells already banked"),
    Param("fidelity_ratio", DECLARED, value=FID_RATIO,
          why="the bar is a RATIO against the contrast the apparatus must "
              "carry, not an absolute distance I would be inventing; 0.10 says "
              "the resynthesis error must be an order of magnitude below the "
              "difference the stimulus isolates"),
    Param("cents", DECLARED, value=CENTS,
          why="the FM twin this arc has used throughout, and the reference "
              "whose witness beat rate the additive twin is MATCHED to"),
    Param("duration_s", DECLARED, value=DUR,
          why="3 s resolves 0.33 Hz, below the slowest witness beat in scope"),
])

T = np.arange(int(SR * DUR)) / SR


def fm_render(alpha, i_mus=I_MUS):
    """GROUND TRUTH: the actual FM synthesis path, no partial decomposition."""
    return np.cos(2 * np.pi * F_C * T
                  + i_mus * np.sin(2 * np.pi * F_C * T)
                  + i_mus * np.sin(2 * np.pi * alpha * F_C * T))


def lattice(alpha, b, floor=FLOOR):
    """(freq, signed amplitude) over the truncated box, folded to |f|."""
    out = []
    for n1 in range(-b, b + 1):
        for n2 in range(-b, b + 1):
            amp = float(jv(n1, i_of())) * float(jv(n2, i_of()))
            if abs(amp) < floor:
                continue
            f = F_C * abs(1.0 + n1 + n2 * alpha)
            out.append((f, amp, n1, n2))
    return out


def i_of():
    return I_MUS


def additive_render(parts, phase_of=None):
    """Sum the partial list. Phases are cosine unless a partial is overridden."""
    x = np.zeros_like(T)
    for k, (f, amp, n1, n2) in enumerate(parts):
        ph = 0.0 if phase_of is None else phase_of(k, n1, n2)
        x += amp * np.cos(2 * np.pi * f * T + 2 * np.pi * ph)
    return x


def erb_of_wave(x):
    """ERB excitation of a MEASURED spectrum, on brocot_marker_erb_gate's ruler."""
    X = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2
    fr = np.fft.rfftfreq(len(x), 1.0 / SR)
    m = (fr >= FMIN) & (fr <= FMAX) & (X > 0)
    fr, X = fr[m], X[m]
    w = 24.7 * (4.37 * fr / 1000.0 + 1.0)
    v = np.zeros(len(ERB_C))
    for c in range(len(ERB_C)):
        v[c] = np.sum(X * np.exp(-0.5 * ((ERB_C[c] - fr) / w) ** 2))
    v = np.sqrt(v)
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def d(u, v):
    return float(np.linalg.norm(u - v))


def witnesses(p, q):
    w1 = (-(-p // 2), -(q // 2))
    w2 = (-(p // 2), -(-q // 2))
    if max(abs(w1[0]), abs(w1[1]), abs(w2[0]), abs(w2[1])) > B:
        return None
    return w1, w2


RATIOS = sorted([Fraction(p, q) for q in range(1, A + 1) for p in range(1, A + 1)
                 if gcd(p, q) == 1 and LO <= p / q <= HI and max(p, q) <= A
                 and Fraction(p, q) != 1], key=float)

rows = []
for r in RATIOS:
    p, q = r.numerator, r.denominator
    w = witnesses(p, q)
    if w is None:
        continue
    w1, w2 = w
    af = float(r)
    at = af * 2.0 ** (CENTS / 1200.0)

    parts = lattice(af, B)
    keys = {(n1, n2) for _, _, n1, n2 in parts}
    if w1 not in keys or w2 not in keys:
        continue

    fm_e, fm_t = fm_render(af), fm_render(at)
    e_fm_e, e_fm_t = erb_of_wave(fm_e), erb_of_wave(fm_t)

    # INSTRUMENT NOISE FLOOR: the same signal over a shifted analysis window.
    # BOTH sub-windows are the SAME LENGTH -- an earlier draft compared a full
    # window against a shorter one, which conflates FFT resolution with window
    # position and would have inflated the floor with a difference that has
    # nothing to do with the instrument's repeatability.
    off = len(T) // 8
    e_w0 = erb_of_wave(fm_e[:len(T) - off])
    e_w1 = erb_of_wave(fm_e[off:])
    noise = d(e_w0, e_w1)
    contrast = d(e_fm_e, e_fm_t)

    # the FM twin's witness beat rate — what the additive twin must MATCH
    fb = abs(F_C * abs(1 + w1[0] + w1[1] * at)
             - F_C * abs(1 + w2[0] + w2[1] * at))

    add_e = additive_render(parts)
    e_add_e = erb_of_wave(add_e)
    fid = d(e_add_e, e_fm_e)

    riv_parts = lattice(af, RIVAL_B)
    e_riv = erb_of_wave(additive_render(riv_parts))
    fid_rival = d(e_riv, e_fm_e)

    # M1: truncation sweep
    bsweep = {str(b): d(erb_of_wave(additive_render(lattice(af, b))), e_fm_e)
              for b in B_SWEEP}

    # the additive twin: move ONLY the witness pair, split to give beat fb
    wi = [k for k, (_, _, n1, n2) in enumerate(parts) if (n1, n2) in (w1, w2)]
    sel = {}
    for ph in PHASES:
        tw = list(parts)
        for j, k in enumerate(wi):
            f, amp, n1, n2 = tw[k]
            tw[k] = (f + (fb / 2.0 if j == 0 else -fb / 2.0), amp, n1, n2)
        moved = set(wi)

        def phase_of(k, n1, n2, _ph=ph, _m=moved):
            return _ph if k in _m else 0.0

        e_add_t = erb_of_wave(additive_render(tw, phase_of))
        sel[f"{ph:g}"] = d(e_add_e, e_add_t)

    rows.append(dict(ratio=str(r), q=q, beat_hz=fb, n_partials=len(parts),
                     noise=noise, contrast=contrast,
                     fidelity=fid, fidelity_ratio=fid / max(contrast, 1e-300),
                     fidelity_rival_B2=fid_rival,
                     rival_ratio=fid_rival / max(contrast, 1e-300),
                     b_sweep=bsweep, add_contrast=sel,
                     selectivity=contrast / max(sel[PREREG_PHASE], 1e-300)))

print(INSTRUMENT.report())
print(f"\nI = {I_MUS}, B = {B}, {len(rows)} ratios; ERB distance between rendered "
      f"waveforms, grid {len(ERB_C)} over {FMIN:.0f}-{FMAX:.0f} Hz\n")
print(f"{'ratio':>7s} {'beat':>6s} {'noise':>8s} {'contrast':>9s} {'fid':>8s} "
      f"{'fid/con':>8s} {'rivalB2':>8s} {'addcon':>8s} {'select':>7s}")
for r in rows:
    print(f"{r['ratio']:>7s} {r['beat_hz']:>6.2f} {r['noise']:>8.5f} "
          f"{r['contrast']:>9.5f} {r['fidelity']:>8.5f} "
          f"{r['fidelity_ratio']:>8.4f} {r['rival_ratio']:>8.4f} "
          f"{r['add_contrast'][PREREG_PHASE]:>8.5f} {r['selectivity']:>7.2f}")

n = len(rows)
p1 = sum(1 for r in rows if r["contrast"] < FLOOR_MULT * r["noise"])
e1v = float(np.median([r["fidelity_ratio"] for r in rows]))
e1r = float(np.median([r["rival_ratio"] for r in rows]))
e2v = float(np.median([r["selectivity"] for r in rows]))
mono = sum(1 for r in rows
           if not all(r["b_sweep"][str(a)] >= r["b_sweep"][str(b)] - 1e-12
                      for a, b in zip(B_SWEEP, B_SWEEP[1:])))
SEL = swept("additive twin contrast by witness phase",
            {k: float(np.median([r["add_contrast"][k] for r in rows]))
             for k in (f"{p:g}" for p in PHASES)}, prereg=PREREG_PHASE)
r1 = sum(1 for r in rows
         if len({r["contrast"] / max(v, 1e-300) >= SEL_FACTOR
                 for v in r["add_contrast"].values()}) > 1)

P1 = Bar("ratios whose contrast fails to clear 10x the instrument noise floor", 0,
         direction="le", floor=0, ceiling=n,
         why=f"a count over the {n} ratios; the floor is a distance the same "
             "signal has from itself over a shifted window, so 0 is attainable")
E1 = Bar("median resynthesis error as a fraction of the contrast", FID_RATIO,
         direction="le", floor=0.0, ceiling=5.0,
         why="a ratio of ERB distances; 0 is attainable (an exact resynthesis) "
             "and a badly truncated one exceeds 1, so 5 is a generous ceiling",
         rival=f"a deliberately truncated resynthesis at B = {RIVAL_B}")
E2 = Bar("median selectivity: FM contrast over additive contrast", SEL_FACTOR,
         floor=0.0, ceiling=1e4,
         why="a ratio of ERB distances at MATCHED beat rate; 0 is attainable "
             "if the additive twin somehow moved more, and the ceiling is "
             "bounded only by the instrument's dynamic range")
M1 = Bar("ratios whose truncation error is not monotone in B", 0,
         direction="le", floor=0, ceiling=n,
         why=f"a count over the {n} ratios across the {len(B_SWEEP)}-point B sweep")
R1 = Bar("ratios whose E2 verdict changes across the phase sweep", 0,
         direction="le", floor=0, ceiling=n,
         why=f"a count over the {n} ratios across {len(PHASES)} phases")

sP, s1 = P1.score(p1), E1.score(e1v, rival_value=e1r)
s2, sM, sR = E2.score(e2v), M1.score(mono), R1.score(r1)

print()
print("  " + P1.line(p1, "{:.0f}"))
print("  " + E1.line(e1v, "{:.4f}") + f"   rival B={RIVAL_B}: {e1r:.4f}")
print("  " + E2.line(e2v, "{:.2f}"))
print("  " + M1.line(mono, "{:.0f}"))
print("  " + R1.line(r1, "{:.0f}"))
print(f"\nadditive twin contrast by witness phase (median over ratios):")
for k, v in SEL["spread"].items():
    print(f"    phase {k:>5s} cycles  ->  {v:.6f}")
print(f"  pre-registered phase {SEL['prereg']}: {SEL['value']:.6f}, "
      f"swing {SEL['swing']:.4f}"
      + ("   [UNSTABLE — beat salience depends on a free parameter]"
         if SEL["unstable"] else "   [stable across the phase sweep]"))

arms = [Arm.from_bar(sP, PRE_ROLE,
                     claim="the ERB ruler resolves the contrast at all"),
        Arm.from_bar(s1, EX_ROLE,
                     claim="the additive render IS the FM render, and a "
                           "knowingly truncated one is not"),
        Arm.from_bar(s2, EX_ROLE,
                     claim="at matched beat rate the additive twin moves far "
                           "less than the detuned twin"),
        Arm.from_bar(sM, MECH_ROLE,
                     claim="because the residual is box truncation"),
        Arm.from_bar(sR, RES_ROLE,
                     claim="and it does not depend on the witness phase")]
v = compose(arms, holds="APPARATUS_IS_FAITHFUL_AND_SELECTIVE",
            fails="APPARATUS_DOES_NOT_EARN_ITS_COST")
print(f"\nVERDICT: {v['citation']}")

with redpath("ratio x render evaluations", expect_min=40) as rp:
    rp.observed(len(rows) * (len(B_SWEEP) + len(PHASES) + 4))

json.dump(dict(I=I_MUS, B=B, sr=SR, duration_s=DUR, f_c=F_C, cents=CENTS,
               floor=FLOOR, erb_grid=len(ERB_C), fmin=FMIN, fmax=FMAX,
               b_sweep=B_SWEEP, rival_B=RIVAL_B, phases=PHASES,
               fidelity_ratio_bar=FID_RATIO, selectivity_bar=SEL_FACTOR,
               instrument=INSTRUMENT.seal(), rows=rows,
               median_fidelity_ratio=e1v, median_rival_ratio=e1r,
               median_selectivity=e2v, phase_sweep=SEL,
               bars={s["name"]: s for s in (sP, s1, s2, sM, sR)},
               verdict=v["head"], composed=v),
          open(f"{HERE}/brocot_resynthesis_fidelity.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_resynthesis_fidelity.json")
