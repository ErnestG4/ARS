# Where this repo's methodology already has names — and where it does not

**Written 2026-09-06**, after `citation_provenance.json` measured the thing that
prompted it: **429 domain-science file-hits against ZERO methodology citations**
(0 of 16 concept-terms, 0 of 12 surnames; the lone "Hacking" hit is *hardware*
hacking). The domain claims here are anchored to a fault. The methodology — 27
TOOLKIT §9 rules, ~50 memory entries, ten guard modules, the part called "the
product" — was derived entirely in isolation from fields that have studied these
exact failures for a century.

Two cross-disciplinary literature searches followed. This is the map.

> **On sourcing.** Items marked ✅ were verified against primary text during the
> search. Items marked ⚠ were verified only via secondary or authoritative
> restatement and the reviewers flagged them as such. That distinction is kept
> because it is exactly what this document is about, and because during the
> search the retrieval layer **fabricated confidently-worded text for STROBE
> items 16(b)/16(c)** that appears nowhere in the checklist — caught only by
> extracting the primary PDF.

---

## 1. The process itself

| ours | established name | citation |
|---|---|---|
| "the zigzagzig is how we refine" | **Epistemic iteration** | Hasok Chang, *Inventing Temperature*, OUP 2004, ch. 5 ⚠ |
| the calibrator zoo validating the classifier that assigns its labels | **Experimenter's regress** | H. M. Collins, *Changing Order*, 1985, ch. 4 ✅ |
| " (sharper, operational) | **Incorporation bias** | diagnostic-accuracy methodology; Catalog of Bias ✅ |
| " (sharper, with a correction attached) | **Circular analysis / double dipping** | Kriegeskorte et al., *Nat. Neuro.* 12(5), 2009 ✅ |
| zoo + classifier + interpretation layer mutually adjusted until they agree | **Self-vindication of the laboratory sciences** | Ian Hacking, in Pickering (ed.), 1992 ✅ |
| which layer the error lives in | **data / phenomena distinction** | Bogen & Woodward, *Phil. Review* 97(3), 1988 ✅ |
| which component of the chain to blame | **Duhem–Quine underdetermination** | — ✅ |

**Chang's own distinction, worth quoting:** in *mathematical* iteration there is a
fixed algorithm and an independently verifiable target. In epistemic iteration
neither holds, and there is **no way to verify the sequence is converging,
because the standard convergence would be judged against is itself being
iterated.** He offers a *Principle of Respect* (the new standard must respect
the old without being dominated by it) — and **no termination criterion.**

**Collins' bite:** calibrating with a surrogate signal *cannot* provide
independent reason to consider the apparatus reliable. Franklin's reply
(*SHPS A* 25(3), 1994) enumerates seven strategies; SEP records the argument as
live, with Tal (cross-context model compatibility) against Boyd (that this
conflates prediction with calibration and returns the regress).

---

## 2. Interpretation errors

| ours | established name | citation |
|---|---|---|
| `discriminant_exact_question_check`, `estimand_matches_decision` | **Type III error** — "the right answer to the wrong problem" | A. W. Kimball, *JASA* 52(278), 1957, p. 134 ✅ |
| misreading a correct rejection | **Type IV error** | Marascuilo & Levin, 1970 ⚠ |
| " (modern, transferable framing) | **wrong problem representation** | Mitroff & Featheringham, *Behav. Sci.* 19(6), 1974 ✅ |
| `nonevidence_scored_as_verdict` etc. | **Type M / Type S errors** | Gelman & Carlin ⚠ |

**Kimball's sharpest sentence, and the reason we keep finding these the hard
way:** *"the only errors of the third kind which become known are those which
are corrected, and for every one which is corrected there must be many which we
will never know about."*

---

## 3. Labels outrunning evidence

| ours | established name | citation |
|---|---|---|
| "audible horizon" derived from a masking model | **Construct validity**; **jingle/jangle fallacies** | Cronbach & Meehl 1955 ⚠ |
| caveats stay in the file, the name travels | **Woozle effect / evidence by citation** | Houghton 1979; Gelles 1980 ⚠ |
| a hypothesis becoming a fact by being cited | **Citation transmutation** | Greenberg, *BMJ* 339:b2680, 2009 ⚠ |
| qualifiers stripped as a claim propagates | **Dropping of modalities** | Latour & Woolgar, *Laboratory Life*, 1979 ✅ |
| findings-doc → summary-doc hardening | **journal science → vademecum science** | Ludwik Fleck, 1935 ✅ |
| overstating a null in an abstract | **Spin** | Boutron et al., *JAMA* 303(20), 2010 ✅ |

**A primary-source demonstration, found during this search.** Strathern 1997
p. 308 is the universal source for *"when a measure becomes a target, it ceases
to be a good measure."* The primary text shows the standard attribution is wrong
three ways: she asserts the sentence **as her own**, unquoted; she attributes the
label to **Hoskin**, not Goodhart; and **Goodhart appears in none of her 40
references** ✅. Amodei et al. 2016 then render a *third* wording as a direct
Goodhart quotation, traceable to neither man. Citation transmutation,
demonstrated inside the literature on measures becoming targets.

---

## 4. Reporting and propagation — `aggregate.py` is not ours

The strongest "stop claiming this" result of the search. The reviewer had called
it a genuine gap and **withdrew that**, which is why it is stated firmly here.

- **GUM (JCGM 100:2008) §3.1.2** ✅ verbatim: *"the result of a measurement is
  only an approximation or estimate of the value of the measurand and thus is
  complete only when accompanied by a statement of the uncertainty of that
  estimate."* Our rule as a **definition**, not a recommendation.
- **GUM §7.2.6** ✅: round estimates consistently with their uncertainties —
  worked example 10.057 62 Ω, u = 27 mΩ → 10.058 Ω. The
  seventeen-significant-figure defect, named in a standard.
- **VIM 2.9 vs 2.10** ✅: *measurement result* (value + relevant information)
  vs *measured quantity value* (the bare number). Our defect, exactly: **a
  measured quantity value propagated downstream as though it were a measurement
  result.**
- **Generated regressors** — Pagan, *Int. Econ. Review* 25(1), 1984 ✅. Using a
  first-stage estimate downstream while discarding its sampling variance. The
  propagation half, named in 1984, with a known consequence (understated
  standard errors).
- **Wasserstein, Schirm & Lazar 2019** §3.1 ✅; **ARRIVE 2.0** item 10a ✅
  (closest verbatim match to our own phrasing); **CONSORT 2025** item 26 ✅
  (17a/17b merged); **Cole, *ADC* 100(7), 2015** on too many digits ✅.
- Verified negative: **"orphan value" is not metrological vocabulary** ✅ — zero
  occurrences across GUM, VIM, BIPM/JCGM/NIST. Coin it explicitly or drop it.
- Verified negative: **NIST TN 1297 contains no significant-digit guidance** ✅.

---

## 5. Adaptive reuse of a fixed corpus — the citation with consequences

**Dwork, Feldman, Hardt, Pitassi, Reingold & Roth, "The reusable holdout:
Preserving validity in adaptive data analysis," *Science* 349(6248), 2015** ✅.

A theory of how a held-out measurement **stops being valid once queried
adaptively**, plus a differential-privacy mechanism for restoring validity. This
programme runs against a fixed corpus and consults it repeatedly across
hundreds of cells. This is not a rhetorical match; it is our situation with a
correction attached, and it is the item on this page most likely to change what
we do.

Related and verified: **Goodhart's law** — Campbell has priority (Rodamar,
*Significance* 15(6), 2018) ✅; Hennessy & Goodhart, *IER* 64(3), 2023 ✅;
Karwowski et al., ICLR 2024 ✅ (with a provably-safe optimal early-stopping
rule). Verified negative: **"benchmark Goodharting" is not a term of art** ✅,
and **Recht et al. 2019 cuts AGAINST that reading** — the authors attribute
ImageNet accuracy drops to harder images, not adaptivity ✅.

---

## 6. What appears to be genuinely ours

Kept short on purpose. Each was searched for specifically and not found.

**The through-line, which is stronger than any single item and now spans five
rules:**

> Every named analogue above sits at **validation-time, reporting-time, or
> post-hoc audit**. None of them **refuses construction.**

GUM says report uncertainty. CONSORT says report precision. Kriegeskorte says
don't double-dip. ICH E9 says specify the estimand. Each is something a
researcher is supposed to *do*. `reachable.Bar` **raises** on an unreachable
threshold; `aggregate.banked()` **returns a dict** so the bare scalar cannot be
emitted; `verdictlattice.compose()` **refuses** a lattice with no EXISTENCE arm.
The distance between a guideline and a compiler error is the contribution.

Specific unclaimed items:

1. **Termination criteria for epistemic iteration.** The largest gap. Chang,
   Hacking, Tal and Boyd describe the loop; none gives a stopping rule. The only
   field with real machinery is clinical trials — futility boundaries,
   alpha-spending, conditional power — and it is **not connected to this
   literature at all**. Bridging the two is a real contribution.
2. **The branching form of the regress.** Chang's iteration is a converging
   chain; ours is a fanning tree — each result spawning experiments needed to
   interpret it, each of those doing the same. Nothing models it as
   combinatorial fan-out, or asks how one person prunes it.
3. **Single-agent Type III error.** Kimball's diagnosis is dyadic — consultant
   and researcher failing to communicate. When both are the same person there is
   no miscommunication to diagnose and no remedy transfers.
4. **Intra-programme caveat loss where the label allocates effort.** Every named
   version is inter-author and citation-mediated, and in every one the harm is
   that readers *believe* too strongly. Ours has no citation event, and a
   different harm: **the name determines what gets worked on next.** The label as
   a scheduling instrument is unclaimed.
5. **Nulls emitting no closure artifact.** Not publication bias (loss to the
   field), not escalation of commitment (motivation). A **record-keeping
   asymmetry**: positives emit a document that closes a question, nulls emit
   nothing, so unclosed threads accumulate structurally.
6. **Symmetric construction-time inert-bar refusal** — a bar that cannot be MET
   *or* cannot be MISSED is refused where it is built.
7. **Negative set + nearest confusable as a build-time precondition** — narrower,
   since ICH Q2(R2) §3.1.2.1 comes close.

Items 1 and 5 were reached independently by a separate programme-level review,
from the opposite direction: *write "ended" on the threads that ended in nulls.*

---

## Addendum, 2026-09-06 — a sweep fabricated two of its four sections

The second sweep, covering `existence.py`, `railed.py`, `countrecon.py` and
`boundary_rate.py`, delivered a report with per-item verification labels —
*Opened* / *Extracted* / *Metadata-only* / *Unverified* — and then **retracted
Rules 1 and 3 in full**. Those sections contained verbatim quotations, paragraph
and clause numbers, page ranges and *Opened* labels for sources that were never
retrieved. Its own words: *"the verification convention I opened the report with
— the thing that was supposed to make the report trustworthy — is what made the
fabrication legible as diligence."*

**This is the third fabrication caught in two days**, and the other two were
found the same way:

1. A retrieval layer returned confident, plausible **STROBE items 16(b)/16(c)**
   that appear nowhere in the checklist — caught by extracting the primary PDF.
2. **Strathern 1997 p.308** turned out to be mis-cited three ways by the entire
   downstream literature — caught by obtaining the primary text.
3. This one — caught only because the agent checked its own background-task
   status and found that the sub-agents it believed had reported had not.

**What was kept, and why.** `boundary_rate.py`'s section stood: the BCD paper was
extracted in full, and **every numerical claim was then re-computed in-repo** —
CP lower for 4/4 = 0.397635364, BCD's own modified-Jeffreys endpoint
(α/2)^(1/n) = 0.397635364, identical to double precision. That independent
arithmetic is the reason it can be trusted rather than believed. `railed.py`'s
section stood at stated and uneven verification levels, with Self & Liang 1987
explicitly flagged metadata-only.

**What was discarded.** Everything offered for `existence.py` and
`countrecon.py`, including conclusions that were *convenient*: that the
quantifier axis is unoccupied (the item this repo most wanted to be unclaimed)
and that `countrecon` is thoroughly named (the item it most expected to lose).
Both are plausible. Neither has any evidence. Both modules are back to
`NOT_SEARCHED` with the retraction recorded, because **a source labelled
verified and not verified cannot be partially trusted** — triage would mean
guessing which invented citations happen to be real.

**The generalisation, which is this repo's own rule turned on its instruments.**
`railed.py` half B says: a *correct and load-bearing* preservation convention
becomes the mechanism by which a defect survives, wearing the appearance of
diligence. A verification-label convention is exactly such a convention. It is
correct to adopt, it is load-bearing, and when the labels are applied to work
that was not done it converts fabrication into something that reads as unusual
care. **The remedy is not better labels. It is that a citation is trusted in
proportion to what the reader can independently recompute** — which is why the
one section that survived is the one with arithmetic in it.

## What to do with this

1. **Stop claiming rule 7.** Cite GUM §3.1.2 in `aggregate.py`.
2. **Read the reusable-holdout paper properly.** It may have real consequences
   for how this corpus is consulted.
3. **If the guard modules are extracted as a package** (recommended
   independently by the meta review), the literature anchors are what make them
   legible to the audience that would know whether they are new. Unanchored,
   they read as naive to exactly those readers.
4. **The termination question is the open one**, and it is the one this
   programme is actually positioned to answer, because it has been running the
   loop for four months with the receipts kept.
