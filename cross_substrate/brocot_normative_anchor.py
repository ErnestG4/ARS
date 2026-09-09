"""NORMATIVE ANCHOR: calibrate the Stage A masking criterion against published
resolvability, on the norms' own stimulus.

COMMITTED GENERATOR of cross_substrate/brocot_normative_anchor.json.
Predictions sealed here, before any harmonic-complex output exists.

WHY, AND WHICH QUESTION THIS CAN AND CANNOT ANSWER
---------------------------------------------------
The `heard-as-listening` ledger row is blocked on listeners: n = 1, and that one
listener is the experimenter, whose first impression broke the blinding. The row
was re-posed 2026-09-07 after the operator asked whether a standard test already
matches his responses. It does, and the norms even mirror this programme's own
beat/merge arm split:

  Moore, Glasberg & Peters, JASA 80(2), 1986, 479-483 -- "Thresholds for hearing
  mistuned partials as separate tones in harmonic complexes". Verified from
  fetched full text: 10 or 12 equal-amplitude components at 60 dB SPL per
  component, f0 in {100, 200, 400} Hz, 410 ms, adaptive to d' = 1, harmonics 1-6.
  Table I (f0 = 200 Hz, 410 ms, percent of harmonic frequency), transcribed from
  the fetched table:
      harmonic       1     2     3     4     5     6
      1985b (any cue)  1.2   1.3   1.0  0.94  0.89  0.29
      1986 (separate)  1.7   1.7   1.3   1.8   2.0   2.1

THE SCOPE LINE, and the paper draws it for us. Its own summary sentence is
"provided a partial is RESOLVABLE, it is heard as separate when it is rejected by
a harmonic sieve whose mesh size is a constant percentage of the harmonic
frequency." Two stages: resolvability, then a sieve. **Our criterion is a model of
the first stage only.** It asks whether a partial stands above the masking its
neighbours produce inside one auditory filter; it contains no harmonic template
and no sieve, so it CANNOT produce the 1-3% mistuning thresholds and this cell
does not pretend to. Anchoring the sieve stage would need a different instrument.

WHAT AN ANCHOR ON STAGE ONE BUYS, which is the thing the ledger row needs. Our
banked headline is a NEGATIVE: at I = 0.9, zero of the 12 non-degenerate
below-horizon ratios clear masking. A negative claim is only as strong as the
permissiveness of the criterion that produced it. If our criterion is MORE
permissive than the published resolvability limit, then a stricter, better-
validated criterion would also return zero, and the headline is conservative. If
it is STRICTER, the headline is manufactured by an over-severe instrument and the
whole audibility line needs re-reading. That direction is what C3 tests, and it
is worth more to this programme than a matched number would be.

THE COMPARISON STANDARD, declared rather than borrowed: a harmonic is RESOLVED
when the auditory filter at its frequency is narrower than the component spacing,
ERB(n*f0) < f0, with the same Glasberg-Moore ERB this toolchain already uses.
At f0 = 200 Hz that gives n_std = 8, which sits inside the 8-10 range this
literature commonly quotes -- stated as a consistency remark, not as a citation,
because the ERB-crossing rule is being DECLARED here and its arithmetic is shown.

MACHINERY: erb_w, audible, lattice and witness_audible are copied VERBATIM from
the committed brocot_masked_horizon.py (which cannot be imported -- it executes
its measurement at import time). Verbatim copying is not trust: P1 re-runs the
copies against two banked artifacts and demands their numbers back.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — every bar strictly inside its stated range.             ║
║                                                                              ║
║ P1  PREMISE    the copied criterion reproduces the banked FM results: the 4  ║
║                masked_horizon ERB-row counts and the 12 criterion_scope_v2   ║
║                sigma>=0.4 cells at I = 0.9. Mismatches <= 0.5 of 16.         ║
║ C1  EXISTENCE  on an extended equal-amplitude complex the criterion          ║
║                DISCRIMINATES: at least one harmonic audible and at least     ║
║                one masked, at every f0. Counted as f0 values that            ║
║                discriminate, >= 2.5 of 3. A criterion that calls everything  ║
║                audible has no resolvability limit to compare and the cell    ║
║                cannot proceed.                                              ║
║ C2  MECHANISM  and the audible set is a PREFIX in harmonic number -- one     ║
║                crossover, no holes. Total holes across the three f0 <= 0.5.  ║
║                Resolvability must degrade monotonically with n; holes would  ║
║                mean the criterion is reading something else.                 ║
║ C3  MECHANISM  DIRECTION, and this is the cell: our crossover is not         ║
║                STRICTER than the declared standard -- n* >= n_std at every   ║
║                f0, counted as f0 values satisfying it, >= 2.5 of 3.          ║
║                A miss inverts the reading of every banked audibility null.   ║
║ C4  RESOLUTION MAGNITUDE: and the permissiveness is bounded, max over f0 of  ║
║                n*/n_std <= 3.0. Unbounded permissiveness would make the      ║
║                criterion uncalibrated rather than conservative.              ║
║                                                                              ║
║ PRE-REGISTERED EXPECTATION, so the report is not written after the fact: a   ║
║ Gaussian with sigma = ERB/sqrt(2pi) has far lighter tails than a real roex   ║
║ filter, so I expect n* ABOVE n_std -- permissive, C3 MET, and C4 the open    ║
║ question. On the norms' literal 12-component stimulus I therefore expect     ║
║ every harmonic to read audible, which is reported as the calibration datum   ║
║ it is rather than as a failure.                                             ║
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
from reachable import Bar                                           # noqa: E402
from verdictlattice import (Arm, compose, PREMISE as PREM_ROLE,      # noqa: E402
                            EXISTENCE as EX_ROLE,
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from modelparams import Model, Param, TESTED, DECLARED               # noqa: E402
from phase3.partial_prediction import order_bound                    # noqa: E402

SIGMA_LIT = 1.0 / np.sqrt(2.0 * np.pi)      # ERB-matched Gaussian, 0.3989...
MARGIN = 0.0
F0_LIST = [100.0, 200.0, 400.0]
N_NORMS = 12                                 # the norms' own component count
N_EXT = 60                                   # extended, so a crossover can exist
F_C = 220.0
LO, HI = Fraction(7, 10), Fraction(7, 5)

MGP1986_TABLE_I = {                          # percent of harmonic frequency
    "f0_hz": 200.0, "duration_ms": 410,
    "any_cue_1985b": {1: 1.2, 2: 1.3, 3: 1.0, 4: 0.94, 5: 0.89, 6: 0.29},
    "separate_tone_1986": {1: 1.7, 2: 1.7, 3: 1.3, 4: 1.8, 5: 2.0, 6: 2.1}}

INSTRUMENT = Model("Stage A masking criterion on a harmonic complex", [
    Param("sigma_scale", DECLARED, value=float(SIGMA_LIT),
          why="the ERB-matched Gaussian, sigma = ERB/sqrt(2pi): the ERB of a "
              "peak-1 Gaussian is its integral, sigma*sqrt(2pi). This is the "
              "operating point the operator chose on 2026-09-07 (follow the "
              "literature), so the anchor tests the criterion as it is actually "
              "used, not a tuned variant"),
    Param("margin_db", DECLARED, value=MARGIN,
          why="the primary margin throughout the arc; masked_horizon showed the "
              "count is stable across a 12 dB swing at this index"),
    Param("f0_hz", TESTED, sweep=F0_LIST,
          why="the three fundamentals of the norms' own design; resolvability "
              "depends on f0 through ERB growth, so a single f0 would not "
              "distinguish a calibration from a coincidence"),
    Param("n_components", TESTED, sweep=[N_NORMS, N_EXT],
          why="12 is the norms' stimulus and is REPORTED as such; 60 is the "
              "extension needed for a crossover to exist at all, since the "
              "pre-registered expectation is a crossover above 12"),
    Param("resolvability_standard", DECLARED, value="ERB(n*f0) < f0",
          why="DECLARED, not cited: a harmonic is resolved when the auditory "
              "filter at its frequency is narrower than the spacing. Arithmetic "
              "shown in the report; lands at n_std = 8 for f0 = 200, inside the "
              "8-10 range this literature commonly quotes"),
    Param("equal_amplitude", DECLARED, value=True,
          why="the norms' stimulus is equal-amplitude components (60 dB SPL "
              "each); using anything else would not be their stimulus"),
])


# ---- VERBATIM from brocot_masked_horizon.py (committed) ----
def erb_w(f):
    return 24.7 * (4.37 * f / 1000.0 + 1.0)


def audible(fk, ak, f, a, margin_db, width_scale=1.0):
    other = f != fk
    if not other.any():
        return True
    e = np.sqrt(np.sum((a[other] ** 2)
                       * np.exp(-0.5 * ((fk - f[other])
                                        / (erb_w(f[other]) * width_scale)) ** 2)))
    if e <= 0:
        return True
    return 20.0 * np.log10(ak / e) > margin_db


def lattice(alpha, I, B):
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
# ---- end verbatim ----


def below_horizon(I):
    B = order_bound(I)
    A = 2 * B
    return B, sorted({Fraction(p, q) for q in range(1, A + 1)
                      for p in range(1, A + 1)
                      if gcd(p, q) == 1 and LO <= Fraction(p, q) <= HI
                      and max(p, q) <= A}, key=float)


# ---- P1: the copies must reproduce the banked FM artifacts ----
mh = json.load(open(os.path.join(HERE, "brocot_masked_horizon.json")))
cs = json.load(open(os.path.join(HERE, "brocot_criterion_scope_v2.json")))
mismatch = 0
for I in mh["I_list"]:
    B, ratios = below_horizon(I)
    got = sum(bool(witness_audible(f, I, B, 0.0, 1.0)) for f in ratios)
    if got != mh["width_sensitivity"]["ERB"][str(I)]:
        mismatch += 1
B09, R09 = below_horizon(0.9)
for m in cs["margins"]:
    for s in cs["sigmas"]:
        if s < 0.4:
            continue
        aud = [f for f in R09 if witness_audible(f, 0.9, B09, m, s)]
        if len(aud) != cs["grid"][f"I=0.9,m={m},s={s}"]["total"]:
            mismatch += 1
P1 = Bar("copied-criterion mismatches vs 16 banked FM numbers", 0.5,
         direction="le", floor=0, ceiling=16,
         why="4 masked_horizon ERB-row counts + 12 criterion_scope sigma>=0.4 "
             "cells at I=0.9; a count of disagreements, 0 to 16")
p1 = P1.score(mismatch)


# ---- the harmonic-complex scan ----
def complex_audible(f0, n_comp, sigma):
    f = np.array([(n + 1) * f0 for n in range(n_comp)])
    a = np.ones(n_comp)
    keep = (f >= 20.0) & (f <= 16000.0)
    f, a = f[keep], a[keep]
    return [bool(audible(f[i], a[i], f, a, MARGIN, sigma)) for i in range(len(f))]


def n_std_of(f0):
    n = 1
    while erb_w((n + 1) * f0) < f0:
        n += 1
    return n


scan, norms_read = {}, {}
disc, holes, dir_ok, ratios_ns = 0, 0, 0, {}
for f0 in F0_LIST:
    aud = complex_audible(f0, N_EXT, SIGMA_LIT)
    scan[str(f0)] = aud
    if any(aud) and not all(aud):
        disc += 1
    first_masked = next((i for i, x in enumerate(aud) if not x), len(aud))
    holes += sum(1 for x in aud[first_masked:] if x)
    n_star = first_masked                      # count of leading audible harmonics
    ns = n_std_of(f0)
    ratios_ns[str(f0)] = dict(n_star=n_star, n_std=ns,
                              ratio=(n_star / ns if ns else float("inf")))
    if n_star >= ns:
        dir_ok += 1
    norms_read[str(f0)] = sum(complex_audible(f0, N_NORMS, SIGMA_LIT))

C1 = Bar("f0 values where the criterion discriminates", 2.5, floor=0, ceiling=3,
         why="a count over the 3 fundamentals; 'some audible and some not'")
c1 = C1.score(disc)
C2 = Bar("holes in the audible prefix, summed over f0", 0.5, direction="le",
         floor=0, ceiling=3 * N_EXT,
         why="an audible harmonic above the first masked one, counted over all "
             "three complexes")
c2 = C2.score(holes)
C3 = Bar("f0 values where n* >= n_std (criterion not stricter)", 2.5,
         floor=0, ceiling=3, why="a count over the 3 fundamentals")
c3 = C3.score(dir_ok)
worst = max(v["ratio"] for v in ratios_ns.values())
C4 = Bar("max over f0 of n*/n_std", 3.0, direction="le", floor=0.0, ceiling=60.0,
         why="a ratio of harmonic numbers; bounded above by N_EXT/1")
c4 = C4.score(worst)

# ---- report ----
print(INSTRUMENT.report())
print(f"\nP1: copied criterion vs banked FM artifacts — {mismatch} of 16 mismatched")
print(f"\nresolvability scan, sigma = ERB/sqrt(2pi) = {SIGMA_LIT:.6f}, "
      f"margin {MARGIN:+.0f} dB, equal amplitude")
print(f"  {'f0':>7s} {'n*':>5s} {'n_std':>6s} {'ratio':>7s}   "
      f"{'ERB(n_std*f0)':>13s} {'audible of 12':>14s}")
for f0 in F0_LIST:
    r = ratios_ns[str(f0)]
    print(f"  {f0:>7.0f} {r['n_star']:>5d} {r['n_std']:>6d} {r['ratio']:>7.2f}   "
          f"{erb_w(r['n_std'] * f0):>13.1f} {norms_read[str(f0)]:>10d} of 12")
print(f"\n  the norms' own stimulus (12 equal-amplitude components): our "
      f"criterion calls\n  {norms_read['200.0']} of 12 audible at f0 = 200 Hz, "
      f"against a declared standard of n_std = {n_std_of(200.0)}")
print("\n  SCOPE, from the source's own summary: their threshold is a harmonic-"
      "SIEVE mesh\n  size CONDITIONAL on resolvability. This criterion models "
      "resolvability only and\n  cannot produce their 1-3% mistuning numbers; "
      "Table I is banked as the record of\n  what an anchor on the second stage "
      "would have to match.")
print()
for b, v, f in ((P1, mismatch, "{:.0f}"), (C1, disc, "{:.0f}"),
                (C2, holes, "{:.0f}"), (C3, dir_ok, "{:.0f}"),
                (C4, worst, "{:.2f}")):
    print("  " + b.line(v, f))

v = compose([Arm.from_bar(p1, PREM_ROLE,
                          claim="the copied criterion IS the banked criterion"),
             Arm.from_bar(c1, EX_ROLE,
                          claim="the criterion has a resolvability limit to compare"),
             Arm.from_bar(c2, MECH_ROLE,
                          claim="and it degrades monotonically in harmonic number"),
             Arm.from_bar(c3, MECH_ROLE,
                          claim="the criterion is not STRICTER than the published "
                                "resolvability standard, so the banked audibility "
                                "nulls are conservative"),
             Arm.from_bar(c4, RES_ROLE,
                          claim="and its permissiveness is bounded, so it is "
                                "calibrated rather than merely loose")],
            holds="AUDIBILITY_NULLS_ARE_CONSERVATIVE_AGAINST_PUBLISHED_RESOLVABILITY",
            fails="CRITERION_NOT_ANCHORED_TO_PUBLISHED_RESOLVABILITY")
print(f"\nVERDICT: {v['citation']}")

json.dump(dict(
    sigma_scale=float(SIGMA_LIT), margin_db=MARGIN, f0_list=F0_LIST,
    n_components={"norms": N_NORMS, "extended": N_EXT},
    resolvability_standard="ERB(n*f0) < f0 (DECLARED)",
    per_f0=ratios_ns, audible_of_12_norms_stimulus=norms_read,
    audible_prefix={k: sum(v) for k, v in scan.items()},
    source=dict(
        citation="Moore, Glasberg & Peters, JASA 80(2), 1986, 479-483",
        stimulus="10 or 12 equal-amplitude components, 60 dB SPL per component, "
                 "f0 in {100,200,400} Hz, 410 ms, adaptive to d'=1, harmonics 1-6",
        scope_sentence="provided a partial is resolvable, it is heard as separate "
                       "when it is rejected by a harmonic sieve whose mesh size is "
                       "a constant percentage of the harmonic frequency",
        table_I=MGP1986_TABLE_I,
        companion="Moore, Peters & Glasberg, JASA 77, 1985, 1861-1867 "
                  "(inharmonicity detection, ~4 Hz at 410 ms)",
        verified="full text fetched and extracted 2026-09-08; Table I and the "
                 "stimulus line transcribed from the fetched text"),
    what_this_does_not_anchor="the harmonic-sieve stage: this criterion contains "
                              "no template and cannot produce the 1-3% mistuning "
                              "thresholds. Anchoring that stage needs a different "
                              "instrument.",
    bars={s["name"]: s for s in (p1, c1, c2, c3, c4)},
    instrument=INSTRUMENT.seal(),
    verdict=v["head"], composed=v),
    open(os.path.join(HERE, "brocot_normative_anchor.json"), "w"), indent=1)
print("\nwrote brocot_normative_anchor.json")
