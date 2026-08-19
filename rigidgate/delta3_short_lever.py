"""The Delta_3 variant's OPENING OBLIGATION — power on the short lever.
COMMITTED GENERATOR of rigidgate/delta3_short_lever.json.

RG-ADD-9 downgraded the Delta_3 growth arm to PROMOTABLE-PENDING-POWER-
INSIDE-WINDOW.  The 12:1 figure that made it promotable (GUE increment
0.1053 +/- 0.0086) was measured across a lever of L = 5 -> 40.  Under the
currently banked L policy the only admissible cell at n=2000 is L = 5, and
zeta's validity cap is 5.99 — so a deployed Delta_3 arm has at best
L in [2, 6], roughly a 3x lever against the 8x the figure came from.  A
growth statistic's power falls with the lever, so the promotion rests on a
number measured where the arm cannot be deployed.

This runs BEFORE anything else in that brief, as required, and it can end
the brief: if the arm cannot resolve GUE's own growth on the short lever,
it is not a candidate instrument and the n=343 problem needs more data
rather than a different statistic.

Three questions, in order:
  Q1 does the GUE ensemble's Delta_3 increment over [2,6] exceed its own
     spread?  (the power question — 12:1 on the long lever, what here?)
  Q2 does the arm still REJECT the hyper-rigid spoofs on the short lever?
     (a powerless arm that rejects nothing is useless; a powerful arm that
     rejects everything is worse)
  Q3 what is the arm's per-realization error rate on the short lever, in
     both directions, against the thresholds already fixed in
     RELIABILITY_THRESHOLDS.md?
"""

import json
import sys

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
for p in (f"{ROOT}/rigidgate", f"{ROOT}/lcap"):
    if p not in sys.path:
        sys.path.insert(0, p)
import gate_probe as G                                          # noqa: E402
from policy import goe_positions                                # noqa: E402

DEG = 6
N_DRAWS = 40
LONG = (5.0, 40.0)          # the lever the 12:1 came from
SHORT = (2.0, 6.0)          # the lever a deployed arm would have
N_GRID = [343, 1200, 2000]
FP_MAX = FN_MAX = 0.05      # RELIABILITY_THRESHOLDS.md, unchanged


def d3_pair(pos, lever):
    lo = G.delta3(pos, lever[0], DEG)
    hi = G.delta3(pos, lever[1], DEG)
    if lo is None or hi is None:
        return np.nan
    return float(hi - lo)


def sample(sampler, n, k, seed0, lever):
    out = []
    for i in range(k):
        pos = sampler(n, np.random.default_rng(seed0 + i))
        out.append(d3_pair(pos, lever))
    return np.asarray(out, float)


def clock(n, rng):
    return np.arange(n, dtype=float)


def anti0(n, rng):
    return G.antithetic_renewal(n, 0.0, rng)


def main():
    out = dict(long_lever=LONG, short_lever=SHORT, n_draws=N_DRAWS,
               thresholds=dict(FP_MAX=FP_MAX, FN_MAX=FN_MAX), by_n={})
    for n in N_GRID:
        print(f"n={n}", flush=True)
        row = {}
        for tag, lever in (("long", LONG), ("short", SHORT)):
            gue = sample(G.gue_positions, n, N_DRAWS, 95_000, lever)
            gue = gue[np.isfinite(gue)]
            if gue.size < 5:
                row[tag] = dict(error="insufficient finite draws")
                continue
            m, sd = float(gue.mean()), float(gue.std(ddof=1))
            snr = m / sd if sd > 0 else np.inf
            # Q2/Q3: spoof rejection and both-direction error rates.
            # ARM RULE (same form as the original): the observation passes if
            # its increment reaches SHAPE_FRAC of the GUE ensemble's mean.
            thr = 0.35 * m
            gue_t = sample(G.gue_positions, n, N_DRAWS, 96_000, lever)
            gue_t = gue_t[np.isfinite(gue_t)]
            fn = float(np.mean(gue_t < thr))          # true class rejected
            fps = {}
            for stag, samp in (("clock", clock), ("antithetic_f0", anti0),
                               ("goe", goe_positions)):
                v = sample(samp, n, max(12, N_DRAWS // 2), 97_000, lever)
                v = v[np.isfinite(v)]
                fps[stag] = float(np.mean(v >= thr)) if v.size else None
            row[tag] = dict(gue_increment_mean=m, gue_increment_sd=sd,
                            snr=float(snr), arm_threshold=float(thr),
                            FN_gue=fn, FP=fps,
                            admissible=bool(fn <= FN_MAX and all(
                                (x is not None and x <= FP_MAX)
                                for x in fps.values())))
            print(f"  {tag:5s} lever {lever}: GUE increment "
                  f"{m:.4f}+-{sd:.4f} (SNR {snr:.1f})  FN {fn:.2f}  "
                  f"FP {fps}  admissible={row[tag]['admissible']}", flush=True)
        if "long" in row and "short" in row and "snr" in row["long"]:
            row["snr_ratio_short_over_long"] = (
                row["short"]["snr"] / row["long"]["snr"]
                if row["long"]["snr"] else None)
        out["by_n"][str(n)] = row

    # verdict: does the arm survive the short lever anywhere?
    survives = [n for n, r in out["by_n"].items()
                if isinstance(r.get("short"), dict) and r["short"].get("admissible")]
    out["verdict"] = dict(
        survives_short_lever_at=survives,
        arm_is_a_candidate=bool(survives),
        note=("If empty: the Delta_3 arm cannot be deployed inside the "
              "admissible L window, the RG-ADD-9 promotion does not "
              "survive, and the n=343 problem needs MORE DATA rather than "
              "a different statistic."))
    json.dump(out, open(f"{ROOT}/rigidgate/delta3_short_lever.json", "w"),
              indent=1)
    print(f"\nVERDICT: arm admissible on the short lever at n = "
          f"{survives or 'NOWHERE'}", flush=True)


if __name__ == "__main__":
    main()
