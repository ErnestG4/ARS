"""Re-derive the normative anchor INDEPENDENTLY of the cell that produced it.

The resolvability scan is recomputed here from a SEPARATE implementation of the
masking sum rather than by importing the cell's (which measures at import time
and could not be imported anyway). That is deliberate: an independent
recomputation that agrees is a method-invariance check, where importing would
only confirm the artifact matches itself.

  1. The scan re-derives: n* and n_std at every f0, and the norms'-stimulus count.
  2. THE DIRECTION HOLDS. C3 is the arm the arc's audibility nulls lean on --
     the criterion must not be STRICTER than the declared resolvability standard,
     or every banked null is manufactured by an over-severe instrument rather
     than conservative. This checker fails if that inverts.
  3. The permissiveness stays BOUNDED (C4), so "conservative" does not quietly
     become "uncalibrated".
  4. The SCOPE LINE survives: the artifact must keep saying, in its own record,
     that it does not anchor the harmonic-sieve stage. Losing that sentence is
     how a resolvability calibration would get read as a mistuning-threshold
     validation, which it is not.
  5. Table I is preserved verbatim as the transcribed source record.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
bad = []
d = json.load(open(os.path.join(HERE, "brocot_normative_anchor.json")))

SIG = d["sigma_scale"]
MARGIN = d["margin_db"]
N_EXT = d["n_components"]["extended"]
N_NORMS = d["n_components"]["norms"]


def erb(f):
    return 24.7 * (4.37 * f / 1000.0 + 1.0)


def audible_independent(idx, f, a):
    """Independent restatement: a partial is audible when its level exceeds, by
    more than the margin, the RMS of its neighbours' excitation at its own
    frequency, each neighbour spread by a Gaussian of sigma = scale * ERB(f_j)."""
    tot = 0.0
    for j in range(len(f)):
        if j == idx:
            continue
        tot += a[j] ** 2 * np.exp(-0.5 * ((f[idx] - f[j]) / (erb(f[j]) * SIG)) ** 2)
    e = np.sqrt(tot)
    if e <= 0:
        return True
    return 20.0 * np.log10(a[idx] / e) > MARGIN


def scan(f0, n_comp):
    f = np.array([(n + 1) * f0 for n in range(n_comp)])
    a = np.ones(n_comp)
    keep = (f >= 20.0) & (f <= 16000.0)
    f, a = f[keep], a[keep]
    return [audible_independent(i, f, a) for i in range(len(f))]


def n_std_of(f0):
    n = 1
    while erb((n + 1) * f0) < f0:
        n += 1
    return n


for f0 in d["f0_list"]:
    aud = scan(f0, N_EXT)
    n_star = next((i for i, x in enumerate(aud) if not x), len(aud))
    ns = n_std_of(f0)
    rec = d["per_f0"][str(f0)]
    if n_star != rec["n_star"]:
        bad.append(f"f0={f0}: n* banked {rec['n_star']}, re-derived {n_star}")
    if ns != rec["n_std"]:
        bad.append(f"f0={f0}: n_std banked {rec['n_std']}, re-derived {ns}")
    if abs(rec["ratio"] - (n_star / ns)) > 1e-9:
        bad.append(f"f0={f0}: ratio does not re-derive")
    if n_star < ns:
        bad.append(f"f0={f0}: the criterion is now STRICTER than the standard "
                   f"(n*={n_star} < n_std={ns}) — the banked audibility nulls "
                   "can no longer be called conservative")
    holes = sum(1 for x in aud[n_star:] if x)
    if holes:
        bad.append(f"f0={f0}: {holes} hole(s) above the first masked harmonic")
    got12 = sum(scan(f0, N_NORMS))
    if got12 != d["audible_of_12_norms_stimulus"][str(f0)]:
        bad.append(f"f0={f0}: norms'-stimulus count banked "
                   f"{d['audible_of_12_norms_stimulus'][str(f0)]}, re-derived {got12}")

worst = max(v["ratio"] for v in d["per_f0"].values())
if worst > 3.0:
    bad.append(f"permissiveness ratio {worst:.2f} now exceeds the sealed 3.0 bar "
               "— conservative has become uncalibrated")
# P1 lives in the bars dict, not at top level. The first version of this check
# read a key the artifact does not have, so it could never fire -- an inert guard,
# which is worse than no guard because it reads as coverage.
_p1 = d["bars"].get("copied-criterion mismatches vs 16 banked FM numbers")
if _p1 is None:
    bad.append("the P1 bar is missing from the artifact")
elif _p1["value"] != 0 or not _p1["met"]:
    bad.append(f"P1 records {_p1['value']} mismatches (met={_p1['met']}) — the "
               "copied criterion no longer reproduces the banked FM numbers, so "
               "this cell is calibrating a different instrument")
if d["verdict"] != "AUDIBILITY_NULLS_ARE_CONSERVATIVE_AGAINST_PUBLISHED_RESOLVABILITY":
    bad.append(f"verdict is {d['verdict']!r}")

# scope + source integrity
if "sieve" not in d["what_this_does_not_anchor"].lower():
    bad.append("the scope line no longer names the harmonic-sieve stage as "
               "un-anchored — a resolvability calibration must not be readable "
               "as a mistuning-threshold validation")
if "resolvable" not in d["source"]["scope_sentence"].lower():
    bad.append("the source's own scope sentence has been altered")
t1 = d["source"]["table_I"]
want = {"1": 1.7, "2": 1.7, "3": 1.3, "4": 1.8, "5": 2.0, "6": 2.1}
got = {str(k): v for k, v in t1["separate_tone_1986"].items()}
if got != want:
    bad.append(f"Table I (separate-tone) altered: {got} vs transcribed {want}")

print(f"  independent re-derivation of the scan at {len(d['f0_list'])} fundamentals:")
for f0 in d["f0_list"]:
    r = d["per_f0"][str(f0)]
    print(f"    f0={f0:>5.0f}  n*={r['n_star']:>3d}  n_std={r['n_std']:>2d}  "
          f"ratio {r['ratio']:.2f}  (permissive by {r['ratio']:.1f}x)")
_n_ok = sum(1 for f0 in d["f0_list"]
            if d["per_f0"][str(f0)]["n_star"] >= d["per_f0"][str(f0)]["n_std"])
print(f"  direction (n* >= n_std): {_n_ok} of {len(d['f0_list'])} fundamentals; "
      f"worst permissiveness {worst:.2f} against the 3.0 bar")

if bad:
    print("VERIFY_NORMATIVE_ANCHOR: FAIL")
    for b in bad:
        print("  *", b)
    sys.exit(1)
print("VERIFY_NORMATIVE_ANCHOR: PASS — an independent implementation reproduces "
      "the scan, the criterion is permissive-not-stricter at every f0 and "
      "boundedly so, and the sieve-stage scope line is intact")
