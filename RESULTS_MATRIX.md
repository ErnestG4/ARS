# ARS results matrix — CERTIFIED 2026-07-10

Every row byte-verified against primary source by a per-family certification pass
(five agents, each reading the full findings docs end-to-end and cross-checking every
number against the exact file it is cited from). Result: **61/61 rows CERTIFIED** on
their headline numbers; corrections and additions the pass produced are in the ledger
at the bottom.

**Cert** column: ✅ = byte-verified this pass. **Status** — banked/closed/open/
data-blocked. **Openness** — live question remaining. **ρ (reliability)** — the column
forced by Phase 38 (`TOOLKIT.md` §9 ceiling arm): any **orthogonality / independence**
claim on a **finite-sample per-unit estimate** is unverdictable until its split-half ρ
clears `R²_obs/τ`. Marginal correlations and full-sequence arithmetic estimates are not
ρ-gated — noted per row.

---

## Neural / biological — 12/12 ✅

| Substrate | Result / class | Status | Open | ρ | Cert |
|---|---|---|---|---|---|
| pvc-11 macaque V1 | H1 OSI↔ks_gue **+0.720** LOCKED **(marginal-spacing gradient, NOT a level-repulsion class)**; H2 pvc-11-specific | closed | low | H1 marginal, not gated. OSI reliability MEASURED (Allen): ρ_OSI=0.957 but **selectivity-gated** (ρ=0.97 selective / ~0 unselective); H1's selective cells reliable → not attenuation-limited; downgrade rests on PSTH-null | ✅ |
| Allen mouse V1 | H1 OSI↔ks_gue **+0.363** (12/12 +, LOCKED as marginal); F1/F0↔rep_med sign-flip ~~+0.388~~ **RE-VERIFIED 2026-07-29, STAYS LOCKED**: quoted +0.388 is unattributed (reproducible **+0.2983**); on the repaired axis pvc-11 **+0.1088 (ns)** but Allen **−0.2502 (12/12 neg)** and the between-substrate contrast holds at **4.70σ** — R-181…R-184 | closed | low | marginal; OSI ρ=0.957 selectivity-gated (not attenuation-limited at selective end); burst axis closed (ladder); OSI ≠ burst (doesn't saturate) | ✅ |
| Allen full visual hierarchy | H1 OSI↔ks_gue pooled **+0.445** (n=7846, 7 areas+LGN), **burst-orthogonal everywhere** | banked | low | marginal | ✅ **[+]** |
| Allen NP <300µm | spatial-scale-dependent; **non-monotone TR-fraction** (15.2→5.6→18.6%); local 100–300µm LEAST TR-structured; Ohiorhenuan closed | closed | low | — | ✅ |
| Buzsáki CA1 (000044) | pillar-1 generalises; pillar-2 spatial-info↔ks_gue **+0.279** | banked | low–mod | UNMEASURED | ✅ |
| CRCNS hc-3 EC/CA3/DG | EC≪CA3 = **intrinsic burst axis**, burst↔ks_gue **+0.78**, state-invariant, hc-3-specific; DG underpowered | banked | mod | UNMEASURED | ✅ |
| IBL BWM (000409) | pillar-1 generalises n=3; pillar-2 weak, contrast↔ks_gue **−0.121** (axis mismatch) | banked | mod | UNMEASURED | ✅ |
| MEC/CA1 attractor arc (000638) | attractor-topology **bounded-negative**; **MEC** spatial-info↔ks_gue **+0.43** (n=255), CA1 +0.44 | banked | mod | UNMEASURED | ✅ **[FIX +0.51→+0.43]** |
| CRCNS ret-1 retina | first feedforward; burst↔ks_gue **+0.53**; pillar-2 null (RF-quality axis mismatch) | banked | low–mod | UNMEASURED | ✅ |
| Allen-HPF | burst↔ks_gue **≈0 / −0.13** — null end of ladder | banked | low | UNMEASURED | ✅ |
| Adamatzky fungal | super-Poissonian, mass<0.3 = **0.654**, n=1470; 2.6-min peak reproduced, **14-min unresolved** | banked | mod | full-pool, n/a | ✅ |
| EEG θ-band ZCR | **FALSIFIED** — bandpass artifact (mass<0.3≈0.001) | closed | none (cautionary) | n/a | ✅ |

*Substrate-relativity ladder (burst↔ks_gue, a modality/state axis, not biology):*
hc-3 +0.78 > ret-1 +0.53 > 000638 +0.44 > V1 +0.25 > Allen-HPF ~0. **Burst-side reliability MEASURED, 4/5 rungs incl. null:** ρ_burst = 0.980 (hc-3), 0.996 (ret-1), 0.984 (V1), **0.970 (HPF null, n=4397)** — flat, saturated at ceiling, flat across rate. Reliability RULED OUT as ordering mechanism; **HPF null is STRUCTURAL not attenuation.** (000638 skipped = interpolation.) Reliability≠biology: ordering still unexplained; next confounds are depth/sorting/session-length, a different instrument. `phase38/LADDER_BURST_FINDINGS.md`.
*Also banked, not rowed:* population-stratification triad (avalanche-timing rate-independent),
CA1 cell-type axis (pyr 0.685 > int 0.575), Buzsáki cycle-2 (θ-γ locking bounded-negative;
SWR-rate consolidation enrichment 8/8), selectivity-QUALITY-vs-PREFERENCE law.

---

## Physical process — 8/8 ✅

| Substrate | Result / class | Status | Open | Cert |
|---|---|---|---|---|
| USGS M≥4.5 quakes | Poisson-clustered, **R₂(0.1)=1.808** (neighbours 0.3→1.701, 1.0→1.532), ETAS | banked (clean physical null) | low | ✅ |
| Solar X-ray flares (GOES) | Poisson-clustered (358,885 flares) | banked | low | ✅ |
| GRB 230307A QPO | **substantive FAIL** (§7.ter.32); late-prompt TR→rate-regime ρ −0.483 / −0.888 (two windows) | closed | low | ✅ |
| NANOGrav TOAs | STRUCTURAL_MISMATCH (folded-template) | closed (**§7.ter.44**) | none w/o raw TOAs | ✅ |
| Binance BTCUSDT | BL / essentially random | banked | low–mod | ✅ |
| CERN Open Data (33b) | **STRUCTURAL_MATCH_BOUNDED** (instrument-validation only) | closed (§7.ter.45) | none | ✅ |
| Single-molecule fluorescence (33c) | STRUCTURAL_MISMATCH + INSTRUMENT_VALIDATION_BOUNDED | closed (§7.ter.46) | none | ✅ |
| SOC pair (ComCat + GOES) | two substrates pass different halves of the SOC calibrator | progress-logged, **verdicts pending** | mod | ✅ |

*GRB legitimately spans §7.ter.29 (PoC) / .32 (fail) / .36 (rate-regime). SOC uses distinct,
larger catalogs (ComCat 173,122; SWPC 50,999) — not double-counting rows 1–2.*

---

## Arithmetic — settled (instrument / Katz–Sarnak validation) — 6/6 ✅

*All full-sequence exact ⇒ **ρ≈1 by construction**, not reliability-gated.*

| Substrate | Result / class | Status | Open | Cert |
|---|---|---|---|---|
| Riemann ζ zeros | GUE, KS **0.0193→0.0109** convergence (21 bins) | closed (pub figure) | none | ✅ |
| LMFDB EC L-functions | 87 curves, bulk GUE, edge separated by root number | closed | low | ✅ |
| Dirichlet L | q≤149, 630 chars, bulk GUE, γ₁ separates Sp/U (p=0.001) | closed | low | ✅ |
| Gaussian/Eisenstein prime angles | RW_SHAPE_CONFIRMED at finite X (Eisenstein 1.000±0.022 @ X=10⁸) | closed | low–mod | ✅ |
| Primes / twin primes | uniform-jitter σ̂ class (BR_artifact); σ̂=0.048 / 0.093 | banked | low | ✅ |
| Mertens / Liouville | NULL beyond support / random-walk null | closed | low | ✅ |

---

## Arithmetic — live spectral frontier — 12/12 ✅

| Substrate | Result / class | Status | Open | Cert |
|---|---|---|---|---|
| Γ₀(N) Maass squarefree (34e) | SARNAK_ANOMALY_REPLICATED, arithmetic-Poisson (6 levels) | banked | mod | ✅ ¹ |
| Level-1 Maass, 600 forms (CP1) | **even(sym0,n266) ⟨r̃⟩=0.399** Poisson, GOE excl **8.4σ**; **odd(sym1,n334) ⟨r̃⟩=0.427**, GOE excl **7.0σ** | banked | HIGH | ✅ (parity correct) |
| Low-r odd crossover (Part B) | ⟨r̃⟩=0.523, Gate-0-clean; elevated is **marginal ~2.3σ**, class unresolved | open, statistics-limited | HIGH (n≈57) | ✅ |
| Sliding-window r\* (Run 2) | **r\*≈45±5** window-stable; +2.6σ = finite-r GOE contamination, **interpretation closed** | banked | low | ✅ |
| CP2 θ∞ / GKW–CF operator | λ₁=**−0.303663** (8 sig figs); θ∞ ladder ≤4e-7; validates Session J | banked | low | ✅ |
| Mayer keystone (Run 1) | Mayer–Ruelle L_s reproduces LMFDB Maass r_n; **welds CP1↔CP2, settles parity** | banked | low | ✅ |
| n=3 vs n=5 length-degeneracy | arithmeticity split ℤ vs ℤ[φ]; s₃/s₅=2.99 PASS | banked | mod | ✅ |
| Hecke n=5 non-arith (C_nonarith) | GOE-contrast pipeline ready | DATA_ACQ_BLOCKED | HIGH | ✅ |
| Bianchi Picard + ℤ[ω] (34f) | both pipelines synthetic-validated (6/6 gates) | DATA_ACQ_BLOCKED | HIGH | ✅ |
| Cohomological Bianchi (BCGNT) | **COMPLETE** — SATO_TATE_CONSISTENT_TO_FINITE_PRIME_DEPTH; 82,373 forms; orig headline retracted | closed (bounded) | mod | ✅ |
| EC root-minus q=17 (34c) | AMBIGUOUS_AT_BOUNDARY — spike survives RMT nulls p<0.001 but q=K pooling artefact | open (methodology boundary) | mod | ✅ **[+]** |
| Part C refusal-zoo | NULL vs baseline B; re-encodes trivial descriptors | dark-appendixed | closed | ✅ |

¹ *Source-doc fix pending:* `PHASE34E_FINDINGS.md` headline still quotes Berry-Robnik
ρ≈0.458, retracted in its own SQ-2 amendment + 34f as a **fitter-bias artifact**
(corrected ρ_GOE≈0.13). The load-bearing NNS Sarnak verdict is independent of the fitter
and unaffected; the stale number should be struck from the 34e headline separately.

*(Prior "Higher-rank GL(m) L-functions (Phase 35)" row — CONFIRMED PHANTOM, deleted; no
GL(m)/Rankin–Selberg substrate exists in the repo. Phase 35 = Almost-Mathieu, below.)*

---

## Arithmetic — approximability / Diophantine arc — ✅

*Full-sequence; ρ≈1.*

| Substrate | Result / class | Status | Open | Cert |
|---|---|---|---|---|
| DEGT panels A–D | C = dim(Σ_λ)·ln λ; **H1 (C affine in 𝓛) FALSIFIED**; C finite ⟺ liminf K<∞ | complete | mod | ✅ |
| Panel C (Λ control) | **approximability Λ decisively controls DEGT dimension C** (arrangement-matched families, within-family pearson +0.80) | complete | low | ✅ **[+]** |
| Panel D (record process) | **π is the lone a.e.-typical/generic number**; metallics + e are the two measure-zero exceptions | complete | low | ✅ **[+]** |
| θ∞ = L_a/C_a metallic ladder | finite ratio DERIVED (both L_a and C_a inherit log ε_a from the shared CF-denominator indexing — Raymond's #bands=q_n theorem, V>4); the **~1.42 plateau is EXTRAPOLATION-GATED, not derived**: absent under crude λ→∞ extrapolation (θ rises 0.61/1.10/1.40/1.53), present only under the convergence-gated extrapolation (gate pre-registered 2026-05-25 on the golden DEGT theorem, 6 wk before the ladder — so not tuned to it). Fresh C_a ~10% independence check has **no power on the plateau** (band > the 1.42-vs-1.53 spread). Tier-2 weld: no weld found, wall unbreached. | banked (plateau UNRESOLVED, extrapolation-dependent) | mod | ⚠ |
| Diatonic Hamiltonian, α=log₂(3/2) | Sturmian operator; circle-of-fifths from Bellissard IDS + Pythagorean comma; **musical gate PASS**; first out-of-sample α | banked | mod | ✅ |
| a=1 substrate-universality (H/I/J) | g̃(a,f) magnitude-universal across substrates; e diverges | banked | mod | ✅ **[FIX: was mislabelled "length-degeneracy"]** |
| Thouless per-step bandwidth law | closed form W_k≈4/λ^{m_k} | banked | low | ✅ |

---

## RF / Ramanujan–Fourier lenses (rf_lenses) — ✅

| Thread | Result | Status | Cert |
|---|---|---|---|
| A — Wiener–Khinchin bridge | RF power = integer-lag autocorrelation (Gadiyar–Padma), verified; in TOOLKIT §9 | banked | ✅ |
| B — supercharacter multiplicativity | R²=1 arithmetic vs fails dynamical | banked | ✅ |
| C — F_q[T] function-field calibrator | conjecture-free Weil ground truth (not RH) | banked | ✅ |
| D — tropical→Farey q_min | q_min = Stern–Brocot min-plus envelope (100% corner-match) | banked | ✅ |
| E — asymmetric reversal | chaos rigid PROMOTABLE / crystal out-of-domain | banked | ✅ |
| **RF-multiplicativity** | **PROMOTED**, scoped {strict-coprime, a₁-normalized} (matched-SNR gate) | banked | ✅ **[+]** |
| **FF-error-rate** | **PROMOTED** genus-0, β≈0.76·log₁₀(q) | banked | ✅ **[+]** |
| Farey gaps — **NNS** | global F_Q vs Hall/BCZ `triangle_cdf`: **KS=0.00013** (7.6M gaps, ~1000× vs RMT); min τ=3/π²=0.304 hard gap | **CERTIFIED-CLASS** | ✅ |
| Farey gaps — **Σ²** | NO finite invariant: spacing variance diverges (max_τ∝Q, Var∝log Q); short-range rigid, long-range heavy-tail-clustered. "Rigidity between Poisson/GUE" **FALSIFIED** (not merely unsupported) — Farey is NOT an RMT intermediate, cannot serve as one; grep confirms the label was inert (no calibrator ever used it) | domain-boundary | ✅ |

---

## Dynamical / deterministic / testbeds — ✅

| Substrate | Result / class | Status | Open | Cert |
|---|---|---|---|---|
| GKW transfer-operator spectrum | REFUSE (deterministic, not an ensemble) | banked refusal | — | ✅ |
| Kuramoto | NO MECHANISTIC MATCH (Ph30); Ph36 two-axis re-audit reads **clustering-type/repulsion-blind** — refines, not overturns | closed | — | ✅ **[+refinement]** |
| Chialvo 2-D neuron map (36) | **NOT-REPULSION-SEPARABLE** → clustering-axis-detectable | banked | low | ✅ **[FIX label]** |
| Kaneko globally-coupled circle maps (36) | **REPULSION-AXIS-BLIND_CLASS-WIDE** / CLUSTERING-AXIS-SEPARATES-OOS | banked | low | ✅ **[FIX +CLASS-WIDE]** |
| Track 4 AM continuous front-end (36) | F1 α-confound-not-promotable; F2 floor-is-**rigidity-not-density** | closed | low | ✅ **[+]** |
| Poisson-Pivot falsification calibrator (36) | POISSON-PIVOT TAXONOMY CONFIRMED (CV-pivot two-axis) | banked | low | ✅ **[+]** |
| Almost-Mathieu (Phase 35) | AC/PP transition at λ=1; kept as fingerprint, brief-and-hold | brief-and-hold | mod | ✅ |
| Fibonacci / Sturmian chains | spectral stratification confirmed; Fibonacci at golden (D_box≈0.628) | banked | low | ✅ |
| Diatonic crystal | **domain-boundary / NO VALUE** (Σ²/L 56→0→>1000 across unfold; singular density) | banked | — | ✅ |
| Lorenz/logistic, Mackey-Glass | dynamical-systems calibrators | banked | low | ✅ |
| Dynamical-breadth panel (Rössler/Chua/Duffing/Hénon) | chaotic maps read rigid (Family-V landscape) | banked | low | ✅ **[+]** |
| Set-4 calibrator family-map (37) | repulsion axis ≈ pure signed-Poisson-distance CV; clustering axis = CV + shape | banked | low | ✅ **[+]** |
| instrument_confound | apparatus-before-substrate (dead-time fakes GUE, efficiency fakes Poisson), validated | banked module | — | ✅ |

*(FHN coherence-resonance / CR_DIP — CONFIRMED PHANTOM, deleted; grep for fitzhugh/FHN/
coherence-resonance/CR_DIP/SNIC returns zero substrate hits repo-wide.)*

---

## LLM / transformer — cautionary — ✅

| Substrate | Result / class | Status | Open | Cert |
|---|---|---|---|---|
| LLM cascade (4 archs, 8 extractors) | **FULLY RETRACTED** — no measurement attributable to model vs extractor (§7.ter.19→23); 6 claims withdrawn | closed (cautionary, w/ EEG) | none for tested extractors | ✅ |
| LLM int4 quantization (phase37 Set-3) | **route A (SUBSTRATE)** — int4 restructures surprisals toward clustering; dither-controlled (mass03 +0.0604 plain=dithered); opposite to Ph36 artefact | **banked & committed** (VERIFICATION.md + json + jsonl) | mod — the one within-extractor differential | ✅ |

---

## Methodology / reliability (Phase 38 — 2026-07-10) — ✅

431 Allen H1∩ARS cells, three per-unit axes, each with a banked split-half ρ vs τ=0.20
(true scale). `phase38/PHASE38_FINDINGS.md`.

| Axis | ρ [95% CI] | verdict |
|---|---|---|
| `p7_mean_z` @100 surr | **0.281** [0.131, 0.401] | **NO orthogonality verdict, any baseline** |
| `rep_med` | **0.921** [0.896, 0.942] | ADMISSIBLE-ORTHOGONAL vs FA-nmo; NOT-ORTHOGONAL vs raw props (R²_true=0.263) |
| `ks_gue_med` | **0.978** [0.971, 0.983] | ADMISSIBLE-ORTHOGONAL vs FA-nmo; NOT-ORTHOGONAL vs raw props (R²_true=**0.414**, strengthens H1) |

Calibrator caught shared-seed surrogate leakage (ρ=+0.257 on pure-noise cells). B4 fired
twice (cohort trim flips FA-drift verdicts). Banked 32b `rep_med`/`ks_gue_med` verdicts
remain **UNCERTIFIED** (different event set). `RESULTS.md §7.ter.50` rewrite **HELD**.
*Note: the Phase 27 (pvc-11) SUBSUMED vs Phase 38 (Allen) ORTHOGONAL readings on ks_gue_med
are **substrate-specific**, not a contradiction — Phase 27 was macaque, Phase 38 mouse.*

---

### Certification ledger (this pass, 2026-07-10)

**Errors in the prior draft that certification FIXED:**
1. Allen <300µm "non-monotone" — my prior [FIX] removed it as unsupported; that was **wrong**. `RESULTS.md:7371` states "non-monotone TR-fraction" and TR% 15.2→5.6→18.6 is a genuine V-dip. **Restored.**
2. 000638 attractor arc: EC +0.51 → **MEC +0.43** (n=255); the +0.51 was the hc-3 EC leg leaking in (`findings_log.md:1350` vs `:1478`).
3. H1 rows: "LOCKED" now carries the **marginal-spacing-gradient, NOT level-repulsion-class** qualifier (class reading downgraded — OSI↔Σ² collapses to null under PSTH unfold, 0/100 V1 cells rigid; `EPISTEMIC_STATE.md:126-136`).
4. Chialvo verdict string: NOT-SPECTRALLY-SEPARABLE → **NOT-REPULSION-SEPARABLE** (superseded label).
5. Kaneko: restored **_CLASS-WIDE** suffix.
6. Approximability a=1 row: "length-degeneracy" was a Session-K descriptor mis-imported; corrected to **g̃(a,f) substrate-universality**.
7. My earlier verbal claim that int4 was "uncommitted" — **wrong**; VERIFICATION.md + json + jsonl are committed, only raw `.log`s untracked.

**Rows ADDED by the completeness hunt [+]:** Allen full visual hierarchy H1 (n=7846);
EC root-minus q=17 AMBIGUOUS; Panel C (Λ→C); Panel D (π lone-typical); RF-multiplicativity
PROMOTED; FF-error-rate PROMOTED; Track 4 F1/F2; Poisson-Pivot calibrator; dynamical-breadth
(Rössler/Chua/Duffing/Hénon); Set-4 family-map.

**Confirmed inherited fixes (byte-verified):** quake 1.808 (not 1.95 = the EC edge γ₁);
CERN = MATCH_BOUNDED (not mismatch); Cohomological Bianchi COMPLETE (not held); GL(m) phantom
deleted; FHN phantom deleted; NANOGrav §7.ter.44; CP1 parity even=sym0=0.399; r\*=45±5.

**One source-doc fix queued (not a matrix issue):** strike the retracted BR ρ≈0.458 from
the `PHASE34E_FINDINGS.md` headline (superseded by ρ_GOE≈0.13; NNS Sarnak verdict unaffected).

**No load-bearing inter-doc contradictions** surfaced across any of the five families —
only stale labels, method-labeled dual estimates (metallic-5 C 1.099 vs 1.160), and
completeness gaps, all now reconciled.
