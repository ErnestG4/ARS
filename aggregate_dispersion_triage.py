"""TWO DETECTORS, BOTH FAILED. Kept as the record of why, not as a tool.

Read-only. Exits 0. ITS OUTPUT IS NOT A FINDING LIST -- see the validation it
runs on itself below before reading a single row of it.

THE DEFECT IT WAS BUILT FOR, 2026-09-05. Session F banked
"genus2_rate_ratio": 0.9583126741064829 -- a mean over curves whose spread is
sd 0.296 across 0.650 to 1.862, with no n and no error bar. Not wrong;
UNFALSIFIABLE AS WRITTEN, because nothing beside it says how much is signal. The
obvious next move is to sweep the repo for siblings. Twice now that sweep has
produced something that looks like a finding list and is not one.

ATTEMPT 1 KEYED ON PRECISION. Flag floats with >= 12 significant figures whose
name looks like an aggregate. Result: 2410 candidates across 50 files, one file
contributing 594. Useless, and the reason is that JSON SERIALISES FULL FLOAT
PRECISION BY DEFAULT -- Session F's constant is not unusual for carrying
seventeen digits, EVERY computed float in this repo carries seventeen digits.
Precision was an incidental property of the artifact that made me notice the
defect, and I built on the thing I noticed rather than the thing that was wrong.

ATTEMPT 2 KEYED ON A MISSING COMPANION. Flag an aggregate-named scalar whose own
object offers nothing describing its spread (n, sd, sem, ci, min/max, ...), and
report the rate plus the sharper tell: files that carry dispersion for SOME
aggregates and not others. That produced a clean-looking statistic -- 54.1% of
6698 carried -- and a ranked list of mixed files.

THEN I HAND-CHECKED FOUR OF THE TOP HITS. All four were false positives, each
for a different reason:

    holonomy/op1_correctness.json   `separation` IS carried, by `separation_se`
                                    -- the companion regex has no `_se`
    survey/mask_kag_measured.json   dispersion is recoverable from the `rows`
                                    array sitting beside it
    lcap/misclass_rate.json         `worst_misclass_rate` is an EXTREMUM, not a
                                    mean; an extremum does not want an error bar
    gate_census/rejected_fits.json  `rejected_fraction` sits beside its own
                                    numerator and denominator

4/4. So the 54.1% is not a measurement of anything, and the mixed-file ranking
is dominated by cases where the dispersion is present in a form the regex cannot
see. Widening the regex would not fix it: `rows` is dispersion because a human
can read the array, and `worst_` is exempt because of what the word MEANS.

THE CONCLUSION, WHICH IS THE POINT OF KEEPING THIS FILE. The Session F defect is
SEMANTIC -- "this mean is a property of the family that was averaged, not a
constant" -- and semantic defects have no syntactic tell. That is already a
recorded lesson in this repo and I re-learned it by ignoring it: a census
detector keyed on syntax gives a LOWER BOUND, and its misses are the hard tail.
Building one without a negative set and a nearest-confusable case in advance
gives a detector that fires on the confusables, which is what both attempts did.

What would actually work is not a sweep. It is a construction-time rule: an
aggregate is banked WITH its n and its spread, enforced where aggregates are
written rather than searched for afterwards. That is a change to how cells bank
numbers, and it is queued rather than smuggled in here.

RUN IT TO SEE THE ATTEMPT-2 OUTPUT AND ITS OWN VALIDATION. Do not cite the rows.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP_DIRS = {".git", "__pycache__", "node_modules", "archive_v1grid", "data"}
AGG = re.compile(r"(mean|median|avg|average|ratio|rate|corr|rho|slope|"
                 r"fraction|share|score|coef|beta|exponent|dim)", re.I)
COMPANION = re.compile(r"(^n$|_n$|\bn_|sd|std|sem|stderr|err|ci|iqr|spread|"
                       r"range|min|max|quantile|percentile|boot)", re.I)
# a value that is plainly a count, a probability of 0/1, or an exact small
# rational does not want an error bar


def sigfigs(x):
    if not isinstance(x, float) or x != x or x == 0.0:
        return 0
    t = repr(abs(x))
    if "e" in t or "E" in t:
        t = t.split("e")[0]
    return len(t.replace(".", "").lstrip("0"))


def scan(obj, path, out):
    """Collect (path, value, carried?) for every aggregate-named scalar."""
    if isinstance(obj, dict):
        keys = [k for k in obj]
        carried = any(COMPANION.search(str(k)) for k in keys)
        for k, v in obj.items():
            if isinstance(v, float) and AGG.search(str(k)):
                out.append(("/".join(path + [str(k)]), v, carried))
            scan(v, path + [str(k)], out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:400]):
            scan(v, path + [f"[{i}]"], out)


rows = []
for dirpath, dirnames, files in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fn in files:
        if not fn.endswith(".json"):
            continue
        full = os.path.join(dirpath, fn)
        try:
            with open(full) as fh:
                d = json.load(fh)
        except Exception:                                       # noqa: BLE001
            continue
        got = []
        scan(d, [], got)
        if got:
            rows.append((os.path.relpath(full, ROOT), got))

tot = sum(len(g) for _, g in rows)
car = sum(1 for _, g in rows for (_, _, c) in g if c)
print("aggregate-dispersion triage — FAILED DETECTOR, kept as a record\n")
print("  HAND-VALIDATION OF ATTEMPT 2, run before any row below is readable:")
for f, why in [
        ("holonomy/op1_correctness.json",
         "`separation` IS carried by `separation_se`; regex has no `_se`"),
        ("survey/mask_kag_measured.json",
         "spread recoverable from the `rows` array beside it"),
        ("lcap/misclass_rate.json",
         "`worst_misclass_rate` is an EXTREMUM; it does not want an error bar"),
        ("gate_census/rejected_fits.json",
         "`rejected_fraction` sits beside its numerator and denominator")]:
    print(f"    FALSE POSITIVE  {f:<42s} {why}")
print("    4 of 4 top hits hand-checked were false positives, so the rate and "
      "the ranking below are NOT findings.\n")
print(f"  {tot} aggregate-named scalars across {len(rows)} files")
print(f"  {car} carry a dispersion companion in their own object "
      f"({100.0 * car / max(tot, 1):.1f}%)\n")

mixed = []
for f, g in rows:
    n, c = len(g), sum(1 for (_, _, x) in g if x)
    if n >= 4 and 0 < c < n:
        mixed.append((c / n, f, n, c))
mixed.sort(reverse=True)
print("  FILES THAT CARRY DISPERSION FOR SOME AGGREGATES AND NOT OTHERS —")
print("  the discriminating tell, because the author demonstrably knew to:\n")
for frac, f, n, c in mixed[:18]:
    print(f"    {frac:5.0%}  {c:3d}/{n:<3d}  {f}")
    miss = [p for (p, _, x) in rows[[r[0] for r in rows].index(f)][1] if not x]
    print(f"             uncarried e.g. {', '.join(miss[:3])}")
print(f"\n  {len(mixed)} mixed file(s).")
print("  LOWER BOUND: JSON-only, so numbers quoted in prose, docstrings and "
      "commit messages are invisible — and that is where headline constants "
      "travel. A companion key's presence is also not proof it describes the "
      "value beside it.")
