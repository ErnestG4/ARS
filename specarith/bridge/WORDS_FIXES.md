# ars-bridge C2 (`words.py`): required fixes, as review findings

Basis: the fresh review (`WORDS_REVIEW.md`) of the seed `~/fpgafun/handoff/ars-bridge-c2/ars_bridge/words.py` (pll-fabric
886e6ac). Its findings 1 and 2 were reproduced in the specarith session.

**Will (2026-11-01):** no staging copy. These findings are the specification. The fixed file is committed as the first
commit of `ars-bridge` once Will creates the repo, and pll-fabric then imports it.

Each finding gives: what is wrong, the required behaviour, and the acceptance test the fixed file must ship. Severity:
**B** (bug), **C** (convention, needed for hardware words), **S** (small).

## B1. `sb_path` continued-fraction recovery

**Problem.** A term before the last is wrong when the decoded word ends in a trailing 1. The fresh review found 683 of
3000 random windows across words wrong; the main session reproduced 37/300 on silver windows. Example: start 511136,
length 685 gives [0,2,2,2,2,2,1,1].

**Required.**
- Fold a trailing 1 into the term before it.
- State the contract precisely: every term except the last is exact, and the last term is a lower bound.
- Add `complete: bool`: True iff the window spans at least two periods of a rational word. The CF is then that rational's
  exact CF.

**Acceptance.** 3000 seeded random windows (100–5000 letters) of each of the golden, silver and ∛2 − 1 words, at random
starts and intercepts: all terms but the last equal the true CF, 3000/3000. Rational words p/q at least two periods
long: `complete` is True and the CF equals `cf_of_fraction(p/q)`.

## B2. `sb_path`'s `balanced` flag

**Problem.** It is not a balance test. Each level drops its last letter, which discards the evidence. 990 unbalanced
words of length ≤ 16 pass, the smallest being `000101`.

**Required.** Remove the flag from `sb_path`, or compute it with the exact balance test of C3 below.

**Acceptance.** For every binary word of length ≤ 18, the flag equals brute-force balance: max over equal-length windows
of the difference in 1-counts ≤ 1.

## B3. `is_sturmian_factor`

**Problem.** The default window cap of 64 accepts unbalanced words: slope-kinked √2 − 1 words go unbalanced only at
408, 985 and 2378 letters.

**Required.** A finite binary word is a factor of a Sturmian word iff it is balanced, so define the function as the
exact balance test (C3) over all window lengths. p(n) ≤ n + 1 may be reported, but it is not the criterion.

**Acceptance.**
- The kinked words are rejected at their first unbalance length.
- Must-fail witnesses are rejected: a last-letter flip of a 5000-letter silver word and of a ∛2 word, and a slope kink
  of 10⁻⁵ … 10⁻⁷.
- Every Sturmian window in B1's suite is accepted.

## B4. `best_rational`

**Problem.** It stops after 80 CF terms: `best_rational(INV_PHI, 2**64)` returns a 55-bit denominator when a closer
64-bit convergent exists. Its ranking against a 2⁻²⁰⁰ approximation is not provably exact.

**Required.**
- No term cap: walk convergents and semiconvergents until the denominator bound.
- Compare |x − p/q| exactly with the module's exact types, not with a float or a 2⁻²⁰⁰ proxy.

**Acceptance.**
- `best_rational(INV_PHI, 2**64)` is the largest Fibonacci ratio within the bound.
- For bounds ≤ 2000 and 20 targets (golden, silver, ∛2 − 1 and random quadratics), it equals brute force over all q ≤ bound.

## B5. `exact_less` and `agreement_length` on equal numbers

**Problem.** Both hang on equal irrationals written two ways, e.g. `Quadratic(-1,1,5,2)` and `Quadratic(-2,2,5,4)`.

**Required.** Canonicalise `Quadratic` and `Cubic`: gcd-reduce, with a sign convention. Detect equality before
comparing. For equal arguments, `exact_less` returns False and `agreement_length` returns `None` (meaning infinite),
documented as such.

**Acceptance.** Equal pairs in several representations return at once. A property test checks that `exact_less` is
consistent with mpmath at 200 digits on 2000 random pairs.

## C1. Agreement lengths: name both, and add the intercept-free one

The existing function is prefix agreement at intercept 0. Hardware words carry an intercept, and ingest needs the
intercept-free version.

**Required.**
- `prefix_agreement(p_q, target, rho=0)`: the longest common prefix of the mechanical words at intercept ρ. This
  generalises the current function. The upper and lower variants are both stated.
- `factor_agreement(p_q, target)`: the largest L such that every length-n factor of the rational word, for n ≤ L, is a
  factor of the target's Sturmian word. Per the review: (the smallest denominator strictly between p/q and the target)
  − 1, i.e. q_k + q_{k+1} − 1 at a convergent, built on `simplest_in`.

**Acceptance.** `factor_agreement` equals brute force (factor sets up to length 2q) on at least 40 cases: convergents,
semiconvergents and random rationals near golden, silver and ∛2 − 1.

## C2. "Closest" is not "longest agreement"

**Problem.** F45/F47, the current "hardware golden choice", agrees for 2,971,215,072 letters. F44/F46 agrees for
4,807,526,975.

**Required.**
- `longest_agreement_rational(target, max_den, kind="prefix"|"factor", rho=0)` returns the rational with the longest
  agreement, beside `best_rational` (the closest).
- The docstrings say which one the hardware manifests use.

**Acceptance.** Brute force for max_den ≤ 5000 on the three targets. The F44/F46 vs F45/F47 case is pinned as a test.

## C3. The exact slope-set / digital-straight-segment primitive

**Required.** `slope_set(w)`: the exact set of (α, ρ) for which w is the mechanical word, empty iff w is not balanced,
in O(N) time with exact arithmetic. It gives:
- an exact balance test (B2, B3);
- the exact slope interval of a window;
- `is_mechanical(w, alpha, rho_range)`, i.e. "Sturmian of slope x to length L", with or without a fixed intercept, for
  lower and upper words.

**Acceptance.**
- Brute-force agreement on all binary words of length ≤ 18.
- The slope interval of a Sturmian window contains the true slope, and its endpoints are the neighbouring Farey
  fractions of the window length.

## C4. Manifest-facing conventions

**Required.**
- Every function that takes a slope names its convention: `density` or `line`. The manifest field is
  `slope_convention`.
- `crc32_bits` is documented as not encoding the length (`[0,1,0]` and `[0,1,0,0]` collide), so manifests carry the
  length beside the CRC. Alternatively, provide a length-prefixed CRC.

## S. Smaller items

- **Floats.** `as_exact` raises on a float, unless an explicit `allow_float=True` is given (`as_exact(0.38)` currently
  becomes a dyadic rational without warning).
- **Letters.** Validate them to {0, 1}: a slope outside [0, 1] or a negative irrational slope raises, instead of wrapping
  in uint8 (slope 300 → letter 44; −x → 255).
- **`Quadratic` with b = 0.** Fix the upper word.
- **Constant words.** `sb_path` distinguishes all-0 from all-1 (currently [0] for both) and reports `complete` for them.
- **Citations.** Check the "Prop. 2.2.24" citation and Lothaire Prop. 2.1.17 against the book, or remove them.

## Tests (beyond the acceptance tests above)

- The cubic CF test must check many windows, not the one that passes only because of B1.
- The random-window `sb_path` test must assert the CF, not only the flag.
- The random-word witness must include near-Sturmian must-fail words: last-letter flip, slope kink, `000101`.
- The Christoffel test must pin the exact rotation: the lower Christoffel word starts with 0 and ends with 1, and must be
  exactly 00101 for 2/5, not 01001.
- The large-denominator (≥ 2⁶²) path must be exercised against a `Fraction` reference.
- The known-answer tests of the shared spec stay: Fibonacci → [0;1,1,1,…] (line slope), silver → [0;2,2,…], Christoffel
  p/q period q, Sturmian complexity n + 1 and balanced, and a random word failing both.

**Licence:** AGPL-3.0-or-later (SPDX header kept).
