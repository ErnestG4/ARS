"""Report un-actioned structural debt so a green board cannot hide it.

WHY THIS IS A CHECK AND NOT AN OWNER. `bridge/proposals/` holds a change that
cannot be applied without the bridge arc's deliberate re-seal (its files are under
blob-SHA freeze). "Someone should own it" is true and will stay true, which is how
a proposal directory becomes a forgotten directory. So instead of assigning it,
make the debt UN-SILENT: every future green board carries a visible PENDING line.

This does NOT fail the board. Forcing the work would be wrong -- the re-seal is the
owning arc's call. It makes the debt visible, which is the same move as read-time
rail visibility: the caveat travels with the artifact or it does not travel.
"""
import glob, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
pending = []

for d in sorted(glob.glob(f"{ROOT}/*/proposals")):
    arc = os.path.basename(os.path.dirname(d))
    for f in sorted(glob.glob(f"{d}/*.md")):
        pending.append((arc, os.path.basename(f)))

if not pending:
    print("VERIFY_PENDING_DEBT: PASS — no un-actioned proposals")
    sys.exit(0)

print(f"VERIFY_PENDING_DEBT: PASS with {len(pending)} PENDING "
      "(visible by design; does not fail the board)")
for arc, f in pending:
    print(f"  PENDING  {arc:10s} {f}")
print("  These require the owning arc's deliberate re-seal, not a drive-by edit.")
sys.exit(0)
