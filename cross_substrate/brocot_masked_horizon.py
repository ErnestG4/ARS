"""STAGE A: the audible horizon from masking, not from a chosen dB floor.

COMMITTED GENERATOR of cross_substrate/brocot_masked_horizon.json.
Predictions sealed here, before any output exists.

WHY THIS EXISTS, AND WHAT IT REPLACES
---------------------------------------
`brocot_audible_horizon` asked whether the eps = 1e-3 horizon is audible and
answered with a floor I picked: 3 regions of 13 at -40 dB, 5 at -60 dB. Two
problems, both recorded rather than buried.

  1. THE FLOOR WAS A GUESS, and the cell's own E4 arm proved it matters: the
     count swings 40% between -40 and -60 dB. A classification resting on a
     number nobody derived is a classification resting on a convention.
  2. THAT CELL'S SEAL WAS VACUOUS. `exposure_audit` records it as the single
     refusal in the exposure window: both arms it designated EXISTENCE were
     inert -- a fraction bounded by 1.0 against a ceiling of 1.0, and a count
     bounded by 13 against a ceiling of 13, off by one from the claim it meant
     to make. As sealed it could not have failed to find a shrinkage.

So this cell derives the floor instead of choosing it, and every arm below is
edge-probed at construction: each bar's threshold is strictly inside its
declared range, so each can be both met and missed by reachable data.

THE CRITERION, DERIVED
----------------------
A partial is audible in a dense spectrum when it stands above the masking its
NEIGHBOURS produce inside the same auditory filter. Using the Glasberg-Moore
ERB width already in this toolchain, w(f) = 24.7*(4.37*f/1000 + 1), and Gaussian
spreading on the ERB scale, the masker excitation at partial k is

    E_k = sqrt( sum over j != k of a_j^2 * exp(-0.5 * ((f_k - f_j)/w(f_j))^2) )

and the partial is audible when 20*log10(a_k / E_k) exceeds a margin. The margin
is the only free parameter left, it has a psychoacoustic meaning (signal-to-
masker ratio inside one filter), and M2 tests whether the answer survives moving
it -- which is the test the dB floor FAILED.

A coincidence counts as audible when BOTH of its witness partials are audible.
Both, because a coincidence is two partials landing together: one audible
partial arriving where nothing else is does not fuse with anything.

SCOPE, stated: this is relative masking only. No absolute threshold in quiet, no
temporal integration, no binaural effects. It answers "would this partial be
swamped by its own spectrum", which is the dominant term for a dense FM spectrum
at moderate level, and not "would a listener report it" -- that is Stage B, the
2AFC detune-twin test, which needs listeners and is queued separately.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — all three edge-probed; none can be met by every value   ║
║                                                                              ║
║ M1  MASKING IS MORE RESTRICTIVE THAN eps — at I = 0.9 and a 0 dB margin,     ║
║     at most 12 of the 13 below-horizon ratios have an audible coincidence.   ║
║     Strictly fewer than all: the bar sits inside [0, 13], so a count of 13   ║
║     misses it.                                                              ║
║ M2  AND IT IS MORE STABLE THAN A CHOSEN FLOOR — moving the margin by 6 dB    ║
║     changes the count by at most 25%. The -40/-60 dB pair moved it 40%, so   ║
║     this is the arm on which "derived beats chosen" actually rests. If it    ║
║     misses, masking is just another convention and should be reported as    ║
║     one.                                                                    ║
║ M3  IT IS NOT THE CRUDE FLOOR IN DISGUISE — the audible count at 0 dB        ║
║     margin is at least 4, i.e. strictly more than the 3 the -40 dB floor     ║
║     gave. If the two agree exactly, the masking model is adding nothing and  ║
║     the honest report is that the crude floor was already right.            ║
║                                                                              ║
║ M2 IS THE CELL. M1 can hold trivially if masking is severe and M3 can hold   ║
║ by luck; M2 is the claim that this criterion is worth preferring.            ║
╚══════════════════════════════════════════════════════════════════════════════╝

AMENDMENT 1 — THE FREE PARAMETER I DID NOT SEAL AGAINST.

M2 tested robustness to the MARGIN and got 0.0% change over 12 dB, which is a
real improvement on the chosen floor's 40%. But the margin is not the only free
parameter: the Gaussian spreading uses sigma = ERB, and a real auditory filter
is NARROWER than that -- ERB is the equivalent rectangular bandwidth, so a
Gaussian with sigma = ERB over-masks. Filter width is the more consequential
knob and nothing sealed here tested it. Measured after the fact:

    sigma        I=0.9  I=1.5  I=2.0  I=3.0
    ERB              1      1      0      0
    ERB/2            1      1      1      2
    ERB/2.5          1      1      2      3
    ERB/4            2      3      4      6

AT THE INSTRUMENT'S OWN INDEX THE RESULT IS ROBUST: 1 to 2 audible coincidences
across a fourfold change in filter width, and 0% change across 12 dB of margin.
AT HIGHER INDICES IT IS NOT: at I = 3.0 the count runs 0 to 6 over the same
range, so any count quoted for I >= 2 must carry its filter width. That is the
same discipline the dB floor got, applied to the parameter that turned out to
matter more.

WHAT THIS DOES AND DOES NOT TOUCH -- stated because the headline invites
overreading.

  IT BOUNDS: the audibility of EXACT COINCIDENCE. At I = 0.9, under relative
  masking, essentially only the unison coincidence clears threshold. The
  coincidence horizon as a PERCEPTUAL object nearly collapses to 1/1.

  IT DOES NOT TOUCH: the theorem, which is arithmetic; the parent taxonomy,
  which is about NEAR-coincidence; or the separation coordinate, which is a
  BEAT -- a dynamic amplitude modulation at gap*f_c Hz, not a static partial
  competing for an auditory filter. `brocot_beat_target` records exactly this
  asymmetry: a 3 Hz beat lives in a regime static masking has no jurisdiction
  over. The structural field organises the space; what a player hears moving
  through it is the beat, not the merge.
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
from reachable import Bar, edge_probe                             # noqa: E402
from verdictlattice import (Arm, compose, EXISTENCE as EX_ROLE,   # noqa: E402
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from phase3.partial_prediction import order_bound                 # noqa: E402

I_LIST = [0.9, 1.5, 2.0, 3.0]
MARGINS = [-6.0, 0.0, 6.0]
F_C = 220.0
LO, HI = Fraction(7, 10), Fraction(7, 5)
PRIMARY_I, PRIMARY_MARGIN = 0.9, 0.0


def erb_w(f):
    return 24.7 * (4.37 * f / 1000.0 + 1.0)


def lattice(alpha, I, B):
    """Product-lattice partials: (freq, amplitude), folded to positive freqs."""
    out = {}
    for n1 in range(-B, B + 1):
        for n2 in range(-B, B + 1):
            a = float(jv(n1, I)) * float(jv(n2, I))
            if a == 0.0:
                continue
            nu = 1.0 + n1 + n2 * float(alpha)
            f = abs(nu) * F_C
            if f < 20.0 or f > 16000.0:
                continue
            out[round(f, 6)] = out.get(round(f, 6), 0.0) + abs(a)
    return np.array(sorted(out)), np.array([out[k] for k in sorted(out)])


def audible(fk, ak, f, a, margin_db, width_scale=1.0):
    """Is the partial at fk above the masking its neighbours produce there?"""
    other = f != fk
    if not other.any():
        return True
    e = np.sqrt(np.sum((a[other] ** 2)
                       * np.exp(-0.5 * ((fk - f[other])
                                        / (erb_w(f[other]) * width_scale)) ** 2)))
    if e <= 0:
        return True
    return 20.0 * np.log10(ak / e) > margin_db


def witness_audible(alpha, I, B, margin_db, width_scale=1.0):
    p, q = alpha.numerator, alpha.denominator
    n1, n1p = -(-p // 2), -(p // 2)
    n2, n2p = -(q // 2), -(-q // 2)
    if max(abs(n1), abs(n1p)) > B or max(abs(n2), abs(n2p)) > B:
        return None
    f, a = lattice(alpha, I, B)
    ok = True
    for (x, y) in ((n1, n2), (n1p, n2p)):
        amp = abs(float(jv(x, I)) * float(jv(y, I)))
        nu = abs(1.0 + x + y * float(alpha)) * F_C
        idx = np.argmin(np.abs(f - nu))
        if not audible(f[idx], amp, f, a, margin_db, width_scale):
            ok = False
    return ok


per = {}
for I in I_LIST:
    B = order_bound(I)
    A = 2 * B
    ratios = sorted({Fraction(p, q) for q in range(1, A + 1)
                     for p in range(1, A + 1)
                     if gcd(p, q) == 1 and LO <= Fraction(p, q) <= HI
                     and max(p, q) <= A}, key=float)
    per[I] = dict(B=B, A=A, n=len(ratios),
                  counts={m: sum(bool(witness_audible(f, I, B, m))
                                 for f in ratios) for m in MARGINS},
                  audible_at_primary=[str(f) for f in ratios
                                      if witness_audible(f, I, B, PRIMARY_MARGIN)])

n0 = per[PRIMARY_I]["n"]
c0 = per[PRIMARY_I]["counts"][PRIMARY_MARGIN]
c_lo = per[PRIMARY_I]["counts"][-6.0]
c_hi = per[PRIMARY_I]["counts"][6.0]
m1 = c0
m2 = abs(c_hi - c_lo) / max(c_lo, 1)
m3 = c0

M1 = Bar("audible ratios at 0 dB margin", n0 - 1, direction="le",
         floor=0, ceiling=n0,
         why=f"a count of the {n0} below-horizon ratios at I = {PRIMARY_I}: "
             f"0 to {n0}, and the bar sits strictly inside")
M2 = Bar("relative change over a 12 dB margin swing", 0.25, direction="le",
         floor=0.0, ceiling=float(n0),
         why=f"a relative change against a count of at least 1, bounded above "
             f"by {n0}")
M3 = Bar("audible ratios at 0 dB margin, vs the crude floor's 3", 4,
         floor=0, ceiling=n0,
         why=f"the same count, 0 to {n0}, with the bar strictly inside")
s1, s2, s3 = M1.score(m1), M2.score(m2), M3.score(m3)

# NO EDGE PROBE ON THE MARGIN. It was written here and it RAISED, correctly:
# the margin range is a SWEEP, not a declared domain. Nothing is claimed to
# change at -6 or +6 dB; they are sampling points. The probe belongs on domains
# whose edge is load-bearing, and misapplying it within an hour of writing the
# rule is recorded in reachable.py rather than quietly deleted. The margin's
# stability is what M2 measures, which is the right instrument for it.

print(f"masked-threshold census, f_c = {F_C:.0f} Hz, Glasberg-Moore ERB\n")
print(f"{'I':>5s} {'B':>3s} {'A':>3s} {'n':>4s} " +
      "".join(f"{'m=' + str(int(m)):>8s}" for m in MARGINS))
for I in I_LIST:
    d = per[I]
    print(f"{I:>5.1f} {d['B']:>3d} {d['A']:>3d} {d['n']:>4d} " +
          "".join(f"{d['counts'][m]:>8d}" for m in MARGINS))
print("\n   count = below-horizon ratios whose BOTH witness partials clear "
      "masking at that margin")
print(f"\nI = {PRIMARY_I}, margin {PRIMARY_MARGIN:+.0f} dB — audible: "
      f"{', '.join(per[PRIMARY_I]['audible_at_primary']) or 'none'}")
print()
for b, v, f in ((M1, m1, "{:.0f}"), (M2, m2, "{:.1%}"), (M3, m3, "{:.0f}")):
    print("  " + b.line(v, f))
print("\n  (no edge probe on the margin: a sweep range is not a declared "
      "domain — see reachable.edge_probe)")
print("\n  FILTER-WIDTH SENSITIVITY (amendment 1, measured not sealed):")
print(f"  {'sigma':>9s} " + "".join(f"{'I=' + str(I):>7s}" for I in I_LIST))
for lab, sc in (("ERB", 1.0), ("ERB/2", 0.5), ("ERB/2.5", 0.4), ("ERB/4", 0.25)):
    row = []
    for I in I_LIST:
        B = order_bound(I)
        A = 2 * B
        rs = sorted({Fraction(p, q) for q in range(1, A + 1)
                     for p in range(1, A + 1)
                     if gcd(p, q) == 1 and LO <= Fraction(p, q) <= HI
                     and max(p, q) <= A}, key=float)
        row.append(sum(bool(witness_audible(f, I, B, PRIMARY_MARGIN, sc))
                       for f in rs))
    print(f"  {lab:>9s} " + "".join(f"{c:>7d}" for c in row))
print("  robust at I = 0.9 (1-2 across a 4x width change); NOT at I >= 2")

v = compose([Arm.from_bar(s1, EX_ROLE,
                          claim="masking excludes at least one ratio the eps "
                                "horizon admits"),
             Arm.from_bar(s2, MECH_ROLE,
                          claim="the derived criterion is stabler than the "
                                "chosen dB floor, which swung 40%"),
             Arm.from_bar(s3, RES_ROLE,
                          claim="it is not the -40 dB floor under another name")],
            holds="MASKING_GIVES_A_DERIVED_HORIZON",
            fails="MASKING_ADDS_NOTHING_OVER_A_CHOSEN_FLOOR")
print(f"\nVERDICT: {v['citation']}")

with redpath("below-horizon ratios masked-tested", expect_min=60) as rp:
    rp.observed(sum(d["n"] for d in per.values()) * len(MARGINS))

json.dump(dict(I_list=I_LIST, margins=MARGINS, f_c=F_C,
               primary_I=PRIMARY_I, primary_margin=PRIMARY_MARGIN,
               per_I={str(k): dict(B=d["B"], A=d["A"], n=d["n"],
                                   counts={str(m): c for m, c in d["counts"].items()},
                                   audible=d["audible_at_primary"])
                      for k, d in per.items()},
               bars={s["name"]: s for s in (s1, s2, s3)},
               scope="relative masking only: no absolute threshold in quiet, no "
                     "temporal integration, no binaural effects. Gaussian "
                     "sigma = ERB over-masks; see amendment 1's width table.",
               width_sensitivity={lab: {str(I): sum(
                   bool(witness_audible(f, I, order_bound(I), PRIMARY_MARGIN, sc))
                   for f in sorted({Fraction(p, q)
                                    for q in range(1, 2 * order_bound(I) + 1)
                                    for p in range(1, 2 * order_bound(I) + 1)
                                    if gcd(p, q) == 1
                                    and LO <= Fraction(p, q) <= HI
                                    and max(p, q) <= 2 * order_bound(I)},
                                   key=float)) for I in I_LIST}
                   for lab, sc in (("ERB", 1.0), ("ERB/2", 0.5),
                                   ("ERB/2.5", 0.4), ("ERB/4", 0.25))},
               verdict=v["head"], composed=v),
          open(f"{HERE}/brocot_masked_horizon.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_masked_horizon.json")
