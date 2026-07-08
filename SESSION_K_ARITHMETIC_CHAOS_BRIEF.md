# ARS Session K (v3 — FINALIZED) — Arithmetic-Chaos Universality of the Modular / Gauss-Map Spectral Substrate, with a Co-Primary Session-J Bridge Check

**Status:** v2 (expert-revised) + three expert refinements folded in + one additional load-bearing catch found on disk. No unseal performed. §7 is pre-registration only. Appendix Z is dark.

**Naming note.** "Session K" here = the *arithmetic-chaos / Maass / Gauss-map* line. It is distinct from the `approximability/` **overnight-K** bridge run (commit c79ce8b), which is the *metallic-ladder* `θ_∞ = L_a/C_a` work this session pre-registers against. Same letter, different substrate; the collision is why §2 below is written with extreme care about *which* `L_a` is meant.

---

## Changes folded in from the expert session

**R1 — `C_nonarith` = Hecke triangle `n=5` (confirmed).** Published GOE NNS data exists (Bogomolny–Schmit; ~6000 levels), clearly departing from Poisson. Hecke triangles are arithmetic only for `n = 3,4,6,∞`, so the *tight* contrast is **within one family**: `n=3` (S1, arithmetic → Poisson) vs `n=5` (non-arithmetic → GOE), same triangle-group geometry, arithmeticity as the sole flipped variable. **Upgrade path (flag to expert, do not block on):** the recent area-preserving perturbation of the Schmit triangle gives the arithmetic→GOE crossover as a *tunable knob* (continuous, locate where the class flips) rather than two endpoints. `n=5` is the safe fallback.

**R2 — Completeness gate gains a MANDATORY desymmetrization clause (load-bearing; gate by construction).** The modular surface has a reflection symmetry commuting with the Laplacian → eigenfunctions split into **even and odd** sectors = two independent superimposed spectra. **Σ²/Δ₃ must be run on even and odd sectors SEPARATELY, never merged.** Two independent spectra superimposed are pushed toward Poisson *by the superposition alone*, independent of arithmeticity — a mechanism that (a) mimics the exact anomaly Co-Primary 1 predicts and (b) **leaves no fingerprint in a completeness count**. Weyl completeness (§3) is therefore checked *per sector* (each ≈ half the total density). This is a fourth instance of the banked parent failure (search/measurement geometry manufacturing the predicted answer) and, unlike incompleteness, it cannot be caught after the fact — so it is gated by construction. **This is the one clause that must hold before any unseal.**

**R3 — Mayer's transfer operator unifies both co-primaries and the contrast on ONE substrate.** Mayer's machinery extends to Hecke triangle groups `G_q` (non-arithmetic for `q≠3,4,6`) via the natural extension of the Hurwitz–Nakada CF map (Mayer–Mühlenbruch–Strömberg). So S1 (arithmetic n=3), `C_nonarith` (n=5), and the S3→θ_∞ bridge all sit on one CF/transfer-operator object — the interface-instrument framing the brief opens with, made literal.

**R4 — [NEW, found on disk] Co-Primary 2 conflates two different `L_a`; split it.** See §2. This is the analogue of R2 for the bridge: the draft's symbol `L_a` denotes the Gauss-map *a.e.* Lévy constant `e^{π²/(12 ln 2)} = 3.27582` in one clause and the *banked per-metallic* `L_a = log ε_a` (0.4812…) in the next. The banked `θ_∞` ladder contains **neither 3.2758 nor π²/(12 ln 2)** — it is built from `log ε_a`. Recovering 3.2758 validates the operator but is **not** the numerator of the banked bridge and cannot reproduce that ladder. Left unfixed, an operator-sanity pass would be laundered into "θ_∞ reproduced independently." Split into 2a (operator sanity) and 2b (the real independent reproduction).

---

## 0. Interface framing

Substrate: modular-surface / Gauss-map dynamics. Observer: point-process universality lens (`Σ²(L)`, `Δ₃(L)`), **run per symmetry sector**. Interface question: what universality class does the arithmetic substrate occupy, where exactly does arithmeticity flip that class, and does the transfer operator reproduce the banked Session-J metallic bridge from the independent (periodic-orbit) spectral direction? No finite-group shadow is hunted this session (Appendix Z dark).

---

## 1. Co-Primary 1 — Arithmetic-chaos fingerprint of the Maass spectrum

**Substrate S1:** Maass cusp-form spectrum of `PSL(2,ℤ)\ℍ`, `{r_n}`, `λ_n = 1/4 + r_n²`. **Per-sector (even/odd) — R2.**

**Claim under test:** classically strongly chaotic + TRI ⇒ generic BGS prediction GOE; Hecke arithmetic expected to force **Poisson-like**. Confirm the anomaly; quantify via crossover scale `L*` where Hecke degeneracy dominates rigidity.

**Class-isolating calibrator (R1):** within-family `n=3` (arithmetic, expect Poisson) vs `n=5` (non-arithmetic, expect GOE). Without a clean `C_nonarith`→GOE, **no S1 conclusion is licensed**.

**Observables (layered, per sector):**
- L1 `P(s)`: expect Poisson `e^{-s}` (corroborating only).
- **L2 (decisive): `Σ²(L)`, `Δ₃(L)`** — expect `Σ²(L)~L` vs GOE `(2/π²)ln L`; **locate `L*`** (primary durable number).
- L2b pair correlation `R₂` as independent long-range cross-check (watch arithmetic-degeneracy origin spike).

**Primary durable output:** class assignment + `L*` + quantified GOE departure, **per sector**.

---

## 2. Co-Primary 2 — Session-J bridge reproduction from the transfer operator (SPLIT per R4)

**Substrate S3:** GKW / Mayer–Ruelle transfer operator of the Gauss map; nuclear, discrete real spectrum `λ₀ = 1 > λ₁ = −0.30366… > …`.

**Mechanism (backbone, not a dataset):** Mayer's identity — Selberg zeta of `PSL(2,ℤ)\ℍ` = Fredholm determinant of the s-parametrized transfer operator. Ties S3 to S1's Maass side; shared root of both co-primaries. Extends to `G_q` (R3).

**Pre-registration (mirror of on-disk sealed values — see `SESSION_K_COPRIMARY2_PREREG_SEALED.json`):**

Banked metallic bridge (`approximability/O1_bridge_prereg_SEALED.json`, run c79ce8b):
- `L_a = log((a+√(a²+4))/2)` exact: {1: 0.4812118, 2: 0.8813736, 3: 1.1947632, 4: 1.4436355, 5: 1.6472311}
- `C_a` (Panel-A measured): {1: 0.8771, 2: 0.8667, 3: 0.9133, 4: 1.02160±0.031, 5: 1.16038±0.045}
- Sealed `θ_∞ = L_a/C_a`: {1: 0.548615 (meas-C) / 0.545979 (closed logφ/log(1+√2)), 2: 1.016917, 3: 1.308113, 4: 1.413106, 5: 1.419558}

**2a — Operator sanity / a.e. calibrator (NOT the bridge numerator).** From the leading-eigenvalue pressure of the discretized operator, recover the Gauss-map a.e. quantities:
- Lyapunov `λ_Gauss = π²/(6 ln 2) = 2.373138…`
- a.e. denominator-growth (Khinchin–Lévy exponent) `π²/(12 ln 2) = 1.186569…`; Lévy constant `e^{π²/(12 ln 2)} = 3.275823…`
- subdominant eigenvalue `λ₁ = −0.3036300…`
- **Pass:** operator reproduces these to discretization precision ⇒ discretization is trustworthy. **This does NOT touch the banked θ_∞ ladder.**

**2b — The actual independent bridge reproduction.** For each a=1..5, read the **a-branch fixed-point multiplier** (periodic-orbit / Fredholm-determinant reading; fixed point `x* = 1/(a + x*)`, growth rate `log ε_a`) *numerically from the discretized operator*, and check it reproduces the sealed `L_exact` to precision. Then feed into banked `C_a` and confirm the sealed `θ_∞` ladder within propagated `C`-bands.
- **Pass:** numeric periodic-orbit `L_a` matches closed-form `log ε_a` AND `θ_∞ = L_a/C_a` reproduces the sealed ladder ⇒ **independent spectral validation of the Session-J metallic bridge**.
- **Fail:** discrepancy at banked precision ⇒ conflict in already-banked ARS state ⇒ **top result of the session; halt, escalate, everything waits** (§8).

**Why co-primary:** low-multiplicity, mechanism-derived, closed-form-checkable, clean pass/fail — the structural opposite of the demoted moonshine probe.

---

## 3. Layer-zero gate (runs first; disqualifies windows for everything above)

**THE gate — completeness against Weyl, PER SECTOR (R2).** Maass counting `N(r) ≈ r²/12` (area `π/3`) + known corrections (`−(r/π)ln r`-type + scattering/Eisenstein). Simultaneously the integer anchor and the completeness test.
- Compute predicted count per `r`-window **per sector** before any spacing statistic.
- Observed short of Weyl in a sector-window ⇒ that sector-window is incomplete ⇒ **disqualified for Σ²/Δ₃, full stop.**
- **Rationale (the spine): missing levels bias Δ₃/Σ² toward Poisson — an incomplete spectrum manufactures the exact anomaly Co-Primary 1 predicts.** A Poisson result on an unverified-complete, un-desymmetrized spectrum is worth nothing.

**Desymmetrize BEFORE unfolding and before any statistic (R2).** Even/odd sectors separated first; Weyl-checked per sector; Σ²/Δ₃ per sector. Merged-list statistics are prohibited.

**Unfold with the known Weyl density only.** Self-derived unfold prohibited (banked fundamental negative). Expert must verify unfold provenance.

**Other anchors:** Hecke multiplicity structure (known discrete structure — characterize, do not confuse for anomaly) and congruence indices `[PSL(2,ℤ):Γ₀(N)]` for bookkeeping only.

---

## 4. Calibrator zoo

- **Analytic references:** GUE, GOE, GSE, Poisson (`P(s)`, `Σ²`, `Δ₃`).
- **S5 — Riemann zeta zeros (arithmetic→GUE control).** Montgomery–Odlyzko. Makes Katz–Sarnak operational: instrument must return arithmetic-Poisson for S1 and arithmetic-GUE for S5.
- **S3-as-deterministic-edge calibrator.** Feed S3's decaying deterministic spectrum through the classifier; confirm it **refuses** a random-matrix class (same role as the `e` refusal). Guards against forcing an ensemble onto non-random input.
- **`C_nonarith` (Hecke n=5)** doubles as the GOE arithmetic-contrast calibrator (R1).

---

## 5. Protocol / discipline

- **Blind-then-single-unseal.** Labels masked; classifier blind against the zoo; one unseal; §7 pre-committed.
- **Desymmetrization + completeness gate FIRST** (§3, R2) — nothing runs on a disqualified or merged sector-window.
- **Per-window surrogate** on every Σ²/Δ₃ estimate.
- **Pole-tests-absolute with calibrated floors** fixed from the zoo before substrates are seen.
- **Published-product compatibility gate:** S1 Poisson-like and S5 GUE must match arithmetic-chaos literature or the discrepancy is *explained, not absorbed*.
- **Dataset-selection audit:** provenance + completeness (+ sector split) logged for every list. S1 from LMFDB / Hejhal-algorithm computations (Steil ~2545 consecutive; Then et al. extensions), completeness cross-checked vs Weyl + trace formula, `[EXPERT: confirm r-range, completeness, and sector labels present in source]`. S5 from Odlyzko. S3 by direct operator discretization.
- **Combined-quadrant** corroborating only; long-range Σ²/Δ₃ (per sector) is the class instrument (banked).

---

## 6. What was cut (do not re-add)

S2 (Selberg zeros as a dataset) — redundant with S1, drags in scattering rabbit hole; Mayer's identity kept as Primary-2 mechanism only. Genus-zero "resonance" — coincidence-shaped, no mechanism, informs no measurement → Appendix Z. Moonshine probe + renorm-identity hunt → Appendix Z, dark, hard entry gate unmet.

---

## 7. Pre-registered predictions (COMMIT before generation)

| Item | Short-range | Long-range (per sector) | Verdict target |
|---|---|---|---|
| S1 Maass n=3 (Co-Prim 1) | Poisson `e^{-s}` | `Σ²~L`; locate `L*` | arithmetic-Poisson, GOE excluded |
| `C_nonarith` n=5 (contrast) | GOE Wigner | GOE `(2/π²)ln L` | GOE — validates class-isolating variable |
| S5 zeta zeros (control) | GUE Wigner | GUE `(1/π²)ln L` | GUE — validates lens on arithmetic input |
| S3 spectrum (edge calib.) | n/a | n/a | classifier returns "not an ensemble" |
| S3 2a (operator sanity) | — | — | `π²/(6 ln 2)`, `3.27582`, `λ₁=−0.30366` to precision |
| S3 2b → θ_∞ (Co-Prim 2) | — | — | numeric `log ε_a` = sealed `L_exact`; `θ_∞` reproduces sealed ladder |

**Falsifiers:**
- S1 → GOE ⇒ incomplete-spectrum **or un-desymmetrized-merge** artifact (§3 gate) or anomaly premise fails. Diagnose, do not absorb.
- `C_nonarith` → Poisson ⇒ calibration void; no S1 conclusion licensed.
- S5 → not-GUE ⇒ lens failure; stop.
- **S3 2b → θ_∞ mismatch at banked precision ⇒ escalate as top result; banked-state conflict outranks everything.**
- S3 2a pass but 2b fail ⇒ operator fine, bridge conflict — **still escalate 2b** (do not let 2a's pass mask it, per R4).

---

## 8. Refinement-loop branches

- S1 Poisson + `L*` located ⇒ characterize approach-to-Poisson vs `r`-cutoff and the arithmetic correction as its own object (durable regardless).
- S3 2b → θ_∞ passes ⇒ bank as independent spectral validation of the Session-J bridge; consider promoting the transfer-operator route to a standing tool.
- S3 2b → θ_∞ fails ⇒ dedicated Session-J reconciliation session, highest priority; Session K pauses.

---

## 9. Expected outcome & value

Most probable: S1 (n=3) = arithmetic-Poisson with clean `L*`, per sector; `C_nonarith` (n=5) = GOE; S5 = GUE; S3 refuses an ensemble; S3 2a recovers the a.e. Gauss constants; S3 2b reproduces the sealed metallic θ_∞ ladder from periodic-orbit multipliers. Value = ARS-standard universality fingerprint of the KAM-spectral substrate, exact localization of the arithmetic anomaly (per sector), and an independent spectral confirmation of Session J — low-multiplicity, falsifiable, moonshine-independent.

---

## Appendix Z — Moonshine shadow probe (DORMANT — does not run)

Entry gate (all required, currently unmet): (1) a named single group + specific proposed grading derived from a *mechanism* predicting graded dimensions = a specific spectral counting function, before looking; (2) a computed honest look-elsewhere correction; (3) power analysis showing the available spectrum can reject the null at that correction. No such mechanism exists for the Maass spectrum — the non-run is the correct outcome, not a gap. Genus-zero coincidence filed as untested speculation; may not be used to *select* a targeted group list.

---

*End v3. No unseal. §7 pre-registration only. Appendix Z dark.*
