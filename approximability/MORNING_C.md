# MORNING_C — CF-cusp cartography of the fifth + FGK banking

Branch `cf-cusp-cartography` off `d15eab4` (**not** master: master 859907c lacks the Session-B artifacts Part 2 reads
from; the prior block's branch is unmerged/unpushed). `$HOME/fmexplorer/bin/python3`,
`PYTHONPATH=…/riemann_explorer`, `BASE_SEED=20240517`. Certified/banked machinery only.

**Pre-flight flag:** block base **not confirmed pushed** — no SSH agent this session (socket doesn't survive across
sessions), and `git@codeberg.org: Permission denied` still. Work is local on the branch; push stays user-driven
(needs `!ssh-agent … ssh-add` then `!git push`). No master or refsuite touched.

## Part 0 — prior-block digest (absorbed)
The five planning-layer reads are noted; two are load-bearing here. **#3 (instrument reach, not the fifth):** the cheap
faces out-reach the eigensolve — this session maps that. **#5 (cross-context contamination watch-flag):** setq()/memo
staleness was the 2nd sighting (padic v1–3 the 1st); one more earns a §9 guard. The others feed carry-forward: #2's
β≈⅓·ln q check and Liu–Wen→Thouless(#5)-on-the-critical-path stay queued, unstarted (new machinery).

## Part 1 — Queue #2 (FGK) BANKED: retired, verify killed the build (zero compute)
Provenance corrected against source; the kill fact verified numerically (`fifth_cusp_map.py` sibling check).

- **Bound exists & is proven** (Donoho–Stark support-product form): `⌈n^d/M⌉ ≤ |supp f|·|supp f̂|`, M = largest orbit
  (superclass). Source = **Brumbaugh et al., "Supercharacters, exponential sums, and the uncertainty principle,"
  arXiv:1208.5271, J. Number Theory 144 (2014) 151–175** (Thm 1 / eq. 3.5).
- **Provenance correction (the queue named two wrong papers):** the UP is **not** in Garcia–Huber–Lutz (1312.1034,
  algebraic-only, Heilbronn sums) nor in Fowler–Garcia–Karaali (1201.1060, the Ramanujan-identities paper that is
  Thread B's *actual* c_q-multiplicativity source). It is in the third overlapping-author paper (1208.5271). The prior
  breadcrumb (`rf_lenses/MORNING.md`) attributed it loosely to "FGK" — corrected here.
- **The kill (VERIFIED numerically):** for the Ramanujan-sum supercharacter theory Γ=(ℤ/nℤ)^×, the supercharacters
  *are* the c_q and the largest orbit is φ(n), so the ceiling is `⌈n/φ(n)⌉`. Computed: **exactly 2 for prime n**
  (vacuous), and worst-case only 3.75→4.38→4.81→5.21 at n≤10²…10⁵ — doubly-log, matching Mertens `n/φ(n) ≲ e^γ·ln ln n`.
  So the UP ceiling is **trivial exactly on the RF-multiplicativity substrate**; a c_q concentration axis would measure
  against a vacuous ceiling. The paper's authors flag this themselves (φ(n) nearly as large as n).
- **No Tao rescue:** the strong support-*sum* bound (`p+1 ≤ |supp f|+|supp f̂|`) rests on Chebotarëv all-minors-invertible,
  which fails for supercharacter matrices and for c_q specifically (von Sterneck/Möbius vanishing). No back door.
- **Verdict: queue #2 RETIRED — the promised "§9-grade axis with a hard limit" does not exist for c_q.** (Fact vs
  judgment kept apart: the φ(n) triviality is a computation; "not worth building" is the planning call.)
- **New queue candidate BANKED (own row, NOT started — new substrate):** *concentration axis on Gauss/Kloosterman
  substrates, where the UP is nontrivial (M ≪ n^d).* Verified the non-triviality: Kloosterman orbits (p−1) against
  ambient p² give a **linear** ceiling ~p+2 (8.17→1010 for p=7→1009); Gauss periods of order k give ~k+1. These carry a
  genuine hard limit — but do **not** couple to RF-multiplicativity; a fresh candidate on its own merits, not a #2 revival.

## Part 2 — Session C: the fifth's CF-cusp reach cartography
Artifacts: `fifth_cusp_map.py`, `fifth_cusp_map.json`, `fifth_cusp_reach.png`. Banked instruments only (Panel-D
`records`; Thread-D-verified Farey `q_min`).

**Layer-zero.** C-Z1: three-precision CF gate (dps 50/80/150) agrees to **depth 48**; the prefix matches the certified
d15eab4 CF exactly (not read from memory/spec). C-Z2: quotients/convergents integer; **a=23 at CF-position 9 → q=15601**
= the spectral frontier. Cusp threshold **a_k ≥ 10** (pre-registered *convention*, not derived; GK
`P(a=k)=log₂(1+1/(k(k+2)))`).

**The cusp map (8 cusps to depth 48) and its verdict — the two-tier pre-registration became a THREE-tier nesting.**

| pos | a | q_k | record clock | Farey aperture | spectral reach |
|---|---|---|---|---|---|
| 9 | 23 | 1.56e4 | ✓ | ✓ | **joint** |
| 14 | 55 | 1.06e7 | ✓ | ✓ | arithmetic-only |
| 20 | 15 | 6.19e9 | ✗ | ✓ | arithmetic-only |
| 31 | 11 | 5.75e15 | ✗ | ✓ | arithmetic-only |
| 33 | 20 | 1.30e17 | ✗ | ✓ | arithmetic-only |
| 36 | 10 | 4.24e18 | ✗ | ✓ | arithmetic-only |
| 44 | 37 | 7.74e21 | ✗ | ✓ | arithmetic-only |
| 46 | 55 | 1.72e24 | ✗ | ✓ | arithmetic-only |

- **a=55 co-registration — PRE-REG LANDS.** a=55 shows on **both** cheap faces (record ✓, Farey ✓), mirroring a=23. The
  falsification-that-mattered (a=55 *not* co-registering → a=23's joint read was a within-reach artifact) **did not
  fire**: cross-face self-consistency does extend past the spectral frontier.
- **NEW (beyond pre-reg): the two cheap faces are NOT equivalent — reach is a nested hierarchy, not one horizon.**
  - **Eigensolve** reaches **a=23 only** (q≤15601): 1 cusp.
  - **Record clock** reaches **records only — {23, 55}** — then saturates (nothing later exceeds 55): 2 cusps.
  - **Farey aperture** reaches **every a≥10 cusp** (each gives a ≥10× q_min jump): all 8, to depth 48.
  So `Eigensolve ⊂ Record clock ⊂ Farey aperture`. Co-registration across cheap faces is a property of **records**, not
  of all cusps: a=23 and a=55 co-register *because they are the running records*; the deeper cusps (15,11,20,10,37,55′)
  register on Farey alone. This refines a=23's "joint on three faces" — the record/Farey agreement is record-conditional.
- **Reach horizon (pre-registered shape, confirmed + sharpened):** the horizon sits **exactly at the a=23 frontier
  (q=15601)** — only a=23 is jointly visible; every deeper cusp is arithmetic-face-only. The diatonic analog of the
  RF ⊥ Family-II "only off the flat corner" asymmetry: **a probe's reach is instrument-dependent, and out-of-reach is a
  finding, not a gap.** Here it's three-tiered.
- **π cross-comparison (DESCRIPTIVE, non-predictive).** π cusps (a≥10): 15 (q=106), 292 (q=33102), 14 (q=2.55e7).
  Fifth: 23,55,15,11,20,10,37,55. Shape difference (not over-read): π is **one-giant** (the 292 dominates); the fifth
  is **cusp-rich but cusp-mild** — many moderate cusps, no single giant. No theorem predicts this; label intuited.

**Deliverable statement (one sentence):** *Of the fifth's certified CF-cusps, the eigensolve sees only a=23, the record
clock sees the two running records {23,55}, and the Farey aperture sees all eight to depth 48 — a nested reach hierarchy
whose horizon sits exactly at the a=23/q=15601 spectral frontier.*

## Block close
- Both parts committed on branch `cf-cusp-cartography`. Master + refsuite untouched. Queue #2 retired + provenance-fixed;
  Gauss/Kloosterman concentration axis banked as a new independent candidate.
- **Carry-forward (unchanged + one sharpening):** genus>0 FF calibrator (new machinery; carries the β≈⅓·ln q check);
  π-292 depths 6–8 (sparse eigensolver **and** the Thouless #5 finite-depth predictor — coupled). Default next pick:
  **Thouless #5 verify** (cheap, unblocks π-292). New this session: the **three-tier reach hierarchy** is the fifth's
  arc-table "reach" dimension, and the record/Farey non-equivalence (record-conditional co-registration) is a reusable
  read on the cheap faces.
