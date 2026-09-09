"""DOES THE GENUS GAP SURVIVE A LONGER WINDOW? Running F_genus_exponent's own queued test.

COMMITTED GENERATOR of approximability/F_window_exponent.json.
Predictions sealed here, before any vmax > 6 output exists.

THE TEST THIS RUNS, AND WHO WROTE ITS DECISION RULE
----------------------------------------------------
F_genus_exponent closed with a third account it could not exclude, and named the
experiment that would settle it, in its own words:

    "The test that separates them is cheap and is queued rather than run here,
    because it changes a DECLARED parameter of a sealed cell after seeing the
    cell's output: extend vmax to 10-12 and ask whether the residual gap
    shrinks. If it shrinks toward zero the exponent is genus-independent and
    every gap so far was window and estimator; if it holds at 0.08 the claim in
    MORNING_F is wrong."

That is a pre-registered decision rule written by an earlier cell, and this cell
executes it rather than inventing a new one. The chain so far, all banked:
F_reproduce measured a genus gap of 0.1138 against a 0.05 bar and refused to call
it a refutation, naming estimator bias as a rival account; F_genus_exponent
CONFIRMED that mechanism (disagreement genus-asymmetric at 2.51x, rho = -0.500
between estimator gap and deepest dip, both as predicted) but bounded it at about
30% of the gap, leaving 0.0800 under a robust estimator. The remaining rival is
FINITE WINDOW: the fit uses v = 1..6, and a sum of four eigenvalue powers
approaches its asymptotic slope differently from a sum of two.

EXPECTATION, STATED SO THE MISS IS INFORMATIVE: I expect the gap to SHRINK. The
residual is |1 - s_n| / p^n with |s_n| ~ C_n * p^(n/2) and C_n an oscillating
prefactor; a longer window averages more of that oscillation, so both genera
should approach the RH slope and the gap should close. If it does not, the third
account is exhausted too and MORNING_F's genus-independence claim is wrong --
which is a real result, not a disappointment.

IDENTICAL BATTERY. Same primes, same families, same estimators, same arithmetic
(the residual is computed exactly as F_genus_exponent computes it, verbatim). The
ONLY thing that varies is vmax, because a battery change and a window change at
once would confound the comparison this cell exists to make. P1 enforces that by
demanding the banked vmax = 6 numbers back.

PRECISION, checked before sealing rather than assumed: the residual is
~2g * p^(-v/2), which at the largest prime and window here (p = 29, v = 12) is
~7e-9, while the float noise floor of the ratio is ~2e-16. The signal clears the
noise by seven orders of magnitude, and the arithmetic stays valid to about
v = 20 at this prime. No high-precision path is needed and none is introduced.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — every bar strictly inside its stated range.             ║
║                                                                              ║
║ P1  PREMISE    at vmax = 6 this cell reproduces F_genus_exponent's five      ║
║                banked summary numbers (gap_ols, gap_theil_sen, asymmetry,    ║
║                rh_worst, rho) to 1e-9 relative, and its curve count of 212.  ║
║                Mismatches <= 0.5 of 6. Same battery or nothing.              ║
║ P2  PREMISE    the provable gates still hold at the LONGEST window: every    ║
║                curve passes Hasse-Weil and RH-for-curves at vmax = 12,       ║
║                failures <= 0.5. These are theorems, so a failure is not a    ║
║                result about arithmetic but a bug in the recurrence at high   ║
║                v -- which is exactly how MORNING_F found the k = 3,4 Newton  ║
║                identity bug, and extending to v = 12 exercises the k >= 5    ║
║                branch far harder than anything run before.                   ║
║ E1  EXISTENCE  the window matters at all: |gap_ts(12) - gap_ts(6)| > 0.01.   ║
║                If the gap is window-invariant, the third account is dead on  ║
║                arrival and E2/E3 are answering nothing.                      ║
║ E2  MECHANISM  and it moves the predicted way: gap_ts is monotone            ║
║                decreasing across vmax = 6, 8, 10, 12 -- inversions <= 0.5    ║
║                of 3.                                                        ║
║ E3  RESOLUTION THE QUEUED DECISION, at the bar the earlier cell missed:      ║
║                gap_ts at vmax = 12 <= 0.05. MET rescues genus-independence   ║
║                and retires the whole chain; MISSED means MORNING_F's claim   ║
║                is wrong and should be corrected in the findings.             ║
║ E4  RESOLUTION and both genera sit on the RH slope at vmax = 12: worst       ║
║                |Theil-Sen ratio - 1| <= 0.05, the bar that missed at 0.0559. ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import json
import os
import sys

import numpy as np
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
from reachable import Bar                                          # noqa: E402
from verdictlattice import (Arm, compose, PREMISE as PREM_ROLE,     # noqa: E402
                            EXISTENCE as EX_ROLE,
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from modelparams import Model, Param, TESTED, DECLARED              # noqa: E402
from ff_curve import g1_Nv, g2_Nv, hasse_weil_gate, rh_gate         # noqa: E402

# Battery constants DECLARED here and asserted against the banked artifact,
# never imported: F_genus_exponent measures at import time.
PRIMES = [7, 11, 13, 17, 19, 23, 29]
G1_AB = [(a, b) for a in range(1, 4) for b in range(1, 4)]
G2_C = [(c3, c1, c0) for c3 in range(3) for c1 in range(3) for c0 in range(3)]
VMAXES = [6, 8, 10, 12]
RH_BAR = 0.05
GAP_BAR = 0.05

INSTRUMENT = Model("finite-window test of the genus exponent gap", [
    Param("vmax", TESTED, sweep=VMAXES,
          why="THE variable of this cell: the fit window in v. Everything else "
              "is held at F_genus_exponent's values so the window is the only "
              "thing that moves"),
    Param("primes", DECLARED, value=str(PRIMES),
          why="identical battery; P1 demands the banked vmax=6 numbers back"),
    Param("estimators", DECLARED, value="OLS and Theil-Sen, verbatim",
          why="changing the estimator and the window together would rebuild the "
              "confound F_genus_exponent spent a whole cell bounding"),
    Param("residual_arithmetic", DECLARED, value="abs(Nv/float(p**v) - 1.0)",
          why="F_genus_exponent's expression, verbatim. Checked before sealing: "
              "at p=29, v=12 the residual is ~7e-9 against a float noise floor "
              "of ~2e-16, so no high-precision path is warranted"),
])


def poly_gcd_deg(f, p):
    """Squarefree test, as used by the banked battery to filter singular f."""
    def trim(a):
        while a and a[-1] % p == 0:
            a = a[:-1]
        return [c % p for c in a]

    def rem(a, b):
        a = a[:]
        db = len(b) - 1
        inv = pow(b[-1], p - 2, p)
        for i in range(len(a) - 1, db - 1, -1):
            c = (a[i] * inv) % p
            for j in range(db + 1):
                a[i - db + j] = (a[i - db + j] - c * b[j]) % p
        return trim(a)

    a, b = trim(list(f)), trim([(i * c) % p for i, c in enumerate(f)][1:])
    while b:
        a, b = b, rem(a, b)
    return max(len(a) - 1, 0)


def slopes(res, vmax):
    """VERBATIM from F_genus_exponent.slopes, with VMAX lifted to a parameter."""
    p = res["p"]
    n, y = [], []
    for v, Nv in enumerate(res["Nv"][:vmax], start=1):
        r = abs(Nv / float(p ** v) - 1.0)
        if r > 0:
            n.append(v)
            y.append(np.log10(r))
    if len(n) < 3:
        return None
    n, y = np.array(n, float), np.array(y, float)
    ols = float(np.polyfit(n, y, 1)[0])
    pair = [(y[j] - y[i]) / (n[j] - n[i])
            for i in range(len(n)) for j in range(i + 1, len(n))]
    ts = float(np.median(pair))
    denom = 0.5 * np.log10(p)
    return dict(ols=-ols / denom, ts=-ts / denom,
                deepest_dip=float(np.min(10.0 ** y)))


def battery(vmax, collect_gates=False):
    rows, gate_fail = [], 0
    for p in PRIMES:
        for (a, b) in G1_AB:
            try:
                res = g1_Nv(a, b, p, vmax=vmax)
            except AssertionError:
                continue
            if collect_gates and not (hasse_weil_gate(res, vmax) and rh_gate(res)):
                gate_fail += 1
            r = slopes(res, vmax)
            if r:
                rows.append(dict(genus=1, p=p, **r))
        for (c3, c1, c0) in G2_C:
            fc = [c0, c1, 0, c3, 0, 1]
            if poly_gcd_deg(fc, p) != 0:
                continue
            try:
                res = g2_Nv(fc, p, vmax=vmax)
            except Exception:
                continue
            if collect_gates and not (hasse_weil_gate(res, vmax) and rh_gate(res)):
                gate_fail += 1
            r = slopes(res, vmax)
            if r:
                rows.append(dict(genus=2, p=p, **r))
    for r in rows:
        r["est_gap"] = abs(r["ols"] - r["ts"])
    g = {k: [r for r in rows if r["genus"] == k] for k in (1, 2)}

    def mean(v, k):
        return float(np.mean([r[k] for r in v]))

    return dict(
        n=len(rows), gate_fail=gate_fail,
        gap_ols=abs(mean(g[1], "ols") - mean(g[2], "ols")),
        gap_ts=abs(mean(g[1], "ts") - mean(g[2], "ts")),
        asymmetry=mean(g[2], "est_gap") / max(mean(g[1], "est_gap"), 1e-12),
        rh_worst=max(abs(mean(g[1], "ts") - 1.0), abs(mean(g[2], "ts") - 1.0)),
        rho=float(spearmanr([r["est_gap"] for r in rows],
                            [r["deepest_dip"] for r in rows]).statistic),
        ts_by_genus={str(k): mean(g[k], "ts") for k in (1, 2)},
        n_by_genus={str(k): len(g[k]) for k in (1, 2)})


sweep = {}
for vm in VMAXES:
    sweep[vm] = battery(vm, collect_gates=(vm == max(VMAXES)))
    print(f"  vmax={vm:>3d}  n={sweep[vm]['n']:>4d}  gap_ols={sweep[vm]['gap_ols']:.4f}"
          f"  gap_ts={sweep[vm]['gap_ts']:.4f}  rh_worst={sweep[vm]['rh_worst']:.4f}",
          flush=True)

# ---- P1: reproduce the banked vmax=6 summary ----
bank = json.load(open(os.path.join(HERE, "F_genus_exponent.json")))
s6 = sweep[6]
checks = [(s6["gap_ols"], bank["gap_ols"]), (s6["gap_ts"], bank["gap_theil_sen"]),
          (s6["asymmetry"], bank["asymmetry"]), (s6["rh_worst"], bank["rh_worst"]),
          (s6["rho"], bank["rho_gap_vs_dip"]), (float(s6["n"]), float(bank["n"]))]
mismatch = sum(1 for got, want in checks
               if abs(got - want) > 1e-9 * max(abs(want), 1.0))
P1 = Bar("vmax=6 mismatches vs the 6 banked F_genus_exponent numbers", 0.5,
         direction="le", floor=0, ceiling=6,
         why="gap_ols, gap_ts, asymmetry, rh_worst, rho and the curve count; "
             "a count of disagreements at 1e-9 relative, 0 to 6")
p1 = P1.score(mismatch)

P2 = Bar("provable-gate failures at vmax=12", 0.5, direction="le",
         floor=0, ceiling=sweep[12]["n"],
         why="Hasse-Weil and RH-for-curves are theorems; a failure is a "
             "recurrence bug at high v, not a finding")
p2 = P2.score(sweep[12]["gate_fail"])

d_gap = abs(sweep[12]["gap_ts"] - sweep[6]["gap_ts"])
E1 = Bar("|gap_ts(12) - gap_ts(6)|", 0.01, floor=0.0, ceiling=2.0,
         why="a change in a difference of two ratios near 1; 0 is attainable "
             "if the window is irrelevant")
e1 = E1.score(d_gap)

seq = [sweep[v]["gap_ts"] for v in VMAXES]
inv = sum(1 for a, b in zip(seq, seq[1:]) if b >= a)
E2 = Bar("adjacent increases in gap_ts across the vmax sweep", 0.5,
         direction="le", floor=0, ceiling=len(VMAXES) - 1,
         why="3 adjacent pairs; monotone decreasing is the predicted shape")
e2 = E2.score(inv)

E3 = Bar("gap_ts at vmax=12", GAP_BAR, direction="le", floor=0.0, ceiling=2.0,
         why="the bar F_reproduce's M1 and F_genus_exponent's E2 both missed; "
             "a difference of two ratios near 1")
e3 = E3.score(sweep[12]["gap_ts"])

E4 = Bar("worst |Theil-Sen ratio - 1| at vmax=12", RH_BAR, direction="le",
         floor=0.0, ceiling=2.0,
         why="the RH slope check; missed at 0.0559 with the short window")
e4 = E4.score(sweep[12]["rh_worst"])

# ---- report ----
print()
print(INSTRUMENT.report())
print(f"\nP1: vmax=6 vs banked — {mismatch} of 6 mismatched")
print(f"P2: provable gates at vmax=12 — {sweep[12]['gate_fail']} failures of "
      f"{sweep[12]['n']} curves")
print(f"\n{'vmax':>5s} {'n':>5s} {'ts(g1)':>8s} {'ts(g2)':>8s} {'gap_ts':>8s} "
      f"{'gap_ols':>8s} {'rh_worst':>9s}")
for vm in VMAXES:
    s = sweep[vm]
    print(f"{vm:>5d} {s['n']:>5d} {s['ts_by_genus']['1']:>8.4f} "
          f"{s['ts_by_genus']['2']:>8.4f} {s['gap_ts']:>8.4f} "
          f"{s['gap_ols']:>8.4f} {s['rh_worst']:>9.4f}")
print(f"\n  gap_ts trend: " + " -> ".join(f"{x:.4f}" for x in seq)
      + ("  (monotone decreasing)" if inv == 0 else f"  ({inv} increase(s))"))
print()
for b, v, f in ((P1, mismatch, "{:.0f}"), (P2, sweep[12]["gate_fail"], "{:.0f}"),
                (E1, d_gap, "{:.4f}"), (E2, inv, "{:.0f}"),
                (E3, sweep[12]["gap_ts"], "{:.4f}"),
                (E4, sweep[12]["rh_worst"], "{:.4f}")):
    print("  " + b.line(v, f))

v = compose([Arm.from_bar(p1, PREM_ROLE,
                          claim="same battery as the banked cell"),
             Arm.from_bar(p2, PREM_ROLE,
                          claim="the recurrence is still correct at v = 12"),
             Arm.from_bar(e1, EX_ROLE,
                          claim="the fit window moves the genus gap"),
             Arm.from_bar(e2, MECH_ROLE,
                          claim="and it moves it downward, monotonically"),
             Arm.from_bar(e3, RES_ROLE,
                          claim="the gap closes below the bar the short window "
                                "missed, so the exponent is genus-independent"),
             Arm.from_bar(e4, RES_ROLE,
                          claim="and both genera sit on the RH slope")],
            holds="GENUS_GAP_WAS_WINDOW_AND_ESTIMATOR",
            fails="GENUS_GAP_SURVIVES_A_LONGER_WINDOW")
print(f"\nVERDICT: {v['citation']}")

json.dump(dict(
    primes=PRIMES, vmaxes=VMAXES, sweep={str(k): v_ for k, v_ in sweep.items()},
    banked_vmax6={"gap_ols": bank["gap_ols"], "gap_ts": bank["gap_theil_sen"],
                  "asymmetry": bank["asymmetry"], "rh_worst": bank["rh_worst"],
                  "rho": bank["rho_gap_vs_dip"], "n": bank["n"]},
    p1_mismatches=mismatch, gate_failures_vmax12=sweep[12]["gate_fail"],
    gap_ts_trend=seq, delta_gap=d_gap,
    bars={s["name"]: s for s in (p1, p2, e1, e2, e3, e4)},
    instrument=INSTRUMENT.seal(),
    executes="the test queued verbatim by F_genus_exponent's amendment 1",
    verdict=v["head"], composed=v),
    open(os.path.join(HERE, "F_window_exponent.json"), "w"), indent=1)
print("\nwrote F_window_exponent.json")
