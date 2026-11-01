# Review of fpgafun `fabric/words.py` (seed of ars-bridge C2), 2026-10-31

This is an independent first-pass review. It covers `~/fpgafun/fabric/words.py` (535 lines, commit 4d1026d) and
`~/fpgafun/tests/test_words.py`. `tests/test_slipword.py` was read only to see how the module is used. Nothing under
~/fpgafun was modified. Tests ran with `PYTHONDONTWRITEBYTECODE=1`, `NUMBA_CACHE_DIR` set to the scratchpad and
`-p no:cacheprovider`. The probe scripts ran with `python -I` and `sys.dont_write_bytecode`. All probes are exact
(Python ints and Fractions). The references were mpmath at 200 digits, brute-force factor sets and exhaustive
enumeration.

**Test run:** `tests/test_words.py` plus `tests/test_slipword.py`: **38 passed** in 4.7 s.

## Verified correct (no action needed)

- **Definitions match Lothaire ch. 2.**
  - Lower mechanical: s_{α,ρ}(n) = ⌊(n+1)α+ρ⌋ − ⌊nα+ρ⌋. Upper: the same with ⌈ ⌉.
  - c_α = s_{α,0}[1:], with s_{α,0} = 0·c_α and s'_{α,0} = 1·c_α. Both are tested against the substitution fixed
    point.
  - Rotation coding: letter 1 iff {nα+ρ} ∈ [1−α, 1), for the lower word.
- **Density vs line slope.** β = α/(1−α), and the two CF conversions (`density_cf_from_line`, `line_cf_from_density`)
  are right on both branches (b₀ ≥ 1 and b₀ = 0; a₁ = 1 and a₁ ≥ 2).
  - Fibonacci: density 1/φ² = [0;2,1,1,…], line slope 1/φ = [0;1,1,…].
  - Silver: the fixed point of 0→001, 1→0 (the silver-mean substitution) has line slope √2−1 = [0;2,2,…] and density
    1−1/√2 = [0;3,2,2,…].
- **Christoffel words.** The density convention gives length q. The line convention (BLRS 2008: slope b/a, a zeros
  and b ones) gives length p+q. Both equal s_{p/(p+q),0}[0:p+q], which is the lower Christoffel word. Degenerate cases:
  (0,1) gives 0, (1,1) gives 1, line (1,0) gives 1.
- **Standard words.** s_1 = 0^{a₁−1}1 and s_n = s_{n−1}^{a_n} s_{n−2}, with |s_n| = q_n (tested). This is Lothaire's
  recursion with α = [0; 1+d₁, d₂, …] re-indexed to α = [0; a₁, a₂, …].
- **Exactness.**
  - `Quadratic.floor_mul`: ⌊(ka + ⌊kb√d⌋)/c⌋ = ⌊(ka + kb√d)/c⌋ because c is a positive integer. For kb < 0 it uses
    ⌊−y⌋ = −⌊y⌋−1, which holds because y is irrational. `Cubic` works the same way via `icbrt`.
  - Against mpmath at 200 digits: 2149 checks of `floor_mul` with |k| from 1 to about 10⁵⁷ (including negative k,
    10⁹, 10¹² and 2⁶⁴−1), on all 5 named constants plus (5−3·7^{1/3})/4 and (7−11√13)/9. **0 mismatches.**
  - `icbrt` at r³−1, r³ and r³+1 for 2500 values of r up to about 10⁴⁵: 0 mismatches.
  - `floor_affine` with random ρ: OK.
  - `CBRT2_M1.cf(30)` equals the mpmath CF.
  - `simplest_in` with irrational endpoints (both lo_open modes) against brute force: 1200 cases, 0 mismatches.
  - The rational Python big-D path (D+P ≥ 2⁶²) against a Fraction reference: 30 × 200 letters, 0 mismatches.
  - Floats get in only through `as_exact(float)` (finding 9).
- **`Exact.cf` bracket argument is sound.** It keeps the common CF prefix of ⌊xS⌋/S and that value + 1/S, dropping
  the last term. Cylinder sets are intervals, so x shares that prefix.
- **`complexity`, `complexity_at`, `imbalance`, `slope`, `runs`, `crc32_bits`** are exact on their stated domains.
  `complexity_at` index ranges were checked by hand: `code(64)` blocks and `code(r)` tail.

## Findings

**1. bug: `sb_path`'s "earlier terms are exact" claim is false.**
- **Where:** words.py:483–486 (docstring), 507–516.
- **Evidence:** 3000 random windows of mechanical words. Slopes were 6 irrationals plus random p/q; intercepts,
  starts, lengths (2–4000) and lower/upper were all random. In **683 of 3000** windows (192/1500 irrational,
  491/1499 rational), `cf[:-1]` is **not** a prefix of the true line CF. Every failure has a non-canonical tail
  `[…, a, 1]` with `a` short. Examples:
  - silver, n=638: `[0,2,2,2,2,2,1,1]` vs true `[0,2,2,2,2,2,2,2,…]`
  - ∛2−1, n=479: `[0,2,1,5,1,1,3,1]` vs `[0,2,1,5,1,1,4,1,…]`
  - √3/6, n=2303: `[0,2,2,6,2,6,1,1]` vs `[0,2,2,6,2,6,2,6,…]`
- **Repair check:** folding a trailing 1 into the term before it (`[…,a,1] → […,a+1]`) makes all-but-last correct in
  **3000/3000** cases.
- **Fix:** normalise the tail before returning, or state "all but the last two terms". Add a randomized-window CF test.
  C5 item 2 ("CF recovery returns the exact expansions") depends on this.

**2. bug: `sb_path(...)["balanced"]` is not a balance certificate.**
- **Where:** words.py:487–506. The per-level `[:-1]` truncation at line 506 throws away the evidence.
- **Evidence:**
  - Exhaustive over all binary words of length 2–16: **990** unbalanced words are reported `balanced=True`. The
    smallest is `000101`, where windows 000 and 101 have sums 0 and 2.
  - Flipping the **last** letter of a 5000-letter silver or ∛2−1 characteristic word is reported balanced.
  - (Interior flips, random words and long-window kinks are caught.)
- **Fix:** document the flag as "not refuted" (rename it), or compute balance exactly and separately (finding 7).

**3. bug / convention risk: `is_sturmian_factor` with its default `nmax=64` accepts unbalanced words.**
- **Where:** words.py:447–454.
- **Evidence:** build the √2−1 lower word (40 000 letters), then continue the same line with slope +10⁻⁵, −10⁻⁶ or
  +10⁻⁷. `is_sturmian_factor` returns **True**, and p(n) ≤ n+1 holds up to 64. The first window with imbalance ≥ 2 is
  **n = 408, 985 and 2378** respectively. (`sb_path` does catch these.)
- **Background:** a finite word is a factor of a Sturmian word **iff it is balanced** (Lothaire Prop. 2.1.17, from
  memory). So:
  - The p(n) part adds nothing once balance is checked at every length.
  - The "or skew-Sturmian" wording is misleading.
  - With `nmax ≥ len(w)` the test would be exact, but it costs O(N²).
- **Fix:** an exact O(N) balance test (finding 7). Until then, make the default `nmax=len(w)` or require it
  explicitly. For "Sturmian to length L", balance must be checked at every window length up to L.

**4. bug: `best_rational` truncates the CF at 80 terms.**
- **Where:** words.py:216.
- **Evidence:** `best_rational(INV_PHI, 2**64)` returns 14472334024676221/23416728348467685, a 55-bit denominator.
  The convergent 7540113804746346429/12200160415121876738 (64-bit, ≤ 2⁶⁴) is closer. F₈₁ < 2⁶⁴, so the bound the
  code itself states (q ≤ 2⁶⁴) is not met.
- **Second issue (nit), lines 228–232:** candidates are ranked against ⌊x·2²⁰⁰⌋/2²⁰⁰. For candidates on opposite
  sides of x, the gap between distances is |p/q + p′/q′ − 2x|. For a quadratic x that can be as small as about 2⁻²⁵⁶
  at q ≈ 2⁶⁴ (Liouville), and smaller still for a cubic. So the ranking is not provably exact.
- **Fix:** extend the CF until q_n > max_den. Compare distances exactly by testing the midpoint (pq′+p′q)/(2qq′) with
  `x.lt` / `x.le`.

**5. convention risk: "closest rational" is not "longest agreement".**
- **Where:** test_words.py:164–167 ("hardware golden choice") and words.py:213.
- **Evidence (prefix agreement at intercept 0):**

  | Target | Choice | Side of x | Agreement length L |
  |---|---|---|---|
  | 1/φ² | F₄₅/F₄₇ = 1134903170/2971215073 (pinned, closest) | above | 2 971 215 072 |
  | 1/φ² | F₄₄/F₄₆ = 701408733/1836311903 (smaller denominator) | below | **4 807 526 975** |
  | √2−1 | 1311738121/3166815962 (closest) | above | 3.17·10⁹ |
  | √2−1 | 543339720/1311738121 | below | **4.48·10⁹** |

- **Why:** `agreement_length` is asymmetric. From above, L = q−1. From below, L = (next denominator inside the
  interval) − 1.
- **Factor (shift-invariant) agreement is symmetric** and ranks the candidates differently again (finding 6).
- **Fix:** pin which L the manifest uses before freezing F/ref_F. Then pick the hardware rational by that criterion,
  not by closeness.

**6. missing / convention risk: three different "agreement lengths"; only one exists, and not the one hardware needs.**
- **Where:** words.py:368–378.
- **(a) Prefix agreement, intercept 0, lower words.** Implemented. Hardware words carry an intercept ρ ≠ 0 (slipword
  `hw_slope_intercept`). Prefix agreement with ρ ≠ 0 is an inhomogeneous problem: find the first k with a j such that
  (j−ρ)/k lies between x and y. `simplest_in` does not solve it. The upper-word variant ([lo, hi)) is also missing.
- **(b) Factor agreement: every length-n factor of the rational word is a factor of slope-x Sturmian words.** This is
  intercept-free. Brute force on factor sets gives **L_f = k° − 1**, where k° is the smallest denominator of a
  fraction strictly between r and x. For convergents this is q_k + q_{k+1} − 1.
  - 1/φ² convergents: 1/3 → 7, 2/5 → 12, 3/8 → 20, …, 34/89 → 232, on both sides.
  - 17/17 random rationals near ∛2−1 and silver match, with the target taken at intercept 1/7.
  - This agrees with the Farey-interval theorem for factors of length n (Mignosi 1991; Berstel–Pocchiola).
    It can be computed with `simplest_in` given an open-open interval.
- **(c) Complexity.** The period-q word has p(n) = n+1 only for n ≤ q−1, and p(n) = q after that.
- **Consequence for the A4 ingest rule** ("p(n) = n+1 and balance applied for n ≤ L"):
  - It is unsatisfiable once L ≥ q. Prefix L can exceed q (4.8·10⁹ > 1.8·10⁹ in finding 5), and L_f > q always holds
    for convergents.
  - On any finite word of length N, p(n) ≤ N−n+1, so equality can only hold for n ≲ N/2.
  - **Fix:** the rule should read "balanced and p(n) ≤ n+1 for n ≤ L", or cap the p(n) = n+1 test at min(L, q−1).
- **Also needed:** a function that takes (p/q, ρ, x) and returns (L_prefix(ρ), L_factor, q−1).

**7. missing: exact slope set / digital-straight-segment recognition.**
- **What:** for a finite w, the set of (α, ρ) with w = mechanical(α, ρ)[0:N] is a convex polygon. It can be computed
  incrementally in O(N) (arithmetic DSS recognition, Debled-Rennesson & Reveillès 1995).
- **What it gives:**
  - an exact O(N) balance test (fixing 2 and 3);
  - the exact density interval of a window, replacing the point estimate `slope()` and `sb_path`'s unreliable last
    term;
  - the exact meaning of "w is Sturmian of slope x to length L": x lies in the slope set of w[:L] (and ρ in it too,
    if intercept-matched).
- **Why it matters:** this is the natural primitive for hardware ingest at L ~ 10⁹, where O(N·nmax) windows are not
  enough.

**8. bug (hang): `exact_less` loops forever on equal irrationals, and so does `agreement_length`.**
- **Where:** words.py:360–365, 374–376.
- **Evidence:** `exact_less(INV_PHI, INV_PHI)` and
  `agreement_length(Quadratic(-1,1,5,2), Quadratic(-2,2,5,4))` both time out.
- **Fix:** normalise representations and test equality first, or cap the precision loop and raise.

**9. convention risk: floats slip in silently.**
- **Where:** words.py:158–162, 252.
- **Evidence:** `as_exact(0.38)` returns `Rational(3422735716801577/9007199254740992)`. `mechanical(0.38, …)` and
  float `rho` are accepted the same way.
- **Fix:** accept only int, Fraction or Exact, and raise on float.

**10. nit / bug: the letter dtype wraps silently.**
- **Where:** words.py:239–244, 273.
- **Evidence:**
  - `mechanical(Fraction(300), 4)` returns `[44 44 44 44]`.
  - An irrational α < 0, e.g. 1−√2, returns letters 255/0.
  - The rational path asserts only P ≥ 0, and the irrational path checks nothing.
- **Fix:** assert 0 ≤ α ≤ 1, or use a wider dtype.

**11. nit: `Quadratic` / `Cubic` accept b = 0.**
- **Where:** words.py:120, 141.
- **Evidence:** `Quadratic(1,0,2,2)` (= 1/2) is marked irrational. Its upper word comes out `110101` instead of
  `101010`.
- **Fix:** assert b ≠ 0.

**12. nit: edge cases.**
- `density_cf_from_line([0])` raises IndexError.
- `sb_path` returns cf `[0]` for both the all-ones word (β = ∞) and the all-zeros word (β = 0).
- Near density 0 or 1, a window holding one 1 returns `[0, 201]` for a word of line slope 1/999. It is flagged
  unreliable, but there is no way to tell "short" from "true".
- For rational words of at least 2q letters, `sb_path`'s value is exact: 1197/1197 at 2, 3 and 5 periods. It comes
  back in either CF form (`[0,1,1,1]` vs `[0,1,2]` for 2/5), still flagged `last_unreliable`, with no
  "terminated / periodic" flag. At 1.5q it is not exact (34/398 failures).
- `complexity_at(w, [n > len(w)])` raises ValueError.
- `standard_word` past the end of a finite CF raises IndexError.
- The `agreement_length` docstring says "c agree on L−1 letters", which is −1 when L = 0, e.g.
  `agreement_length(1/2, 1)`.

**13. convention risk: naming and indexing to pin in the shared spec.**
- **Silver word.** Some sources mean the characteristic word of *density* √2−1. The module (and the brief's
  line-slope statement) means the 0→001, 1→0 word, with density 1−1/√2. Every manifest should state the convention
  next to the CF.
- **Standard-word index.** The brief writes s_{n+1} = s_n^{a_n} s_{n−1}. Read literally with α = [0; a₁, …], that is
  shifted from the module's s_n = s_{n−1}^{a_n} s_{n−2}, and it does not show the a₁−1 exponent on the first step.
- **Citations.** The module cites Lothaire "Prop. 2.2.24". I did not check that number (no copy at hand), nor my own
  Prop. 2.1.17 above.

**14. Tests: what they do and do not pin.**
- **`test_cubic_word_cf_recovery`** (test_words.py:72–79) relies on the false claim in finding 1. It passes for this
  one window (intercept 0, start 1).
- **`test_sb_path_never_rejects_mechanical_factors`** (187–197) checks only the flag, never the CF.
- **Witnesses are too easy.** There is no must-fail near-Sturmian witness: no kink (finding 3), no last-letter flip
  (finding 2), nothing unbalanced only beyond `nmax`. The random-word witness fails at the smallest window lengths
  (n ≈ 3), so it cannot catch any of findings 2–3.
- **`test_christoffel`** pins `christoffel` only to `mechanical`. That is fine by the theorem, but `c[0]==0, c[-1]==1`
  does not pin the conjugate: for 2/5, both 00101 and 01001 pass. Add a lattice-path or Lyndon-minimal check.
- **`test_rational_fast_path_matches_python`** never reaches the D+P ≥ 2⁶² Python path (its largest D is about
  3.3·10¹⁰). I checked that path separately and it is correct.
- **`agreement_length`** is tested at intercept 0, lower words only.
- **`test_best_rational...`** pins closeness (finding 5).
- **`test_floor_mul_against_decimal`** sets the global `decimal` precision as a side effect (nit).
- **Tests that are independent and sound:** the Fibonacci and silver substitution known answers, the Fraction
  reference for the rational path, the brute force for `simplest_in` and `agreement_length`, and `complexity_at`
  against a brute-force count.

**15. nit: packaging.**
- The C2 spec says "pure Python". The module imports numba at load time, and `cache=True` writes next to the package.
- `crc32_bits` does not include the word length: `[0,1,0]` and `[0,1,0,0]` give the same CRC. The manifest must carry
  N alongside the CRC.

## Verdict

**The core is correct.** The exact arithmetic (Quadratic, Cubic, Rational floor; `simplest_in`; `Exact.cf`), the
generators (mechanical lower/upper with intercept, characteristic, Christoffel in both conventions, standard words)
and the stated conventions are right. I found no float leakage on the exact path and no off-by-one.

**The check layer over-claims.**
- `sb_path`'s penultimate CF term is wrong in about 23% of random windows (fixable by a one-line tail
  normalisation).
- Its `balanced` flag accepts unbalanced words.
- `is_sturmian_factor` at `nmax=64` accepts words that become unbalanced at n ≈ 400–2400.
- `best_rational` truncates at 80 CF terms.
- The only agreement length implemented (prefix, intercept 0) is not the one hardware words with an intercept need.
  Together with findings 5–6, the A4 ingest rule "p(n) = n+1 for n ≤ L" needs restating.

**Recommendation:** do not seal it as the ars-bridge seed yet. First fix findings 1, 2, 3, 4 and 8. Then pin the
agreement-length definition (finding 6) and add an exact DSS / slope-set primitive (finding 7) with near-Sturmian
must-fail witnesses.

---
**Main-session reproduction (2026-10-31; read-only import of ~/fpgafun/fabric/words.py @ 4d1026d).**
- **Bug 2 confirmed.** `sb_path([0,0,0,1,0,1])` returns `balanced: True`, while `imbalance` of the same word shows 2.
- **Bug 1 confirmed.** In 37 of 300 random windows of the silver mechanical word (200–2000 letters, random start), a
  term other than the last is wrong. Example: start 511136, length 685 gives [0, 2, 2, 2, 2, 2, 1, 1].
- Not re-checked here: findings 3–5, the agreement-length analysis and the smaller items.
