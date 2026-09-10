"""Check that every number in the LaTeX paper traces to a committed source.

The .tex is a TRANSCRIPTION of PROSE.md (plus NOTE.md's appendices), and a
transcription's characteristic failure is silent: a digit changes, or a line is
dropped, and nothing downstream notices because prose has no arithmetic to
re-derive.  So this checker treats the numerals themselves as the checkable
content.

What it protects, in order:

  1. NO INVENTED NUMBER.  Every numeral in the body of paper.tex must occur in
     PROSE.md or NOTE.md, or be RE-DERIVED HERE from a committed artifact.  The
     .tex adds one footnote and one parenthetical that postdate the prose draft
     (the correlated-error study); those numbers are recomputed from
     zbeta_correlated_error.json at check time rather than allowlisted as
     strings, so editing the artifact breaks this row.
  2. NO DROPPED NUMBER.  Every numeral in PROSE.md must appear in paper.tex,
     except tokens listed with a reason below -- draft management, and the
     citations dropped when section 5 was de-linked from the glass literature.
     This is the arm that catches a paragraph lost in conversion.
  3. STRUCTURE.  Every PROSE section heading has a sectioning command in the
     .tex, and every \\includegraphics target exists on disk.

What it does NOT check: that each number is attached to the same QUANTITY in
both documents.  Numerals are compared as a multiset of strings, so a
transposition between two sentences passes.  That is a real gap and is stated
rather than papered over; the defence against it is that both documents are
read by a human before submission.

Formatting numerals (font sizes, margins, figure widths) are excluded by
stripping the preamble and \\includegraphics options -- they are typography, not
claims, and allowlisting them individually would slowly become a place to hide
a real number.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DFLOW = os.path.dirname(HERE)
bad = []

tex_raw = open(os.path.join(HERE, "paper.tex")).read()
prose = open(os.path.join(HERE, "PROSE.md")).read()
note = open(os.path.join(HERE, "NOTE.md")).read()

# --- body only: the preamble is typography, not claims -----------------------
if "\\begin{document}" not in tex_raw:
    bad.append("paper.tex has no \\begin{document}")
    tex_body = tex_raw
else:
    tex_body = tex_raw.split("\\begin{document}", 1)[1]

NUM = re.compile(r"\d+(?:\.\d+)?(?:e-?\d+)?")


def numerals(text):
    text = re.sub(r"\\includegraphics\[[^\]]*\]", " \\\\includegraphics ", text)
    text = re.sub(r"\\[a-zA-Z]+\*?", " ", text)
    for ch in "{}$":
        text = text.replace(ch, " ")
    return set(NUM.findall(text))


# --- numbers the .tex adds, re-derived from the artifact ---------------------
z = json.load(open(os.path.join(DFLOW, "zbeta_correlated_error.json")))
gls = z["z"]["gls_sweep"]
c4 = z["bars"]["max |z_gls - z_boot| / z_boot over the shrinkage sweep"]
n80 = z["bars"]["recovered-vs-banked mismatches (80 numbers)"]
derived = {
    "%.2f" % z["z"]["bootstrap"],            # 8.24, footnote in section 4
    "%.2f" % min(gls),                       # 9.97   \
    "%.2f" % max(gls),                       # 11.12  / the GLS sweep's range
    "%.2f" % z["z"]["sealed_recomputed"],    # 9.31
    "%.3f" % z["ratios"]["gue"],             # 0.735  tightens
    "%.3f" % z["ratios"]["iid"],             # 1.363  loosens
    "%d" % n80["ceiling"],                   # 80 numbers recovered
    "%d" % round(c4["value"] * 100),         # 35% disagreement
    "%d" % round(c4["thresh"] * 100),        # against the 25% ceiling
}
if n80["value"] != 0:
    bad.append("the recovery premise no longer reads 0 mismatches; the "
               "footnote's 'reproduced the banked artifact exactly' is stale")
if c4["met"]:
    bad.append("C4 now reads MET; the .tex footnote says the stability bar was "
               "MISSED, so one of the two is wrong")

# --- numerals PROSE carries that the paper deliberately does not --------------
# Two classes, each entry named with its reason.  This list is the ONLY way a
# numeral may go missing, so adding to it is a deliberate, reviewable act; a
# conversion that silently dropped a paragraph would still fail the row.
DRAFT_ONLY = {
    "1.0": "the prose draft's own version marker (v1.0)",
    "19": "the draft header's target submission date, 2026-08-19, now past",
}
# 2026-09-09, on Will's instruction to "back off of any claims of linkage and
# only point out facts": section 5 no longer places this system's stretched
# exponential inside the glass-relaxation literature's open question, so the
# bibliographic numerals of the works cited ONLY to make that linkage are gone
# with it.  The measurements they sat beside are all still in the paper -- what
# was removed is the claim of kinship, not a result.
DELINKED = {
    "51": "Ediger, Annu. Rev. Phys. Chem. 51", "2000": "Ediger, year",
    "99": "Ediger, page", "14": "Richert, J. Phys. Condens. Matter 14",
    "2002": "Richert, year", "703": "Richert, page R703",
    "243": "Sillescu, J. Non-Cryst. Solids 243", "1999": "Sillescu, year",
    "81": "Sillescu, page", "93": "Widmer-Cooper et al., PRL 93",
    "2004": "Widmer-Cooper et al., year",
    "135701": "Widmer-Cooper et al., article number",
    "2011.00579": "arXiv preprint on KWW origins",
}
EXCLUDED = {**DRAFT_ONLY, **DELINKED}

tex_nums = numerals(tex_body)
src_nums = numerals(prose) | numerals(note)

invented = sorted(tex_nums - src_nums - derived, key=lambda s: (len(s), s))
if invented:
    bad.append("numerals in paper.tex with no source and no derivation: "
               + ", ".join(invented))

dropped = sorted(numerals(prose) - tex_nums - set(EXCLUDED),
                 key=lambda s: (len(s), s))
if dropped:
    bad.append("numerals in PROSE.md missing from paper.tex: "
               + ", ".join(dropped))

for tok, why in EXCLUDED.items():
    if tok in tex_nums:
        bad.append(f"{tok!r} is in paper.tex but was excluded as {why}")

# --- structure ---------------------------------------------------------------
heads = re.findall(r"^#{2,3} (.+)$", prose, re.M)
tex_heads = re.findall(r"\\(?:section|subsection)\*?\{([^}]*)\}", tex_body)
tex_heads_l = [h.lower() for h in tex_heads] + (
    ["abstract"] if "\\begin{abstract}" in tex_body else [])
for h in heads:
    key = re.sub(r"^(?:\d+\.|Appendix [A-Z]\s*[-—]?)\s*", "", h).strip().lower()
    if not any(key in t for t in tex_heads_l):
        bad.append(f"PROSE heading {h!r} has no matching section in paper.tex")

figs = re.findall(r"\\includegraphics\[[^\]]*\]\{([^}]*)\}", tex_body)
if not figs:
    bad.append("no \\includegraphics in paper.tex — the figures were dropped")
for f in figs:
    if not os.path.exists(os.path.join(HERE, f)):
        bad.append(f"figure {f} does not exist")

print(f"  numerals: {len(tex_nums)} in the paper, "
      f"{len(tex_nums & src_nums)} traced to PROSE/NOTE, "
      f"{len(tex_nums & derived)} re-derived from zbeta_correlated_error.json")
print(f"  sections: {len(heads)} PROSE headings, {len(tex_heads)} in the .tex; "
      f"figures: {len(figs)} included, all present")
print(f"  the C4 miss the footnote reports still reads MISSED at "
      f"{c4['value']:.4f} vs {c4['thresh']}")

if bad:
    print("VERIFY_PAPER_NUMBERS: FAIL")
    for b in bad:
        print("  *", b)
    sys.exit(1)
print("VERIFY_PAPER_NUMBERS: PASS — no invented numeral, no dropped numeral, "
      "every section and figure carried over")
