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


def audible(fk, ak, f, a, margin_db):
    """Is the partial at fk above the masking its neighbours produce there?"""
    other = f != fk
    if not other.any():
        return True
    e = np.sqrt(np.sum((a[other] ** 2)
                       * np.exp(-0.5 * ((fk - f[other]) / erb_w(f[other])) ** 2)))
    if e <= 0:
        return True
    return 20.0 * np.log10(ak / e) > margin_db


def witness_audible(alpha, I, B, margin_db):
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
        if not audible(f[idx], amp, f, a, margin_db):
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

# the declared domain gets its own edge probe, per the construction-time rule
probe = edge_probe(f"margin in [{MARGINS[0]}, {MARGINS[-1]}] dB",
                   MARGINS[0], MARGINS[-1],
                   lambda m: per[PRIMARY_I]["counts"].get(
                       m, sum(bool(witness_audible(f, PRIMARY_I,
                                                   per[PRIMARY_I]["B"], m))
                              for f in [Fraction(1), Fraction(4, 3)])) > 2,
                   step=6.0)

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
print(f"\n  margin-domain edge probe: lower bound bites = "
      f"{probe['lo_is_a_boundary']}, upper = {probe['hi_is_a_boundary']}")

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
               margin_edge_probe={k: str(x) for k, x in probe.items()},
               bars={s["name"]: s for s in (s1, s2, s3)},
               scope="relative masking only: no absolute threshold in quiet, no "
                     "temporal integration, no binaural effects",
               verdict=v["head"], composed=v),
          open(f"{HERE}/brocot_masked_horizon.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_masked_horizon.json")
