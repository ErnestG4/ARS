"""
GATE 0h — the injection arm: axis 2 of the power question. R-070's owed item.

The ladder varies COUNT at fixed PERFECT alignment (measured lag spread 2e-13). The target's
plausible weak signal is the opposite shape -- many events, partially coincident, SMEARED in u --
and a detector calibrated on "few but perfect" is uncalibrated for "many but smeared". Dirichlet
precedent: the amplitude gate was unpowered until the injected control fired.

So: inject coincidences at controlled fraction f AND controlled jitter half-width J, and report the
detection floor JOINTLY on both axes.

NO TARGET DATA IS TOUCHED. The processes here are synthetic, generated from Gauss-Kuzmin and
calibrated against the anchors measured in gate0g (Levy 1.1866, events/unit u 0.0602 at A = 20,
which gate0g showed agree across strata to 0.9 sem). Pairing two real stratum-A objects is the
sealed statistic and is not computed anywhere in this file.

DETECTOR (pre-registration candidate, stated so it can be sealed verbatim):
  events of object 1 at {u_i}, object 2 at {v_j}, both on the log-denominator line.
  candidate lags are exactly the pairwise differences u_i - v_j, so
      S(w) = max over lag L of  #{(i,j) : |u_i - v_j - L| <= w}
  computed exactly by sliding a window of width 2w over the sorted difference multiset.
  NULL: permutation over object pairings -- pair each object with an unrelated one and recompute S.
  DETECTION: S_obs above the 95th percentile of that null.
"""
from __future__ import annotations
import json, math, os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
p_ = lambda *a: print(*a, flush=True)
rng = np.random.default_rng(20260726)

NPQ, A_EV = 2000, 20
WS = (0.02, 0.05, 0.2, 1.0)
JS = (0.0, 0.05, 0.2, 1.0)
FS = (0.02, 0.05, 0.10, 0.20, 0.40)
NTRIAL, NNULL = 200, 400


def gk_events(npq=NPQ, A=A_EV):
    """simulate a Gauss-Kuzmin continued fraction; return (event u-locations, total u range).
    lambda_n = [a_{n+1}; a_{n+2}, ...] + q_{n-1}/q_n, computed exactly from the simulated digits;
    log q_n = sum log(a_i + q_{i-2}/q_{i-1}).  Reproduces Levy and the 1.4427/A tail by construction."""
    V = rng.random(npq + 60)
    a = np.floor(1.0 / (np.power(2.0, V) - 1.0)).astype(np.float64)
    a = np.clip(a, 1, 1e12)
    r = np.empty(npq + 60)                       # r_n = q_{n-1}/q_n
    r[0] = 0.0
    for n in range(1, npq + 60):
        r[n] = 1.0 / (a[n] + r[n - 1])
    u = np.cumsum(np.log(a[1:npq + 1] + r[0:npq]))
    t = np.empty(npq + 60)                       # t_n = [a_n; a_{n+1}, ...]
    t[-1] = a[-1]
    for n in range(npq + 58, -1, -1):
        t[n] = a[n] + 1.0 / t[n + 1]
    lam = t[2:npq + 2] + r[1:npq + 1]
    ev = u[lam >= A]
    return ev, float(u[-1])


def stat_all(uu, vv, ws=WS):
    """S(w) for every w at once -- the sorted difference multiset is shared, so this is one sort."""
    if len(uu) == 0 or len(vv) == 0:
        return [0] * len(ws)
    d = np.sort((uu[:, None] - vv[None, :]).ravel())
    ar = np.arange(len(d))
    return [int((np.searchsorted(d, d + 2 * w, side="right") - ar).max()) for w in ws]


def stat(uu, vv, w):
    return stat_all(uu, vv, (w,))[0]


def inject(uu, base, rangeu, f, J):
    """partner: a fraction f of uu's events shifted by a fixed lag + Uniform(-J, J) jitter,
    the rest independent. Total count held at len(base) so the marginal rate is unchanged."""
    k = int(round(f * len(uu)))
    k = min(k, len(uu), len(base))
    lag = rng.random() * 0.4 * rangeu - 0.2 * rangeu
    pick = rng.choice(len(uu), size=k, replace=False)
    shifted = uu[pick] + lag + (rng.random(k) * 2 - 1) * J
    keep = rng.choice(len(base), size=len(base) - k, replace=False)
    return np.sort(np.concatenate([shifted, base[keep]]))


if __name__ == "__main__":
    p_("=== GATE 0h — injected coincidence: fraction f x jitter J, detection floor ===")
    ev0, R0 = gk_events()
    p_(f"  synthetic calibration: {len(ev0)} events over u-range {R0:.0f}  ->  "
       f"{len(ev0)/R0:.5f} events per unit u")
    p_(f"  gate0g measured (stratum A):                                     0.06119 +/- 0.00113")
    p_(f"  Levy check: {R0/NPQ:.5f} vs pi^2/(12 ln2) = {math.pi**2/(12*math.log(2)):.5f}\n")

    # ---- null distribution per window: independent pairings (the permutation null's shape)
    p_(f"  building the permutation null: {NNULL} independent pairings per window")
    pool = [gk_events() for _ in range(NNULL + NTRIAL + 8)]
    null = {}
    for w in WS:
        s = [stat(pool[i][0], pool[i + 1][0], w) for i in range(NNULL)]
        null[w] = float(np.percentile(s, 95))
        p_(f"    w = {w:<5g}: null median {np.median(s):>5.1f}, 95th pct {null[w]:>5.1f}, "
           f"max {max(s):>4d}")

    p_(f"\n  DETECTION POWER (fraction of {NTRIAL} injections exceeding the null's 95th pct)")
    out = {}
    for w in WS:
        p_(f"\n  --- detector window w = {w} ---")
        p_(f"  {'f \\\\ J':>7s} " + "".join(f"{'J='+str(J):>9s}" for J in JS))
        for f in FS:
            cells = []
            for J in JS:
                hit = 0
                for tr in range(NTRIAL):
                    uu, _ = pool[NNULL + tr]
                    base, R = pool[NNULL + tr + 1]
                    vv = inject(uu, base, R, f, J)
                    if stat(uu, vv, w) > null[w]:
                        hit += 1
                cells.append(hit / NTRIAL)
                out[f"{w}|{f}|{J}"] = hit / NTRIAL
            p_(f"  {f:>7.2f} " + "".join(f"{100*c:>8.0f}%" for c in cells))

    # ---- the floor: smallest f reaching 80% power, per (w, J)
    p_(f"\n  FLOOR: smallest injected fraction f reaching 80% power")
    p_(f"  {'w \\\\ J':>7s} " + "".join(f"{'J='+str(J):>9s}" for J in JS))
    floors = {}
    for w in WS:
        cells = []
        for J in JS:
            got = next((f for f in FS if out[f"{w}|{f}|{J}"] >= 0.8), None)
            floors[f"{w}|{J}"] = got
            cells.append(f"{got:.2f}" if got else f">{FS[-1]:.2f}")
        p_(f"  {w:>7g} " + "".join(f"{c:>9s}" for c in cells))

    best = {J: min((w for w in WS if floors[f"{w}|{J}"] is not None),
                   key=lambda w: (floors[f"{w}|{J}"], w), default=None) for J in JS}
    p_(f"\n  best window per jitter, and the floor there:")
    for J in JS:
        w = best[J]
        p_(f"    J = {J:<5g}: w = {w}  ->  floor f = "
           f"{floors[f'{w}|{J}'] if w else '--'}")
    # ---------------------------------------------------------- the SEALABLE detector
    p_("\n  === MULTIPLICITY-CORRECTED DETECTOR (the version that can be sealed) ===")
    p_("  The 'best window per jitter' row above is POST-HOC: w was chosen with hindsight, and the")
    p_("  quoted floor does not pay for that look. A sealable statistic must fix the w-ladder in")
    p_("  advance and correct for scanning it:")
    p_("      for each w in a PRE-REGISTERED ladder, p(w) = null-tail probability of S(w);")
    p_("      T = min_w p(w);  null distribution of T taken from the same permutation null.")
    nullS = np.array([stat_all(pool[i][0], pool[i + 1][0]) for i in range(NNULL)], float)

    def Tstat(S):
        return min(float((nullS[:, k] >= S[k]).mean()) for k in range(len(WS)))

    nullT = np.array([Tstat(nullS[i]) for i in range(NNULL)])
    thrT = float(np.percentile(nullT, 5))
    p_(f"  null: T's 5th percentile = {thrT:.4f} (a single-w test would use 0.05; the ladder of "
       f"{len(WS)} windows costs the difference)")

    p_(f"\n  {'f \\\\ J':>7s} " + "".join(f"{'J='+str(J):>9s}" for J in JS))
    corr = {}
    for f_ in FS:
        cells = []
        for J in JS:
            hit = 0
            for tr in range(NTRIAL):
                uu, _ = pool[NNULL + tr]
                base, R = pool[NNULL + tr + 1]
                vv = inject(uu, base, R, f_, J)
                if Tstat(stat_all(uu, vv)) <= thrT:
                    hit += 1
            cells.append(hit / NTRIAL)
            corr[f"{f_}|{J}"] = hit / NTRIAL
        p_(f"  {f_:>7.2f} " + "".join(f"{100*c:>8.0f}%" for c in cells))

    p_(f"\n  SEALABLE FLOOR (80% power, w-ladder scanned and paid for):")
    p_(f"  {'':>7s} " + "".join(f"{'J='+str(J):>9s}" for J in JS))
    cf = {}
    for J in JS:
        got = next((f_ for f_ in FS if corr[f"{f_}|{J}"] >= 0.8), None)
        cf[str(J)] = got
    p_(f"  {'f_min':>7s} " + "".join(f"{(f'{cf[str(J)]:.2f}' if cf[str(J)] else f'>{FS[-1]:.2f}'):>9s}"
                                     for J in JS))
    p_(f"  post-hoc-best-w floor, for comparison:")
    p_(f"  {'f_min':>7s} " + "".join(
        f"{(f'{floors[chr(124).join([str(best[J]),str(J)])]:.2f}' if best[J] and floors[f'{best[J]}|{J}'] else '--'):>9s}"
        for J in JS))
    p_(f"  -> the multiplicity cost is the gap between those two rows. Quote the SEALABLE row.")

    p_(f"\n  WHERE THE LADDER ARM SITS ON THIS GRID: J = 0 exactly, and f = the coincidence rate")
    p_(f"  from gate0d/0e -- 1.00 (|det|=1), 0.48 (4), 0.21 (25), 0.12 (169), 0.08 (841).")
    p_(f"  So the ladder samples the J = 0 COLUMN only. Everything to the right of it is")
    p_(f"  reachable only by injection, which is why axis 2 could not be earned from real data.")

    json.dump({"npq": NPQ, "A_event": A_EV, "n_trial": NTRIAL, "n_null": NNULL,
               "rate_per_u": len(ev0) / R0, "null_95": {str(k): v for k, v in null.items()},
               "power": out, "floors": floors,
               "corrected_power": corr, "corrected_floor": cf, "T_threshold": thrT},
              open(os.path.join(HERE, "gate0h_injection_measured.json"), "w"), indent=2)
    p_("\nwrote gate0h_injection_measured.json")
