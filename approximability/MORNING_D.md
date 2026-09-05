# MORNING_D — Thouless #5: AMO identification + π-292 predictor resurrection

Branch `thouless-amo-identify` off `main` (merged, pushed base). `/home/combust/fmexplorer/bin/python3`,
`PYTHONPATH=…/riemann_explorer`, `BASE_SEED=20240517`. No new machinery; layer-zero inspection + lit-anchored
identification + derivation on certified data. Sparse eigensolver NOT built (still its own session).

## Layer-zero gates — all pass; gate 1 is decisive
Artifacts: `thouless_amo_gates.py/.json`.
- **GATE 1 (operator form, the load-bearing fact):** the banked diatonic/π on-site term is
  `V = λ·[(n·p mod q) ≥ q−p] = λ·χ_{[1−p/q,1)}({np/q})` — a **Sturmian STEP potential (0 or λ)**. The code itself calls
  it "a Sturmian potential." It is **NOT** the almost-Mathieu cosine `2λ·cos(2π(θ+nα))`. Printed verbatim from
  `task1_pi_depth5.potential`.
- **GATE 2 (definitions):** `λ` = the on-site step height (coeff of the 0/1 Sturmian indicator). "Measure-thinning" in
  the banked Thouless law = the **per-step total-bandwidth ratio W_{k−1}/W_k of the periodic approximants** across a
  convergent step — a property of finite approximants, **not** the Lebesgue measure of the irrational-limit spectrum.
- **GATE 3 (λ=0 anchor):** free Laplacian measure = **4.0000000000** at q=55, 89 (the fixed-bug anchor). PASS.
- **GATE 4 (count_eq_q):** band-count == q at q=7,106,113. PASS.

## Identification verdict — AMO measure law: **NEGATIVE (retired), on three independent grounds**
1. **Wrong operator** (gate 1): Sturmian step, not AMO cosine. The Jitomirskaya–Krasovsky `Leb(σ)=|4−4λ|` theorem is
   specifically for the cosine potential.
2. **No λ=1 critical collapse:** the Sturmian approximant fraction-removed `1−W/4` at q=113 is **0.623 at λ=1**, and it
   grows *monotonically through* λ=1 (0.62 → 0.75 → 0.83 at λ=1,1.5,2). The AMO law's defining feature — measure→0
   (fraction→1) at λ=1 — is **absent**. The pre-registered discriminator fails outright.
3. **Slope mismatch:** fraction-removed (0.227/0.399/0.526/0.623 at λ=0.25…1) tracks **neither λ nor λ/2**.
- **Why there is no measure law to match at all:** the Sturmian/Fibonacci Hamiltonian spectrum has **Leb(σ)=0 for all
  λ>0** in the irrational limit (Bellissard–Iochum–Scoppola–Testard / Sütő), so the finite-q measure just shrinks toward
  0 with q — there is no `|4−4λ|`-type coupling law. The `≈λ` of the Thouless law is a **per-refinement-step** bandwidth
  ratio (fixed λ, increasing q), **orthogonal** to the AMO measure-vs-coupling law. The spec's framing conflated two
  different λ-dependences.
- **Convention fork (λ vs λ/2):** moot — the operator is not AMO in either convention. (The real AMO `|4−4λ|`,
  critical-at-λ=1, IS proven and IS observed in the banked corpus — but on the **separate** cosine operator,
  `cross_substrate/am_confluence.py`, D_box→0.513 at λ=1. Different operator, different law.)
- **`≈λ` stays certified-empirical** (its own BIST+2nd-order Thouless derivation), **not** identified with a named
  measure theorem. A Sturmian-specific bandwidth-scaling identification remains open; not fabricated here.

## π-292 predictor — RESURRECTED from the certified Thouless law (not AMO)
Artifacts: `pi292_thouless_prediction.py`, **`pi292_prediction_SEALED.json`** (locked pre-registration),
`pi292_sealed_prediction.png`.

The AMO route to the predictor failed, but the deeper goal — a real finite-depth predictor to replace the dead
Liu–Wen anchor — is met by the **certified Thouless law itself** (the actual Sturmian operator's law, banked +
validated), via the homecoming-run mechanism `dim = ln q / ln(q/W)`.

**Sealed prediction (λ=8):** π (a=292) dim is **flat at depth 4→5 (≈0.680)**, then **MONOTONE RETREAT** across depths
6,7,8: **0.680 → 0.636 → 0.622 → 0.591**.
- **Mechanism:** after the giant a₄=292, the consecutive a₅,a₆,a₇=1 give Fibonacci-like convergents, so the
  older-block fractions jump to **~50% (a₆), ~33% (a₇)** — golden-regime a=1 steps that **thin W** (unlike a₅'s 0.34%
  which preserves it) — plus the a₈=2 step. Every step 6–8 thins W faster than q grows ⇒ dim retreats.
- **Robustness:** the **direction** is robust (each step `ln(thin_factor) > ln(q_growth)`, margins +0.75/+0.25/+0.65);
  **magnitudes are estimates** (the a=1 factor is interpolated from 4 banked calibration points). **Depth 7 is the
  least-certain** (smallest margin; near-flat if its a=1 factor is <1.5).
- **Falsifier (sealed):** if the future sparse-eigensolver run finds dim **rising** across 6–8, this predictor is
  falsified and π-292 is genuinely predictor-less (a 2nd null after Liu–Wen). The locked file states this.
- **This resurrects the "retreat" direction** Liu–Wen wrongly implied — now for the *correct* reason (Thouless
  older-block thinning), not the asymptotic liminf-K reason.

## Status of Thouless #5
Not the AMO measure law (identification negative), **but** #5 IS the finite-depth predictor π-292 was blocked on — it
delivers the sealed direction as its own certified law. The two π-292 gates are now both specced ahead of the dedicated
run: the sparse shift-invert eigensolver (machinery) **and** this locked derived prediction to test against.

## Banking rider — already done
The Session-C §9 record/Farey discipline ("record/Farey agreement is record-conditional, not independent joint
confirmation") was **already banked to TOOLKIT.md §9 in the prior turn (commit 9e3c743)** — confirmed present on this
branch. Not duplicated. The cross-context-contamination watch-flag stays at two sightings (concrete lru_cache signature
banked), awaiting a third.

## CF-convergence bridge (intuited) — VOID as specced, one qualitative note
The intuited "convergence rate to the law set by the CF" was conditional on the identification holding; it didn't, and
there's no limit-law to converge to (Sturmian measure is 0). Qualitative link that survives: the Thouless thinning is
CF-structured — it happens at a≥2 steps **and** large-older-block a=1 steps (π's post-292 golden run) — the **same
large-quotient structure** that set Session C's reach horizon. So measure-thinning and cusp cartography are plausibly
two reads of one CF object, but this is intuited and not tested here.

## Close
- Committed on branch; main + refsuite untouched. Carry-forward: π-292 depths 6–8 now fully specced ahead (sparse
  eigensolver + this sealed prediction → a clean execute-against-pre-registration run). Still queued: genus>0 FF
  calibrator (β≈⅓·ln q guess), Gauss/Kloosterman concentration axis, the CF-cusp divergence-profile candidate (Session C).
