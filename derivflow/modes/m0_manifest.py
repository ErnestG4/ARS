#!/usr/bin/env python3
"""M0 — context resolution manifest. COMMITTED GENERATOR of derivflow/modes/MANIFEST_M0.json.

Every entry below is a LOOKUP RESULT (file:line, value) recorded on 2026-09-17 during M0 of
BRIEF.md, or a conflict between sources recorded per BRIEF §0.5 and NOT resolved by editing.
The smoke-cell numbers are read from m0_smoke.json (its own committed generator: m0_smoke.py).
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()


smoke = json.load(open(os.path.join(HERE, "m0_smoke.json")))
tim = smoke["timing"]

# ---- projections from measured timings (single-process; 8 workers ~2-3x slower each) ----
t = {n: tim[str(n)] for n in (1024, 4096, 16384)}


def flow_cost(n, kmax, n_refs, n_pop=0):
    return t[n]["diff_step_s"] * kmax + t[n]["prod_reference_pair_s"] * n_refs + t[n]["popref_pair_s"] * n_pop


proj = {
    "ML": {"n=4096": {"runs": 61, "kmax": 64, "serial_s_per_run": flow_cost(4096, 64, 0),
                      "note": "raw positions only, no reference; 6 A x 10 qw + LATTICE"},
           "n=16384": {"runs": 61, "kmax": 64, "serial_s_per_run": flow_cost(16384, 64, 0)},
           "int128_arm": "NOT RUN — no int128 path exists in the repo (M0.6 STOP); float64 twins run for every A"},
    "MT": {"n=16384": {"runs": 11, "kmax": 40, "prod_ref_pairs_per_run": 6, "popref_pairs_per_run": 6,
                       "serial_s_per_run": flow_cost(16384, 40, 6, 6),
                       "note": "reference iterations grow with k (sub_iters); the k=1 timing is a floor"}},
    "M3": {"iid n=4096": "= the smoke cell (done in M0.10)",
           "gue n=4096": {"runs": 16, "serial_s_per_run": flow_cost(4096, 64, 20, 20),
                          "measured_smoke_per_rep_s_8workers": smoke["per_rep_runtime_s"]},
           "n=1024,2048 both classes": {"runs": 64, "serial_s_per_run_1024": flow_cost(1024, 64, 20, 20)},
           "n=16384 both classes": {"runs": 32, "serial_s_per_run": flow_cost(16384, 64, 20, 20),
                                    "banked_precedent": "step3_scale_law.json: 84476 s for 32 flows on 5 workers",
                                    "decision": "CUT from Night 1 (exceeds the window by itself); "
                                                "queued; BRIEF priority puts it last"}},
}

manifest = {
    "manifest": "MANIFEST_M0 — derivflow/modes Night 1 context resolution",
    "generated": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
    "launch_options_as_read": {
        "WINDOW": "until 08:00 PDT 2026-09-17 (Will: 'proceed until 8am'); ~6.5 h from launch at 01:19",
        "AFTER_M0": "continue (Will: 'proceed until 8am'; no STOP raised that blocks the float64 scope)",
        "PUSH_BRANCH": "no (unset -> conservative; Will pushes)",
        "timer": "CronCreate */30 * * * * checkpoint (job 19ba4052)",
    },
    "M0.1_git": {
        "HEAD_at_launch": "13c4696ad46bc30a6ac2f092ea79a1acec28f57b (main)",
        "brief_expected_main": "589d7d8 — differs: four later doc-only commits (1dd45e9, 7f82b38, 6165aab, 13c4696); proceeded from actual HEAD per BRIEF",
        "branch_created": "derivflow-modes from 13c4696 (did not pre-exist)",
        "branches_at_launch": git("branch", "--format=%(refname:short)").split("\n"),
        "clean_tree": "tracked tree clean; ONE untracked path `ring/` (the other session's planning doc, "
                      "rotational-dynamics-build-plan.md) — not touched, recorded as a conflict with the "
                      "literal 'must be clean' rule; the other session works in its own worktree "
                      ".claude/worktrees/ring-stage0 so no branch collision in this working tree",
        "HEAD_now": git("rev-parse", "HEAD"),
    },
    "M0.2_production_statistic": {
        "function": "derivflow/track0_harness.py:117-118 rtilde(gaps) = mean(min(g[:-1],g[1:])/max(g[:-1],g[1:]))",
        "omr": "1 - rtilde(np.diff(u[bulk_idx(m)])) — science_rate_question.py:55 (one_flow), u = F_at*m",
        "gaps_consumed": "consecutive gaps of the UNFOLDED positions restricted to the bulk window; "
                         "no filtering, no clipping (knownanswer.rtilde_distance mirrors it)",
        "bulk_window": "track0_harness.py:110-113 bulk_idx(m): central w = ceil(BULK_FRACTION*m) roots BY ROOT INDEX, slice((m-w)//2, (m-w)//2+w)",
        "candidates_found": ["track0_harness.rtilde (the instrument)",
                             "knownanswer.rtilde_distance (Gate D mirror of the same arithmetic, documented as such)",
                             "spacings.Spacings.rtilde_distance (guard wrapper, 'as track0_harness.rtilde computes it')"],
        "resolution": "ONE production function (track0_harness.rtilde); the other two are declared mirrors — not a STOP",
    },
    "M0.3_constants": {
        "KSTAR_LEVEL": {"value": 1e-2, "definition": "derivflow/science_rate_question.py:28", "duplicates": "none (all other uses import it)"},
        "FIT_WINDOW_MIN": {"value": 1e-3, "definition": "derivflow/science_rate_question.py:27",
                           "duplicates": "identical literal 1e-3 re-typed in step3_scale_law.py:15, step2_env_decomposition.py:53, step2b_isoconfig.py:40, gue_isoconfig_adapted.py:141 — NON-conflicting; not a STOP"},
        "BULK_FRACTION": {"value": 0.20, "definition": "derivflow/track0_harness.py:32", "selects_by": "ROOT INDEX (bulk_idx), not position",
                          "duplicates": "none"},
        "census": "derivflow/verify_declared_params.py BASELINE 17; sealgen.sh refuses a derivflow generator using these undeclared",
    },
    "M0.4_seals_and_arms": {
        "seal_paths": ["derivflow/seals/RATE_QUESTION_SEAL.json (2026-08-11, 95e1ad3)",
                       "derivflow/seals/SCALE_LAW_SEAL.json (2026-08-12, 889f472)"],
        "arm_names": {"PROD_PRIMARY": "primary = Richardson 2F(eps)-F(2eps) (JSON keys mean/sigma_mean; rec one_minus_rtilde)",
                      "PROD_BW1": "eps = raw eps (keys mean_epsraw; rec one_minus_rtilde_epsraw; diag F_at_eps_raw)",
                      "PROD_BW2": "2eps = raw 2eps (keys mean_2eps; rec one_minus_rtilde_2eps; diag F_at_2eps)"},
        "k_grid_sealed": "dense v1.6 (c986573): {1..16} u {24,32,48,64} — science_dense.K_DENSE",
        "k_grid_original": "{1,2,4,8,16,32,64} (RATE_QUESTION_SEAL) + doc rows {128,256,410} at n=4096",
        "n_grid": "{1024,2048,4096} (RATE_QUESTION_SEAL) + 16384 (SCALE_LAW_SEAL) = expected set",
        "replicates": 16,
        "rng": "SeedSequence(20260811).spawn(128): iid children 0-15/16-31/32-47 (n=1024/2048/4096), 96-111 (16384); gue 48-63/64-79/80-95, 112-127",
        "commit_chain_verified": "all ten hashes resolve (4f29d70 c235861 be7f2b9 78ce01a c7275d3 d6a7cff c986573 6cc2562 d629f6f/889f472 505931c)",
    },
    "M0.5_machinery": {
        "solver": "derivflow/track0_harness.py:47-79 diff_step(r): CPU numpy float64, 25 bisections + 5 clamped Newton on S(x)=sum 1/(x-r_i) per bracket, DS_BLOCK=2048 candidate blocks (bitwise identical to unblocked); certified by run_hermite_gate (track0_hermite_gate.json). Device: CPU only; no GPU path exists.",
        "reference_entry": "derivflow/track0_iid_scaling.py:110-127 reference_cdf(F_seed, roots_flowed, s, m)",
        "eps_rule": "eps_rule_v15 (track0_iid_scaling.py:56-58): eps_k = Delta_s*sqrt(0.25 + 16(n-k)/(kn)), Delta_s = flowed span/m; applied in FLOWED coordinates (flow_density rescales to seed coords by 1/(1-s))",
        "smoothing_kernel": "Stieltjes inversion rho_eps(x) = -(1/pi) Im G(x+i eps): POISSON (Cauchy) kernel of half-width eps convolved with the free-convolution density; then per-gap 3-point Gauss quadrature between consecutive roots, tails 6 mean gaps / 8 panels",
        "richardson": "primary = 2*F(eps) - F(2*eps) (track0_iid_scaling.py:124); raw eps and raw 2eps retained as the band arms",
        "exposes": "unfolded POSITIONS: F_at (absolute CDF at each root) * m; gaps are np.diff of that",
        "subordination_accepts_analytic": "YES — free_conv.free_power_G(F_mu, z, kappa) takes ANY callable F = 1/G; track0_iid_scaling.F_uniform (analytic Uniform[-1,1]) already rides as the 'population reference DIAGNOSTIC'; free_conv.F_semicircle(sigma) is the semicircle closed form. POPREF is possible; NOT a STOP.",
        "gue_de_normalization": "science_rate_question.gue_seed: DE beta=2 tridiagonal / sqrt(n) -> semicircle sc(sigma=1), support [-2,2] (R=2); verified: KS(seed, sc(1)) = 8.9e-4 at n=4096, minimised at sigma=1.00 on a 0.98..1.02 scan",
        "spawn_scheme": "np.random.SeedSequence(MASTER_SEED=20260811).spawn(96 or 128); child index -> np.random.default_rng(child)",
        "seed_roster_beta": "derivflow/seed_roster_beta.py:beta_seed(n, rng, beta): DE tridiagonal, chi_{beta(n-i)} off-diagonal, /sqrt(beta), /sqrt(n); beta=2 == gue_seed (P1 reproduced 0/40 banked)",
        "sigma2": "derivflow/track0_harness.py:121-127 sigma2(u, L): variance of counts in length-L boxes slid by 0.5 along the unfolded window",
    },
    "M0.6_precision": {
        "int128_grep": "git grep -nE 'int128|__int128|i128|Int128|INT128' -> ZERO hits outside derivflow/modes/BRIEF.md",
        "elevated_precision_paths_that_exist": "mpmath (dps 30/40) — used ONLY as the authoritative REFERENCE in the Hermite self-map gate (hermite_roots_mp) and step1_lattice_k1; the certified solver diff_step and the reference reference_cdf are float64 only",
        "STOP": "M0.6 fires: neither the certified solver nor the reference has an int128 path. Per BRIEF: no new arithmetic backend written. "
                "ML cells A in {1e-9, 1e-7} on the int128 path are HELD for Will; every A gets its float64 twin; "
                "float64 assessability is declared in the seal (predicted signal >= FLOAT64_FLOOR_ULPS * eps_mach * |x|)",
        "consequence_for_gate_ML": "the PASS rule as written ('every A <= 1e-5') cannot be fully evaluated; ML is graded on the float64-assessable cells and the report says so",
    },
    "M0.7_paper_copies": [
        {"path": "derivflow/paper/paper.tex", "last_commit": "6955281 2026-09-15", "appendix_D": "YES by count (4th appendix after \\appendix: 'Reproducibility and cost'; 3rd = 'Corrections to Section 4, and their order'); literal string 'Appendix D' absent (LaTeX auto-numbers)"},
        {"path": "derivflow/paper/PROSE.md", "last_commit": "f75b012 2026-09-09", "appendix_D": "NO (Appendices A-C only; C = Reproducibility); leads with z(tau)=20.4 / z(beta)=9.3 at lines 89, 174"},
        {"path": "derivflow/paper/NOTE.md", "last_commit": "e3ef31b 2026-08-13", "appendix_D": "NO (working skeleton v0.1)"},
    ],
    "M0.8_guards": {
        "spacings": "Unfolding(reference, arm, eps_over_delta, window) has free string fields -> NOUNFOLD tagged Unfolding('none','nounfold',0.0,'bulk-0.20'); RM1 ('none','rm1',0.0,...); POPREF ('analytic-uniform'|'analytic-semicircle','richardson',eps_k/Delta,...); PROD ('empirical-seed', 'richardson'|'raw-eps'|'raw-2eps', ...). No extension needed; cross-arm arithmetic REFUSES by construction (modes_common.tag/omr)",
        "lineage": "Lineage(cell, construction, data, protocol); arms within a cell share `data` (identical roots) -> assert_independent(a, b, 'data') would REFUSE; recorded in every artifact as arms_share_roots=True and a Lineage.record()",
        "errormodel": "shape_z fork covariance/bootstrap by declared degeneracy threshold; for k* this arc reports BOTH the production MVN-covariance error and a replicate-bootstrap error on every number (curve_summary)",
        "sealgen_checkrun_hook": "sealgen.sh commits generator alone then runs (refuses undeclared KSTAR_LEVEL/FIT_WINDOW_MIN/BULK_FRACTION in derivflow/ generators); checkrun.sh writes CHECKRUN lines to .checkrun_log; .githooks/commit-msg refuses outcome claims without a logged CHECKRUN line (3 h window)",
        "verify_all": "discovers verify_*.py by walking the tree — 'registration' = naming the checker verify_*.py under derivflow/modes/ (no list to edit). NOTE: it also walks .claude/worktrees/ring-stage0 (the other session's worktree) and would double every checker there; not fixed (out of scope), reported",
    },
    "M0.9_banking": {
        "per_replicate_roots_banked_by_sealed_runs": "NO. science_dense_grid.json / step3_scale_law.json bank per-k mean and sigma_mean only; zbeta_correlated_error recovered per-replicate CURVES by regeneration; paper.tex:635 discloses the per-replicate gap. Roots are regenerated from the sealed SeedSequence (deterministic) and banked here as derivflow/modes/roots/<class>_<n>.npz with sha256 per array",
    },
    "M0.10_smoke": {
        "cell": "IID_UNIFORM n=4096, children 32..47, K_DENSE",
        "reproduction": smoke["reproduction"],
        "arms_kstar_ptail": {a: {"kstar_fit": smoke["arms"][a]["kstar_fit"]["value"],
                                 "err_cov": smoke["arms"][a]["kstar_fit"]["err_covariance"],
                                 "err_boot": smoke["arms"][a]["kstar_fit"]["err_bootstrap"],
                                 "form": smoke["arms"][a]["kstar_fit"]["selected"],
                                 "kstar_interp": smoke["arms"][a]["kstar_interp"]["value"],
                                 "kstar_interp_err_boot": smoke["arms"][a]["kstar_interp"]["err_bootstrap"],
                                 "p_tail": smoke["arms"][a]["p_tail"]["value"],
                                 "p_tail_err_boot": smoke["arms"][a]["p_tail"]["err_bootstrap"]}
                             for a in smoke["arms"]},
        "interlacing": smoke["interlacing"],
        "timing_single_process": tim,
        "roots_npz_sha256": smoke["roots_npz_sha256"],
    },
    "M6_bound_conflict": {
        "brief_says": "D_k <= 2k/(n-k), red path = one root moved outside its Rolle bracket must fire",
        "theorem": "c_0 - k <= c_k <= min(c_0, n-k) from the j-th root of p^(k) in (r_j, r_{j+k}) => D_k <= k/n (sharp; attained by a genuine flow: n=64,k=1 gave D = 1/64 exactly)",
        "why_it_matters": "one moved root changes D by <= 1/(n-k), and k/n + 1/(n-k) < 2k/(n-k) for all k>=1, n>2k: the BRIEF's bound cannot fire on its own red path (n=64,k=1: moved-root D = 0.0300 < 0.0317). Checker uses the sharp bound; both ratios reported. Not resolved by editing the BRIEF.",
    },
    "projections_night1": proj,
    "cuts_declared_before_ML": [
        "ML int128 arm (A in {1e-9,1e-7} at int128): NOT RUN — no such path; float64 twins for all A run",
        "M3 n=16384 (both classes): NOT RUN tonight — projected > the window on its own; queued",
        "M3 n=4096 GUE, n=1024/2048 both classes: RUN after ML and MT if the window allows (BRIEF priority)",
    ],
    "conflicts_recorded": [
        "BRIEF expected main 589d7d8; actual 13c4696 (proceeded from actual)",
        "BRIEF 'working tree must be clean' vs untracked ring/ (other session's file; left untouched)",
        "BRIEF int128 path vs repo (none exists) — STOP honoured for that arm only; see M0.6",
        "BRIEF M6 bound 2k/(n-k) vs theorem k/n — sharp bound checked, both reported",
        "BRIEF 'the tolerance recorded in its artifact' — science_dense_grid.json records no tolerance; used the repo precedent (seed_roster_beta P1: 1e-12 relative, 0 mismatches) and 1e-9 relative on k*",
    ],
}
json.dump(manifest, open(os.path.join(HERE, "MANIFEST_M0.json"), "w"), indent=1)
print(json.dumps({"reproduction": smoke["reproduction"]["REPRODUCED"],
                  "interlacing_holds": smoke["interlacing"]["holds"],
                  "projections": proj}, indent=1))
print("wrote MANIFEST_M0.json")
