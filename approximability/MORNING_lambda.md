# MORNING_λ — the λ-sweep: Θ(G) is a finite-λ crossover; the golden anchor is a DEGT corollary (0.546, not ½)

Branch off `cubics-wilderness`. The λ-extension of the g̃(a,f) surface. main/refsuite untouched.

## The conjecture and its refutation
Session I/J established g̃(a,f) universal AT λ=8. The λ-extension conjecture was g̃(a,f,λ)=λ^{Θ(G)−1} with Θ(G)
λ-INDEPENDENT (G=a/(1−f)=q-growth). **REFUTED** by the metallic-mean sweep (λ=4,8,16): Θ drifts monotone +0.05…+0.10,
orders of magnitude outside propagated bands. The gorgeous λ=8 collapse Θ(G) is a **finite-λ crossover**, not the
asymptotic law. (Pre-registered OUTCOME 3.)

## The scaling underneath, and the precision wall
Raw factor F=W_{k−1}/W_k scales as F~λ^{η}: η(a=1)≈½-ish, η(a≥2)≈1 at λ=8, BUT η itself runs with f (0→1 within a=1)
and with λ — factor(G,λ) is a genuine two-variable object, no power-law separation. Pushing to λ=32,64 hit the
**double-precision band-resolution wall**: for self-similar golden the depth-pair factor scatter grows 3-digit(λ=4)→
1%(λ=8)→5%(λ=16)→30%(λ=32)→2×(λ=64) — bands narrower than E-bisection can locate. Diagnosed as precision (monotone
scatter growth), NOT physical drift. Reliable range (λ=4→8): η=0.499.

## The golden anchor — DEGT corollary, not ½
The "√λ / η=½" read was the **8th low-λ shadow** of the run. The exact value:
  dim·log λ → log(1+√2)=0.88137  (DEGT, Fibonacci strong coupling)
  dim = log q/(log q − log W), q_k~φ^k, W_k~λ^{−θk}  ⇒  dim·log λ → log φ/θ
  ⇒  **θ_∞(golden) = log φ / log(1+√2) = 0.54598**, NOT ½.
CONFIRMED on data: dim·log λ = 0.676/0.754/0.789 (λ=4,8,16), climbing toward 0.881 (approach 0.881−0.28/log λ).
θ data 0.414/0.442/0.460 fits →0.546 as well as →0.5; the data can't separate them, DEGT (theorem) pins 0.546.
**No trace-map derivation needed — the bandwidth exponent is a direct corollary of the proven dimension law.**

## Landing
- **λ=8 fixed-coupling arc: COMPLETE & banked** (direction closed-form 17/17+68/68; magnitude universal g̃(a,f)).
- **λ→∞: golden anchor EXACT = logφ/log(1+√2) (DEGT).** The general Θ_∞(G) surface = large-coupling dimension
  asymptotics for general Sturmian frequencies (harder DEGT-type literature) — a named separate investigation.
- The √λ was a coordinate/low-λ artifact. Caught by cross-checking the TARGET against the theorem before deriving.

## ADDENDUM — reconciled with prior Panel A (the λ→∞ work was ALREADY DONE)
A search surfaced **Panel A** (`FINDINGS.md`, `panel_A_C_levy.csv`, `thread3_constants.py`, `DOUBLING_BACK.md`):
the λ→∞ layer was substantially mapped already. Corrections to the above:
- **C ≡ dim·ln λ (λ→∞) is Panel A's object**, with metallic ladder C(golden)=0.877, silver 0.867, bronze 0.913,
  m-4 1.022; **golden C=ln(1+√2)=0.8814 (DEGT 2008), prior-verified to −0.4%.** So today's golden anchor
  θ_∞=logφ/ln(1+√2)=0.546 is CONFIRMED by prior work, not new.
- **Order parameter already identified:** liminf K=liminf(a₁···a_k)^{1/k} (Liu–Wen 2004). dim<1 ⟺ liminf K<∞;
  C finite ⟺ liminf K<∞. **e has liminf K=∞ (theorem) → no finite C** (dim·lnλ diverges).
- **Bridge: θ_∞(metallic a) = L_a/C_a** (Lévy over DEGT const): golden 0.549✓, silver 1.02, bronze 1.31 — so ALL
  today's λ=8 θ-values (incl a≥2 "saturation at ~1") are finite-λ shadows; θ_∞ grows past 1 with a.
- **`thouless_law.py` already flagged the a=1/√λ subtlety** (a=1→ratio-1 contradicts Sütő; golden test set up).
CORRECTION to my prior "λ→∞ general surface = unexplored separate investigation": the metallic ladder + order
parameter are DONE. Genuinely-new-today = the finite-DEPTH fixed-λ layer (direction law + g̃(a,f) universality).
Still open: non-metallic/general-frequency C beyond golden's closed form (Liu–Wen frames it via liminf-K, no closed forms a≥2).
