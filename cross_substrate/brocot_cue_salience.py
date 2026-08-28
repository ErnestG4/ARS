"""WHAT DID THE SKIPS TRACK? Concentration, energy, or share.

COMMITTED GENERATOR of cross_substrate/brocot_cue_salience.json.
Predictions sealed here, before any output exists.

THE OPEN QUESTION THIS INHERITS
---------------------------------
A listener ran 90 trials of an ill-formed task and skipped 29 of them, reporting
that those "sounded the same". The answered set is selected on discriminability
so it yields no rate -- but the SKIP PATTERN is real structure and nothing so far
explains it:

    presence  fails: every ratio carries the cue, 21 to 101 dB above the floor
    SNR       fails: 8/7 carries 55 dB and was skipped 7/7
                     5/6 carries 63 dB and was answered 5/5
    share     works: 34% answered at low cue fraction, 97% at high

Share working while presence and SNR fail is the clue. Cue fraction is the beat
band's portion of the total exact-vs-twin difference, so it is high when the
difference is CONCENTRATED at one frequency and low when the same energy is
spread across many micro-shifted partials. That suggests the listener was not
reporting detection at all but SALIENCE -- one clear beat versus a diffuse
smear of equal energy.

If so, a concentration statistic computed on the difference spectrum should
predict the skips better than either the difference's total energy or the
cue-band share, because concentration is the thing itself while share is one
band's proxy for it.

WHAT THIS CELL IS NOT
---------------------
It is not a perceptual result. n = 12 ratios, ONE listener, a task whose
answered set is selected, and a skip criterion the listener set themselves. S3
exists so the cell cannot overclaim on twelve points: if the bootstrap interval
on the best correlation covers zero, the answer is UNRESOLVED and the structure
stays unexplained.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — bars edge-probed                                        ║
║                                                                              ║
║ S1  CONCENTRATION PREDICTS THE SKIPS — |Spearman| between the difference     ║
║     spectrum's concentration and the per-ratio answer rate is at least 0.60. ║
║ S2  AND BEATS ENERGY — it exceeds |Spearman| for the difference's TOTAL      ║
║     energy by at least 0.20. Energy is the rival account: louder differences ║
║     are easier, and it needs beating rather than ignoring.                  ║
║ S3  AND SURVIVES n = 12 — the 95% bootstrap interval on the best correlation ║
║     excludes zero. THIS IS THE ARM THAT DECIDES WHETHER ANYTHING IS SAID.    ║
║     Twelve points make a rho of 0.6 unremarkable; without S3 the other two   ║
║     arms are decoration.                                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import csv
import json
import os
import sys
from fractions import Fraction
from math import gcd

import numpy as np
from scipy import stats
from scipy.signal import hilbert
from scipy.special import jv

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/brocot"))
from redpath import redpath                                       # noqa: E402
from reachable import Bar                                         # noqa: E402
from modelparams import Model, Param, TESTED, DECLARED            # noqa: E402
from verdictlattice import (Arm, compose, EXISTENCE as EX_ROLE,   # noqa: E402
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from phase3.partial_prediction import order_bound                 # noqa: E402

I_MUS = 0.9
B = order_bound(I_MUS)
A = 2 * B
SR, DUR, F_C, CENTS = 44100, 3.0, 220.0, 6.0
MOD_LO, MOD_HI, BW = 0.5, 40.0, 1.0
FLOOR = 1e-4
N_BOOT, SEED = 4000, 20260828
T_ = os.path.join(HERE, "stageb_trials")

INSTRUMENT = Model("modulation-spectrum difference, three summary statistics", [
    Param("concentration_stat", TESTED,
          sweep=["participation_ratio", "gini", "top_band_share"],
          why="three ways to say 'concentrated'; if they disagree the concept "
              "is doing less work than the winner suggests"),
    Param("band_width_hz", TESTED, sweep=[0.5, 1.0, 2.0],
          why="concentration is measured over bands, so it must not be an "
              "artifact of the binning"),
    Param("render_floor", DECLARED, value=FLOOR,
          why="brocot_cue_presence showed every result identical from 1e-4 to "
              "1e-9, so this is not a live parameter here"),
    Param("listener", DECLARED, value="n = 1, self-set skip criterion",
          why="the hard limit on everything this cell can say; S3 exists "
              "because of it"),
])

T = np.arange(int(SR * DUR)) / SR


def render(alpha):
    x = np.zeros_like(T)
    for n1 in range(-B, B + 1):
        for n2 in range(-B, B + 1):
            a = float(jv(n1, I_MUS)) * float(jv(n2, I_MUS))
            if abs(a) < FLOOR:
                continue
            f = abs(F_C * (1.0 + n1 + n2 * alpha))
            if 20 <= f <= 16000:
                x += a * np.cos(2 * np.pi * f * T)
    return x


def diffspec(alpha, bw):
    def ms(x):
        e = np.abs(hilbert(x))
        return np.abs(np.fft.rfft((e - e.mean()) * np.hanning(len(e)))) ** 2
    Se, St = ms(render(alpha)), ms(render(alpha * 2 ** (CENTS / 1200.0)))
    fr = np.fft.rfftfreq(len(T), 1.0 / SR)
    d = np.abs(St - Se)
    edges = np.arange(MOD_LO, MOD_HI, bw)
    return np.array([d[(fr >= a_) & (fr < a_ + bw)].sum() for a_ in edges])


def concentration(v, kind):
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


key = {k["trial"]: k for k in
       json.load(open(f"{T_}/KEY_do_not_open.json"))["key"]}
rows_csv = list(csv.DictReader(open(f"{T_}/responses.csv")))
ansd = {int(r["trial"]) for r in rows_csv if (r["odd"] or "").strip()}
reached = max(ansd) if ansd else 0
rate = {}
for t in range(1, reached + 1):
    k = key[t]
    if k["arm"] != "merge":
        continue
    d = rate.setdefault(k["ratio"], [0, 0])
    d[0] += 1
    d[1] += (t in ansd)

RATIOS = [r for r in rate if Fraction(r) != 1]
data = []
for r in sorted(RATIOS, key=lambda x: float(Fraction(x))):
    n, a = rate[r]
    rec = dict(ratio=r, reached=n, answered=a, answer_rate=a / n)
    for bw in (0.5, 1.0, 2.0):
        v = diffspec(float(Fraction(r)), bw)
        rec[f"energy|{bw}"] = float(v.sum())
        for kind in ("participation_ratio", "gini", "top_band_share"):
            rec[f"{kind}|{bw}"] = concentration(v, kind)
    data.append(rec)

y = np.array([d["answer_rate"] for d in data])


def rho(k):
    return float(stats.spearmanr([d[k] for d in data], y)[0])


cands = {f"{kind}|{bw}": abs(rho(f"{kind}|{bw}"))
         for kind in ("participation_ratio", "gini", "top_band_share")
         for bw in (0.5, 1.0, 2.0)}
best_k = max(cands, key=cands.get)
s1 = cands[best_k]
e_best = max(abs(rho(f"energy|{bw}")) for bw in (0.5, 1.0, 2.0))
s2 = s1 - e_best

rng = np.random.default_rng(SEED)
xb = np.array([d[best_k] for d in data])
boot = []
for _ in range(N_BOOT):
    i = rng.integers(0, len(y), len(y))
    if len(set(y[i])) < 2 or len(set(xb[i])) < 2:
        continue
    boot.append(stats.spearmanr(xb[i], y[i])[0])
lo, hi = np.percentile(boot, [2.5, 97.5])
s3 = 1 if (lo > 0 or hi < 0) else 0

S1 = Bar("|rho| concentration vs answer rate", 0.60, floor=0.0, ceiling=1.0,
         why="|Spearman| is bounded by 1")
S2 = Bar("concentration |rho| minus energy |rho|", 0.20, floor=-1.0,
         ceiling=1.0, why="a difference of two |Spearman| values")
S3 = Bar("bootstrap CI on the best rho excludes zero", 1, floor=0, ceiling=1,
         why="a boolean: 0 or 1")
sc1, sc2, sc3 = S1.score(s1), S2.score(s2), S3.score(s3)

print(INSTRUMENT.report())
print(f"\n{len(data)} ratios, {sum(d['reached'] for d in data)} merge trials "
      f"reached by one listener\n")
print(f"{'ratio':>7s} {'reached':>8s} {'answered':>9s} {'rate':>6s} "
      f"{'energy':>11s} {'concentr.':>10s}")
for d in sorted(data, key=lambda x: -x["answer_rate"]):
    print(f"{d['ratio']:>7s} {d['reached']:>8d} {d['answered']:>9d} "
          f"{d['answer_rate']:>6.0%} {d['energy|1.0']:>11.3e} "
          f"{d[best_k]:>10.3f}")
print(f"\nbest concentration statistic: {best_k}")
print(f"{'statistic':>28s} {'|rho| vs answer rate':>22s}")
for k in sorted(cands, key=cands.get, reverse=True):
    print(f"{k:>28s} {cands[k]:>21.3f}")
for bw in (0.5, 1.0, 2.0):
    print(f"{'energy|' + str(bw):>28s} {abs(rho(f'energy|{bw}')):>21.3f}")
print(f"\nbootstrap 95% CI on {best_k}: [{lo:+.3f}, {hi:+.3f}]  "
      f"({len(boot)} resamples)")
print()
for b, v, f in ((S1, s1, "{:.3f}"), (S2, s2, "{:+.3f}"), (S3, s3, "{:.0f}")):
    print("  " + b.line(v, f))

v = compose([Arm.from_bar(sc3, EX_ROLE,
                          claim="twelve points support saying anything at all"),
             Arm.from_bar(sc1, RES_ROLE,
                          claim="concentration tracks the skips"),
             Arm.from_bar(sc2, MECH_ROLE,
                          claim="and beats loudness, the rival account")],
            holds="SKIPS_TRACK_SALIENCE", fails="SKIP_STRUCTURE_UNRESOLVED")
print(f"\nVERDICT: {v['citation']}")
print("  One listener, twelve ratios, a self-set skip criterion. Whatever this")
print("  says, it is a lead and not a perceptual result.")

with redpath("ratios with reached merge trials", expect_min=10) as rp:
    rp.observed(len(data))

json.dump(dict(I=I_MUS, sr=SR, f_c=F_C, cents=CENTS, floor=FLOOR,
               instrument=INSTRUMENT.seal(), rows=data,
               rho_candidates=cands, best=best_k, energy_best=e_best,
               boot_ci=[float(lo), float(hi)], n_boot=len(boot),
               bars={s["name"]: s for s in (sc1, sc2, sc3)},
               verdict=v["head"], composed=v),
          open(f"{HERE}/brocot_cue_salience.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_cue_salience.json")
