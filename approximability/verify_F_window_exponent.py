"""Re-derive the finite-window test and its oscillation amendment.

  1. The PREMISES hold: vmax=6 still reproduces F_genus_exponent's banked
     summary, and the provable gates still hold at vmax=12. The second is the
     load-bearing one -- Hasse-Weil and RH are theorems, and v=12 exercises the
     k>=5 Newton branch whose k=3,4 sibling carried MORNING_F's original bug.
  2. THE FOUR MISSES ARE PRESERVED. E1-E4 all missed. The amendment explains what
     they measured; it does not convert them. An artifact where they read MET
     without the numbers moving would be the negative tuned away.
  3. The gap is WINDOW-INVARIANT: it must not drift below the bar across the
     sweep, or the exclusion of the finite-window account no longer holds.
  4. THE AMENDMENT'S IDENTITY re-derives independently: ratio equals
     1 - trend(log oscillation)/(0.5 log p) on every curve, and the genus-2
     oscillation trend is an order of magnitude larger than genus-1's. This is
     the only positive claim in the pair, so it is the one checked hardest.
  5. The amendment keeps its POST-HOC label.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from ff_curve import g1_Nv, g2_Nv, rh_gate, hasse_weil_gate         # noqa: E402

bad = []
d = json.load(open(os.path.join(HERE, "F_window_exponent.json")))
am = json.load(open(os.path.join(HERE, "F_oscillation_amendment.json")))
bank = json.load(open(os.path.join(HERE, "F_genus_exponent.json")))

# 1. premises
if d["p1_mismatches"] != 0:
    bad.append(f"P1 mismatches {d['p1_mismatches']}, not 0")
if d["gate_failures_vmax12"] != 0:
    bad.append(f"{d['gate_failures_vmax12']} provable-gate failures at vmax=12 — "
               "a theorem is failing, which is a recurrence bug and not a result")
s6 = d["sweep"]["6"]
for key, bkey in (("gap_ols", "gap_ols"), ("gap_ts", "gap_theil_sen"),
                  ("asymmetry", "asymmetry"), ("rh_worst", "rh_worst"),
                  ("rho", "rho_gap_vs_dip")):
    if abs(s6[key] - bank[bkey]) > 1e-9 * max(abs(bank[bkey]), 1.0):
        bad.append(f"vmax=6 {key} no longer reproduces the banked cell")

# 2. the misses are preserved
for name in ("|gap_ts(12) - gap_ts(6)|",
             "adjacent increases in gap_ts across the vmax sweep",
             "gap_ts at vmax=12",
             "worst |Theil-Sen ratio - 1| at vmax=12"):
    if d["bars"][name]["met"]:
        bad.append(f"bar '{name}' now reads MET — all four science arms MISSED, "
                   "and the amendment explains that, it does not undo it")
if d["verdict"] != "GENUS_GAP_SURVIVES_A_LONGER_WINDOW":
    bad.append(f"verdict is {d['verdict']!r}")

# 3. window invariance
if min(d["gap_ts_trend"]) < 0.05:
    bad.append(f"gap_ts dips to {min(d['gap_ts_trend']):.4f} inside the sweep — "
               "the finite-window account is no longer excluded")

# 4. the identity, re-derived from scratch
PRIMES, VMAX = d["primes"], 12
G1_AB = [(a, b) for a in range(1, 4) for b in range(1, 4)]
G2_C = [(c3, c1, c0) for c3 in range(3) for c1 in range(3) for c0 in range(3)]


def sqfree(f, p):
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
    return max(len(a) - 1, 0) == 0


def ts(x, y):
    return float(np.median([(y[j] - y[i]) / (x[j] - x[i])
                            for i in range(len(x)) for j in range(i + 1, len(x))]))


rows, gates = [], 0
for p in PRIMES:
    cands = [("g1", ab) for ab in G1_AB] + [("g2", c) for c in G2_C]
    for kind, par in cands:
        try:
            if kind == "g1":
                res = g1_Nv(par[0], par[1], p, vmax=VMAX)
            else:
                fc = [par[2], par[1], 0, par[0], 0, 1]
                if not sqfree(fc, p):
                    continue
                res = g2_Nv(fc, p, vmax=VMAX)
        except Exception:
            continue
        n, y, osc = [], [], []
        for v, Nv in enumerate(res["Nv"][:VMAX], start=1):
            r = abs(Nv / float(p ** v) - 1.0)
            if r <= 0:
                continue
            n.append(v)
            y.append(np.log10(r))
            osc.append(np.log10(abs(1.0 - res["power_sums"][v - 1]) / p ** (v / 2.0)))
        if len(n) < 3:
            continue
        if rh_gate(res) and hasse_weil_gate(res, VMAX):
            gates += 1
        nn = np.array(n, float)
        den = 0.5 * np.log10(p)
        rows.append(dict(genus=res["genus"],
                         ratio=-ts(nn, np.array(y)) / den,
                         osc_trend=ts(nn, np.array(osc)), den=den))

if len(rows) != am["n_curves"]:
    bad.append(f"curve count {len(rows)} != amendment's {am['n_curves']}")
if gates != am["gates_hold"]:
    bad.append(f"gates hold on {gates}, amendment records {am['gates_hold']}")
err = max(abs(r["ratio"] - (1.0 - r["osc_trend"] / r["den"])) for r in rows)
if abs(err - am["identity_max_error"]) > 1e-9:
    bad.append(f"identity max error {err:.3e} != amendment's "
               f"{am['identity_max_error']:.3e}")
if err > 0.01:
    bad.append(f"the identity no longer holds (max error {err:.3e}) — the "
               "amendment's whole account rests on it")
for g in (1, 2):
    sub = [r for r in rows if r["genus"] == g]
    got = float(np.mean([abs(r["osc_trend"]) for r in sub]))
    want = am["by_genus"][str(g)]["mean_abs_osc_trend"]
    if abs(got - want) > 1e-9 * max(abs(want), 1.0):
        bad.append(f"genus {g} mean |osc_trend| {got} != banked {want}")
if am["oscillation_amplitude_ratio"] < 3.0:
    bad.append("the genus-2/genus-1 oscillation amplitude ratio has fallen below "
               "3x — the mechanism the amendment names no longer separates")

# 5. label
if "POST-HOC" not in am["status"].upper():
    bad.append("the amendment has lost its POST-HOC label")

print(f"  premises: P1 {d['p1_mismatches']} mismatches; gates {gates}/{len(rows)} "
      f"hold at vmax=12")
print(f"  gap_ts across the sweep: " + " -> ".join(f"{x:.4f}" for x in d["gap_ts_trend"])
      + "  (all four science arms MISSED, preserved)")
print(f"  identity max error {err:.2e}; oscillation amplitude ratio "
      f"{am['oscillation_amplitude_ratio']:.1f}x (POST-HOC)")

if bad:
    print("VERIFY_F_WINDOW_EXPONENT: FAIL")
    for b in bad:
        print("  *", b)
    sys.exit(1)
print("VERIFY_F_WINDOW_EXPONENT: PASS — premises hold, the four misses are "
      "preserved, and the amendment's identity re-derives independently")
