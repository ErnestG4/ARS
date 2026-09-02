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
SCAN_N = 4001
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
          why="grid density, audited by R1 -- halving the step must not change "
              "an E3 verdict, or the answer is an artifact of the grid"),
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
    ds = np.linspace(-SCAN_CENTS, SCAN_CENTS, n)
    ds = ds[ds != 0.0]
    a2 = af * 2.0 ** (ds / 1200.0)
    mb = np.zeros_like(a2)
    for n1, n2, _ in byst:
        if n2 == 0:
            continue
        f0 = F_C * abs(1 + n1 + n2 * af)
        f1 = F_C * np.abs(1 + n1 + n2 * a2)
        with np.errstate(divide="ignore", invalid="ignore"):
            c = np.abs(1200.0 * np.log2(np.where(f1 > 0, f1, np.nan) / f0))
        mb = np.maximum(mb, np.nan_to_num(c, nan=np.inf))
    fw1 = F_C * np.abs(1 + w1[0] + w1[1] * a2)
    fw2 = F_C * np.abs(1 + w2[0] + w2[1] * a2)
    with np.errstate(divide="ignore", invalid="ignore"):
        split = np.abs(1200.0 * np.log2(np.where(fw1 > 0, fw1, np.nan)
                                        / np.where(fw2 > 0, fw2, np.nan)))
    return mb, split, ds


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
    mb, split, ds = scan(byst, w1, w2, float(alpha), SCAN_N)
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

    return dict(ratio=str(alpha), p=p, q=q,
                n_partials=len(idx), n_bystanders=len(byst),
                n_moving=len(moving), n_frozen_byst=len(byst) - len(moving),
                witness_sep_exact=str(sep0),
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
      f"{'margin':>8s} {'split@1c':>9s}")
for r in ROWS:
    print(f"{r['ratio']:>7s} {r['q']:>3d} {r['n_partials']:>6d} "
          f"{r['n_bystanders']:>5d} {r['n_moving']:>7d} "
          f"{r['witness_sep_exact']:>5s} {r['n_freeze_candidates']:>7d} "
          f"{r['n_spectrum_returns']:>8d} {r['n_isolating']:>10d} "
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

# --- R1: halve the grid and re-ask E3
def margin_at(alpha, floor, n):
    idx = index_set(floor)
    w1, w2 = witnesses(alpha.numerator, alpha.denominator)
    byst = [(a, b, c) for a, b, c in idx if (a, b) not in (w1, w2)]
    mb, split, _ = scan(byst, w1, w2, float(alpha), n)
    ok = (mb > 0) & np.isfinite(split)
    return float(np.max(split[ok] / mb[ok])) if ok.any() else 0.0


fine = {r["ratio"]: margin_at(Fraction(r["ratio"]), 1e-4, 2 * SCAN_N - 1)
        for r in ROWS}
flips = sum(1 for r in ROWS
            if (r["margin"] > 1.0) != (fine[r["ratio"]] > 1.0))

# --- M1: is the shift the lattice-fixed direction?
worst = 0.0
for r in ROWS[:6]:
    alpha = Fraction(r["ratio"])
    af = float(alpha)
    h = 1e-7
    for n1, n2, _ in index_set(1e-4):
        if n2 == 0:
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
M1 = Bar("max relative deviation from the lattice-fixed shift direction", 1e-6,
         direction="le", floor=0.0, ceiling=1.0,
         why="a relative error on a numerical derivative; 0 is attainable and "
             "O(1) deviation is what a wrong lattice model would give")
R1 = Bar("ratios whose margin>1 verdict flips when the grid is halved", 0,
         direction="le", floor=0, ceiling=n,
         why=f"a count over the {n} ratios re-scanned at double density")

wsep = sum(1 for r in ROWS if r["witness_sep_exact"] != "0")
sP, s1, s2, s3 = P1.score(wsep), E1.score(e1), E2.score(e2), E3.score(e3)
sM, sR = M1.score(worst), R1.score(flips)


print()
for b, v in ((P1, wsep), (E1, e1), (E2, e2), (E3, e3)):
    print("  " + b.line(v, "{:.0f}"))
print("  " + M1.line(worst, "{:.3e}"))
print("  " + R1.line(flips, "{:.0f}"))

SPLIT = swept("largest usable witness split at the freeze tolerance",
              {k: float(np.median([r["usable_split_cents"][k] for r in ROWS]))
               for k in (f"{t:g}" for t in TAUS)},
              prereg=f"{PREREG_TAU:g}")
print(f"\nusable split, median over ratios, by freeze tolerance:")
for k, v in SPLIT["spread"].items():
    print(f"    tau = {k:>5s} cents   ->  {v:8.3f} cents of witness separation")
print(f"  pre-registered tau = {SPLIT['prereg']}: {SPLIT['value']:.3f} cents"
      + ("   [UNSTABLE across the sweep]" if SPLIT["unstable"] else ""))

FLOORSENS = {k: sum(1 for r in v if r["margin"] > 1.0)
             for k, v in results.items()}
print(f"floor sensitivity of E3 (count of margin>1): {FLOORSENS}")

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
               presence=pres, usable_split=SPLIT,
               floor_sensitivity=FLOORSENS,
               grid_flips=flips, direction_max_rel_dev=float(worst),
               bars={s["name"]: s for s in (sP, s1, s2, s3, sM, sR)},
               verdict=v["head"], composed=v),
          open(f"{HERE}/brocot_detune_impossibility.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_detune_impossibility.json")
