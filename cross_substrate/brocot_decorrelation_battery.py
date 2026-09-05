"""CAN ENERGY AND CONCENTRATION BE PULLED APART? The battery the detune could not build.

COMMITTED GENERATOR of cross_substrate/brocot_decorrelation_battery.json.
Predictions sealed here, before any output exists.

THE QUESTION THIS INHERITS
--------------------------
`brocot_cue_salience` found the listener's skips tracking the STRUCTURE of the
exact-vs-twin difference at |rho| ~ 0.6, and could not say which structure. Two
live accounts:

    CONCENTRATION   the difference is packed into few modulation bands
    ENERGY          there is simply more difference

In the FM twin family those are not separable, and not for want of trying: one
alpha moves every alpha-dependent partial together, so louder and more-packed
arrive as a single knob. That cell's verdict was amended to
SKIP_STRUCTURE_IS_REAL_MECHANISM_UNRESOLVED for exactly this reason, and the
rival rule and the swing rule were both minted from its wreckage.

`brocot_detune_impossibility` then closed the route formally: no detune of any
magnitude splits a witness pair while returning the rest. [CORRECTED 2026-09-05:
this sentence originally added "and locally the attempt costs 2.4x to 7.4x more
collateral than it buys". RETRACTED -- ruler-dependent in sign, and reversed
under an amplitude-weighted ruler.] The EXACT result is what stands, and it is
enough: the decorrelation cannot be dialled, so it has to be built.

WHAT THE APPARATUS MAKES POSSIBLE
---------------------------------
`brocot_resynthesis_fidelity` established that an additive render IS the FM render
(median error 0.013 of the contrast, B=2 rival failing at 3.30) and that a twin
built by moving partials CARRIES the cue (7/8, with both controls). Under that
apparatus the manipulable object is a COINCIDENT BIN -- two or more index vectors
sharing a frequency -- which can be split at any rate, independently of every
other bin. Each ratio here offers 20 to 28 of them, with summed amplitudes
spanning 1e-3 to 7.3e-1, nearly three decades.

That is the whole trick. Choosing HOW MANY bins to split sets the concentration
of the modulation difference; choosing WHICH bins sets its energy. Two knobs
where the detune had one.

EVERY MEMBER IS A PURE FREQUENCY MOVE. No amplitude is edited anywhere in the
battery -- M1 checks the amplitude multiset is bit-identical to the exact
stimulus. Scaling a partial would have been the easy way to vary energy and it
would have made the battery a different manipulation from the one the arc studies.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                           ║
║                                                                              ║
║ P1  PREMISE — the confound is real in the family it was measured in. Across  ║
║     the FM detune family (a cents sweep), |Spearman rho(energy,              ║
║     concentration)| >= 0.5. If energy and concentration are ALREADY          ║
║     separable by detuning, this battery is unnecessary and the salience      ║
║     cell's problem was not the one I diagnosed.                              ║
║                                                                              ║
║ E1  MATCHED ENERGY, DIFFERING CONCENTRATION — at least 5 stimulus pairs      ║
║     exist whose modulation-difference energies agree within 5% while their   ║
║     concentrations differ by at least 2x.                                    ║
║                                                                              ║
║ E2  AND THE REVERSE — at least 5 pairs whose concentrations agree within 5%  ║
║     while their energies differ by at least 3x. Both directions are needed:  ║
║     one alone confounds "we can vary X" with "we can hold Y".                ║
║                                                                              ║
║ E3  THE BATTERY ACTUALLY DECORRELATES — |Spearman rho| over the whole        ║
║     constructed battery <= 0.20. RIVAL, and the arm is scored against it:    ║
║     the FM detune family must FAIL this same bar. A decorrelation bar the    ║
║     confounded family also clears would be measuring nothing.                ║
║                                                                              ║
║ M1  MECHANISM — every battery member is a pure frequency move. The sorted    ║
║     amplitude multiset of each member is bit-identical to the exact          ║
║     stimulus's. Measured as: zero members differ.                            ║
║                                                                              ║
║ R1  RESOLUTION — WITHIN SUBSTRATE BEFORE POOLED. E1 and E2 must both hold    ║
║     inside individual ratios, not only in the pooled battery, for at least   ║
║     5 of the 7. Pooling across ratios manufactures spread and would let a    ║
║     between-ratio effect masquerade as a constructible contrast.             ║
╚══════════════════════════════════════════════════════════════════════════════╝

SCOPE. The 7 ratios on which the apparatus was validated AND carries the cue.
5/7 is excluded by name, as the fidelity cell scoped it: its witness pair sits at
amplitude ~2e-4 and cannot beat audibly alone. Staying inside validated scope
matters more than the extra row.

INSTRUMENTS ARE TAKEN UNCHANGED. `concentration()` is copied from
brocot_cue_salience byte-for-byte including its participation-ratio convention
(higher = MORE concentrated), and the modulation spectrum is the same Hilbert
envelope readout. The pre-registered statistic is participation_ratio at 1.0 Hz
bands -- the configuration named in advance in that cell, not the one that
happened to score highest, which is the defect the swing rule exists for.

AMENDMENT 1 — THE CELL IS INVALID AT ITS OWN PREMISE, THE BATTERY MADE THINGS
WORSE, AND THE STATED SCOPE WAS NOT THE EXECUTED SCOPE. Three findings, none of
them the one I sealed for.

(1) P1 MISSED: 0.432 against a 0.5 bar, so the lattice returns INVALID and the
four arms below it are UNREAD -- not false, unread. The confound between energy
and concentration in the FM detune family is MODERATE, not the strong thing I
predicted. That matters beyond bookkeeping: the battery's whole justification was
"these cannot be separated by detuning", and at |rho| = 0.43 that premise is
weaker than the argument needed. I do not get to read the rest and I do not get
to keep the parts that passed.

(2) THE BATTERY IS MORE CORRELATED THAN THE FAMILY IT REPLACES: 0.546 against the
FM family's 0.432, both far above the 0.20 bar. And E1 is ZERO at every single
ratio -- not one matched-energy pair with differing concentration, anywhere.

The diagnosis is visible in the table and is a design error, not noise:

    energy span      up to 1.2e11 across the battery
    concentration    span 1.12 to 1.27, i.e. it BARELY MOVES

I assumed subset size was a concentration knob. It is not. Splitting k bins does
not spread the modulation difference across k bands, because the difference is
broadband -- splitting any bin perturbs the envelope's cross-terms everywhere,
not just at that bin's beat rate -- and its concentration sits near saturation
whatever k is. Meanwhile amplitudes span three decades, so subset choice moves
energy enormously. One knob again, pointed at the wrong axis. The battery
reproduced the very defect it was built to remove.

WHAT I NEVER VARIED, AND SHOULD HAVE: every manipulation assigned DISTINCT beat
rates (BEATS[i % len(BEATS)]). The obvious concentration handle is the opposite
contrast -- k bins all split at the SAME rate, piling the difference into ONE
band, against k bins at k rates. That condition does not appear anywhere in this
battery, so its absence is not evidence about it. Registered as its own sealed
cell rather than re-run here: a design changed after seeing the table, and then
run until it goes green, is the thing the seal exists to prevent.

(3) SCOPE MISMATCH, MINE. The docstring above says the battery runs on "the 7
ratios on which the apparatus was validated AND carries the cue". The code
excludes only 5/7 from a 12-ratio enumeration and ran on ELEVEN. The two are not
the same set and I wrote both. There is a real argument for 11 -- this battery
splits arbitrary coincident bins and never touches the witness pair, so
"carries the cue" was never the binding constraint here -- but that argument is
one I am making now, after the fact, and the sealed text says 7. Recorded as a
mismatch rather than resolved in the direction that flatters the run.

AMENDMENT 2 — P1 WAS SCORED BY POOLING, WHICH THIS CELL'S OWN R1 FORBIDS, AND
THE INVALID VERDICT WAS AN ARTIFACT OF THAT. Found by adversarial review, not by
me.

R1 above reads: "WITHIN SUBSTRATE BEFORE POOLED ... Pooling across ratios
manufactures spread and would let a between-ratio effect masquerade as a
constructible contrast." I applied that doctrine to the battery arms and then
scored the PREMISE arm -- the one that killed the run -- on a single Spearman
over all 11 ratios x 10 detunes pooled together.

Scored the way this cell's own methodology demands:

    pooled (what P1 scored)        |rho| = 0.4320   MISSES the 0.5 bar
    within-ratio median            |rho| = 0.6360   MEETS it
    ratios individually clearing 0.5              7 of 11

So the confound between energy and concentration in the FM detune family is
REAL, at the strength the premise asked for, and the INVALID verdict came from
scoring it with the instrument the cell elsewhere refuses.

WHAT THIS CHANGES, AND WHICH DIRECTION. The premise holds, so the four arms below
it become READABLE rather than unread -- and they are the negative. E1 is zero
matched-energy pairs at every ratio; E3 is a battery MORE correlated (0.546) than
the family it replaces (0.432). The corrected reading is therefore
DECORRELATION_NOT_ACHIEVED with its arms read, which is a STRONGER and better
supported negative than INVALID with nothing readable. The correction does not
rescue the battery; it removes the excuse that the battery was never properly
tested.

HOW IT IS RECORDED. The sealed P1 stays in the artifact exactly as scored, and
the corrected within-ratio premise is reported beside it, with `verdict_amended`
carrying the corrected head. Re-scoring an arm after seeing it fail is the move
this repo's seals exist to prevent, so the discipline is: the seal is not
rewritten, the correction is additive and labelled, and the reason it is
legitimate is stated -- the arm violated the cell's OWN stated rule, and an
outside reviewer found it, and the fix makes the result worse for the
hypothesis rather than better.

WHAT THIS CELL DOES NOT CLAIM. Nothing about what any listener hears. It says a
CONTRAST IS CONSTRUCTIBLE. Whether concentration or energy drives the skips is a
question this battery makes askable and does not answer, and answering it needs
people -- which is the first place in this arc where spending a listener is
defensible, because until now the stimulus could not isolate what it claimed to.
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
N_MANIP = 120
BEATS = [2.0, 3.0, 5.0, 7.0, 11.0, 13.0, 17.0, 19.0]
SUBSET_SIZES = [1, 2, 3, 4, 6, 8]
MOD_LO, MOD_HI, BW = 0.5, 40.0, 1.0
STAT = "participation_ratio"
FM_CENTS = [1.0, 2.0, 3.0, 6.0, 10.0, 15.0, 20.0, 30.0, 45.0, 60.0]
EXCLUDE = {"5/7"}
E_TOL, C_TOL = 0.05, 0.05
C_FACTOR, E_FACTOR = 2.0, 3.0
RHO_BAR, PREMISE_BAR = 0.20, 0.5

INSTRUMENT = Model("modulation-difference energy and concentration under "
                   "additive resynthesis", [
    Param("subset_size", TESTED, sweep=SUBSET_SIZES,
          why="how many coincident bins are split. This is the CONCENTRATION "
              "knob -- more bins at more distinct beat rates spreads the "
              "modulation difference across bands"),
    Param("beat_rates_hz", TESTED, sweep=BEATS,
          why="distinct rates so split bins land in different 1.0 Hz bands; "
              "if they coincided, subset size would stop controlling spread"),
    Param("concentration_stat", DECLARED, value=STAT,
          why="the configuration brocot_cue_salience NAMED IN ADVANCE, not the "
              "one that scored highest there -- taking the max is the defect "
              "the swing rule was minted to prevent, and this cell inherits "
              "that cell's question and so inherits its pre-registration"),
    Param("band_width_hz", DECLARED, value=BW,
          why="1.0 Hz, the width every other cell in this line uses; changing "
              "it here would break comparability with the salience result this "
              "battery exists to decide"),
    Param("seed", DECLARED, value=SEED,
          why="subsets are sampled, so the battery is a random object and must "
              "be reproducible; the repo's BASE_SEED"),
    Param("duration_s", DECLARED, value=DUR,
          why="2 s resolves 0.5 Hz, half the band width, so a beat cannot "
              "straddle two bands unresolved"),
])

T = np.arange(int(SR * DUR)) / SR


def bins_of(alpha):
    """Coincident bins: frequency -> list of (n1, n2, amp), exact in alpha."""
    d = {}
    for n1 in range(-B, B + 1):
        for n2 in range(-B, B + 1):
            amp = float(jv(n1, I_MUS)) * float(jv(n2, I_MUS))
            if abs(amp) < FLOOR:
                continue
            d.setdefault(abs(1 + n1 + n2 * alpha), []).append((n1, n2, amp))
    return d


def render_from(bins, splits=None):
    """Additive render, returning the waveform AND the (freq, amp) list it was
    actually built from.

    RETURNING THE PARTS IS NOT COSMETIC. The first draft checked M1 by comparing
    `bins` against itself -- and since render_from never mutates its input, that
    comparison was true by construction and the arm reported zero violations
    while testing nothing. A vacuous mechanism arm on a board that prints MET is
    the exact failure this repo keeps re-finding, so the check now runs on the
    amplitudes that were RENDERED."""
    x = np.zeros_like(T)
    parts = []
    for k, members in bins.items():
        f0 = F_C * float(k)
        rate = (splits or {}).get(k)
        for j, (n1, n2, amp) in enumerate(members):
            f = f0 if rate is None else f0 + (rate / 2.0 if j % 2 == 0
                                              else -rate / 2.0)
            x += amp * np.cos(2 * np.pi * f * T)
            parts.append((f, amp))
    return x, parts


def amp_multiset(parts):
    return tuple(sorted(round(a, 15) for (_, a) in parts))


def modspec(x):
    e = np.abs(hilbert(x))
    return np.abs(np.fft.rfft((e - e.mean()) * np.hanning(len(e)))) ** 2


FR = np.fft.rfftfreq(len(T), 1.0 / SR)
EDGES = np.arange(MOD_LO, MOD_HI, BW)


def banded_diff(Sx, Se):
    d = np.abs(Sx - Se)
    return np.array([d[(FR >= a_) & (FR < a_ + BW)].sum() for a_ in EDGES])


def concentration(v, kind=STAT):
    """COPIED UNCHANGED from brocot_cue_salience, convention included:
    participation_ratio here is 1 - 1/(n*sum p^2), so HIGHER means MORE
    concentrated. Re-deriving it would have silently broken comparability."""
    v = v[v > 0]
    if v.size < 2:
        return 0.0
    p = v / v.sum()
    if kind == "participation_ratio":
        return float(1.0 - 1.0 / (len(p) * np.sum(p ** 2)))
    if kind == "top_band_share":
        return float(p.max())
    x = np.sort(p)
    n = len(x)
    return float((2 * np.arange(1, n + 1) - n - 1).dot(x) / n)


def fm_render(alpha):
    return np.cos(2 * np.pi * F_C * T
                  + I_MUS * np.sin(2 * np.pi * F_C * T)
                  + I_MUS * np.sin(2 * np.pi * alpha * F_C * T))


RATIOS = [r for r in sorted(
    [Fraction(p, q) for q in range(1, A + 1) for p in range(1, A + 1)
     if gcd(p, q) == 1 and 0.70 <= p / q <= 1.40 and max(p, q) <= A
     and Fraction(p, q) != 1], key=float)
    if str(r) not in EXCLUDE]

rng = np.random.default_rng(SEED)
rows, pooled_e, pooled_c, n_amp_bad = [], [], [], 0

for r in RATIOS:
    bd = bins_of(r)
    multi = sorted([k for k, v in bd.items() if len(v) >= 2],
                   key=lambda k: -sum(abs(a) for (_, _, a) in bd[k]))
    if len(multi) < max(SUBSET_SIZES):
        continue
    base_x, base_parts = render_from(bd)
    Se = modspec(base_x)
    base_amp = amp_multiset(base_parts)

    pts = []
    for _ in range(N_MANIP):
        k = int(rng.choice(SUBSET_SIZES))
        # bias the draw across the amplitude range so energy and count are not
        # forced to move together by the sampling itself
        tier = rng.integers(0, 3)
        pool = (multi[:len(multi) // 2] if tier == 0 else
                multi[len(multi) // 2:] if tier == 1 else multi)
        if len(pool) < k:
            pool = multi
        chosen = rng.choice(len(pool), size=k, replace=False)
        splits = {pool[int(c)]: BEATS[i % len(BEATS)]
                  for i, c in enumerate(chosen)}
        x, parts = render_from(bd, splits)
        if amp_multiset(parts) != base_amp:
            n_amp_bad += 1
        v = banded_diff(modspec(x), Se)
        pts.append(dict(k=k, tier=int(tier), energy=float(v.sum()),
                        conc=concentration(v)))

    E = np.array([p["energy"] for p in pts])
    C = np.array([p["conc"] for p in pts])
    ok = (E > 0) & np.isfinite(C)
    E, C = E[ok], C[ok]
    pooled_e += list(E)
    pooled_c += list(C)

    # matched pairs, within this ratio
    n_e_match = n_c_match = 0
    for i in range(len(E)):
        for j in range(i + 1, len(E)):
            if abs(E[i] - E[j]) <= E_TOL * max(E[i], E[j]):
                lo, hi = sorted((C[i], C[j]))
                if lo > 0 and hi / lo >= C_FACTOR:
                    n_e_match += 1
            if abs(C[i] - C[j]) <= C_TOL * max(C[i], C[j]):
                lo, hi = sorted((E[i], E[j]))
                if lo > 0 and hi / lo >= E_FACTOR:
                    n_c_match += 1
    rho = float(spearmanr(E, C).statistic) if len(E) > 3 else 0.0
    rows.append(dict(ratio=str(r), n_bins=len(multi), n_points=int(len(E)),
                     matched_energy_pairs=n_e_match,
                     matched_conc_pairs=n_c_match, rho=rho,
                     energy_span=float(E.max() / max(E.min(), 1e-300)),
                     conc_span=float(C.max() / max(C.min(), 1e-300))))

# --- the RIVAL: the FM detune family, where the two are confounded
fe, fc, fm_per_ratio = [], [], {}
for r in RATIOS:
    Se = modspec(fm_render(float(r)))
    ee, cc = [], []
    for cents in FM_CENTS:
        v = banded_diff(modspec(fm_render(float(r) * 2 ** (cents / 1200.0))), Se)
        if v.sum() > 0:
            ee.append(float(v.sum()))
            cc.append(concentration(v))
    fm_per_ratio[str(r)] = (ee, cc)
    fe += ee
    fc += cc
rho_fm = float(spearmanr(fe, fc).statistic)
# AMENDMENT 2: the premise, scored WITHIN RATIO as R1 demands.
rho_fm_within = {k: float(spearmanr(v[0], v[1]).statistic)
                 for k, v in fm_per_ratio.items() if len(v[0]) > 3}
rho_fm_median = float(np.median([abs(x) for x in rho_fm_within.values()]))
n_clear = sum(1 for x in rho_fm_within.values() if abs(x) >= PREMISE_BAR)
rho_batt = float(spearmanr(pooled_e, pooled_c).statistic)

print(INSTRUMENT.report())
print(f"\n{len(rows)} ratios (5/7 excluded by the apparatus's own scope), "
      f"{N_MANIP} manipulations each, {STAT} at {BW} Hz bands\n")
print(f"{'ratio':>7s} {'bins':>5s} {'pts':>5s} {'E-span':>9s} {'C-span':>7s} "
      f"{'matchE':>7s} {'matchC':>7s} {'rho':>7s}")
for r in rows:
    print(f"{r['ratio']:>7s} {r['n_bins']:>5d} {r['n_points']:>5d} "
          f"{r['energy_span']:>9.1f} {r['conc_span']:>7.2f} "
          f"{r['matched_energy_pairs']:>7d} {r['matched_conc_pairs']:>7d} "
          f"{r['rho']:>+7.3f}")

n = len(rows)
e1 = sum(r["matched_energy_pairs"] for r in rows)
e2 = sum(r["matched_conc_pairs"] for r in rows)
r1 = sum(1 for r in rows
         if r["matched_energy_pairs"] > 0 and r["matched_conc_pairs"] > 0)

P1 = Bar("|rho| between energy and concentration in the FM detune family",
         PREMISE_BAR, floor=0.0, ceiling=1.0,
         why="a Spearman magnitude; 0 and 1 are both attainable, and if the FM "
             "family is ALREADY decorrelated this battery is unnecessary")
E1 = Bar("matched-energy pairs differing in concentration", 5,
         floor=0, ceiling=n * N_MANIP * (N_MANIP - 1) // 2,
         why="a count of within-ratio pairs; the ceiling is every pair in every "
             "ratio and 0 is attainable if the plane cannot be spanned")
E2 = Bar("matched-concentration pairs differing in energy", 5,
         floor=0, ceiling=n * N_MANIP * (N_MANIP - 1) // 2,
         why="the same count in the other direction, on the same ceiling")
E3 = Bar("|rho| over the constructed battery", RHO_BAR, direction="le",
         floor=0.0, ceiling=1.0,
         why="a Spearman magnitude on the pooled battery; 0 is attainable by "
             "construction and 1 by a battery that failed to decorrelate",
         rival="the FM detune family this battery replaces")
M1 = Bar("battery members whose amplitude multiset differs from exact", 0,
         direction="le", floor=0, ceiling=n * N_MANIP,
         why="a count over every rendered member; every one is meant to be a "
             "pure frequency move")
R1 = Bar("ratios where BOTH matched-pair families exist within the ratio", 5,
         floor=0, ceiling=n,
         why=f"a count over the {n} ratios; pooling across ratios manufactures "
             "spread, so the contrast must be constructible inside one")

sP = P1.score(abs(rho_fm))
s1, s2 = E1.score(e1), E2.score(e2)
s3 = E3.score(abs(rho_batt), rival_value=abs(rho_fm))
sM, sR = M1.score(n_amp_bad), R1.score(r1)

print()
print("  " + P1.line(abs(rho_fm), "{:.3f}") + "   [SEALED, pooled]")
print("  " + P1.line(rho_fm_median, "{:.3f}")
      + f"   [AMENDMENT 2, within-ratio median; {n_clear}/{len(rho_fm_within)} "
        "ratios clear individually]")
print("  " + E1.line(e1, "{:.0f}"))
print("  " + E2.line(e2, "{:.0f}"))
print("  " + E3.line(abs(rho_batt), "{:.3f}", rival_value=abs(rho_fm)))
print("  " + M1.line(n_amp_bad, "{:.0f}"))
print("  " + R1.line(r1, "{:.0f}"))

arms = [Arm.from_bar(sP, PRE_ROLE,
                     claim="energy and concentration really are confounded in "
                           "the family the salience question was asked in"),
        Arm.from_bar(s1, EX_ROLE,
                     claim="concentration can be varied at fixed energy"),
        Arm.from_bar(s2, EX_ROLE,
                     claim="and energy at fixed concentration"),
        Arm.from_bar(s3, EX_ROLE,
                     claim="the battery decorrelates them where the detune "
                           "family cannot"),
        Arm.from_bar(sM, MECH_ROLE,
                     claim="by pure frequency moves, with no amplitude edited"),
        Arm.from_bar(sR, RES_ROLE,
                     claim="and it holds within ratios, not only pooled")]
v = compose(arms, holds="BATTERY_IS_CONSTRUCTIBLE",
            fails="DECORRELATION_NOT_ACHIEVED")
# the corrected lattice: identical arms, premise scored within-ratio
arms_amended = [Arm.from_bar(P1.score(rho_fm_median), PRE_ROLE,
                             claim="energy and concentration are confounded in "
                                   "the FM family, scored within ratio as R1 "
                                   "demands")] + arms[1:]
v_amended = compose(arms_amended, holds="BATTERY_IS_CONSTRUCTIBLE",
                    fails="DECORRELATION_NOT_ACHIEVED")
print(f"\nSEALED   : {v['citation']}")
print(f"AMENDED  : {v_amended['citation']}")
print(f"\nrho: FM family {rho_fm:+.3f}   constructed battery {rho_batt:+.3f}")
print(f"VERDICT: {v['citation']}")

with redpath("rendered battery members", expect_min=500) as rp:
    rp.observed(len(rows) * N_MANIP)

json.dump(dict(I=I_MUS, B=B, sr=SR, duration_s=DUR, f_c=F_C, floor=FLOOR,
               seed=SEED, n_manip=N_MANIP, beats=BEATS,
               subset_sizes=SUBSET_SIZES, stat=STAT, band_width=BW,
               mod_lo=MOD_LO, mod_hi=MOD_HI, fm_cents=FM_CENTS,
               excluded=sorted(EXCLUDE), instrument=INSTRUMENT.seal(),
               rows=rows, rho_fm_family=rho_fm, rho_battery=rho_batt,
               matched_energy_pairs=e1, matched_conc_pairs=e2,
               ratios_with_both=r1, amplitude_violations=n_amp_bad,
               bars={s["name"]: s for s in (sP, s1, s2, s3, sM, sR)},
               verdict=v["head"],
               verdict_amended=v_amended["head"],
               composed_amended=v_amended,
               amendment2=dict(
                   rho_fm_pooled=rho_fm, rho_fm_within=rho_fm_within,
                   rho_fm_within_median=rho_fm_median,
                   n_ratios_clearing=n_clear, n_ratios=len(rho_fm_within),
                   why="P1 was scored by pooling 11 ratios x 10 detunes, which "
                       "this cell's own R1 forbids ('within substrate before "
                       "pooled'). Within ratio the premise HOLDS (median 0.636, "
                       "7/11 individually), so the four arms below it are "
                       "readable and the corrected head is the negative with "
                       "its arms READ rather than INVALID with them unread. "
                       "Found by adversarial review."),
               amendment1=dict(
                   premise_failed=True, rho_fm=rho_fm, rho_battery=rho_batt,
                   conc_span_min=float(min(r["conc_span"] for r in rows)),
                   conc_span_max=float(max(r["conc_span"] for r in rows)),
                   energy_span_max=float(max(r["energy_span"] for r in rows)),
                   diagnosis="subset size is not a concentration knob: the "
                             "modulation difference is broadband and its "
                             "concentration is near-saturated regardless of k, "
                             "while amplitudes span three decades so subset "
                             "choice moves energy by up to 1e11. The battery "
                             "reproduced the one-knob defect it was built to "
                             "remove.",
                   untested_condition="same-rate splitting (k bins at ONE beat "
                                      "rate) never appears in this battery; "
                                      "its absence is not evidence about it",
                   scope_mismatch="docstring says 7 ratios, code ran 11"),
               composed=v),
          open(f"{HERE}/brocot_decorrelation_battery.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_decorrelation_battery.json")
