# MORNING_B — Session B: Diatonic full battery + π-292 follow-up (queue #3)

Branch `rf-promo-diatonic-battery`. Banked instruments only; certified engine frozen; refsuite frozen.
`$HOME/fmexplorer/bin/python3`, `PYTHONPATH=…/riemann_explorer`, `BASE_SEED=20240517`.

## Layer-zero gates
- **B-Z1 (musical, fresh, two-precision):** CF of α=log₂(3/2) computed in-session at dps {50, 80, 150}; banked only
  where **all three agree** — they agree to depth 16. Banked CF `[1,1,2,2,3,1,5,2,23,2,2,1,1,55,1,4]`; convergent
  ladder `1,2,5,12,41,53,306,665,15601` reproduces the historical tuning denominators; q=12 is a cell (white keys).
  **PASS.** (Caught mid-run: an earlier single-precision pass to depth 14 was ungated — the two-precision gate is
  what certifies the deep quotients, and it does: a=55 is real, see below.)
- **B-Z2 (spectral):** banked π depth-5 Floquet reloaded; `count_eq_q` PASS (33215 bands == q). **PASS.**

## π-292 depth 6→8 — **STOP-AND-BANK (infeasible with certified machinery).**
π convergent denominators: q₆=66317, q₇=99532, q₈=265381. Dense Floquet (the certified engine) needs q²·8 bytes:
**35 GB (q₆) / 79 GB (q₇) / 563 GB (q₈)** vs **15 GB RAM**. Depths 6–8 require a sparse shift-invert eigensolver =
**new machinery → banked as a dedicated session.** Depth-5 remains the certified frontier; no depth curve produced.
- **Liu–Wen label — downgraded to INTUITED, and moot.** The pre-reg called the "dimension retreats as finite-depth K
  relaxes" direction *derived from Liu–Wen*. Verified against the theorem's content: Liu–Wen 2004 is an **asymptotic**
  `dim_H σ<1 ⟺ liminf K<∞` statement — it does **not** predict the finite-depth dimension-trajectory *direction*. That
  direction is governed by the banked Thouless m_k / q-vs-W race (the homecoming run already **demoted** the K-coupling
  for exactly this reason). So the label is **intuited, not derived** — and unmeasurable this session regardless.
  Banked breadcrumb: sparse-eigensolver π-292 depth 6–8 + the finite-depth-vs-K direction question.

## The fifth's arc-table row — all five faces + fingerprint
Artifacts: `fifth_battery.py`, `fifth_battery.json`, `fifth_battery_faces.png`.

| face | instrument | reading for α=log₂(3/2) |
|---|---|---|
| 1 dimension (banked) | Floquet + bs_dim | 0.466 / 0.342 / 0.321 (λ=8/24/32); **below π**; rises at the a=23 step |
| 2 bandwidth-law (banked) | Thouless g(a) | g(23)≈1.00 (saturated by a=5); a=1 older-block deficit monotone in q_{k−2}/q_k |
| 3 gap-labeling (banked) | Bellissard IDS | q=53 gaps = pitch classes (fifth 5.7e-5…); two widest gaps = 4th & 5th |
| **4 record process (NEW)** | Panel-D `records` | record clock **1,2,3,5,23,55**; Λ-cusp **a=55 @ CF-pos 14** |
| **5 Farey aperture (NEW)** | D3 q_min (Thread-D-verified) | q_min ladder = Stern-Brocot semiconvergents; big jumps at the **a=23 and a=55 blocks** |
| fingerprint (10-D) | `full_analysis` | KS_GUE/GOE/Poisson 0.39/0.37/0.44, **mass<0.3 = 0.00, repulsion = 0.90** (rigid/clock), padic-prime 7 |

**Verdict — the fifth is axis-dependent ("class visible, not decided"), self-consistent across faces.**
- The **spacing/marginal faces read RIGID/clock** — mass<0.3 = 0.00, repulsion = 0.90: the diatonic Sturmian word is
  3-distance-rigid (generic to all Sturmian words, not fifth-specific), so the fingerprint carries no Λ-cusp.
- The **arithmetic faces (record + Farey) both flag the Λ-cusp** — exactly as pre-registered *conditional on the fresh
  CF carrying large quotients*, which B-Z1 confirms (a=23, a=55).
- **Cross-face self-consistency (the good outcome, stated plainly):** the a=23 cusp shows on **three** faces at once —
  the spectral dimension (rises at the 23 step), the record clock, and the Farey aperture. The arithmetic faces then
  see **further than the spectral run could reach**: the two-precision-verified record clock climbs to **a=55 at
  position 14**, a deeper Λ-cusp than the a=23/q=15601 frontier of the certified eigensolve. Same object, coherent
  across observables — the observable-binding thesis again, and the arithmetic faces are the cheap ones that reach
  deepest.

**New substantive datum:** the fifth's Λ-cusp is **a=55** (verified, deeper than the homecoming a=23) — the record
and Farey faces are the ones that surface it. It plays π's 292 role but milder, and it sits beyond the spectral
frontier, so it's a genuinely new read the homecoming run could not have produced.

## Session-B close
- The fifth's arc-table row is **complete** (5 faces + fingerprint). No promotion verdict (certified instruments);
  the deliverable is the row + the axis-dependent-class reading + the a=55 finding.
- π-292 depth extension **banked** (RAM wall; sparse eigensolver = new machinery); Liu–Wen label downgraded to intuited.
- Carry-forward: (a) a=55 Λ-cusp for the arc-table narrative; (b) sparse-eigensolver π-292 depths 6–8; (c) Liu–Wen
  finite-depth-direction stays intuited (not a theorem) — a queue breadcrumb alongside Thouless #5.
