"""Any cell that READS another cell's artifact must DECLARE its lineage.

Will, 2026-09-15: "the lineage guard being right about a case it wasn't asked is
a coverage hole, not a win. A guard invoked on request protects against the
failures you already suspect." Stage 3d's P2 compared itself to zbeta and called
it a cross-cell reproduction; the lineage guard would have refused the pair about
`protocol`, and was never asked. This row makes the asking automatic.

THE TRIGGER IS THE ACT, not the claim. A generator that `json.load`s a sibling
cell's artifact is, by that act, building on another cell -- and whatever it
then says about independence or reproduction is a lineage claim whether or not
it uses the word. So: every generator in derivflow/ that reads another
derivflow/*.json must produce an artifact carrying a `lineage` field that names
what it shares and what it does not. No field, no pass.

RATCHET, not prohibition: cells sealed before this rule existed are listed with
their reads and counted; the count may not grow. Cells sealed after it must
comply. Construction-time-over-advisory, one level up.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
READ = re.compile(r'json\.load\(\s*open\([^)]*?"([A-Za-z0-9_]+\.json)"')
CUTOFF_UNIX = 1789400000          # ~2026-09-15 05:00 local: cells sealed after this must declare
import subprocess


def added_at(path):
    """Unix time of the commit that ADDED this file — stable across checkouts.

    The first version classified pre/post-rule by file mtime, which a checkout,
    clone or touch resets. Merging the branch into main set every mtime to the
    merge time and turned all eight pre-rule cells red. A checker that passes on
    one checkout of the same tree and fails on another is not checking the tree.
    """
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=A", "--follow", "--format=%ct", "--", path],
            capture_output=True, text=True, cwd=os.path.dirname(HERE)).stdout.split()
        return int(out[-1]) if out else 0
    except Exception:
        return 0
BASELINE_PRE = 8                  # pre-rule cells that read siblings without declaring; may not grow

bad, pre, post = [], [], []
for fn in sorted(os.listdir(HERE)):
    if not fn.endswith(".py") or fn.startswith("verify_") or fn.startswith("_"):
        continue
    src = open(os.path.join(HERE, fn), encoding="utf-8").read()
    reads = sorted({m for m in READ.findall(src)
                    if m != fn[:-3] + ".json" and os.path.exists(os.path.join(HERE, m))})
    if not reads:
        continue
    own = os.path.join(HERE, fn[:-3] + ".json")
    if not os.path.exists(own):
        continue                  # generator without a banked artifact: nothing to check yet
    art = json.load(open(own))
    has = isinstance(art.get("lineage"), dict) and bool(art["lineage"])
    when = added_at(os.path.relpath(own, os.path.dirname(HERE)))
    if when == 0:
        # not yet committed: it is new by definition, so it must comply
        when = CUTOFF_UNIX
    (post if when >= CUTOFF_UNIX else pre).append((fn, reads, has))

print(f"  cells that read a sibling artifact: {len(pre) + len(post)} "
      f"({len(pre)} pre-rule, {len(post)} post-rule)")
for fn, reads, has in pre:
    print(f"    [pre ] {fn:<38} reads {len(reads):>2}  lineage: {'yes' if has else 'NO'}")
for fn, reads, has in post:
    print(f"    [post] {fn:<38} reads {len(reads):>2}  lineage: {'yes' if has else 'NO'}")
    if not has:
        bad.append(f"{fn} reads {reads} and its artifact declares no lineage — a "
                   "cell that builds on another cell must say what it shares")

undeclared_pre = sum(1 for _, _, h in pre if not h)
if undeclared_pre > BASELINE_PRE:
    bad.append(f"{undeclared_pre} pre-rule cells lack lineage (baseline {BASELINE_PRE}) "
               "— the baseline can only shrink")

if bad:
    print("VERIFY_LINEAGE_COVERAGE: FAIL")
    for b in bad:
        print("  *", b)
    sys.exit(1)
print("VERIFY_LINEAGE_COVERAGE: PASS — every post-rule cell that reads a sibling "
      "declares its lineage; the pre-rule count has not grown")
