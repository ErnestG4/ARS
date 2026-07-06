# Track 1.1 — Chialvo Map Calibrator · Configuration Justification

**Authored before execution** (brief non-negotiable). Phase 36. Date 2026-05-31.
Gated on Track 0 PASS (strict gate). Chialvo is a **calibrator** (known-ground-truth transition),
NOT a substrate-of-study.

## System & route (located by λ₁-Benettin scan, 2026-05-31)
Chialvo (1995) 2-D map: `x' = x² exp(y−x) + k`, `y' = a y − b x + c`. Fixed (b=0.45, k=0.06);
sweep recovery-decay **a** as the bifurcation parameter:
- **a≈0.89** — smooth 2-torus, λ₁≈0 (Benettin), ~3000 median-upcrossing events / 80k iter →
  the **pure-quasiperiodic / no-false-positive** regime.
- **a≈0.925–0.95** — Arnold-tongue mode-locking windows (λ₁<0).
- **a≈0.96** — torus-breakdown locus (λ₁ crosses 0⁺).
- **a≈0.97** — developed **chaos**, λ₁≈+0.054, ~4200 events / 80k iter → the post-breakdown regime.

Ground-truth loci: NS onset analytic (det J(fixed pt)=1, complex pair); torus-breakdown via λ₁=0
crossing (tangent-space Benettin — exact sign+magnitude for known equations, same tool class as
`mg_lyapunov_benettin`/`dynamical_breadth`). This is what makes it a calibrator.

## Instrument configuration (matched to the calibrator zoo — NOT chosen for convenience)
`N_SUBWINDOWS=30, MIN_EVENTS_PER_SUB=100, Q_MAX=25` — **identical to `run_phase20_5_calibrators`**
(logistic/Mackey-Glass live on this exact lens). Matching is the point: Chialvo must be read on the
same instrument the lens was validated on, so its verdict is comparable to the banked dynamical
calibrators. Events = **median-upcrossings of x_n** (the `dynamical_breadth` convention — NOT
find_peaks), discrete iteration index as the clock; downstream renormalises to unit mean.

- **Q_MAX=25**: the banked zoo value. The RF axis reads Farey-q bands up to 25; a quasiperiodic
  rotation number can have high-order rational approximants, so as a guard the run also reports a
  Q_MAX∈{25,50} sensitivity check on the detection trajectory (does the verdict move with q_max?).
- **Sub-window count 30**: matches the zoo; total event budget therefore needs ≥3000 events
  (30×100). Stationary regimes are iterated long enough to clear this (~200k iter).
- **No physical frequency scale**: this is a map (dimensionless iteration clock), so "frequency
  scale" reduces to events-per-subwindow, fixed by the zoo config above.

## Protocol & pre-registered verdict map
1. **Detection** — swept-a trajectory (a: 0.89→0.975, ~200k iter) → `characterize_transition`.
   PASS = `transition_detected=True` (any shape). The torus→chaos change in spacing statistics is
   the signal.
2. **No-false-positive** — stationary regimes at fixed a (A_QUASI=0.89 pure torus; ALSO A_CHAOS=0.97)
   → trajectory must be FLAT, `transition_detected=False`. Run first at the **N=2584-event** budget
   (matches the banked AM NFP number; n_subwindows scaled so ≥100 ev/sub), then EXTEND to the full
   3000+/30-subwindow zoo config. A stationary regime that does not flip = no false positive.
3. **Sensitivity** — vary total events (iteration count) on the detection trajectory; report the N
   floor at which detection is reliable. Compared to the banked AM floor (N≳5×10⁴, but that N is
   matrix dimension; here N is event count — the two are NOT collapsed, reported as separate numbers).
4. **Engine attribution** — per-subwindow `rep_int_q` median (NNS/spacing axis) vs `rf_spike`
   fraction / `rf_amplitude_q` (Ramanujan-Fourier axis) across the swept trajectory. Report WHICH
   axis carries the transition (torus breakdown may load on RF — quasiperiodic rotation-number
   spikes vanishing — or on NNS — spacing repulsion changing — or both). This is the template the
   AM leg established (AM loads on NNS rep_med, not RF).

## EPISTEMIC_STATE status tags (one entry, pre-registered vocabulary)
`{DETECTED-AT-LOCUS, NFP-CONFIRMED, SENSITIVITY-BOUNDED, FAILED}`. A FAILED calibrator is a finding,
banked not discarded. STRICT GATE: Chialvo must reach DETECTED-AT-LOCUS + NFP-CONFIRMED before the
Kaneko GCM calibrator (Track 1.4) is built; otherwise that branch halts and the FAIL is banked.

## Out of scope
Forced-Hodgkin-Huxley and Baesens-Guckenheimer-Kim-MacKay (continuous-time ODE calibrators) are
DEFERRED to a dedicated engineering arc (per the chosen discrete-maps-first policy). No real data.
