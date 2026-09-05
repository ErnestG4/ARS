"""CAN A RATIO DETUNE SPLIT THE WITNESS PAIR AND LEAVE THE REST ALONE?

COMMITTED GENERATOR of cross_substrate/brocot_detune_impossibility.json.
Predictions sealed here, before any output exists.

WHY THIS CELL EXISTS
--------------------
`heard-as-listening` is not blocked on listeners. It is blocked on a CONTRAST.
Every stimulus this arc has built compares an exact ratio against a detuned twin,
and `brocot_modulation_cue` measured what that comparison actually does: a 6-cent
detune at 5/4 moves 26 of 31 partials. So a listener discriminating the pair
tells you the two spectra differ -- which was never in doubt -- and cannot
attribute the discrimination to the coincidence. The seal claims to test fusion;
the stimulus tests "is this a different sound".

My instinct, recorded in the ledger, is that NO ratio detune can do better,
because one alpha controls every alpha-dependent partial at once. An instinct is
not a scope statement. This cell tries to turn it into one, and is built so that
the interesting outcome is the one that refutes me.

THE LATTICE, AND THE ONE DEGREE OF FREEDOM
------------------------------------------
Two simultaneous modulators at ratios 1 and alpha put a partial at

    f(n1, n2; alpha) = f_c * |1 + n1 + n2*alpha|,   amplitude J_n1(I)*J_n2(I)

Write a = 1 + n1 + n2*alpha for the SIGNED argument. A ratio detune moves alpha
and nothing else, so the whole spectrum is a one-parameter family: K partials,
one knob. For small delta the shift is

    df_k/d(delta) = f_c * sign(a_k) * n2_k

-- a direction vector the LATTICE fixes, not the player. "Split the witnesses,
freeze the bystanders" asks for a shift with zero in every bystander coordinate
and nonzero in the witness ones. If any bystander has n2 != 0, that vector is
off the line, and no magnitude of delta reaches it.

WHY THAT ARGUMENT IS NOT YET A THEOREM, AND WHERE THE COUNTEREXAMPLE HIDES
-------------------------------------------------------------------------
The absolute value. f is PIECEWISE linear in alpha, and a partial that crosses
a = 0 comes back up the other side. This is the FOLD, the standing caveat of
this arc, and it has bitten three times. A folded partial can RETURN TO ITS OWN
STARTING FREQUENCY at a nonzero detune:

    |a_k + n2_k*d| = |a_k|   <=>   d = 0   or   d = -2*a_k / n2_k

So every alpha-dependent partial IS individually freezable, at its own d. The
question is whether one d freezes them all -- which happens exactly when
(1 + n1_k)/n2_k is constant across the moving bystanders. That is a real
condition on a real lattice, it is not obviously empty, and if it holds anywhere
then ratio detune DOES isolate and this cell has found the manipulation.

AND ONE MORE ESCAPE ROUTE, WHICH PER-PARTIAL FREEZING WOULD MISS. What must be
held fixed is the SPECTRUM, not the identity of each partial. Two bystanders
could SWAP frequencies and leave the sound unchanged. So the honest question is
whether the bystander spectrum -- the multiset of (frequency, summed amplitude)
over bins -- returns to itself, permutations allowed.

That version is still decidable, and exhaustively so. If the multiset is
preserved then in particular each moving bystander j lands on SOME bystander
frequency |a_k|, so any such d satisfies a_j + n2_j*d = +/- a_k for some pair
(j, k). That is a FINITE candidate set, computable in exact rationals, with no
scan and no bound on |d|. Enumerate it, test each candidate, and the answer is a
theorem rather than a sample.

    E2 is therefore UNBOUNDED IN MAGNITUDE and exact. E3 below is the bounded,
    practical, approximate statement. They answer different questions and both
    are reported.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                           ║
║                                                                              ║
║ P1  PREMISE — the witness pair really does coincide. For every ratio in      ║
║     scope the two witness index vectors give EXACTLY equal |a| in rational   ║
║     arithmetic. Measured as: zero ratios with nonzero separation. If this    ║
║     fails, nothing below is readable and the horizon's own construction is   ║
║     wrong.                                                                   ║
║                                                                              ║
║ E1  THE LINEAR ARM — no ratio has an all-frozen bystander set. Measured as:  ║
║     zero ratios in which every bystander has n2 = 0. If a ratio has none     ║
║     that move, a detune isolates trivially and the whole question is over.   ║
║                                                                              ║
║ E2  THE FOLD ARM, exact and unbounded — no ratio admits a detune d != 0      ║
║     that returns the bystander spectrum to itself (permutations allowed)     ║
║     while splitting the witness bin. Measured as: zero such ratios, over     ║
║     the COMPLETE candidate set. THIS IS THE ARM THAT CAN FIND THE            ║
║     COUNTEREXAMPLE, and the one I most expect to be wrong about.             ║
║                                                                              ║
║ E3  THE PRACTICAL ARM, threshold-free — no ratio has isolation margin > 1,   ║
║     where margin = max over d of (witness split) / (largest bystander        ║
║     shift), both in cents. Margin > 1 means there EXISTS a tolerance at      ║
║     which the pair separates by more than anything else moves, with no       ║
║     tolerance chosen in advance. Measured as: zero ratios above 1.           ║
║     THE MARGIN DISTRIBUTION IS REPORTED IN FULL, per the presence/share      ║
║     rule -- a count over a threshold is what got the cue question wrong.     ║
║                                                                              ║
║ M1  MECHANISM — the shift really is the lattice-fixed direction. Measured    ║
║     numerically: max relative deviation of df_k/dd from f_c*sign(a_k)*n2_k   ║
║     is <= 1e-6 across every ratio and partial. This is the arm that fails    ║
║     if my model of the lattice is wrong, rather than my reasoning about it.  ║
║                                                                              ║
║ R1  RESOLUTION — the E3 answer is not a grid artifact. Halving the delta     ║
║     step changes the margin>1 verdict for zero ratios.                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

POSITIVE CONTROL, RUN FIRST AND PRINTED. A detector that reports "no freeze
exists" is worthless until it is shown to find one. So the cell first builds a
lattice in which a common reflection freeze DOES exist by construction --
bystanders sharing a single (1+n1)/n2, which forces one common d -- and requires
E2's machinery to find it. If the control does not fire, the run aborts and
no verdict is written. An arm that cannot fire is not evidence.

AMENDMENT 1 — M1 FIRED, AND IT CAUGHT TWO INSTRUMENT DEFECTS, NOT A FINDING.

The first run scored M1 at a relative deviation of EXACTLY 1.0, which is the
signature of a structural error rather than numerical noise. It was.

At alpha = 3/4 the index (2, -4) gives a = 1 + 2 - 3 = 0 EXACTLY, and at 4/3 the
index (3, -3) gives a = 1 + 3 - 4 = 0. Those partials sit at DC. Their Bessel
products (1.55e-4, 2.08e-4) clear the 1e-4 floor, so they were in the bystander
set. Two consequences, both mine:

  (a) |a| has a CORNER at a = 0, so df/d(alpha) does not exist there, and M1's
      predicted direction sign(a)*n2 is not defined either. M1 was right and the
      sealed claim "the shift is the lattice-fixed direction" is FALSE AS
      WRITTEN -- it holds away from fold points, and a partial at DC is a
      partial already sitting on one. The corrected claim is piecewise, and the
      arm now tests it away from the corners while COUNTING the corners.

  (b) Far worse, and the reason this is an amendment and not a footnote: with
      f0 = 0 the shift in cents is log(x/0) = infinity, so mb was infinite at
      every delta, `ok` was empty, and margin fell through to its initial 0.0.
      Ratios 3/4 and 4/3 were then counted as margin <= 1, i.e. as PASSES of
      the arm, on the strength of a division by zero. That is non-evidence
      scored as a verdict, in the denominator of my own headline count -- the
      dominant recorded error mode of this repo, produced here by the cell that
      cites it.

  (c) And the tau column was a grid artifact. A linear grid of 4001 points over
      +/-2400 cents has a step of 1.2 cents, so no sampled delta could ever hold
      every bystander within 1 cent, and "usable split at tau = 1c: 0.000" was
      a statement about my grid. R1 did not catch it because R1 only re-checked
      the margin verdict, not the tau numbers -- a resolution arm scoped to
      half of what it was guarding.

FIXED, AND THE PREDICTIONS ARE UNCHANGED: the cents metric is now applied only
to partials above a declared pitch floor, unpitched partials are counted and
reported separately in Hz rather than silently making a ratio unmeasurable, the
delta grid is logarithmic so it resolves the small-tolerance regime, and R1 now
re-checks the tau result as well as the margin. No bar moved and no prediction
was rewritten; what changed is the instrument, which is what a MECHANISM arm is
for. Recorded here because the fix came AFTER seeing output, which is exactly
the circumstance a seal exists to make visible rather than deniable.

AMENDMENT 2 — E3 MISSED, AND THE MISS LOCATES THE ANSWER RATHER THAN OVERTURNING IT.

E3 asked whether ANY delta in the scan window gives isolation margin > 1. It
does, for 8 ratios of 8. My sealed prediction was wrong and stays on the record
as wrong: the composed head is ISOLATING_DETUNE_EXISTS, read off the arm as
sealed, and nothing below rescues it.

But WHERE the margin is achieved was not part of the statistic, and it decides
what the number means:

    margin achieved at   814 to 1499 cents   -- 8 to 15 SEMITONES of detune

That is not a detune. At 1000 cents alpha has become a different ratio, the
spectrum is a different spectrum, and "the bystanders were disturbed less than
the witnesses separated" is true of a sound nobody would call the same sound.
E3's window was right for E2, which must be unbounded to be a theorem, and
WRONG for E3, where the design question is local.

So a post-hoc statistic is added, and labelled as post-hoc: the LOCAL isolation
ratio, split rate over largest-bystander rate in the small-delta limit. It is
not a new arm, it does not touch the head, and it was chosen after seeing that
the margin lived at large delta.

    local ratio  0.134 to 0.417  (median 0.221)

Read the other way up: to separate the witness pair by one cent you must move
some bystander by 2.4 to 7.5 cents. The witnesses separate SLOWER than the
disturbance, everywhere in the local regime, at every ratio in scope. The linear
scaling is exact -- usable split is proportional to tau to four figures across a
50x sweep -- so this is a rate, not a coincidence of one tolerance.

THE TWO ANSWERS, WHICH ARE NOT IN TENSION:
  E2, exact and unbounded: NO delta returns the bystander spectrum to itself
  while splitting the witnesses. 2306 candidates over 8 ratios, folds and
  permutations included, zero returns. Exact isolation does not exist at any
  magnitude, and that IS the scoped theorem the ledger asked for.
  E3 plus the local ratio: approximate isolation is worse than useless locally
  (2.4x to 7.5x against you) and only becomes favourable once the detune is
  large enough to be a different ratio.

AMENDMENT 3 — THE LOCAL COST CLAIM IS RETRACTED. IT WAS RULER-DEPENDENT IN SIGN,
AND THE RULER I USED IS DOMINATED BY AN INAUDIBLE PARTIAL. Found by adversarial
review.

E2 IS UNAFFECTED AND STILL STANDS. It is exact, unbounded in magnitude, decided
in rational arithmetic over a complete candidate set, and involves NO RULER AT
ALL: no delta returns the bystander SPECTRUM to itself while splitting the
witness pair. 2306 candidates, folds and permutations included, zero returns.
Nothing below touches it.

WHAT IS RETRACTED is Amendment 2's gloss -- "separating the witness pair by one
cent costs 2.4x to 7.4x that much bystander movement" -- which was quoted
forward into the resynthesis cell, the decorrelation cell, the ledger and the
capability report.

The local ratio divided the witness split by the MAX bystander displacement in
CENTS. Three things are wrong with that, and each was invisible from inside the
cell:

  (a) THE MAX IS AN EXTREME-VALUE PICK OF WHATEVER IS NEAREST DC. In cents the
      displacement rate goes as 1/f, so the lowest-frequency moving partial
      dominates by construction. Every driver of the reported ratio sits at
      31-110 Hz with amplitude 1.5e-4 to 1.4e-3 -- at or barely above the 1e-4
      render floor, about -76 dB. The headline was set by a partial nobody can
      hear.

  (b) pitch_floor_hz WAS DECLARED AND NEVER SWEPT, and no arm guarded it; R1
      guards the delta grid only. Raising it moves the ratio monotonically and
      flips the conclusion.

  (c) THE SIGN REVERSES UNDER EVERY OTHER REASONABLE RULER:

          cents, unweighted max       median 0.317    0 of 12 ratios buy > cost
          Hz,    unweighted max       median 1.375    9 of 12
          cents, AMPLITUDE-WEIGHTED   median 1.160   11 of 12

      The third is the one that should have been used. Weighting each
      bystander's displacement by how loud it is IS what "disturbed the rest"
      means; an unweighted max over a set containing sub-floor partials answers
      a different question. Under it, ratio detune BUYS more than it costs at
      eleven of twelve ratios -- the opposite of what I published.

AND THE BAR ITSELF WAS INCOHERENT, which should have caught this before any
reviewer did. E3's `why` defends its reachable range in the Hz ruler -- "margin
> 1 is reachable whenever the witness split rate q exceeds the largest bystander
rate B" -- while the statistic it guards is computed in CENTS. Under the Hz
ruler the local ratio is exactly q/B, reproducing to three decimals. A bar whose
range defence and whose statistic use different rulers is the commensurability
failure this repo keeps a four-clause check for, sitting inside the guard
module's own call site.

WHAT REPLACES IT: all three rulers are computed and reported, none is privileged
in the verdict token, and the honest summary is that ratio detune's LOCAL
selectivity is a function of how the bystanders are weighted and is FAVOURABLE
under the weighting that tracks audibility. The case for the resynthesis
apparatus therefore rests on E2 -- exact isolation impossible at any magnitude --
and not on the local cost, which is what I had been leaning on.

WHAT THIS CELL DOES NOT CLAIM. Nothing here is about audibility. It is a
statement about what the FM synthesis path can express, under two operators, the
direct channel, sine carriers, at index I, over the ratios the horizon puts in
scope. Whether a listener would notice any of it is a different question with a
criterion in it, and this cell deliberately has no criterion.
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
from existence import summarise, PRESENCE                         # noqa: E402
from verdictlattice import (Arm, compose, PREMISE as PRE_ROLE,    # noqa: E402
                            EXISTENCE as EX_ROLE,
                            MECHANISM as MECH_ROLE,
                            RESOLUTION as RES_ROLE)
from phase3.partial_prediction import order_bound                 # noqa: E402

I_MUS = 0.9
B = order_bound(I_MUS)
A = 2 * B
F_C = 220.0
FLOORS = [1e-4, 1e-6]
PREREG_FLOOR = "1e-04"
LO, HI = 0.70, 1.40
# the practical scan window for E3, declared: alpha may not go non-positive,
# and two octaves either way is already far beyond any twin this arc has built.
SCAN_CENTS = 2400.0
SCAN_MIN_CENTS = 1e-3
SCAN_N = 4000
PITCH_FLOOR_HZ = 20.0
TAUS = [0.5, 1.0, 2.0, 5.0, 10.0, 25.0]
PREREG_TAU = 1.0

INSTRUMENT = Model("exact rational analysis of the two-operator partial lattice", [
    Param("render_floor", TESTED, sweep=FLOORS,
          why="the amplitude below which a partial is not synthesised decides "
              "WHICH partials are bystanders, so every arm here depends on it; "
              "1e-4 is the shipped value and is pre-registered as the answer"),
    Param("delta_scan_cents", DECLARED, value=SCAN_CENTS,
          why="E3 only. E2 is exact over a complete candidate set with NO "
              "magnitude bound, so the 'at any magnitude' claim rests there "
              "and not on this window"),
    Param("delta_scan_points", DECLARED, value=SCAN_N,
          why="grid density, audited by R1 -- doubling it must change neither "
              "the margin verdict NOR the usable split, or the answer is an "
              "artifact of the grid. The grid is LOGARITHMIC in |delta|: the "
              "first version was linear and its 1.2-cent step made every "
              "small-tolerance answer identically zero"),
    Param("pitch_floor_hz", DECLARED, value=PITCH_FLOOR_HZ,
          why="cents are undefined at f = 0, and this lattice really does put "
              "partials at DC (2,-4 at alpha=3/4; 3,-3 at 4/3). Rather than "
              "let those ratios divide by zero and score as passes, partials "
              "below this floor are excluded from the cents metric, COUNTED, "
              "and reported by absolute Hz displacement instead"),
    Param("tau_cents", TESTED, sweep=TAUS,
          why="the freeze tolerance. E3's headline is threshold-FREE (the "
              "margin), and tau only converts a margin into a usable split; "
              "swept because criterion-as-axis survived the framing death"),
    Param("I", DECLARED, value=I_MUS,
          why="the musical index this arc has used throughout; B and the "
              "horizon A = 2B follow from it"),
    Param("f_c", DECLARED, value=F_C,
          why="cents are ratios of frequencies, so every quantity reported "
              "here is f_c-invariant; it is carried only to print Hz"),
])


def index_set(floor):
    """Index vectors whose Bessel product clears the render floor."""
    out = []
    for n1 in range(-B, B + 1):
        for n2 in range(-B, B + 1):
            a = float(jv(n1, I_MUS)) * float(jv(n2, I_MUS))
            if abs(a) >= floor:
                out.append((n1, n2, a))
    return out


def arg_at(n1, n2, alpha):
    """The SIGNED argument 1 + n1 + n2*alpha, exact when alpha is a Fraction."""
    return 1 + n1 + n2 * alpha


def bins_of(idx, alpha):
    """Multiset of (|a|, summed amplitude) -- the spectrum, exactly."""
    d = {}
    for n1, n2, amp in idx:
        k = abs(arg_at(n1, n2, alpha))
        d[k] = d.get(k, 0.0) + amp
    return frozenset((k, round(v, 12)) for k, v in d.items())


def witnesses(p, q):
    """The horizon's sufficiency witness pair for alpha = p/q."""
    w1 = (-(-p // 2), -(q // 2))
    w2 = (-(p // 2), -(-q // 2))
    if max(abs(w1[0]), abs(w1[1]), abs(w2[0]), abs(w2[1])) > B:
        return None
    return w1, w2


# ---------------------------------------------------------------------------
# E2's exhaustive candidate machinery, used by the positive control FIRST.
# ---------------------------------------------------------------------------
def freeze_candidates(byst, alpha):
    """Every d != 0 at which the bystander spectrum COULD return to itself.

    Completeness: if the multiset is preserved then each moving bystander j
    lands on some bystander frequency |a_k|, so a_j + n2_j*d = +/- a_k. Ranging
    over all (j, k) therefore cannot miss a solution. Exact rationals.
    """
    cands = set()
    for n1j, n2j, _ in byst:
        if n2j == 0:
            continue
        aj = arg_at(n1j, n2j, alpha)
        for n1k, n2k, _ in byst:
            ak = arg_at(n1k, n2k, alpha)
            for s in (1, -1):
                d = Fraction(s * ak - aj, n2j)
                if d != 0:
                    cands.add(d)
    return sorted(cands)


def spectrum_returns(byst, alpha, d):
    return bins_of(byst, alpha) == bins_of(byst, alpha + d)


def witness_splits(w1, w2, alpha, d):
    return abs(arg_at(*w1, alpha + d)) != abs(arg_at(*w2, alpha + d))


# --- POSITIVE CONTROL: a lattice where a common freeze EXISTS by construction.
# bystanders all share (1 + n1)/n2 = 1, so every one of them reflects at the
# same d = -2*(1 + alpha). If the machinery cannot find that, it cannot find
# anything, and nothing below is worth printing.
CTRL_ALPHA = Fraction(5, 4)
CTRL_BYST = [(0, 1, 0.5), (1, 2, 0.25), (-2, -1, 0.5), (-3, -2, 0.25)]
CTRL_WANT = -2 * (1 + CTRL_ALPHA)
_cands = freeze_candidates(CTRL_BYST, CTRL_ALPHA)
_found = [d for d in _cands if spectrum_returns(CTRL_BYST, CTRL_ALPHA, d)]
CONTROL = dict(alpha=str(CTRL_ALPHA), n_candidates=len(_cands),
               expected=str(CTRL_WANT),
               found=[str(d) for d in _found],
               fired=bool(CTRL_WANT in _found))
print("positive control — a lattice built to HAVE a common reflection freeze")
print(f"  bystanders {CTRL_BYST}")
print(f"  candidates enumerated : {len(_cands)}")
print(f"  freezes found         : {[str(d) for d in _found]}")
print(f"  contains expected {CTRL_WANT}: {CONTROL['fired']}")
if not CONTROL["fired"]:
    print("\nABORT: the freeze detector did not fire on a lattice built to "
          "contain a freeze. No verdict is written — an arm that cannot fire "
          "is not evidence.")
    sys.exit(1)
print("  CONTROL PASSES — the detector can find a freeze when one exists.\n")


RATIOS = sorted([Fraction(p, q) for q in range(1, A + 1) for p in range(1, A + 1)
                 if gcd(p, q) == 1 and LO <= p / q <= HI and max(p, q) <= A
                 and Fraction(p, q) != 1], key=float)


def scan(byst, w1, w2, af, n):
    """Bystander max-shift and witness split, in cents, over the delta grid.

    Vectorised because the loop version is ~28M Python-level operations and a
    slow cell is a cell that gets run once.
    """
    half = np.geomspace(SCAN_MIN_CENTS, SCAN_CENTS, n // 2)
    ds = np.concatenate([-half[::-1], half])
    a2 = af * 2.0 ** (ds / 1200.0)
    mb = np.zeros_like(a2)
    n_unpitched, max_hz = 0, 0.0
    for n1, n2, _ in byst:
        if n2 == 0:
            continue
        f0 = F_C * abs(1 + n1 + n2 * af)
        f1 = F_C * np.abs(1 + n1 + n2 * a2)
        if f0 < PITCH_FLOOR_HZ:
            # UNPITCHED. A partial at or near DC has no cents displacement to
            # be within a JND of; it is reported in Hz and excluded from mb
            # rather than making the whole ratio unmeasurable via log(x/0).
            n_unpitched += 1
            max_hz = max(max_hz, float(np.max(np.abs(f1 - f0))))
            continue
        c = np.abs(1200.0 * np.log2(np.maximum(f1, 1e-12) / f0))
        mb = np.maximum(mb, c)
    fw1 = F_C * np.abs(1 + w1[0] + w1[1] * a2)
    fw2 = F_C * np.abs(1 + w2[0] + w2[1] * a2)
    with np.errstate(divide="ignore", invalid="ignore"):
        split = np.abs(1200.0 * np.log2(np.where(fw1 > 0, fw1, np.nan)
                                        / np.where(fw2 > 0, fw2, np.nan)))
    return mb, split, ds, n_unpitched, max_hz


def analyse(alpha, floor):
    p, q = alpha.numerator, alpha.denominator
    w = witnesses(p, q)
    if w is None:
        return None
    w1, w2 = w
    idx = index_set(floor)
    keys = {(n1, n2) for n1, n2, _ in idx}
    if w1 not in keys or w2 not in keys:
        return None
    byst = [(n1, n2, a) for n1, n2, a in idx if (n1, n2) not in (w1, w2)]
    moving = [b for b in byst if b[1] != 0]

    sep0 = abs(abs(arg_at(*w1, alpha)) - abs(arg_at(*w2, alpha)))

    # --- E2: exact, unbounded, permutations allowed
    cands = freeze_candidates(byst, alpha)
    frozen = [d for d in cands if spectrum_returns(byst, alpha, d)]
    isolating = [d for d in frozen if witness_splits(w1, w2, alpha, d)]
    pos = [d for d in isolating if alpha + d > 0]

    # --- E3: threshold-free margin over the declared window
    mb, split, ds, n_unp, unp_hz = scan(byst, w1, w2, float(alpha), SCAN_N)
    ok = (mb > 0) & np.isfinite(split)
    margin, best = 0.0, None
    if ok.any():
        m = np.where(ok, split / np.where(mb > 0, mb, 1.0), 0.0)
        j = int(np.argmax(m))
        margin, best = float(m[j]), float(ds[j])

    # usable split at each tau: the largest witness separation reachable while
    # every bystander stays within tau cents.
    usable = {}
    for tau in TAUS:
        sel = ok & (mb <= tau)
        usable[f"{tau:g}"] = float(split[sel].max()) if sel.any() else 0.0

    # POST-HOC, ADDED AFTER SEEING E3 MISS (Amendment 2). Linear-limit rate of
    # witness separation against largest bystander displacement. Not an arm.
    lin = usable[f"{PREREG_TAU:g}"] / PREREG_TAU

    # AMENDMENT 3: the same quantity under three rulers, because the sign of the
    # conclusion depends on the choice and the cents-max ruler is dominated by a
    # sub-floor partial near DC.
    dd = 1e-6
    af = float(alpha)      # the vectorised scan refactor removed the earlier one
    fw1 = F_C * abs(arg_at(*w1, af + dd))
    fw2 = F_C * abs(arg_at(*w2, af + dd))
    sc = abs(1200.0 * np.log2(fw1 / fw2))
    sh = abs(fw1 - fw2)
    mbc = mbh = num = den = 0.0
    for n1, n2, amp in byst:
        if n2 == 0:
            continue
        f0 = F_C * abs(arg_at(n1, n2, af))
        f1 = F_C * abs(arg_at(n1, n2, af + dd))
        mbh = max(mbh, abs(f1 - f0))
        if f0 >= PITCH_FLOOR_HZ:
            c = abs(1200.0 * np.log2(f1 / f0))
            mbc = max(mbc, c)
            num += (amp ** 2) * (c ** 2)
            den += amp ** 2
    awrms = (num / den) ** 0.5 if den > 0 else float("inf")
    rulers = dict(cents_max=(sc / mbc if mbc > 0 else None),
                  hz_max=(sh / mbh if mbh > 0 else None),
                  cents_amp_weighted=(sc / awrms if awrms > 0 else None))

    return dict(ratio=str(alpha), p=p, q=q,
                local_isolation_ratio=float(lin), rulers=rulers,
                local_cost_factor=(float(1.0 / lin) if lin > 0 else None),
                n_partials=len(idx), n_bystanders=len(byst),
                n_moving=len(moving), n_frozen_byst=len(byst) - len(moving),
                witness_sep_exact=str(sep0),
                n_unpitched_bystanders=n_unp,
                unpitched_max_hz_shift=unp_hz,
                n_freeze_candidates=len(cands),
                n_spectrum_returns=len(frozen),
                n_isolating=len(isolating),
                n_isolating_alpha_positive=len(pos),
                isolating_deltas=[str(d) for d in isolating[:8]],
                margin=float(margin), margin_at_cents=best,
                usable_split_cents=usable)


results = {}
for fl in FLOORS:
    rows = [r for r in (analyse(a, fl) for a in RATIOS) if r]
    results[f"{fl:.0e}"] = rows

ROWS = results[PREREG_FLOOR]
print(INSTRUMENT.report())
print(f"\nI = {I_MUS}, B = {B}, horizon A = {A}; {len(ROWS)} ratios in scope at "
      f"the pre-registered floor {PREREG_FLOOR}\n")
print(f"{'ratio':>7s} {'q':>3s} {'parts':>6s} {'byst':>5s} {'moving':>7s} "
      f"{'sep':>5s} {'cands':>7s} {'returns':>8s} {'isolating':>10s} "
      f"{'unpit':>6s} {'margin':>8s} {'split@1c':>9s}")
for r in ROWS:
    print(f"{r['ratio']:>7s} {r['q']:>3d} {r['n_partials']:>6d} "
          f"{r['n_bystanders']:>5d} {r['n_moving']:>7d} "
          f"{r['witness_sep_exact']:>5s} {r['n_freeze_candidates']:>7d} "
          f"{r['n_spectrum_returns']:>8d} {r['n_isolating']:>10d} "
          f"{r['n_unpitched_bystanders']:>6d} "
          f"{r['margin']:>8.4f} {r['usable_split_cents']['1']:>9.3f}")

# --- the distribution, not a count (presence/share rule)
margins = [r["margin"] for r in ROWS]
moving_frac = [r["n_moving"] / max(r["n_bystanders"], 1) for r in ROWS]
qs = np.percentile(margins, [0, 25, 50, 75, 100])
print(f"\nisolation margin over {len(margins)} ratios — "
      f"min {qs[0]:.4f}  q1 {qs[1]:.4f}  median {qs[2]:.4f}  "
      f"q3 {qs[3]:.4f}  max {qs[4]:.4f}")
print(f"moving-bystander fraction — min {min(moving_frac):.3f}  "
      f"median {float(np.median(moving_frac)):.3f}  max {max(moving_frac):.3f}")
# no `acknowledge`: these are counts of partials, not shares, so the
# share-detector should stay LIVE rather than be pre-emptively silenced.
pres = summarise("bystanders that a detune moves", [r["n_moving"] for r in ROWS],
                 PRESENCE)
print(f"presence check: {pres}")
unp = [r["n_unpitched_bystanders"] for r in ROWS]
print(f"unpitched bystanders (below {PITCH_FLOOR_HZ:.0f} Hz, excluded from the "
      f"cents metric and reported in Hz): total {sum(unp)} across "
      f"{sum(1 for u in unp if u)} ratios; "
      f"largest Hz displacement {max(r['unpitched_max_hz_shift'] for r in ROWS):.3f}")

# --- R1: halve the grid and re-ask E3
def margin_at(alpha, floor, n):
    idx = index_set(floor)
    w1, w2 = witnesses(alpha.numerator, alpha.denominator)
    byst = [(a, b, c) for a, b, c in idx if (a, b) not in (w1, w2)]
    mb, split, _, _, _ = scan(byst, w1, w2, float(alpha), n)
    ok = (mb > 0) & np.isfinite(split)
    margin = float(np.max(split[ok] / mb[ok])) if ok.any() else None
    sel = ok & (mb <= PREREG_TAU)
    return margin, (float(split[sel].max()) if sel.any() else 0.0)


fine = {r["ratio"]: margin_at(Fraction(r["ratio"]), 1e-4, 2 * SCAN_N)
        for r in ROWS}
# R1 NOW GUARDS BOTH HALVES. The first version re-checked only the margin
# verdict and passed while the tau column was pure grid artifact.
flips = sum(1 for r in ROWS
            if (r["margin"] > 1.0) != ((fine[r["ratio"]][0] or 0.0) > 1.0)
            or abs(r["usable_split_cents"][f"{PREREG_TAU:g}"]
                   - fine[r["ratio"]][1]) > 0.05 * max(
                       r["usable_split_cents"][f"{PREREG_TAU:g}"], 1e-9))

# --- M1: is the shift the lattice-fixed direction?
worst, n_corners = 0.0, 0
for r in ROWS:
    alpha = Fraction(r["ratio"])
    af = float(alpha)
    h = 1e-7
    for n1, n2, _ in index_set(1e-4):
        if n2 == 0:
            continue
        # AT A CORNER (a = 0) the derivative does not exist and the claim is
        # not defined, so the corner is COUNTED rather than scored. Silently
        # skipping it would be the inert-arm defect; counting it keeps the
        # exception visible in the artifact.
        if arg_at(n1, n2, alpha) == 0:
            n_corners += 1
            continue
        a0 = arg_at(n1, n2, af)
        num = (F_C * abs(arg_at(n1, n2, af + h))
               - F_C * abs(arg_at(n1, n2, af - h))) / (2 * h)
        pred = F_C * (1.0 if a0 > 0 else -1.0) * n2
        worst = max(worst, abs(num - pred) / max(abs(pred), 1e-30))

# --- arms
n = len(ROWS)
e1 = sum(1 for r in ROWS if r["n_moving"] == 0)
e2 = sum(1 for r in ROWS if r["n_isolating"] > 0)
e3 = sum(1 for r in ROWS if r["margin"] > 1.0)

P1 = Bar("ratios whose witness pair does not coincide exactly", 0,
         direction="le", floor=0, ceiling=n,
         why=f"a count over the {n} ratios in scope; exact rational arithmetic, "
             "so the floor 0 is attainable and the ceiling is every ratio")
E1 = Bar("ratios with no alpha-dependent bystander", 0, direction="le",
         floor=0, ceiling=n,
         why=f"a count over the {n} ratios; a ratio with none would be isolated "
             "by any detune whatsoever")
E2 = Bar("ratios admitting an exact isolating detune", 0, direction="le",
         floor=0, ceiling=n,
         why=f"a count over the {n} ratios, from the COMPLETE candidate set at "
             "unbounded magnitude — the ceiling is every ratio and the floor is "
             "attainable because a freeze is a codimension-1 coincidence")
E3 = Bar("ratios with isolation margin above 1", 0, direction="le",
         floor=0, ceiling=n,
         why=f"a count over the {n} ratios; margin > 1 is reachable in principle "
             "whenever the witness split rate q exceeds the largest bystander "
             f"rate B = {B}, which happens for q > {B} in this scope")
print(f"lattice corners (a = 0 exactly, derivative undefined, excluded from M1 "
      f"and counted): {n_corners}")

M1 = Bar("max relative deviation from the lattice-fixed direction, off corners", 1e-6,
         direction="le", floor=0.0, ceiling=1.0,
         why="a relative error on a numerical derivative; 0 is attainable and "
             "O(1) deviation is what a wrong lattice model would give")
R1 = Bar("ratios whose margin OR usable split moves when the grid is doubled", 0,
         direction="le", floor=0, ceiling=n,
         why=f"a count over the {n} ratios re-scanned at double density; it "
             "guards the tau column as well as the margin verdict, because "
             "scoped to the margin alone it passed over a tau column that was "
             "entirely grid artifact")

wsep = sum(1 for r in ROWS if r["witness_sep_exact"] != "0")
sP, s1, s2, s3 = P1.score(wsep), E1.score(e1), E2.score(e2), E3.score(e3)
sM, sR = M1.score(worst), R1.score(flips)


print()
for b, v in ((P1, wsep), (E1, e1), (E2, e2), (E3, e3)):
    print("  " + b.line(v, "{:.0f}"))
print("  " + M1.line(worst, "{:.3e}"))
print("  " + R1.line(flips, "{:.0f}"))

# SWEPT ON THE SCALE-FREE QUANTITY. The raw usable split is PROPORTIONAL to tau
# by construction, so sweeping it makes swept() report unstable=True on every
# possible dataset -- a flag that cannot be absent is a flag that says nothing,
# which is the inert-arm defect wearing a different hat. Swept per unit
# tolerance instead: constant IFF the small-delta regime is linear, and a swing
# here would be a real finding about nonlinearity rather than about tau.
RAW = {k: float(np.median([r["usable_split_cents"][k] for r in ROWS]))
       for k in (f"{t:g}" for t in TAUS)}
SPLIT = swept("usable witness split PER UNIT freeze tolerance",
              {k: RAW[k] / t for k, t in zip(RAW, TAUS)},
              prereg=f"{PREREG_TAU:g}")
print(f"\nusable split, median over ratios, by freeze tolerance:")
for (k, v), t in zip(RAW.items(), TAUS):
    print(f"    tau = {k:>5s} cents   ->  {v:8.3f} cents of separation "
          f"({v / t:.4f} per unit tolerance)")
print(f"  pre-registered tau = {SPLIT['prereg']}: {SPLIT['value']:.4f} "
      f"cents per cent, swing {SPLIT['swing']:.4f}"
      + ("   [UNSTABLE — the local regime is NOT linear]" if SPLIT["unstable"]
         else "   [stable: the linear regime holds across the 50x sweep]"))

FLOORSENS = {k: sum(1 for r in v if r["margin"] > 1.0)
             for k, v in results.items()}
print(f"floor sensitivity of E3 (count of margin>1): {FLOORSENS}")

lr = [r["local_isolation_ratio"] for r in ROWS]
cf = [r["local_cost_factor"] for r in ROWS]
mac = [r["margin_at_cents"] for r in ROWS]
print(f"\nPOST-HOC (Amendment 2), not an arm — the LOCAL regime:")
print(f"  margin is achieved at {min(mac):.0f} to {max(mac):.0f} cents of detune "
      f"— 8 to 15 semitones, i.e. a different ratio, not a detune")
print(f"  local isolation ratio  min {min(lr):.4f}  median "
      f"{float(np.median(lr)):.4f}  max {max(lr):.4f}")
print(f"  read as cost under the CENTS-MAX ruler only: "
      f"{min(cf):.1f}x to {max(cf):.1f}x -- RETRACTED, see below")
print("\nAMENDMENT 3 — THE SAME QUANTITY UNDER THREE RULERS. The sign of the "
      "conclusion\n  depends on the choice, so none is privileged and the "
      "Amendment 2 gloss is RETRACTED:")
for key, label in (("cents_max", "cents, unweighted max"),
                   ("hz_max", "Hz, unweighted max"),
                   ("cents_amp_weighted", "cents, AMPLITUDE-WEIGHTED")):
    vals = [r["rulers"][key] for r in ROWS if r["rulers"][key] is not None]
    print(f"    {label:<27s} median {float(np.median(vals)):.3f}   "
          f"{sum(1 for x in vals if x > 1)} of {len(vals)} ratios BUY > COST")
print("  The amplitude-weighted ruler tracks audibility, and under it ratio "
      "detune\n  BUYS more than it costs almost everywhere. E2 is untouched: "
      "exact,\n  unbounded, and ruler-free.")

arms = [Arm.from_bar(sP, PRE_ROLE,
                     claim="the witness pair coincides exactly, so there is "
                           "something to split"),
        Arm.from_bar(s1, EX_ROLE,
                     claim="every ratio has bystanders a detune must move"),
        Arm.from_bar(s2, EX_ROLE,
                     claim="no exact isolating detune exists at any magnitude, "
                           "folds and permutations included"),
        Arm.from_bar(s3, EX_ROLE,
                     claim="no detune separates the pair by more than it "
                           "disturbs everything else"),
        Arm.from_bar(sM, MECH_ROLE,
                     claim="because the shift direction is fixed by the "
                           "lattice and a detune has one degree of freedom"),
        Arm.from_bar(sR, RES_ROLE,
                     claim="the margin verdict is not a grid artifact")]
v = compose(arms, holds="RATIO_DETUNE_CANNOT_ISOLATE",
            fails="ISOLATING_DETUNE_EXISTS")
print(f"\nVERDICT: {v['citation']}")

with redpath("ratio x floor analyses", expect_min=12) as rp:
    rp.observed(sum(len(x) for x in results.values()))

json.dump(dict(I=I_MUS, B=B, A=A, f_c=F_C, floors=FLOORS,
               prereg_floor=PREREG_FLOOR, scan_cents=SCAN_CENTS,
               scan_points=SCAN_N, taus=TAUS,
               instrument=INSTRUMENT.seal(),
               positive_control=CONTROL,
               rows=ROWS, by_floor=results,
               margin_quantiles=dict(zip(["min", "q1", "median", "q3", "max"],
                                         [float(x) for x in qs])),
               presence=pres, usable_split=SPLIT, usable_split_raw=RAW,
               floor_sensitivity=FLOORSENS,
               local_isolation=dict(
                   posthoc=True,
                   added_after="E3 missed; the margin was found to live at "
                               "814-1499 cents, so a local statistic was added "
                               "and is labelled rather than substituted",
                   ratio_min=float(min(lr)), ratio_median=float(np.median(lr)),
                   ratio_max=float(max(lr)),
                   cost_min=float(min(cf)), cost_max=float(max(cf)),
                   margin_at_cents_min=float(min(mac)),
                   margin_at_cents_max=float(max(mac))),
               grid_flips=flips, direction_max_rel_dev=float(worst),
               n_lattice_corners=n_corners, pitch_floor_hz=PITCH_FLOOR_HZ,
               scan_min_cents=SCAN_MIN_CENTS,
               bars={s["name"]: s for s in (sP, s1, s2, s3, sM, sR)},
               verdict=v["head"],
               # NO NUMBER IN THE TOKEN. The first draft read
               # ..._COSTS_2.4x_TO_7.5x while the measured max was 7.4x -- a
               # verdict label that disagrees with its own artifact in the
               # third significant figure, which is how a token outlives the
               # measurement it names. The range lives in the data.
               verdict_amended="EXACT_ISOLATION_IMPOSSIBLE_"
                               "LOCAL_COST_CLAIM_RETRACTED_RULER_DEPENDENT",
               amendment="E3's sealed prediction was wrong and the head is "
                         "read off the arm as sealed. What the miss locates: "
                         "the margin lives at 814-1499 cents, a different "
                         "ratio rather than a detune, while in the local "
                         "regime separating the witness pair by one cent "
                         "costs 2.4x to 7.5x that much bystander movement "
                         "[THIS CLAUSE RETRACTED BY AMENDMENT 3: ruler-"
                         "dependent in sign; see verdict_amended and the "
                         "per-ratio `rulers` field]. "
                         "E2 is untouched and is the theorem: no delta of any "
                         "magnitude returns the bystander spectrum to itself "
                         "while splitting the witnesses, folds and "
                         "permutations included, over 2306 exact candidates.",
               composed=v),
          open(f"{HERE}/brocot_detune_impossibility.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_detune_impossibility.json")
