# PHASE 35a — PRE-COMPUTE ADVERSARIAL REVIEW of rev 2 (2026-05-16)

**What this is:** an in-bounds use of "free reign" — the same adversarial-read
discipline that produced rev 1 and rev 2, applied to rev 2 *before* it costs a
compute cycle. **Not a brief revision** (design changes are Will's to
adjudicate; I did not write a rev 3). **No code, no compute, no lit-lock
execution was performed.** Brief-and-hold is intact. Each item is flagged as a
*candidate* for Will's adjudication on return, with the strongest first.

Grounding done: read `calibrator_panel.py`, `transition_calibrators_dynamical.py`
head, `transition_diagnostic.py` head, grep for resolution/renorm prior art,
`PHASE34F_G_EXECUTION_PLAN.md:347`.

---

## P1 (strongest — a verdict-map gap, a §D.0b surface). "N→∞ limit" may presuppose a limit the Fibonacci renormalization does not have.

**Rev 2 says** (§1.1, §3, §7): derive the (V,N) NNS, "isolate the finite-N
gap-stranding artifact from the N→∞ behaviour," via "a clean N→∞ extrapolation."
§7's only non-artifact outcomes are `FIB_CANTOR_NNS_SIGNATURE_DERIVED` (a
single limiting signature) or `DERIVATION_INTRACTABLE_HALT`.

**Concern.** The Fibonacci Hamiltonian's finite-volume spectra live on the
*periodic-approximant ladder* N = F_k, related by the Fibonacci **trace map**.
DGY's rigour is the *hyperbolicity* of that map on the Fricke–Vogt surface —
a self-similar dynamical iteration, **not a contraction to a fixed point**.
Critical/multifractal spectra of this lineage are characteristically
**log-periodic in the renormalization index k** (the IDS itself has
log-periodic oscillations; gap structure is scale-dependent). So the
"N→∞ behaviour" the brief wants to extrapolate to may **not be a single limit
distribution** — it may be a family *periodic in k* (period = trace-map
period), with the finite-size stranding decaying *within* each renorm period.

**Why this is the strongest item.** rev 2's §7 has **no slot for the most
likely true outcome**: "derived, but a renorm-periodic family, not a single
limit." Execution forced into that situation would have to either (a) mis-stamp
a renorm-periodic family as a single-limit signature, or (b) mis-`HALT` a
*successfully characterised* family as `DERIVATION_INTRACTABLE`. Both are
silent corruption — exactly the §D.0b surface the arc exists to avoid. This is
the same error-class as every prior rev: a thing assumed static/limiting that
is actually regime/index-indexed (§7.ter.5/22; the [[stride_decimation...]]
lesson; "well-defined operation ≠ known statistic" one level further — the
*existence of a limit* is itself the unverified assumption).

**Project-canon cross-ref that sharpens it.** `PHASE34F_G_EXECUTION_PLAN.md:347`
+ §7.ter.52 / [[bulk_vs_global_moment_readout]]: **bulk NNS is scale-invariant;
the renorm-periodic signature lives in the global-moment / number-variance
σ²(K,X) readout.** So P1 may be *good news* if handled right: the **bulk NNS**
could be the renorm-*stable* object (a clean single-limit calibrator after
all), with the log-periodicity confined to σ²(K,X). The brief currently
specifies neither readout. It must.

**Proposed direction (for adjudication, not applied):** (i) §6 lit-lock adds an
explicit determination — *does the IDS-unfolded Fibonacci NNS (and its σ²(K,X))
converge along the F_k ladder, or is it log-periodic in k?* — as a gating
question, citing Damanik/DGY. (ii) §1/§3 specify the deliverable as
**readout-resolved**: bulk-NNS (candidate single-limit calibrator) vs σ²(K,X)
(candidate renorm-periodic). (iii) §7 gains a third non-halt verdict, e.g.
`FIB_CANTOR_NNS_RENORM_PERIODIC_FAMILY_DERIVED`, so a successfully
characterised periodic family is *stampable as what it is*, not forced into
mis-stamp-or-false-halt.

## P2 (real, understated §D.0b surface). §5b is a self-consistency check; its independent teeth are only §5a.

**Rev 2 says** (§5b): step 2 — "the NNS derived from the rigorous generator is
the calibrator ground truth"; step 3 — "the empirical trace-map NNS is
validated against that derived ground truth."

**Concern.** Steps 2 and 3 both originate in the *same* Fibonacci trace-map
generator. A derivation+generator pair that is **wrong but self-consistent**
passes §5b. The only *independent* anchor is §5a (generator ↔ DGY exact
exponents) plus the *correctness of the analytic DOS→NNS derivation itself* —
not the §5b empirical match, which has no external referent.

**Proposed direction:** §5b explicitly labelled a *self-consistency* gate;
external validity rests on §5a **and** an explicit *derived analytic relation*
mapping the DGY f(α) to an independently-checkable NNS feature (small-spacing
exponent and/or a low moment), with that relation cross-checked against DGY —
not "empirical matches derived" alone. State that a self-consistent derivation
error is the residual §D.0b surface and is closed only by the f(α)→NNS-feature
relation, not by §5b.

## P3 (real; rev 2 flags the pinning as open but not its *nature*). Class II's validity boundary is exactly where it resolves AM-Cantor structure — past it, option 1's defect returns.

**Rev 2 says** (§4): Class II pinned by "an explicit analytical
small-λ/coarse-resolution condition … not by where the NNS looks AC," with
`CLASS_II_PINNING_INTRACTABLE_HALT` if unpinnable. It does not state *what the
pinning is for*.

**Concern.** Ten Martini ⇒ AM is Cantor for *all* λ≠0. Class II is rigorous
*only* in the corner where finite N has **not yet resolved** the
(exponentially-small-in-1/λ) Cantor gaps — there it is the rigorous clock +
controlled perturbation. The instant (λ,N) crosses into resolved-Cantor, the
object *is* AM-Cantor NNS — which has **no DGY-grade ground truth** (precisely
why option 1 was killed). So the pinning is not a free parameter choice: it is
"stay provably inside the un-resolved-Cantor / rigorously-clock-perturbative
region; the boundary is a hard HALT, not a soft edge." Unstated, Class II
silently re-imports the killed option-1 phantom over part of its range.

**Proposed direction:** §4 states the pinning condition explicitly as a
**gap-scale vs 1/N inequality** (Class II valid ⇔ provably sub-resolution
Cantor gaps), and that crossing it is `CLASS_II_*_HALT` (option-1 territory),
not a calibrator extension.

## P4 (concrete, code-grounded). The zoo has no representation for a parametric/indexed calibrator family.

**Code fact:** `calibrator_panel.py` — every calibrator is a fixed-N
(`N_POINTS=400`) single-realization `(name, gen_fn)` tuple; the
extractor-distinctness pairwise matrix and `transition_diagnostic` consume
those, not a parametric family. rev 2 repeatedly says "the family enters the
zoo" (§1.5, §7 `*_CALIBRATOR_STAMPED`) but a (V,N)- / k-indexed family has **no
interface**. Grep confirms no prior art — rev 2 would be the first indexed
calibrator into an all-fixed-N zoo.

**Proposed direction:** a design decision is required *before* §5/§7, not
discovered at stamp time: either (a) discretize the family into a small set of
named anchor calibrators (and P1 answers *which* — if renorm-periodic, one per
renorm-phase; plus the shared free-Laplacian anchor), or (b) extend the zoo
interface to carry a parametric family. (a) is lighter and matches the existing
fixed-N idiom; it depends on P1's resolution.

## Checked and clean (not phantoms)

- **Shared anchor.** AM λ=0 and Fibonacci V=0 are both the free discrete
  Laplacian, *and both unfold by the same arcsine IDS of [−2,2]* → genuinely
  the identical clock endpoint including the unfolding. The "diverge
  immediately above" claim is the correct content; no issue. (Confirm at
  lit-lock as routine.)
- **Operator-asymmetry-as-forced** and the **lit-lock BAR / §7.ter.48
  framing** are sound as written.

---

## The one async input that de-risks the most (not blocking)

P1 is the highest-leverage item and it is a *domain fact Will already knows*:
**does the IDS-unfolded Fibonacci NNS (and its σ²(K,X)) converge to a single
distribution along the F_k ladder, or is it log-periodic in the
renormalization index k?** A one-line answer before wipe collapses P1 from
"candidate phantom needing lit-lock" to "resolve in the brief now," and
determines P4(a)'s discretization. Everything else here can wait for normal
review. No external dataset is needed for 35a (analytic/synthetic substrate).

**State:** brief-and-hold intact; rev 2 committed (`0ee07c1`); this memo is the
only artifact; no compute performed; awaiting Will's return + explicit
compute-go.
