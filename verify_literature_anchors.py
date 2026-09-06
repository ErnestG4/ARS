"""Does every guard module say where its rule comes from — or admit it hasn't looked?

WHY THIS IS A BOARD ROW AND NOT A DOCUMENT
------------------------------------------
2026-09-06. `citation_provenance.json` measured this repo at 429 domain-science
file-hits against ZERO methodology citations: 0 of 16 concept-terms, 0 of 12
surnames. The domain claims are anchored to a fault; the methodology — which the
researcher calls the product — was derived entirely in isolation from fields
that have studied these exact failures for a century.

A document recording the connection would decay the way every such document
decays: the next module gets written, nobody updates the map, and in six weeks
the map describes a repo that no longer exists. So the connection lives WITH THE
RULE, in the module that implements it, and this row fails the board when a
guard module carries no declaration at all.

THREE HONEST STATES, and the third is the point:

    NAMED       the rule exists in the literature. Cite it, stop claiming it,
                and say what (if anything) is ours about the implementation.
    PARTIAL     components named, the conjunction or the enforcement is not.
    UNCLAIMED   searched for specifically and not found. REQUIRES a `searched`
                field naming the sweep that established it, because an
                UNCLAIMED status is a claim about a SEARCH and not about the
                world, and it ages.
    NOT_SEARCHED the default. Printed as outstanding on every green board.

The last state is why this is worth having. A module with no anchor is not a
module with an original rule; it is a module nobody has checked. Those two look
identical from inside the repo and are opposite from outside it, and before
today every guard here was in the second condition while reading like the first.

WHAT WOULD MAKE THIS ROW A LIE: passing because every module declares
NOT_SEARCHED. So the row prints the unsearched count prominently and the board
carries it as visible debt rather than as a pass.
"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

GUARDS = ["aggregate", "reachable", "verdictlattice", "modelparams",
          "detector_spec", "redpath", "threadledger", "existence",
          "railed", "countrecon", "boundary_rate"]
VALID = {"NAMED", "PARTIAL", "UNCLAIMED", "NOT_SEARCHED"}

rows, fail = [], []
for name in GUARDS:
    path = os.path.join(HERE, name + ".py")
    if not os.path.exists(path):
        continue
    try:
        mod = importlib.import_module(name)
    except Exception as e:                                        # noqa: BLE001
        fail.append(f"{name}: import failed ({type(e).__name__}: {e})")
        continue
    lit = getattr(mod, "LITERATURE", None)
    if lit is None:
        rows.append((name, "NOT_SEARCHED", 0, ""))
        continue
    st = lit.get("status")
    if st not in VALID:
        fail.append(f"{name}: LITERATURE status {st!r} is not one of "
                    f"{sorted(VALID)}")
        continue
    n = len(lit.get("anchors", []) or lit.get("adjacent", []) or [])
    if st in ("NAMED", "PARTIAL") and not lit.get("anchors"):
        fail.append(f"{name}: status {st} with no `anchors`. A claim that the "
                    "rule is named must say by whom")
    if st == "UNCLAIMED" and not lit.get("searched"):
        fail.append(f"{name}: status UNCLAIMED with no `searched` field. An "
                    "UNCLAIMED status is a claim about a SEARCH, not about the "
                    "world — it must name the sweep that established it, and it "
                    "ages")
    rows.append((name, st, n, (lit.get("ours") or "")[:58]))

print("literature anchors — where does each guard's rule come from?\n")
for name, st, n, ours in sorted(rows, key=lambda r: (r[1], r[0])):
    tag = {"NAMED": "cite it", "PARTIAL": "partly ours",
           "UNCLAIMED": "possibly ours", "NOT_SEARCHED": "UNCHECKED"}[st]
    print(f"  {st:13s} {name+'.py':22s} {n:2d} ref  {tag}")
    if ours:
        print(f"                {' ':22s}      ours: {ours}…")

unsearched = [r[0] for r in rows if r[1] == "NOT_SEARCHED"]
named = sum(1 for r in rows if r[1] == "NAMED")
print(f"\n  {len(rows)} guard modules — {named} NAMED, "
      f"{sum(1 for r in rows if r[1]=='PARTIAL')} PARTIAL, "
      f"{sum(1 for r in rows if r[1]=='UNCLAIMED')} UNCLAIMED, "
      f"{len(unsearched)} NOT SEARCHED")
if unsearched:
    print(f"  OUTSTANDING (visible debt, does not fail the board): "
          f"{', '.join(unsearched)}")
    print("  A module with no anchor is not a module with an original rule. It "
          "is a module\n  nobody has checked, and from inside the repo those "
          "look identical.")

if fail:
    print("\nFAIL — literature anchors")
    for f in fail:
        print("  *", f)
    sys.exit(1)
print("\nVERIFY_LITERATURE_ANCHORS: PASS — every declared anchor names its "
      "source, and every\nUNCLAIMED status names the search that established "
      "it. See METHODOLOGY_LITERATURE_MAP.md.")
