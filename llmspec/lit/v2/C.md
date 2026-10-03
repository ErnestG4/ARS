# LIT REVIEW v2 — C (critic), 2026-10-02

Read-only. V's corrections applied: Staats 2410.17770 pinned to v3 (the "closer to random initialization" sentence is v2-only; v3: W_O "develops substantially fewer outliers … may be trained in the lazy regime", App. D; trajectory = Fig. 10); Li 2607.06621 = Pythia-410m and 160m; Michaud–Gorton–McGrath −0.74 (16k) / −0.57 (32k); Kwok = 10× warm-up, "does not eliminate"; Cheng & Hall and Freeman & Dale body numbers UNVERIFIED, used at abstract level only.

## 1. Cite, don't claim

**A. Already published (same object, same or sibling substrate).**

| Row / text | Prior art | New wording |
|---|---|---|
| Memo §2 "Stable rank collapses for Q/K/O/MLP_OUT 128–2000; V later; O/MLP_OUT rebound" | WeLore 2407.11239 (Q/K/O/gate low-rank fast, V/up/down high-rank; LLaMA-130M); Ndubuaku+ 2607.18363 ("Q/K crystallize early, content matrices accumulate rank slowly"); JoMA 2310.00535 (MLP stable-rank drop-and-bounce **on public Pythia 70M/1.4B/6.9B checkpoints**) | "The type ordering is the published pattern (WeLore; Ndubuaku+). JoMA reports an MLP drop-and-bounce on these checkpoints; our MLP_IN collapses without rebound — the discrepancy to carry." |
| Row 15 "INCONCLUSIVE; Q/K 5–7× lower-rank, V/O/MLP not" | WeLore; Biderman+ 2405.09673 (MLP ΔW higher-rank than attention, 7B) | "TYPE-DEPENDENT, as predicted; the all-type sealed bar asked a question the field answers per type." |
| Memo §2 "Lower-decile MP departure in Q/K from ~8k" | Staats+ v3: Q/V/MLP leave MP at **both** ends at the endpoint; W_O stays MP-like | "Endpoint fact published; the ~8k onset and the precision bound are ours." |
| Memo §2 "σ₁ grows throughout (Q 1.26→17.3)" | Anson & Aitchison 2511.21377 (abs); Xie+ 2608.02091 | "Known direction; Pythia values are ours." |
| Row 8 K on rotary dims | Barbero+ 2410.06205 (lowest frequencies get higher norm in **both** q and k, Gemma 7B); Jin+ 2502.01563 (Q and K low-frequency RoPE dims incl. GPT-NeoX, "gradually formed through training") | "Endpoint fact published for Q and K; the per-seed trajectory and within-head rotation null are new. Our statistic is per-head, not per-frequency." |
| Row 16 / README "Flatter Muon spectra (Moonlight)" | Add Beneventano+ 2606.08388 (Muon preserves stable rank; theory flows to equal σ); Zhang+ 2605.09991 (GPT-2 AdamW outlier-heavy vs Muon concentrated); Ruan+ 2606.09658 | "Endpoint: Moonlight; Beneventano+; Zhang+; Ruan+. The dense-trajectory TIMING is new." Same citations on PDYN §2 P3. |
| Row 16 "Kimi K2 reports σ₁ growth … under Muon" | K2 2507.20534 App. D: QK-Clip active only in the first ≈30 % of steps; Muown 2605.10797: drift = row magnitude | "…a **transient** σ₁ growth, consistent with a WD ceiling." |
| Memo §2 "First sink head 48k–64k" | Gu+ 2410.10781 (onset 1k–2k in 60M; WD sets rate); McClendon+ 2610.00423 (MA channels lock by ~4k on Pythia-410m) | Keep "not commensurable"; add Gu's metric on A0/M0s1 (CPU). |
| Row 14 A0r floor | Jordan 2304.01910 (one-weight change at init ≈ new seed); Kwok+ 2506.13234 (sensitivity in the first ~0.5 %) | "The floor's size is expected (Jordan; Kwok+); its value for 70M spectral curves is ours; one pair cannot estimate its own spread." |
| Memo §2 seeds 3/4 | PolyPythias 2503.09543 App. C: spike runs deviate "long before", transitions "driven by a sharp decrease in σ_λ" | "PolyPythias already reads a pre-spike weight-spectrum signature; lead 6 is its vector-level counterpart." |
| Row 7 | Dewage+ 2608.07921 (K/O band outliers on persistent residual dims; heuristic MP split) | Cite as nearest confusable. |

**B. Endpoint / one block only; our trajectory, seed or null version is new.**

| Row / text | Prior art | New wording |
|---|---|---|
| Row 9 MP exit 1000–2000 | Staats+ Fig. 10 (Pythia-410m **block 10**): overlap for every type by step 1000; W_O loses it later | "The step-1000 departure is in Staats+ 2025 for one block; ours is every layer, 3 sizes, 10 seeds." |
| MF_EXPLORE §3 deepest MLP octave | Staats+ Fig. 10: down-projection's smallest σ "only gain significant overlap in the later phases"; Thamm+ 2022 (rich regime) | "Prior art at endpoint + one block. New: side asymmetry, norm-preserving null, 5 seeds, q-shape, spike reversal." |
| Row 11 / lead 7 | Staats+ decile-removal on Pythia-410m-deduped: Q/K/V ↓, O ≈ flat, MLP U-shaped | Lead 7 → "Function at the small EDGE of MLP is published; untested is the MP-INTERIOR bulk's directions." |
| Row 10 ΔW rank ↑ | Biderman+ (Δ rank "increases when trained on more data"); ReLoRA 2307.05695; InRank 2306.11250; Karkada+ 2502.09863 (theory) | "Coarse versions published; equal-interval constant-LR ΔW with seeds is new. Diehl Martinez+ 2410.11451's falling gradient-PER on Pythia is a different object (one-batch gradient)." |
| Rows 5/6 | Li 2607.06621 (Pythia-410m/160m, Ginibre null, prev-token heads snap by step 1000, "consolidated after function"); Chen & Luo 2510.06954 (theory: projections condense before key-query) | Add beside Olsson/Tigges; Chen & Luo as the OV-before-QK theory direction. |

## 2. Contradicted

1. **README open leads 1–2 (HIGH, internal).** Still say "multimodality that fades … sub-floor after mid-training" and "92 at the final checkpoint"; memo row 3 withdrew the fade and HF oids (A7) confirm `main` ≠ lineage. Re-word today.
2. **Row 16 "depends on the optimizer" (MEDIUM).** Kobayashi+ 2410.23819 (AdamW decay on W_KᵀW_Q = fast nuclear-norm penalty) vs Chen–Li–Liu 2506.15054 / Muown (Muon decay = spectral-norm constraint): the contrast confounds update geometry with WD geometry. Re-word "including its weight-decay geometry"; re-test (§3 #5).
3. **Q4EXT item 3 "M0s3 varies the INIT only" (MEDIUM; sealed → amendment).** pythia issue #203: some PolyPythias step-0 uploads are not the run's init. Gate `pythia-70m-seed2` and the ten 70M reference runs on ‖W₁−W₀‖/‖W₀‖ ≈ 1e-5 before M0s3-vs-band or any lead-8 null read.
4. **Row 3 dip-test size (MEDIUM).** Cheng & Hall 1998; Ameijeiras-Alonso+ 2019: uniform-calibrated dip/excess-mass are "very/extremely conservative". The OLMo positive survives (stronger); the Pythia NULL is weaker than written → "NULL under an undersized test"; add calibrated ACR in OLMO_PREMISE T1/T4.
5. **ARMA §6 verdict table (HIGH, design).** Staats+ O_k: noise-level inside MP, elevated at both edges → P_j predicted U-shaped; Karkada+ 2602.15029 Cor. 2 (submitted ICML 2026): a_n² ∝ 1/(1+σ²k²) → a data-kernel scale is the generic prediction. "Break elsewhere → anomaly" misclassifies the expected outcome.
6. **ARMA §3 "3 = 1 × 2" (MEDIUM).** Dauphin+ 2401.10809 (Hessian = GN + NME, NME large while learning features); Meterez+ 2607.21716 (150M LM: tail GN ≠ H; negative eigenvalues in mlp.up). Holds for the GN part only; antithetic costs can be negative in MLP_IN bands.
7. **PDYN A1 single τ_v = 1/(1−β₁) (MEDIUM, draft).** Fong & Yang 2608.20638: gradient reversal at EoS (GPT-2 medium) → lag-1 velocity autocorrelation negative in the spike band, positive in the bulk; Bai+ 2506.04805, Regis & Chewi 2605.06821: β₁ and β₂ are distinct scales. Muon τ_v = 20 already reproduces only 27/48.
8. **MF §2 negative Q/K [32,64) cells read as "less concentrated than the null" (LOW–MED).** Alt–Erdős–Krüger 1606.07353: the null is delocalised by theorem only under flatness (A) and (F2); the spike and first octave violate them (MF §6 −5…−13). Label null-INAPPLICABLE.
9. **BULK_INIT_OVERLAP reading (LOW, wording).** Wang+ 2211.06506 Cor. 5.3 is GD at small constant LR, spectrum only (V #6): it never licenses "bulk invariant ⇒ reservoir" under Adam.
10. **OLMO_PREMISE T5 (LOW).** OLMo 2 (2501.00656) excludes embeddings from WD; read the stage-1 WD groups before quoting e^{−50}.

## 3. Tests ranked by value per GPU-hour

| # | Test | Cost | Settles |
|---|---|---|---|
| 1 | **BULK_INIT_OVERLAP** (sealed + A1) | 0 GPU-h; hours CPU | Whether H_RES needs the co-adapted calibrator (arm A ≈ tens of GPU-h); MP law vs init instance via W_O |
| 2 | **Staats O_k on the Q/K lower decile from 8k** (+ MLP deepest octave), 1.4B | ≈ 0.3 GPU-h (probe forward pass per checkpoint) | Lead 4: alignment vs precision; MF §3's functional read-out |
| 3 | **Writer-row projection, lead 3** (banked 4k→5k ΔW onto `attention.dense` / `mlp.dense_4h_to_h` MA writer rows vs random rows; planted control) | ≈ 0.2 GPU-h | A named mechanism (McClendon+) for an unexplained row |
| 4 | **SiZer** on banked Arm B and Pythia curves | 0 | Whether the ~2k turning points exist at coarse scale, with a scale-indexed error bar; replaces the NOT LICENSED detector (rows 13–14) |
| 5 | **WD-decoupled AdamW arm** (attention WD = 0, A0 config, 3000 steps) | ≈ 7 GPU-h | Row 16's confound and the Q/K-collapse mechanism; the one GPU buy before arm A |
| 6 | Curvature-defined fourth Q1 map (preconditioned-sharpness HVPs, banked 70M ckpts) | 1–2 GPU-h | Readable only on MLP_OUT (O sits at the paired floor) and chosen after seeing A2 — post hoc. Defer until fork-perturbation runs give a second floor |
| 7 | OLMo early-training paired floor (10k/20k/30k overlap) | 0 | Prerequisite for any OLMo trajectory claim; run when the trajectory is un-held |
| — | Pre-spike IPR early-warning | 0 | **Drop as a test**: n = 2 spikes, already seen (seed 4 +8.4 at 96k). Report beside PolyPythias σ_λ |

## 4. Design changes before sealing (section → change → source)

**Arm A (skeleton; edits)**
- §0 → run #1 first; its word decides whether §4 is funded → A2.
- §0 H_KNEE → split architectural (d_head) vs data-kernel scale → Karkada (A4).
- §1 X → real / order-shuffled / Zipf+LRD probe sets; context length as a knob → Montemurro 2603.02213; Yang 2604.05536 (A4).
- §1 checkpoints → mid checkpoint at a Li+ 2509.23024 phase boundary → A4.
- §2 regime → allow negative antithetic costs; bank (3 − 1×2) → Dauphin; Meterez (A3).
- §2 D → split-half reproducible-rank k* beside CV² → Thomas 2607.05872 (A1).
- §3 → calibrator P_j on its own post-fine-tune activations → Nakamuta & Teramae 2608.15239 (A8).
- §4 → name primary: Haar-within-subspace vs rainbow resample → Guth+ 2305.18512 (A8).
- §5 → α = 1+α_SAE ≈ 1.6–1.7; add hierarchical-kernel plant; name order-2 clone null → Michaud+; Nava & Wyart 2605.23821; Rende+ 2410.19637 (A4/A8).
- §6 → add U-shape and Lorentzian; minimum-octaves on MP-interior octaves; pool within type only → Staats; Ormaniec 2410.10986 (A3/A4/A8).
- Prior art → Staats decile shapes recorded before the seal → A8.

**Arm B (MF §6 → sealed version; edits)**
- Null licence → row/col-norm² flatness; bands where the null leaves Haar = INAPPLICABLE → Alt–Erdős–Krüger (A5).
- τ(q) → fractal / multifractal / few-vector shapes, RP line as confusable → Kravtsov 2015; Kutlin–Khaymovich 2024 (A5).
- Nulls → heavy-tail-preserving null → Aggarwal+ 2002.09355 (A5).
- §3(a) → pairwise cosines of supported neurons → Gurnee+ 2401.12181 (A5).
- §5 → "Gaussian with the null's profile", not PT → Benigni 2020; Marcinek–Yau 2022 (A5).
- Read-out → O_k beside IPR; position against Staats Fig. 10 / Thamm 2022 → A4/A5.
- Optimiser → localisation predicted AdamW-specific; 70M UNREAD until Will names it → Elhage 2023; Park 2506.19697; Singh 2608.05136 (A6).

**PDYN A1 (draft; edits)**
- A1.1 → τ_v per band from measured update autocorrelation, or single-τ_v declared as the tested assumption → Fong & Yang (A3).
- A1.1 → two time scales (β₁, β₂) → Bai; Regis & Chewi (A3).
- Reference → DBM-for-weights family as the SGD-white-noise prior; A1 adds OU-momentum → Aarts 2407.16427/2411.13512; Olsen 2507.12709; Park 2509.01349 (A6).
- P4 → v_rms ∝ √(lr/B) prediction; check the (lr·wd)⁻¹ ≈ 10⁴ stationarity premise → A6; Kosson.
- Header → "what had been seen when this was written" → Hofman+ 2311.18807 (A9).
- M4 → off until the off/off control; head/bulk step profile as its target → Wu+ 2608.25990 (A6).

**OLMO_PREMISE (draft; edits)**
- T1/T4 → calibrated ACR excess-mass (lower support 0) beside the dip → Ameijeiras-Alonso 2019 / `multimode` (A9).
- §4 → (weight, separation, skew) power grid + right-skewed-unimodal FPR cell → Freeman & Dale 2013 (A9).
- §1 → diff `OLMo2-1B-stage2-seed*.yaml` before "seed replicates" → A7.
- T5 → read stage-1 WD groups → OLMo 2 paper (A7).
- T3 → gain≈0 ⇔ dead-row 2×2 → Li 2606.04405 (A7).
- §6 → trajectory prereg seals the early-training paired floor first → A7.

**BULK_INIT_OVERLAP (SEALED → amendments)**
- W_O's MP-KS at the same checkpoint beside ρ_bulk(O) → Staats (A2).
- Known answer at Kosson's equilibrium (αW₀ + isotropic update at rms √(η/2λ)) to red-path the MIXED/LEARNED boundary → A2.
- Continuity gate extended to the ten 70M reference runs and `pythia-70m-seed2` → issue #203 (also a **Q4EXT amendment**).

**Q4EXT (SEALED → amendment 2)**: WD ceiling 0.2√max(A,B)/wd and (lr·wd)⁻¹ e-fold marker on σ₁ (A6, derivation PARTIAL); per-head σ₁(W_Q^h W_K^hᵀ) (Kimi K2); stable rank of W−W₀ (Kang+ 2602.06385); seed2 gate.

**README** → leads 1–2 re-worded to row 3's current text.
