"""Board checker for the B1-B4 overnight (brocot re-run, key census, extraction).

ONE ARTIFACT IS DELIBERATELY NOT CHECKED FOR BIT-IDENTITY
---------------------------------------------------------
`b3_keys.json` is a census of THIS REPO'S OWN KEY SPACE. It changes whenever the
repo gains an artifact, so asserting bit-identity would make this row go red on
every unrelated commit — a permanently-red row, which this repo has recorded as
worth nothing. Measured 2026-08-23: the file had drifted from 2882 to 2920
distinct keys purely because the C3 arc's own outputs (`n_sites`, `CAPTURED`,
`line`, `inputs_differing`) entered the census.

So the row asserts the SUBSTANTIVE invariant instead: `BOUNDED_FIT` stayed at 69
across that drift, and the sealed prediction (`predicted_max_bounded_fit`) is
unchanged. Generic buckets may grow; the bounded-fit population may not move
without someone noticing.

Distinguishing "the subject changed" from "the measurement changed" is the whole
job of this row, and it is the reason bit-identity is the wrong tool for exactly
one of these three artifacts.
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


b1b2, b3, b4 = (os.path.join(HERE, f) for f in
                ("b1_b2_results.json", "b3_keys.json", "b4_extraction.json"))
banked_b1b2, banked_b3, banked_b4 = (json.load(open(p)) for p in (b1b2, b3, b4))
before = sha(b1b2), sha(b4)                    # b3 deliberately excluded
b3_before = sha(b3)

for label, script in (("B1/B2 brocot regenerates", "run_b1_b2_brocot.py"),
                      ("B4 extraction regenerates", "run_b4_extraction.py")):
    p = subprocess.run([PY, os.path.join(HERE, script)],
                       capture_output=True, text=True, cwd=ROOT)
    CHECKS.append((label, p.returncode == 0,
                   "" if p.returncode == 0 else
                   (p.stderr.strip().splitlines() or ["(no stderr)"])[-1]))

after = sha(b1b2), sha(b4)
CHECKS.append(("B1/B2 and B4 bit-identical", before == after,
               "" if before == after else "regenerated output differs from banked"))
CHECKS.append(("b3_keys left untouched by this row", sha(b3) == b3_before,
               "b3_keys was rewritten; this row must not regenerate it"))

# ── B1/B2 content: the corrected brocot findings ────────────────────────────
B1, B2 = banked_b1b2["B1"], banked_b1b2["B2"]
CHECKS.append((f"B1 population is the full n={banked_b1b2['n']}, no selection",
               banked_b1b2["n"] == 255, f"n={banked_b1b2['n']}"))
CHECKS.append(("B1 metallic ordering is still perfect (rho = -1)",
               abs(B1["rho"] + 1.0) < 1e-9, f"rho={B1['rho']}"))
med = B1["medians_metallic"]
order = [med[k] for k in ("golden", "silver", "bronze", "metallic4", "metallic5")]
CHECKS.append(("and the medians are still monotone decreasing",
               all(a > b for a, b in zip(order, order[1:])), f"medians={order}"))
CHECKS.append(("B2 full-population rho is still positive",
               B2["rho_full"] > 0, f"rho_full={B2['rho_full']}"))
CHECKS.append(("B2 top-tercile CI still excludes zero",
               B2["ci"][0] > 0, f"ci={B2['ci']}"))

# ── B3 content: the invariant, not the bytes ────────────────────────────────
counts = banked_b3["counts"]
CHECKS.append(("B3 BOUNDED_FIT population is still 69", counts.get("BOUNDED_FIT") == 69,
               f"BOUNDED_FIT={counts.get('BOUNDED_FIT')}"))
CHECKS.append(("B3 sealed prediction is unchanged",
               banked_b3.get("predicted_max_bounded_fit") == 15,
               f"predicted={banked_b3.get('predicted_max_bounded_fit')}"))

# ── B4 content: the case-insensitivity repair must hold ─────────────────────
# universality.py was originally MISSED by an uppercase-only matcher and emitted
# NEEDS_JUDGMENT for a tooling reason. Its presence here is the red-path of that bug.
b4rows = banked_b4["rows"]
CHECKS.append(("B4 still reaches universality.py (the uppercase-matcher bug)",
               any("universality" in k for k in b4rows),
               f"rows={sorted(b4rows)}"))
CHECKS.append(("B4 gives every row a verdict, none silent",
               all(r.get("verdict") for r in b4rows.values()),
               "a row has no verdict"))

print("B1-B4 overnight verification\n")
for label, ok, why in CHECKS:
    # show the diagnostic ONLY on a failing row. Passing rows were printing their
    # own failure text -- a checker that prints a false statement on a green row
    # spends the credibility the row exists to build.
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f"   [{why}]" if why and not ok else ""))
bad = [c for c in CHECKS if not c[1]]
print(f"\n  {len(CHECKS) - len(bad)}/{len(CHECKS)} passed")
print(f"  note: b3_keys.json is a census of the repo's own key space and drifts by "
      f"design (2882 -> 2920 keys as of 2026-08-23); its INVARIANT is checked, not its bytes")
if bad:
    print("\nVERIFY_OVERNIGHT_B: FAIL")
    sys.exit(1)
print("\nVERIFY_OVERNIGHT_B: PASS — B1/B2 and B4 reproduce, brocot's corrected "
      "findings stand, and B3's bounded-fit invariant survives repo drift.")
