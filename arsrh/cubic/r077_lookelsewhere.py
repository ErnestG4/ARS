"""
r077_lookelsewhere.py — does the R-077 anomaly survive the trials factor it never stated?

SEALED IN ADVANCE: arsrh/seals/R077_CONTROL_PRECOMMIT_ADDENDUM_1.json (written unrun).

THE PROBLEM THIS FIXES. R-156 reported "+3.30 sem" and R-158 "+3.07 sem" at |t|=13, g=13. That
cell is the one that looked most interesting out of NINE (stratum, g) branches, and no trials
factor was ever stated -- not in the register, not in a seal. A per-cell z quoted as though it
were a global significance is the sem-vs-CI family in a new costume: a number correct for the
quantity it measures, reported in a slot that owns a different quantity.

THE STATISTIC, fixed in the addendum before this ran: T = max over all 9 branches of |z|.
That is the statistic that actually selected the finding, so it is the one whose null matters.
Using an EMPIRICAL max-|z| null (generic reals through the identical pipeline) makes the trials
factor exact rather than a Bonferroni approximation, and it handles correctly the fact that
branches within a stratum are NOT independent -- their proportions sum to 1.

  observed T = 3.5871 at |t|=5, g=25  -- note this is NOT the cell R-156/R-158 argued from
  (|t|=13, g=13, z = +3.2954), and it points the other way: depletion, not enrichment.

Run:  $HOME/fmexplorer/bin/python3 arsrh/cubic/r077_lookelsewhere.py
Writes: arsrh/cubic/r077_lookelsewhere_measured.json
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
for _p in (_HERE, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from gate0e_precision import collect_cyclic                              # noqa: E402
from r077_control import random_real_cf, orbit, A_EV                     # noqa: E402

N_REP = 200
SEED = 20260729
STRATA = (2, 5, 13)
OBS_T = 3.5871
OBS_AT = "|t|=5, g=25"
# the cubic's own 9 branches, from the committed r077_conditional run
OBS_BRANCHES = {(2, 1): +1.2815, (2, 2): -1.7765, (2, 4): +0.1511,
                (5, 1): -0.2355, (5, 5): +2.0333, (5, 25): -3.5871,
                (13, 1): -3.2867, (13, 13): +3.2954, (13, 169): +0.4185}
p_ = lambda *a: print(*a, flush=True)


def stratum_z(rng, mats):
    """The 3 branch z's for one control stratum, pooled exactly as the cubics are."""
    G, Y, L, lens = [], [], [], []
    for M in mats:
        g_, y_, l_, n = orbit(random_real_cf(rng), M)
        G.append(g_); Y.append(y_); L.append(l_); lens.append(n)
    G, Y, L = np.concatenate(G), np.concatenate(Y), np.concatenate(L)
    w, ev = 1.0 + Y, L >= A_EV
    n_ev = int(ev.sum())
    if n_ev == 0:
        return None, 0, 0.0
    out = {}
    for g in sorted(set(G.tolist())):
        pred = float((w * (G == g)).sum() / w.sum())
        meas = float((G[ev] == g).mean())
        se = float(np.sqrt(max(pred * (1 - pred), 1e-12) / n_ev))
        out[int(g)] = (meas - pred) / se
    return out, n_ev, float(np.median(lens))


def main():
    rng = np.random.default_rng(SEED)
    by_t = collect_cyclic(box=14, per=8)
    mats = {t: [o[3] for o in by_t[t]] for t in STRATA}
    p_("=" * 78)
    p_("R-077 LOOK-ELSEWHERE — does the anomaly survive its own trials factor?")
    p_("  sealed: R077_CONTROL_PRECOMMIT_ADDENDUM_1.json (written unrun)")
    p_(f"  T = max|z| over 9 branches;  observed T = {OBS_T} at {OBS_AT}")
    for t in STRATA:
        p_(f"  stratum |t|={t}: {len(mats[t])} objects")
    p_("=" * 78)

    Ts, per_branch, nevs, divok = [], {}, {t: [] for t in STRATA}, True
    for _ in range(N_REP):
        zs, ok = {}, True
        for t in STRATA:
            out, n_ev, _ = stratum_z(rng, mats[t])
            if out is None:
                ok = False
                break
            nevs[t].append(n_ev)
            for g, z in out.items():
                zs[(t, g)] = z
        if not ok:
            continue
        if set(zs) != set(OBS_BRANCHES):
            divok = False
        Ts.append(max(abs(v) for v in zs.values()))
        for k, v in zs.items():
            per_branch.setdefault(k, []).append(v)
    Ts = np.array(Ts)

    # ---- instrument gate FIRST -------------------------------------------
    fail = []
    if not divok:
        fail.append("control branch set differs from the cubic's 9 branches")
    if len(Ts) < 0.95 * N_REP:
        fail.append(f"only {len(Ts)}/{N_REP} replicates yielded all 9 branches")
    cub_nev = {2: 626, 5: 652, 13: 492}
    for t in STRATA:
        med = float(np.median(nevs[t]))
        if abs(med - cub_nev[t]) / cub_nev[t] > 0.25:
            fail.append(f"|t|={t}: control n_events {med:.0f} vs cubic {cub_nev[t]} (>25%)")

    p_(f"\n[control]  {len(Ts)}/{N_REP} replicates usable")
    for t in STRATA:
        p_(f"  |t|={t}: n_events median {np.median(nevs[t]):.0f}  (cubic {cub_nev[t]})")
    p_(f"\n  per-branch control z (should each be ~N(0,1)):")
    p_(f"{'branch':>16s} {'mean':>8s} {'sd':>7s} {'cubic z':>9s}")
    pb = {}
    for k in sorted(per_branch):
        v = np.array(per_branch[k])
        pb[f"|t|={k[0]},g={k[1]}"] = {"mean": float(v.mean()), "sd": float(v.std(ddof=1)),
                                      "cubic_z": OBS_BRANCHES.get(k)}
        p_(f"{'|t|='+str(k[0])+' g='+str(k[1]):>16s} {v.mean():>+8.3f} {v.std(ddof=1):>7.3f} "
           f"{OBS_BRANCHES.get(k, float('nan')):>+9.3f}")

    q = np.percentile(Ts, [50, 90, 95, 99])
    p_(f"\n  T = max|z| over 9 branches, NULL distribution:")
    p_(f"    median {q[0]:.3f}   90% {q[1]:.3f}   95% {q[2]:.3f}   99% {q[3]:.3f}")
    p_(f"    (a single N(0,1) would give 95% at 1.96; the 9-branch max sits far above — "
       f"that gap IS the trials factor)")
    p_val = float((Ts >= OBS_T).mean())
    p_(f"\n  observed T = {OBS_T}    P(T_control >= observed) = {p_val:.4f}"
       f"   [{int((Ts>=OBS_T).sum())}/{len(Ts)} replicates]")

    p_("\n" + "=" * 78)
    if fail:
        verdict = "LE_C_INSTRUMENT_FAILURE"
        p_("VERDICT: LE_C — INSTRUMENT FAILURE. VOID; do not interpret.")
        for f in fail:
            p_(f"  - {f}")
    elif p_val <= 0.05:
        verdict = "LE_A_SURVIVES"
        p_(f"VERDICT: LE_A — the anomaly SURVIVES its trials factor. p = {p_val:.4f}")
        p_("  The premise is established globally, not at a hand-picked cell.")
        p_("  Third localisation is warranted. Quote the trials factor with it, always.")
    else:
        verdict = "LE_B_DOES_NOT_SURVIVE"
        p_(f"VERDICT: LE_B — DOES NOT SURVIVE. p = {p_val:.4f} > 0.05")
        p_("  The reported significance of R-156/R-158 was inflated by unstated multiplicity.")
        p_("  The estimator is clean (parent seal) but NO anomaly survives attached to it.")
        p_("  Both register entries require correction. The thread PARKS.")
    p_("=" * 78)

    res = {"seal": "R077_CONTROL_PRECOMMIT_ADDENDUM_1", "verdict": verdict,
           "n_rep": N_REP, "n_usable": int(len(Ts)),
           "observed_T": OBS_T, "observed_at": OBS_AT,
           "p_value": p_val,
           "T_null_percentiles": {str(k): float(v) for k, v in zip([50, 90, 95, 99], q)},
           # the FULL null array, so a corrected p can be read off for ANY cell later without
           # re-running. Saving only percentiles cost a 40-minute re-run to answer "and what is
           # the corrected p for the cell R-156 actually argued from?" -- which is the first
           # question anyone asks of a max-statistic null.
           "T_null": [float(x) for x in Ts],
           "corrected_p_per_cubic_branch": {
               f"|t|={k[0]},g={k[1]}": float((Ts >= abs(v)).mean())
               for k, v in OBS_BRANCHES.items()},
           "per_branch_control": pb,
           "n_events_median": {str(t): float(np.median(nevs[t])) for t in STRATA},
           "instrument_failures": fail}
    dest = os.path.join(_HERE, "r077_lookelsewhere_measured.json")
    with open(dest, "w") as f:
        json.dump(res, f, indent=2)
    p_(f"-> wrote {dest}")
    return res


if __name__ == "__main__":
    main()
