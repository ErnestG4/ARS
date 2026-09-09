#!/usr/bin/env python3
"""SIEVE-STAGE ANCHOR: what the norms predict for the twin we actually built.

POST-HOC AND UNSEALED, STATED FIRST. The comparison below is arithmetic on
numbers that were already banked, against published thresholds already read. No
prediction is sealed because none was made before the answer was visible;
pretending otherwise would be theatre. What this cell supplies is a decision for
the `heard-as-listening` row, not a discovery.

WHAT THE RESOLVABILITY ANCHOR LEFT OPEN
----------------------------------------
`brocot_normative_anchor` (2026-09-08) anchored STAGE ONE and said so: Moore,
Glasberg & Peters 1986's own summary is "provided a partial is RESOLVABLE, it is
heard as separate when it is rejected by a harmonic SIEVE whose mesh size is a
constant percentage of the harmonic frequency." Our masking criterion models
resolvability; the sieve stage was left explicitly un-anchored, and the
`heard-as-listening` row was narrowed to it.

The sieve stage turns out to be reachable after all, for a reason that was in
front of us: **at rational alpha = p/q the FM spectrum is HARMONIC.** Partials
sit at f_c*|1 + n1 + n2*(p/q)| = f_c*(integer)/q, i.e. on a harmonic series with
fundamental f_c/q. And `brocot_resynthesis_fidelity`'s twin moves ONLY the
witness pair, which makes those two partials mistuned against an otherwise
harmonic complex. That is Moore et al.'s paradigm, not an analogue of it.

THE NORMS, with their verification levels stated separately because they differ:

  MGP 1986 (JASA 80(2), 479-483) -- FULL TEXT fetched and Table I transcribed
  2026-09-08. "Heard as a SEPARATE TONE", f0 = 200 Hz, 410 ms, percent of
  harmonic frequency, harmonics 1-6: 1.7, 1.7, 1.3, 1.8, 2.0, 2.1.
  Same table, Moore et al. 1985b, detection by ANY CUE: 1.2, 1.3, 1.0, 0.94,
  0.89, 0.29.

  MPG 1985 (JASA 77, 1861-1867) -- ABSTRACT LEVEL ONLY, not full text.
  Inharmonicity detection thresholds "roughly constant when expressed in Hz,
  having a mean value of about 4 Hz (range 2.4-7.3)" at 410 ms; and "for
  harmonics above the fifth the thresholds increased from less than 1 Hz to
  about 40 Hz as duration was decreased from 1610-50 ms". The duration scaling
  is therefore a DIRECTION taken from an abstract, and every use of it below is
  marked as a bound rather than a value.

THE STIMULUS WE BUILT, read from the banked artifact rather than recalled:
6.0 cents of detune on the witness pair, 3.0 s duration, f_c = 220 Hz, 8 ratios.

The two halves of the row get opposite answers, which is why the row could not be
settled by asking one question.
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

MGP1986_SEPARATE = {1: 1.7, 2: 1.7, 3: 1.3, 4: 1.8, 5: 2.0, 6: 2.1}   # % of harmonic f
MGP1985_ANY_CUE = {1: 1.2, 2: 1.3, 3: 1.0, 4: 0.94, 5: 0.89, 6: 0.29}
MPG1985_HZ_410MS = dict(mean=4.0, lo=2.4, hi=7.3)

d = json.load(open(os.path.join(HERE, "brocot_resynthesis_fidelity.json")))
cents = d["cents"]
dur = d["duration_s"]
pct = (2.0 ** (cents / 1200.0) - 1.0) * 100.0        # detune as % of frequency
beats = {r["ratio"]: r["beat_hz"] for r in d["rows"]}

sep_min, sep_max = min(MGP1986_SEPARATE.values()), max(MGP1986_SEPARATE.values())
any_min, any_max = min(MGP1985_ANY_CUE.values()), max(MGP1985_ANY_CUE.values())
margin_sep = sep_min / pct
n_above_410 = sum(1 for b in beats.values() if b >= MPG1985_HZ_410MS["mean"])
n_above_lo = sum(1 for b in beats.values() if b >= MPG1985_HZ_410MS["lo"])

print(__doc__.split("THE NORMS")[0].strip()[:0] or "", end="")
print("POST-HOC ANCHOR — unsealed. Arithmetic on banked numbers.\n")
print(f"the twin as built: {cents:.1f} cents = {pct:.4f}% of frequency, "
      f"{dur:.1f} s, {len(beats)} ratios\n")
print("HALF 1 — 'heard as a detuned X' (Moore 1986, heard-as-SEPARATE-TONE)")
print(f"  published mesh, harmonics 1-6 : {sep_min:.1f}% - {sep_max:.1f}%")
print(f"  our detune                    : {pct:.4f}%")
print(f"  => the twin is {margin_sep:.1f}x BELOW the smallest published threshold.")
print("     PREDICTED NEGATIVE: at 6 cents the moved pair is not heard as a")
print("     separate tone by these norms, at any harmonic they measured.\n")
print("HALF 2 — 'a difference is discriminable' (beat / inharmonicity detection)")
print(f"  published, 410 ms, ~constant in Hz: mean {MPG1985_HZ_410MS['mean']:.1f} Hz "
      f"(range {MPG1985_HZ_410MS['lo']:.1f}-{MPG1985_HZ_410MS['hi']:.1f})")
print(f"  our beat rates                    : "
      f"{min(beats.values()):.2f} - {max(beats.values()):.2f} Hz")
print(f"  {n_above_410} of {len(beats)} ratios clear the 410 ms MEAN; "
      f"{n_above_lo} of {len(beats)} clear the bottom of its range.")
print(f"  our stimulus is {dur:.1f} s, and the published thresholds FALL with")
print("     duration (<1 Hz by 1610 ms for harmonics above the fifth), so at 3 s")
print("     the bound moves in our favour. PREDICTED DETECTABLE, as a bound.\n")
print(f"{'ratio':>7s} {'beat Hz':>8s}  {'vs 410ms mean':>14s}")
for r, b in beats.items():
    print(f"{r:>7s} {b:>8.2f}  {'clears' if b >= 4.0 else 'below':>14s}")

out = dict(
    status="POST-HOC, UNSEALED ANCHOR — no sealed prediction; arithmetic on "
           "banked numbers against published thresholds",
    stimulus=dict(cents=cents, percent_of_frequency=pct, duration_s=dur,
                  f_c=d["f_c"], n_ratios=len(beats), beat_hz=beats),
    why_the_sieve_applies="at rational alpha = p/q the FM spectrum is harmonic "
                          "with fundamental f_c/q, and the twin mistunes ONLY the "
                          "witness pair against it — Moore et al.'s paradigm, not "
                          "an analogue",
    norms=dict(
        separate_tone_1986=dict(values_percent=MGP1986_SEPARATE,
                                verification="FULL TEXT fetched, Table I transcribed",
                                citation="Moore, Glasberg & Peters, JASA 80(2), "
                                         "1986, 479-483; f0=200 Hz, 410 ms"),
        any_cue_1985b=dict(values_percent=MGP1985_ANY_CUE,
                           verification="FULL TEXT (same Table I)"),
        inharmonicity_hz_1985=dict(**MPG1985_HZ_410MS,
                                   verification="ABSTRACT LEVEL ONLY — the "
                                                "duration scaling is a direction "
                                                "from an abstract and is used "
                                                "only as a bound",
                                   citation="Moore, Peters & Glasberg, JASA 77, "
                                            "1985, 1861-1867")),
    half1_heard_as_separate=dict(
        our_percent=pct, smallest_published=sep_min,
        factor_below=margin_sep, prediction="NEGATIVE"),
    half2_discriminable=dict(
        beat_hz_range=[min(beats.values()), max(beats.values())],
        n_clearing_410ms_mean=n_above_410, n_clearing_410ms_low=n_above_lo,
        duration_s=dur, prediction="DETECTABLE (as a bound, duration favourable)"),
    reading="The row's two halves get OPPOSITE answers. The twin carries a "
            "discriminable difference by the norms, but at 6 cents it is 3.7x "
            "below the smallest published threshold for being HEARD AS A "
            "SEPARATE TONE. So the positive claim as worded — 'heard as a "
            "detuned X' — is predicted NEGATIVE at the stimulus we actually "
            "built, while 'a listener can tell the two apart' is predicted "
            "positive.",
    options_for_the_row=[
        "raise the detune to >= 1.3% (~22 cents) if the 'heard as' wording is "
        "wanted, and re-run the fidelity cell at that detune — note this may "
        "break the twin's fidelity, which was certified at 6 cents",
        "re-word the claim to discriminability, which the norms support at the "
        "built stimulus and which is what the apparatus was actually validated for",
    ],
    what_this_does_not_settle=[
        "the duration extrapolation from 410 ms to 3 s is a DIRECTION from an "
        "abstract, not a fitted curve",
        "Moore's complexes carry 10-12 equal-amplitude components; ours carry 69 "
        "partials at FM amplitudes, so the masking environment differs and the "
        "resolvability precondition must be checked per partial (that is what "
        "brocot_normative_anchor does, and it found our criterion permissive)",
        "a beat between two formerly-coincident partials is not identical to a "
        "single partial mistuned against a complex; the 1985 threshold is the "
        "closest published quantity, not the same quantity",
    ])
json.dump(out, open(os.path.join(HERE, "brocot_sieve_anchor.json"), "w"), indent=1)
print("\nwrote brocot_sieve_anchor.json")
