"""Report un-actioned structural debt so a green board cannot hide it.

WHY THIS IS A CHECK AND NOT AN OWNER. `bridge/proposals/` holds a change that
cannot be applied without the bridge arc's deliberate re-seal (its files are under
blob-SHA freeze). "Someone should own it" is true and will stay true, which is how
a proposal directory becomes a forgotten directory. So instead of assigning it,
make the debt UN-SILENT: every future green board carries a visible PENDING line.

This does NOT fail the board. Forcing the work would be wrong -- the re-seal is the
owning arc's call. It makes the debt visible, which is the same move as read-time
rail visibility: the caveat travels with the artifact or it does not travel.

RESOLUTION MARKER, added 2026-09-09. The first version listed every file in a
proposals/ directory as PENDING, with no way to record that one had been acted
on. The moment a proposal IS resolved that line becomes permanently wrong, and a
debt line that is always wrong trains the reader to skip it -- the exact failure
this check exists to prevent, one level up. So a proposal whose text carries a
top-level `## RESOLVED` heading is reported SEPARATELY, as a record rather than
as debt. The file stays where it is: the request and its resolution belong
together, and deleting it would lose the reasoning.
"""

import glob, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
pending, resolved = [], []

for d in sorted(glob.glob(f"{ROOT}/*/proposals")):
    arc = os.path.basename(os.path.dirname(d))
    for f in sorted(glob.glob(f"{d}/*.md")):
        text = open(f).read()
        row = (arc, os.path.basename(f))
        if re.search(r"^##+\s*RESOLVED\b", text, re.M):
            resolved.append(row)
        else:
            pending.append(row)

if not pending:
    print(f"VERIFY_PENDING_DEBT: PASS — no un-actioned proposals"
          + (f" ({len(resolved)} resolved, listed below)" if resolved else ""))
else:
    print(f"VERIFY_PENDING_DEBT: PASS with {len(pending)} PENDING "
          "(visible by design; does not fail the board)")
    for arc, f in pending:
        print(f"  PENDING   {arc:10s} {f}")
    print("  These require the owning arc's deliberate re-seal, not a "
          "drive-by edit.")
for arc, f in resolved:
    print(f"  RESOLVED  {arc:10s} {f}")
sys.exit(0)
