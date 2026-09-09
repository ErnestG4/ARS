"""Re-derive the sieve-stage anchor from the artifact it reads.

  1. The stimulus numbers come from brocot_resynthesis_fidelity, not from this
     cell: the detune, the duration and every beat rate must still match there.
     If the twin is ever rebuilt at a different detune, this anchor's whole
     comparison changes and must not silently keep its old conclusion.
  2. The cents-to-percent conversion re-derives.
  3. THE TWO HALVES STILL DISAGREE. That is the finding — a single answer would
     mean the row could have been settled by asking one question, and it could
     not. If both halves ever agree, the reading needs rewriting, not patching.
  4. The verification levels are preserved: Moore 1986 full-text, Moore 1985
     ABSTRACT ONLY. The duration argument leans on the abstract-level source, so
     an artifact that upgraded that label without new reading would be claiming
     evidence it does not have.
  5. The POST-HOC label survives.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
bad = []
a = json.load(open(os.path.join(HERE, "brocot_sieve_anchor.json")))
src = json.load(open(os.path.join(HERE, "brocot_resynthesis_fidelity.json")))

st = a["stimulus"]
if st["cents"] != src["cents"]:
    bad.append(f"detune {st['cents']} != the twin's {src['cents']} — the anchor "
               "is describing a stimulus that no longer exists")
if st["duration_s"] != src["duration_s"]:
    bad.append(f"duration {st['duration_s']} != the twin's {src['duration_s']}")
beats_src = {r["ratio"]: r["beat_hz"] for r in src["rows"]}
if st["beat_hz"] != beats_src:
    bad.append("beat rates no longer match brocot_resynthesis_fidelity")

want_pct = (2.0 ** (st["cents"] / 1200.0) - 1.0) * 100.0
if abs(st["percent_of_frequency"] - want_pct) > 1e-9:
    bad.append(f"percent-of-frequency {st['percent_of_frequency']} != re-derived "
               f"{want_pct}")

h1, h2 = a["half1_heard_as_separate"], a["half2_discriminable"]
sep_min = min(a["norms"]["separate_tone_1986"]["values_percent"].values())
if abs(h1["smallest_published"] - sep_min) > 1e-12:
    bad.append("half 1 no longer cites the smallest published threshold")
if abs(h1["factor_below"] - sep_min / want_pct) > 1e-9:
    bad.append("half 1's factor-below does not re-derive")
if h1["prediction"] != "NEGATIVE":
    bad.append(f"half 1 prediction is {h1['prediction']!r}, not NEGATIVE")
if not h2["prediction"].startswith("DETECTABLE"):
    bad.append(f"half 2 prediction is {h2['prediction']!r}")
if h1["prediction"] == "NEGATIVE" and h2["prediction"].startswith("NEGATIVE"):
    bad.append("both halves now agree — the row's two-answer structure, which is "
               "the finding, has collapsed and the reading needs rewriting")

lvl = a["norms"]["inharmonicity_hz_1985"]["verification"]
if "ABSTRACT" not in lvl.upper():
    bad.append("the 1985 source's ABSTRACT-ONLY verification label is gone; the "
               "duration argument rests on it and may not be upgraded without "
               "new reading")
if "FULL TEXT" not in a["norms"]["separate_tone_1986"]["verification"].upper():
    bad.append("the 1986 full-text label has changed")
if "POST-HOC" not in a["status"].upper():
    bad.append("the anchor has lost its POST-HOC label")
if len(a["what_this_does_not_settle"]) < 3:
    bad.append("the not-settled list has shrunk; it carries the scope of a "
               "listener-free claim about a perceptual question")

print(f"  twin: {st['cents']:.1f} cents = {st['percent_of_frequency']:.4f}%, "
      f"{st['duration_s']:.1f} s, beats {min(beats_src.values()):.2f}-"
      f"{max(beats_src.values()):.2f} Hz")
print(f"  half 1 (heard-as-separate): {h1['factor_below']:.1f}x below the "
      f"smallest published mesh -> {h1['prediction']}")
print(f"  half 2 (discriminable): {h2['n_clearing_410ms_low']} of "
      f"{len(beats_src)} clear the 410 ms low bound -> {h2['prediction']}")

if bad:
    print("VERIFY_SIEVE_ANCHOR: FAIL")
    for b in bad:
        print("  *", b)
    sys.exit(1)
print("VERIFY_SIEVE_ANCHOR: PASS — the stimulus still matches the twin, the "
      "comparison re-derives, the two halves still disagree, and the "
      "abstract-level source is still labelled as one")
