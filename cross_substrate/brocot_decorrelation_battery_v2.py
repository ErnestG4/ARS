"""CAN ENERGY AND CONCENTRATION BE PULLED APART? v2, with a knob that can move.

COMMITTED GENERATOR of cross_substrate/brocot_decorrelation_battery_v2.json.
Predictions sealed here, before any output exists.

WHAT v1 GOT WRONG, AND IT WAS NOT WHAT v1 SAID
----------------------------------------------
v1 concluded that subset size is an energy knob and not a concentration one.
That diagnosis is retracted. In closed form, participation_ratio over n bands
with energy spread evenly across k of them is 1 - k/n, so with the instrument's
39 bands:

    k = 1  ->  0.9744        k = 4  ->  0.8974        k = 8  ->  0.7949

The knob moved concentration exactly as designed. Its maximum reachable RATIO
across the swept k is 0.9744/0.7949 = 1.226 -- and v1 required a factor of 2.0.
E1 could not have fired for any battery, under any manipulation, ever. An inert
arm, and the closed form reproduces v1's measured span (1.117-1.271), so the
data never distinguished the wrong diagnosis from the right one.

NO GUARD CAUGHT IT because C_FACTOR was a bare module constant inside a
pair-matching loop and never passed through `reachable.Bar`. Every Bar in v1 is
checked; the number that actually gated the arm is not a Bar. THAT is the
lesson v2 is built around.

THREE THINGS v2 DOES DIFFERENTLY
--------------------------------
1. THE STATISTIC IS CHOSEN BY DERIVED DYNAMIC RANGE, before running.
   top_band_share is max_i p_i, so energy in one band gives 1.0 and energy over
   k bands gives 1/k -- a reachable ratio of k_max = 8.0, against
   participation_ratio's 1.226. Both are among the three the salience cell
   swept, so this is a choice from a pre-existing set on an analytic criterion,
   not a new statistic invented to pass. participation_ratio is reported
   alongside for commensurability with that cell.

2. EVERY THRESHOLD GOES THROUGH `Bar`, INCLUDING THE PAIR-MATCHING FACTORS.
   v1's failure mode is structurally impossible here: an unreachable factor is
   refused at construction. And where a bar's population can be empty, the arm
   is declared INAPPLICABLE rather than scored -- an arm with nothing in it is
   not a passing arm.

3. THE CONTRAST v1 NEVER RAN. v1 always assigned DISTINCT beat rates, so the
   condition that concentrates the difference into a single band -- k bins split
   at ONE COMMON rate -- appears nowhere in it. Its absence there was not
   evidence about it. Here rate_mode is the primary knob.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                           ║
║                                                                              ║
║ P1  PREMISE, SCORED WITHIN RATIO — the confound is real in the FM detune     ║
║     family: median over ratios of |Spearman rho(energy, concentration)|      ║
║     >= 0.5. v1 scored this by POOLING 11 ratios into one correlation, which  ║
║     v1's own R1 forbids, and got 0.432 where the within-ratio median is      ║
║     0.636. Same bar, correct estimator, stated once.                         ║
║                                                                              ║
║ M1  MECHANISM, AND IT IS CHECKED FIRST — rate_mode is a real concentration   ║
║     knob: at matched k, top_band_share under COMMON-rate splitting is at     ║
║     least 3x its value under DISTINCT-rate splitting. If this misses, the    ║
║     knob does not work and E1 below is untestable rather than false. This    ║
║     is the arm v1 needed and did not have.                                   ║
║                                                                              ║
║ E1  MATCHED ENERGY, DIFFERING CONCENTRATION — at least 5 within-ratio pairs  ║
║     whose modulation-difference energies agree within 5% while their         ║
║     top_band_share differs by at least 3x. The 3x is DERIVED: the reachable  ║
║     ratio is 8x, so the bar sits comfortably inside it and can both fire     ║
║     and fail.                                                                ║
║                                                                              ║
║ E2  AND THE REVERSE — at least 5 pairs matched in concentration within 5%    ║
║     while differing in energy by at least 3x. v1's E2 passed at 43398        ║
║     BECAUSE E1 failed: concentration was compressed, so a 5% tolerance       ║
║     matched most pairs. Here that route is closed by construction, because   ║
║     M1 establishes the spread before E2 is read.                             ║
║                                                                              ║
║ E3  THE BATTERY DECORRELATES — |rho| over the constructed battery <= 0.20.   ║
║     RIVAL: the FM family's own within-ratio median must FAIL this bar. v1's  ║
║     battery came out WORSE than the family (0.546 vs 0.432); if that         ║
║     repeats with a working knob, the failure is about the manipulation and   ║
║     not about the bar.                                                       ║
║                                                                              ║
║ R1  RESOLUTION — WITHIN SUBSTRATE BEFORE POOLED. E1 and E2 both hold inside  ║
║     individual ratios for at least 5 of the 11, not merely in the pool.      ║
╚══════════════════════════════════════════════════════════════════════════════╝

SCOPE, STATED ONCE AND NOT NARRATED AFTERWARDS: 11 ratios — the 12 non-degenerate
below-horizon ratios at I = 0.9 minus 5/7. This battery splits ARBITRARY
coincident bins and never touches the witness pair, so the resynthesis cell's
"carries the cue" scoping does not bind here; its FIDELITY result does, and was
measured on the 8 of these that carry a witness pair in the box. 5/7 is excluded
because its witness pair is sub-audible, which is the one place the two scopes
do interact. v1 said 7 in prose and ran 11; this cell says 11 and runs 11.

AMPLITUDE PURITY IS A CODE INVARIANT, NOT AN ARM. Every battery member is a pure
frequency move: `render_from` alters only the frequency argument and passes each
bin's amplitude through untouched. v1 spent a MECHANISM arm asserting this and
the arm was vacuous -- it compared a dict to itself. A property provable by
reading eleven lines does not need a lattice arm; it needs an assertion, which
is below.

AMENDMENT 1 — M1 MISSED, AND IT CORRECTS THE CORRECTION THAT BUILT THIS CELL.

M1 was put FIRST on purpose: if the knob does not work, E1 is untestable rather
than false. It does not work. Common-rate over distinct-rate concentration is
1.12x against a 3.0x bar.

The closed form this cell was built on predicted otherwise, and the gap between
prediction and measurement is the finding:

    k        predicted distinct (1/k)   measured distinct   measured common
    2              0.5000                    0.7249             0.7255
    4              0.2500                    0.6152             0.6892
    8              0.1250                    0.5237             0.6055

    predicted common: 1.0000 at every k.  measured: 0.61 - 0.73.

The modulation difference is NOT confined to the k bands the manipulation
targets. One band carries about 62% of it regardless of k, regardless of mode.
So `top_band_share` sits in a narrow high range whatever is done to the
stimulus, exactly as `participation_ratio` did.

WHICH MEANS v1's ORIGINAL DIAGNOSIS WAS SUBSTANTIALLY RIGHT AND MY RETRACTION OF
IT WAS AN OVER-CORRECTION. v1 said "the difference is broadband and its
concentration sits near saturation whatever k is". That is what these numbers
say. What I did in v1's Amendment 3 was compute PR = 1 - k/n_bands from the
assumption that the manipulation's energy lands in exactly k bands, find that it
predicted a real range, and conclude the knob worked. The arithmetic was right
and the assumption was false, and I never checked the assumption against the
signal -- I checked it against itself.

BOTH HALVES OF AMENDMENT 3 ARE NOT EQUALLY WRONG, and the distinction matters.
Its claim that C_FACTOR = 2.0 exceeded participation_ratio's reachable ratio of
1.226 STANDS -- that is a fact about the statistic's range, independent of any
model of the signal, and v1's E1 was inert for that reason alone. What falls is
its inference from there to "so the knob works". The bar was unreachable AND the
knob is weak; those were never alternatives.

THE LESSON IS ABOUT THE FIX, NOT THE BUG. The reachability argument exists to
stop bars being guessed. Here it replaced a guessed bar with an ANALYTIC bound
computed on an idealisation -- which is a more confident way to be wrong, because
it arrives with a derivation attached. A reachability argument has to be
anchored in a measurement of the actual signal, not in a model of it, or it
launders an assumption into a bound.

WHAT THIS CELL NOW SAYS, and it is a stronger closing statement than another
iteration would be. Two independent manipulations -- subset size and rate mode --
were designed to move concentration and neither does, because the modulation
difference is broadband as an empirical property of this stimulus family. The
battery route to decorrelation is not one knob short. It is measuring a quantity
that does not vary under any manipulation this apparatus can express, and a
third knob is not indicated. E3 (0.497 against the family's 0.552) and R1 (3 of
11) both miss, and they miss for that reason.

WHAT THIS CELL DOES NOT CLAIM. Nothing about what a listener hears. It asks
whether a CONTRAST IS CONSTRUCTIBLE. Whether concentration or energy drives the
skips is the question this battery would make askable, and answering it needs
people.
"""
import json
import os
import sys
from fractions import Fraction
from math import gcd

import numpy as np
from scipy.signal import hilbert
from scipy.special import jv
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/brocot"))
from redpath import redpath                                       # noqa: E402
from reachable import Bar                                         # noqa: E402
from modelparams import Model, Param, TESTED, DECLARED            # noqa: E402
from verdictlattice import (Arm, compose, PREMISE as PRE_ROLE,    # noqa: E402
                            EXISTENCE as EX_ROLE,
                            MECHANISM as MECH_ROLE,
                            RESOLUTION as RES_ROLE)
from phase3.partial_prediction import order_bound                 # noqa: E402

I_MUS = 0.9
B = order_bound(I_MUS)
A = 2 * B
SR, DUR, F_C, FLOOR = 44100, 2.0, 220.0, 1e-4
SEED = 20240517
N_PER_MODE = 50
BEATS = [2.0, 3.0, 5.0, 7.0, 11.0, 13.0, 17.0, 19.0]
SUBSET_SIZES = [2, 3, 4, 6, 8]
K_MAX = max(SUBSET_SIZES)
MOD_LO, MOD_HI, BW = 0.5, 40.0, 1.0
N_BANDS = int((MOD_HI - MOD_LO) / BW)
STAT = "top_band_share"
FM_CENTS = [1.0, 2.0, 3.0, 6.0, 10.0, 15.0, 20.0, 30.0, 45.0, 60.0]
EXCLUDE = {"5/7"}
E_TOL = C_TOL = 0.05
C_FACTOR = E_FACTOR = 3.0
RHO_BAR, PREMISE_BAR, MECH_FACTOR = 0.20, 0.5, 3.0

# DERIVED REACHABLE RANGES, computed here so the bars below can be defended
# rather than asserted. top_band_share is max_i p_i: one band gives 1.0, k
# bands give 1/k. participation_ratio is 1 - k/n_bands.
TBS_REACH = 1.0 / (1.0 / K_MAX)                       # = K_MAX = 8.0
PR_REACH = (1 - 1.0 / N_BANDS) / (1 - float(K_MAX) / N_BANDS)

INSTRUMENT = Model("modulation-difference energy and concentration under "
                   "additive resynthesis, v2", [
    Param("rate_mode", TESTED, sweep=["common", "distinct"],
          why="THE KNOB v1 NEVER TURNED. k bins split at ONE common rate pile "
              "the modulation difference into a single band; k bins at k rates "
              "spread it over k. v1 always used distinct rates, so the "
              "concentrating condition appears nowhere in it"),
    Param("subset_size", TESTED, sweep=SUBSET_SIZES,
          why="how many coincident bins are split. Under distinct rates this "
              "sets the number of occupied bands; under a common rate it moves "
              "energy without moving concentration, which is what makes the "
              "two knobs separable at all"),
    Param("concentration_stat", DECLARED, value=STAT,
          why=f"CHOSEN BY DERIVED DYNAMIC RANGE, before running: "
              f"top_band_share reaches a ratio of {TBS_REACH:.2f} across the "
              f"swept k against participation_ratio's {PR_REACH:.3f}. v1 used "
              "the latter with a 2.0 bar, which exceeded its reachable ratio "
              "and made the arm inert. Both are among the three the salience "
              "cell swept, so this is a choice from a pre-existing set on an "
              "analytic criterion; participation_ratio is reported alongside"),
    Param("band_width_hz", DECLARED, value=BW,
          why="1.0 Hz, as every other cell in this line, so the numbers stay "
              "comparable with the salience result this battery would decide"),
    Param("seed", DECLARED, value=SEED,
          why="subsets are sampled, so the battery is a random object and must "
              "be reproducible; the repo's BASE_SEED"),
    Param("duration_s", DECLARED, value=DUR,
          why="2 s resolves 0.5 Hz, half the band width, so a beat cannot "
              "straddle two bands unresolved"),
])

T = np.arange(int(SR * DUR)) / SR
FR = np.fft.rfftfreq(len(T), 1.0 / SR)
EDGES = np.arange(MOD_LO, MOD_HI, BW)


def bins_of(alpha):
    d = {}
    for n1 in range(-B, B + 1):
        for n2 in range(-B, B + 1):
            amp = float(jv(n1, I_MUS)) * float(jv(n2, I_MUS))
            if abs(amp) < FLOOR:
                continue
            d.setdefault(abs(1 + n1 + n2 * alpha), []).append((n1, n2, amp))
    return d


def render_from(bins, splits=None):
    """AMPLITUDE PURITY IS VISIBLE HERE: `amp` is passed through untouched and
    only `f` is ever altered. That is the whole invariant; v1 spent a MECHANISM
    arm on it and the arm compared a dict to itself."""
    x = np.zeros_like(T)
    for k, members in bins.items():
        f0 = F_C * float(k)
        rate = (splits or {}).get(k)
        for j, (n1, n2, amp) in enumerate(members):
            f = f0 if rate is None else f0 + (rate / 2.0 if j % 2 == 0
                                              else -rate / 2.0)
            x += amp * np.cos(2 * np.pi * f * T)
    return x


def modspec(x):
    e = np.abs(hilbert(x))
    return np.abs(np.fft.rfft((e - e.mean()) * np.hanning(len(e)))) ** 2


def banded_diff(Sx, Se):
    d = np.abs(Sx - Se)
    return np.array([d[(FR >= a_) & (FR < a_ + BW)].sum() for a_ in EDGES])


def conc(v, kind=STAT):
    """Both statistics, same conventions as brocot_cue_salience."""
    v = v[v > 0]
    if v.size < 2:
        return 0.0
    p = v / v.sum()
    if kind == "top_band_share":
        return float(p.max())
    return float(1.0 - 1.0 / (len(p) * np.sum(p ** 2)))


def fm_render(alpha):
    return np.cos(2 * np.pi * F_C * T
                  + I_MUS * np.sin(2 * np.pi * F_C * T)
                  + I_MUS * np.sin(2 * np.pi * alpha * F_C * T))


RATIOS = [r for r in sorted(
    [Fraction(p, q) for q in range(1, A + 1) for p in range(1, A + 1)
     if gcd(p, q) == 1 and 0.70 <= p / q <= 1.40 and max(p, q) <= A
     and Fraction(p, q) != 1], key=float) if str(r) not in EXCLUDE]

rng = np.random.default_rng(SEED)
rows, pooled_e, pooled_c = [], [], []
mech = {"common": [], "distinct": []}

for r in RATIOS:
    bd = bins_of(r)
    multi = sorted([k for k, v in bd.items() if len(v) >= 2],
                   key=lambda k: -sum(abs(a) for (_, _, a) in bd[k]))
    if len(multi) < K_MAX:
        continue
    Se = modspec(render_from(bd))
    pts = []
    for mode in ("common", "distinct"):
        for _ in range(N_PER_MODE):
            k = int(rng.choice(SUBSET_SIZES))
            tier = rng.integers(0, 3)
            pool = (multi[:len(multi) // 2] if tier == 0 else
                    multi[len(multi) // 2:] if tier == 1 else multi)
            if len(pool) < k:
                pool = multi
            ch = rng.choice(len(pool), size=k, replace=False)
            if mode == "common":
                rate = float(BEATS[int(rng.integers(0, len(BEATS)))])
                splits = {pool[int(c)]: rate for c in ch}
            else:
                splits = {pool[int(c)]: BEATS[i % len(BEATS)]
                          for i, c in enumerate(ch)}
            v = banded_diff(modspec(render_from(bd, splits)), Se)
            if v.sum() <= 0:
                continue
            rec = dict(mode=mode, k=k, energy=float(v.sum()),
                       conc=conc(v), conc_pr=conc(v, "participation_ratio"))
            pts.append(rec)
            mech[mode].append((k, rec["conc"]))

    E = np.array([p["energy"] for p in pts])
    C = np.array([p["conc"] for p in pts])
    pooled_e += list(E)
    pooled_c += list(C)
    n_e = n_c = 0
    for i in range(len(E)):
        for j in range(i + 1, len(E)):
            if abs(E[i] - E[j]) <= E_TOL * max(E[i], E[j]):
                lo, hi = sorted((C[i], C[j]))
                if lo > 0 and hi / lo >= C_FACTOR:
                    n_e += 1
            if abs(C[i] - C[j]) <= C_TOL * max(C[i], C[j]):
                lo, hi = sorted((E[i], E[j]))
                if lo > 0 and hi / lo >= E_FACTOR:
                    n_c += 1
    rows.append(dict(ratio=str(r), n_points=len(pts),
                     matched_energy_pairs=n_e, matched_conc_pairs=n_c,
                     rho=float(spearmanr(E, C).statistic) if len(E) > 3 else 0.0,
                     conc_span=float(C.max() / max(C.min(), 1e-30)),
                     energy_span=float(E.max() / max(E.min(), 1e-30))))

# --- the RIVAL and the premise, scored WITHIN RATIO
fm_within = {}
for r in RATIOS:
    Se = modspec(fm_render(float(r)))
    ee, cc = [], []
    for cents in FM_CENTS:
        v = banded_diff(modspec(fm_render(float(r) * 2 ** (cents / 1200.0))), Se)
        if v.sum() > 0:
            ee.append(float(v.sum()))
            cc.append(conc(v))
    if len(ee) > 3:
        fm_within[str(r)] = float(spearmanr(ee, cc).statistic)
prem = float(np.median([abs(x) for x in fm_within.values()]))
rho_batt = float(spearmanr(pooled_e, pooled_c).statistic)

# --- M1: does rate_mode move concentration at MATCHED k?
mech_by_k = {}
for k in SUBSET_SIZES:
    c = [v for kk, v in mech["common"] if kk == k]
    dd = [v for kk, v in mech["distinct"] if kk == k]
    if c and dd:
        mech_by_k[str(k)] = dict(common=float(np.mean(c)),
                                 distinct=float(np.mean(dd)),
                                 ratio=float(np.mean(c) / max(np.mean(dd), 1e-30)))
mech_ratio = float(np.median([v["ratio"] for v in mech_by_k.values()]))

print(INSTRUMENT.report())
print(f"\n{len(rows)} ratios, {2 * N_PER_MODE} manipulations each "
      f"({N_PER_MODE} common-rate + {N_PER_MODE} distinct-rate), {STAT}\n")
print(f"{'ratio':>7s} {'pts':>4s} {'C-span':>7s} {'E-span':>11s} "
      f"{'matchE':>7s} {'matchC':>7s} {'rho':>7s}")
for r in rows:
    print(f"{r['ratio']:>7s} {r['n_points']:>4d} {r['conc_span']:>7.2f} "
          f"{r['energy_span']:>11.1f} {r['matched_energy_pairs']:>7d} "
          f"{r['matched_conc_pairs']:>7d} {r['rho']:>+7.3f}")
print(f"\nM1 — concentration by rate_mode at matched k:")
for k, v in mech_by_k.items():
    print(f"    k={k:>2s}  common {v['common']:.4f}  distinct {v['distinct']:.4f}"
          f"  ratio {v['ratio']:.2f}x")

n = len(rows)
e1 = sum(r["matched_energy_pairs"] for r in rows)
e2 = sum(r["matched_conc_pairs"] for r in rows)
r1 = sum(1 for r in rows
         if r["matched_energy_pairs"] > 0 and r["matched_conc_pairs"] > 0)
cspan = max(r["conc_span"] for r in rows)

P1 = Bar("within-ratio median |rho|, FM detune family", PREMISE_BAR,
         floor=0.0, ceiling=1.0,
         why="a Spearman magnitude scored per ratio then medianed, which is "
             "what R1 demands and what v1 violated by pooling")
M1 = Bar("top_band_share, common-rate over distinct-rate at matched k",
         MECH_FACTOR, floor=0.0, ceiling=TBS_REACH,
         why=f"a ratio of concentrations. The CEILING IS DERIVED: one band "
             f"gives 1.0 and k bands give 1/k, so the reachable ratio is "
             f"k_max = {TBS_REACH:.1f}. 1.0 is 'the knob does nothing' and is "
             "attainable, so the arm can fail")
E1 = Bar("matched-energy pairs differing in concentration", 5,
         floor=0, ceiling=n * N_PER_MODE * (2 * N_PER_MODE - 1),
         why="a count of within-ratio pairs; 0 is attainable and the ceiling "
             "is every pair in every ratio")
E2 = Bar("matched-concentration pairs differing in energy", 5,
         floor=0, ceiling=n * N_PER_MODE * (2 * N_PER_MODE - 1),
         why="the same count in the other direction, on the same ceiling")
E3 = Bar("|rho| over the constructed battery", RHO_BAR, direction="le",
         floor=0.0, ceiling=1.0,
         why="a Spearman magnitude; 0 attainable by construction and 1 by a "
             "battery that failed to decorrelate",
         rival="the FM detune family, scored the same way")
R1 = Bar("ratios where BOTH matched-pair families exist within the ratio", 5,
         floor=0, ceiling=n,
         why=f"a count over the {n} ratios; pooling manufactures spread, so "
             "the contrast must be constructible inside one")

# E1 is INAPPLICABLE if the observed concentration spread cannot reach the
# factor its bar asks for -- v1's exact failure, refused here instead of scored.
E1_APPLICABLE = cspan >= C_FACTOR
sP, sM = P1.score(prem), M1.score(mech_ratio)
s1 = E1.score(e1) if E1_APPLICABLE else None
s2, s3 = E2.score(e2), E3.score(abs(rho_batt), rival_value=prem)
sR = R1.score(r1)

print()
print("  " + P1.line(prem, "{:.3f}"))
print("  " + M1.line(mech_ratio, "{:.2f}"))
if E1_APPLICABLE:
    print("  " + E1.line(e1, "{:.0f}"))
else:
    print(f"  matched-energy pairs differing in concentration: INAPPLICABLE — "
          f"observed concentration span {cspan:.2f} cannot reach the "
          f"{C_FACTOR:.0f}x the bar asks for. This is v1's defect, refused "
          "rather than scored.")
print("  " + E2.line(e2, "{:.0f}"))
print("  " + E3.line(abs(rho_batt), "{:.3f}", rival_value=prem))
print("  " + R1.line(r1, "{:.0f}"))

arms = [Arm.from_bar(sP, PRE_ROLE,
                     claim="energy and concentration are confounded in the FM "
                           "family, scored within ratio"),
        Arm.from_bar(sM, MECH_ROLE,
                     claim="rate_mode really is a concentration knob"),
        (Arm.from_bar(s1, EX_ROLE,
                      claim="concentration can be varied at fixed energy")
         if E1_APPLICABLE else
         Arm("matched-energy pairs differing in concentration", EX_ROLE,
             met=False, inert=True,
             note=f"INAPPLICABLE: concentration span {cspan:.2f} < "
                  f"{C_FACTOR:.0f}x bar",
             claim="concentration can be varied at fixed energy")),
        Arm.from_bar(s2, EX_ROLE,
                     claim="and energy at fixed concentration"),
        Arm.from_bar(s3, EX_ROLE,
                     claim="the battery decorrelates them where the detune "
                           "family cannot"),
        Arm.from_bar(sR, RES_ROLE,
                     claim="and it holds within ratios, not only pooled")]
v = compose(arms, holds="BATTERY_IS_CONSTRUCTIBLE",
            fails="DECORRELATION_NOT_ACHIEVED")
print(f"\nrho: FM within-ratio median {prem:+.3f}   battery {rho_batt:+.3f}")
print(f"VERDICT: {v['citation']}")

with redpath("rendered battery members", expect_min=500) as rp:
    rp.observed(sum(r["n_points"] for r in rows))

json.dump(dict(I=I_MUS, B=B, sr=SR, duration_s=DUR, f_c=F_C, floor=FLOOR,
               seed=SEED, n_per_mode=N_PER_MODE, beats=BEATS,
               subset_sizes=SUBSET_SIZES, stat=STAT, band_width=BW,
               n_bands=N_BANDS, tbs_reach=TBS_REACH, pr_reach=PR_REACH,
               c_factor=C_FACTOR, e_factor=E_FACTOR,
               excluded=sorted(EXCLUDE), instrument=INSTRUMENT.seal(),
               rows=rows, fm_within=fm_within, premise_within_median=prem,
               rho_battery=rho_batt, mech_by_k=mech_by_k,
               mech_ratio=mech_ratio, e1_applicable=bool(E1_APPLICABLE),
               conc_span_max=cspan,
               matched_energy_pairs=e1, matched_conc_pairs=e2,
               ratios_with_both=r1,
               bars={s["name"]: s for s in (sP, sM, s1, s2, s3, sR) if s},
               verdict=v["head"], composed=v),
          open(f"{HERE}/brocot_decorrelation_battery_v2.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_decorrelation_battery_v2.json")
