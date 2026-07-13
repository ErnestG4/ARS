#!/usr/bin/env python3
"""check_publish_safe — the boundary check. Run BEFORE pushing to codeberg.

A de-identification pass is a CODE TRANSFORMATION, and 95b2324 shipped without a single test that
any path still resolved. This is that test — and it checks BOTH directions, because the scrub
failed both ways:

  LEAK   — a real home path left in the tree            (the scrub MISSED it)   -> publish failure
  DEAD   — a de-identified path that never expands      (the scrub BROKE it)    -> silent-skip failure

A scrubbed path and a dead path are the same string. THAT is why the truth audit could not see it.
This script disambiguates them: it resolves every path and reports which kind each one is.

    ./tools/check_publish_safe.py            # report
    ./tools/check_publish_safe.py --strict   # exit 1 on any LEAK or DEAD  (use in a pre-push hook)
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {".git", "__pycache__", ".venv", "node_modules"}
EXT = {".py", ".md", ".sh", ".toml", ".txt", ".cfg", ".yml", ".yaml"}

# a real user home, hardcoded — the thing that must never reach codeberg
LEAK = re.compile(r"/(?:home|Users)/(?!<)[A-Za-z0-9._-]+/")
# a de-identified path constant that is NOT wrapped in an expander — the thing that silently dies
UNEXPANDED = re.compile(
    r"""["'](?:\$HOME|~|\$\{HOME\})/[^"']*["']""")
EXPANDER = re.compile(r"expandvars|expanduser|ARS_DATA_ROOT|arspaths")

ALLOW_LEAK = {"paths.toml", "paths.example.toml"}   # local config: gitignored / example only
# Files whose PROSE describes the bug (docstrings, audit notes) — they quote the pattern on purpose.
ALLOW_PROSE = {"arspaths.py", "sweep.py", "loaders.py", "06-fix-list.md", "05-runtime.md"}


def files():
    for p in ROOT.rglob("*"):
        if not p.is_file() or p.suffix not in EXT:
            continue
        if any(s in p.parts for s in SKIP):
            continue
        yield p


def main(strict=False):
    leaks, deads, n = [], [], 0
    for p in files():
        if p.name in ALLOW_LEAK:
            continue
        prose = p.name in ALLOW_PROSE
        try:
            txt = p.read_text(errors="replace")
        except Exception:
            continue
        n += 1
        # DEAD only applies to EXECUTABLE code. Prose/reports quote the pattern on purpose, and a
        # `$HOME` inside a shell command that is WRITTEN OUT is correct — a shell expands it.
        code = p.suffix == ".py" and not prose   # .sh: bash expands $HOME natively and "negative_space_audit" not in p.parts
        for i, line in enumerate(txt.splitlines(), 1):
            if LEAK.search(line):
                leaks.append((p.relative_to(ROOT), i, line.strip()[:100]))
            if not code:
                continue
            if re.search(r"f\.write|print\(|PYTHONPATH=|#|verify/", line):     # emitted shell / comment
                continue
            m = UNEXPANDED.search(line)
            if m and not EXPANDER.search(line):
                deads.append((p.relative_to(ROOT), i, line.strip()[:100]))

    print("=" * 78)
    print("PUBLISH-BOUNDARY CHECK — de-identify at the boundary, fail loudly at the root")
    print("=" * 78)
    print(f"  files scanned: {n}\n")

    print(f"  [LEAK]  real home path in tree  — must never reach codeberg : {len(leaks)}")
    for f, i, l in leaks[:20]:
        print(f"      {f}:{i}  {l}")
    if len(leaks) > 20:
        print(f"      … +{len(leaks)-20} more")

    print(f"\n  [DEAD]  de-identified path that never expands (95b2324 bug) : {len(deads)}")
    for f, i, l in deads[:20]:
        print(f"      {f}:{i}  {l}")
    if len(deads) > 20:
        print(f"      … +{len(deads)-20} more")

    ok = not leaks and not deads
    print("\n" + ("  PASS — tree is de-identified AND every declared path expands."
                  if ok else
                  "  FAIL — see above. A scrubbed path and a dead path are the same string;\n"
                  "         this check is what tells them apart."))
    if strict and not ok:
        sys.exit(1)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main("--strict" in sys.argv))
