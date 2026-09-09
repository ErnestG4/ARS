#!/usr/bin/env python3
"""THE GUE-ADAPTED ISOCONFIGURATIONAL PROBE — is the STRETCH MECHANISM seed-dependent?

COMMITTED GENERATOR of derivflow/gue_isoconfig_adapted.json.
Predictions sealed here, before any per-bin curve at K_COND = 1 exists.

WHY THIS EXISTS
---------------
ROADMAP backlog 2026-08-14. Step 2b's GUE arm was UNDERPOWERED and said so: at
K_COND = 2 on the grid {4,6,8,12,16,24,32,64}, GUE's per-bin fit windows came out
at 4, 4, 3, 3, 3 points (verified in step2b_isoconfig_gue.json today, not
recalled). Three points cannot support a three-parameter form at all, so F3 was
unassessable in most bins and the arm filed MIXED. "No per-bin stretch in GUE" was
therefore never a reading the data could deliver -- the design could not have seen
it. GUE crystallizes at k* ~ 6 against iid's ~ 11, so a grid designed on iid's
timescale spends most of its points after GUE's signal has already left the fit
window.

THE ADAPTATION, pinned in the backlog on 2026-08-14: K_COND = 1 with the k-grid
starting at 2 and dense through GUE's live range.

THE QUESTION, and why it is not the same as the one Step 2/2b answered: those
established that the (tau, beta) PARAMETERS are seed-dependent (20.4 sigma /
9.3 sigma). Whether the stretch MECHANISM is seed-dependent -- whether GUE's
stretch decomposes under conditioning where iid's does not -- is untouched, and it
is the difference between "two seeds relax at different rates by the same physics"
and "two seeds relax by different physics".

COMMENSURABILITY, and why the iid arm is re-run rather than cited. The banked iid
result is at K_COND = 2 on the old grid. Comparing GUE at K_COND = 1 against that
would confound the seed contrast with the design change -- the exact 4-clause
failure the commensurability rule exists to stop, and the cheapest possible way to
manufacture a mechanism difference. Both classes are therefore run under the
IDENTICAL adapted design, and C3 checks that iid still reads NOT_SUPPORTED there.

REPLICATE, DO NOT RECONSTRUCT: every piece of measurement machinery below is
IMPORTED from step2b_isoconfig / step2_env_decomposition / track0_harness -- the
conditioning rule, per-root ratios, unfolding, reference CDF, and the sealed fit
ladder are the committed ones, not re-typed. P1 then checks the import actually
behaves like the banked cell by re-running the OLD design and demanding the banked
numbers back.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — every bar strictly inside its stated range.             ║
║                                                                              ║
║ P1  PREMISE    re-running the OLD design (K_COND = 2, old grid) on GUE        ║
║                reproduces step2b_isoconfig_gue.json: 5 selected forms and     ║
║                5 taus (1e-9 relative where both are non-None).                ║
║                Mismatches <= 0.5 of 10. If this misses, this harness is not   ║
║                the banked instrument and no arm below is readable.            ║
║ P2  PREMISE    the adaptation does what it was designed to do: the SMALLEST   ║
║                GUE per-bin fit window under the adapted design is >= 6        ║
║                points. At 3 points F3 is not merely noisy, it is              ║
║                unidentifiable; if this misses, the probe still cannot ask     ║
║                its question and says so instead of reporting a null.          ║
║ C1  EXISTENCE  GUE's stretch SURVIVES conditioning as iid's did: at least 3   ║
║                of 5 GUE bins select F3 with beta < 0.9 (the pre-committed     ║
║                NOT_SUPPORTED threshold, inherited verbatim). Predicted        ║
║                because GUE's rigidity makes its bins near-coincident, and     ║
║                Step 2b's own pinned logic calls coincident-and-still-         ║
║                stretched the cleanest intrinsic-nonexponentiality datum       ║
║                available. A MISS is the bigger finding: it would mean the     ║
║                stretch decomposes for GUE where it did not for iid, i.e.      ║
║                the MECHANISM is seed-dependent, not just its parameters.      ║
║ C2  MECHANISM  the slow subpopulation survives a THIRD conditioning time:     ║
║                max over classes of max(tau_new/tau_old, tau_old/tau_new)      ║
║                <= 1.5, where tau is the LARGEST fitted tau among that         ║
║                class's bins. Banked anchors, read from the artifacts today:   ║
║                iid 3.070 (K_COND = 0) -> 3.184 (K_COND = 2), already stable   ║
║                to 3.7%; GUE 2.354 (K_COND = 2, on a 4-point window). This is  ║
║                the BINDING sealed secondary the 08-14 findings note           ║
║                required, and it adjudicates the standing ambiguity: a real    ║
║                coexisting slow subpopulation should keep its timescale when   ║
║                the conditioning time moves, while a merely CRUDE conditioning ║
║                variable should let it drift with where the cut is taken.      ║
║ C3  RESOLUTION the control holds: the iid arm under the ADAPTED design still  ║
║                reads NOT_SUPPORTED (>= 3 of 5 bins F3 with beta < 0.9), so    ║
║                any GUE/iid contrast in C1 is attributable to the seed and     ║
║                not to the redesign.                                          ║
║                                                                              ║
║ C1 IS THE CELL, and C3 is what makes C1 mean anything.                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

EXPLORATORY STATUS: this probe inherits Step 2b's exploratory, unsealed-science
grade -- it adjudicates a mechanism question with a pre-committed ladder, and it
does not touch the sealed RATE-SEED-DEPENDENT verdict, which stands on the sealed
rule as executed. What is sealed here is THIS cell's own prediction set.

AMENDMENT 1 -- AFTER OUTPUT. C2 MISSED, AND C2'S COMPARISON WAS THE DEFECT.

C2 ratioed "the largest fitted tau" across conditioning times. The slow bin is F2
at K_COND = 2 and F3 at K_COND = 1 in BOTH classes, so the arm compared tau
between different functional forms, where F3's tau is degenerate with beta. That
ratio measures nothing, which is the commensurability rule failing inside a cell
whose premise arms were built to catch exactly this at the instrument level -- the
arms guarded the instrument and the comparison walked in through the parameters.

The miss STANDS in the artifact. On the commensurable statistic -- k*, the
crossing of KSTAR_LEVEL, defined for F1/F2/F3 alike and already this arc's
scale-law quantity -- the reading REVERSES: iid 13.631 -> 13.510 (ratio 1.009),
gue 7.039 -> 6.754 (1.042), both stable to within 5% against C2's 1.5 bar, and
every bin stable, not only the slowest. So C2's SCIENTIFIC claim is supported and
C2's ARM is not, and the two facts are recorded separately.

Same cause, second place: this cell reports tau_monotone = False for adapted GUE;
its k* sequence decreases strictly, so GUE does order monotonically by
environment. Both corrections live in gue_isoconfig_kstar_amendment.py/.json,
POST-HOC and unsealed by construction, deliberately NOT registered as a seal pair
because the only label verify_seal_order could give it is DECLARED, and DECLARED
would overstate a generator written after its subject was read.

CARRY-FORWARD: tau is not a safe cross-fit comparison quantity in this arc.
Compare relaxation timescales at a level crossing.
"""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
from reachable import Bar                                            # noqa: E402
from verdictlattice import (Arm, compose, PREMISE as PREM_ROLE,       # noqa: E402
                            EXISTENCE as EX_ROLE,
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from modelparams import Model, Param, TESTED, DECLARED                # noqa: E402
from track0_harness import diff_step, bulk_idx                        # noqa: E402
from free_conv import F_empirical                                     # noqa: E402
from track0_iid_scaling import reference_cdf                          # noqa: E402
from science_rate_question import fit_ladder, gue_seed, MASTER_SEED    # noqa: E402
from step2_env_decomposition import per_root_ratios                   # noqa: E402

N = 4096
R = 16
NBINS = 5
FIT_WINDOW_MIN = 1e-3
K_COND_NEW = 1
K_GRID_NEW = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16]
K_COND_OLD = 2
K_GRID_OLD = [4, 6, 8, 12, 16, 24, 32, 64]
TAU_OLD = {"iid": 3.184, "gue": 2.354}      # largest banked per-bin tau at K_COND=2

INSTRUMENT = Model("isoconfigurational conditioning, GUE-adapted", [
    Param("K_COND", TESTED, sweep=[K_COND_OLD, K_COND_NEW],
          why="the conditioning time. Both are run: the OLD value to reproduce "
              "the banked cell (P1), the NEW one to ask the question. Moving it "
              "is also the instrument for C2 -- a slow subpopulation that is "
              "real should not care where the cut is taken"),
    Param("k_grid", TESTED, sweep=["old {4,6,8,12,16,24,32,64}",
                                   "adapted dense 2..12 + {14,16}"],
          why="the old grid was designed on iid's k* ~ 11 and left GUE 3-4 "
              "assessable points at k* ~ 6. P2 scores whether the adaptation "
              "actually repairs that, rather than assuming it did"),
    Param("seed_class", TESTED, sweep=["iid", "gue"],
          why="both classes under the IDENTICAL adapted design, so the seed "
              "contrast is not confounded with the design change"),
    Param("NBINS", DECLARED, value=NBINS,
          why="quintiles, inherited verbatim from Step 2 and 2b; changing the "
              "binning while changing the grid would make the comparison to the "
              "banked arms uninterpretable"),
    Param("ladder_thresholds", DECLARED,
          value="F2 in >=4/5 + monotone tau => SUPPORTED; F3 with beta<0.9 in "
                ">=3/5 => NOT_SUPPORTED; else MIXED",
          why="the pre-committed Step 2 ladder, inherited unchanged so this "
              "arm's outcome is comparable to the two banked ones"),
    Param("n", DECLARED, value=N, why="the adjudicated size throughout the arc"),
])


def _arm(args):
    """One replicate: flow, condition at K_COND, bin by ancestry-cone environment.

    Body is step2b_isoconfig.run()'s inner loop with (K_COND, K_GRID) lifted to
    parameters -- the conditioning rule, cone definition, bulk window, per-root
    ratios and unfolding are unchanged."""
    seed_class, i, k_cond, k_grid = args
    children = np.random.SeedSequence(MASTER_SEED).spawn(96)
    if seed_class == "iid":
        seed = np.sort(np.random.default_rng(children[32 + i]).uniform(-1.0, 1.0, N))
    else:
        seed = gue_seed(N, np.random.default_rng(children[80 + i]))
    F_seed = F_empirical(seed)
    r = seed.copy()
    xc = None
    per_bin, aggr = {}, {}
    for k in range(1, k_grid[-1] + 1):
        r = diff_step(r)
        if k == k_cond:
            xc = r.copy()
        if k not in k_grid:
            continue
        m = N - k
        F_at, _ = reference_cdf(F_seed, r, k / N, m)
        u = F_at * m
        bi = bulk_idx(m)
        lo, hi = bi.start, bi.stop
        ratios = per_root_ratios(u)
        j_idx = np.arange(max(lo, 1), min(hi, m - 1))
        rj = ratios[j_idx - 1]
        cone = k - k_cond
        E = (xc[j_idx + cone] - xc[j_idx]) / cone
        edges = np.quantile(E, np.linspace(0, 1, NBINS + 1))
        edges[0] -= 1e-12
        edges[-1] += 1e-12
        which = np.digitize(E, edges) - 1
        per_bin[k] = [1.0 - float(np.mean(rj[which == b])) for b in range(NBINS)]
        aggr[k] = 1.0 - float(np.mean(rj))
    return seed_class, i, per_bin, aggr


def run_arm(seed_class, k_cond, k_grid, pool):
    reps = pool.map(_arm, [(seed_class, i, k_cond, k_grid) for i in range(R)])
    acc = {k: [[] for _ in range(NBINS)] for k in k_grid}
    agg = {k: [] for k in k_grid}
    for _, _, pb, ag in reps:
        for k in k_grid:
            for b in range(NBINS):
                acc[k][b].append(pb[k][b])
            agg[k].append(ag[k])
    out = {"K_COND": k_cond, "k_grid": k_grid, "per_bin": {}, "aggregate": {},
           "fits": {}}
    for k in k_grid:
        out["aggregate"][str(k)] = {
            "mean": float(np.mean(agg[k])),
            "sigma_mean": float(np.std(agg[k], ddof=1) / np.sqrt(R))}
        out["per_bin"][str(k)] = [
            {"mean": float(np.mean(acc[k][b])),
             "sigma_mean": float(np.std(acc[k][b], ddof=1) / np.sqrt(R))}
            for b in range(NBINS)]
    forms, taus, betas, wins = [], [], [], []
    for b in range(NBINS):
        ks = [k for k in k_grid if out["per_bin"][str(k)][b]["mean"] > FIT_WINDOW_MIN]
        means = np.array([out["per_bin"][str(k)][b]["mean"] for k in ks])
        sm = np.array([out["per_bin"][str(k)][b]["sigma_mean"] for k in ks])
        sel, fits = fit_ladder(np.array(ks, dtype=float), means, sm)
        out["fits"][f"bin{b}"] = {"fit_window_k": ks, "selected": sel, "ladder": fits}
        forms.append(sel)
        wins.append(len(ks))
        p = fits[sel].get("params")
        taus.append(p[1] if sel in ("F2", "F3") and p else None)
        betas.append(p[2] if sel == "F3" and p else None)
    n_f2 = sum(1 for f in forms if f == "F2")
    n_stretch = sum(1 for f, be in zip(forms, betas)
                    if f == "F3" and be is not None and be < 0.9)
    tau_ok = all(t is not None for t in taus) and (
        all(taus[b] < taus[b + 1] for b in range(NBINS - 1))
        or all(taus[b] > taus[b + 1] for b in range(NBINS - 1)))
    out.update(selected_forms=forms, taus=taus, betas=betas, windows=wins,
               n_f2=n_f2, n_f3_stretch=n_stretch, tau_monotone=tau_ok,
               ladder_outcome=("SUPPORTED" if n_f2 >= 4 and tau_ok else
                               "NOT_SUPPORTED" if n_stretch >= 3 else "MIXED"))
    return out


t0 = time.time()
res = {}
with Pool(8) as pool:
    print("P1: re-running the OLD design on GUE (K_COND=2, old grid)...", flush=True)
    res["gue_old"] = run_arm("gue", K_COND_OLD, K_GRID_OLD, pool)
    print(f"  old-design GUE done ({time.time() - t0:.0f}s)", flush=True)
    for sc in ("gue", "iid"):
        print(f"adapted design, {sc} (K_COND=1, dense grid)...", flush=True)
        res[f"{sc}_new"] = run_arm(sc, K_COND_NEW, K_GRID_NEW, pool)
        print(f"  {sc} adapted done ({time.time() - t0:.0f}s)", flush=True)

# ---- P1: does the old-design re-run reproduce the banked GUE arm? ----
bank = json.load(open(os.path.join(HERE, "step2b_isoconfig_gue.json")))
mm = sum(1 for a, b in zip(res["gue_old"]["selected_forms"], bank["selected_forms"])
         if a != b)
for a, b in zip(res["gue_old"]["taus"], bank["taus"]):
    if (a is None) != (b is None):
        mm += 1
    elif a is not None and abs(a - b) > 1e-9 * max(abs(b), 1e-300):
        mm += 1
P1 = Bar("old-design re-run vs banked GUE arm, mismatches", 0.5, direction="le",
         floor=0, ceiling=10,
         why="5 selected forms + 5 taus; a count of disagreements, 0 to 10")
p1 = P1.score(mm)

P2 = Bar("smallest GUE per-bin fit window under the adapted design", 5.5,
         floor=0, ceiling=len(K_GRID_NEW),
         why=f"a count of in-window k-points, 0 to {len(K_GRID_NEW)}; at 3 a "
             f"3-parameter form is unidentifiable, and the banked arm sat there")
p2 = P2.score(min(res["gue_new"]["windows"]))

C1 = Bar("GUE bins selecting F3 with beta < 0.9 (adapted)", 2.5,
         floor=0, ceiling=NBINS,
         why="the pre-committed NOT_SUPPORTED threshold, 0 to 5 bins")
c1 = C1.score(res["gue_new"]["n_f3_stretch"])

ratios = {}
for sc in ("iid", "gue"):
    tn = [t for t in res[f"{sc}_new"]["taus"] if t is not None]
    if tn:
        t_new, t_old = max(tn), TAU_OLD[sc]
        ratios[sc] = max(t_new / t_old, t_old / t_new)
    else:
        ratios[sc] = 99.0
worst = max(ratios.values())
C2 = Bar("worst-class slow-tau ratio across conditioning times", 1.5,
         direction="le", floor=1.0, ceiling=100.0,
         why="max(new/old, old/new) is >= 1 by construction; 100 is a stated "
             "practical ceiling for a timescale that has moved beyond comparison")
c2 = C2.score(worst)

C3 = Bar("iid bins selecting F3 with beta < 0.9 (adapted, control)", 2.5,
         floor=0, ceiling=NBINS,
         why="the same threshold on the control arm, 0 to 5 bins")
c3 = C3.score(res["iid_new"]["n_f3_stretch"])

# ---- report ----
print()
print(INSTRUMENT.report())
print(f"\nP1 old-design GUE re-run: forms {res['gue_old']['selected_forms']}")
print(f"                   banked: forms {bank['selected_forms']}")
print(f"  taus re-run: {[None if t is None else round(t, 4) for t in res['gue_old']['taus']]}")
print(f"  taus banked: {[None if t is None else round(t, 4) for t in bank['taus']]}")
print(f"  mismatches: {mm} of 10")
for sc in ("gue", "iid"):
    a = res[f"{sc}_new"]
    print(f"\n{sc.upper()} adapted (K_COND=1, dense grid) -> {a['ladder_outcome']}")
    print(f"  windows: {a['windows']}   forms: {a['selected_forms']}")
    print(f"  taus   : {[None if t is None else round(t, 4) for t in a['taus']]}")
    print(f"  betas  : {[None if b is None else round(b, 4) for b in a['betas']]}")
    print(f"  n_f3_stretch {a['n_f3_stretch']}/5, n_f2 {a['n_f2']}/5, "
          f"tau monotone {a['tau_monotone']}")
print(f"\nslow-tau across conditioning times (largest per-bin tau):")
for sc in ("iid", "gue"):
    tn = [t for t in res[f"{sc}_new"]["taus"] if t is not None]
    print(f"  {sc}: K_COND=2 {TAU_OLD[sc]:.3f}  ->  K_COND=1 "
          f"{max(tn) if tn else float('nan'):.3f}   ratio {ratios[sc]:.3f}")
print()
for b, v, f in ((P1, mm, "{:.0f}"), (P2, min(res["gue_new"]["windows"]), "{:.0f}"),
                (C1, res["gue_new"]["n_f3_stretch"], "{:.0f}"),
                (C2, worst, "{:.3f}"),
                (C3, res["iid_new"]["n_f3_stretch"], "{:.0f}")):
    print("  " + b.line(v, f))

v = compose([Arm.from_bar(p1, PREM_ROLE,
                          claim="this harness reproduces the banked isoconfig cell"),
             Arm.from_bar(p2, PREM_ROLE,
                          claim="the adaptation delivers assessable GUE windows"),
             Arm.from_bar(c1, EX_ROLE,
                          claim="GUE's stretch survives conditioning, as iid's did"),
             Arm.from_bar(c2, MECH_ROLE,
                          claim="the slow subpopulation keeps its timescale at a "
                                "third conditioning time"),
             Arm.from_bar(c3, RES_ROLE,
                          claim="and the iid control still reads NOT_SUPPORTED "
                                "under the same adapted design")],
            holds="STRETCH_MECHANISM_IS_NOT_SEED_DEPENDENT",
            fails="STRETCH_MECHANISM_SEED_DEPENDENCE_NOT_ESTABLISHED")
print(f"\nVERDICT: {v['citation']}")

json.dump(dict(
    n=N, replicates=R, nbins=NBINS,
    designs={"old": {"K_COND": K_COND_OLD, "k_grid": K_GRID_OLD},
             "adapted": {"K_COND": K_COND_NEW, "k_grid": K_GRID_NEW}},
    arms=res, tau_old_anchor=TAU_OLD, tau_ratios=ratios,
    p1_mismatches=mm,
    bars={s["name"]: s for s in (p1, p2, c1, c2, c3)},
    instrument=INSTRUMENT.seal(),
    scope="exploratory, unsealed science (inherits Step 2b's grade). Adjudicates "
          "the MECHANISM question with the pre-committed Step 2 ladder; does not "
          "touch the sealed RATE-SEED-DEPENDENT verdict.",
    verdict=v["head"], composed=v,
    runtime_s=round(time.time() - t0, 1)),
    open(os.path.join(HERE, "gue_isoconfig_adapted.json"), "w"), indent=1)
print("\nwrote gue_isoconfig_adapted.json")
