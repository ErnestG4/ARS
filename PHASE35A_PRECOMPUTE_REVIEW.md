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

---

## Addendum — bounded literature reconnaissance on P1 (review input, NOT the §6 lit-lock gate)

Two web searches (abstract-level only; no deep fetch — that would be lit-lock-grade
and is gated). Result: **P1 is substantiated and upgraded.**

- **Log-periodic oscillations of the IDS are a documented, established feature
  of the Fibonacci Hamiltonian**, arising from the *discrete scale invariance
  inherent to its singular-continuous spectrum* (Lifshitz & Even-Dar Mandel;
  Jagannathan, *The Fibonacci quasicrystal*, Rev. Mod. Phys. 93, 045001 (2021),
  arXiv:2012.14744). Quantum-dynamical quantities (diffusion, conductance) show
  log-periodic oscillations on top of leading power-law behaviour; conductance
  is log-periodic in *system size* from the same discrete scale invariance.
- **Damanik–Gorodetski, "The Density of States Measure of the Weakly Coupled
  Fibonacci Hamiltonian"** (GAFA 2012): the DOS measure is exact-dimensional
  with a local scaling exponent *strictly smaller than the Hausdorff dimension
  of the spectrum* — i.e. the DGY-rigorous object the brief leans on is itself
  multifractal with nontrivial local scaling. This is the base the IDS-unfolded
  NNS is derived *on top of* (rev 2 §3 / P2).

**What this does and does not establish (kept honest).** It establishes that
*this operator has documented discrete scale invariance / log-periodicity in
its IDS and quantum dynamics* — so a single-limit NNS along the F_k ladder is
the *unlikely* case and a renorm-periodic family the *expected* one. It does
**not** establish that the log-periodicity propagates specifically to the
*IDS-unfolded NNS* (the literature documents it in IDS / conductance /
diffusion, not in the unfolded spacing distribution). Whether the IDS-unfolding
*absorbs* the log-periodicity (→ a clean single-limit bulk-NNS calibrator, the
P1 "good news" branch) or *preserves* it (→ renorm-periodic family) is itself
the underived question — a textbook instance of "well-defined operation ≠ known
statistic": the unfolding is well-defined; whether it absorbs or carries the
discrete-scale-invariance is **not known and must not be assumed either way.**

**Net effect on P1's status:** upgraded from "candidate phantom, verify at
lit-lock" to **"the briefed single-limit framing is the operator's atypical
case; §6 must make the absorb-vs-preserve determination a hard gate, and §7
must carry the renorm-periodic verdict slot, before §3 runs."** The §7
verdict-map gap (mis-stamp-or-false-HALT, §D.0b) is therefore a real exposure
on the *likely* execution path, not a tail risk. P2–P4 unchanged.

Sources: [Jagannathan, RMP 2021 (arXiv:2012.14744)](https://arxiv.org/pdf/2012.14744);
[Damanik–Gorodetski, GAFA 2012 — DOS measure of the weakly coupled Fibonacci Hamiltonian](https://link.springer.com/article/10.1007/s00039-012-0173-8);
[Observation of log-periodic oscillations in Fibonacci-quasicrystal electron dynamics (Lifshitz & Even-Dar Mandel)](https://www.academia.edu/1453982/Observation_of_log_periodic_oscillations_in_the_quantum_dynamics_of_electrons_on_the_one_dimensional_Fibonacci_quasicrystal).

---

---

## Resolution log (2026-05-16, Will engaged)

- **P1 — RESOLVED (Will): PRESERVES.** IDS-unfolding is the probability-integral
  transform → uniformizes the DOS, absorbing only *one-point-density*-carried
  log-periodicity; Fibonacci's is *renormalization*-carried (one trace-map step
  per Fibonacci level; F_k ~ φ^k ⟹ log-periodic in scale), which a one-time
  per-level scale normalization cannot remove. Class I signature = a
  **log-periodic family indexed by renormalization phase k mod L**, L = the
  trace-map cycle length DGY computes. Good news (structured finite-parameter,
  DGY-controlled). **Folded into brief rev 3** (§0/§1/§3/§5/§7 + new §5c;
  single-limit framing rejected; `FIB_CANTOR_NNS_RENORM_PHASE_FAMILY_DERIVED`
  + `CYCLE_PERIOD_MISMATCH_HALT` added, closing the §D.0b verdict-map gap).
- **P2 — substantially resolved by P1's answer.** The DGY-computed cycle period
  L is an *independent external anchor*: §5b confirms the empirical period = L,
  so a self-consistent-but-wrong derivation fails the period match. Residual:
  the per-phase member shapes still rest on the §3 derivation + §5a; the period
  match is the new independent teeth. Encoded in rev 3 §5b.
- **P3 — STILL OPEN, reserved for Will.** Class II (λ,N) pinning as a hard
  un-resolved-Cantor HALT condition (else option-1's no-ground-truth defect
  returns). rev 3 §4 states the *proposed* framing and marks Class II `_HELD`
  until Will adjudicates. Not silently resolved.
- **P4 — resolved by P1's answer.** The cycle is *finite* (L members,
  DGY-computed) ⇒ maps onto the existing fixed-N `(name, gen_fn)` zoo idiom as
  L named phase-members + the shared anchor; phase-appropriate-member
  selection. No interface extension. Encoded in rev 3 §5c. (L impractically
  large ⇒ `DERIVATION_INTRACTABLE_HALT`, not an interface problem.)

**State:** brief-and-hold intact; brief now **rev 3**; this memo is the audit
trail; **no compute performed.** Remaining gates before any compute: (1) Will's
**P3** adjudication (Class II pinning), (2) explicit **compute-go**. P1's async
question is closed (answered: preserves).
