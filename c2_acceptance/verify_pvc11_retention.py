"""C2 ACCEPTANCE TEST — bit-identical retention of pvc-11's bounded Brody key.
Nonzero exit on any failure. SEALED BEFORE THE WRITE IT GATES.

WHY IT EXISTS. C2 adds `I.8_brody_q_unbounded` to pvc-11.jsonl. The bounded key
`I.8_brody_q` must survive untouched, because:

  * the identical-constant record IS the evidence. "100% railed, 100% the same
    float" is a repo-grade measured claim precisely because 1,152 banked slots
    carry `6.610696135189609e-05`. Null them and the finding's provenance drops
    to "measured once in a session".
  * the other five substrates carry a bounded key, so nulling this one breaks
    the six-substrate comparability structure regardless of the values.

And the hazard is real WITHOUT being a bug: `_matched_axes` nulls
`I.8_brody_q` when `all_pass` is False, which is the fitter gate working exactly
as designed. **Policy-correct and a loss are compatible.** That is why this test
exists rather than a refusal guard in someone else's generator.

WHAT IT CHECKS, and why each arm is here:
  A. RECORD COUNT is 1159            -- catches truncation (`--limit` cut this
                                        file 1159 -> 3 once already)
  B. BOUNDED KEY PRESENT on all 1159 -- catches deletion. WITHOUT THIS, ARM C
                                        PASSES VACUOUSLY: iterating over
                                        surviving keys and checking each one
                                        succeeds trivially if the keys are gone.
                                        Presence-check-is-not-a-value-check,
                                        pointed at this acceptance test itself.
  C. EVERY VALUE BIT-IDENTICAL       -- repr() round-trip against the baseline
  D. RAIL COUNT still exactly 1152   -- the finding's own number, pinned. Note
                                        the file is NOT uniformly railed: 7
                                        cells carry genuine interior fits
                                        (0.0252 .. 0.1012).
                                        HONEST SCOPE OF ARM D: for in-place edits
                                        arm C catches everything D would, and the
                                        red-path confirmed exactly that -- D did
                                        not fire independently. D's non-redundant
                                        job is the case C STRUCTURALLY CANNOT see:
                                        C compares against the baseline file, so
                                        if the baseline is regenerated alongside
                                        the data the comparison is vacuous. D
                                        compares against a HARDCODED constant and
                                        count, so it survives baseline drift.
                                        Reported as a backstop, not as an
                                        independently-demonstrated arm.
                                        D IS ALSO A TRIPWIRE ON THE WRITE ITSELF:
                                        the count is invariant only if C2 leaves
                                        the bounded key untouched, which is the
                                        design (repaired value lands under a NEW
                                        key). So 1152 is load-bearing FOR THIS ARC
                                        and is not a universal law of the file --
                                        a future session that legitimately banks
                                        new bounded values into pvc-11 (a new
                                        substrate, a re-extraction) WILL trip D,
                                        and should re-baseline deliberately rather
                                        than edit the constant.
  E. NO NULLS                        -- the specific gate-False signature
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
# BASELINE PINNED IN THIS FILE. Arm C compares against the baseline snapshot, so
# regenerating that snapshot alongside the data makes C vacuous -- the seal would
# just move one file over. The baseline's own sha256 is therefore committed HERE,
# in the verifier, in the same motion. Changing the baseline now breaks the
# verifier loudly instead of silently re-anchoring it.
BASELINE_SHA256 = "fa44393069e160ee98ab9c064b145982c39b53ccad638077c7e3b9a48ad4d98b"
_raw = open(f"{HERE}/pvc11_bounded_baseline.json").read()
BASE = json.loads(_raw)
_recomputed = __import__("hashlib").sha256(
    json.dumps(BASE["per_cell"], sort_keys=True).encode()).hexdigest()
SRC = f"{ROOT}/{BASE['source']}"
RAIL = 6.610696135189609e-05
EXPECT_RECORDS, EXPECT_PRESENT, EXPECT_RAILED = 1159, 1159, 1152

fails = []
if _recomputed != BASELINE_SHA256:
    fails.append(f"BASELINE DRIFT: snapshot hashes {_recomputed[:16]}… but this "
                 f"verifier is pinned to {BASELINE_SHA256[:16]}… — the baseline "
                 "was regenerated, which would make arm C compare the data "
                 "against itself")

recs = [json.loads(l) for l in open(SRC)]

# A — record count
if len(recs) != EXPECT_RECORDS:
    fails.append(f"A RECORD COUNT: {len(recs)} != {EXPECT_RECORDS} — truncation "
                 "(`--limit` has done exactly this to this file before)")

cur = {r["cell_id"]: r.get("axes_computed", {}).get("I.8_brody_q") for r in recs}

# B — presence (must precede C, or C is vacuous)
present = sum(1 for v in cur.values() if v is not None)
if present != EXPECT_PRESENT:
    fails.append(f"B BOUNDED KEY PRESENT: {present} != {EXPECT_PRESENT} — the key "
                 "was deleted or nulled; arm C would pass vacuously on what remains")

# E — nulls (the gate-False signature, reported distinctly from B)
nulled = [c for c, v in cur.items() if v is None]
if nulled:
    fails.append(f"E NULLS: {len(nulled)} cells have I.8_brody_q = None — this is "
                 "the `all_pass: False` gate signature; policy-correct, and still "
                 "a loss of the banked record")

# C — bit-identical
missing, differing = [], []
for cid, want in BASE["per_cell"].items():
    if cid not in cur:
        missing.append(cid)
    elif repr(cur[cid]) != want:
        differing.append((cid, want, repr(cur[cid])))
if missing:
    fails.append(f"C MISSING CELLS: {len(missing)} baseline cell_ids absent "
                 f"(e.g. {missing[:2]})")
if differing:
    ex = differing[:2]
    fails.append(f"C VALUE DRIFT: {len(differing)} bounded values changed "
                 f"(e.g. {ex[0][0]}: {ex[0][1]} -> {ex[0][2]})")

# D — the finding's own number
railed = sum(1 for v in cur.values()
             if isinstance(v, float) and abs(v - RAIL) < 1e-18)
if railed != EXPECT_RAILED:
    fails.append(f"D RAIL COUNT: {railed} != {EXPECT_RAILED} — the '100% railed, "
                 "100% the same float' claim is pinned to this count, and 7 cells "
                 "legitimately carry interior fits")

if fails:
    print("VERIFY_PVC11_RETENTION: FAIL")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print(f"VERIFY_PVC11_RETENTION: PASS — {len(recs)} records, {present} bounded keys "
      f"present, all bit-identical, {railed} at the rail constant, 0 nulls")
