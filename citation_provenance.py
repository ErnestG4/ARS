"""Is this repo's METHODOLOGY anchored in literature the way its SCIENCE is?

COMMITTED GENERATOR of citation_provenance.json.
Predictions sealed here, before any output exists.

WHY THIS EXISTS
---------------
2026-09-06. The recurring failure this programme keeps finding is not in the
measurements. It is in the INTERPRETATION: a label that outruns its evidence, an
arm that answers a subtly different question than the decision needs, a null
returned by an instrument that cannot resolve the quantity. Twenty-seven rules in
TOOLKIT §9 and roughly fifty memory entries were derived, one at a time, from
specific failures in this repo.

Those failure modes are not new. Construct validity, the jingle and jangle
fallacies, Type III error, the experimenter's regress, epistemic iteration,
Goodhart's law, the garden of forking paths, estimand frameworks, limits of
detection — entire fields have been studying this class of error for a century.

So the question is measurable: does this repo CITE any of that, the way it cites
Berry, Brody, Sarnak and Montgomery for its domain claims? If the answer is no,
then the methodology — which the researcher calls the product — was reinvented in
isolation, and every rule is at risk of being either a rediscovery under a
private name or a genuine contribution that cannot be recognised as one because
it is not connected to anything.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                           ║
║                                                                              ║
║ P1  PREMISE — the domain probe is live: the domain-science surnames appear   ║
║     in at least 40 file-hits. If the probe finds nothing anywhere, it is     ║
║     measuring my grep and not the repo.                                      ║
║                                                                              ║
║ E1  THE ASYMMETRY IS LARGE — domain-science citation exceeds methodology     ║
║     citation by at least 20x in file-hits. This is the claim: the science    ║
║     is anchored and the methodology is not.                                  ║
║                                                                              ║
║ E2  AND IT IS NEAR-TOTAL ON THE METHODOLOGY SIDE — at most 2 of the 16       ║
║     methodology concept-terms appear anywhere in the repo. A handful of      ║
║     scattered mentions would mean the connection exists and is thin; near    ║
║     zero means it was never made.                                            ║
║                                                                              ║
║ M1  MECHANISM — it is not that the repo avoids citation. The domain side     ║
║     cites HEAVILY: at least 8 of the 12 domain surnames appear, so the       ║
║     absence on the methodology side is specific rather than a house style.   ║
╚══════════════════════════════════════════════════════════════════════════════╝

WHAT THIS DOES NOT CLAIM. Not that the rules are wrong, and not that they are
unoriginal — that is exactly what the literature search underway is for. It
measures one thing: whether the connection was ever made. A rule can be correct,
hard-won, AND already named by someone in 1955.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from redpath import redpath                                       # noqa: E402
from reachable import Bar                                         # noqa: E402
from verdictlattice import (Arm, compose, PREMISE as PRE_ROLE,    # noqa: E402
                            EXISTENCE as EX_ROLE, MECHANISM as MECH_ROLE)

DOMAIN = ["Montgomery", "Odlyzko", "Berry", "Brody", "Sarnak", "Bohigas",
          "Weil", "Khinchin", "Chowning", "Truax", "Elgindi", "Bhargava"]
METHOD_NAMES = ["Cronbach", "Goodhart", "Gelman", "Simmons", "Ioannidis",
                "Kuhn", "Duhem", "Hacking", "Meehl", "Thorndike", "Kelley",
                "Fiske"]
METHOD_TERMS = ["construct validity", "jingle", "jangle", "forking paths",
                "researcher degrees", "multiverse analysis",
                "specification curve", "Type III error",
                "experimenter's regress", "epistemic iteration",
                "theory-laden", "multitrait", "hard negative",
                "limit of detection", "ecological fallacy",
                "Simpson's paradox"]


def hits(term):
    r = subprocess.run(["grep", "-rli", term, "--include=*.md",
                        "--include=*.py", "."],
                       cwd=ROOT, capture_output=True, text=True)
    return [l for l in r.stdout.splitlines() if not l.startswith("./.git")]


dom = {t: len(hits(t)) for t in DOMAIN}
mnm = {t: len(hits(t)) for t in METHOD_NAMES}
mtm = {t: len(hits(t)) for t in METHOD_TERMS}
dom_total, mnm_total = sum(dom.values()), sum(mnm.values())
terms_present = sum(1 for v in mtm.values() if v > 0)
dom_present = sum(1 for v in dom.values() if v > 0)
ratio = dom_total / max(mnm_total, 1)

print("citation provenance — is the methodology anchored the way the science is?\n")
print(f"  {'domain-science surnames':32s} {dom_total:4d} file-hits "
      f"({dom_present}/{len(DOMAIN)} present)")
print(f"  {'methodology surnames':32s} {mnm_total:4d} file-hits "
      f"({sum(1 for v in mnm.values() if v>0)}/{len(METHOD_NAMES)} present)")
print(f"  {'methodology concept-terms':32s} {sum(mtm.values()):4d} file-hits "
      f"({terms_present}/{len(METHOD_TERMS)} present)")
print(f"\n  ratio (domain : methodology surnames) = {ratio:.0f}x\n")
print("  present on the domain side :",
      ", ".join(f"{k}({v})" for k, v in sorted(dom.items(), key=lambda x: -x[1]) if v))
print("  present on the method side :",
      ", ".join(f"{k}({v})" for k, v in {**mnm, **mtm}.items() if v) or "NONE")

n_dom, n_met = len(DOMAIN), len(METHOD_TERMS)
P1 = Bar("domain-surname file-hits", 40, floor=0, ceiling=5000,
         why="a count of files; 0 is attainable if the probe is broken and the "
             "ceiling is every markdown and python file in the tree")
E1 = Bar("domain-to-methodology citation ratio", 20.0, floor=0.0, ceiling=5000.0,
         why="a ratio of file-hit counts; 1.0 is parity and attainable, and the "
             "ceiling is the domain total against a denominator of one")
E2 = Bar("methodology concept-terms appearing anywhere", 2, direction="le",
         floor=0, ceiling=n_met,
         why=f"a count over the {n_met} probed terms; both ends attainable")
M1 = Bar("domain surnames present", 8, floor=0, ceiling=n_dom,
         why=f"a count over the {n_dom} probed surnames; this is the arm that "
             "distinguishes 'does not cite methodology' from 'does not cite'")

sP, s1 = P1.score(dom_total), E1.score(ratio)
s2, sM = E2.score(terms_present), M1.score(dom_present)
print()
for b, v, f in ((P1, dom_total, "{:.0f}"), (E1, ratio, "{:.1f}"),
                (E2, terms_present, "{:.0f}"), (M1, dom_present, "{:.0f}")):
    print("  " + b.line(v, f))

v = compose([Arm.from_bar(sP, PRE_ROLE, claim="the probe finds citations at all"),
             Arm.from_bar(s1, EX_ROLE,
                          claim="the science is anchored far more than the "
                                "methodology"),
             Arm.from_bar(s2, EX_ROLE,
                          claim="and the methodology connection was never made"),
             Arm.from_bar(sM, MECH_ROLE,
                          claim="because the absence is specific to methodology, "
                                "not a house style of not citing")],
            holds="METHODOLOGY_DERIVED_IN_ISOLATION",
            fails="METHODOLOGY_IS_LITERATURE_ANCHORED")
print(f"\nVERDICT: {v['citation']}")

with redpath("terms probed", expect_min=30) as rp:
    rp.observed(len(DOMAIN) + len(METHOD_NAMES) + len(METHOD_TERMS))

json.dump(dict(domain=dom, method_names=mnm, method_terms=mtm,
               domain_total=dom_total, method_name_total=mnm_total,
               method_term_total=sum(mtm.values()),
               ratio=ratio, terms_present=terms_present,
               domain_present=dom_present,
               bars={s["name"]: s for s in (sP, s1, s2, sM)},
               verdict=v["head"], composed=v),
          open(f"{ROOT}/citation_provenance.json", "w"), indent=1)
print("\nwritten -> citation_provenance.json")
