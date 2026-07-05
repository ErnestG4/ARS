# MORNING — Lens Expansions of the RF Engine (honesty ledger)

Session frame: exploratory lens-engineering on the RF engine (`arithmetic_toolkit.ramanujan_fourier`,
`padic_amplitude_v4`). Nothing tool-side modified; refsuite frozen; banked ARS read-only. All work in
`rf_lenses/`. `/home/combust/fmexplorer/bin/python3`, `PYTHONPATH=…/riemann_explorer`, `BASE_SEED=20240517`.
Negatives banked at equal prominence — a lens that doesn't fit, with the reason, is a full deliverable.

Priority order attempted: A → E → B → C → D.

---

## Thread A — Wiener–Khinchin bridge (Gadiyar–Padma 1999) — **LANDS. Reframes the session.**
Artifacts: `threadA_wiener_khinchin.py`, `threadA.json`, `threadA_figure.py`, `threadA_orthogonality.png`.

**Lit anchor verified (house rule).** Derived the bridge independently from Ramanujan-sum shift
orthogonality `(1/N)Σ_n c_q(n)c_q(n+h) → c_q(h)` (cross terms q≠r vanish), giving the sharp identity
> **R(h) = ⟨f(n)f(n+h)⟩ₙ = Σ_q a_q² c_q(h)**,  with the toolkit's `a_q = (1/φ(q))⟨f·c_q⟩`.
Confirmed numerically on the squarefree indicator to **max residual 4.5e-4** (h≥1); the h=0 offset (0.0225)
is exactly the truncated high-q power. The code's `a_q` match the **closed form** `(6/π²)·μ(q)/∏_{p|q}(p²−1)`
exactly (a₂=−0.2026, a₃=−0.0760, a₆=+0.0253) — so the RF engine computes *true* arithmetic RF coefficients
and Gadiyar–Padma is real, not a normalization coincidence.

**The session-scoping finding.** The WK dual of the RF power spectrum is the **raw integer-lag**
autocorrelation. Family II runs on **unfolded** (unit-rate) spacings. These coincide only at constant rate.
Demonstrated (not asserted) across 4 substrates (WK residual ~1e-3 on the arithmetic/flat ones):

| substrate | rate CV | Family-II best-fit | Fam-II ks_gue | RF top-q | RF concentration |
|---|---|---|---|---|---|
| squarefree | 0.002 | goe | 0.35 | [4,2,3,9,5] | 8.2e5 |
| **primes** | 0.11 | **poisson** | 0.23 | **[2,3,6,5,10]** | 5.2e3 |
| poisson_flat | 0.01 | goe | 0.40 | [16,2,12,9,8] | 62 |
| gue_wigner_unit | 0.07 | gue | 0.31 | [2,5,8,12,7] | 149 |

- **Decisive orthogonality:** primes read as **POISSON** by Family II (unfolded spacings — Gallagher's
  theorem) yet carry huge **even-q** RF power (Hardy–Littlewood singular series). RF and Family II give
  **orthogonal readings on the same substrate** ⇒ Family III is *not* a WK restatement of Family II.
- On flat calibrators (poisson, GUE-unfolded) RF concentration is O(100) with no arithmetic peak — there RF
  *is* WK-redundant with spacing. **The brief's redundancy worry is real only in the flat corner.**
- **Consequence for the session:** RF carries genuinely new information exactly on variable-rate arithmetic
  substrates (primes, ζ/L-zeros) — so Threads B/C probe real independent structure; an RF read on a flat
  dynamical calibrator (e.g. a Family-V map's unfolded events) is WK-forced by its spacing and should not be
  banked as new.

**Honest caveats.** (1) `gue_wigner_unit` WK residual is 9.6e-2 — a *truncation* artifact (binning unit-mean
GUE events at width 1 gives a near-unit-density indicator whose autocorrelation needs q_max≫120), not an
identity failure; the sparse arithmetic indicators (density 0.08–0.6) converge at q_max=120. (2) rate_CV is a
coarse 50-block density-CV; it orders the substrates correctly but is not a calibrated statistic. (3) Only 98
ζ-zeros are on hand (< the Σ² floor of 200), so ζ enters only qualitatively; primes carry the variable-rate
arithmetic case.

---

## Thread E — time-chaos vs space-quasiperiodicity universality diff — **PRE-REG FALSIFIED + INSTRUMENT-BOUNDED.**
Artifacts: `threadE_universality_diff.py`, `threadE.json`, `threadE_figure.py`, `threadE_rigidity.png`.
Substrates: diatonic Hamiltonian spectrum (banked `fifth_edges_lam8_q665/q15601`, band centers) vs Mackey–Glass
chaos τ=30 (3-extractor consensus, continuous-system discipline). Family II via `longrange_discriminator`.

**The pre-registration reversed — both directions.** Registered: crystal rigid (Σ²~logL), MG chaos Poisson-like
(Σ²~L). Measured at matched N≈600–680:
- **Mackey–Glass chaos reads RIGID, not Poisson:** Σ²/L ≈ 0.13–0.28, Family I best_fit GOE/GUE — **stable across
  all 3 extractors AND all unfold degrees 4→28** (a genuine, robust reading). A deterministic chaotic oscillator has
  a dominant timescale, so its recurrence intervals are sub-Poisson regular. *Chaos ≠ Poisson recurrence.*
- **The crystal spectrum is NOT READABLE by Family II.** Its band-center density is singular — the **top-3 gaps carry
  94% of the span** — so no smooth unfold can flatten it. Σ²/L is a **free parameter of the unfold**: 55.9 (deg-4) →
  21.5 (deg-28), still falling, never converging; rank-unfold gives 0.0 (spurious perfect rigidity). The reading spans
  **five orders of magnitude** with the unfold choice. The pre-registered "crystal rigid (logL)" is not even measurable
  with this instrument.

**Verdict.** The clean headline the brief hoped for ("distinguished by long-range rigidity, not marginal spacing")
does NOT land as stated. What lands, and is worth more:
1. **Chaos-recurrence is rigid, not Poisson** — a robust cross-substrate fact (3 extractors × 7 unfold degrees, Σ²/L
   locked ~0.2). The marginal (Family I) also reversed the brief's guess (MG→GOE/GUE, crystal→Poisson) — as the brief
   warned, do not bank Family I; here it was backwards too.
2. **The quasicrystal's long-range spectral class is inaccessible to density-unfolding** — a singular (Cantor) density
   defeats Family II by construction. This re-instantiates the banked *"floor is rigidity not density; no DOS estimator
   recovers it below M≫N cost"* lesson (AM metal→floor, Phase-36) **across the time/space divide**: the instrument
   reads the time-domain substrate cleanly and the space-domain substrate not at all.
3. **Observable-binding (banked node) is the resolution:** the crystal's long-range order lives in its multifractal
   *band-width* spectrum (Family IV box-dim, banked D_box≈0.47 / the Thouless law / gap-labeling), NOT in a
   density-unfolded level sequence; MG's lives in recurrence-rigidity (Family II) + Lyapunov (Family V). Forcing both
   onto Family II exposes the observable mismatch, not a shared class axis.

**Period-doubling cascade (pre-registered bonus) — PARTIAL.** τ-sweep 9→20 shows the MG route present in the amplitude
spread: period-1 (τ<13.3, spread≈0) → period-2 (τ≈13.4–15.6) → period-4 (τ≈15.7–16.9) → chaos (τ>17). But a clean
**Feigenbaum δ is not resolved** — the recurrence-based period counter is noise-dominated at low amplitude and δ only
emerges near the accumulation point, which needs finer τ scanning than run. Route confirmed; δ not banked.

**Honest caveats.** (1) Only the first two crude doublings were caught → no δ. (2) MG's Σ²(L) has few L points at
N≈600 (Family II floor is N=200); the *stability* across extractors/degrees is the load-bearing evidence, not any
single Σ²(L) curve. (3) The crystal "un-readable" claim is specifically about *density-unfolding* instruments; the
crystal is richly structured — just on Family IV, not Family II.
