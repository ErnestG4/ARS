# Phase 6 code review, third pass (2026-10-07)

**Scope:** `git diff 1fc3552 HEAD -- specarith/ph6/*.py` on branch ph6-xp (HEAD 0d8c038). That covers `preread.py`
(the g1_block/g2_block refactor, `--proposed`), `gates.py` (`maass_gate(name=)`, the G1s_*/G2s_* loops, G2-s RP13),
`make_seal_json.py` (new, with `--pre`), `chi4_zeros_v2.py` (T_LO), `known_answers`' skip, and `synth_run.py`.
Context read: PH6_PROPOSED_AMENDMENTS.md (A1, A4, A6, A12), MORNING_2026-10-07.md, DATA_MANIFEST.md, and the committed
`results/preread*` metadata.

**Rules kept:** I loaded no zero or Maass data file, computed no gate statistic, and did not run `preread.py tables` or
`gates.py run`. I ran three kinds of check:
- hashes, and the npz/JSON metadata of the pre-read outputs (RHS, eps, band and config files only);
- a 30-digit mpmath check of the G2-s RHS only;
- a synthetic crash test of the new gate paths, using GUE-null levels with seeds 7101/7102 and uniform synthetic Maass
  levels, against the real `preread_proposed` tables.

Scripts are in the session scratchpad. They are not committed.

**Verdict:**
- No BLOCKER.
- The default (as-sealed) path is unchanged apart from one fail-closed assertion.
- The proposed path computes what A1, A6 and A4(b) describe, and every gate/reach key matches.
- Three MAJOR findings are about **binding the sealed run to its sealed inputs**. Each should be fixed before
  `make_seal_json.py` is run. Fixing one after the seal commit would need a new seal.

---

## MAJOR

**M1. `gates.main_run` never checks that the files it reads are the pinned ones, or that the χ₋₄ list belongs to the
pre-read (gates.py:262–273, :286; make_seal_json.py:57–58).**

`check_seal` only re-hashes what `seal["files"]` lists (review v2 N9). `main_run` then opens five caller-supplied
paths: `pre_dir`, `zeros1_path`, `maass_path`, `chi_path`, and the accuracy JSON derived from it. Nothing ties them to
the pins.

There are now two pre-read dirs and two χ₋₄ lists on disk. The dangerous pairing is the `--pre results/preread_proposed`
seal with `data/chi4_zeros_T20000_p38.txt`:
- G2's window is centred at T₀ = 2·10⁴ with σ = 2353, so the LHS would lose every zero in (2·10⁴, 4·10⁴], where w ≈ 1.
- That gives a massive Layer A FAIL, scored as "the χ₋₄ identity fails". It is a mis-score, not a crash.
- Nothing catches it. `make_seal_json` pins whichever chi file it is handed. `delta` is 1e-30 in both accuracy JSONs.
  The RHS-vs-pre-read assertion does not look at zeros.

The reverse pairing (sealed tables with the T40000 list) is harmless: the extra zeros have w ≤ e⁻³⁶.

**Fix:**
1. In `main_run`, after `check_seal`, require `os.path.abspath(p) in seal["files"]` for every file opened:
   - `preread_tables.json`, and every `rhs_*.npz` / `nulls_*.npz` passed to `np.load` (wrap `pre` and `band`);
   - the zeros1, Maass and chi files, and the chi accuracy JSON.
2. Assert all of the following:
   - `len(zc) == tab["gates"]["G2"]["n_levels"]`;
   - `float(delta) == tab["gates"]["G2"]["delta"]`;
   - `max(zc) >= C["G2"].E_hi - 1`;
   - the same `n_levels` check for G2s_* when present.
3. Run the same n_levels/E_hi check in `make_seal_json` against the chi file's `.merge.json` `n_total` and last chunk
   `b`, so a wrong pairing is refused before sealing. As committed, the merge JSONs give n_total 26,903 and 58,220,
   which match `tables` n_levels in `preread/` and `preread_proposed/` respectively. The correct pairing is consistent.

**M2. The seal JSON pins absolute workstation paths; the gate run is planned on spot (make_seal_json.py:18, :56, :58,
:63–64; gates.py:44).**

- Every key in `seal["files"]` is an absolute path under
  `/home/combust/fmexplorer/criticality_tool/.claude/worktrees/ph6-xp/specarith/ph6/…`, plus the data paths.
- The seal text (line 7) and MORNING (line 52) put `gates.py run` on spot. The spot launchers use `~/tmp/claude/specarith/ph6`.
- There, `check_seal` calls `sha256(p)` on paths that do not exist. That raises `FileNotFoundError`, not a REFUSED
  message, and the sealed run cannot start without rebuilding the worktree's exact layout on spot.
- It fails closed, so no mis-score. But the seal is a single commit, and fixing this afterwards means re-sealing.

**Fix:** pin code, text and pre-read files by path relative to `HERE`, and resolve them relative to `HERE` in
`check_seal`. Pin the three data inputs by role (`zeros1`, `maass`, `chi4`, `chi4_accuracy`, `chi4_merge` → sha256).
`main_run` then hashes the paths it is actually given and compares them by role. This also closes M1's data half.
`check_seal` should report a missing file as REFUSED.

**M3. `--proposed` bundles three independent decisions, and nothing checks the decisions against the chosen pre-read
(preread.py:38–62, :377–378; make_seal_json.py:48–51).**

- `--proposed` switches on A1, A6 and A4(b) together. `results/preread_proposed/` is the only non-sealed pre-read.
- If Will approves a subset (e.g. A4(b) without A6, or A1 alone), no committed pre-read matches. The author would have
  to edit `preread.py` at seal time, which is unreviewed code.
- `--decisions "A1=yes,…"` is stored as a free string. `make_seal_json` never checks that the configs in the chosen
  `preread_tables.json` are exactly the sealed set plus the approved windows, or that G2's E_hi is 4·10⁴ iff A4 = (b).
  A seal whose JSON says "A6=no" could pin a pre-read that contains G2s_*, and `main_run` would run them.

**Fix:**
- Replace `--proposed` with `--A1 --A6 --A4b` (each adding only its own configs).
- In `make_seal_json`, parse `--decisions` and assert `set(tab["configs"]) == SEALED ∪ approved windows`, and
  `tab["configs"]["G2"]["E_hi"] == (4e4 if A4 == "b" else 2e4)`.

The G2s eps depend on the chi file through d_eff = δ + 2⁻⁵³·max(γ): ≈2.2e-12 for the T2e4 list, 4.4e-12 for T4e4. So
"A6 without A4(b)" needs its own `tables` run with the T20000 list. It cannot reuse `preread_proposed/rhs_G2s_*`.

## MINOR

**m1. `make_seal_json`'s `need` list is incomplete (make_seal_json.py:62–63).**

`main_run` also reads:
- `rhs_G0s_{a,b,c}.npz`;
- `nulls_G0_poisson.npz` and `nulls_G0c_poisson.npz` (G3, G3-c);
- under the proposed pre-read, `rhs_G1s_{a,b}_{even,odd}.npz` and `rhs_G2s_{a,b}.npz`.

The glob pins whichever of these exist, but a missing one would be sealed and only crash at run time. **Fix:** derive
`need` from `tab["configs"]`, using the same list `main_run` uses. My static check found every needed file present in
both dirs.

**m2. The `seal_commit` key does not match (gates.py:277 vs make_seal_json.py:70).** `main_run` records
`seal.get("commit")`, but the JSON writes `parent_commit`, so the result file says `seal_commit: null`. **Fix:** read
`parent_commit`, or better, record `git rev-parse HEAD` at run time next to it.

**m3. The pinned chi4 recipe text is wrong for the A4(b) list (make_seal_json.py:32–35).**
- It says "40 cost-balanced interval calls". The T40000 list is 90 chunks: the 40 of [0, 2·10⁴] plus 50 on
  [2·10⁴, 4·10⁴], launched with T_LO = 20000 (merge.json `chunks`).
- `merge()` asserts `rows[0]["a"] == 0` (chi4_zeros_v2.py:91), so the contingency dir cannot be merged alone. The
  combined `jobs.txt` was a manual step, and the [0,1000] p57 window was reused from the T2e4 run.

**Fix:** make the recipe text depend on the chi file chosen, and record the combination step (DATA_MANIFEST already
says "the [0,20000] chunks above plus 50 chunks"). Optionally, let `merge` take several outdirs.

**m4. The S-block check skips the trailing partial block (chi4_zeros_v2.py:96–98).**
- `nb = len(S) // BLOCK` drops the last 153 zeros at T = 2·10⁴, and the last 220 at 4·10⁴.
- A zero missed there leaves only a −1 step in `count_dev` (+0.666 → −0.334), which the |dev| < 2 assertion cannot see.
- The p57 window [T−100, T] runs the same algorithm and divz, so it is not an independent completeness check.
- No gate impact: w ≤ e⁻³⁶ at E_hi for G2 at either height.

**Fix:** also test `S[-BLOCK:].mean()`, so the documented claim ("a missed zero leaves a persistent step in its block
means") covers every zero.

**m5. The new `g2_block` premise assertion is heuristic (preread.py:116).** `zc.max() >= E_hi − 1` can false-fail when
a normal gap (max gap 4.22 in both lists) straddles E_hi − 1. It passed for both lists. It is also the only behavioural
change on the default path, and it can only fail closed. **Fix:** assert on the merge JSON's last chunk upper edge
`b >= E_hi` (the computed range), not on the largest zero.

**m6. The null band files carry no config (preread.py:259–261; gates.py:273).**
- `main_run` cannot check that `nulls_G2_gue.npz` belongs to `C["G2"]`.
- I verified it by hand: `preread_proposed/nulls_G2_{gue,poisson}.npz` are byte-identical to `preread_A4b/`, with
  `nlev` mean 58,219.2 vs 26,903.1 in `preread/`, and calibration seeds 1000–1099.
- `nulls_G0*` in `preread_proposed/` are byte-identical to `preread/`.

**Fix:** store `config=` in the npz, and assert it equals `tab["configs"][name]` in `band()`. Also copy (or pin) the
`nulls_*.json` provenance into `preread_proposed/`. It currently has none: its bands are copies whose provenance lives
in `preread/` and `preread_A4b/`.

**m7. The crash check of the new paths is not committed.**
- `synth_run.py` exercises only G0, G0s, G0c, G2 and G1, so NOTES 05:42's "synthetic crash check of the new paths
  passes" cannot be reproduced from the repo.
- I reran one: G1s_a/b and G2s_a/b through `gates.maass_gate(…, name)` and `gates.zeta_like_gate`, with the real
  `preread_proposed` tables and synthetic levels.
- It completes (7–15 s each). The RHS-vs-pre-read assertions hold, all reach keys resolve, the gate labels are
  `G1s_a_even` etc., and G2-s has no Layer B.

**Fix:** add the G1s/G2s loops to `synth_run.py`, conditional on the configs being present.

**m8. Cosmetic: G1s results keep the G1 key names (gates.py:184–185).** `maass_gate` returns `G1a_sum_implied` and
`G1b_difference_implied` for G1s too. They are nested under `results["gates"]["G1s_a"]`, so nothing is ambiguous, but
`f"{name}a_sum_implied"` would read cleaner.

**m9. The environment is not pinned.** `classes.pari_counts(30, 30)` runs PARI at gate time (cypari2), and the
tolerances assume float64 numpy/scipy. Record the `numpy`, `scipy`, `cypari2` and PARI versions in the seal JSON, as
the chi4 merge already does for PARI.

## Notes for Will (not defects)

- **A6 (40, 3) adds no Γ-parity test.** `G2s_b:RP11_wrong_parity_a0` is INAPPLICABLE (1.3·10⁻⁵). Only (10, 4) fires RP11
  (1.95·10⁹). (40, 3) contributes RP10 and RP13. A6 says "e.g." about the windows, so this is a choice to make
  knowingly, not an error.
- **G2's `delta` is inert.** `main_run` reads `delta` from the chi accuracy JSON, but `zeta_like_gate` uses `delta` only
  in RP3 (q = 1). It cannot mis-score G2 under either pre-read.
- **G2 at 4·10⁴ still cannot fire RP11** (5.2·10⁻⁸), as A6's finding says. G2-s is what tests it.

## Confirmed

1. **The default path is unchanged in behaviour (read, not rerun).**
   - `g1_block` is the old G1 block with `"G1"` → `name`. The key strings come out identical for `name = "G1"`:
     `G1_even:RP5…`, `G1_even:RP8_drop_scattering`, `G1:RP7_swap_parity`, `rhs_G1_{even,odd}.npz`, and eps_even read
     from `rhs_G1_even.npz`. The arithmetic is unchanged.
   - `g2_block` is the old G2 block plus the m5 assertion, with RP13 only for `G2s*`. The order of RHS evaluation is
     the same.
   - `configs(z)` with `proposed=False` returns the same seven configs (G2 = rule_config(0, 2·10⁴)).
   - The CLI parse is equivalent without `--proposed`. `known_answers`' skip is a no-op when all three configs exist.
   - `gates.maass_gate(name="G1")` and `zeta_like_gate` behave identically for the sealed names. The new loops do
     nothing unless G1s_*/G2s_* are in the tables.
   - `ph6lib.py`, `classes.py` and `rulings.py` are untouched in 1fc3552..HEAD.
   - Independent corroboration: `results/preread/` was written by the pre-refactor code (e42196f) and
     `results/preread_proposed/` by the refactored code (df0a409). The two are **byte-identical (sha256)** for
     `rhs_G0, G0c, G0s_{a,b,c}, G1_even, G1_odd, G4_{confusable,incommensurate}`. The `G1_*` pair proves `g1_block`
     reproduces G1 exactly. G2 cannot be compared that way, because its T differs; there the reading argument above
     applies.
   - The sealed-dir reachability entries for G0/G0s/G0c/G1/G4 are identical in both tables.
2. **The proposed path matches A1, A6 and A4(b).**
   - A1: G1s_a = fixed (12, 4), E_hi 46; G1s_b = (20, 5), E_hi 62.5. Both are under the Maass list's 98.765.
     - It uses the same §5 tolerance construction as G1: d_eff, e_float, e_trunc at E_hi/6 + 1 (conservative, since
       the list continues to 98.76), and e_rhs with the N10 factor.
     - It uses the same reach rule (|removed|/2ε > 1), and RP5, RP6, RP7, RP8 (even) and RP9 per sector.
     - The selberg_integrals trapezoid starts at r = 0 on even integrands, so it is spectrally accurate at small T₀ as
       well. h(i/2) is carried in `maass_sector_sum`.
   - A6: G2s_a = (10, 4), E_hi 44; G2s_b = (40, 3), E_hi 65.5. Layer A only (no band), with RP10, RP11 and RP13 on both
     sides. The RP13 removed term is `R["gamma"]` with a = 1 in both preread and gates.
   - A4(b): G2 = rule_config(0, 4·10⁴) (T₀ 2·10⁴, σ 2352.94), n_levels 58,220. The G2 band in `preread_proposed` is the
     T = 4·10⁴ draws (see m6).
   - **Key strings.** I enumerated every `reach.status` key `main_run` requests, given each dir's configs. All are
     present in both `preread/` and `preread_proposed/`, and no table entry goes unused. Examples:
     `G1s_a_even:RP5_elliptic_x2`, `G1s_a:RP7_swap_parity`, `G2s_a:RP13_drop_gamma`.
   - **RHS accuracy at the new tight tolerances.** At 30 digits (mpmath: Γ integral by quadrature, prime sum to 10⁴,
     conductor term), the G2-s RHS agrees with `preread_proposed/rhs_G2s_{a,b}.npz` to |diff|/ε ≤ 1.5·10⁻⁴ at 10 τ
     points, including each window's ε minimum (ε ≈ 6–10·10⁻¹²).
3. **make_seal_json** pins every file `main_run` reads under either `--pre` choice:
   - code (ph6lib, preread, gates, rulings, classes, chi4_zeros_v2) and text;
   - `preread_tables.json` and all `rhs_*.npz` and `nulls_*.npz` (by glob, so the proposed G1s/G2s tables and the
     T4e4 G2 bands are included);
   - zeros1, Maass, chi4 and its accuracy and merge JSON.

   Nothing `main_run` reads is left out, given the right arguments. The gaps are binding and portability (M1, M2) and
   the `need` list (m1).
4. **chi4_zeros_v2 merge, accuracy and S-block check are correct.**
   - S_k = (k − ½) − N̄(γ_k), with N̄ = arg Γ(¾ + iT/2)/π + (T/2π) log(4/π). That is θ(T)/π for odd primitive χ₋₄, with
     no "+1" since there is no pole, and mpmath's `loggamma` gives the continuous argument.
   - It is confirmed empirically: block means are within ±0.003 (2e4) and ±0.004 (4e4), and count_dev is −0.374 and
     +0.666. A constant offset would show up as ≈ ±1.
   - Dedup at 1e-20 is backed by the fail-closed min-gap > 1e-8 assertion. Contiguity and range are asserted.
   - Accuracy pairs p38 and p57 by sorted order with a length assertion. δ = max(10·worst, 1e-30) = 1e-30 for both
     lists.
   - The `plan()` T_LO change is correct (cost targets offset by C(T_LO), bisection on [T_LO, T_MAX]). The launcher
     skips the [0,1000] p57 window when T_LO > 0.
5. **Under either pre-read dir, with the right chi file, `main_run` finds everything it loads.** That covers G3's and
   G3-c's G0 and G0c gue/poisson bands, G4's `rhs_G4_*` and G0 band, and the chi accuracy JSON in `data/` for both
   heights. The only crash or mis-score routes I found are the wrong-argument and wrong-host cases in M1 and M2.
