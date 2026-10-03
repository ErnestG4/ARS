# LIT REVIEW v2 — S (synthesis), 2026-10-02

Read-only. Sources: C.md (V-corrected), V.md, A1–A9. Citations as V verified them; UNVERIFIED-body marked. Nothing from v1 repeated. BULK_INIT_OVERLAP Amendment A1 (b42d2c3) already seats A2's items (per-run step-0 gate for 1.4B/410M, separate rows, α̂ ≤ α_wd, Kosson lines, W_O prediction, [32,64) octave separate); not re-listed.

## 1. Five items that change the plan most

**1. ARMA §6 classifies the expected outcome as an anomaly (HIGH; skeleton unsealed).**
Staats, Thamm, Rosenow 2410.17770 v3 (NeurIPS 2025) already measured the per-vector form of panel A's P_j (O_k = max_j |v_k·f_j|) on Pythia-410m: noise-level inside the MP bulk, "significantly increased overlap" at both edges including the small edge of rectangular matrices (verified; "O_k > 0.5" not verbatim). Their decile removal on Pythia-410m-deduped: Q/K/V monotone decreasing, Attention-Output ≈ flat, MLP Up/Down U-shaped (verified). Karkada, Korchinski, Nava, Wyart, Bahri 2602.15029 (submitted to ICML 2026), Cor. 2: a_n = √(2σ/(1+σ²k_n²)) — a data-kernel scale, k⁻² only for k ≫ 1/σ ("Lorentzian" is our gloss). The generic data prediction for P_j is a U-shape or a knee at a kernel scale, not a power law; "break elsewhere → anomaly" misreads it. SELF-SIMILAR must mean "exponent ≠ calibrator's". Cost: edits before the seal, 0 GPU-h.

**2. Step 0 is not always the run's init; the A0r floor is the expected size (MEDIUM; two SEALED files).**
EleutherAI/pythia issue #203 (open, 2026-07-21): pythia-160m-weight-seed1/2 step ≥ 1 checkpoints are numerically identical to the DEFAULT init at step 1 (continuity ratio 1.000), not descendants of their own step-0 upload (verified). Jordan 2304.01910 (ICLR 2024): one weight changed at init gives 7.0–7.5 % prediction disagreement vs ≈ 8.5 % for a new seed. Kwok, Altıntaş, Raffel, Rolnick 2506.13234 (ICML 2025): sensitivity confined to the first ~0.5 % of training; 10× warm-up (20 % vs 2 %) "does not eliminate barriers at initialization" (V-corrected from "10–20×"). Remaining: extend the gate to `pythia-70m-seed2` and the ten 70M reference runs (Q4EXT amendment 2) before M0s3-vs-band or any lead-8 null read; re-word row 14 — floor size expected, its 70M value ours, one pair cannot estimate its own spread. Cost: gate is CPU. Fork-perturbation runs (fork A0 at 100/500/1430/2000, one weight perturbed) give c_pair with n > 1 and test whether A2's larger misfit is a shortened-warmup chaos window; each is a partial A0 rerun — Will's budget call.

**3. Row 16 "depends on the optimizer" confounds update geometry with weight-decay geometry (MEDIUM; the one GPU buy before arm A).**
Kobayashi, Akram, von Oswald 2410.23819 (NeurIPS 2024): decoupled AdamW decay on W_KᵀW_Q is a nuclear-norm penalty, acting exponentially fast, even fully online (verified) — also the first mechanism candidate for the Q/K stable-rank collapse at 128–2000. Chen, Li, Liu 2506.15054 and Muown 2605.10797: Muon's decay is a spectral-norm constraint; σ₁ drift is row-magnitude-driven (GPT 124M–2.7B). The ceiling 0.2√max(A,B)/wd and (lr·wd)⁻¹ ≈ 10⁴-step e-fold are A6's derivation (PARTIAL). Re-word row 16 "including its weight-decay geometry". Cost: AdamW arm, attention WD = 0, A0 config, 3000 steps ≈ 7 GPU-h.

**4. The row-3 dip test is undersized; the Pythia NULL is weaker than written (MEDIUM; OLMO_PREMISE draft).**
Ameijeiras-Alonso, Crujeiras, Rodríguez-Casal 2019 (TEST 28:900–919): uniform-calibrated dip/excess-mass tests are "extremely conservative"; only their ACR is well calibrated (V: "only HY/CH/ACR" was A9's gloss). Cheng & Hall 1998 (JRSS-B 60:579–589): abstract says existing tests are "very conservative"; "asymptotic level zero" and the York 0.000/0.010/0.032/0.102 figures are UNVERIFIED-body. The OLMo positive survives; the Pythia row becomes "NULL under an undersized test". Singular values have lower support 0, so known-support ACR applies (`multimode::modetest(method="ACR", lowsup=…)`). Cost: 0 GPU; R.

**5. MF §3's core is prior art; run the published read-out before interpreting (MEDIUM; MF §6 → sealed version; lead 4).**
Staats v3 Fig. 10 (Pythia-410m block 10): overlap for every type by step 1000; Attention-Output "loses this overlap at later stages"; down-projection's smallest σ "only gain significant overlap in the later phases of pretraining" (verified; A8's "Fig. 5" was wrong). Thamm, Staats, Rosenow PRE 106, 054124 (2022): small-vector PT departure marks the rich regime. Ours, not theirs: neuron- vs residual-side asymmetry, norm-preserving null, q-shape, 5 seeds, spike reversal. Cost: O_k on the Q/K lower decile from 8k and the deepest MLP octave, 1.4B, ≈ 0.3 GPU-h; settles lead 4 directly.

## 2. Cite, don't claim

| Row / text | Citation | Remains ours |
|---|---|---|
| Memo §2 type order of stable-rank collapse; O/MLP_OUT rebound; row 15 | WeLore 2407.11239; Ndubuaku+ 2607.18363; JoMA 2310.00535 (MLP drop-and-bounce on public Pythia 70M/1.4B/6.9B); Biderman+ 2405.09673 | Dense trajectory; MLP_IN collapses without JoMA's rebound; row 15 → TYPE-DEPENDENT, as predicted |
| Memo §2 Q/K lower-decile MP departure ~8k | Staats v3: W_O "develops substantially fewer outliers … may be trained in the lazy regime" (App. D) | The ~8k onset; precision bound |
| Memo §2 σ₁ growth (Q 1.26→17.3) | Anson & Aitchison 2511.21377; Xie+ 2608.02091 (abs) | Pythia values |
| Row 8 K on rotary dims | Barbero+ 2410.06205 (both q and k, Gemma 7B); Jin+ 2502.01563 (incl. GPT-NeoX) | Per-seed trajectory; within-head rotation null; ours is per-head, not per-frequency |
| Row 16 / README flatter Muon spectra; Kimi σ₁ growth | Moonlight; Beneventano+ 2606.08388; Zhang+ 2605.09991; Ruan+ 2606.09658; K2 2507.20534 App. D (QK-Clip active first ≈ 30 % of steps) | Dense TIMING; σ₁ growth "transient, consistent with a WD ceiling" |
| Memo §2 first sink head 48k–64k | Gu+ 2410.10781 (onset 1k–2k at 60M); McClendon+ 2610.00423 (MA channels lock ~4k, Pythia-410m) | "Not commensurable"; add Gu's metric on A0/M0s1 |
| Memo §2 seeds 3/4 | PolyPythias 2503.09543 App. C: deviate "long before"; "sharp decrease in σ_λ" | Lead 6 = vector-level counterpart |
| Row 7 band outliers | Dewage+ 2608.07921 (11 endpoint models; heuristic MP split) | Nearest confusable |
| Row 9 MP exit 1000–2000; MF §3 | Staats Fig. 10, one block | Every layer, 3 sizes, 10 seeds; item 5's list |
| Row 11 / lead 7 | Staats decile removal | Lead 7 → MP-INTERIOR directions |
| Row 10 ΔW rank ↑ | Biderman+; ReLoRA 2307.05695; InRank 2306.11250; Karkada+ 2502.09863 | Equal-interval constant-LR ΔW with seeds; Diehl Martinez+ 2410.11451's gradient-PER is a different object |
| Rows 5/6 OV before QK | Li 2607.06621 (Pythia-410m and 160m, 22 ckpts each; Ginibre null; snap by step 1000); Chen & Luo 2510.06954 | Add beside Olsson/Tigges |

## 3. Contradictions, by severity

1. HIGH, internal — README leads 1–2 still say "multimodality that fades … 92 at the final checkpoint"; row 3 withdrew the fade; HF LFS oids (main c52e4ac8/5f807625 vs ingredient3-step23852 6d259b6a/f4274551; all branches differ) confirm `main` ≠ lineage. Re-word today.
2. HIGH, design — ARMA §6 (item 1).
3. MEDIUM — Row 16 WD geometry (item 3).
4. MEDIUM, sealed → amendment — Q4EXT item 3 "M0s3 varies the INIT only" (item 2).
5. MEDIUM — Row 3 dip size (item 4).
6. MEDIUM — ARMA §3 "3 = 1 × 2": Dauphin, Agarwala, Mobahi 2401.10809 (Hessian = GN + NME); Meterez+ 2607.21716 (150M LM: tail exponent ≈ 0.96 GN vs ≈ 0.65 full H; negative eigenvalues in mlp.up). Holds for GN only; antithetic costs can be negative in MLP_IN bands.
7. MEDIUM, draft — PDYN A1 single τ_v = 1/(1−β₁): Fong & Yang 2608.20638 (gradient reversal at EoS, GPT-2 medium) → lag-1 velocity autocorrelation negative in the spike band, positive in the bulk; Bai+ 2506.04805, Regis & Chewi 2605.06821: β₁, β₂ distinct. Muon τ_v = 20 reproduces only 27/48.
8. LOW–MED — MF §2 negative Q/K [32,64) cells: Alt, Erdős, Krüger 1606.07353 delocalises the null's bulk vectors only under flatness (A) s_ik ≤ s*/(p+n) and (F2) s_ik ≥ φ/(n+p) (verified); the spike (−5…−13) and first octave violate them. Label null-INAPPLICABLE.
9. LOW, wording — Wang+ 2211.06506 Cor. 5.3 is bulk-spectrum only, GD under Thm 5.2's step-size bound; never licenses "bulk invariant ⇒ reservoir" under Adam.
10. LOW — OLMO T5: OLMo 2 (2501.00656) excludes embeddings from WD; read stage-1 WD groups before quoting e^{−50}.

## 4. Ranked tests (C's order; V changes none)

| # | Test | Cost | Settles |
|---|---|---|---|
| 1 | BULK_INIT_OVERLAP (sealed + A1) | 0 GPU; hours CPU | Whether H_RES needs the co-adapted calibrator (arm A ≈ tens of GPU-h); MP law vs init instance via W_O |
| 2 | Staats O_k on Q/K lower decile from 8k + deepest MLP octave, 1.4B | ≈ 0.3 GPU-h | Lead 4; MF §3 read-out |
| 3 | Writer-row projection: banked 4k→5k ΔW onto `attention.dense` / `mlp.dense_4h_to_h` MA writer rows vs random rows, planted control | ≈ 0.2 GPU-h | A named mechanism (McClendon+) for lead 3 |
| 4 | SiZer (Chaudhuri & Marron 1999, JASA 94:807) on banked Arm B and Pythia curves | 0 | Whether ~2k turning points exist at coarse scale, with a scale-indexed error bar; replaces the NOT LICENSED detector |
| 5 | WD-decoupled AdamW arm | ≈ 7 GPU-h | Row 16 confound; Q/K-collapse mechanism |
| 6 | Curvature-defined fourth Q1 map (preconditioned-sharpness HVPs, banked 70M) | 1–2 GPU-h | Post hoc; readable only on MLP_OUT; defer until fork runs give a second floor |
| 7 | OLMo early-training paired floor (`OLMo-2-0425-1B-early-training` overlaps the official repo at 0/10k/20k/30k; "not identical to the original run") | 0 | Prerequisite for any OLMo trajectory claim |
| — | Pre-spike IPR early-warning | 0 | Drop: n = 2 spikes, already seen (seed 4 +8.4 at 96k). Report beside PolyPythias σ_λ |

## 5. Design changes by document (sealed → AMENDMENT)

**Arm A skeleton (edits)**
- §0: run test #1 first; its word funds §4. H_KNEE split architectural (d_head) vs data-kernel scale.
- §1: probe sets real / order-shuffled / Zipf+LRD (Montemurro & Degli Esposti 2603.02213); context length as a knob (Yang+ 2604.05536); mid checkpoint at a Li+ 2509.23024 phase boundary.
- §2: allow negative antithetic costs; bank (3 − 1×2). Split-half reproducible rank k* beside CV² (Thomas 2607.05872: k* ≈ 39/128).
- §3: calibrator P_j on its own post-fine-tune activations (Nakamuta & Teramae 2608.15239).
- §4: name the primary calibrator — Haar-within-subspace vs rainbow resample (Guth+ 2305.18512).
- §5: plant α = 1+α_SAE ≈ 1.6–1.7 (Michaud, Gorton, McGrath 2509.02565: −0.74 at 16k / −0.57 at 32k); hierarchical-kernel plant (Nava & Wyart 2605.23821); order-2 clone null (Rende+ 2410.19637).
- §6: add U-shape and Lorentzian; minimum-octaves on MP-interior octaves only; pool within type only (Ormaniec+ 2410.10986).
- Prior art: Staats decile shapes recorded before the seal.

**Arm B, MF §6 → sealed version (edits)**
- Null licence: record max/min row- and column-norm²; bands where the null leaves Haar = INAPPLICABLE.
- τ(q): declare fractal / multifractal (size sweep) / few-vector shapes; RP line as confusable (Kravtsov+ 2015; Kutlin & Khaymovich 2024).
- One heavy-tail-preserving null (Aggarwal, Lopatto, Marcinek 2002.09355).
- §3(a): pairwise cosines of supported neurons (Gurnee+ 2401.12181: antipodal pairs cos −0.886).
- §5: compare to "Gaussian with the null's profile", not PT (Benigni 2020; Marcinek & Yau 2022).
- Read-out: O_k beside IPR, against Staats Fig. 10 / Thamm 2022.
- Optimiser: localisation predicted AdamW-specific (Park+ 2506.19697: kurtosis 0.04 vs 1818.56 at 1.4B; Singh 2608.05136). 70M UNREAD until Will names it.

**PDYN A1 (draft)**
- τ_v per band from measured update autocorrelation, or single-τ_v declared as the tested assumption; two scales β₁, β₂.
- Reference family: DBM-for-weights as SGD-white-noise prior (Aarts+ 2407.16427/2411.13512; Olsen, Fatehmanesh, Xiao, Kumarappan, Gajula 2507.12709; Park, Lucini, Aarts 2509.01349); A1 adds OU-momentum.
- P4: v_rms ∝ √(lr/B); check the (lr·wd)⁻¹ ≈ 10⁴-step stationarity premise.
- Header: "what had been seen when this was written" (Hofman+ 2311.18807); pilot/banked arms = calibration–confirmation split (Jankowsky+ NHB 10 Sep 2026).
- M4 off until the off/off control; head/bulk step profile as target (Wu+ 2608.25990).

**OLMO_PREMISE (draft)**
- T1/T4: calibrated ACR beside the dip. §4: (weight, separation, skew) power grid + right-skewed-unimodal FPR cell (Freeman & Dale 2013; βs UNVERIFIED-body).
- §1: diff the three `OLMo2-1B-stage2-seed*.yaml` before "seed replicates" (HF card: ingredients 1–2 "exploratory runs").
- T5: read stage-1 WD groups. T3: gain ≈ 0 ⇔ dead-row 2×2 (Li 2606.04405).
- §6: trajectory prereg seals the early-training paired floor first.

**BULK_INIT_OVERLAP (SEALED → AMENDMENT A2)**: W_O's MP-KS beside ρ_bulk(O); known answer at Kosson's equilibrium (αW₀ + isotropic update, rms √(η/2λ)) to red-path MIXED/LEARNED; continuity gate extended to the ten 70M reference runs and `pythia-70m-seed2`.

**Q4EXT (SEALED → AMENDMENT 2)**: WD ceiling and e-fold marker on σ₁ (PARTIAL); per-head σ₁(W_Q^h W_K^hᵀ); stable rank of W−W₀ (Kang+ 2602.06385: incremental growth under AdamW, none under Muon); seed2 gate; row 16 at n = 2 as a reference-band statement vs the 10 AdamW seed runs.

**ARMB lead 8**: max |d|/SD, exceedance count, max adjacent-checkpoint cluster mass; null by circular block bootstrap over checkpoints of the 10 reference runs (Meinshausen+ 2011; Romano & Wolf 2005, block-bootstrap sentence UNVERIFIED-body; Blanchard, Neuvial, Roquain 2020 `sanssouci`); planted-departure red path; timing never from cell-wise or cluster tests.

**README**: leads 1–2 re-worded to row 3's text.

## 6. What the literature does NOT contain

- Any trained BULK's overlap with its own step-0 instance (ρ_bulk, E_init). Published work tests the LAW or whole-matrix cosines (Lopardo+ 2603.26663: Pythia-1B embeddings end at 0.32 / 0.21).
- ΔW stable-rank trajectories on PolyPythias, or any < 1k-step update-rank trajectory at 70M–1B.
- Band-wise perturbation vs a co-adapted calibrator; value- vs direction-perturbation; dose² linearity; antithetic pairs; cost curves along a trajectory beyond Staats' one block.
- A derivation from sequence self-similarity (Hurst ≈ 0.7, MI decay, 5/3 spectrum) to a per-matrix ‖v_kᵀX‖² profile — unlicensed in both directions.
- Post-spike singular-VECTOR statistics.
- MP-exit timing across every layer, three sizes, ten seeds; per-seed rotary-pair trajectory with a within-head rotation null; dense timing of Muon-vs-AdamW collapse.
- OU-momentum velocity in the DBM-for-weights family (all SGD per abstracts); pdyn is the first spacing/velocity test under Adam/Muon.
- W_Q σ₁ trajectory under QK-norm; any public statement of what OLMo-2 1B `main` is.
- Function carried by MP-INTERIOR bulk directions (edges and top directions are published).

## 7. V's corrections to the agents

1. A7: Li 2607.06621 = Pythia-410m and 160m (22 checkpoints each), not 410m/1.4B.
2. A8/A2: Staats trajectory is Fig. 10, not Fig. 5. "Closer to random initialization, mainly affected by regularization" and the rich/lazy 20 % MLP control are v1/v2 text only; v3 says W_O "develops substantially fewer outliers … may be trained in the lazy regime". Pin the version.
3. A8: Michaud, Gorton, McGrath exponents are −0.74 (16k) / −0.57 (32k); widths were swapped.
4. A3: Kwok+ tested 10× warm-up, which "does not eliminate barriers at initialization".
5. A3: Granziol & Juarev 2602.00816 — cosine 0.311 is Qwen-0.6B, 0.004 is DeepSeek-1.3B; negative outliers are the 120B model; Pythia appears only in precision/subsampling studies. HessFormer 2505.11564 abstract names DeepSeek-70B only.
6. A2: Wang+ 2211.06506 Cor. 5.3 holds under Thm 5.2's step-size bound, not "η = Θ(1)".
7. A4: Karkada+ 2602.15029 "submitted to ICML 2026", not accepted.
8. A9 UNVERIFIED-body: Cheng & Hall level-zero and York table; Freeman & Dale β −.44/−.59; Romano & Wolf's Lahiri sentence; NOT's "fit lands between kinks". Glosses: Rousselet 2025 — "onset is a second-order property" is A9's reading; Ameijeiras-Alonso — only ACR well calibrated.
9. Carried PARTIALs: Chen–Li–Liu radius; Sign Lock-In 2602.17063 1B from-scratch UNVERIFIED; Biroli & Tarzia μ-range UNVERIFIED; Huang+ 2602.00969 exponent UNVERIFIED. The 54 "n" rows were not re-fetched.
