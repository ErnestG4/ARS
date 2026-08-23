"""Board checker for the bounded-solver census (C1).

WHAT TURNS THIS RED:
  (a) either artifact stops reproducing from its committed generator
  (b) the RAIL discriminator loses its discriminating power — the whole finding is
      that a distinct-value ratio SEPARATES an optimizer floor from a real
      concentration, so a state where every row falls the same way is the
      finding evaporating, not the check passing
  (c) the coverage caveat is quietly upgraded: `rail_fractions.json` records a
      LOWER BOUND with 250 keys unchecked, and a later edit claiming completeness
      would be the census overstating its own reach

WHY THIS DID NOT EXIST UNTIL 2026-08-23: this arc banked two artifacts and no
verifier, so nothing would have reported drift. It was checked by hand once,
during a repo-wide sweep for things needing a re-run, and both artifacts happened
to reproduce. "Happened to" is the reason a row exists now.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = sys.executable
CHECKS = []


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


rails = os.path.join(HERE, "rail_fractions.json")
redp = os.path.join(HERE, "discriminator_redpath.json")

banked_rails = json.load(open(rails))          # banked content, read before regenerating
banked_redp = json.load(open(redp))
before = sha(rails), sha(redp)

for label, script in (("rail census regenerates", "measure_rails.py"),
                      ("discriminator red-path regenerates", "discriminator_redpath.py")):
    p = subprocess.run([PY, os.path.join(HERE, script)],
                       capture_output=True, text=True, cwd=ROOT)
    CHECKS.append((label, p.returncode == 0,
                   "" if p.returncode == 0 else
                   (p.stderr.strip().splitlines() or ["(no stderr)"])[-1]))

after = sha(rails), sha(redp)
CHECKS.append(("both artifacts bit-identical", before == after,
               "" if before == after else "regenerated output differs from banked"))

# ── content: the discriminator must still DISCRIMINATE ──────────────────────
rows = banked_redp["rows"]
disc_true = [k for k, r in rows.items() if r.get("discriminator")]
disc_false = [k for k, r in rows.items() if not r.get("discriminator")]
CHECKS.append(("the discriminator fires on at least one row", bool(disc_true),
               "" if disc_true else "no row is discriminated — the separation is gone"))
CHECKS.append(("and stays silent on at least one row", bool(disc_false),
               "" if disc_false else "every row discriminated — a one-sided detector again"))

# the worked instance: an optimizer floor is 4 distinct values in 15174 near-bound
lo = rows.get("brody_q@lo", {})
_ok = lo.get("distinct") == 4 and lo.get("near") == 15174
CHECKS.append(("brody_q@lo is still the optimizer-floor case (4 distinct of 15174)", _ok,
               "" if _ok else f"got distinct={lo.get('distinct')} near={lo.get('near')}"))
_ok = lo.get("ratio", 1.0) < 0.001
CHECKS.append(("its distinct-value ratio is still ~1/n, not ~1", _ok,
               "" if _ok else f"ratio={lo.get('ratio')}"))

# ── content: coverage stays stated as a LOWER BOUND ─────────────────────────
cov = banked_rails.get("coverage", "")
_ok = "LOWER BOUND" in cov and "unchecked" in cov
CHECKS.append(("coverage is still declared a LOWER BOUND with keys unchecked", _ok,
               "" if _ok else f"coverage now reads: {cov[:80]}"))

# ── content: a railed verdict must never be silently promoted ───────────────
sites = banked_rails["sites"]
insufficient = [k for k, v in sites.items()
                if any("INSUFFICIENT_N" in str(v.get(f, "")) for f in ("verdict_lo", "verdict_hi"))]
CHECKS.append(("INSUFFICIENT_N verdicts are retained, not resolved away",
               bool(insufficient),
               "" if insufficient else
               "no INSUFFICIENT_N remains — check it was measured, not dropped"))

print("bounded-solver census (C1) verification\n")
for label, ok, why in CHECKS:
    # show the diagnostic ONLY on a failing row. Passing rows were printing their
    # own failure text -- a checker that prints a false statement on a green row
    # spends the credibility the row exists to build.
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f"   [{why}]" if why and not ok else ""))
bad = [c for c in CHECKS if not c[1]]
print(f"\n  {len(CHECKS) - len(bad)}/{len(CHECKS)} passed")
print(f"  discriminator: fires on {len(disc_true)}, silent on {len(disc_false)}")
if bad:
    print("\nVERIFY_BOUNDED_CENSUS: FAIL")
    sys.exit(1)
print("\nVERIFY_BOUNDED_CENSUS: PASS — artifacts reproduce, the distinct-value "
      "discriminator still separates both ways, and the coverage caveat stands.")
