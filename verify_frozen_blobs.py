"""Do every sealed arc's FROZEN BLOB SHAs still resolve in the object store?
Nonzero exit on any unreachable blob.

WHY: `git prune` + `git gc` ran 2026-08-19 (3.2G -> 1.6G) immediately after an
edit to a frozen file was reverted. The frozen SHAs *should* stay reachable
through each arc's sealed commit — and "should" is the word standing obligation 7
exists to kill. The board being green does not cover this unless the board
actually cat-files the SHAs, which it does not: `verify_bridge` compares the
WORKING TREE file's hash to the addendum, which passes whether or not the frozen
object is still in the store.

This converts "the freeze survived gc" from assumption to measurement. Read-only.
"""
import glob, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SHA = re.compile(r"\b([0-9a-f]{40}|[0-9a-f]{12})\b")


def blobs_from(obj, out, path=""):
    """Collect any 40-hex VALUE. The first version keyed on the NAME containing
    'blob'/'sha' -- but seals store `frozen_blob_shas: {<filename>: <sha>}`, so
    the keys are filenames and it matched nothing, then printed PASS on zero
    checks. Vacuous pass, the exact failure this session keeps finding; the
    ASSERT_MIN_BLOBS guard below is here so it cannot recur silently."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and SHA.fullmatch(v.strip()) and len(v.strip()) == 40:
                out.append((path + "/" + k, v.strip()))
            blobs_from(v, out, path + "/" + k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            blobs_from(v, out, f"{path}[{i}]")


found, missing, short = [], [], []
for f in sorted(glob.glob(f"{ROOT}/*/prereg_sealed.json")):
    arc = os.path.basename(os.path.dirname(f))
    try:
        d = json.load(open(f))
    except Exception as e:
        missing.append((arc, "<unreadable seal>", str(e))); continue
    out = []
    blobs_from(d, out)
    for where, sha in out:
        if len(sha) < 40:
            short.append((arc, where, sha)); continue
        # Seals record BOTH frozen blob SHAs and code-freeze COMMIT SHAs.
        # The first version asked for `<sha>^{blob}` unconditionally, so a
        # perfectly healthy commit object reported MISSING. Resolve by OBJECT
        # TYPE instead of assuming everything is a blob.
        t = subprocess.run(["git", "cat-file", "-t", sha], cwd=ROOT,
                           capture_output=True, text=True)
        kind = t.stdout.strip() if t.returncode == 0 else None
        if kind in ("blob", "commit", "tree", "tag"):
            found.append((arc, f"{where} [{kind}]", sha))
        else:
            missing.append((arc, where, sha))

# FLOOR SEMANTICS, stated so tripping it is unambiguous. 60 objects resolve
# across 6 sealed arcs today; this floor is 10. It is therefore a detector for
# ONE thing only -- THE EXTRACTOR BROKE -- and NOT a per-arc counter. Sealing a
# seventh arc raises the true count and cannot trip it; deleting five arcs' seals
# would, and should. If this fires, fix the extractor; do not raise the number.
# (Contrast the C2 verifier's arm D, where 1152 IS load-bearing for that arc and a
# legitimate new banking trips it by design.)
ASSERT_MIN_BLOBS = 10
n_checked = len(found) + len(missing)
if n_checked < ASSERT_MIN_BLOBS:
    print(f"VERIFY_FROZEN_BLOBS: FAIL — only {n_checked} SHAs extracted "
          f"(< {ASSERT_MIN_BLOBS}). The extractor is broken, and reporting PASS "
          "on zero checks is a vacuous pass, not a clean bill of health.")
    sys.exit(1)

print(f"frozen blob SHAs checked: {n_checked}"
      f"  (+{len(short)} abbreviated, not resolvable as-is)")
for arc, where, sha in found:
    print(f"  OK      {arc:12s} {sha[:12]}  {where}")
for arc, where, sha in short:
    print(f"  SHORT   {arc:12s} {sha}  {where}  (abbreviated in the seal)")
for arc, where, sha in missing:
    print(f"  MISSING {arc:12s} {str(sha)[:12]}  {where}")

if missing:
    print("\nVERIFY_FROZEN_BLOBS: FAIL — a sealed arc's frozen object is no longer "
          "in the store; the freeze cannot be re-derived from history")
    sys.exit(1)
print("\nVERIFY_FROZEN_BLOBS: PASS — every full-length frozen blob resolves")
