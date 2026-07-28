"""
rep_int MIGRATION CHECKER — makes the unclassified bucket FAIL rather than DECAY.

The clip fix (R-093/R-094) added `repulsion_integral_signed` and left the biased `repulsion_integral`
in place, because hundreds of sites consume it. Will's point, and it is the sharp one: everything else
on the board is a CHOICE; an unclassified bucket with no assigned resolution is a DECAY — it becomes
permanent by default, because the default action is to do nothing.

So the default action here is a NON-ZERO EXIT. Every reference to the deprecated field is PENDING
until it is entered in the manifest with a resolution and a reason. The checker reports:

    migrated  — site now reads repulsion_integral_signed
    fine      — reviewed, clip cannot affect it (placeholder, display, None-guard)
    needs     — reviewed, clip DOES affect it, migration owed
    PENDING   — nobody has looked

RATCHET, not a permanent red light: it exits non-zero only on an INCREASE -- new sites on the
deprecated field, or any count above a high-water mark that moves DOWN only. A check that fails on
every run for as long as the backlog exists gets learned as noise and is then inert regardless of
what it reports; that is the SUPERSEDED lesson from the verify harness, one level over. Static
backlog does not fire. Regression does.

Usage:  python3 arsrh/rep_int_migration.py [--summary]
"""
from __future__ import annotations
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MANIFEST = os.path.join(HERE, "rep_int_migration_manifest.json")
p_ = lambda *a: print(*a, flush=True)

PAT = r"repulsion_integral|rep_int_q|rep_int_per_q|rep_int"

# Reviewed rulesets. A site matching MIGRATED is already on the signed field.
# The signed field in ANY of its names is the migration, not a new deprecated site. Without this,
# the checker counts its own remediation as a regression -- the instrument-is-not-its-own-witness
# family, one face further on: a tool must not score its own fix as a defect.
MIGRATED = re.compile(r"repulsion_integral_signed|rep_int_signed|_signed_q")
# Clip provably cannot matter: None placeholders, None-guards, pure display, comments.
FINE = re.compile(
    # A BACKTICK-QUOTED mention is prose in a docstring, not a call site. Added after the ratchet
    # fired on a comment in cross_substrate/axes.py explaining a DIFFERENT repair -- the tool
    # counting prose about itself, the same family as it counting its own remediation.
    r"`(repulsion_integral|rep_int\w*)`|"
    r"=\s*None\s*\)?$|is\s+not\s+None|is\s+None|^\s*#|"
    r"^\s*(print|p_)\(|\.\d+f\}|:>\d|json\.dump|columns\s*=|header|label\s*="
)
# Clip DOES matter: thresholding, ordering, correlating, or any real-vs-surrogate comparison
# (a saturated variable has near-zero variance, so correlations and percentiles are corrupted).
NEEDS = re.compile(
    r"[<>]=?|threshold|rep_int_low|rep_int_mid|quadrant|corr|rho|median|"
    r"np\.(sign|where|sort|argsort)|rank|delta|diff|"
    r"p95|p99|pct|percentile|surr|real_rep|_med\b|mean\(|std\(|abs\("
)


def sites():
    out = subprocess.run(["grep", "-rn", "--include=*.py", "-E", PAT, "."],
                         capture_output=True, text=True, cwd=ROOT).stdout
    rows = []
    for line in out.strip().split("\n"):
        if not line.strip():
            continue
        path, ln, code = line.split(":", 2)
        # Tooling is not a site (same family as above).
        if os.path.basename(path) in ("rep_int_migration.py", "commensurable.py"):
            continue
        # A regression FIXTURE that references the deprecated field is pinning its behaviour, not
        # consuming it -- excluding it is not a loophole, since the fixture's whole purpose is to
        # assert the field stays bit-identical. Third time the tooling has counted something about
        # itself (own references -> own remediation -> own prose -> own fixture).
        if path.lstrip("./").startswith("tests/"):
            continue
        rows.append((path.lstrip("./"), int(ln), code.strip()))
    return rows


_STRIP_STR = re.compile(r'("""(?:.|\n)*?"""|\'\'\'(?:.|\n)*?\'\'\'|"[^"]*"|\'[^\']*\')')


_SUBSCRIPT = re.compile(r"""(\[\s*|\.get\(\s*)(["'])(repulsion_integral\w*|rep_int\w*)\2""")


def _code_only(line):
    """The line with string literals removed. A field name surviving this appears in CODE position;
    one that does not was only ever PROSE.

    Added after the checker miscounted my own text a FOURTH time: own references -> own remediation
    -> backtick-quoted prose -> a print() of a plain string containing the word "rho", which the
    NEEDS pattern matched before FINE could be tried. Testing code-position is GENERAL where each of
    those three patches was specific."""
    # A quoted field used as a SUBSCRIPT or .get() key -- df["rep_int_q"], d.get('rep_int_q') --
    # is a genuine code site even though the name sits inside a string. Protect those BEFORE
    # stripping literals, or the fix introduces a false-negative class (over-correction: exactly
    # the failure this session keeps catching).
    line = _SUBSCRIPT.sub(lambda m: m.group(1) + "CODEKEY_" + m.group(3), line)
    return _STRIP_STR.sub("", line)


def classify(code, manifest):
    if MIGRATED.search(code):
        return "migrated"
    if not re.search(PAT, _code_only(code)):
        return "fine"
    if NEEDS.search(code) and not code.startswith("#"):
        return "needs"
    if FINE.search(code):
        return "fine"
    return "PENDING"


if __name__ == "__main__":
    man = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {"resolved": {}, "note": ""}
    rows = sites()
    cats = {"migrated": [], "fine": [], "needs": [], "PENDING": []}
    for path, ln, code in rows:
        key = f"{path}:{ln}"
        c = man["resolved"].get(key) or classify(code, man)
        cats[c if c in cats else "PENDING"].append((key, code[:80]))

    p_("=== rep_int migration status ===")
    tot = sum(len(v) for v in cats.values())
    for k in ("migrated", "fine", "needs", "PENDING"):
        p_(f"  {k:>9s}: {len(cats[k]):>4d}  ({100*len(cats[k])/max(tot,1):.0f}%)")
    p_(f"  {'TOTAL':>9s}: {tot:>4d}")

    if "--summary" not in sys.argv:
        for k in ("needs", "PENDING"):
            if cats[k]:
                p_(f"\n  {k} ({len(cats[k])}):")
                for key, code in cats[k][:12]:
                    p_(f"    {key:<52s} {code}")
                if len(cats[k]) > 12:
                    p_(f"    ... {len(cats[k])-12} more")

    # ── RATCHET, not a permanent red light ────────────────────────────────────
    # A check that fails on every run for as long as a 334-site backlog exists gets LEARNED AS
    # NOISE, and then it is inert regardless of what it reports -- someone appends `|| true` and
    # the decay resumes behind a green light. That is the SUPERSEDED lesson from the verify
    # harness, one level over: a permanently-red row is as inert as a missing one.
    #
    # So: fail on INCREASE. A static backlog does not fire; a regression does. The high-water
    # mark only ever moves DOWN, which is what makes it a ratchet rather than a rubber stamp.
    bad = len(cats["PENDING"]) + len(cats["needs"])
    hw = man.get("high_water")
    hw_p = man.get("pending_high_water")
    first = hw is None
    if first:
        hw, hw_p = bad, len(cats["PENDING"])

    p_(f"\n  open = {len(cats['needs'])} needs-signed + {len(cats['PENDING'])} unreviewed = {bad}")
    p_(f"  high-water mark: {hw} open / {hw_p} unreviewed  (moves DOWN only)")

    regress = (bad > hw) or (len(cats["PENDING"]) > hw_p)
    if regress:
        p_(f"\n  *** REGRESSION *** open {bad} > mark {hw}, or unreviewed "
           f"{len(cats['PENDING'])} > mark {hw_p}.")
        p_("  New sites were added on the deprecated field. THAT is what this check exists to catch.")
    else:
        moved = hw - bad
        if moved > 0 or first:
            man["high_water"] = bad
            man["pending_high_water"] = len(cats["PENDING"])
            json.dump(man, open(MANIFEST, "w"), indent=2)
            p_(f"  ratcheted DOWN by {moved} — mark rewritten to {bad}/{len(cats['PENDING'])}."
               if moved > 0 else "  mark initialised.")
        p_(f"\n  NO REGRESSION. {bad} open is a BACKLOG, tracked and non-increasing — not a")
        p_("  permanent red light. Bulk-marking `fine` to shrink it is called out in the manifest.")
    sys.exit(1 if regress else 0)
