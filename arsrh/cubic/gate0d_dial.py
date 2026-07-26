"""
GATE 0d — the coupling dial, at EVENT level. R-066's owed table, axis 1 of 2.

A transferred convergent is NOT a transferred event. At threshold A, an alpha-event (lambda >= A)
has a partner that is itself an event only when lambda' = (g^2/|Delta|) lambda >= A, i.e.
    lambda >= |Delta| A / g^2.
Under Gauss-Kuzmin P(lambda >= A) ~ 1.4427/A, so on the g=1 branch the coincidence rate falls
like ~ g^2/|Delta| = 1/|Delta|, while the g=|Delta| branch transfers everything. That is the dial,
and every setting has a computable answer.

AXIS 1 (this script): |Delta| varies the COINCIDENCE FRACTION at fixed perfect alignment.
AXIS 2 (not here):    injected coincidences at controlled fraction AND controlled jitter in u.
  The ladder cannot calibrate jitter: its lag is EXACTLY log|c*alpha+d| - log g, zero scatter.
  Real data therefore has no jitter axis at all, and a detector tuned on "few but perfect" is
  uncalibrated for "many but smeared". Injection is the only way to earn that arm.
"""
from __future__ import annotations
import json, math, os
from math import gcd

import mpmath as mp
from gate0_ladder import certified_cf, convergents, lam, cf_cbrt

HERE = os.path.dirname(os.path.abspath(__file__))
p_ = lambda *a: print(*a, flush=True)
DIG, NPQ = 1600, 2000
mp.mp.dps = DIG + 60
THRESH = (20, 50, 100, 500)


def cf_of_mpf(x, digits=DIG, maxn=NPQ):
    return certified_cf(int(mp.floor(x * 10 ** digits)), 10 ** digits, maxn)


def pair_stats(a0, a1, M):
    """event-level coincidence rate at each threshold, plus the lag spectrum."""
    a, b, c, d = M
    Delta = abs(a * d - b * c)
    P0, Q0 = convergents(a0); P1, Q1 = convergents(a1)
    idx = {Q1[k]: k for k in range(len(Q1))}
    ev = {A: [0, 0] for A in THRESH}          # [n_events, n_coincident]
    lags, ghist = {}, {}
    for n in range(1, len(a0) - 45):
        A_, B_ = a * P0[n] + b * Q0[n], c * P0[n] + d * Q0[n]
        if B_ == 0:
            continue
        if B_ < 0:
            A_, B_ = -A_, -B_
        g = gcd(abs(A_), B_)
        k = idx.get(B_ // g)
        ok = k is not None and 1 <= k < len(a1) - 45 and P1[k] == A_ // g
        for A in THRESH:
            if a0[n + 1] >= A:
                ev[A][0] += 1
                if ok and a1[k + 1] >= A:
                    ev[A][1] += 1
        if ok:
            lags.setdefault(g, []).append((n, math.log(B_ // g) - math.log(Q0[n])))
        ghist[g] = ghist.get(g, 0) + 1
    return Delta, ev, lags, ghist


def run(label, a0, a1, M):
    Delta, ev, lags, ghist = pair_stats(a0, a1, M)
    # PREDICTED rate: an alpha-event survives iff lambda >= |Delta| A / g^2; under the
    # Gauss-Kuzmin tail P(lambda>=A) ~ 1/A this is min(1, g^2/|Delta|), averaged over the g branches.
    tot = sum(ghist.values())
    pred = sum(v / tot * min(1.0, g * g / Delta) for g, v in ghist.items())
    row = {"label": label, "det": Delta, "pred_rate": pred,
           "rate": {str(A): (ev[A][1] / ev[A][0] if ev[A][0] else None) for A in THRESH},
           "n_events": {str(A): ev[A][0] for A in THRESH},
           "g_hist": {str(g): v for g, v in sorted(ghist.items())},
           "lag_by_g": {str(g): [float(min(x for _, x in v)), float(max(x for _, x in v)),
                                 float(max(x for n, x in v if n >= 200) -
                                       min(x for n, x in v if n >= 200)) if any(n >= 200 for n, _ in v)
                                 else None, len(v)]
                        for g, v in sorted(lags.items())}}
    cells = "".join(f"{100*row['rate'][str(A)]:>6.1f}%/{ev[A][0]:<4d}" if row["rate"][str(A)] is not None
                    else f"{'--':>11s}" for A in THRESH)
    p_(f"  {label:>20s} {Delta:>5d} {100*pred:>7.1f}%  {cells}")
    return row


if __name__ == "__main__":
    p_("=== GATE 0d — the coupling dial at EVENT level ===")
    p_("coincidence rate = fraction of alpha-events (lambda>=A) whose ladder partner is ALSO an event\n")
    p_("  rate is shown as  measured% / n_events  -- cells with tiny n are noise, not signal")
    p_(f"  {'pair':>20s} {'|det|':>5s} {'PRED':>8s}  " +
       "".join(f"{'A='+str(A):>11s}" for A in THRESH))

    out = []

    # ---- cyclic strata (the target's own construction)
    src = json.load(open(os.path.join(HERE, "gate0b_stratify_measured.json")))
    for t_want in (1, 2, 5, 13):
        for e in src["examples"]:
            A_, B_, C_, D_, a, b, c, d, tt, Dl = e
            if abs(tt) != t_want:
                continue
            r = mp.polyroots([1, A_, B_, C_], maxsteps=400, extraprec=800)
            r = sorted(mp.re(x) for x in r)
            img = (a * r[0] + b) / (c * r[0] + d)
            j = min(range(3), key=lambda i: abs(r[i] - img))
            out.append(run(f"cyclic |t|={t_want}", cf_of_mpf(r[0]), cf_of_mpf(r[j]), (a, b, c, d)))
            break

    # ---- the cbrt m family, same law with |det| = m
    for m in (2, 3, 5, 7, 12):
        out.append(run(f"cbrt {m} / cbrt {m}^2", cf_cbrt(m, 1, DIG, NPQ), cf_cbrt(m, 2, DIG, NPQ),
                       (0, m, 1, 0)))

    p_("\n  PREDICTED vs MEASURED coincidence rate (the dial is a formula, not a lookup table)")
    p_(f"  {'pair':>20s} {'pred':>8s} {'meas A=20':>11s} {'ratio':>8s}")
    for o in out:
        m = o["rate"]["20"]
        p_(f"  {o['label']:>20s} {100*o['pred_rate']:>7.1f}% {100*m:>10.1f}% {m/o['pred_rate']:>8.2f}")

    p_("\n  LAG STRUCTURE — lag -> log|c*alpha+d| - log g, a CONSTANT per g-branch.")
    p_("  The full-range spread is a small-q transient; the n>=200 spread is the asymptotic jitter.")
    p_(f"  {'pair':>20s} {'g':>4s} {'lag':>11s} {'spread all n':>13s} {'spread n>=200':>14s} {'n':>6s}")
    for o in out[:2] + out[4:6]:
        for g, (lo, hi, sp200, n) in sorted(o["lag_by_g"].items(), key=lambda kv: int(kv[0])):
            s2 = f"{sp200:>14.2e}" if sp200 is not None else f"{'--':>14s}"
            p_(f"  {o['label']:>20s} {g:>4s} {hi:>11.6f} {hi-lo:>13.2e}{s2} {n:>6d}")

    p_("\n  -> AXIS 1 (count) spans ~100% down to ~6%, a factor of 15-20 in coincidence fraction,")
    p_("     and the PREDICTED rate tracks it -- so any |det| can be sized without running it.")
    p_("  -> AXIS 2 (jitter) has NO handle in this data. The asymptotic lag spread is at the")
    p_("     rationalisation floor; the ladder places partners at an EXACT lag. A detector tuned")
    p_("     on 'few but perfect' is uncalibrated for 'many but smeared', and that arm can only")
    p_("     be earned by INJECTION at controlled fraction and controlled jitter.")

    json.dump(out, open(os.path.join(HERE, "gate0d_dial_measured.json"), "w"), indent=2)
    p_("\nwrote gate0d_dial_measured.json")
