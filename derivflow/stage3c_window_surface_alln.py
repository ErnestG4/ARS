#!/usr/bin/env python3
"""STAGE 3c — is the window sensitivity an n=4096 artifact?

COMMITTED GENERATOR of derivflow/stage3c_window_surface_alln.json.
Predictions sealed here, before any n != 4096 window surface exists.

WHY THIS RUNS. Stage 3b (ea96b69) measured, at n=4096 only: the k* separation
moves 6.1% across 15 defensible window rules while z(beta) -- the number the
paper leads with -- moves 95.6x, and the SEALED window sits at the 87th
percentile of that range. That is the basis for a disclosure the paper does not
currently carry, so it had better not be a property of one n.

A design audit of Stage 3 checked the other n with MVN fit errors and found the
ordering stable. MVN is not the error model 3b adjudicated on, and
roster_stretch_error (72d6a28) measured MVN k* errors to be 2.1-2.5x TIGHTER
than resampling on this same family. So the other-n check has to be redone with
the bootstrap, which needs per-replicate curves at n=1024 and n=2048 -- banked
nowhere. This cell recovers them (deterministic under the seal's SeedSequence,
children 0+NI*R+i for iid and 48+NI*R+i for gue, NI the index of n in
[1024,2048,4096]) and BANKS them, so no later cell pays for this again.

WHAT WOULD MAKE THE DISCLOSURE UNNECESSARY: if the z(beta) swing collapses at
smaller n, the 95.6x is an n=4096 peculiarity and the paper's number is safer
than 3b suggested. C2 is written so that outcome MISSES.

DISCLOSED PRIOR LOOK. The n=4096 row of this surface is Stage 3b, already seen.
The n=1024 and n=2048 rows are not: no bootstrap surface exists at those n, and
every bar below is set from a reachability argument or carried verbatim from 3b
rather than from any value seen at the new n. Grade DECLARED-WITH-PRIOR-LOOK.

LINEAGE, declared because two cells sharing a construction are not independent
evidence (a defect this arc committed in Stage 2a's P2 and had to correct):
this cell SHARES with Stage 3b the fitter, the window rules, the discriminant
and the bootstrap protocol. It shares NO DATA at n=1024/2048, which is the whole
point; the n=4096 column is a REPRODUCTION of 3b, not a confirmation of it, and
P3 tests it as such.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — every bar strictly inside its stated range.             ║
║                                                                              ║
║ P1  PREMISE     RECOVERY IS EXACT AT EVERY n: recovered mean and sigma_mean   ║
║                 reproduce science_dense_grid at all 20 k, both classes,       ║
║                 all three n. Mismatches <= 0.5 of 240.                       ║
║ P2  PREMISE     THE SEALED ADJUDICATION REPRODUCES AT n=4096, judged in       ║
║                 units of each parameter's OWN standard error, <= 1e-3 sigma.  ║
║                 Stage 3's absolute 1e-9 bar failed this same fit; 3b's        ║
║                 conditioning-aware bar cleared it at 2.45e-07.                ║
║ P3  PREMISE     THE n=4096 COLUMN REPRODUCES STAGE 3b to 1e-9 relative on     ║
║                 z(beta) at every one of its 15 cells. Same data, same         ║
║                 protocol -- so this is a reproduction check, and a failure    ║
║                 means the two cells are not running the same measurement.     ║
║ C1  EXISTENCE   THE SEPARATION IS ROBUST AT EVERY n: worst-over-n of          ║
║                 (max-min)/mean of the k* separation <= 0.25. MISSED means     ║
║                 the sealed science's central claim is window-dependent        ║
║                 somewhere, which would be the most serious finding of the     ║
║                 arc.                                                         ║
║ C2  MECHANISM   THE SIGNIFICANCE SWING IS NOT AN n=4096 ARTIFACT: the         ║
║                 z(beta) max/min swing is >= 3.0 at EVERY n (3 of 3). If it    ║
║                 collapses at smaller n this MISSES and the disclosure is      ║
║                 narrower than 3b implied -- a clean, useful negative.         ║
║ C3  RESOLUTION  AND THE SEALED WINDOW IS FAVOURABLY PLACED AT EVERY n: the    ║
║                 MINIMUM over n of the sealed z(beta) percentile > 0.75.       ║
║                 3b measured 0.87 at n=4096 and MISSED its own 0.75 bar;       ║
║                 this asks whether that holds generally. Stated in the         ║
║                 direction where MET is the uncomfortable answer.              ║
╚══════════════════════════════════════════════════════════════════════════════╝

SCOPE. Recovers flows at two n and refits banked+recovered data over a window
surface. Changes no instrument and re-grades nothing.
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

NS = [1024, 2048, 4096]
R = 16
K_LO = [1, 2, 3, 4, 5]
UPPER = ["sealed_1e-3", "shared_11", "shared_16"]
B_BOOT = 600
BOOT_SEED = 20260914

INSTRUMENT = Model("sealed science refitted over a window surface at every n", [
    Param("n", TESTED, sweep=NS,
          why="THE axis this cell adds. Stage 3b measured the whole surface at "
              "n=4096 only, and a disclosure resting on one n is a disclosure "
              "about one n"),
    Param("window_lower_k", TESTED, sweep=K_LO,
          why="carried from 3b, where it was the edge Stage 3 omitted entirely. "
              "This is where the significance lives while the separation does not "
              "move"),
    Param("window_upper_rule", TESTED, sweep=UPPER,
          why="sealed_1e-3 is the science's own OBSERVABLE-matched rule; "
              "shared_11 and shared_16 equalise k and thereby de-equalise the "
              "observable. Decades spanned are recorded per cell"),
    Param("discriminant", DECLARED, value="z(beta) from the fit covariance",
          why="what the paper quotes. k* is carried alongside to show the two "
              "diverge, which is 3b's finding and the reason this cell exists"),
    Param("form", DECLARED, value="F3",
          why="held from the sealed adjudication; an independent audit ran the "
              "full ladder on all 24 (n, class, window) cells and F3 wins every "
              "one"),
    Param("bootstrap_B", DECLARED, value=B_BOOT,
          why="45 cells x 2 classes x 3 n; 600 keeps Monte-Carlo noise well "
              "under the 1/sqrt(2(R-1)) ~ 18% floor the 16-replicate ensemble "
              "imposes on any resampled SE, which B cannot improve"),
    Param("error_model", DECLARED, value="absolute_sigma diagonal, as sealed",
          why="the sealed fit's own error model, kept so the reproduced z "
              "matches the published one. zbeta filed it as optimistic; that is "
              "a known limitation, not one this cell introduces"),
])


def fit_f3(mu, sg, ks):
    y, sy = np.log10(mu), sg / (mu * LN10)
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
    return p[1] * ((p[0] - np.log10(KSTAR_LEVEL)) / np.log10(np.e)) ** (1.0 / p[2])


def mask(mu, ka, lo, rule):
    up = (mu > FIT_WINDOW_MIN) if rule == "sealed_1e-3" else (
        ka <= (11 if rule == "shared_11" else 16))
    return up & (ka >= lo)


def _one(args):
    sc, i, n, child, kd = args
    rng = np.random.default_rng(child)
    seed = (np.sort(rng.uniform(-1, 1, n)) if sc == "iid" else gue_seed(n, rng))
    rec = one_flow(seed, n, kd, f"{sc} n={n} rep={i}")
    return sc, i, n, [rec[k]["one_minus_rtilde"] for k in kd]


t0 = time.time()
s3 = json.load(open(os.path.join(HERE, "stage3_commensurable_window.json")))
bank = json.load(open(os.path.join(HERE, "science_dense_grid.json")))
s3b = json.load(open(os.path.join(HERE, "stage3b_window_surface.json")))
K_DENSE = s3["k_grid"]
KA = np.array(K_DENSE, float)

curves = {4096: {sc: np.array(s3["per_replicate_curves"][sc])
                 for sc in ("iid", "gue")}}
need = [n for n in NS if n not in curves]
print(f"recovering {2 * R * len(need)} flows at n={need} (8 workers)...", flush=True)
ch = np.random.SeedSequence(MASTER_SEED).spawn(96)
jobs = []
for n in need:
    ni = NS.index(n)
    jobs += [("iid", i, n, ch[0 + ni * R + i], K_DENSE) for i in range(R)]
    jobs += [("gue", i, n, ch[48 + ni * R + i], K_DENSE) for i in range(R)]
if jobs:
    with Pool(8) as p:
        res = p.map(_one, jobs)
    for n in need:
        curves[n] = {sc: np.zeros((R, len(K_DENSE))) for sc in ("iid", "gue")}
    for sc, i, n, cur in res:
        curves[n][sc][i] = cur
print(f"  flows done in {time.time() - t0:.0f}s", flush=True)

means = {n: {sc: curves[n][sc].mean(axis=0) for sc in ("iid", "gue")} for n in NS}
sigs = {n: {sc: curves[n][sc].std(axis=0, ddof=1) / np.sqrt(R)
            for sc in ("iid", "gue")} for n in NS}

# ---------- P1 ----------
p1 = 0
for n in NS:
    for sc in ("iid", "gue"):
        cell = bank["data"][sc][str(n)]
        for j, k in enumerate(K_DENSE):
            for got, want in ((means[n][sc][j], cell[str(k)]["mean"]),
                              (sigs[n][sc][j], cell[str(k)]["sigma_mean"])):
                if abs(got - want) > 1e-12 * max(abs(want), 1e-300):
                    p1 += 1
P1 = Bar("recovery mismatches across all three n (240 numbers)", 0.5,
         floor=0, ceiling=240, direction="le",
         why="3 n x 2 classes x 20 k x {mean, sigma_mean}; a count of "
             "disagreements at 1e-12 relative, 0 to 240 by construction")
b1 = P1.score(p1)

# ---------- P2 ----------
worst_sig = 0.0
for sc in ("iid", "gue"):
    w = mask(means[4096][sc], KA, 1, "sealed_1e-3")
    _, p, cov = fit_f3(means[4096][sc][w], sigs[4096][sc][w], KA[w])
    for i, want in enumerate(bank["adjudication"]["shape_params"][sc]):
        worst_sig = max(worst_sig, abs(p[i] - want) / max(np.sqrt(cov[i, i]), 1e-300))
P2 = Bar("worst |recovered - banked| in units of that parameter's own sigma",
         1e-3, floor=0.0, ceiling=10.0, direction="le",
         why="a discrepancy measured in the fit's OWN uncertainty, so a shallow "
             "optimum is judged by what it can support. 10 sigma is a stated "
             "practical ceiling; Stage 3's absolute 1e-9 bar failed this same "
             "fit and 3b's conditioning-aware bar cleared it at 2.45e-07")
b2 = P2.score(float(worst_sig))

# ---------- the surface, per n ----------
rng = np.random.default_rng(BOOT_SEED)
surf = {}
for n in NS:
    for lo in K_LO:
        for rule in UPPER:
            fits, dec, npts, ok = {}, {}, {}, True
            for sc in ("iid", "gue"):
                w = mask(means[n][sc], KA, lo, rule)
                if w.sum() < 5:
                    ok = False
                    break
                got = fit_f3(means[n][sc][w], sigs[n][sc][w], KA[w])
                if got is None:
                    ok = False
                    break
                fits[sc], npts[sc] = got, int(w.sum())
                kk = KA[w]
                dec[sc] = float(f3(kk[0], *got[1]) - f3(kk[-1], *got[1]))
            if not ok:
                continue
            z = {}
            for nm, i in (("tau", 1), ("beta", 2)):
                d_ = abs(fits["iid"][1][i] - fits["gue"][1][i])
                se = np.hypot(np.sqrt(fits["iid"][2][i, i]),
                              np.sqrt(fits["gue"][2][i, i]))
                z[nm] = float(d_ / se)
            kp = {sc: kstar_of(fits[sc][1]) for sc in ("iid", "gue")}
            bs = {sc: [] for sc in ("iid", "gue")}
            for _ in range(B_BOOT):
                idx = rng.integers(0, R, R)
                for sc in ("iid", "gue"):
                    c = curves[n][sc][idx]
                    mu = c.mean(axis=0)
                    sg = c.std(axis=0, ddof=1) / np.sqrt(R)
                    w2 = mask(mu, KA, lo, rule)
                    if w2.sum() < 5 or np.any(mu[w2] <= 0):
                        continue
                    g2 = fit_f3(mu[w2], sg[w2], KA[w2])
                    if g2 is None:
                        continue
                    kk2 = kstar_of(g2[1])
                    if np.isfinite(kk2) and kk2 > 0:
                        bs[sc].append(kk2)
            sep = abs(kp["iid"] - kp["gue"])
            se_k = np.hypot(np.std(bs["iid"], ddof=1) if len(bs["iid"]) > 2 else np.inf,
                            np.std(bs["gue"], ddof=1) if len(bs["gue"]) > 2 else np.inf)
            surf[(n, lo, rule)] = dict(
                z_tau=z["tau"], z_beta=z["beta"], sep=float(sep),
                z_kstar=float(sep / se_k) if np.isfinite(se_k) and se_k > 0 else float("nan"),
                kstar_iid=float(kp["iid"]), kstar_gue=float(kp["gue"]),
                n_iid=npts["iid"], n_gue=npts["gue"],
                dec_iid=dec["iid"], dec_gue=dec["gue"],
                chi2dof_iid=fits["iid"][0] / max(npts["iid"] - 3, 1),
                chi2dof_gue=fits["gue"][0] / max(npts["gue"] - 3, 1))
    print(f"  n={n} surface done ({time.time() - t0:.0f}s)", flush=True)

per_n = {}
for n in NS:
    seps = np.array([v["sep"] for (nn, _, _), v in surf.items() if nn == n])
    zb = np.array([v["z_beta"] for (nn, _, _), v in surf.items() if nn == n])
    sealed_zb = surf[(n, 1, "sealed_1e-3")]["z_beta"]
    per_n[n] = dict(spread=float((seps.max() - seps.min()) / seps.mean()),
                    swing=float(zb.max() / max(zb.min(), 1e-12)),
                    sealed_zbeta=float(sealed_zb),
                    pct=float(np.mean(zb <= sealed_zb)),
                    sep_min=float(seps.min()), sep_max=float(seps.max()),
                    zb_min=float(zb.min()), zb_max=float(zb.max()))

# ---------- P3: the n=4096 column reproduces Stage 3b ----------
p3 = 0
for lo in K_LO:
    for rule in UPPER:
        key3b = f"lo{lo}_{rule}"
        if key3b not in s3b["surface"]:
            continue
        a = surf[(4096, lo, rule)]["z_beta"]
        b = s3b["surface"][key3b]["z_beta"]
        if abs(a - b) > 1e-9 * max(abs(b), 1e-300):
            p3 += 1
P3 = Bar("n=4096 cells disagreeing with Stage 3b on z(beta)", 0.5, floor=0,
         ceiling=15, direction="le",
         why="15 cells, same data and same protocol, so this is a REPRODUCTION "
             "check; 0 to 15 by construction. A failure means the two cells are "
             "not running the same measurement")
b3 = P3.score(p3)

worst_spread = max(per_n[n]["spread"] for n in NS)
n_swing = sum(1 for n in NS if per_n[n]["swing"] >= 3.0)
min_pct = min(per_n[n]["pct"] for n in NS)

C1 = Bar("worst-over-n (max-min)/mean of the k* separation", 0.25, floor=0.0,
         ceiling=2.0, direction="le",
         why="a relative spread of a positive quantity; 0 is perfect invariance "
             "and 2 the practical ceiling (a spread of twice the mean would mean "
             "the separation changes sign somewhere)")
c1 = C1.score(worst_spread)
C2 = Bar("n at which the z(beta) swing reaches 3x", 2.5, floor=0, ceiling=3,
         direction="ge",
         why="a count over the 3 sizes; 2.5 requires all three. MISSED is a "
             "clean negative -- the swing would be an n=4096 peculiarity and the "
             "disclosure narrower than 3b implied")
c2 = C2.score(n_swing)
C3 = Bar("minimum over n of the SEALED z(beta) percentile", 0.75, floor=0.0,
         ceiling=1.0, direction="ge",
         why="a percentile, so [0,1] by construction. Stated so that MET is the "
             "UNCOMFORTABLE answer: the published window is favourably placed at "
             "every n, not just at 4096")
c3 = C3.score(min_pct)

print(INSTRUMENT.report())
print(f"\nP1 recovery: {p1} of 240 mismatched")
print(f"P2 worst reproduction: {worst_sig:.2e} sigma")
print(f"P3 vs Stage 3b at n=4096: {p3} of 15 cells disagree")
print(f"\n{'n':>6} {'sep range':>19} {'spread':>8} {'z(beta) range':>18} "
      f"{'swing':>8} {'sealed':>8} {'pct':>6}")
for n in NS:
    v = per_n[n]
    print(f"{n:>6} {v['sep_min']:>8.4f}-{v['sep_max']:<8.4f} {v['spread']:>8.1%} "
          f"{v['zb_min']:>8.2f}-{v['zb_max']:<8.2f} {v['swing']:>8.1f} "
          f"{v['sealed_zbeta']:>8.2f} {v['pct']:>6.2f}")
print()
for bb, val, f in ((P1, p1, "{:.0f}"), (P2, worst_sig, "{:.2e}"),
                   (P3, p3, "{:.0f}"), (C1, worst_spread, "{:.3f}"),
                   (C2, n_swing, "{:.0f}"), (C3, min_pct, "{:.2f}")):
    print("  " + bb.line(val, f))

v = compose(
    [Arm.from_bar(b1, PREM_ROLE, claim="the recovery is exact at every n"),
     Arm.from_bar(b2, PREM_ROLE, claim="and the sealed adjudication reproduces"),
     Arm.from_bar(b3, PREM_ROLE, claim="and n=4096 reproduces Stage 3b"),
     Arm.from_bar(c1, EX_ROLE, claim="the separation is robust at every n"),
     Arm.from_bar(c2, MECH_ROLE,
                  claim="while the significance swing is not an n=4096 artifact"),
     Arm.from_bar(c3, RES_ROLE,
                  claim="and the published window is favourably placed at every n")],
    holds="SEPARATION_ROBUST_AND_SIGNIFICANCE_WINDOW_DEPENDENT_AT_EVERY_N",
    fails="THE_SEPARATION_ITSELF_IS_WINDOW_DEPENDENT_AT_SOME_N")
print(f"\nVERDICT: {v['citation']}")

json.dump(dict(
    ns=NS, replicates=R, k_grid=K_DENSE, k_lo=K_LO, upper_rules=UPPER,
    B=B_BOOT, boot_seed=BOOT_SEED,
    p1_mismatches=p1, p2_worst_in_sigma=float(worst_sig), p3_disagree=p3,
    per_replicate_curves={str(n): {sc: curves[n][sc].tolist()
                                   for sc in ("iid", "gue")} for n in need},
    surface={f"n{n}_lo{lo}_{rule}": val for (n, lo, rule), val in surf.items()},
    per_n={str(n): per_n[n] for n in NS},
    worst_spread=worst_spread, n_with_swing=n_swing, min_percentile=min_pct,
    lineage=dict(shares_with_stage3b=["fitter", "window rules", "discriminant",
                                      "bootstrap protocol", "n=4096 data"],
                 independent_of_stage3b=["n=1024 data", "n=2048 data"],
                 note="the n=4096 column is a REPRODUCTION of Stage 3b, not "
                      "independent confirmation of it; P3 tests it as such"),
    bars={s["name"]: s for s in (b1, b2, b3, c1, c2, c3)},
    instrument=INSTRUMENT.seal(),
    scope="RECERT_SCOPE Stage 3c. Recovers flows at n=1024 and n=2048, BANKS "
          "them, and refits the window surface at every n. Changes no "
          "instrument and re-grades nothing.",
    verdict=v["head"], composed=v,
    runtime_s=round(time.time() - t0, 1),
), open(os.path.join(HERE, "stage3c_window_surface_alln.json"), "w"), indent=1)
print("\nwrote stage3c_window_surface_alln.json")
