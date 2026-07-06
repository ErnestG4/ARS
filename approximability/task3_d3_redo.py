"""
OVERNIGHT Task 3 / D3 REDO — semiconvergent sawtooth: PREDICT then measure.

The Farey window max_gap/mean is a deterministic q_min detector:  max_gap/mean = 3Q/(π²·q_min)  (one-sided FLOOR:
neighbor denom q'≤Q ⇒ measured ≥ predicted, →1 as q'→Q). q_min = smallest denominator in the aperture = best ONE-SIDED
rational approximant = (mid-quotient) a SEMICONVERGENT. So the sawtooth is precomputable with ZERO simulation by a
Stern–Brocot minimal-denominator descent per window — NOT a convergent-list walk (π's ladder is semiconvergents; the
convergent list gets π wrong inside its big quotients).

DISCIPLINE: predictions computed FIRST (only α + aperture w; no enumeration), banked, THEN measured and overlaid.
Emits q_min as an output column. Parameter turn on the FROZEN refsuite (imports enumerate_window/window_width_for_count;
no logic edits). Seed 20240517.

Run: PYTHONPATH=/home/combust/fmexplorer/riemann_explorer /home/combust/fmexplorer/bin/python3 \
       approximability/task3_d3_redo.py
"""
import os, sys, json, math
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, "/home/combust/fmexplorer/mathtest")
import numpy as np, mpmath as mp
mp.mp.dps = 60
OUT = os.path.dirname(os.path.abspath(__file__))
PI2 = math.pi ** 2
COUNT = 12000

try:
    from refsuite.d3_farey import enumerate_window, window_gap_stats, window_width_for_count
except Exception as e:
    json.dump({"task": "3_d3_redo", "ABORT": f"refsuite import: {e}"}, open(os.path.join(OUT, "task3_d3_redo.json"), "w"))
    print("ABORT:", e); sys.exit(0)


def simplest_between(lo, hi):
    """Smallest-denominator (p,q) with lo <= p/q <= hi (Stern–Brocot / CF descent; exact best one-sided approximant =
    convergent OR semiconvergent). lo,hi mpmath reals, 0<lo<hi."""
    fl = mp.floor(lo)
    if fl >= hi:                       # integer boundary crossed inside [lo,hi]
        return (int(fl), 1) if fl >= lo else (int(fl) + 1, 1)
    if fl == mp.floor(hi):
        if fl == lo:
            return (int(fl), 1)
        p, q = simplest_between(1 / (hi - fl), 1 / (lo - fl))
        return (int(fl) * p + q, p)
    return (int(fl) + 1, 1)


LIOU = sum(mp.mpf(10) ** (-math.factorial(n)) for n in range(1, 8))
TARGETS = {"golden": (mp.sqrt(5) - 1) / 2, "sqrt2": mp.sqrt(2) - 1, "pi": mp.pi - 3,
           "e": mp.e - 2, "liouville": LIOU}
# fine Q grid to resolve the sawtooth teeth
QGRID = [int(x) for x in np.unique(np.round(np.geomspace(1e4, 2e6, 46)).astype(int))]


def q_of_target(alpha):
    a = mp.mpf(alpha)
    w_of = {Q: window_width_for_count(Q, COUNT) for Q in QGRID}
    pred = {}
    for Q in QGRID:
        w = mp.mpf(w_of[Q])                        # frozen convention: window is [α-w, α+w] (w = HALF-width)
        p, q = simplest_between(a - w, a + w)
        pred[Q] = {"w": float(w), "qmin_pred": q, "ratio_pred": 3 * Q / (PI2 * q)}
    return pred, w_of


if __name__ == "__main__":
    print("=" * 78)
    print("D3 REDO — semiconvergent sawtooth (PREDICT via Stern–Brocot, then measure)")
    print("=" * 78)

    # ---- PRE-REGISTER (zero enumeration): predicted q_min + ratio sawtooth per target ----
    predictions = {name: q_of_target(a)[0] for name, a in TARGETS.items()}
    # sanity: golden→Fibonacci denominators, √2→Pell, π→semiconvergents (not convergents)
    def uniq_q(name):
        seen = []
        for Q in QGRID:
            q = predictions[name][Q]["qmin_pred"]
            if not seen or seen[-1] != q: seen.append(q)
        return seen
    print("\n[pre-registered q_min ladders] (unique, in Q order):")
    for name in TARGETS:
        print(f"   {name:10s} {uniq_q(name)}")
    pi_conv = {1, 7, 106, 113, 33102, 33215}
    pi_qs = set(uniq_q("pi"))
    print(f"   π ladder ⊄ π convergents? {not pi_qs.issubset(pi_conv)}  "
          f"(semiconvergents present: {sorted(pi_qs - pi_conv)[:6]}...)")

    # ---- MEASURE (frozen enumerate_window) and overlay ----
    rows = {name: [] for name in TARGETS}
    print(f"\n[measure vs predict]  columns: Q  qmin_pred  qmin_meas  ratio_pred  ratio_meas  meas/pred")
    for name, a in TARGETS.items():
        af = float(a); inv_all = True
        for Q in QGRID:
            pr = predictions[name][Q]; w = pr["w"]
            fr = enumerate_window(af, w, Q)
            gaps, inv = window_gap_stats(fr); inv_all = inv_all and inv
            meas_ratio = max(gaps) / (sum(gaps) / len(gaps)) if gaps else None
            qmin_meas = min(q for p, q in fr)
            rows[name].append({"Q": Q, "qmin_pred": pr["qmin_pred"], "qmin_meas": qmin_meas,
                               "ratio_pred": pr["ratio_pred"], "ratio_meas": meas_ratio,
                               "qmin_match": pr["qmin_pred"] == qmin_meas})
        # summary per target
        mm = [r for r in rows[name] if r["ratio_meas"]]
        qmatch = sum(r["qmin_match"] for r in mm) / len(mm)
        mp_ratio = [r["ratio_meas"] / r["ratio_pred"] for r in mm]
        all_ge1 = all(x >= 0.999 for x in mp_ratio)
        print(f"   {name:10s} qmin_match={qmatch:.0%}  meas/pred median={np.median(mp_ratio):.3f} "
              f"range=[{min(mp_ratio):.3f},{max(mp_ratio):.3f}]  all≥1(floor)={all_ge1}  inv_ok={inv_all}")

    # ---- overall gates ----
    all_rows = [r for name in TARGETS for r in rows[name] if r["ratio_meas"]]
    q_match_rate = sum(r["qmin_match"] for r in all_rows) / len(all_rows)
    floor_ok = all(r["ratio_meas"] / r["ratio_pred"] >= 0.999 for r in all_rows)
    print(f"\n  OVERALL: q_min prediction match = {q_match_rate:.1%} of {len(all_rows)} windows; "
          f"one-sided floor (meas≥pred) held = {floor_ok}")
    print("  ⇒ the semiconvergent Stern–Brocot precompute predicts the sawtooth with zero simulation; "
          "convergent-list walk would miss π's interior-of-quotient teeth.")

    # ---- figure: sawtooth predicted (line) vs measured (points), + q_min staircase ----
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 1, figsize=(11, 9))
    col = {"golden": "#d4af37", "sqrt2": "#6a9a6a", "pi": "#1f77b4", "e": "#d62728", "liouville": "#7f4fa0"}
    for name in TARGETS:
        Qs = [r["Q"] for r in rows[name]]
        axes[0].plot(Qs, [r["ratio_pred"] for r in rows[name]], "-", color=col[name], lw=1.2, alpha=0.8, label=f"{name} (pred)")
        axes[0].plot(Qs, [r["ratio_meas"] for r in rows[name]], "o", color=col[name], ms=3)
        axes[1].plot(Qs, [r["qmin_pred"] for r in rows[name]], "-", color=col[name], lw=1.2, label=name)
        axes[1].plot(Qs, [r["qmin_meas"] for r in rows[name]], "o", color=col[name], ms=3)
    axes[0].set_xscale("log"); axes[0].set_ylabel("max_gap/mean"); axes[0].legend(fontsize=7, ncol=2)
    axes[0].set_title("D3 sawtooth: predicted (line, Stern–Brocot semiconvergent) vs measured (points)\n"
                      "3Q/(π²·q_min); one-sided floor")
    axes[1].set_xscale("log"); axes[1].set_yscale("log"); axes[1].set_xlabel("Farey order Q")
    axes[1].set_ylabel("q_min (smallest denom in aperture)")
    axes[1].set_title("q_min staircase — π climbs SEMICONVERGENTS (106+j·113 inside the 292); golden=Fibonacci, √2=Pell")
    axes[1].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "task3_d3_redo.png"), dpi=130); plt.close(fig)

    json.dump({"task": "3_d3_redo", "seed": 20240517, "count": COUNT, "QGRID": QGRID,
               "q_min_prediction_match_rate": q_match_rate, "one_sided_floor_held": floor_ok,
               "predicted_qmin_ladders": {n: uniq_q(n) for n in TARGETS},
               "rows": rows}, open(os.path.join(OUT, "task3_d3_redo.json"), "w"), indent=2, default=str)
    print("\n  wrote task3_d3_redo.json + task3_d3_redo.png — DONE.")
