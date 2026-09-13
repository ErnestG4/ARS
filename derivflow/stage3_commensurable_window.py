#!/usr/bin/env python3
"""STAGE 3 — does RATE-SEED-DEPENDENT survive a window both classes share?

COMMITTED GENERATOR of derivflow/stage3_commensurable_window.json.
Predictions sealed here, before any commensurable-window fit exists.

THE QUESTION, unchanged since RECERT_SCOPE opened and still the only one that
matters. The sealed verdict is that the two seed classes DIFFER in relaxation
rate. The fit windows they are compared on are set by a threshold -- `mean >
1e-3` on the full ensemble -- and that threshold lands in a different place for
each class: iid gets k = 1..16 (16 points), GUE gets k = 1..11 (11 points). So a
claim that the classes differ is read off fits taken over different domains,
which is the [[commensurability-check]] failure in its plainest form. The arc's
own rule already says tau is degenerate with beta and is not commensurable across
fits; this asks whether the WINDOW carries the same problem.

WHY THIS DOES NOT NEED THE RECERT GATE. Stages 1, 2a and 2b were building an
instrument-side known-answer gate, and Stage 2c is parked: seven constructions,
six of which failed on how the configuration and reference relate, and the
seventh converges too slowly to ensemble. None of that is required here. This
cell changes ONE thing -- the k-range both classes are fitted over -- and reads
the consequence. The instrument is held fixed at exactly the sealed settings.

WHAT IT RE-DERIVES RATHER THAN TRUSTS. The per-replicate curves were never banked
by the dense-grid science (an internal-rule violation the paper already
discloses), and zbeta_correlated_error recovered them without banking them
either, so this is the THIRD recovery of the same object. It is banked here.
P1/P2 make the recovery a premise: the re-run must reproduce the banked ensemble
statistics exactly, AND refitting on the SEALED per-class windows must reproduce
the sealed shape parameters and shape-z exactly. Only then does changing the
window mean anything.

THE COMPARISON IS AT k*, NOT AT tau. Fixed by the arc's own rule
(gue_isoconfig_kstar_amendment, tau_vs_kstar_census): tau in F3 is degenerate
with the stretch exponent, and k* is the level crossing, defined identically for
every form in the ladder. The sealed shape-z is reported alongside for
continuity, not as the discriminant.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — every bar strictly inside its stated range.             ║
║                                                                              ║
║ P1  PREMISE     RECOVERY IS EXACT: the re-run reproduces science_dense_grid's ║
║                 banked mean and sigma_mean at all 20 k for both classes at    ║
║                 n=4096. Mismatches <= 0.5 of 80 at 1e-12 relative. A third    ║
║                 recovery that does not reproduce is a different instrument.   ║
║ P2  PREMISE     THE ADJUDICATION REPRODUCES: refitting F3 on each class's     ║
║                 OWN sealed window returns the banked shape_params and both    ║
║                 sealed shape-z values. Mismatches <= 0.5 of 8. If the sealed  ║
║                 fit cannot be reproduced, no statement about changing the     ║
║                 window is readable.                                          ║
║ C1  EXISTENCE   THE VERDICT SURVIVES: on the COMMENSURABLE window -- the      ║
║                 intersection k = 1..11, which both classes reach by the       ║
║                 sealed threshold -- the bootstrap z(k*) between classes       ║
║                 >= 5.0, the arc's own sealed bar. MET composes                ║
║                 RATE_SEED_DEPENDENCE_SURVIVES_A_COMMENSURABLE_WINDOW.         ║
║                 MISSED means the sealed verdict rests on the window           ║
║                 asymmetry and must be re-graded. It can genuinely miss:       ║
║                 dropping iid from 16 points to 11 removes a third of its      ║
║                 lever arm, and k* is an extrapolated level crossing.          ║
║ C2  MECHANISM   AND IT IS NOT MERELY THE WINDOW MOVING THE NUMBER:            ║
║                 |z(k*) commensurable - z(k*) sealed-windows| / z_sealed       ║
║                 <= 0.5. A verdict that survives but whose magnitude halves    ║
║                 is a different claim than one that is stable, and the         ║
║                 paper quotes the magnitude.                                   ║
║ C3  RESOLUTION  WINDOW-INVARIANCE ACROSS THE SWEEP: z(k*) clears 5.0 on all   ║
║                 three windows tested (1..8, 1..11, 1..16). Bar: 3 of 3. This  ║
║                 is the strong form -- a verdict that holds only at one        ║
║                 window choice is a verdict about the window.                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

SCOPE. Re-fits the SEALED science on alternative windows with the instrument held
fixed. It does not re-run the instrument, does not touch Stages 1-2, and does not
by itself re-grade anything -- Stage 4 is Will's.
"""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
from scipy.optimize import curve_fit

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

from reachable import Bar                                            # noqa: E402
from verdictlattice import (Arm, compose, PREMISE as PREM_ROLE,      # noqa: E402
                            EXISTENCE as EX_ROLE,
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from modelparams import Model, Param, TESTED, DECLARED               # noqa: E402
from science_rate_question import (one_flow, f3, gue_seed, MASTER_SEED,  # noqa: E402
                                   LN10, KSTAR_LEVEL, FIT_WINDOW_MIN)

N = 4096
R = 16
NI = 2
K_DENSE = list(range(1, 17)) + [24, 32, 48, 64]
WINDOWS = [8, 11, 16]            # upper k of each commensurable window tested
K_COMMENSURABLE = 11
B_BOOT = 2000
BOOT_SEED = 20260913
SEALED_Z_BAR = 5.0

INSTRUMENT = Model("sealed science refitted on shared windows", [
    Param("window_upper_k", TESTED, sweep=WINDOWS,
          why="THE axis. 11 is the intersection both classes reach under the "
              "sealed mean>1e-3 rule; 16 is iid's own window applied to GUE too "
              "(those GUE points exist, they are merely below the threshold); 8 "
              "is a shorter shared window, because a verdict that needs the "
              "longest lever arm available is a weaker verdict than one that "
              "does not"),
    Param("comparison_statistic", DECLARED, value="k* (level crossing)",
          why="fixed by the arc's own rule: tau in F3 is degenerate with the "
              "stretch exponent and is not commensurable across fits "
              "(gue_isoconfig_kstar_amendment, tau_vs_kstar_census). k* is "
              "defined identically for every form in the ladder"),
    Param("form", DECLARED, value="F3",
          why="held from the sealed adjudication. Re-selecting the form per "
              "window would confound a window question with a model-choice "
              "question, and the sealed ladder already chose F3 on every band "
              "at every n"),
    Param("bootstrap_B", DECLARED, value=B_BOOT,
          why="resamples of the 16-replicate ensemble, matching "
              "zbeta_correlated_error and roster_stretch_error so all three "
              "error models are directly comparable"),
    Param("resample_unit", DECLARED, value="replicate (whole curve)",
          why="the 16 replicates are SHARED across k within a curve; resampling "
              "k-points would destroy the correlation that zbeta established "
              "is real and class-dependent"),
    Param("n", DECLARED, value=N,
          why="the adjudicated size; the sealed shape-z is defined at n=4096"),
])


def _one(args):
    sc, i, child = args
    rng = np.random.default_rng(child)
    seed = (np.sort(rng.uniform(-1, 1, N)) if sc == "iid" else gue_seed(N, rng))
    rec = one_flow(seed, N, K_DENSE, f"{sc} rep={i}")
    return sc, i, [rec[k]["one_minus_rtilde"] for k in K_DENSE]


def recover():
    """Third recovery of the per-replicate curves. BANKED this time."""
    ch = np.random.SeedSequence(MASTER_SEED).spawn(96)
    jobs = ([("iid", i, ch[0 + NI * R + i]) for i in range(R)]
            + [("gue", i, ch[48 + NI * R + i]) for i in range(R)])
    with Pool(8) as p:
        res = p.map(_one, jobs)
    out = {"iid": [None] * R, "gue": [None] * R}
    for sc, i, cur in res:
        out[sc][i] = cur
    return {sc: np.array(v) for sc, v in out.items()}


def fit_f3(means, sig, ks):
    y = np.log10(means)
    sy = sig / (means * LN10)
    best = None
    for t in (2.0, 5.0, 10.0, 30.0):
        for b in (0.5, 0.75, 1.0):
            try:
                p, cov = curve_fit(f3, ks, y, p0=[y[0], t, b], sigma=sy,
                                   absolute_sigma=True,
                                   bounds=([-np.inf, 1e-3, 0.05],
                                           [np.inf, 1e4, 3.0]), maxfev=20000)
                c2 = float(np.sum(((y - f3(ks, *p)) / sy) ** 2))
                if np.isfinite(c2) and np.all(np.isfinite(cov)) and (
                        best is None or c2 < best[0]):
                    best = (c2, p, cov)
            except Exception:
                continue
    return best


def kstar_of(p):
    la, tau, be = p
    return tau * ((la - np.log10(KSTAR_LEVEL)) / np.log10(np.e)) ** (1.0 / be)


t0 = time.time()
print(f"recovering {2 * R} flows at n={N} (8 workers)...", flush=True)
curves = recover()
print(f"  flows done in {time.time() - t0:.0f}s", flush=True)

KA = np.array(K_DENSE, float)
bank = json.load(open(os.path.join(HERE, "science_dense_grid.json")))

# ---------- P1: recovery reproduces the banked ensemble ----------
p1_mis = 0
for sc in ("iid", "gue"):
    cell = bank["data"][sc][str(N)]
    for j, k in enumerate(K_DENSE):
        col = curves[sc][:, j]
        for got, want in ((float(np.mean(col)), cell[str(k)]["mean"]),
                          (float(np.std(col, ddof=1) / np.sqrt(R)),
                           cell[str(k)]["sigma_mean"])):
            if abs(got - want) > 1e-12 * max(abs(want), 1e-300):
                p1_mis += 1
P1 = Bar("recovery mismatches vs the banked ensemble (80 numbers)", 0.5,
         floor=0, ceiling=80, direction="le",
         why="2 classes x 20 k x {mean, sigma_mean} at n=4096; a count of "
             "disagreements at 1e-12 relative, 0 to 80 by construction")
p1 = P1.score(p1_mis)

means = {sc: curves[sc].mean(axis=0) for sc in ("iid", "gue")}
sigs = {sc: curves[sc].std(axis=0, ddof=1) / np.sqrt(R) for sc in ("iid", "gue")}

# ---------- P2: the sealed adjudication reproduces ----------
sealed_fits, p2_mis = {}, 0
for sc in ("iid", "gue"):
    w = means[sc] > FIT_WINDOW_MIN
    c2, p, cov = fit_f3(means[sc][w], sigs[sc][w], KA[w])
    sealed_fits[sc] = dict(params=p, cov=cov, chi2=c2, n=int(w.sum()))
    for got, want in zip(p, bank["adjudication"]["shape_params"][sc]):
        if abs(got - want) > 1e-9 * max(abs(want), 1e-300):
            p2_mis += 1
ss = np.array(bank["adjudication"]["shape_params"]["iid"]) - \
     np.array(bank["adjudication"]["shape_params"]["gue"])
for key, idx in (("param1", 1), ("param2", 2)):
    se = np.hypot(np.sqrt(sealed_fits["iid"]["cov"][idx, idx]),
                  np.sqrt(sealed_fits["gue"]["cov"][idx, idx]))
    z = abs(ss[idx]) / se
    if abs(z - bank["adjudication"]["shape_z"][key]) > 1e-6 * abs(
            bank["adjudication"]["shape_z"][key]):
        p2_mis += 1
P2 = Bar("sealed-adjudication reproduction mismatches (8 numbers)", 0.5,
         floor=0, ceiling=8, direction="le",
         why="6 shape parameters + 2 sealed shape-z values; a count of "
             "disagreements, 0 to 8 by construction")
p2 = P2.score(p2_mis)

# ---------- the window sweep, bootstrapped ----------
rng = np.random.default_rng(BOOT_SEED)
res = {}
for kw in WINDOWS + ["sealed"]:
    ks_b = {sc: [] for sc in ("iid", "gue")}
    for _ in range(B_BOOT):
        idx = rng.integers(0, R, R)
        for sc in ("iid", "gue"):
            c = curves[sc][idx]
            mu = c.mean(axis=0)
            sg = c.std(axis=0, ddof=1) / np.sqrt(R)
            w = (mu > FIT_WINDOW_MIN) if kw == "sealed" else (KA <= kw)
            if w.sum() < 5 or np.any(mu[w] <= 0):
                continue
            got = fit_f3(mu[w], sg[w], KA[w])
            if got is None:
                continue
            kk = kstar_of(got[1])
            if np.isfinite(kk) and kk > 0:
                ks_b[sc].append(kk)
    nb = min(len(ks_b["iid"]), len(ks_b["gue"]))
    a, b = np.array(ks_b["iid"][:nb]), np.array(ks_b["gue"][:nb])
    pt = {}
    for sc in ("iid", "gue"):
        w = (means[sc] > FIT_WINDOW_MIN) if kw == "sealed" else (KA <= kw)
        pt[sc] = kstar_of(fit_f3(means[sc][w], sigs[sc][w], KA[w])[1])
    z = abs(pt["iid"] - pt["gue"]) / np.hypot(a.std(ddof=1), b.std(ddof=1))
    res[kw] = dict(kstar_iid=float(pt["iid"]), kstar_gue=float(pt["gue"]),
                   se_iid=float(a.std(ddof=1)), se_gue=float(b.std(ddof=1)),
                   z=float(z), n_ok=int(nb),
                   n_pts_iid=int(((means["iid"] > FIT_WINDOW_MIN) if kw == "sealed"
                                  else (KA <= kw)).sum()),
                   n_pts_gue=int(((means["gue"] > FIT_WINDOW_MIN) if kw == "sealed"
                                  else (KA <= kw)).sum()))
    print(f"  window {str(kw):>7}: k* iid {pt['iid']:.4f} gue {pt['gue']:.4f}  "
          f"z={z:.2f}  ({time.time() - t0:.0f}s)", flush=True)

z_comm, z_sealed = res[K_COMMENSURABLE]["z"], res["sealed"]["z"]
C1 = Bar(f"bootstrap z(k*) on the commensurable window k<={K_COMMENSURABLE}",
         SEALED_Z_BAR, floor=0.0, ceiling=1000.0, direction="ge",
         why="the arc's OWN sealed 5-sigma bar, applied to the arc's own "
             "comparison statistic; a z is non-negative and 1000 is a stated "
             "practical ceiling")
c1 = C1.score(z_comm)
C2 = Bar("|z_commensurable - z_sealed| / z_sealed", 0.5, floor=0.0,
         ceiling=100.0, direction="le",
         why="a relative change in the quoted magnitude; non-negative, and 100 "
             "is a stated practical ceiling (a 100x change would mean the two "
             "fits are not describing the same comparison)")
c2 = C2.score(abs(z_comm - z_sealed) / max(z_sealed, 1e-12))
n_clear = sum(1 for kw in WINDOWS if res[kw]["z"] >= SEALED_Z_BAR)
C3 = Bar("windows clearing the sealed 5-sigma bar", 2.5, floor=0, ceiling=3,
         direction="ge",
         why="a count over the 3 shared windows tested; 2.5 requires all three, "
             "because a verdict that holds at only some window choices is a "
             "verdict about the window")
c3 = C3.score(n_clear)

print(INSTRUMENT.report())
print(f"\nP1 recovery: {p1_mis} of 80 mismatched")
print(f"P2 sealed adjudication: {p2_mis} of 8 mismatched")
print(f"\n{'window':>8} {'pts i/g':>9} {'k* iid':>9} {'k* gue':>9} {'z(k*)':>8}")
for kw in WINDOWS + ["sealed"]:
    r = res[kw]
    print(f"{str(kw):>8} {r['n_pts_iid']:>4}/{r['n_pts_gue']:<4} "
          f"{r['kstar_iid']:>9.4f} {r['kstar_gue']:>9.4f} {r['z']:>8.2f}")
print()
for bb, val, f in ((P1, p1_mis, "{:.0f}"), (P2, p2_mis, "{:.0f}"),
                   (C1, z_comm, "{:.2f}"),
                   (C2, abs(z_comm - z_sealed) / max(z_sealed, 1e-12), "{:.3f}"),
                   (C3, n_clear, "{:.0f}")):
    print("  " + bb.line(val, f))

v = compose(
    [Arm.from_bar(p1, PREM_ROLE, claim="the recovery IS the sealed ensemble"),
     Arm.from_bar(p2, PREM_ROLE, claim="and the sealed adjudication reproduces"),
     Arm.from_bar(c1, EX_ROLE,
                  claim="the classes still separate on a window they share"),
     Arm.from_bar(c2, MECH_ROLE, claim="without the magnitude moving much"),
     Arm.from_bar(c3, RES_ROLE, claim="at every shared window tested")],
    holds="RATE_SEED_DEPENDENCE_SURVIVES_A_COMMENSURABLE_WINDOW",
    fails="THE_SEALED_SEPARATION_DEPENDS_ON_THE_WINDOW_ASYMMETRY")
print(f"\nVERDICT: {v['citation']}")

json.dump(dict(
    n=N, replicates=R, k_grid=K_DENSE, windows=WINDOWS,
    k_commensurable=K_COMMENSURABLE, B=B_BOOT, boot_seed=BOOT_SEED,
    p1_mismatches=p1_mis, p2_mismatches=p2_mis,
    per_replicate_curves={sc: curves[sc].tolist() for sc in ("iid", "gue")},
    sealed_fits={sc: dict(params=list(map(float, sealed_fits[sc]["params"])),
                          chi2=float(sealed_fits[sc]["chi2"]),
                          n_points=sealed_fits[sc]["n"])
                 for sc in ("iid", "gue")},
    by_window={str(kw): res[kw] for kw in WINDOWS + ["sealed"]},
    z_commensurable=z_comm, z_sealed=z_sealed,
    bars={s["name"]: s for s in (p1, p2, c1, c2, c3)},
    instrument=INSTRUMENT.seal(),
    scope="RECERT_SCOPE Stage 3. Refits the SEALED science on shared windows "
          "with the instrument held fixed. Does not re-run the instrument and "
          "does not re-grade anything; Stage 4 is Will's. Per-replicate curves "
          "BANKED -- third recovery of the same object.",
    verdict=v["head"], composed=v,
    runtime_s=round(time.time() - t0, 1),
), open(os.path.join(HERE, "stage3_commensurable_window.json"), "w"), indent=1)
print("\nwrote stage3_commensurable_window.json")
