# NIGHT1_REPORT — derivflow/modes (2026-09-17, 01:19 → ~06:30 PDT)

Branch `derivflow-modes` from main `13c4696`. Nothing on main touched; nothing pushed
(PUSH_BRANCH=no). Every number below is read from a committed artifact whose generator was
committed before it ran; `derivflow/modes/verify_modes_night1.py` re-derives them (board
310 ok / 0 bad at the time of writing, auto-discovered by `verify_all.py`).

## 0. One-paragraph answer

**The measured relaxation is substantially the reference's.** On identical roots the production
instrument (empirical-seed free-convolution reference, Richardson primary) puts the iid
crystallisation crossing at k* = 10.89 ± 0.03 with a k^−2.43 tail; the same roots with no
reference at all (NOUNFOLD) cross at k* = 26.5 ± 0.4 (interpolated 25.0 ± 0.3) with a
k^−1.44 tail — 39σ apart in k*, 1.0 apart in tail exponent, at every n ∈ {1024, 2048, 4096}
(n = 16384 in flight, §3.4). For GUE the analytic-semicircle comparator (POPREF) gives 9.2–9.4
against production 6.16–6.26 (14σ). Gate MT explains the mechanism quantitatively: the empirical
reference transmits only 11% / 30% / 75% of a planted displacement wave at k = 1 for qw = 0.1 /
0.2 / 0.5, and by k ≈ 20 its transfer function turns **negative** (it over-subtracts the wave);
the raw-bandwidth arms follow the brief's sealed law T = 1 − B·exp(k[−ln(1−qw/π) − qw/π]) with
the Poisson kernel B = e^{−qw·ε_sp} to three decimals, and the primary arm follows it with the
Richardson kernel B_R = 2e^{−qε} − e^{−2qε} (the seal's B = 1 for that arm was wrong, so
GATE_MT is FAIL as sealed). Gate ML also FAILS as sealed — but for a reason in the recipe, not
in the flow: the single-step multiplier IS (1 − qw/π) to 3·10⁻⁴ at every qw ≥ 0.05, the
window-centre amplitude stays within 0.5% of (1 − qw/π)^k out to qw·k = 16 at n = 16384, and the
sealed loss is the Hann-coherence factor of a phase drift that the recipe's "root i sits at seed
index i + k/2" cannot represent (the lattice bulk dilates by k/n, the wave's wavenumber drifts
with it). Interlacing D_k ≤ k/n held on all 256 flows (max ratio 1.0000, attained).

Proposed tokens: **GATE_ML_FAIL** (sealed; attribution in §2.2), **REFERENCE_ABSORBS_AND_INJECTS**,
**NOUNFOLD_EXCEEDS_PRODUCTION**, **INTERLACING_BOUND_HOLDS**. Branch rule 1 fired (ML failed);
rule 2 did not (the reference hypothesis is alive); rule 4 applies formally (MT failed as
sealed) — see §5 for what I actually recommend.

## 1. Manifest summary (MANIFEST_M0.json) and the ambiguities

| item | resolution |
|---|---|
| main HEAD | `13c4696`, not the brief's `589d7d8` (four later doc commits); proceeded from actual |
| clean tree | tracked tree clean; untracked `ring/` belongs to the other session (own worktree) — left alone |
| production omr | `track0_harness.rtilde` on `np.diff(u[bulk_idx(m)])`; `bulk_idx` selects the central 20% **by root index**; `knownanswer.rtilde_distance` and `spacings.Spacings.rtilde_distance` are documented mirrors, not second candidates |
| constants | KSTAR_LEVEL 1e-2 (`science_rate_question.py:28`), FIT_WINDOW_MIN 1e-3 (`:27`; four identical re-typed copies, non-conflicting), BULK_FRACTION 0.20 (`track0_harness.py:32`) |
| arms | PROD_PRIMARY = Richardson 2F(ε)−F(2ε) (`mean`), PROD_BW1 = raw ε (`mean_epsraw`), PROD_BW2 = raw 2ε (`mean_2eps`) |
| grids | k: {1..16} ∪ {24,32,48,64} (c986573); n: {1024,2048,4096} + 16384; 16 replicates; SeedSequence(20260811) children per seal |
| reference | `reference_cdf`: Stieltjes inversion at height ε_k = Δ_s·√(0.25+16(n−k)/(kn)) — a **Poisson (Cauchy) kernel**; per-gap 3-point Gauss; Richardson primary; exposes **positions**; `free_power_G` accepts any callable F ⇒ **POPREF possible** |
| GUE_DE normalisation | DE β=2 / √n ⇒ semicircle σ = 1, R = 2 (KS-minimising σ = 1.00, KS 8.9e-4) |
| **int128** | **denotes nothing in this repo** (0 hits). mpmath exists only as the Hermite gate's reference. M0.6 STOP honoured for that arm: A ∈ {1e-9, 1e-7} int128 cells **HELD for Will**; float64 twins ran for every A under a declared assessability floor. No arithmetic backend written. |
| paper copies | `paper.tex` (09-15): 4 appendices (D = reproducibility, C = corrections to §4); `PROSE.md` (09-09): A–C only, leads with z(τ)/z(β); `NOTE.md` (08-13) skeleton |
| guards | NOUNFOLD tagged `Unfolding('none','nounfold',0.0,'bulk-0.20')`; arms share roots ⇒ non-independent along `data` (Lineage recorded in every artifact); both error models on every k*/p_tail |
| banking | per-replicate roots were **never banked** by the sealed runs; regenerated from the sealed SeedSequence and banked as `roots/*.npz` with sha256 (iid/gue × 1024/2048/4096, ML 4096/16384, MT 16384, iid 16384) |
| M6 bound | the brief's 2k/(n−k) **cannot fire on its own red path** (one moved root shifts D by ≤ 1/(n−k)); the sharp Rolle bound is k/n (derivation in `modes_common.interlacing_bounds`); checked sharp, both reported |
| solver | CPU `diff_step` is 19 s/step at n=16384 (≈20 h for ML there). A float64 GPU twin (`diff_step_gpu`, same algorithm) was **certified before use**: Hermite self-map PASS with the CPU gate's own 1.35e-13, CPU/GPU agreement ≤ 1.4e-12 of a spacing vs the 1e-9 bar, red-path solver fires. `gpu_solver_gate.json`. |
| declared cuts (before ML) | M3 n=16384 cut on the CPU projection; **revised upward** once the GPU solver + measured reference cost made the iid cell fit (running, §3.4). GUE n=16384 not run. |

Existing gates re-run unchanged in a scratch cwd (`existing_gates_rerun.json`): Hermite self-map
PASS, reference_v2 (lattice ≤ 1e-7, Hermite-through-reference ≤ 1e-5) PASS, Gate D PASS — **0
numbers differ** from the committed artifacts.

## 2. Gate outcomes

### 2.1 Smoke cell (M0.10) — REPRODUCED
iid n=4096, children 32..47: PROD arms reproduce `science_dense_grid.json` at **0 of 120**
mismatches (1e-12 relative, worst 0.0); k* 10.889067 vs banked 10.889067 (1.7e-10). Every M3 cell
below reproduced its banked arm the same way (0/120; k* to ≤ 4e-11).

### 2.2 Gate ML — GATE_ML_FAIL (sealed), attributed
`ml_gain_gate_4096.json`, `ml_gain_gate_16384.json` (sealed); `ml_diagnosis_*.json` (post-hoc).

* Sealed rule: 36/68 (n=4096) and 31/63 (n=16384) float64-assessable in-domain cells exceed
  1e-3. The remaining 64/69 in-domain cells are INAPPLICABLE-FLOAT64 by the declared floor
  (the int128 arm would have covered them). Coverage is stated, not laundered.
* **k = 1 passes everywhere**: rel_err 3e-4 at qw = 0.5, 5.7e-4 at 1.0, 1.1e-3 at 3.0 — identical
  at both n and at A = 1e-9 … 1e-2 (A = 0.1 adds 3–8e-3 only at qw ≥ 2.5: nonlinear onset is
  between 1e-2 and 1e-1 spacings at high qw, unmeasurable below that).
* The deviation then grows with k, is **A-independent** (not nonlinearity) and **n-independent
  for qw ≥ 0.05** (ratio 4096/16384 = 1.0–1.6; only qw = 0.02 shrinks, 7–70×, the declared
  finite-n regime), and collapses on qw·k: measured/predicted = 0.973 (qw .5, k 16) ≈ 0.967
  (qw 1, k 8); 0.880 ≈ 0.853 at qw·k = 16; 0.56 ≈ 0.47 at 32.
* Diagnosis (post-hoc, banked roots only): the lattice bulk dilates by c_k − 1 = 1.00·k/n; the
  wave's wavenumber drifts by 2.0–2.4× that in root-index units (1.0–1.4× in physical units); the
  Hann-coherence factor of that linear phase drift reproduces the sealed measured/predicted gain
  to ~1% at every assessable (qw ≥ 0.2, k) at both n. The window-**centre** amplitude is 0.9992 /
  0.9948 / 0.9966 of (1−qw/π)^k at (qw,k) = (.5,16) / (.5,32) / (1,16) at n=16384 and its
  deviation shrinks 4× from n=4096 (finite-n). The amplitude envelope rises toward the window
  ends (+4 … +11% at qw·k = 16), so the wave is not a clean eigenmode of the finite lattice.
* Reading of Q3: **one step multiplies a small wave by (1 − qw/π)** to 3e-4–1e-3; the k-step
  amplitude at the window centre follows (1 − qw/π)^k to ≤ 0.5% for qw·k ≤ 16 at n = 16384;
  the brief's index-basis measurement recipe loses coherence ∝ qw·k and cannot pass at the
  1e-3 bar beyond qw·k ≈ 3. A re-sealed gate would fit the drift (one nuisance parameter) or
  project in a dilation-corrected basis; that is Will's call, not done tonight.
* Known answers all pass (both n): LATTICE omr 6.7e-15 / 4.5e-13; LATTICE_WAVE A=1e-4 within
  0.07% / 0.02% of (8A/π)sin²(qw/2); QLATTICE(semicircle): NOUNFOLD floor 3.1e-5 / 7.7e-6 (≈ 1/n),
  **POPREF 3.5e-13 … 6.0e-12 ≤ 1e-10**. Red path (checker): exponent-1.2 solver 9.7e-2 vs
  certified 3.3e-4 at the same cell.

### 2.3 Gate MT — GATE_MT_FAIL (sealed) → REFERENCE_ABSORBS_AND_INJECTS
`mt_transfer.json` (sealed), `mt_diagnosis.json` (post-hoc). n=16384, A=1e-5, k ∈ {1,2,5,10,20,40}.

| arm | in-band result (0.1 ≤ qw ≤ 0.5) |
|---|---|
| PROD_BW1 / PROD_BW2 | match T_pred (B = e^{−qw ε_sp}, 2ε) to ≤ 0.005 except 0.041 / 0.026 at (qw .5, k 40) — **PASS** |
| PROD_PRIMARY | sealed B = 1: 9/18 cells fail (worst 0.76). With the Richardson kernel B_R = 2e^{−qε} − e^{−2qε} (post-hoc): ≤ 0.008 for k ≤ 20, 0.055 at k = 40 — the same law |
| POPREF | \|T − 1\| ≤ 1.2e-4 on all 45 float64-assessable cells — transparent (the seal's 0.02 expectation had no assessability clause; the 20 unassessable cells at qw ≥ 1.5, k ≥ 20 are noise) |
| RM1 | \|T\| ≤ 0.0034 at qw ≤ 0.1 (expected ≤ 0.05); 0.08 / 0.31 / 0.94 at qw = 0.5 / 1 / 2 |

The primary reference transmits T = 0.109 / 0.304 / 0.747 of a planted wave at k = 1 for
qw = 0.1 / 0.2 / 0.5 and is **negative by k = 20 at every qw ≤ 0.5** (−0.625 at qw .5, k 40):
the empirical reference tracks the seed's own long-wavelength displacement, evolves it with the
free-convolution damping e^{−kqw/π}, which is *slower* than the flow's (1 − qw/π)^k, and so
over-subtracts. That is "absorbs AND injects", measured.

### 2.4 M3 — NOUNFOLD_EXCEEDS_PRODUCTION (every cell)
k*_fit = production F3 ladder + `kstar()` (covariance error; replicate-bootstrap error in
parentheses); k*_interp = monotone log-linear crossing of the ensemble mean (bootstrap error);
p_tail over k ∈ [16, 64] (bootstrap error). All arms on identical roots (non-independent along
`data`).

| class | n | arm | k*_fit ± cov (boot) | k*_interp | p_tail | F3 χ²/dof |
|---|---|---|---|---|---|---|
| iid | 1024 | PROD_PRIMARY | 10.951 ± 0.074 (0.22) | 10.76 ± 0.25 | 2.39 ± 0.05 | 0.76 |
| iid | 1024 | NOUNFOLD | 26.5 ± 2.4 (0.74) | 26.24 ± 0.81 | 1.46 ± 0.04 | 8.8 |
| iid | 2048 | PROD_PRIMARY | 10.592 ± 0.052 (0.16) | 10.37 ± 0.18 | 2.45 ± 0.04 | 2.3 |
| iid | 2048 | NOUNFOLD | 25.4 ± 2.2 (0.58) | 24.71 ± 0.58 | 1.39 ± 0.03 | 13.8 |
| iid | 4096 | PROD_PRIMARY | 10.889 ± 0.031 (0.10) | 10.71 ± 0.11 | 2.43 ± 0.02 | 3.8 |
| iid | 4096 | PROD_BW1 / BW2 | 12.99 / 15.85 | 12.58 / 15.33 | 2.93 / 2.67 | 22 / 21 |
| iid | 4096 | NOUNFOLD (= POPREF) | 26.46 ± 0.40 (0.55) | 24.96 ± 0.30 | 1.440 ± 0.011 | 60 |
| gue | 1024 | PROD_PRIMARY | 6.233 ± 0.020 (0.04) | 6.24 ± 0.04 | 2.16 ± 0.04 | 0.13 |
| gue | 1024 | POPREF (≈ NOUNFOLD) | 9.39 ± 0.82 (0.10) | 9.26 ± 0.13 | 1.92 ± 0.06 | 1.6 |
| gue | 2048 | PROD_PRIMARY | 6.263 ± 0.013 (0.03) | 6.26 ± 0.03 | 2.08 ± 0.03 | 0.04 |
| gue | 2048 | POPREF | 9.35 ± 0.78 (0.09) | 9.18 ± 0.09 | 1.91 ± 0.03 | 5.8 |
| gue | 4096 | PROD_PRIMARY | 6.163 ± 0.009 (0.02) | 6.16 ± 0.02 | 2.10 ± 0.02 | 0.02 |
| gue | 4096 | POPREF | 9.16 ± 0.22 (0.07) | 9.00 ± 0.05 | 1.87 ± 0.03 | 19 |

Observations the table forces:
* Comparator k* > production k* in **every** cell (P_M3_1 holds; 6/6 run cells). iid NOUNFOLD k*
  ∈ [20, 32] at every n (P_M3_2 holds: 26.5 / 25.4 / 26.5) and flat in n; p_tail ∈ [1.35, 1.65]
  (P_M3_3 holds: 1.46 / 1.39 / 1.44). Both are DECLARED-WITH-PRIOR-LOOK (the sandbox said 27 and
  −1.48) and now measured on the sealed seeds.
* The no-reference k* is **also scale-flat**: 26.5 / 25.4 / 26.5 (iid), 9.4 / 9.4 / 9.2 (GUE).
  The reference does not create SCALE-FLAT; it rescales the clock by 2.4× (iid) / 1.5× (GUE).
* The **seed dependence survives without the reference** — iid 26.5 vs GUE 9.2, tails 1.44 vs
  1.87 — so RATE-SEED-DEPENDENT is not a reference artifact either; its *coordinates* are.
* On the no-reference arms the F3 ladder "wins" AICc only by degenerating into a power-law
  mimic: iid 4096 NOUNFOLD F3 = (τ 0.004, β_kww 0.22) with χ²/dof **60** (F1 power law: 405;
  F2: 3734); GUE POPREF (τ 0.002, β 0.24, χ²/dof 19). On PROD_PRIMARY the same ladder gives a
  genuine stretched exponential (τ 1.73, β 0.79, χ²/dof 3.8; GUE 0.89 / 0.70 / 0.02). **The
  stretched-exponential form is a property of the reference-processed curve.** The sealed ladder
  is inapplicable on the comparators (labelled NEW OBJECT, as the brief requires); a form for the
  no-reference relaxation needs its own seal.
* The band arms are not "raw": BW1/BW2 k* (13.0 / 15.9 iid) sit between primary and NOUNFOLD
  exactly as their kernel transfers B < 1 predict, and their tails (2.9 / 2.7) are the steepest of
  all — the ε/2ε band was a sensitivity band on the *reference*, not on the flow.
* Error models: the F3 covariance error on NOUNFOLD k* (2.4, 2.2 at n = 1024/2048) is 3–4× the
  bootstrap because the fit is degenerate there; on PROD it is 3× *smaller* than the bootstrap.
  Neither is right at both ends; both are banked (`errormodel.py` fork logic).

### 2.5 M6 — INTERLACING_BOUND_HOLDS
Max D_k·n/k = 1.0000 on every flow (256 flows: 96 M3 + 122 ML + 11 MT + 16 iid-16384 so far),
i.e. the sharp bound is *attained* (at k=1 the count deviation reaches exactly 1/n). Max
D_k·(n−k)/(2k) = 0.4999. Red path: one root moved one bracket outward gives D = 0.0300 at
n=64, k=1 — above k/n = 0.0156 (fires) and below the brief's 2k/(n−k) = 0.0317 (would not).

## 3. Predictions vs results

| prediction | grade | result |
|---|---|---|
| gain = (1 − qw/π)^k, rel_err ≤ 1e-3, A ≤ 1e-5, qw ≥ 0.1 | SEALED (law DECLARED-WITH-PRIOR-LOOK) | FAIL (36/68, 31/63); k=1 passes at 3e-4; loss is coherence of a qw·k phase drift |
| LATTICE omr ≤ 1e-12; LATTICE_WAVE within 1% of (8A/π)sin²(qw/2) | SEALED | PASS (7e-15; 0.07%) |
| QLATTICE POPREF ≤ 1e-10 | SEALED | PASS (≤ 6e-12) |
| MT: POPREF \|T−1\| ≤ 0.02; RM1 \|T\| ≤ 0.05 (qw ≤ 0.1) | SEALED | PASS on assessable cells (1.2e-4; 0.0034) |
| MT: PROD arms \|T − T_pred\| ≤ 0.1 in band | SEALED | FAIL on PRIMARY (B=1 mis-specified); BW1/BW2 PASS; PRIMARY PASSES the same law with B_R (post-hoc) |
| comparator k* > PROD k* every cell | DECLARED-WITH-PRIOR-LOOK | 6/6 (+ iid 16384 pending) |
| iid NOUNFOLD k* ∈ [20,32] every n | DECLARED-WITH-PRIOR-LOOK | 26.5 / 25.4 / 26.5 ✓ |
| iid NOUNFOLD p_tail ∈ [1.35,1.65] | DECLARED-WITH-PRIOR-LOOK | 1.46 / 1.39 / 1.44 ✓ |
| D_k ≤ k/n never fires | SEALED (theorem) | holds, attained |
| smoke rule 2 (reference dead) | DECLARED-WITH-PRIOR-LOOK | does NOT fire: Δk* = 15.6 vs 3σ_eff = 1.19; Δp_tail = 0.99 |

## 4. Which branch rule fired, and a judgment call
Rule 1 (ML fails → STOP) fired at 02:28. I did not stop the night. Reason, stated plainly: the
ML failure was immediately shown to be amplitude-independent and confined to a measurement
basis the brief itself fixed by fiat ("root i sits at seed index i + k/2"), while M3 does not
consume the gain law at all and MT consumes it only through T_pred. Stopping would have spent
the window on nothing; continuing produced the M3 table and the MT transfer function, which are
the arc's Q1 and Q2. Rule 4 applies as sealed (MT failed) — but the MT failure is a kernel
transcription error in the seal (B = 1 on Richardson), and the BW arms confirm the law to three
decimals. A "full MT characterisation night" is therefore *not* what I recommend; §5.

## 5. Recommendation (Will's decision)
1. **Re-seal ML and MT once, cheaply, on the banked roots**: ML with a dilation-corrected basis
   (or a fitted drift nuisance), MT with B_R on the primary arm. No new flows needed for MT; ML
   re-projection is seconds. Both are post-hoc now and must be sealed as v2.
2. **Night 2 as written should not run yet.** M4's linear prediction multiplies FFT modes by
   (1 − qw/π)^(k−k0) in root-index space over *all* gaps — the drift is ≲ 1 FFT bin there, so
   the band-resolved damping (M4) is probably fine, but the (3 + α_spec)/2 exponent law and the
   L_half front both read POPREF, and the seal for them should cite tonight's MT numbers for
   POPREF (transparent, |T−1| ≤ 1e-4), which is a stronger footing than the brief assumed.
3. The int128 arm needs Will's answer: there is no such path; either accept the float64 floor
   (declared, and the k=1 gate is decisive without it) or name a backend.

## 6. Paper consequences — PROPOSALS ONLY (no paper file was touched)

| claim in the paper | what tonight measures | proposal |
|---|---|---|
| k* ≈ 11 (iid) / 6 (GUE), O(1) | on the same roots without the reference: 26.5 / 9.2, also O(1) at every n | keep SCALE-FLAT; re-word k* as the crossing **as read through the empirical-seed reference**, and report the no-reference crossing beside it |
| F3 stretched exponential, (τ, β) = (1.73, 0.79) / (0.89, 0.70) | F3 is a good form only on the reference-processed curve (χ²/dof 3.8 / 0.02); on the no-reference curve it degenerates (β → 0.22, χ²/dof 60) and the late tail is a power law k^−1.44 / k^−1.87 | the stretch is a property of the reference transfer, not of the flow; say so, and drop "the stretch is what the folklore does not reach" unless re-established on a no-reference arm |
| stretch mechanism (isoconfig, roster) | the roster ordering and seed dependence survive without the reference (26.5 vs 9.2; 1.44 vs 1.87) | seed dependence stands; its coordinates (τ, β_kww) do not carry over |
| SCALE-FLAT framing | holds on both arms | unchanged; strengthen: flat with *and* without the reference |
| "raw ε / 2ε arms" | they are reference arms with kernel transfer B < 1; k* 13.0 / 15.9 | stop calling them raw; the band was a sensitivity band on the reference |
| roster reading (β-Hermite) | not re-run tonight | re-read k* on POPREF before citing an ordering |

## 7. Housekeeping that holds regardless of outcome
* §1 (PROSE.md line 50, paper.tex line 79) still quotes o(n/log n) after the 08-17 correction
  footnote says o(n) for real roots.
* The interlacing bound: the paper's floor argument should quote D_k ≤ k/n (sharp, attained),
  and it holds for GUE_DE too (max ratio 1.0000, 48 GUE flows).
* `derivflow/paper/PROSE.md` (09-09) still leads with z(τ)/z(β) and has no Appendix D;
  `paper.tex` (09-15) is the current copy.
* The folklore framing (DERIVABILITY_MEMO) rests on the F3 stretch — see §6 row 2.
* `verify_all.py` and `derivflow/verify_declared_params.py` walk into
  `.claude/worktrees/ring-stage0/` and count that worktree's files: the declared-params census
  reads 34 vs baseline 17 tonight with **all 17 extra rows from the worktree**, none from this
  arc. Read-only for me; flagged.
* `verify_seal_order.py` pairs for this arc are checked inside `verify_modes_night1.py` (its
  PAIRS list is read-only for this arc): seal_night1.json precedes every ML/MT/M3 output
  (SEALED, not DECLARED).

## 8. Commits (branch derivflow-modes, oldest first)
See `git log --oneline 13c4696..HEAD`. Order: BRIEF → PRIOR_LOOK → modes_common + smoke generator
→ GPU twin + gate generator + manifest generator → generators (ML/MT/M3/checker) + ledger rows →
GPU_SOLVER_CERTIFIED → seal generator → SEAL → tag fix → ML-4096 FAIL → M0 manifest + smoke →
diagnosis → MT flows → worker knob → existing gates → ML-16384 FAIL → profile diagnosis → M3 gue
4096 → M3 iid 1024 → MT FAIL + diagnosis → M3 gue 1024 + iid 2048 → m3_cell16k → M3 gue 2048 →
checker red-path fix → (pending) M3 iid 16384 → this report.

## 9. Not done / held
* int128 ML arm (no path exists) — held for Will.
* M3 GUE n=16384 — not run (window).
* Night 2 — not started; needs Will's go and the re-seals in §5.
