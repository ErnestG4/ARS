"""IS THE DECAY EXPONENT GENUS-DEPENDENT, OR IS MY ESTIMATOR? Resolving F_reproduce's caveat.

COMMITTED GENERATOR of approximability/F_genus_exponent.json.
Predictions sealed here, before any output exists.

THE CAVEAT THIS DISCHARGES
--------------------------
`F_reproduce` measured the decay exponent of |N_n/p^n - 1| against the RH-
predicted 0.5*log10(p) and got 1.0008 at genus 1 and 1.1147 at genus 2 -- a gap
of 0.114 against a 0.05 bar, on a claim (MORNING_F) that the exponent is
genus-INDEPENDENT, genus entering only through the 2g prefactor.

It refused to call that a refutation, and the refusal was not politeness. Its
estimator is an ordinary least-squares fit of log10|N_n/p^n - 1| against n. When
that quantity dips near zero at some n the log dives, the point becomes a large
negative outlier, and the fitted slope STEEPENS -- biasing the ratio UP. Genus 2
has four Frobenius eigenvalues rather than two, so near-cancellation is far more
frequent there, which is also why its sd was 3.6x the genus-1 sd. A
genus-dependent BIAS and a genus-dependent EXPONENT predict the same sign of
miss, and that cell could not separate them.

This one separates them, by measuring the same curves two ways.

    OLS         the F_reproduce estimator, reproduced here unchanged
    THEIL-SEN   median of pairwise slopes -- a single outlying point cannot
                move a median of pairs the way it moves a least-squares fit

If the gap is my estimator, it shrinks under Theil-Sen and shrinks MORE at genus
2. If the gap is real arithmetic, it survives both estimators and MORNING_F's
genus-independence claim is wrong.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                           ║
║                                                                              ║
║ P1  PREMISE — the two estimators actually disagree, so the comparison has    ║
║     content: median |OLS - TheilSen| over all curves is > 0.01. If they      ║
║     agree everywhere, robustness was never the issue and E1/E2 below are     ║
║     answering a question that does not arise.                                ║
║                                                                              ║
║ E1  THE BIAS IS GENUS-ASYMMETRIC — the estimator gap |OLS - TheilSen| is at  ║
║     least 2x larger at genus 2 than at genus 1. This is the arm that says    ║
║     my diagnosis was right about the MECHANISM, and it is the one I most     ║
║     expect to be wrong about, because "more eigenvalues, more cancellation"  ║
║     is a story I told after seeing the sd.                                   ║
║                                                                              ║
║ E2  AND IT EXPLAINS THE GAP — under Theil-Sen the genus gap falls to <=      ║
║     0.05, the bar F_reproduce's M1 missed at 0.114. If it does, the          ║
║     genus-independence claim SURVIVES and F_reproduce's miss was mine.       ║
║                                                                              ║
║ E3  AND THE EXPONENT IS THE RH ONE — the Theil-Sen ratio is within 0.05 of   ║
║     1.0 in BOTH genera, i.e. |N_n/p^n - 1| really does decay like            ║
║     p^(-n/2). This is what makes E2 a result rather than two wrong numbers   ║
║     agreeing.                                                                ║
║                                                                              ║
║ M1  MECHANISM — the outliers are where I say they are. Curves whose OLS and  ║
║     Theil-Sen slopes differ most are curves that HAVE a near-zero dip:       ║
║     Spearman rho between |OLS - TheilSen| and the smallest observed          ║
║     |N_n/p^n - 1| is negative, at least 0.3 in magnitude. If the             ║
║     disagreement is unrelated to dips, my account of it is wrong even if     ║
║     E1 and E2 pass.                                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

SAME BATTERY, DELIBERATELY. Identical primes and families to F_reproduce, so the
two cells differ in exactly one thing: the estimator. Changing the family at the
same time would confound the comparison this cell exists to make.

WHAT THIS CELL DOES NOT CLAIM. Nothing about Session F's banked 0.9583, which
came from a family that was never stated and cannot be recovered. This is about
whether the EXPONENT is genus-dependent, which is a claim about all curves.
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
from redpath import redpath                                       # noqa: E402
from reachable import Bar                                         # noqa: E402
from modelparams import Model, Param, TESTED, DECLARED            # noqa: E402
from verdictlattice import (Arm, compose, PREMISE as PRE_ROLE,    # noqa: E402
                            EXISTENCE as EX_ROLE,
                            MECHANISM as MECH_ROLE)
from ff_curve import g1_Nv, g2_Nv                                 # noqa: E402

# NOT `from F_reproduce import ...`: that module does its work at import time,
# so importing it would re-run the whole battery, reprint its output and
# REWRITE its banked artifact as a side effect of loading a constant. The
# battery must still be identical, so the constants are declared here and then
# ASSERTED against what F_reproduce actually banked -- which is a stronger tie
# than an import anyway, because it compares against the recorded run rather
# than against code that might since have changed.
PRIMES = [7, 11, 13, 17, 19, 23, 29]
G1_AB = [(a, b) for a in range(1, 4) for b in range(1, 4)]
G2_C = [(c3, c1, c0) for c3 in range(3) for c1 in range(3) for c0 in range(3)]
VMAX = 6

_prev = json.load(open(os.path.join(HERE, "F_reproduce.json")))
assert _prev["primes"] == PRIMES and _prev["vmax"] == VMAX, (
    "battery drift: this cell exists to isolate the ESTIMATOR, so the primes "
    f"and vmax must match F_reproduce's banked run exactly "
    f"({_prev['primes']}, vmax={_prev['vmax']})")


def poly_gcd_deg(f, p):
    """Degree of gcd(f, f') over F_p; 0 means squarefree. Same routine
    F_reproduce uses to keep singular curves out of the battery."""
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

GAP_BAR, RH_BAR, ASYM_BAR, PREMISE_BAR, DIP_BAR = 0.05, 0.05, 2.0, 0.01, 0.3

INSTRUMENT = Model("two slope estimators on one curve battery", [
    Param("estimator", TESTED, sweep=["ols", "theil_sen"],
          why="THE ONLY THING THAT VARIES. The battery, primes and families are "
              "identical to F_reproduce so the comparison isolates the "
              "estimator; changing the family too would confound it"),
    Param("vmax", DECLARED, value=VMAX,
          why="extension degrees 1..6, as F_reproduce, so the fitted points "
              "are the same points"),
    Param("dip_bar", DECLARED, value=DIP_BAR,
          why="M1's correlation magnitude. 0.3 is a modest association; the "
              "claim is that dips explain the disagreement's LOCATION, not "
              "that they explain all of its size"),
])


def slopes(res):
    """OLS and Theil-Sen slope of log10|N_n/p^n - 1| vs n, plus the deepest dip."""
    p = res["p"]
    n, y = [], []
    for v, Nv in enumerate(res["Nv"][:VMAX], start=1):
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


rows = []
for p in PRIMES:
    for (a, b) in G1_AB:
        try:
            r = slopes(g1_Nv(a, b, p, vmax=VMAX))
        except AssertionError:
            continue
        if r:
            rows.append(dict(genus=1, p=p, **r))
    for (c3, c1, c0) in G2_C:
        fc = [c0, c1, 0, c3, 0, 1]
        if poly_gcd_deg(fc, p) != 0:
            continue
        try:
            r = slopes(g2_Nv(fc, p, vmax=VMAX))
        except Exception:
            continue
        if r:
            rows.append(dict(genus=2, p=p, **r))

for r in rows:
    r["est_gap"] = abs(r["ols"] - r["ts"])
g = {k: [r for r in rows if r["genus"] == k] for k in (1, 2)}
mean = lambda v, k: float(np.mean([r[k] for r in v]))                  # noqa: E731

premise = float(np.median([r["est_gap"] for r in rows]))
asym = mean(g[2], "est_gap") / max(mean(g[1], "est_gap"), 1e-12)
gap_ts = abs(mean(g[1], "ts") - mean(g[2], "ts"))
gap_ols = abs(mean(g[1], "ols") - mean(g[2], "ols"))
rh_worst = max(abs(mean(g[1], "ts") - 1.0), abs(mean(g[2], "ts") - 1.0))
rho_dip = float(spearmanr([r["est_gap"] for r in rows],
                          [r["deepest_dip"] for r in rows]).statistic)

print(INSTRUMENT.report())
print(f"\n{len(rows)} curves ({len(g[1])} genus-1, {len(g[2])} genus-2), "
      f"same battery as F_reproduce\n")
print(f"{'genus':>6s} {'n':>5s} {'OLS':>9s} {'TheilSen':>10s} {'est gap':>9s}")
for k in (1, 2):
    print(f"{k:>6d} {len(g[k]):>5d} {mean(g[k], 'ols'):>9.4f} "
          f"{mean(g[k], 'ts'):>10.4f} {mean(g[k], 'est_gap'):>9.4f}")
print(f"\n  genus gap under OLS       {gap_ols:.4f}   (F_reproduce's M1 miss)")
print(f"  genus gap under Theil-Sen {gap_ts:.4f}")
print(f"  estimator asymmetry g2/g1 {asym:.2f}x")
print(f"  rho(est gap, deepest dip) {rho_dip:+.3f}")

P1 = Bar("median |OLS - TheilSen| over all curves", PREMISE_BAR,
         floor=0.0, ceiling=5.0,
         why="a difference of two ratios near 1; 0 is attainable if the "
             "estimators agree and O(1) if they diverge")
E1 = Bar("estimator disagreement, genus-2 over genus-1", ASYM_BAR,
         floor=0.0, ceiling=100.0,
         why="a ratio of mean disagreements; 1 is 'no asymmetry' and is "
             "attainable, and the ceiling is generous")
E2 = Bar("genus gap under Theil-Sen", GAP_BAR, direction="le",
         floor=0.0, ceiling=2.0,
         why="the same bar and scale F_reproduce's M1 used and missed at "
             "0.114, so the two are directly comparable")
E3 = Bar("worst |Theil-Sen ratio - 1| across genera", RH_BAR, direction="le",
         floor=0.0, ceiling=2.0,
         why="distance from the RH-predicted exponent; 0 attainable, and a "
             "wholly different exponent gives O(1)")
M1 = Bar("|rho| between estimator gap and deepest dip", DIP_BAR,
         floor=0.0, ceiling=1.0,
         why="a Spearman magnitude; both ends attainable")

sP, s1 = P1.score(premise), E1.score(asym)
s2, s3 = E2.score(gap_ts), E3.score(rh_worst)
sM = M1.score(abs(rho_dip))
print()
for b, v, f in ((P1, premise, "{:.4f}"), (E1, asym, "{:.2f}"),
                (E2, gap_ts, "{:.4f}"), (E3, rh_worst, "{:.4f}"),
                (M1, abs(rho_dip), "{:.3f}")):
    print("  " + b.line(v, f))

arms = [Arm.from_bar(sP, PRE_ROLE, claim="the estimators disagree at all"),
        Arm.from_bar(s1, EX_ROLE, claim="the bias is genus-asymmetric"),
        Arm.from_bar(s2, EX_ROLE, claim="and it accounts for the genus gap"),
        Arm.from_bar(s3, EX_ROLE, claim="with the exponent landing at the RH "
                                        "value in both genera"),
        Arm.from_bar(sM, MECH_ROLE, claim="because the disagreement sits on "
                                          "curves with near-zero dips")]
v = compose(arms, holds="GAP_WAS_THE_ESTIMATOR_GENUS_INDEPENDENCE_SURVIVES",
            fails="GENUS_GAP_SURVIVES_A_ROBUST_ESTIMATOR")
print(f"\nVERDICT: {v['citation']}")

with redpath("curves measured two ways", expect_min=100) as rp:
    rp.observed(len(rows))

json.dump(dict(primes=PRIMES, vmax=VMAX, n=len(rows),
               instrument=INSTRUMENT.seal(),
               means={str(k): dict(n=len(g[k]), ols=mean(g[k], "ols"),
                                   theil_sen=mean(g[k], "ts"),
                                   est_gap=mean(g[k], "est_gap"),
                                   ols_sd=float(np.std([r["ols"] for r in g[k]],
                                                       ddof=1)),
                                   ts_sd=float(np.std([r["ts"] for r in g[k]],
                                                      ddof=1)))
                      for k in (1, 2)},
               gap_ols=gap_ols, gap_theil_sen=gap_ts, asymmetry=asym,
               rh_worst=rh_worst, rho_gap_vs_dip=rho_dip, rows=rows,
               bars={s["name"]: s for s in (sP, s1, s2, s3, sM)},
               verdict=v["head"], composed=v),
          open(f"{HERE}/F_genus_exponent.json", "w"), indent=1)
print("\nwritten -> approximability/F_genus_exponent.json")
