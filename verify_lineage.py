"""Certify the lineage guard, and prove it refuses the case this arc actually got wrong.

A guard that has never been shown to refuse is not a guard. The refusal below is
not hypothetical: it is Stage 2a's P2 premise, which treated agreement with
Stage 1 as continuity while sharing Stage 1's entire construction.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from lineage import Lineage, SharedLineage, assert_independent, DIMENSIONS  # noqa: E402

bad = []

# The real cells, as they were actually built.
S1 = Lineage("recert_bias_surface (Stage 1)",
             construction="analytic-semicircle + bisection placement",
             data="gate-D perturbed lattice, eta sweep, n=4096",
             protocol="richardson pair via _abs_cdf_at_roots")
S2A = Lineage("recert_section_sweep (Stage 2a)",
              construction="analytic-semicircle + bisection placement",
              data="gate-D perturbed lattice, eta sweep, n=4096",
              protocol="richardson pair via _abs_cdf_at_roots")
S2B = Lineage("recert_finite_seed (Stage 2b)",
              construction="analytic-semicircle + bisection placement",
              data="gate-D lattice vs FINITE empirical reference",
              protocol="richardson pair via _abs_cdf_at_roots")
S3B = Lineage("stage3b_window_surface",
              construction="none (refit of banked science)",
              data="science per-replicate curves n=4096",
              protocol="F3 multi-start, absolute_sigma, replicate bootstrap")
S3C_LOW = Lineage("stage3c n=1024/2048 rows",
                  construction="none (refit of banked science)",
                  data="science per-replicate curves n=1024,2048",
                  protocol="F3 multi-start, absolute_sigma, replicate bootstrap")

# ---- 1. THE REFUSAL THIS ARC EARNED --------------------------------------
print("  the case this arc got wrong:")
fired, msg = False, ""
try:
    assert_independent(S1, S2A, about="construction")
except SharedLineage as e:
    fired, msg = True, str(e)
print(f"    Stage 1 vs Stage 2a, about 'construction' -> "
      f"{'REFUSED' if fired else 'ALLOWED  <-- BAD'}")
if not fired:
    bad.append("Stage 1 / Stage 2a was ALLOWED as independent about "
               "construction — the guard does not catch the case it was "
               "written for")
elif "one route reported twice" not in msg:
    bad.append("the refusal does not explain WHY; a guard that refuses without "
               "naming the reason gets overridden")

# ---- 2. IT MUST NOT OVER-REFUSE ------------------------------------------
print("\n  permitted, and it matters that these are permitted:")
for a, b, about, why in (
        (S3B, S3C_LOW, "data", "different n — genuinely independent DATA"),
        (S1, S2B, "data", "2b changed the reference; the data differ"),
        (S1, S3B, "construction", "3b builds nothing; it refits banked science")):
    try:
        assert_independent(a, b, about=about)
        print(f"    {a.cell[:28]:<28} vs {b.cell[:24]:<24} about {about!r}: OK"
              f"   ({why})")
    except SharedLineage as e:
        bad.append(f"over-refused {a.cell} vs {b.cell} about {about}: {e}")
        print(f"    {a.cell} vs {b.cell} about {about!r}: REFUSED  <-- BAD")

# ---- 3. THE DIMENSION MATTERS --------------------------------------------
# 3b and 3c share the PROTOCOL but not the DATA. They are independent evidence
# about the data and NOT about the fitter. Both directions must hold.
ok_data, ref_proto = True, False
try:
    assert_independent(S3B, S3C_LOW, about="data")
except SharedLineage:
    ok_data = False
try:
    assert_independent(S3B, S3C_LOW, about="protocol")
except SharedLineage:
    ref_proto = True
print(f"\n  3b vs 3c: independent about DATA = {ok_data}; "
      f"refused about PROTOCOL = {ref_proto}")
if not ok_data:
    bad.append("3b/3c refused about data, which they do not share")
if not ref_proto:
    bad.append("3b/3c ALLOWED about protocol, which they DO share — the "
               "`about` dimension is not being honoured, so the guard would "
               "permit citing a shared fitter as independent")

# ---- 4. NO DEFAULTS, AND A BAD DIMENSION IS REFUSED ----------------------
try:
    Lineage("x")                                   # type: ignore[call-arg]
    bad.append("Lineage constructed with missing fields — a default hides a "
               "share, which is the failure mode itself")
except TypeError:
    print("  Lineage requires every field (no defaults to omit)")
try:
    assert_independent(S1, S3B, about="vibes")
    bad.append("an unknown dimension was accepted")
except ValueError:
    print(f"  an unknown dimension is refused (valid: {', '.join(DIMENSIONS)})")

if bad:
    print("\nVERIFY_LINEAGE: FAIL")
    for b_ in bad:
        print("  *", b_)
    sys.exit(1)
print("\nVERIFY_LINEAGE: PASS — the Stage 1 / Stage 2a pair is refused by name, "
      "genuinely independent pairs are permitted, and the claim's dimension is "
      "honoured in both directions")
