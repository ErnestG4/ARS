"""
r077_control.py — is the R-156/R-158 anomaly a property of CUBICS or of the ESTIMATOR?

SEALED IN ADVANCE: arsrh/seals/R077_CONTROL_PRECOMMIT.json (written unrun).
Outcomes A/B/C/D are declared there BEFORE any replicate was generated. Outcome C
(anomaly not established) is at equal prominence with B by construction.

THE POINT. R-158 localised the failure of P(g|event) = E[(1+y)1{g}]/E[(1+y)] to a claim about
residues mod Delta. That asks WHY the prediction fails. This asks the prior question: does it
fail *for cubics*, or does this estimator sit +3.3 sem off on ANY continued-fraction orbit? The
+3.30 was never checked against an orbit for which the prediction is a THEOREM.

THE CONTROL IS A GENERIC REAL, and the density matters:
  - For a.e. real, the Gauss natural extension is ergodic, so (x_n, y_n) equidistributes w.r.t.
    1/(ln2 (1+xy)^2) EXACTLY -- the very density the prediction is derived from. H0 holds by
    theorem, not by assumption.
  - An i.i.d. Gauss-Kuzmin a-sequence was considered and REJECTED (recorded in the seal): drawing
    a_i i.i.d. makes x = [0;a_{n+1},...] and y = [0;a_n,...,a_1] functions of disjoint independent
    blocks, hence EXACTLY independent -- while a real orbit couples them. It is the obvious null
    and it is the wrong density.

Everything else is held fixed: same certified_cf at DIG=1200/NPQ=1400, the six |t|=13 matrices
VERBATIM (so the residue structure is fixed and only the number is flipped), same A=20, same
45-term tail guard, same pooling, same z formula.

POWERED FALSIFIER (a quiet control is worthless unless it could have spoken):
  INJECTION ARM builds, by hand, exactly the dependence R-158 hypothesises -- a_{n+1} is boosted
  into the event range with probability delta whenever the residue at n lies in the g=13 class --
  and sweeps delta. If the statistic does not move under an INJECTED residue->future dependence,
  it cannot be trusted to report the absence of one.

Run:  $HOME/fmexplorer/bin/python3 arsrh/cubic/r077_control.py
Writes: arsrh/cubic/r077_control_measured.json
"""
from __future__ import annotations

import json
import math
import os
import sys
from math import gcd

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
for _p in (_HERE, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from gate0_ladder import certified_cf, convergents, lam, bigratio      # noqa: E402
from gate0e_precision import collect_cyclic, DIG, NPQ                  # noqa: E402

A_EV = 20
TAIL = 45
N_REP = 200
STRATUM = 13
SEED = 20260728
DELTAS = [0.0, 0.02, 0.05, 0.10, 0.20]
p_ = lambda *a: print(*a, flush=True)

# OBSERVED VALUES UNDER TEST, copied from the seal (which copied them from the committed
# r077_conditional.py run). Hard-coded so the comparison cannot drift.
OBS_Z_IID, OBS_Z_BLOCK, OBS_N_EVENTS = 3.30, 3.07, 492


def random_real_cf(rng):
    """CF of a uniformly random 1200-decimal-digit real, through the SAME certification the
    cubics go through. Digits are drawn independently -- an earlier attempt built the numerator
    as hi*10^(DIG-18)+lo, which plants a 1164-zero run in the middle and truncated the CF at 33
    terms. A malformed control is an instrument failure that looks like data."""
    d = rng.integers(0, 10, size=DIG)
    return certified_cf(int("".join(map(str, d))), 10 ** DIG, NPQ)


def _gk_tail_draw(rng, floor_a=A_EV):
    """Draw a partial quotient from the Gauss-Kuzmin law CONDITIONED on a >= floor_a.
    P(a >= k) = log2(1 + 1/k), so inverting on (0, log2(1+1/floor_a)] gives the tail."""
    u = rng.random() * math.log2(1.0 + 1.0 / floor_a)
    return max(floor_a, int(1.0 / (2.0 ** u - 1.0)))


def _g_of(P, Q, M):
    a, b, c, d = M
    A_, B_ = a * P + b * Q, c * P + d * Q
    if B_ == 0:
        return None
    if B_ < 0:
        A_, B_ = -A_, -B_
    return gcd(abs(A_), B_)


def orbit(a0, M, rng=None, delta=0.0, inject_g=None):
    """(g, y, lambda) along the orbit. If delta > 0, a_{n+1} is replaced by a Gauss-Kuzmin
    TAIL draw with probability delta whenever g at index n equals `inject_g` -- i.e. the
    residue class is made to predict the future, which is the hypothesis under test."""
    if delta > 0.0:
        a = [a0[0], a0[1]]
        P, Q = [a0[0], a0[1] * a0[0] + 1], [1, a0[1]]
        for i in range(2, len(a0)):
            ai = a0[i]
            g_prev = _g_of(P[i - 1], Q[i - 1], M)
            if g_prev == inject_g and rng.random() < delta:
                ai = _gk_tail_draw(rng)
            a.append(ai)
            P.append(ai * P[-1] + P[-2])
            Q.append(ai * Q[-1] + Q[-2])
    else:
        a = list(a0)
        P, Q = convergents(a)

    G, Y, L = [], [], []
    for i in range(1, len(a) - TAIL):
        g = _g_of(P[i], Q[i], M)
        if g is None:
            continue
        G.append(g)
        Y.append(bigratio(Q[i - 1], Q[i]))
        L.append(lam(a, Q, i))
    return np.array(G), np.array(Y), np.array(L), len(a)


def one_replicate(rng, mats, delta=0.0, inject_g=None):
    """Pool `len(mats)` generic reals exactly as the cubic stratum is pooled."""
    G, Y, L, lens = [], [], [], []
    for M in mats:
        a0 = random_real_cf(rng)
        g_, y_, l_, n = orbit(a0, M, rng=rng, delta=delta, inject_g=inject_g)
        G.append(g_); Y.append(y_); L.append(l_); lens.append(n)
    G, Y, L = np.concatenate(G), np.concatenate(Y), np.concatenate(L)
    w, ev = 1.0 + Y, L >= A_EV
    n_ev = int(ev.sum())
    out = {}
    if n_ev == 0:
        return None
    for g in sorted(set(G.tolist())):
        pred = float((w * (G == g)).sum() / w.sum())
        meas = float((G[ev] == g).mean())
        se = float(np.sqrt(max(pred * (1 - pred), 1e-12) / n_ev))
        out[int(g)] = {"pred": pred, "meas": meas, "z": (meas - pred) / se}
    return {"branches": out, "n_events": n_ev, "cf_len_median": float(np.median(lens)),
            "divisors": sorted(out)}


def main():
    rng = np.random.default_rng(SEED)
    mats = [o[3] for o in collect_cyclic(box=14, per=8)[STRATUM]]
    p_("=" * 78)
    p_("R-077 CONTROL — is the +3.30 a property of cubics, or of the estimator?")
    p_(f"  sealed: arsrh/seals/R077_CONTROL_PRECOMMIT.json    outcomes A/B/C/D declared unrun")
    p_(f"  stratum |t|={STRATUM}, {len(mats)} matrices held VERBATIM, {N_REP} replicates")
    p_("=" * 78)

    # ---- SPECIFICITY ARM: delta = 0. The primary readout. -------------------
    reps = [r for r in (one_replicate(rng, mats) for _ in range(N_REP)) if r]
    z13 = np.array([r["branches"][STRATUM]["z"] for r in reps if STRATUM in r["branches"]])
    nev = np.array([r["n_events"] for r in reps])
    clen = np.array([r["cf_len_median"] for r in reps])
    divsets = {tuple(r["divisors"]) for r in reps}

    p_(f"\n[SPECIFICITY, delta=0]  {len(z13)}/{N_REP} replicates usable")
    p_(f"  control z(g={STRATUM}):  mean {z13.mean():+.4f}   sd {z13.std(ddof=1):.4f}   "
       f"sem {z13.std(ddof=1)/math.sqrt(len(z13)):.4f}")
    pct = np.percentile(z13, [5, 50, 90, 95, 99])
    p_(f"  percentiles  5% {pct[0]:+.2f}   50% {pct[1]:+.2f}   90% {pct[2]:+.2f}   "
       f"95% {pct[3]:+.2f}   99% {pct[4]:+.2f}")
    p_(f"  n_events per replicate: median {np.median(nev):.0f} (cubic had {OBS_N_EVENTS})")
    p_(f"  CF length median {np.median(clen):.0f}")
    p_(f"  g-divisor sets observed: {divsets}")

    # ---- outcome D gate, BEFORE reading A/B/C ------------------------------
    fail = []
    if len(divsets) != 1 or set(next(iter(divsets))) != {1, 13, 169}:
        fail.append(f"divisor set != {{1,13,169}}: {divsets}")
    if abs(np.median(nev) - OBS_N_EVENTS) / OBS_N_EVENTS > 0.25:
        fail.append(f"n_events median {np.median(nev):.0f} vs cubic {OBS_N_EVENTS} (>25%)")
    if len(z13) < 0.95 * N_REP:
        fail.append(f"only {len(z13)}/{N_REP} replicates produced a z")

    # ---- SENSITIVITY ARM: can it fire at all? ------------------------------
    p_(f"\n[SENSITIVITY]  injected residue->future dependence at g={STRATUM}")
    p_(f"{'delta':>8s} {'n':>4s} {'mean z':>9s} {'sd':>7s} {'P(z>obs)':>9s}")
    inj = {}
    n_inj = 40
    for d in DELTAS:
        zz = []
        for _ in range(n_inj):
            r = one_replicate(rng, mats, delta=d, inject_g=STRATUM)
            if r and STRATUM in r["branches"]:
                zz.append(r["branches"][STRATUM]["z"])
        zz = np.array(zz)
        frac = float((zz > OBS_Z_IID).mean())
        inj[d] = {"n": len(zz), "mean_z": float(zz.mean()), "sd_z": float(zz.std(ddof=1)),
                  "frac_above_observed": frac}
        p_(f"{d:>8.2f} {len(zz):>4d} {zz.mean():>+9.3f} {zz.std(ddof=1):>7.3f} {frac:>9.2f}")

    # ---- verdict against the SEALED map ------------------------------------
    m, s = float(z13.mean()), float(z13.std(ddof=1))
    ctrl_clean = abs(m) < 0.5 and 0.7 <= s <= 1.4
    p_obs = float((z13 >= OBS_Z_IID).mean())
    lo90, hi90 = np.percentile(z13, [5, 95])

    p_("\n" + "=" * 78)
    if fail:
        verdict = "D_INSTRUMENT_FAILURE"
        p_("VERDICT: D — INSTRUMENT FAILURE. The run is VOID; do not interpret A/B/C.")
        for f in fail:
            p_(f"  - {f}")
    elif abs(m) >= 1.5 or (lo90 <= OBS_Z_IID <= hi90):
        verdict = "A_ARTIFACT"
        p_("VERDICT: A — ARTIFACT. The anomaly is a property of the ESTIMATOR, not of cubics.")
        p_(f"  control mean z = {m:+.3f}; observed {OBS_Z_IID:+.2f} sits inside the control range.")
        p_("  R-077's third localisation is VOID. R-156/R-158 need CORRECTION, not extension.")
    elif ctrl_clean and OBS_Z_IID > np.percentile(z13, 99):
        verdict = "B_REAL_AND_CUBIC_SPECIFIC"
        p_("VERDICT: B — the premise SURVIVES. Anomaly is substrate-real and cubic-specific.")
        p_(f"  control z ~ ({m:+.3f}, sd {s:.3f}); observed {OBS_Z_IID:+.2f} beyond 99th pct "
           f"({np.percentile(z13,99):+.2f}); P(control >= observed) = {p_obs:.4f}")
        p_("  Proceed to the residue test -- WITH the look-elsewhere arm (9 branches).")
    else:
        verdict = "C_NOT_ESTABLISHED"
        p_("VERDICT: C — NOT ESTABLISHED, and this is a result, not a non-result.")
        p_(f"  control z ~ ({m:+.3f}, sd {s:.3f}); observed {OBS_Z_IID:+.2f} sits at "
           f"P(control >= observed) = {p_obs:.4f}, inside the 99th pct.")
        p_("  The thread PARKS. The formula stays CALIBRATED. No localisation is pursued.")
    p_("=" * 78)

    res = {"seal": "R077_CONTROL_PRECOMMIT", "verdict": verdict,
           "n_rep": N_REP, "n_usable": len(z13), "stratum": STRATUM,
           "matrices": [list(m_) for m_ in mats],
           "control_z_mean": m, "control_z_sd": s,
           "control_z_percentiles": {str(k): float(v) for k, v in
                                     zip([5, 50, 90, 95, 99], np.percentile(z13, [5, 50, 90, 95, 99]))},
           "control_clean": bool(ctrl_clean),
           "p_control_ge_observed": p_obs,
           "observed": {"z_iid": OBS_Z_IID, "z_block": OBS_Z_BLOCK, "n_events": OBS_N_EVENTS},
           "n_events_median": float(np.median(nev)), "cf_len_median": float(np.median(clen)),
           "divisor_sets": [list(d) for d in divsets],
           "instrument_failures": fail,
           "injection": {str(k): v for k, v in inj.items()}}
    dest = os.path.join(_HERE, "r077_control_measured.json")
    with open(dest, "w") as f:
        json.dump(res, f, indent=2)
    p_(f"-> wrote {dest}")
    return res


if __name__ == "__main__":
    main()
