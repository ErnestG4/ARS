"""Census: which cells depend on an instrument constant they never declared?

`modelparams` forces every parameter a cell DECLARES to be TESTED-with-a-sweep or
DECLARED-with-a-defence. It cannot force a cell to declare a parameter it never
mentions -- it cannot know the parameter exists. That gap is not hypothetical:

  Stage 3 (53130cb) declared `window_upper_k` and no lower edge. Sweeping the
  upper edge, z(k*) is stable 47.7 -> 148.6. Sweeping the LOWER edge on the same
  window, the separation stays flat (4.444 -> 4.544) while z(k*) collapses
  82.5 -> 0.1. The sensitive axis was the undeclared one, and no guard could
  have said so.

Three module-level constants change a banked number and are imported rather than
declared:

  KSTAR_LEVEL    = 1e-2  the level whose crossing DEFINES k*, the arc's declared
                         comparison statistic. Every k* in every cell is relative
                         to it. A Stage 3 design audit swept it (3e-2 .. 1e-3)
                         and found no verdict changes -- an honest negative, but
                         one nobody had run until an outside reader asked.
  FIT_WINDOW_MIN = 1e-3  defines the sealed fit window. Stage 3c measured that
                         the window moves z(beta) by 15x-109x and places the
                         sealed choice at the 87th percentile at every n. This
                         is the most consequential undeclared constant in the
                         repo.
  BULK_FRACTION  = 0.20  the central window every statistic is read over.

THIS ROW IS A CENSUS, NOT A PROHIBITION. The existing uses are in SEALED cells
and cannot be retroactively declared without breaking the seal -- so it records
them permanently and fails only when the number GOES UP. Same shape as the fix
to `verify_guard_usage`, which once froze consumer counts exactly and turned the
board red when a guard was used MORE: a regression guard must fail on the thing
getting worse, not on the arithmetic changing.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Constants that change a banked number if they change.
WATCHED = {
    "KSTAR_LEVEL": "the level whose crossing defines k*",
    "FIT_WINDOW_MIN": "defines the sealed fit window",
    "BULK_FRACTION": "the central window statistics are read over",
}
# Census taken 2026-09-14. Fails if it GROWS; shrinking is progress.
#
# The first number written here was 11, from hand-listing seven files I thought
# were the relevant ones. The systematic walk found 15 -- four cells I had not
# thought to name, including two of the recert series' own. Recorded because it
# is the same defect one level up: a count over an enumerated list is blind to
# whatever the list omits, which is why this row walks the tree instead.
#
# Raised 15 -> 16 on 2026-09-14 at 05:15. stage3d_error_model.py imports
# FIT_WINDOW_MIN without declaring it -- a cell I sealed at 04:38, ONE HOUR
# after writing this census forbidding exactly that. The ratchet caught its own
# author's next cell. Recorded rather than quietly absorbed: 3d is sealed and
# cannot be amended, so the count moves and the reason is written down.
#
# Raised 16 -> 18 on 2026-09-15. stage3e_identifiability.py imports KSTAR_LEVEL
# and FIT_WINDOW_MIN undeclared — the SECOND cell in 24 hours I sealed after
# writing this census, and the second it caught. A board-time census that fires
# after the seal cannot prevent the seal. sealgen.sh now runs this check on the
# generator BEFORE committing it and refuses on a new undeclared dependency.
#
# Then 18 -> 17 the same hour: the census had a FALSE POSITIVE. It accepted only
# a Param whose NAME matched the constant, so recert_bias_surface's
# Param("bulk_window", DECLARED, value=BULK_FRACTION) was miscounted as
# undeclared. Both forms are accepted now. recert_section_sweep stays counted:
# it sweeps window sizes that include 0.20 but never declares that BULK_FRACTION
# is the reference value it indexes results by, which is a real omission.
BASELINE = 17

bad = []
rows = []
for root, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "archive_v1grid")]
    for fn in sorted(files):
        if not fn.endswith(".py") or fn.startswith("verify_"):
            continue
        path = os.path.join(root, fn)
        try:
            src = open(path, encoding="utf-8").read()
        except Exception:
            continue
        if "Model(" not in src and "modelparams" not in src:
            continue
        for const in WATCHED:
            if not re.search(rf"\b{const}\b", src):
                continue
            # declared under its own name, OR declared under any name with the
            # constant as its value -- recert_section_sweep declares
            # Param("bulk_window", DECLARED, value=BULK_FRACTION), which the
            # first version of this census miscounted as undeclared.
            if re.search(rf"Param\(\s*[\"']{const}[\"']", src) or \
               re.search(rf"Param\([^)]*?value\s*=\s*{const}\b", src, re.S):
                continue
            rows.append((os.path.relpath(path, ROOT), const))

print(f"  cells depending on an instrument constant they do not declare: "
      f"{len(rows)} (baseline {BASELINE})")
by_const = {}
for f, c in rows:
    by_const.setdefault(c, []).append(f)
for c in sorted(by_const):
    print(f"    {c:<15} ({WATCHED[c]})")
    for f in by_const[c]:
        print(f"        {f}")

if len(rows) > BASELINE:
    new = len(rows) - BASELINE
    bad.append(f"{new} NEW undeclared dependency(ies) since the 2026-09-14 "
               f"census. A cell that imports one of {sorted(WATCHED)} without "
               "declaring it cannot sweep it, and an unswept parameter is one "
               "nothing can flag — that is how Stage 3 missed its lower window "
               "edge. Declare it as a Param, or add it here with a reason.")
elif len(rows) < BASELINE:
    print(f"  -> {BASELINE - len(rows)} fewer than baseline; lower BASELINE to "
          f"{len(rows)} so the ratchet cannot slip back.")

if bad:
    print("VERIFY_DECLARED_PARAMS: FAIL")
    for b in bad:
        print("  *", b)
    sys.exit(1)
print("VERIFY_DECLARED_PARAMS: PASS — no new undeclared instrument dependency; "
      "the existing ones are named above and cannot be forgotten")
