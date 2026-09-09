"""Re-derive the lambda-16 result and hold both the invariance and v1's miss.

  1. THE PREMISE, at the bar v2 re-specified: lam=8 must still reproduce the
     banked ladder to 1e-4 relative (bands exact). This is the arm that makes
     lam=16 a fourth point on the SAME ladder rather than a neighbouring one.
  2. THE INVARIANCE, which is the finding: all four jumps must stay inside a
     narrow band while the LEVELS stay spread. If the levels ever collapse
     together, "invariant jump across a wide level range" stops being a claim
     about anything.
  3. THE RIVAL STAYS EXCLUDED. A jump proportional to the level would give
     ~0.0373 at lam=16; the measured 0.0463 must remain further from that than
     from the banked mean. Without this the cell is four numbers that agree,
     not a test that could have failed.
  4. V1'S MISS IS PRESERVED. v1 asked for bit-equality and did not get it; that
     miss is the evidence the banked ladder is only reproducible up to BLAS
     configuration, and an artifact where it reads MET would erase it.
  5. The numerical environment is recorded, since it changes the answer.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
bad = []
v2 = json.load(open(os.path.join(HERE, "fifth_lambda16_v2.json")))
v1 = json.load(open(os.path.join(HERE, "fifth_lambda16.json")))
bank = json.load(open(os.path.join(HERE, "fifth_ladder.json")))["results"]
REL = v2.get("rel_tol", 1e-4)

# 1. premise at the re-specified bar
mine8, bank8 = v2["results"]["8.0"], bank["lam8.0"]
mism = 0
for q, row in bank8.items():
    got = mine8.get(q)
    if got is None:
        mism += 4
        continue
    for f in ("bands", "total_width", "dim_bandscaling", "dim_boxcount"):
        a, b = got[f], row[f]
        if isinstance(a, float) and isinstance(b, float) and a != a and b != b:
            continue
        if f == "bands":
            if a != b:
                mism += 1
        elif abs(a - b) > REL * max(abs(b), 1e-300):
            mism += 1
if mism:
    bad.append(f"lam=8 no longer reproduces the banked ladder at {REL:g} relative "
               f"({mism} of 36) — lam=16 would not be a point on the same ladder")

# 2. the invariance: jumps tight, levels spread
jumps, levels = {}, {}
for lab, src in (("8", bank["lam8.0"]), ("16", v2["results"]["16.0"]),
                 ("24", bank["lam24.0"]), ("32", bank["lam32.0"])):
    jumps[lab] = src["15601"]["dim_bandscaling"] - src["665"]["dim_bandscaling"]
    levels[lab] = src["15601"]["dim_bandscaling"]
jspread = max(jumps.values()) - min(jumps.values())
lspread = max(levels.values()) - min(levels.values())
if jspread > 0.005:
    bad.append(f"the jumps now span {jspread:.4f} (> 0.005) — they are no longer "
               "a narrow band and the invariance claim is gone")
if lspread < 0.05:
    bad.append(f"the LEVELS now span only {lspread:.4f} — an invariant jump "
               "across a narrow level range says nothing; the claim needs the "
               "levels to move while the jump does not")
if jspread >= lspread:
    bad.append(f"jump spread {jspread:.4f} is no longer much smaller than level "
               f"spread {lspread:.4f}, which is the whole content of the finding")

# 3. the rival stays excluded
lvl16, j8, lvl8 = levels["16"], jumps["8"], levels["8"]
rival = j8 * lvl16 / lvl8
mean_banked = sum(jumps[k] for k in ("8", "24", "32")) / 3.0
if abs(jumps["16"] - rival) <= abs(jumps["16"] - mean_banked):
    bad.append(f"the proportional rival ({rival:.4f}) now fits at least as well "
               f"as the invariant one ({mean_banked:.4f}) for the measured "
               f"{jumps['16']:.4f} — the cell no longer distinguishes them")

# 4. v1's miss is preserved
p1v1 = v1["bars"]["lam=8 mismatches vs the 36 banked ladder numbers"]
if p1v1["met"] or p1v1["value"] == 0:
    bad.append("v1's P1 now reads MET. It MISSED at 6 of 36, and that miss is "
               "the evidence that the banked ladder is reproducible only up to "
               "BLAS configuration")
if v1["verdict"] != "INVALID":
    bad.append(f"v1's head is {v1['verdict']!r}, not INVALID")

# 5. environment recorded
env = v2.get("numerical_environment") or {}
if not env.get("numpy") or not env.get("scipy"):
    bad.append("the numerical environment is not recorded, and it changes the "
               "answer in the eighth decimal")
if v2["verdict"] != "THE_23_STEP_JUMP_IS_LAMBDA_INVARIANT":
    bad.append(f"verdict is {v2['verdict']!r}")

print(f"  premise: lam=8 reproduces the banked ladder, {mism} of 36 outside "
      f"{REL:g} relative")
print("  " + "  ".join(f"lam{k}: jump {jumps[k]:+.4f} level {levels[k]:.4f}"
                       for k in ("8", "16", "24", "32")))
print(f"  jump spread {jspread:.4f} against level spread {lspread:.4f}")
print(f"  proportional rival would give {rival:.4f}; measured {jumps['16']:.4f}; "
      f"invariant mean {mean_banked:.4f}")
print(f"  v1's premise miss preserved at {p1v1['value']} of 36 (head "
      f"{v1['verdict']}); env numpy {env.get('numpy')} scipy {env.get('scipy')}")

if bad:
    print("VERIFY_FIFTH_LAMBDA16: FAIL")
    for b in bad:
        print("  *", b)
    sys.exit(1)
print("VERIFY_FIFTH_LAMBDA16: PASS — the premise holds at its re-specified bar, "
      "the jump stays invariant while the levels spread, the proportional rival "
      "stays excluded, and v1's miss is preserved")
